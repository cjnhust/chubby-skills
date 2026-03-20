#!/usr/bin/env python3
"""Prepare a repeatable incremental publish PR in the configured repo."""

from __future__ import annotations

import argparse
import re
import shlex
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from publish_sync_manifest import write_manifest
from sync_incremental_update import load_local_config, resolve_destination_root, sync_one


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or reuse a publish PR branch, sync skill roots, and rerun strict local checks."
    )
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
    parser.add_argument("--base", default="main", help="Base branch to refresh from. Defaults to main.")
    parser.add_argument("--branch", help="Explicit PR branch name.")
    parser.add_argument(
        "--branch-prefix",
        default="codex/",
        help="Prefix for generated PR branches. Defaults to codex/.",
    )
    parser.add_argument(
        "--reuse-branch",
        action="store_true",
        help="Reuse an existing branch name by resetting it to the refreshed base before syncing.",
    )
    parser.add_argument(
        "--allow-review-required",
        action="store_true",
        help="Allow explicit sync of internal/, .system/, or danger-* skill roots.",
    )
    parser.add_argument(
        "--skip-preflight",
        action="store_true",
        help="Skip the strict preflight scan after syncing.",
    )
    parser.add_argument(
        "--skip-git-identity",
        action="store_true",
        help="Skip the git identity audit before the sync handoff.",
    )
    parser.add_argument(
        "--skip-fetch",
        action="store_true",
        help="Skip fetching the base branch from origin before creating the PR branch.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned git/sync commands without changing the repo.",
    )
    return parser.parse_args()


def git_output(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def git_run(repo: Path, *args: str, dry_run: bool = False) -> None:
    cmd = ["git", "-C", str(repo), *args]
    if dry_run:
        print(shlex.join(cmd))
        return
    subprocess.run(cmd, check=True)


def git_status_clean(repo: Path) -> bool:
    return git_output(repo, "status", "--short") == ""


def git_ref_exists(repo: Path, ref: str) -> bool:
    result = subprocess.run(
        ["git", "-C", str(repo), "show-ref", "--verify", "--quiet", ref],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def remote_branch_exists(repo: Path, branch: str) -> bool:
    result = subprocess.run(
        ["git", "-C", str(repo), "ls-remote", "--exit-code", "--heads", "origin", branch],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode == 0:
        return True
    if result.returncode == 2:
        return False
    raise SystemExit(f"could not verify whether origin/{branch} exists; check remote connectivity and authentication first")


def resolve_publish_repo(args: argparse.Namespace, config: dict) -> Path:
    if args.publish_repo:
        return Path(args.publish_repo).expanduser().resolve()

    publish_repo = config.get("default_publish_repo")
    if isinstance(publish_repo, str) and publish_repo:
        return Path(publish_repo).expanduser().resolve()

    if args.owned_root:
        owned_root = Path(args.owned_root).expanduser().resolve()
        if owned_root.name in {"owned", "third-party"}:
            return owned_root.parent

    raise SystemExit("publish repo is not configured; pass --publish-repo or set default_publish_repo in local config")


def ensure_within_repo(path: Path, repo: Path) -> None:
    try:
        path.relative_to(repo)
    except ValueError as exc:
        raise SystemExit(f"destination root escapes the publish repo boundary: {path} (repo: {repo})") from exc


def slugify_branch_suffix(skill_roots: list[Path]) -> str:
    names = "-".join(src_root.name for src_root in skill_roots)
    slug = re.sub(r"[^a-z0-9]+", "-", names.lower()).strip("-")
    return slug[:64] or "skills-update"


def resolve_branch_name(args: argparse.Namespace, skill_roots: list[Path]) -> str:
    if args.branch:
        return args.branch
    prefix = args.branch_prefix
    suffix = slugify_branch_suffix(skill_roots)
    return f"{prefix}{suffix}" if prefix else suffix


def select_start_ref(repo: Path, base: str, skip_fetch: bool, dry_run: bool) -> str:
    if not skip_fetch:
        git_run(repo, "fetch", "--prune", "origin", base, dry_run=dry_run)

    if git_ref_exists(repo, f"refs/remotes/origin/{base}"):
        return f"origin/{base}"
    if git_ref_exists(repo, f"refs/heads/{base}"):
        return base
    raise SystemExit(f"base branch '{base}' is missing locally and on origin")


def run_local_check(
    script_name: str,
    repo: Path,
    config: dict,
    extra_args: list[str],
    dry_run: bool,
) -> None:
    script_path = Path(__file__).with_name(script_name)
    cmd = ["python3", str(script_path), "--root", str(repo), *extra_args]
    local_policy = config.get("default_local_policy_file")
    if isinstance(local_policy, str) and local_policy:
        cmd.extend(["--local-policy-file", local_policy])
    if dry_run:
        print(shlex.join(cmd))
        return
    subprocess.run(cmd, check=True)


def main() -> int:
    args = parse_args()
    config = load_local_config()
    publish_repo = resolve_publish_repo(args, config)
    if not (publish_repo / ".git").exists():
        raise SystemExit(f"not a git repo: {publish_repo}")
    if not git_status_clean(publish_repo):
        raise SystemExit("publish repo working tree is not clean; commit or stash before starting a new incremental PR")

    src_roots = [Path(raw_path).expanduser().resolve() for raw_path in args.skill_root]
    dest_group_root = resolve_destination_root(args, config, src_roots)
    ensure_within_repo(dest_group_root, publish_repo)

    branch = resolve_branch_name(args, src_roots)
    start_ref = select_start_ref(publish_repo, args.base, args.skip_fetch, args.dry_run)
    local_branch_ref = f"refs/heads/{branch}"

    if git_ref_exists(publish_repo, local_branch_ref):
        if not args.reuse_branch:
            raise SystemExit(
                f"branch '{branch}' already exists; pass --reuse-branch to continue on it or choose a new branch name"
            )
        git_run(publish_repo, "switch", "-C", branch, start_ref, dry_run=args.dry_run)
    else:
        git_run(publish_repo, "switch", "-c", branch, start_ref, dry_run=args.dry_run)

    for src_root in src_roots:
        sync_one(
            src_root,
            dest_group_root,
            args.dry_run,
            args.allow_review_required,
        )

    manifest_path = None
    if args.dry_run:
        script_path = Path(__file__).with_name("publish_sync_manifest.py")
        print(
            shlex.join(
                [
                    "python3",
                    str(script_path),
                    "--root",
                    str(publish_repo),
                    "--base-ref",
                    start_ref,
                ]
            )
        )
    else:
        manifest_path = write_manifest(publish_repo, start_ref, Path(".publish-sync/manifest.json"))

    if not args.skip_git_identity:
        run_local_check("check_git_identity.py", publish_repo, config, ["--strict"], args.dry_run)
    if not args.skip_preflight:
        run_local_check(
            "preflight_scan.py",
            publish_repo,
            config,
            ["--strict", "--strict-provenance"],
            args.dry_run,
        )

    remote_base_exists = remote_branch_exists(publish_repo, args.base)
    print(f"repo: {publish_repo}")
    print(f"branch: {branch}")
    print(f"base: {args.base}")
    print(f"start_ref: {start_ref}")
    print(f"destination_root: {dest_group_root}")
    if manifest_path is not None:
        print(f"publish_sync_manifest: {manifest_path}")
    print(f"origin_base_exists: {'yes' if remote_base_exists else 'no'}")
    if args.dry_run:
        return 0

    status = git_output(publish_repo, "status", "--short")
    print("git_status:")
    print(status or "(clean)")
    print("next_steps:")
    print(f"1. Review the diff in {publish_repo}")
    print("2. Commit the intended changes on the PR branch")
    print(
        "3. Run `python3 owned/skills-github-publisher/scripts/push_pr_handoff.py --base "
        f"{args.base}` to inspect the push and PR handoff"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
