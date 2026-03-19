#!/usr/bin/env python3
"""Resolve maintainer-local defaults for skills-github-publisher."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True


def candidate_paths() -> list[Path]:
    candidates: list[Path] = []
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        candidates.append(Path(codex_home).expanduser() / "private" / "skills-github-publisher.json")
    candidates.append(Path.home() / ".codex" / "private" / "skills-github-publisher.json")
    return candidates


def load_first_config() -> tuple[Path | None, dict]:
    for path in candidate_paths():
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if not isinstance(payload, dict):
            raise SystemExit(f"local config is not a JSON object: {path}")
        return path, payload
    return None, {}


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve local defaults for skills-github-publisher.")
    parser.add_argument("--key", help="Return only one config key.")
    parser.add_argument("--path-only", action="store_true", help="Print only the resolved config file path.")
    args = parser.parse_args()

    config_path, payload = load_first_config()

    if args.path_only:
        if config_path is not None:
            print(config_path)
        return

    result = dict(payload)
    if config_path is not None:
        result["_config_path"] = str(config_path)

    if args.key:
        value = result.get(args.key)
        if value is None:
            return
        if isinstance(value, (dict, list)):
            print(json.dumps(value, ensure_ascii=False, indent=2))
        else:
            print(value)
        return

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
