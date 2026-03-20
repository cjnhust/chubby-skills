#!/usr/bin/env python3
"""Verify that changed publish-repo skill content matches the recorded local sync manifest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from publish_sync_manifest import (
    MANIFEST_PATH,
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


def main() -> int:
    args = parse_args()
    repo = Path(args.root).expanduser().resolve()
    manifest_path = Path(args.manifest_path)
    if not (repo / ".git").exists():
        raise SystemExit(f"not a git repo: {repo}")

    changed_paths, deleted_paths, all_paths = collect_changed_skill_paths(
        repo,
        args.base_sha,
        head_ref=args.head_sha,
    )
    changed_skill_paths = sorted(set(changed_paths + deleted_paths))
    if not changed_skill_paths:
        print("publish-sync-guard: no managed skill content changes")
        return 0

    manifest_relative = manifest_path.as_posix()
    manifest_updated = manifest_relative in all_paths
    if not manifest_updated and args.head_sha is None and (repo / manifest_path).exists():
        manifest_updated = True
    if not manifest_updated:
        raise SystemExit(
            f"managed skill content changed but {manifest_relative} was not updated. "
            "Use the local sync helper instead of editing publish-repo skill files directly."
        )

    manifest = load_manifest(repo, manifest_path)
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
        "publish-sync-guard: verified "
        f"{len(changed_paths)} changed managed file(s), "
        f"{len(deleted_paths)} deleted managed file(s), "
        f"{len(changed_roots)} changed skill root(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
