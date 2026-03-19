#!/usr/bin/env python3
"""Compile Python files without leaving __pycache__ in the target tree."""

from __future__ import annotations

import argparse
import py_compile
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Syntax-check Python files without polluting the repo with __pycache__.",
    )
    parser.add_argument("files", nargs="+", help="Python files to compile.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    failures = 0

    with tempfile.TemporaryDirectory(prefix="safe-pycache-") as pycache_dir:
        original_prefix = sys.pycache_prefix
        sys.pycache_prefix = pycache_dir
        try:
            for raw_path in args.files:
                path = Path(raw_path)
                if not path.is_file():
                    print(f"[missing] {path}", file=sys.stderr)
                    failures += 1
                    continue
                try:
                    py_compile.compile(str(path), doraise=True)
                    print(f"[ok] {path}")
                except py_compile.PyCompileError as exc:
                    print(f"[compile-error] {path}", file=sys.stderr)
                    print(exc.msg, file=sys.stderr)
                    failures += 1
        finally:
            sys.pycache_prefix = original_prefix

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
