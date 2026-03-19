---
name: skills-github-publisher
description: Orchestrate safe publication of local Codex skills to GitHub. Use when the user wants to publish, open-source, split, sanitize, export, or audit skills before creating a GitHub repo or pushing changes. Covers candidate inventory, public/private classification, security scanning, structure cleanup, path normalization, .gitignore baseline, export-repo staging, and push-readiness review.
---

# Skills GitHub Publisher

Use this skill when the user wants to publish some or all local skills to GitHub and the work needs more than a simple `git push`.

Typical triggers:

- "把这些 skills 放到 GitHub"
- "帮我整理成可公开仓库"
- "先做安全审核再发布"
- "把本地 skills 拆成 public/private"
- "把绝对路径和本地脏文件清掉"

## Scope

This skill is the orchestrator for one publication run. It owns:

- choosing the candidate skill roots
- classifying what is public, private, repo-local, built-in, third-party, or review-required
- running a local preflight scan for secrets, local paths, and junk artifacts
- deciding structure changes before export
- normalizing publishable paths and references
- preparing or updating an export repo instead of pushing directly from a live skills directory
- producing a final publish-readiness summary with blockers

This skill does not own the final GitHub UI clicks. It prepares the local tree so the later push is deliberate and low-risk.

## Entry Rules

Use this skill before editing skill content for publication if any of the following is true:

- the source tree mixes repo-local skills and global skills
- the tree contains `danger-*` skills, `.system/`, `vendor/`, or generated dependency directories
- the user wants a public repo instead of a private backup
- absolute local paths, usernames, or home-directory references may exist
- the user explicitly asks for a security audit, GitHub-ready cleanup, or export staging

If the user only wants to create a brand-new skill and not publish anything, use `skill-creator` instead.

## Modes

Default to `audit-only` unless the user explicitly asks to apply the proposed cleanup.

### `audit-only`

Use this mode by default for security-sensitive publication work.

What it does:

- inventory candidates
- classify public, private, built-in, and third-party content
- run scans
- produce redacted findings
- produce a proposed change list

What it does not do:

- no source-tree edits
- no staging-tree path rewrites
- no structural cleanup beyond reporting unless the user explicitly asked for a dry-run staging pass

### `apply-on-confirm`

Use this mode only after the user confirms the proposed security and structure changes.

What it may do:

- update staging copies
- rewrite publish-facing path leaks in the staged export
- add `.gitignore`
- remove blocked runtime artifacts from the staged export
- prepare the final export tree

## Workflow

1. Inventory the candidate roots.
   - List the requested roots before changing anything.
   - Separate repo-local skill families from global skill families.
   - Treat `.system/` as excluded by default unless the user explicitly wants it and the license situation is understood.
   - Treat `danger-*` skills as review-required, not as default public candidates.

2. Choose the publish boundary.
   - Prefer a clean export repo over pushing directly from `~/.codex/skills`.
   - For mixed trees, prefer separate public repos or clearly separated top-level families.
   - Keep repo-local skills with their source repo when their scripts, references, or assumptions only make sense there.
   - Mark copied upstream or non-user-authored material as `third-party` in the report and export plan.
   - If a whole skill family is known to be authored by others, such as an externally maintained `baoyu-*` family, stage it under a `third-party/` boundary by default instead of keeping it at the `owned/` root.
   - Read [references/classification-and-structure.md](references/classification-and-structure.md) when the boundary is unclear.

3. Run the preflight audit first.
   - Read [references/security-baseline.md](references/security-baseline.md).
   - Run `python3 scripts/preflight_scan.py --root <path> [--root <path> ...]`.
   - Add `--strict` when the scan should fail on blockers.
   - Add `--strict-provenance` when publish-ready means third-party content must already carry origin and license metadata.
   - Add `--json-out <file>` when the run needs a saved machine-readable report.
   - Review three blocker classes:
     - secret-like literals
     - local absolute path leaks
     - junk, generated, or runtime credential artifacts
     - hardcoded auth headers, JWT-like literals, webhook secrets, or credential-bearing URIs
   - Review three caution classes:
     - `.system/`
     - `danger-*`
     - `third-party`
   - Review the provenance gate:
     - `third_party_provenance_gaps`
     - treat this as publish-blocking when the run is checking final public distribution readiness
     - placeholder review docs or `pending` manifests do not satisfy this gate
   - In `audit-only` mode, stop here and present a redacted remediation plan before changing staged content for security reasons.
   - Redact any suspected secret values in the summary and describe the fix as a proposal, not as an already-applied change.

4. Reshape the tree before content edits.
   - Remove or ignore `.DS_Store`, `__pycache__/`, `*.pyc`, `node_modules/`, `.env*`, cookie/session files, local browser profiles, local databases, and raw key material.
   - Do not treat third-party or built-in content as publishable just because it is present.
   - If the user approves inclusion of third-party material, keep it under an explicit `third-party` boundary in the export plan and preserve origin and license context.
   - If the user wants a single public repo, keep the family structure explicit so cross-skill references remain stable after export.
   - In `apply-on-confirm` mode, apply these changes only to the staged export unless the user explicitly authorizes source edits.

5. Normalize publish-facing paths and references.
   - Read [references/path-and-ignore-rules.md](references/path-and-ignore-rules.md).
   - Rewrite `/Users/<name>/...`, `/home/<name>/...`, `C:\Users\...`, and `~/.codex/...` references in docs and skill instructions.
   - Prefer relative paths when the referenced file stays inside the exported bundle.
   - Prefer `$CODEX_HOME/skills/<skill>/...` when the target is an installed sibling skill and the reference should remain installation-relative.
   - Do not rewrite runtime storage code that intentionally uses `os.homedir()`, `APPDATA`, `XDG_DATA_HOME`, or explicit env overrides unless the user asked to change runtime behavior. That is runtime configuration, not a publish leak by itself.

6. Prepare the export repo.
   - Ensure the export repo contains only publishable source-of-truth files.
   - Add or update `.gitignore` using the baseline from the reference file.
   - Keep placeholder examples and env-var names, but never commit real token values.
   - If the tree contains review-required skills, keep them out of the staged public export until the user confirms.
   - If third-party content is intentionally included, keep it explicitly marked as `third-party` in the export notes instead of blending it into `owned/` content.
   - If the export is meant to be publish-ready, require origin and license metadata for each intentionally included `third-party` or vendored unit before calling the tree ready.
   - Generate publish-facing docs in the staged export:
     - root `README.md`
     - root `THIRD_PARTY_ACKNOWLEDGEMENTS.md`
     - root `SECURITY.md`
     - root `RELEASE_CHECKLIST.md`
     - root `LICENSE_DECISION.md`
     - prefilled `third-party/ORIGIN.md`
     - prefilled `third-party/LICENSES.md`
   - If stronger external evidence has been verified, record it in `third-party/review-evidence.json` before doc generation.
   - Run `python3 scripts/generate_export_docs.py --root <stage-export>` to derive these docs from the staged `SKILL.md` files, vendored package metadata, and optional review-evidence data.
   - If the user wants a formal repo skeleton instead of only a staging tree, promote the staged export into a dedicated publish-repo working copy and initialize Git there after doc generation. Do not auto-create the root `LICENSE`; leave that decision explicit in `LICENSE_DECISION.md`.
   - Read [references/repo-docs-and-attribution.md](references/repo-docs-and-attribution.md) when shaping the repo-facing docs.

7. Finish with a publish-readiness summary.
   - State what was included.
   - State what was excluded.
   - State the remaining blockers, if any.
   - Do not call the tree publish-ready if secret-like literals, absolute user paths, or runtime artifacts remain.
   - If a real secret is found, stop, rotate or revoke it, remove it from the export tree, and only then continue.

## Boundary Rules

- Do not push directly from the live `~/.codex/skills` tree unless the user explicitly asks for that riskier path.
- Do not treat plain env-var names as leaked secrets by themselves.
- Do not print or preserve full suspected secret values in summaries; redact them.
- Do not auto-include `.system/` in a public export.
- Do not silently fold third-party content into `owned/` skill ownership; keep a `third-party` marker in reports and export structure decisions.
- If provenance is already known, prefer a physical `third-party/` directory boundary in the staged export instead of only tagging the report.
- Do not "fix" runtime credential storage code when the real issue is only a doc path or a committed runtime artifact.
- Prefer a smaller public export with clean boundaries over a broader export with ambiguous ownership.

## Resources

- `scripts/preflight_scan.py`: local scan for secret-like literals, local-path leaks, and junk artifacts
- `scripts/generate_export_docs.py`: generate staged `README.md`, acknowledgement docs, and prefilled third-party review manifests
- `references/classification-and-structure.md`: repo-shaping rules for public/private and repo-local/global splits
- `references/path-and-ignore-rules.md`: path rewrite rules and `.gitignore` baseline
- `references/security-baseline.md`: stricter shift-left security baseline for publication checks
- `references/repo-docs-and-attribution.md`: what the staged README and attribution docs should contain
