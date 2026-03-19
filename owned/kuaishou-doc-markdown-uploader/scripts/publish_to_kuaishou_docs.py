#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


DEFAULT_DOCS_URL = "https://docs.corp.kuaishou.com/home"


class PublishError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Safely publish local Markdown to Kuaishou Docs.")
    parser.add_argument("markdown_path", type=Path)
    parser.add_argument("--asset-root", type=Path, action="append", default=[])
    parser.add_argument("--docs-url", default=DEFAULT_DOCS_URL)
    parser.add_argument("--work-dir", type=Path)
    parser.add_argument("--allow-raw-html", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--keep-work-dir", action="store_true")
    parser.add_argument("--keep-browser-open", action="store_true")
    parser.add_argument("--max-image-bytes", type=int, default=10 * 1024 * 1024)
    parser.add_argument("--max-total-image-bytes", type=int, default=25 * 1024 * 1024)
    return parser.parse_args()


def run_prepare(
    script_path: Path,
    *,
    markdown_path: Path,
    work_dir: Path,
    asset_roots: list[Path],
    allow_raw_html: bool,
    max_image_bytes: int,
    max_total_image_bytes: int,
) -> dict[str, object]:
    cmd = [
        sys.executable,
        str(script_path),
        str(markdown_path),
        "--output-dir",
        str(work_dir),
        "--max-image-bytes",
        str(max_image_bytes),
        "--max-total-image-bytes",
        str(max_total_image_bytes),
    ]
    if allow_raw_html:
        cmd.append("--allow-raw-html")
    for root in asset_roots:
        cmd.extend(["--asset-root", str(root)])

    completed = subprocess.run(cmd, capture_output=True, text=True)
    if completed.returncode != 0:
        raise PublishError(completed.stderr.strip() or completed.stdout.strip() or "Bundle preparation failed.")
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise PublishError(f"Failed to parse bundle generator output: {exc}") from exc


def run_upload(
    script_path: Path,
    *,
    bundle_json: Path,
    docs_url: str,
    keep_browser_open: bool,
) -> None:
    node_bin = shutil.which("node")
    if not node_bin:
        raise PublishError("Node.js is required for the browser uploader but was not found in PATH.")

    cmd = [node_bin, str(script_path), "--bundle-json", str(bundle_json), "--docs-url", docs_url]
    if keep_browser_open:
        cmd.append("--keep-browser-open")
    completed = subprocess.run(cmd)
    if completed.returncode != 0:
        raise PublishError(f"Browser upload failed with exit code {completed.returncode}.")


def main() -> int:
    args = parse_args()
    base_dir = Path(__file__).resolve().parent
    prepare_script = base_dir / "prepare_markdown_bundle.py"
    upload_script = base_dir / "upload_via_cdp.mjs"

    markdown_path = args.markdown_path.expanduser().resolve()
    if not markdown_path.exists() or not markdown_path.is_file():
        raise PublishError(f"Markdown file does not exist: {markdown_path}")

    created_temp_dir = False
    if args.work_dir:
        work_dir = args.work_dir.expanduser().resolve()
        work_dir.mkdir(parents=True, exist_ok=True)
    else:
        work_dir = Path(tempfile.mkdtemp(prefix="kuaishou-doc-upload-"))
        created_temp_dir = True

    keep_work_dir = args.keep_work_dir or args.dry_run
    success = False
    try:
        result = run_prepare(
            prepare_script,
            markdown_path=markdown_path,
            work_dir=work_dir,
            asset_roots=[root.expanduser().resolve() for root in args.asset_root],
            allow_raw_html=args.allow_raw_html,
            max_image_bytes=args.max_image_bytes,
            max_total_image_bytes=args.max_total_image_bytes,
        )
        stats = result.get("stats", {})
        print(
            f"[prepared] blocks={stats.get('block_count', '?')} "
            f"images={stats.get('image_count', '?')} "
            f"image_bytes={stats.get('total_image_bytes', '?')}"
        )
        print(f"[bundle] {result['bundle_json']}")
        print(f"[preview] {result['preview_html']}")
        print(f"[manifest] {result['manifest_json']}")

        if args.dry_run:
            print("[dry-run] bundle generated only; browser upload was skipped.")
            return 0

        run_upload(
            upload_script,
            bundle_json=Path(str(result["bundle_json"])).resolve(),
            docs_url=args.docs_url,
            keep_browser_open=args.keep_browser_open,
        )
        print("[done] upload flow completed.")
        success = True
        return 0
    except PublishError as exc:
        print(f"[publish-error] {exc}", file=sys.stderr)
        print(f"[work-dir] preserved at {work_dir}", file=sys.stderr)
        return 2
    finally:
        if created_temp_dir and work_dir.exists() and not keep_work_dir and success:
            shutil.rmtree(work_dir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
