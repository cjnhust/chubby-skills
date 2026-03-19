#!/usr/bin/env python3
"""Sync one or more local skills into a publish repo working copy."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True


RSYNC_EXCLUDES = (
    ".DS_Store",
    "__pycache__/",
    "*.pyc",
    "node_modules/",
    ".env",
    ".env.*",
    "cookies.json",
    "consent.json",
    "sessions/",
    "chrome-profile/",
    "*.db",
    "*.sqlite",
    "*.pem",
    "*.key",
    "*.p12",
    "*.pfx",
)


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
    parser.add_argument(
        "--allow-review-required",
        action="store_true",
        help="Allow explicit sync of internal/, .system/, or danger-* skill roots.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print rsync commands without executing them.")
    return parser.parse_args()


def resolve_destination_root(args: argparse.Namespace, config: dict) -> Path:
    if args.owned_root:
        return Path(args.owned_root).expanduser().resolve()

    if args.publish_repo:
        return Path(args.publish_repo).expanduser().resolve() / args.group

    if args.group == "owned" and isinstance(config.get("default_owned_root"), str):
        return Path(config["default_owned_root"]).expanduser().resolve()

    publish_repo = args.publish_repo or config.get("default_publish_repo")
    if not isinstance(publish_repo, str) or not publish_repo:
        raise SystemExit("publish repo is not configured; pass --publish-repo or set default_publish_repo in local config")

    return (Path(publish_repo).expanduser().resolve() / args.group)


def is_review_required_root(src_root: Path) -> bool:
    return src_root.name.startswith("danger-") or src_root.parent.name in {"internal", ".system"}


def sync_one(src_root: Path, dest_group_root: Path, dry_run: bool, allow_review_required: bool) -> None:
    if not (src_root / "SKILL.md").exists():
        raise SystemExit(f"not a skill root: {src_root}")
    if is_review_required_root(src_root) and not allow_review_required:
        raise SystemExit(
            f"refusing to sync review-required skill root by default: {src_root} "
            "(pass --allow-review-required only after an explicit publication decision)"
        )

    dest_root = dest_group_root / src_root.name
    dest_root.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "rsync",
        "-a",
        "--delete",
        "--delete-excluded",
    ]
    for pattern in RSYNC_EXCLUDES:
        cmd.extend(["--exclude", pattern])
    cmd.extend(
        [
        f"{src_root}/",
        f"{dest_root}/",
        ]
    )

    if dry_run:
        print(shlex.join(cmd))
        return

    subprocess.run(cmd, check=True)
    print(dest_root)


def main() -> None:
    args = parse_args()
    config = load_local_config()
    dest_group_root = resolve_destination_root(args, config)

    for raw_path in args.skill_root:
        sync_one(
            Path(raw_path).expanduser().resolve(),
            dest_group_root,
            args.dry_run,
            args.allow_review_required,
        )


if __name__ == "__main__":
    main()
