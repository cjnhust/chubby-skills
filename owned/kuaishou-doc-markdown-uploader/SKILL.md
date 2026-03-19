---
name: kuaishou-doc-markdown-uploader
description: Safely publish a local Markdown file and its referenced local images to docs.corp.kuaishou.com cloud docs by staging a preview bundle, launching an isolated Chrome profile, requiring manual user login, and injecting rich HTML without reading cookies, API keys, localStorage, or browser credential stores. Use when Codex needs to upload or sync local .md content into Kuaishou cloud docs under strict internal-network safety constraints.
---

# Kuaishou Docs Markdown Uploader

Convert local Markdown into an upload bundle with inline local images, then push it into `https://docs.corp.kuaishou.com/home` through a temporary Chrome profile that the user logs into manually.

Also read [references/safety-and-limitations.md](references/safety-and-limitations.md) before running the browser step.

## Guardrails

- Never ask the user for `cookie`, `api_key`, `token`, private key, password export, or browser profile paths.
- Never read `Cookies`, `Local Storage`, `Session Storage`, network headers, or browser credential files.
- Always use the bundled uploader, which launches a fresh temporary Chrome profile and deletes it after the run unless the operator explicitly keeps it.
- Keep the browser flow on `docs.corp.kuaishou.com` only. Do not repurpose this skill for arbitrary sites.
- Treat image references conservatively. Only inline files under the Markdown directory unless the operator explicitly widens scope with `--asset-root`.
- If the editor rejects HTML injection, stop and return the generated preview artifacts. Do not escalate to cookie scraping or undocumented internal APIs.

## Workflow

### 1. Run a dry run first when the content is unfamiliar

Use dry run when the Markdown contains many images, raw HTML, or wide tables:

```bash
python3 {baseDir}/scripts/publish_to_kuaishou_docs.py /abs/path/doc.md --dry-run --keep-work-dir
```

This creates:

- `bundle.json`: block-level upload payload
- `preview.html`: local render preview
- `manifest.json`: sanitized asset summary

### 2. Run the real upload

```bash
python3 {baseDir}/scripts/publish_to_kuaishou_docs.py /abs/path/doc.md
```

Default behavior:

1. Parse Markdown and strip YAML frontmatter from the upload body
2. Resolve referenced local images under the allowed asset roots
3. Inline images as `data:` URLs in generated HTML
4. Open `docs.corp.kuaishou.com` in a temporary Chrome profile
5. Ask the user to log in manually and open or create the target doc in the same tab
6. Wait for the user to place the caret inside the cloud-doc editor
7. Inject the prepared HTML blocks into the focused editor
8. Let the user review, then close Chrome and remove the temporary profile

### 3. Adjust scope only when needed

If the Markdown references images outside its own directory tree, widen the allowlist explicitly:

```bash
python3 {baseDir}/scripts/publish_to_kuaishou_docs.py /abs/path/doc.md --asset-root /abs/path/shared-assets
```

If the document intentionally contains raw HTML that must remain raw, opt in explicitly:

```bash
python3 {baseDir}/scripts/publish_to_kuaishou_docs.py /abs/path/doc.md --allow-raw-html --keep-work-dir
```

## Execution Notes

- Resolve `{baseDir}` to this skill directory before running commands.
- Prefer `--dry-run --keep-work-dir` before the first upload against a new document style.
- Keep the login and editing flow in a single tab inside the temporary Chrome window. The uploader attaches to that tab.
- Ask the user to focus the document body before confirming the upload prompt. The uploader targets the currently focused rich-text element.
- If the document title needs special handling in Kuaishou Docs, let the user adjust it after body upload instead of guessing selectors.

## Supported Markdown Surface

The bundle generator is intentionally conservative and optimized for safe internal publishing:

- headings
- paragraphs
- fenced code blocks
- blockquotes
- ordered and unordered lists
- basic GFM pipe tables
- inline code, emphasis, strong, strike-through
- inline links
- inline images and reference-style images

Raw HTML is escaped by default unless `--allow-raw-html` is set.

## Scripts

- `scripts/publish_to_kuaishou_docs.py`: high-level entrypoint
- `scripts/prepare_markdown_bundle.py`: Markdown-to-HTML bundle generator with image inlining
- `scripts/upload_via_cdp.mjs`: isolated Chrome uploader for `docs.corp.kuaishou.com`
- `scripts/cdp_lib.mjs`: minimal Chrome DevTools Protocol helpers
- `scripts/editor_injection.mjs`: contenteditable targeting and block injection
- `scripts/selftest_injection.mjs`: local non-internal validation against a temporary `contenteditable` page

## Validation

Use the local self-test before trusting browser changes:

```bash
node {baseDir}/scripts/selftest_injection.mjs
```

Use the skill validator after edits:

```bash
python3 $CODEX_HOME/skills/.system/skill-creator/scripts/quick_validate.py {baseDir}
```

## Failure Handling

- Missing local image: stop and fix the Markdown or widen `--asset-root`
- Remote image URL: stop unless the user explicitly wants to keep it remote
- No focused editor found: ask the user to click inside the doc body and retry
- Editor rejects injected HTML: preserve the work dir and return `preview.html` plus `bundle.json`
- Upload succeeds but formatting is imperfect: inspect `preview.html` locally before changing the uploader
