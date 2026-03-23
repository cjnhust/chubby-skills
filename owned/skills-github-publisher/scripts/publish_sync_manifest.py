#!/usr/bin/env python3
"""Record and verify publish-repo skill sync metadata."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from fnmatch import fnmatch
from pathlib import Path

sys.dont_write_bytecode = True

from sync_incremental_update import RSYNC_EXCLUDES, REVIEW_REQUIRED_BOUNDARIES, load_local_config


MANIFEST_PATH = Path(".publish-sync/manifest.json")
MANIFEST_SIGNATURE_PATH = Path(".publish-sync/manifest.json.sig")
ALLOWED_SIGNERS_PATH = Path(".publish-sync/allowed_signers")
MANAGED_GROUPS = {"owned", "third-party"}
SIGNING_NAMESPACE = "file"
DEFAULT_SIGNER_IDENTITY = "publish-sync"


def git_output(repo: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(repo), *args],
        text=True,
        encoding="utf-8",
        errors="replace",
    ).strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record publish-repo sync metadata for changed skill roots.")
    parser.add_argument("--root", required=True, help="Publish repo working copy.")
    parser.add_argument("--base-ref", required=True, help="Base ref used to detect changed skill roots.")
    parser.add_argument(
        "--manifest-path",
        default=str(MANIFEST_PATH),
        help="Manifest path relative to the repo root.",
    )
    parser.add_argument(
        "--signature-path",
        default=str(MANIFEST_SIGNATURE_PATH),
        help="Signature path relative to the repo root.",
    )
    parser.add_argument(
        "--signing-key",
        help="Private signing key used to sign the manifest. Defaults to local config default_publish_signing_key.",
    )
    parser.add_argument(
        "--signer-identity",
        help="Signer identity used with the allowed signers file. Defaults to local config default_publish_signing_identity.",
    )
    return parser.parse_args()


def path_from_text(raw_path: str) -> Path:
    return Path(raw_path.replace("\\", "/"))


def relative_posix(path: Path) -> str:
    return path.as_posix()


def skill_root_for_relative_path(relative_path: str) -> str | None:
    parts = path_from_text(relative_path).parts
    if len(parts) < 3:
        return None
    if parts[0] not in MANAGED_GROUPS:
        return None
    return relative_posix(Path(parts[0]) / parts[1])


def diff_base_ref(repo: Path, base_ref: str, head_ref: str | None = None) -> str:
    target_ref = head_ref or "HEAD"
    return git_output(repo, "merge-base", base_ref, target_ref)


def collect_changed_skill_paths(
    repo: Path,
    base_ref: str,
    head_ref: str | None = None,
) -> tuple[list[str], list[str], list[str]]:
    cmd = ["diff", "--name-status", "-M", diff_base_ref(repo, base_ref, head_ref)]
    if head_ref:
        cmd.append(head_ref)
    cmd.extend(
        [
            "--",
            "owned",
            "third-party",
            str(MANIFEST_PATH),
            str(MANIFEST_SIGNATURE_PATH),
            str(ALLOWED_SIGNERS_PATH),
        ]
    )
    output = git_output(repo, *cmd)

    changed_paths: set[str] = set()
    deleted_paths: set[str] = set()
    all_paths: set[str] = set()

    for raw_line in filter(None, output.splitlines()):
        parts = raw_line.split("\t")
        if not parts:
            continue
        status = parts[0]

        if status.startswith("R"):
            if len(parts) < 3:
                continue
            old_path = parts[1]
            new_path = parts[2]
            all_paths.update({old_path, new_path})
            if skill_root_for_relative_path(old_path):
                deleted_paths.add(old_path)
            if skill_root_for_relative_path(new_path):
                changed_paths.add(new_path)
            continue

        if status.startswith("C"):
            if len(parts) < 3:
                continue
            new_path = parts[2]
            all_paths.add(new_path)
            if skill_root_for_relative_path(new_path):
                changed_paths.add(new_path)
            continue

        if len(parts) < 2:
            continue
        relative_path = parts[1]
        all_paths.add(relative_path)
        if not skill_root_for_relative_path(relative_path):
            continue
        if status == "D":
            deleted_paths.add(relative_path)
        else:
            changed_paths.add(relative_path)

    if head_ref is None:
        untracked_output = git_output(
            repo,
            "ls-files",
            "--others",
            "--exclude-standard",
            "--",
            "owned",
            "third-party",
            str(MANIFEST_PATH),
            str(MANIFEST_SIGNATURE_PATH),
            str(ALLOWED_SIGNERS_PATH),
        )
        for relative_path in filter(None, untracked_output.splitlines()):
            all_paths.add(relative_path)
            if skill_root_for_relative_path(relative_path):
                changed_paths.add(relative_path)

    return sorted(changed_paths), sorted(deleted_paths), sorted(all_paths)


def changed_skill_roots(repo: Path, base_ref: str, head_ref: str | None = None) -> list[str]:
    changed_paths, deleted_paths, _ = collect_changed_skill_paths(repo, base_ref, head_ref=head_ref)
    roots = {skill_root_for_relative_path(path) for path in [*changed_paths, *deleted_paths]}
    return sorted(root for root in roots if root)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def manifest_excludes_path(relative_to_skill_root: Path) -> bool:
    parts = relative_to_skill_root.parts
    if any(part in REVIEW_REQUIRED_BOUNDARIES or part.startswith("danger-") for part in parts):
        return True

    relative_path = relative_posix(relative_to_skill_root)
    for pattern in RSYNC_EXCLUDES:
        normalized_pattern = pattern.rstrip("/")
        if pattern.endswith("/"):
            if any(part == normalized_pattern for part in parts):
                return True
            continue
        if "/" in normalized_pattern:
            if fnmatch(relative_path, normalized_pattern):
                return True
            continue
        if any(fnmatch(part, normalized_pattern) for part in parts):
            return True
    return False


def collect_skill_files(repo: Path, skill_root: str) -> list[dict[str, str]]:
    root = repo / skill_root
    if not root.exists():
        return []

    entries: list[dict[str, str]] = []
    for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file()):
        relative_to_skill_root = path.relative_to(root)
        if manifest_excludes_path(relative_to_skill_root):
            continue
        relative_path = relative_posix(path.relative_to(repo))
        entries.append(
            {
                "path": relative_path,
                "sha256": sha256_file(path),
            }
        )
    return entries


def build_manifest(
    repo: Path,
    base_ref: str,
    skill_roots: list[str],
    deleted_files: list[str],
    signer_identity: str,
) -> dict:
    files: list[dict[str, str]] = []
    for skill_root in skill_roots:
        files.extend(collect_skill_files(repo, skill_root))

    return {
        "schema_version": 1,
        "generator": "owned/skills-github-publisher/scripts/publish_sync_manifest.py",
        "mode": "local-sync-only",
        "base_ref": base_ref,
        "signer_identity": signer_identity,
        "synchronized_skill_roots": skill_roots,
        "deleted_files": sorted(deleted_files),
        "files": files,
    }


def resolve_signing_key(explicit_signing_key: str | None) -> Path:
    if explicit_signing_key:
        candidate = Path(explicit_signing_key).expanduser().resolve()
    else:
        config = load_local_config()
        signing_key = config.get("default_publish_signing_key")
        if not isinstance(signing_key, str) or not signing_key:
            raise SystemExit(
                "publish signing key is not configured; set default_publish_signing_key in local config or pass --signing-key"
            )
        candidate = Path(signing_key).expanduser().resolve()

    if not candidate.exists():
        raise SystemExit(f"publish signing key does not exist: {candidate}")
    if not candidate.is_file():
        raise SystemExit(f"publish signing key is not a file: {candidate}")
    return candidate


def resolve_signer_identity(explicit_signer_identity: str | None) -> str:
    if explicit_signer_identity:
        candidate = explicit_signer_identity.strip()
        if not candidate:
            raise SystemExit("publish signer identity must not be empty")
        return candidate

    config = load_local_config()
    signer_identity = config.get("default_publish_signing_identity")
    if isinstance(signer_identity, str) and signer_identity.strip():
        return signer_identity.strip()
    return DEFAULT_SIGNER_IDENTITY


def sign_manifest(manifest_path: Path, signature_path: Path, signing_key: Path) -> Path:
    generated_signature = manifest_path.with_name(f"{manifest_path.name}.sig")
    if generated_signature.exists():
        generated_signature.unlink()

    subprocess.run(
        [
            "ssh-keygen",
            "-q",
            "-Y",
            "sign",
            "-f",
            str(signing_key),
            "-n",
            SIGNING_NAMESPACE,
            str(manifest_path),
        ],
        check=True,
    )
    if not generated_signature.exists():
        raise SystemExit(f"ssh-keygen did not produce a signature for {manifest_path}")

    signature_path.parent.mkdir(parents=True, exist_ok=True)
    if generated_signature != signature_path:
        generated_signature.replace(signature_path)
    return signature_path


def write_manifest(
    repo: Path,
    base_ref: str,
    manifest_path: Path,
    signature_path: Path | None = None,
    signing_key: Path | None = None,
    signer_identity: str | None = None,
) -> Path | None:
    changed_paths, deleted_paths, _ = collect_changed_skill_paths(repo, base_ref)
    skill_roots = changed_skill_roots(repo, base_ref)
    if not changed_paths and not deleted_paths and not skill_roots:
        return None

    effective_signature_path = signature_path or MANIFEST_SIGNATURE_PATH
    effective_signing_key = signing_key or resolve_signing_key(None)
    effective_signer_identity = resolve_signer_identity(signer_identity)

    payload = build_manifest(repo, base_ref, skill_roots, deleted_paths, effective_signer_identity)
    target = repo / manifest_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    sign_manifest(target, repo / effective_signature_path, effective_signing_key)
    return target


def main() -> int:
    args = parse_args()
    repo = Path(args.root).expanduser().resolve()
    if not (repo / ".git").exists():
        raise SystemExit(f"not a git repo: {repo}")

    manifest = write_manifest(
        repo,
        args.base_ref,
        Path(args.manifest_path),
        signature_path=Path(args.signature_path),
        signing_key=resolve_signing_key(args.signing_key),
        signer_identity=resolve_signer_identity(args.signer_identity),
    )
    if manifest is None:
        print("publish-sync-manifest: no changed skill roots")
        return 0

    print(manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
