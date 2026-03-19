#!/usr/bin/env python3
"""Preflight scan for publishing local Codex skills to GitHub."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


IGNORE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "coverage",
}

TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".py",
    ".sh",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".conf",
    ".c",
    ".cc",
    ".cpp",
    ".h",
    ".hpp",
    ".java",
    ".kt",
    ".kts",
    ".gradle",
    ".rb",
    ".go",
    ".rs",
    ".xml",
    ".html",
    ".css",
    ".scss",
    ".sql",
}

HARD_SECRET_PATTERNS = [
    re.compile(r"BEGIN PRIVATE KEY"),
    re.compile(r"BEGIN (?:RSA|OPENSSH|EC|DSA) PRIVATE KEY"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9._-]{8,}\.[A-Za-z0-9._-]{8,}\b"),
    re.compile(r"\bhttps://hooks\.slack\.com/services/[A-Za-z0-9/_-]{20,}\b"),
]

HEADER_SECRET_PATTERNS = [
    re.compile(r"""(?ix)\bauthorization\b[^"'`\n]{0,20}["']?\s*[:=]\s*["']bearer\s+[A-Za-z0-9._\-+/=]{12,}["']"""),
    re.compile(r"""(?ix)\bauthorization\b[^"'`\n]{0,20}["']?\s*[:=]\s*["']basic\s+[A-Za-z0-9._\-+/=]{12,}["']"""),
    re.compile(r"""(?ix)\bx-api-key\b[^"'`\n]{0,20}["']?\s*[:=]\s*["'][^"'\n]{12,}["']"""),
    re.compile(r"""(?ix)\bcookie\b[^"'`\n]{0,20}["']?\s*[:=]\s*["'][^"'\n]{16,}["']"""),
]

URI_CREDENTIAL_PATTERN = re.compile(r"""(?i)\b[a-z][a-z0-9+.-]*://[^/\s:@]+:[^/\s@]+@""")

ASSIGNMENT_PATTERN = re.compile(
    r"""(?x)
    (?P<key>["']?[A-Za-z0-9_.-]+["']?)
    \s*
    (?:
      =
      |
      :
    )
    \s*
    (?P<quote>["'])
    (?P<value>[^"'\n]{6,})
    (?P=quote)
    """
)

UNQUOTED_ASSIGNMENT_PATTERN = re.compile(
    r"""(?x)
    (?P<key>["']?[A-Za-z0-9_.-]+["']?)
    \s*
    (?:
      =
      |
      :
    )
    \s*
    (?P<value>[^\s"'`#]{6,})
    """
)

ABSOLUTE_PATH_PATTERN = re.compile(
    r"""(?x)
    (
      /Users/[^/\s]+/
      |
      /home/[^/\s]+/
      |
      [A-Za-z]:\\Users\\[^\\\s]+\\
    )
    """
)

PLACEHOLDER_MARKERS = (
    "example",
    "dummy",
    "placeholder",
    "your_",
    "your-",
    "replace-me",
    "changeme",
    "test",
    "sample",
    "fake",
    "mock",
    "openai-key",
    "google-key",
    "replace_with",
    "insert_",
    "set_me",
    "todo",
)

JUNK_NAMES = {
    ".DS_Store",
    "cookies.json",
    "consent.json",
    ".npmrc",
    ".pypirc",
    ".netrc",
    ".dockercfg",
    "id_rsa",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
    "credentials.json",
    "service-account.json",
    "service_account.json",
    "client_secret.json",
}

JUNK_SUFFIXES = {
    ".pyc",
    ".db",
    ".sqlite",
    ".pem",
    ".key",
    ".p12",
    ".pfx",
    ".kdbx",
    ".ovpn",
}

JUNK_PATH_PARTS = {
    "__pycache__",
    "node_modules",
    "sessions",
    "chrome-profile",
    ".aws",
    ".ssh",
    ".kube",
    ".gnupg",
}

REVIEW_DIR_NAMES = {
    ".system": "built_in_system_tree",
    "vendor": "third_party_content",
    "third-party": "third_party_content",
}

ORIGIN_METADATA_PREFIXES = (
    "ORIGIN",
    "ATTRIBUTION",
    "PROVENANCE",
    "UPSTREAM",
    "SOURCE",
    "THIRD_PARTY",
)

LICENSE_METADATA_PREFIXES = (
    "LICENSE",
    "LICENSES",
    "COPYING",
    "NOTICE",
    "THIRD_PARTY_LICENSES",
)

INCOMPLETE_METADATA_MARKERS = (
    "[todo]",
    "todo:",
    "tbd",
    "pending",
    "unknown",
    "unverified",
    "confirm before release",
    "fill in before release",
    "required before public release",
)


@dataclass
class LineFinding:
    path: str
    line: int
    reason: str
    excerpt: str


def should_scan_text(path: Path) -> bool:
    if path.suffix.lower() in TEXT_SUFFIXES:
        return True
    return path.name in {"SKILL.md", "AGENTS.md", ".gitignore"}


def is_placeholder_value(value: str) -> bool:
    lowered = value.strip().lower()
    if not lowered:
        return False
    if lowered.startswith(("$", "${", "%", "<")):
        return True
    if lowered.startswith(("{{", "<<")):
        return True
    if any(marker in lowered for marker in ("process.env", "system.getenv", "os.environ", "getenv(")):
        return True
    return any(marker in lowered for marker in PLACEHOLDER_MARKERS)


def is_placeholder_uri_credential(match_text: str) -> bool:
    lowered = match_text.lower()
    return any(marker in lowered for marker in ("user:pass@", "username:password@", "example:example@", "demo:demo@"))


def is_sensitive_key(raw_key: str) -> bool:
    key = raw_key.strip().strip("'\"").lower()
    if not key:
        return False
    parts = [part for part in re.split(r"[_\-.]+", key) if part]
    if not parts:
        return False
    last = parts[-1]
    if last in {"secret", "password", "passwd"}:
        return True
    if len(parts) >= 2 and parts[-2:] in (
        ["api", "key"],
        ["client", "secret"],
        ["access", "key"],
        ["access", "token"],
        ["auth", "token"],
        ["bearer", "token"],
        ["refresh", "token"],
        ["session", "token"],
    ):
        return True
    if key in {"apikey", "clientsecret", "accesskey", "accesstoken", "refreshtoken", "sessionid", "csrftoken"}:
        return True
    return False


def looks_like_unquoted_secret_literal(value: str) -> bool:
    candidate = value.strip().strip(",;)}]\"'")
    if not candidate or is_placeholder_value(candidate):
        return False
    lowered = candidate.lower()
    if any(token in lowered for token in ("<", ">", "|", "record<", "array<")):
        return False
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*", candidate):
        return False
    if any(ch in candidate for ch in "[](){}") and not any(ch in candidate for ch in "-_=+/@:"):
        return False
    if candidate.startswith(("sk-", "ghp_", "AKIA", "AIza", "xox", "eyJ", "ya29.")):
        return True
    if len(candidate) < 12:
        return False
    if not any(ch.isdigit() for ch in candidate) and not any(ch in candidate for ch in "-_=+/@:"):
        return False
    return True


def redact_excerpt(line: str, match_text: str) -> str:
    clean = line.strip()
    if not clean:
        return "<redacted>"
    if match_text:
        clean = clean.replace(match_text, "<redacted>")
    if len(clean) > 160:
        clean = clean[:157] + "..."
    return clean


def walk_files(root: Path) -> Iterable[Path]:
    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        current_path = Path(current_root)
        for name in filenames:
            yield current_path / name


def collect_junk_paths(root: Path) -> list[str]:
    findings: list[str] = []
    for path in walk_files(root):
        rel = str(path.relative_to(root))
        parts = set(path.parts)
        if path.name in JUNK_NAMES:
            findings.append(rel)
            continue
        if path.suffix.lower() in JUNK_SUFFIXES:
            findings.append(rel)
            continue
        if parts & JUNK_PATH_PARTS:
            findings.append(rel)
            continue
        if path.name.startswith(".env"):
            findings.append(rel)
            continue
    return sorted(set(findings))


def collect_review_dirs(root: Path) -> dict[str, list[str]]:
    findings = {
        "built_in_system_tree": [],
        "third_party_content": [],
        "danger_skills": [],
    }
    for current_root, dirnames, _filenames in os.walk(root):
        current_path = Path(current_root)
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for dirname in dirnames:
            child = current_path / dirname
            rel = str(child.relative_to(root))
            if dirname in REVIEW_DIR_NAMES:
                findings[REVIEW_DIR_NAMES[dirname]].append(rel)
            if dirname.startswith("danger-") or "-danger-" in dirname:
                findings["danger_skills"].append(rel)
    for key in findings:
        findings[key] = sorted(set(findings[key]))
    return findings


def file_has_prefix(name: str, prefixes: tuple[str, ...]) -> bool:
    normalized = name.replace("-", "_").upper()
    return any(normalized.startswith(prefix) for prefix in prefixes)


def metadata_file_is_complete(path: Path) -> bool:
    try:
        content = path.read_text(encoding="utf-8", errors="replace").strip()
    except OSError:
        return False
    if not content:
        return False
    lowered = content.lower()
    return not any(marker in lowered for marker in INCOMPLETE_METADATA_MARKERS)


def dir_has_metadata_file(directory: Path, prefixes: tuple[str, ...]) -> bool:
    if not directory.exists() or not directory.is_dir():
        return False
    try:
        for child in directory.iterdir():
            if child.is_file() and file_has_prefix(child.name, prefixes) and metadata_file_is_complete(child):
                return True
    except OSError:
        return False
    return False


def package_json_has_origin_metadata(package_json_path: Path) -> bool:
    if not package_json_path.exists() or not package_json_path.is_file():
        return False
    try:
        payload = json.loads(package_json_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    repository = payload.get("repository")
    homepage = payload.get("homepage")
    bugs = payload.get("bugs")
    return bool(repository or homepage or bugs)


def package_json_has_license_metadata(package_json_path: Path) -> bool:
    if not package_json_path.exists() or not package_json_path.is_file():
        return False
    try:
        payload = json.loads(package_json_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    license_field = payload.get("license")
    licenses_field = payload.get("licenses")
    return bool(license_field or licenses_field)


def third_party_scope_ancestors(unit_dir: Path, root: Path) -> list[Path]:
    ancestors: list[Path] = []
    current = unit_dir
    highest_boundary: Path | None = None
    while True:
        ancestors.append(current)
        if current.name in REVIEW_DIR_NAMES and REVIEW_DIR_NAMES[current.name] == "third_party_content":
            highest_boundary = current
        if current == root or current.parent == current:
            break
        current = current.parent
    if highest_boundary is None:
        return ancestors
    scoped: list[Path] = []
    for path in ancestors:
        scoped.append(path)
        if path == highest_boundary:
            break
    return scoped


def collect_third_party_provenance_gaps(root: Path) -> list[str]:
    gaps: list[str] = []
    seen_units: set[Path] = set()

    for current_root, dirnames, _filenames in os.walk(root):
        current_path = Path(current_root)
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for dirname in dirnames:
            if dirname not in {"third-party", "vendor"}:
                continue
            boundary_dir = current_path / dirname
            try:
                children = sorted(boundary_dir.iterdir(), key=lambda item: item.name)
            except OSError:
                continue
            for child in children:
                if not child.is_dir() or child.name in IGNORE_DIRS:
                    continue
                if child in seen_units:
                    continue
                seen_units.add(child)
                scope_dirs = third_party_scope_ancestors(child, root)
                package_json_path = child / "package.json"
                has_origin = any(dir_has_metadata_file(directory, ORIGIN_METADATA_PREFIXES) for directory in scope_dirs)
                has_license = any(dir_has_metadata_file(directory, LICENSE_METADATA_PREFIXES) for directory in scope_dirs)
                if not has_origin and package_json_has_origin_metadata(package_json_path):
                    has_origin = True
                if not has_license and package_json_has_license_metadata(package_json_path):
                    has_license = True
                if has_origin and has_license:
                    continue
                missing: list[str] = []
                if not has_origin:
                    missing.append("origin")
                if not has_license:
                    missing.append("license")
                rel = str(child.relative_to(root))
                gaps.append(f"{rel} missing {', '.join(missing)} metadata")

    return sorted(gaps)


def collect_line_findings(root: Path) -> tuple[list[LineFinding], list[LineFinding]]:
    secret_findings: list[LineFinding] = []
    absolute_path_findings: list[LineFinding] = []

    for path in walk_files(root):
        if (
            path.name == "preflight_scan.py"
            and path.parent.name == "scripts"
            and (path.parent.parent.name == "skills-github-publisher" or root.name == "skills-github-publisher")
        ):
            continue
        if not should_scan_text(path):
            continue

        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        rel = str(path.relative_to(root))
        for line_no, line in enumerate(content.splitlines(), start=1):
            for pattern in HARD_SECRET_PATTERNS:
                match = pattern.search(line)
                if match:
                    secret_findings.append(
                        LineFinding(
                            path=rel,
                            line=line_no,
                            reason="hard_secret_pattern",
                            excerpt=redact_excerpt(line, match.group(0)),
                        )
                    )
                    break
            else:
                for pattern in HEADER_SECRET_PATTERNS:
                    match = pattern.search(line)
                    if match:
                        secret_findings.append(
                            LineFinding(
                                path=rel,
                                line=line_no,
                                reason="hardcoded_auth_header",
                                excerpt=redact_excerpt(line, match.group(0)),
                            )
                        )
                        break
                else:
                    uri_match = URI_CREDENTIAL_PATTERN.search(line)
                    if uri_match:
                        match_text = uri_match.group(0)
                        if not is_placeholder_uri_credential(match_text):
                            secret_findings.append(
                                LineFinding(
                                    path=rel,
                                    line=line_no,
                                    reason="credential_in_uri",
                                    excerpt=redact_excerpt(line, match_text),
                                )
                            )
                        continue
                    match = ASSIGNMENT_PATTERN.search(line)
                    if match:
                        key = match.group("key")
                        value = match.group("value")
                        if is_sensitive_key(key) and not is_placeholder_value(value):
                            secret_findings.append(
                                LineFinding(
                                    path=rel,
                                    line=line_no,
                                    reason="secret_like_assignment",
                                    excerpt=redact_excerpt(line, value),
                                )
                            )
                    else:
                        match = UNQUOTED_ASSIGNMENT_PATTERN.search(line)
                        if match:
                            key = match.group("key")
                            value = match.group("value")
                            if is_sensitive_key(key) and looks_like_unquoted_secret_literal(value):
                                secret_findings.append(
                                    LineFinding(
                                        path=rel,
                                        line=line_no,
                                        reason="secret_like_assignment",
                                        excerpt=redact_excerpt(line, value),
                                    )
                                )

            path_match = ABSOLUTE_PATH_PATTERN.search(line)
            if path_match:
                matched_path = path_match.group(0)
                if "<" in matched_path or ">" in matched_path:
                    continue
                if any(char in matched_path for char in "[](){}+?\\"):
                    continue
                absolute_path_findings.append(
                    LineFinding(
                        path=rel,
                        line=line_no,
                        reason="absolute_local_path",
                        excerpt=redact_excerpt(line, matched_path),
                    )
                )

    return secret_findings, absolute_path_findings


def to_serializable(findings: list[LineFinding]) -> list[dict[str, object]]:
    return [asdict(item) for item in findings]


def print_section(title: str) -> None:
    print(f"\n[{title}]")


def print_line_findings(title: str, findings: list[LineFinding], max_matches: int) -> None:
    print_section(title)
    if not findings:
        print("0")
        return
    print(len(findings))
    for item in findings[:max_matches]:
        print(f"- {item.path}:{item.line} {item.reason}: {item.excerpt}")
    remaining = len(findings) - max_matches
    if remaining > 0:
        print(f"- ... {remaining} more")


def print_path_findings(title: str, paths: list[str], max_matches: int) -> None:
    print_section(title)
    if not paths:
        print("0")
        return
    print(len(paths))
    for item in paths[:max_matches]:
        print(f"- {item}")
    remaining = len(paths) - max_matches
    if remaining > 0:
        print(f"- ... {remaining} more")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan skill trees before publishing them to GitHub.",
    )
    parser.add_argument(
        "--root",
        action="append",
        required=True,
        help="Root directory to scan. Repeat for multiple roots.",
    )
    parser.add_argument(
        "--json-out",
        help="Optional path to write a JSON report.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero if blocker findings are present.",
    )
    parser.add_argument(
        "--strict-provenance",
        action="store_true",
        help="Exit non-zero if third-party or vendored content lacks origin/license metadata.",
    )
    parser.add_argument(
        "--max-matches",
        type=int,
        default=20,
        help="Maximum matches to print per section.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    all_results: dict[str, object] = {"roots": []}
    blocker_total = 0
    provenance_gap_total = 0

    for root_arg in args.root:
        root = Path(root_arg).expanduser().resolve()
        if not root.exists():
            print(f"[ERROR] Root not found: {root}", file=sys.stderr)
            return 2
        if not root.is_dir():
            print(f"[ERROR] Root is not a directory: {root}", file=sys.stderr)
            return 2

        secret_findings, absolute_path_findings = collect_line_findings(root)
        junk_paths = collect_junk_paths(root)
        review_dirs = collect_review_dirs(root)
        provenance_gaps = collect_third_party_provenance_gaps(root)

        blocker_count = len(secret_findings) + len(absolute_path_findings) + len(junk_paths)
        blocker_total += blocker_count
        provenance_gap_total += len(provenance_gaps)

        print(f"\n=== {root} ===")
        print_line_findings("secret_like_matches", secret_findings, args.max_matches)
        print_line_findings("absolute_path_matches", absolute_path_findings, args.max_matches)
        print_path_findings("junk_paths", junk_paths, args.max_matches)
        print_path_findings("built_in_system_tree", review_dirs["built_in_system_tree"], args.max_matches)
        print_path_findings("third_party_content", review_dirs["third_party_content"], args.max_matches)
        print_path_findings("third_party_provenance_gaps", provenance_gaps, args.max_matches)
        print_path_findings("danger_skills", review_dirs["danger_skills"], args.max_matches)

        all_results["roots"].append(
            {
                "root": str(root),
                "blocker_count": blocker_count,
                "provenance_gap_count": len(provenance_gaps),
                "secret_like_matches": to_serializable(secret_findings),
                "absolute_path_matches": to_serializable(absolute_path_findings),
                "junk_paths": junk_paths,
                "review_dirs": review_dirs,
                "third_party_provenance_gaps": provenance_gaps,
            }
        )

    if args.json_out:
        output_path = Path(args.json_out).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(all_results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"\n[json_report]\n- {output_path}")

    if args.strict and blocker_total > 0:
        return 1
    if args.strict_provenance and provenance_gap_total > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
