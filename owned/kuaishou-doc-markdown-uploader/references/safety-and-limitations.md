# Safety And Limitations

## Hard Safety Rules

- Use manual login only. The user must type credentials into the temporary browser window directly.
- Do not read or dump cookies, tokens, browser sqlite files, localStorage, sessionStorage, request headers, or password-manager data.
- Do not point the uploader at non-Kuaishou hosts during real runs.
- Do not silently widen file access. If an image path escapes the Markdown directory tree, require explicit `--asset-root`.
- Do not replace a failed upload with undocumented internal APIs.

## Operational Model

The uploader relies on four boundaries:

1. Local Markdown is converted to a staging bundle entirely on disk.
2. Local referenced images are inlined as `data:` URLs without touching browser secrets.
3. A fresh Chrome profile is launched with remote debugging enabled.
4. The user logs in manually and confirms when the caret is inside the target editor.

The skill automates editor insertion only after those boundaries are satisfied.

## Known Limits

- The Markdown converter is intentionally conservative. It supports common publishing syntax, not every edge case from full CommonMark plus GFM.
- Very large image payloads can exceed editor tolerance. The generator enforces per-image and total-size limits.
- If the cloud-doc editor sanitizes `data:` images or rejects `insertHTML`, the run will stop rather than falling back to unsafe methods.
- The body upload is automated. Title fields, page location, folder moves, and permissions remain manual unless a future safe adapter is added.

## Recommended Operator Habits

- Start with `--dry-run --keep-work-dir` on the first document from a new source.
- Keep only the required doc tab open in the temporary Chrome window.
- Review the rendered result before closing the temporary browser.
- Preserve the work dir only when you need to inspect `preview.html` or `bundle.json`.
