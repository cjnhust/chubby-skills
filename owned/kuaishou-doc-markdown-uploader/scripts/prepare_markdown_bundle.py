#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import dataclasses
import html
import json
import mimetypes
import re
import sys
from pathlib import Path


LIST_ITEM_RE = re.compile(r"^(\s*)([-+*]|\d+\.)\s+(.*)$")
HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.*?)(?:\s+#*)?\s*$")
FENCE_RE = re.compile(r"^\s*(```+|~~~+)\s*([A-Za-z0-9_+-]*)\s*$")
HR_RE = re.compile(r"^\s{0,3}((\*\s*){3,}|(-\s*){3,}|(_\s*){3,})\s*$")
BLOCKQUOTE_RE = re.compile(r"^\s{0,3}>\s?(.*)$")
REF_DEF_RE = re.compile(
    r'^\s{0,3}\[([^\]]+)\]:\s*(<[^>]+>|[^\s]+)(?:\s+(?:"([^"]*)"|\'([^\']*)\'|\(([^)]*)\)))?\s*$'
)
HTML_IMG_RE = re.compile(r'(<img\b[^>]*\bsrc\s*=\s*)(["\'])(.+?)(\2)', re.IGNORECASE)
REMOTE_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


class BundleError(RuntimeError):
    pass


@dataclasses.dataclass
class AssetEntry:
    original_ref: str
    resolved_path: str
    mime_type: str
    size_bytes: int


def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def strip_frontmatter(text: str) -> tuple[str, str | None]:
    if not text.startswith("---\n"):
        return text, None
    end = text.find("\n---\n", 4)
    if end == -1:
        return text, None
    return text[end + 5 :], text[4:end]


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


class AssetResolver:
    def __init__(
        self,
        *,
        asset_roots: list[Path],
        max_image_bytes: int,
        max_total_image_bytes: int,
    ) -> None:
        self.asset_roots = [root.resolve() for root in asset_roots]
        self.max_image_bytes = max_image_bytes
        self.max_total_image_bytes = max_total_image_bytes
        self.total_image_bytes = 0
        self.assets: list[AssetEntry] = []
        self._cache: dict[Path, str] = {}

    def resolve_image_src(self, raw_src: str, base_dir: Path) -> str:
        src = raw_src.strip()
        if not src:
            raise BundleError("Empty image source is not allowed.")
        if src.startswith("data:"):
            return src
        if src.startswith("#"):
            raise BundleError(f"Fragment-only image reference is not supported: {raw_src}")
        if REMOTE_SCHEME_RE.match(src):
            raise BundleError(
                f"Remote or non-file image reference is not allowed without a safe adapter: {raw_src}"
            )

        candidate = Path(src).expanduser()
        if not candidate.is_absolute():
            candidate = (base_dir / candidate).resolve()
        else:
            candidate = candidate.resolve()

        if not candidate.exists():
            raise BundleError(f"Referenced image does not exist: {candidate}")
        if not candidate.is_file():
            raise BundleError(f"Referenced image is not a file: {candidate}")
        if not any(is_relative_to(candidate, root) for root in self.asset_roots):
            roots = ", ".join(str(root) for root in self.asset_roots)
            raise BundleError(
                f"Image path escapes the allowed roots. Add --asset-root explicitly if intended: {candidate} | allowed: {roots}"
            )

        cached = self._cache.get(candidate)
        if cached:
            return cached

        mime_type, _ = mimetypes.guess_type(candidate.name)
        if not mime_type or not mime_type.startswith("image/"):
            raise BundleError(f"Referenced file is not a supported image: {candidate}")

        size_bytes = candidate.stat().st_size
        if size_bytes > self.max_image_bytes:
            raise BundleError(
                f"Image exceeds --max-image-bytes ({self.max_image_bytes}): {candidate} ({size_bytes})"
            )

        new_total = self.total_image_bytes + size_bytes
        if new_total > self.max_total_image_bytes:
            raise BundleError(
                f"Total inlined image size exceeds --max-total-image-bytes ({self.max_total_image_bytes})."
            )

        encoded = base64.b64encode(candidate.read_bytes()).decode("ascii")
        data_url = f"data:{mime_type};base64,{encoded}"
        self.total_image_bytes = new_total
        self.assets.append(
            AssetEntry(
                original_ref=raw_src,
                resolved_path=str(candidate),
                mime_type=mime_type,
                size_bytes=size_bytes,
            )
        )
        self._cache[candidate] = data_url
        return data_url


class MarkdownConverter:
    def __init__(self, *, asset_resolver: AssetResolver, allow_raw_html: bool) -> None:
        self.asset_resolver = asset_resolver
        self.allow_raw_html = allow_raw_html

    def convert(self, markdown_text: str, source_dir: Path) -> dict[str, object]:
        body_text, frontmatter = strip_frontmatter(normalize_newlines(markdown_text))
        lines = body_text.split("\n")
        refs, body_lines = self._extract_reference_definitions(lines)
        blocks, _ = self._parse_blocks(body_lines, 0, source_dir, refs)
        html_body = "\n".join(blocks).strip()
        plain_text = body_text.strip()
        return {
            "frontmatter": frontmatter,
            "plain_text": plain_text,
            "blocks": blocks,
            "html": html_body,
            "reference_definitions": refs,
        }

    def _extract_reference_definitions(self, lines: list[str]) -> tuple[dict[str, dict[str, str]], list[str]]:
        refs: dict[str, dict[str, str]] = {}
        body_lines: list[str] = []
        for line in lines:
            match = REF_DEF_RE.match(line)
            if not match:
                body_lines.append(line)
                continue
            key = match.group(1).strip().lower()
            destination = match.group(2).strip()
            if destination.startswith("<") and destination.endswith(">"):
                destination = destination[1:-1]
            title = match.group(3) or match.group(4) or match.group(5) or ""
            refs[key] = {"url": destination, "title": title}
        return refs, body_lines

    def _parse_blocks(
        self,
        lines: list[str],
        index: int,
        source_dir: Path,
        refs: dict[str, dict[str, str]],
    ) -> tuple[list[str], int]:
        blocks: list[str] = []
        while index < len(lines):
            line = lines[index]
            if not line.strip():
                index += 1
                continue

            fence_match = FENCE_RE.match(line)
            if fence_match:
                block, index = self._parse_fence(lines, index, fence_match)
                blocks.append(block)
                continue

            heading_match = HEADING_RE.match(line)
            if heading_match:
                level = len(heading_match.group(1))
                content = self._render_inline(heading_match.group(2).strip(), source_dir, refs)
                blocks.append(f"<h{level}>{content}</h{level}>")
                index += 1
                continue

            if HR_RE.match(line):
                blocks.append("<hr />")
                index += 1
                continue

            if self._is_table_header(lines, index):
                block, index = self._parse_table(lines, index, source_dir, refs)
                blocks.append(block)
                continue

            if LIST_ITEM_RE.match(line):
                block, index = self._parse_list(lines, index, source_dir, refs)
                blocks.append(block)
                continue

            if BLOCKQUOTE_RE.match(line):
                block, index = self._parse_blockquote(lines, index, source_dir, refs)
                blocks.append(block)
                continue

            if self.allow_raw_html and self._looks_like_html_block(line):
                block, index = self._parse_raw_html(lines, index, source_dir)
                blocks.append(block)
                continue

            paragraph_lines: list[str] = []
            while index < len(lines):
                current = lines[index]
                if not current.strip():
                    break
                if paragraph_lines and self._is_block_start(lines, index):
                    break
                paragraph_lines.append(current)
                index += 1
            merged = " ".join(part.strip() for part in paragraph_lines if part.strip())
            blocks.append(f"<p>{self._render_inline(merged, source_dir, refs)}</p>")
        return blocks, index

    def _parse_fence(
        self, lines: list[str], index: int, opening_match: re.Match[str]
    ) -> tuple[str, int]:
        fence = opening_match.group(1)
        language = opening_match.group(2).strip()
        index += 1
        code_lines: list[str] = []
        while index < len(lines):
            current = lines[index]
            if re.match(rf"^\s*{re.escape(fence)}\s*$", current):
                index += 1
                break
            code_lines.append(current)
            index += 1
        escaped_code = html.escape("\n".join(code_lines))
        class_attr = f' class="language-{html.escape(language)}"' if language else ""
        return f"<pre><code{class_attr}>{escaped_code}</code></pre>", index

    def _parse_blockquote(
        self,
        lines: list[str],
        index: int,
        source_dir: Path,
        refs: dict[str, dict[str, str]],
    ) -> tuple[str, int]:
        inner_lines: list[str] = []
        while index < len(lines):
            current = lines[index]
            if not current.strip():
                inner_lines.append("")
                index += 1
                continue
            match = BLOCKQUOTE_RE.match(current)
            if not match:
                break
            inner_lines.append(match.group(1))
            index += 1
        inner_blocks, _ = self._parse_blocks(inner_lines, 0, source_dir, refs)
        return f"<blockquote>{''.join(inner_blocks)}</blockquote>", index

    def _parse_list(
        self,
        lines: list[str],
        index: int,
        source_dir: Path,
        refs: dict[str, dict[str, str]],
    ) -> tuple[str, int]:
        first = LIST_ITEM_RE.match(lines[index])
        assert first is not None
        base_indent = len(first.group(1).expandtabs(4))
        list_tag = "ol" if first.group(2).endswith(".") else "ul"
        items: list[str] = []

        while index < len(lines):
            line = lines[index]
            if not line.strip():
                index += 1
                continue
            match = LIST_ITEM_RE.match(line)
            if not match:
                break
            indent = len(match.group(1).expandtabs(4))
            current_tag = "ol" if match.group(2).endswith(".") else "ul"
            if indent != base_indent or current_tag != list_tag:
                break

            item_lines = [match.group(3)]
            index += 1
            while index < len(lines):
                current = lines[index]
                if not current.strip():
                    item_lines.append("")
                    index += 1
                    continue
                nested_match = LIST_ITEM_RE.match(current)
                nested_indent = len(nested_match.group(1).expandtabs(4)) if nested_match else None
                if nested_match and nested_indent == base_indent and current_tag == (
                    "ol" if nested_match.group(2).endswith(".") else "ul"
                ):
                    break
                if nested_match and nested_indent is not None and nested_indent < base_indent:
                    break
                if self._leading_spaces(current) <= base_indent:
                    break
                strip_width = min(self._leading_spaces(current), base_indent + 2)
                item_lines.append(current[strip_width:])
                index += 1

            item_blocks, _ = self._parse_blocks(item_lines, 0, source_dir, refs)
            if len(item_blocks) == 1 and item_blocks[0].startswith("<p>") and item_blocks[0].endswith("</p>"):
                item_html = item_blocks[0][3:-4]
            else:
                item_html = "".join(item_blocks)
            items.append(f"<li>{item_html}</li>")

        return f"<{list_tag}>{''.join(items)}</{list_tag}>", index

    def _parse_table(
        self,
        lines: list[str],
        index: int,
        source_dir: Path,
        refs: dict[str, dict[str, str]],
    ) -> tuple[str, int]:
        header_cells = self._split_table_row(lines[index])
        align_cells = self._split_table_row(lines[index + 1])
        aligns = [self._parse_table_alignment(cell) for cell in align_cells]
        index += 2
        body_rows: list[list[str]] = []
        while index < len(lines):
            line = lines[index]
            if not line.strip() or "|" not in line:
                break
            body_rows.append(self._split_table_row(line))
            index += 1

        header_html = "".join(
            self._render_table_cell("th", cell, aligns[pos] if pos < len(aligns) else "", source_dir, refs)
            for pos, cell in enumerate(header_cells)
        )
        body_html = []
        for row in body_rows:
            row_html = "".join(
                self._render_table_cell("td", cell, aligns[pos] if pos < len(aligns) else "", source_dir, refs)
                for pos, cell in enumerate(row)
            )
            body_html.append(f"<tr>{row_html}</tr>")
        tbody = f"<tbody>{''.join(body_html)}</tbody>" if body_html else ""
        return f"<table><thead><tr>{header_html}</tr></thead>{tbody}</table>", index

    def _render_table_cell(
        self,
        tag: str,
        cell_text: str,
        align: str,
        source_dir: Path,
        refs: dict[str, dict[str, str]],
    ) -> str:
        align_attr = f' style="text-align:{align}"' if align else ""
        return f"<{tag}{align_attr}>{self._render_inline(cell_text.strip(), source_dir, refs)}</{tag}>"

    def _parse_raw_html(self, lines: list[str], index: int, source_dir: Path) -> tuple[str, int]:
        html_lines: list[str] = []
        while index < len(lines):
            current = lines[index]
            if not current.strip():
                break
            html_lines.append(current)
            index += 1
            if current.strip().endswith(">") and not self._looks_like_html_block(lines[index - 1]):
                break
        fragment = "\n".join(html_lines)
        fragment = self._rewrite_html_images(fragment, source_dir)
        return fragment, index

    def _rewrite_html_images(self, fragment: str, source_dir: Path) -> str:
        def replacer(match: re.Match[str]) -> str:
            src = match.group(3)
            new_src = self.asset_resolver.resolve_image_src(src, source_dir)
            return f"{match.group(1)}{match.group(2)}{new_src}{match.group(4)}"

        return HTML_IMG_RE.sub(replacer, fragment)

    def _render_inline(
        self,
        text: str,
        source_dir: Path,
        refs: dict[str, dict[str, str]],
    ) -> str:
        if not text:
            return ""

        placeholders: dict[str, str] = {}

        def stash(content: str) -> str:
            token = f"@@CODE{len(placeholders)}@@"
            placeholders[token] = f"<code>{html.escape(content)}</code>"
            return token

        text = re.sub(r"`([^`]+)`", lambda m: stash(m.group(1)), text)
        escaped = html.escape(text)

        escaped = re.sub(
            r'!\[([^\]]*)\]\(([^)]+)\)',
            lambda m: self._render_inline_image(m.group(1), m.group(2), source_dir),
            escaped,
        )
        escaped = re.sub(
            r'!\[([^\]]*)\]\[([^\]]*)\]',
            lambda m: self._render_ref_image(m.group(1), m.group(2), source_dir, refs),
            escaped,
        )
        escaped = re.sub(
            r'(?<!!)\[([^\]]+)\]\(([^)]+)\)',
            lambda m: self._render_inline_link(m.group(1), m.group(2)),
            escaped,
        )
        escaped = re.sub(
            r'(?<!!)\[([^\]]+)\]\[([^\]]+)\]',
            lambda m: self._render_ref_link(m.group(1), m.group(2), refs),
            escaped,
        )

        escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
        escaped = re.sub(r"__([^_]+)__", r"<strong>\1</strong>", escaped)
        escaped = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", escaped)
        escaped = re.sub(r"(?<!_)_([^_\n]+)_(?!_)", r"<em>\1</em>", escaped)
        escaped = re.sub(r"~~([^~]+)~~", r"<del>\1</del>", escaped)

        for token, value in placeholders.items():
            escaped = escaped.replace(html.escape(token), value)
            escaped = escaped.replace(token, value)
        return escaped

    def _render_inline_image(self, alt: str, body: str, source_dir: Path) -> str:
        destination, title = self._split_link_body(html.unescape(body))
        data_url = self.asset_resolver.resolve_image_src(destination, source_dir)
        alt_text = html.escape(html.unescape(alt))
        title_attr = f' title="{html.escape(title)}"' if title else ""
        return f'<img alt="{alt_text}" src="{data_url}"{title_attr} />'

    def _render_ref_image(
        self,
        alt: str,
        ref_key: str,
        source_dir: Path,
        refs: dict[str, dict[str, str]],
    ) -> str:
        key = html.unescape(ref_key or alt).strip().lower()
        ref = refs.get(key)
        if not ref:
            raise BundleError(f"Missing image reference definition: [{ref_key}]")
        data_url = self.asset_resolver.resolve_image_src(ref["url"], source_dir)
        title_attr = f' title="{html.escape(ref["title"])}"' if ref["title"] else ""
        return f'<img alt="{html.escape(html.unescape(alt))}" src="{data_url}"{title_attr} />'

    def _render_inline_link(self, label: str, body: str) -> str:
        destination, title = self._split_link_body(html.unescape(body))
        safe_href = html.escape(destination, quote=True)
        title_attr = f' title="{html.escape(title)}"' if title else ""
        return f'<a href="{safe_href}"{title_attr}>{label}</a>'

    def _render_ref_link(
        self,
        label: str,
        ref_key: str,
        refs: dict[str, dict[str, str]],
    ) -> str:
        key = html.unescape(ref_key or label).strip().lower()
        ref = refs.get(key)
        if not ref:
            return label
        title_attr = f' title="{html.escape(ref["title"])}"' if ref["title"] else ""
        return f'<a href="{html.escape(ref["url"], quote=True)}"{title_attr}>{label}</a>'

    def _split_link_body(self, raw_body: str) -> tuple[str, str]:
        body = raw_body.strip()
        if body.startswith("<"):
            end = body.find(">")
            if end == -1:
                return body, ""
            destination = body[1:end]
            remainder = body[end + 1 :].strip()
            return destination, self._strip_wrapped_title(remainder)

        title_match = re.match(r'^(.*?)(?:\s+(".*?"|\'.*?\'))\s*$', body)
        if title_match:
            destination = title_match.group(1).strip()
            title = self._strip_wrapped_title(title_match.group(2))
            return destination, title
        return body, ""

    @staticmethod
    def _strip_wrapped_title(raw_title: str) -> str:
        text = raw_title.strip()
        if len(text) >= 2 and text[0] == text[-1] and text[0] in {"'", '"'}:
            return text[1:-1]
        if len(text) >= 2 and text[0] == "(" and text[-1] == ")":
            return text[1:-1]
        return text

    @staticmethod
    def _leading_spaces(text: str) -> int:
        return len(text) - len(text.lstrip(" "))

    @staticmethod
    def _looks_like_html_block(line: str) -> bool:
        stripped = line.strip()
        return stripped.startswith("<") and stripped.endswith(">")

    @staticmethod
    def _split_table_row(line: str) -> list[str]:
        stripped = line.strip().strip("|")
        return [cell.strip() for cell in stripped.split("|")]

    @staticmethod
    def _parse_table_alignment(cell: str) -> str:
        token = cell.strip()
        if token.startswith(":") and token.endswith(":"):
            return "center"
        if token.endswith(":"):
            return "right"
        if token.startswith(":"):
            return "left"
        return ""

    @staticmethod
    def _is_table_divider(line: str) -> bool:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not cells:
            return False
        return all(re.match(r"^:?-{3,}:?$", cell) for cell in cells)

    def _is_table_header(self, lines: list[str], index: int) -> bool:
        if index + 1 >= len(lines):
            return False
        current = lines[index]
        next_line = lines[index + 1]
        return "|" in current and self._is_table_divider(next_line)

    def _is_block_start(self, lines: list[str], index: int) -> bool:
        line = lines[index]
        return bool(
            FENCE_RE.match(line)
            or HEADING_RE.match(line)
            or HR_RE.match(line)
            or BLOCKQUOTE_RE.match(line)
            or LIST_ITEM_RE.match(line)
            or self._is_table_header(lines, index)
            or (self.allow_raw_html and self._looks_like_html_block(line))
        )


def render_preview_page(title: str, html_body: str) -> str:
    safe_title = html.escape(title)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{safe_title}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f6f7fb;
      --fg: #1d2433;
      --muted: #5a6478;
      --surface: #ffffff;
      --border: #d9dfea;
      --code-bg: #f0f3f9;
    }}
    body {{
      margin: 0;
      background: linear-gradient(180deg, #f3f5fb 0%, #eef2f7 100%);
      color: var(--fg);
      font-family: "Helvetica Neue", "PingFang SC", sans-serif;
    }}
    main {{
      max-width: 860px;
      margin: 32px auto;
      padding: 24px 28px;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 16px;
      box-shadow: 0 16px 40px rgba(31, 45, 61, 0.08);
    }}
    img {{
      max-width: 100%;
      height: auto;
    }}
    pre {{
      background: var(--code-bg);
      padding: 14px 16px;
      border-radius: 12px;
      overflow: auto;
    }}
    code {{
      background: var(--code-bg);
      padding: 0.1em 0.35em;
      border-radius: 6px;
    }}
    pre code {{
      padding: 0;
      background: transparent;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 16px 0;
    }}
    th, td {{
      border: 1px solid var(--border);
      padding: 8px 10px;
      vertical-align: top;
    }}
    blockquote {{
      margin: 16px 0;
      padding: 0 0 0 16px;
      border-left: 4px solid #c6d0e1;
      color: var(--muted);
    }}
  </style>
</head>
<body>
  <main>{html_body}</main>
</body>
</html>
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare a safe Markdown upload bundle for Kuaishou Docs.")
    parser.add_argument("markdown_path", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--asset-root", type=Path, action="append", default=[])
    parser.add_argument("--allow-raw-html", action="store_true")
    parser.add_argument("--max-image-bytes", type=int, default=10 * 1024 * 1024)
    parser.add_argument("--max-total-image-bytes", type=int, default=25 * 1024 * 1024)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    markdown_path = args.markdown_path.expanduser().resolve()
    if not markdown_path.exists():
        raise BundleError(f"Markdown file does not exist: {markdown_path}")
    if not markdown_path.is_file():
        raise BundleError(f"Markdown path is not a file: {markdown_path}")

    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    asset_roots = [markdown_path.parent] + [root.expanduser().resolve() for root in args.asset_root]
    for root in asset_roots:
        if not root.exists() or not root.is_dir():
            raise BundleError(f"Asset root must exist and be a directory: {root}")

    resolver = AssetResolver(
        asset_roots=asset_roots,
        max_image_bytes=args.max_image_bytes,
        max_total_image_bytes=args.max_total_image_bytes,
    )
    converter = MarkdownConverter(asset_resolver=resolver, allow_raw_html=args.allow_raw_html)
    converted = converter.convert(markdown_path.read_text(encoding="utf-8"), markdown_path.parent)

    bundle = {
        "source_markdown": str(markdown_path),
        "asset_roots": [str(root) for root in asset_roots],
        "allow_raw_html": args.allow_raw_html,
        "frontmatter": converted["frontmatter"],
        "plain_text": converted["plain_text"],
        "blocks": converted["blocks"],
        "html": converted["html"],
        "stats": {
            "block_count": len(converted["blocks"]),
            "image_count": len(resolver.assets),
            "total_image_bytes": resolver.total_image_bytes,
        },
    }
    manifest = {
        "source_markdown": str(markdown_path),
        "asset_roots": [str(root) for root in asset_roots],
        "stats": bundle["stats"],
        "assets": [dataclasses.asdict(entry) for entry in resolver.assets],
    }

    title = markdown_path.stem
    preview_html = render_preview_page(title, str(converted["html"]))

    bundle_path = output_dir / "bundle.json"
    preview_path = output_dir / "preview.html"
    manifest_path = output_dir / "manifest.json"

    bundle_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    preview_path.write_text(preview_html, encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    result = {
        "bundle_json": str(bundle_path),
        "preview_html": str(preview_path),
        "manifest_json": str(manifest_path),
        "stats": bundle["stats"],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BundleError as exc:
        print(f"[bundle-error] {exc}", file=sys.stderr)
        raise SystemExit(2)
