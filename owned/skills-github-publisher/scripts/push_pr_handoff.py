#!/usr/bin/env python3
"""Validate and execute the final push/PR handoff for a publish repo."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

sys.dont_write_bytecode = True

from sync_incremental_update import load_local_config


def git_output(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def git_status_clean(repo: Path) -> bool:
    return git_output(repo, "status", "--short") == ""


def normalize_origin_url(remote: str) -> str | None:
    remote = remote.strip()
    if remote.startswith("https://github.com/"):
        return remote.removesuffix(".git")
    if remote.startswith("git@") and ":" in remote:
        _, slug = remote.split(":", 1)
        slug = slug.removesuffix(".git")
        return f"https://github.com/{slug}"
    if remote.startswith("ssh://git@"):
        slug = remote.split("/", 3)[-1].removesuffix(".git")
        return f"https://github.com/{slug}"
    return None


def compare_url(origin_url: str, base: str, branch: str) -> str:
    return f"{origin_url}/compare/{quote(base, safe='')}...{quote(branch, safe='')}?expand=1"


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


def resolve_gh() -> str | None:
    candidate = shutil.which("gh")
    if candidate:
        return candidate
    for path in ("/opt/homebrew/bin/gh", "/usr/local/bin/gh"):
        if Path(path).exists():
            return path
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate and execute push/PR handoff for a publish repo.")
    parser.add_argument(
        "--root",
        help="Publish repo working copy. Defaults to local default_publish_repo.",
    )
    parser.add_argument("--base", default="main", help="PR base branch. Defaults to main.")
    parser.add_argument("--branch", help="PR branch. Defaults to the current branch.")
    parser.add_argument("--title", help="Optional PR title for gh pr create.")
    parser.add_argument("--body-file", help="Optional PR body file for gh pr create.")
    parser.add_argument("--draft", action="store_true", help="Create the PR as a draft when using gh.")
    parser.add_argument("--push", action="store_true", help="Run git push -u origin <branch>.")
    parser.add_argument("--create-pr", action="store_true", help="Create the PR via gh after push.")
    return parser.parse_args()


def resolve_repo_root(explicit_root: str | None) -> Path:
    if explicit_root:
        return Path(explicit_root).expanduser().resolve()

    config = load_local_config()
    publish_repo = config.get("default_publish_repo")
    if isinstance(publish_repo, str) and publish_repo:
        return Path(publish_repo).expanduser().resolve()

    raise SystemExit("publish repo is not configured; pass --root or set default_publish_repo in local config")


def main() -> int:
    args = parse_args()
    repo = resolve_repo_root(args.root)
    if not (repo / ".git").exists():
        raise SystemExit(f"not a git repo: {repo}")

    branch = args.branch or git_output(repo, "branch", "--show-current")
    if not branch:
        raise SystemExit("could not determine current branch")
    if not git_status_clean(repo):
        raise SystemExit("working tree is not clean; commit or stash before push/PR handoff")

    remote_lines = git_output(repo, "remote", "-v").splitlines()
    origin_fetch = next((line for line in remote_lines if line.startswith("origin\t") and "(fetch)" in line), None)
    if origin_fetch is None:
        raise SystemExit("origin remote is missing")
    remote_url = origin_fetch.split("\t", 1)[1].split(" ", 1)[0]
    web_origin = normalize_origin_url(remote_url)
    base_branch_exists = remote_branch_exists(repo, args.base)
    bootstrap_base_push = branch == args.base and not base_branch_exists

    if branch == args.base and not bootstrap_base_push:
        raise SystemExit(f"refusing PR handoff from base branch '{args.base}'; create or switch to a PR branch first")
    if args.create_pr and branch == args.base:
        raise SystemExit(f"cannot create a PR from base branch '{args.base}'; push the bootstrap branch first")

    print(f"repo: {repo}")
    print(f"branch: {branch}")
    print(f"base: {args.base}")
    print(f"origin: {remote_url}")
    print(f"push_command: git -C {repo} push -u origin {branch}")
    if bootstrap_base_push:
        print("handoff_mode: bootstrap-base-push")
    if web_origin:
        print(f"compare_url: {compare_url(web_origin, args.base, branch)}")
    else:
        print("compare_url: unavailable (non-GitHub remote or unsupported remote format)")

    if args.push:
        subprocess.run(["git", "-C", str(repo), "push", "-u", "origin", branch], check=True)

    if args.create_pr:
        gh = resolve_gh()
        if gh is None:
            raise SystemExit("gh is not installed; use the printed compare_url to open the PR manually")
        if not args.push and not remote_branch_exists(repo, branch):
            raise SystemExit(
                f"branch '{branch}' is not published on origin; push it first or rerun with --push before --create-pr"
            )

        cmd = [gh, "pr", "create", "--base", args.base, "--head", branch]
        if args.title:
            cmd.extend(["--title", args.title])
        if args.body_file:
            cmd.extend(["--body-file", args.body_file])
        if not (args.title and args.body_file):
            cmd.append("--fill-first")
        if args.draft:
            cmd.append("--draft")
        subprocess.run(cmd, check=True, cwd=repo)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
