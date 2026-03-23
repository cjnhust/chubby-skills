#!/usr/bin/env python3
"""Check git author/committer identity for publish-safe values."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from preflight_scan import (
    FORBID_LITERALS_FILE_ENV,
    LOCAL_POLICY_FILE_ENV,
    compile_regexes,
    default_local_policy_path,
    find_forbidden_literal,
    normalize_forbidden_literals,
    parse_forbidden_literals_env,
    read_forbidden_literals_file,
    read_local_policy_file,
)
from sync_incremental_update import load_local_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check git identity metadata before publishing.")
    parser.add_argument(
        "--root",
        help="Git repository root. Defaults to local default_publish_repo.",
    )
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if blocked identity data is found.")
    parser.add_argument(
        "--forbid-literal",
        action="append",
        default=[],
        help="Case-insensitive literal that must not appear in author/committer identity.",
    )
    parser.add_argument(
        "--forbid-literal-file",
        help="Path to a local private file containing one forbidden literal per line.",
    )
    parser.add_argument(
        "--local-policy-file",
        help="Path to a local private JSON policy file. Supported keys: forbid_literals, forbid_regexes.",
    )
    return parser.parse_args()


def git_output(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True, encoding="utf-8", errors="replace")


def resolve_repo_root(explicit_root: str | None) -> Path:
    if explicit_root:
        return Path(explicit_root).expanduser().resolve()

    config = load_local_config()
    publish_repo = config.get("default_publish_repo")
    if isinstance(publish_repo, str) and publish_repo:
        return Path(publish_repo).expanduser().resolve()

    raise SystemExit("publish repo is not configured; pass --root or set default_publish_repo in local config")


def safe_git_config(repo: Path, *args: str) -> str | None:
    try:
        value = git_output(repo, "config", *args).strip()
    except subprocess.CalledProcessError:
        return None
    return value or None


def field_block_reason(value: str, forbidden_literals: list[str], forbidden_regexes: list[object]) -> str | None:
    literal = find_forbidden_literal(value, forbidden_literals)
    if literal:
        return f"forbidden literal {literal!r}"
    for pattern in forbidden_regexes:
        if pattern.search(value):
            return f"forbidden regex {pattern.pattern!r}"
    return None


def main() -> int:
    args = parse_args()
    repo = resolve_repo_root(args.root)
    if not repo.exists() or not repo.is_dir():
        raise SystemExit(f"Repository root not found: {repo}")

    try:
        git_output(repo, "rev-parse", "--git-dir")
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"Not a git repository: {repo}") from exc

    forbidden_literal_values: list[str] = []
    forbidden_regex_texts: list[str] = []
    forbidden_literal_values.extend(args.forbid_literal)
    forbidden_literal_values.extend(parse_forbidden_literals_env())

    policy_path: Path | None = None
    if args.local_policy_file:
        policy_path = Path(args.local_policy_file).expanduser()
    else:
        from_env = os.environ.get(LOCAL_POLICY_FILE_ENV, "").strip()
        if from_env:
            policy_path = Path(from_env).expanduser()
        else:
            policy_path = default_local_policy_path()

    if policy_path is not None:
        local_policy = read_local_policy_file(policy_path)
        forbidden_literal_values.extend(local_policy.forbid_literals)
        forbidden_regex_texts.extend(local_policy.forbid_regexes)

    forbid_literal_file = args.forbid_literal_file or os.environ.get(FORBID_LITERALS_FILE_ENV, "")
    if forbid_literal_file.strip():
        forbidden_literal_values.extend(read_forbidden_literals_file(Path(forbid_literal_file).expanduser()))

    forbidden_literals = normalize_forbidden_literals(forbidden_literal_values)
    forbidden_regexes = compile_regexes(forbidden_regex_texts, "forbid_regexes")

    findings: list[str] = []

    local_name = safe_git_config(repo, "--get", "user.name")
    local_email = safe_git_config(repo, "--get", "user.email")
    global_name = safe_git_config(repo, "--global", "--get", "user.name")
    global_email = safe_git_config(repo, "--global", "--get", "user.email")

    config_fields = [
        ("effective git user.name", local_name or global_name or ""),
        ("effective git user.email", local_email or global_email or ""),
    ]

    for label, value in config_fields:
        reason = field_block_reason(value, forbidden_literals, forbidden_regexes)
        if reason:
            findings.append(f"{label}: {reason} in {value!r}")

    log_output = git_output(repo, "log", "--format=%H%x09%an%x09%ae%x09%cn%x09%ce%x09%s")
    for raw_line in log_output.splitlines():
        sha, author_name, author_email, committer_name, committer_email, subject = raw_line.split("\t", 5)
        for label, value in (
            ("author name", author_name),
            ("author email", author_email),
            ("committer name", committer_name),
            ("committer email", committer_email),
        ):
            reason = field_block_reason(value, forbidden_literals, forbidden_regexes)
            if reason:
                findings.append(f"{sha[:7]} {label}: {reason} in {value!r}; subject={subject!r}")

    print(f"\n=== git identity audit: {repo} ===")
    if not findings:
        print("[git_identity_matches]")
        print("0")
        return 0

    print("[git_identity_matches]")
    print(len(findings))
    for item in findings:
        print(f"- {item}")
    return 1 if args.strict else 0


if __name__ == "__main__":
    raise SystemExit(main())
