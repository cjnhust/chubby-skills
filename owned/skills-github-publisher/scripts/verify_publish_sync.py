#!/usr/bin/env python3
"""Verify that changed publish-repo skill content matches the recorded local sync manifest."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from publish_sync_manifest import (
    ALLOWED_SIGNERS_PATH,
    DEFAULT_SIGNER_IDENTITY,
    MANIFEST_PATH,
    MANIFEST_SIGNATURE_PATH,
    SIGNING_NAMESPACE,
    collect_changed_skill_paths,
    path_from_text,
    sha256_file,
    skill_root_for_relative_path,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify publish-repo skill changes came from the local sync flow.")
    parser.add_argument("--root", required=True, help="Publish repo working copy.")
    parser.add_argument("--base-sha", required=True, help="PR base SHA.")
    parser.add_argument("--head-sha", help="PR head SHA. Defaults to the current working tree.")
    parser.add_argument(
        "--manifest-path",
        default=str(MANIFEST_PATH),
        help="Manifest path relative to the repo root.",
    )
    parser.add_argument(
        "--signature-path",
        default=str(MANIFEST_SIGNATURE_PATH),
        help="Manifest signature path relative to the repo root.",
    )
    parser.add_argument(
        "--allowed-signers-path",
        default=str(ALLOWED_SIGNERS_PATH),
        help="Trusted allowed signers file used to verify the signed manifest.",
    )
    parser.add_argument(
        "--signer-identity",
        help="Optional signer identity override. Defaults to the manifest signer_identity.",
    )
    return parser.parse_args()


def load_manifest(repo: Path, manifest_path: Path) -> dict:
    target = repo / manifest_path
    if not target.exists():
        raise SystemExit(
            f"publish sync manifest is missing: {manifest_path}. "
            "Use the local sync flow instead of editing publish-repo skill content directly."
        )

    with target.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if not isinstance(payload, dict):
        raise SystemExit(f"publish sync manifest is not a JSON object: {manifest_path}")
    return payload


def verify_manifest_signature(
    repo: Path,
    manifest_path: Path,
    signature_path: Path,
    allowed_signers_path: Path,
    signer_identity: str,
) -> None:
    target_signature = repo / signature_path
    if not target_signature.exists():
        raise SystemExit(
            f"publish sync signature is missing: {signature_path}. "
            "Use the local sync helper instead of editing publish-repo skill content directly."
        )

    target_allowed_signers = repo / allowed_signers_path
    if not target_allowed_signers.exists():
        raise SystemExit(f"allowed signers file is missing: {allowed_signers_path}")

    with (repo / manifest_path).open("rb") as handle:
        result = subprocess.run(
            [
                "ssh-keygen",
                "-Y",
                "verify",
                "-f",
                str(target_allowed_signers),
                "-I",
                signer_identity,
                "-n",
                SIGNING_NAMESPACE,
                "-s",
                str(target_signature),
            ],
            stdin=handle,
            capture_output=True,
            check=False,
        )

    if result.returncode == 0:
        return

    details = (result.stderr or result.stdout).decode("utf-8", errors="replace").strip()
    suffix = f" ({details})" if details else ""
    raise SystemExit(
        "publish sync manifest signature is invalid. "
        "Rerun the local sync helper instead of editing the publish repo directly."
        + suffix
    )


def verify_allowed_signers_update(
    repo: Path,
    repo_allowed_signers_path: Path,
    trusted_allowed_signers_path: Path,
) -> None:
    target_allowed_signers = repo / repo_allowed_signers_path
    if not target_allowed_signers.exists():
        raise SystemExit(f"publish repo allowed signers file is missing: {repo_allowed_signers_path}")

    trusted_allowed_signers = repo / trusted_allowed_signers_path
    if not trusted_allowed_signers.exists():
        raise SystemExit(f"trusted allowed signers file is missing: {trusted_allowed_signers_path}")

    if sha256_file(target_allowed_signers) == sha256_file(trusted_allowed_signers):
        return

    raise SystemExit(
        "publish repo allowed signers file does not match the trusted signer set for this run. "
        "Bootstrap or rotate the signer out of band before changing .publish-sync/allowed_signers."
    )


def main() -> int:
    args = parse_args()
    repo = Path(args.root).expanduser().resolve()
    manifest_path = Path(args.manifest_path)
    signature_path = Path(args.signature_path)
    trusted_allowed_signers_path = Path(args.allowed_signers_path)
    repo_allowed_signers_path = ALLOWED_SIGNERS_PATH
    if not (repo / ".git").exists():
        raise SystemExit(f"not a git repo: {repo}")

    changed_paths, deleted_paths, all_paths = collect_changed_skill_paths(
        repo,
        args.base_sha,
        head_ref=args.head_sha,
        manifest_path=manifest_path,
        signature_path=signature_path,
        repo_allowed_signers_path=repo_allowed_signers_path,
    )
    changed_skill_paths = sorted(set(changed_paths + deleted_paths))

    manifest_relative = manifest_path.as_posix()
    manifest_updated = manifest_relative in all_paths
    if not manifest_updated and args.head_sha is None and (repo / manifest_path).exists():
        manifest_updated = True

    signature_relative = signature_path.as_posix()
    signature_updated = signature_relative in all_paths
    if not signature_updated and args.head_sha is None and (repo / signature_path).exists():
        signature_updated = True
    allowed_signers_relative = repo_allowed_signers_path.as_posix()
    allowed_signers_updated = allowed_signers_relative in all_paths

    if allowed_signers_updated:
        if trusted_allowed_signers_path.as_posix() == repo_allowed_signers_path.as_posix():
            raise SystemExit(
                "publish repo allowed_signers changed but verification still points at the PR copy. "
                "Pass --allowed-signers-path to a trusted baseline file for signer rotations."
            )
        verify_allowed_signers_update(repo, repo_allowed_signers_path, trusted_allowed_signers_path)

    if not changed_skill_paths:
        if manifest_updated or signature_updated:
            raise SystemExit(
                "publish sync manifest metadata changed without any managed skill content changes. "
                "Only update manifest.json and manifest.json.sig together with a local skill sync."
            )
        if allowed_signers_updated:
            print("publish-sync-guard: verified trusted allowed_signers update")
            return 0
        print("publish-sync-guard: no managed skill content changes")
        return 0

    if not manifest_updated:
        raise SystemExit(
            f"managed skill content changed but {manifest_relative} was not updated. "
            "Use the local sync helper instead of editing publish-repo skill files directly."
        )
    if not signature_updated:
        raise SystemExit(
            f"managed skill content changed but {signature_relative} was not updated. "
            "Use the local sync helper instead of editing publish-repo skill files directly."
        )

    manifest = load_manifest(repo, manifest_path)
    manifest_signer_identity = manifest.get("signer_identity")
    if not isinstance(manifest_signer_identity, str) or not manifest_signer_identity.strip():
        raise SystemExit("publish sync manifest signer identity is missing")
    expected_signer_identity = args.signer_identity or manifest_signer_identity
    if manifest_signer_identity != expected_signer_identity:
        raise SystemExit(
            "publish sync manifest signer identity "
            f"{manifest_signer_identity!r} does not match expected {expected_signer_identity!r}"
        )
    verify_manifest_signature(
        repo,
        manifest_path,
        signature_path,
        trusted_allowed_signers_path,
        expected_signer_identity,
    )
    manifest_files = manifest.get("files", [])
    manifest_deleted = set(manifest.get("deleted_files", []))
    manifest_roots = set(manifest.get("synchronized_skill_roots", []))
    file_hashes = {
        item.get("path"): item.get("sha256")
        for item in manifest_files
        if isinstance(item, dict) and isinstance(item.get("path"), str) and isinstance(item.get("sha256"), str)
    }

    changed_roots = {skill_root_for_relative_path(path) for path in changed_skill_paths}
    changed_roots.discard(None)
    missing_roots = sorted(root for root in changed_roots if root not in manifest_roots)
    if missing_roots:
        raise SystemExit(
            "publish sync manifest is missing changed skill roots: "
            + ", ".join(missing_roots)
        )

    for relative_path in deleted_paths:
        if relative_path not in manifest_deleted:
            raise SystemExit(
                f"deleted managed file {relative_path} is missing from manifest deleted_files"
            )

    for relative_path in changed_paths:
        expected_hash = file_hashes.get(relative_path)
        if expected_hash is None:
            raise SystemExit(
                f"changed managed file {relative_path} is missing from publish sync manifest"
            )

        absolute_path = repo / path_from_text(relative_path)
        if not absolute_path.exists():
            raise SystemExit(f"changed managed file is missing from HEAD: {relative_path}")

        actual_hash = sha256_file(absolute_path)
        if actual_hash != expected_hash:
            raise SystemExit(
                f"publish sync manifest hash mismatch for {relative_path}. "
                "Rerun the local sync helper instead of editing the publish repo directly."
            )

    print(
        "publish-sync-guard: verified signed manifest for "
        f"{len(changed_paths)} changed managed file(s), "
        f"{len(deleted_paths)} deleted managed file(s), "
        f"{len(changed_roots)} changed skill root(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
