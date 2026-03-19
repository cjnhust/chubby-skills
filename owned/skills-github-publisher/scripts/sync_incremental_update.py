#!/usr/bin/env python3
"""Sync one or more local skills into a publish repo working copy."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True


def candidate_config_paths() -> list[Path]:
    candidates: list[Path] = []
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        candidates.append(Path(codex_home).expanduser() / "private" / "skills-github-publisher.json")
    candidates.append(Path.home() / ".codex" / "private" / "skills-github-publisher.json")
    return candidates


def load_local_config() -> dict:
    for path in candidate_config_paths():
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise SystemExit(f"local config is not a JSON object: {path}")
        return payload
    return {}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync local skills into a publish repo working copy.")
    parser.add_argument(
        "--skill-root",
        action="append",
        required=True,
        help="Absolute path to a local skill root to sync.",
    )
    parser.add_argument("--publish-repo", help="Override the publish repo working copy.")
    parser.add_argument("--owned-root", help="Override the destination owned/ root.")
    parser.add_argument(
        "--group",
        choices=("owned", "third-party"),
        default="owned",
        help="Destination group when owned-root is not provided.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print rsync commands without executing them.")
    return parser.parse_args()


def resolve_destination_root(args: argparse.Namespace, config: dict) -> Path:
    if args.owned_root:
        return Path(args.owned_root).expanduser().resolve()

    if args.group == "owned" and isinstance(config.get("default_owned_root"), str):
        return Path(config["default_owned_root"]).expanduser().resolve()

    publish_repo = args.publish_repo or config.get("default_publish_repo")
    if not isinstance(publish_repo, str) or not publish_repo:
        raise SystemExit("publish repo is not configured; pass --publish-repo or set default_publish_repo in local config")

    return (Path(publish_repo).expanduser().resolve() / args.group)


def sync_one(src_root: Path, dest_group_root: Path, dry_run: bool) -> None:
    if not (src_root / "SKILL.md").exists():
        raise SystemExit(f"not a skill root: {src_root}")

    dest_root = dest_group_root / src_root.name
    dest_root.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "rsync",
        "-a",
        "--delete",
        f"{src_root}/",
        f"{dest_root}/",
    ]

    if dry_run:
        print(" ".join(cmd))
        return

    subprocess.run(cmd, check=True)
    print(dest_root)


def main() -> None:
    args = parse_args()
    config = load_local_config()
    dest_group_root = resolve_destination_root(args, config)

    for raw_path in args.skill_root:
        sync_one(Path(raw_path).expanduser().resolve(), dest_group_root, args.dry_run)


if __name__ == "__main__":
    main()
