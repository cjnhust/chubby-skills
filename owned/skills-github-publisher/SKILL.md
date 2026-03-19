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
- classifying what is internal-only and therefore excluded from a public export by default
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

0. Resolve local defaults before inventory when available.
   - Read [references/local-config.md](references/local-config.md) when the user wants repeated local publication work, incremental updates against one publish repo, or a local default publish boundary.
   - Prefer `python3 scripts/resolve_local_publish_config.py` to discover private local defaults instead of hardcoding workstation paths in the skill, export repo, or committed docs.
   - Supported local defaults should stay outside the public repo, for example:
     - `default_publish_repo`
     - `default_owned_root`
     - `default_local_policy_file`
   - If the local config resolves a publish repo and the user asks for an incremental update, diff and sync against that repo boundary instead of inventing a new staging path.
   - For deterministic incremental updates into a local publish git working copy, prefer `python3 scripts/sync_incremental_update.py --skill-root <path> [...]` and let it resolve the default publish repo / owned root from the local config when possible.
   - The incremental sync helper should refuse `internal/`, `.system/`, and `danger-*` skill roots by default, and it should exclude publish-blocking junk such as `__pycache__/`, `node_modules/`, `.env*`, cookies, sessions, and raw key material unless the operator explicitly overrides that review-required boundary.
   - Explicit CLI overrides such as `--publish-repo` or `--owned-root` should win over local config defaults so an incremental sync cannot drift into the wrong working copy.
   - The incremental sync helper should also strip nested `internal/`, `.system/`, and `danger-*` subtrees from otherwise allowed skill roots so a mixed local skill tree cannot reintroduce blocked content through rsync.
   - If a source skill root already lives under a clear ownership boundary such as `third-party/`, the incremental sync helper should preserve that boundary by default instead of silently restaging the skill into `owned/`.

1. Inventory the candidate roots.
   - List the requested roots before changing anything.
   - Separate repo-local skill families from global skill families.
   - Treat `.system/` as excluded by default unless the user explicitly wants it and the license situation is understood.
   - Treat `danger-*` skills as review-required, not as default public candidates.
   - Treat any skill placed under a dedicated internal boundary such as `internal/` as internal-only and exclude that path from a public export by default.

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
   - Prefer `--local-policy-file <private-json>` or a local default such as `$CODEX_HOME/private/publish-policy.json` for sensitive blocklist inputs like personal identifiers, local-only regexes, or extra secret/internal-host detection rules. Do not put those values in the public repo, README, or shared command examples.
   - Add `--json-out <file>` when the run needs a saved machine-readable report.
   - Review three blocker classes:
     - secret-like literals
     - maintainer-marked personal identifiers
     - local absolute path leaks
     - internal-only hosts or corp-network endpoints
     - junk, generated, or runtime credential artifacts
     - hardcoded auth headers, JWT-like literals, webhook secrets, or credential-bearing URIs
   - Review the default review-required classes:
     - `.system/` and `danger-*` are publish-blocking by default in strict publication checks
     - `third-party` stays allowed only when the intended ownership boundary is explicit and provenance review is complete
   - Review the provenance gate:
     - `third_party_provenance_gaps`
     - treat this as publish-blocking when the run is checking final public distribution readiness
     - placeholder review docs or `pending` manifests do not satisfy this gate
   - In `audit-only` mode, stop here and present a redacted remediation plan before changing staged content for security reasons.
   - Redact any suspected secret values in the summary and describe the fix as a proposal, not as an already-applied change.

4. Reshape the tree before content edits.
   - Remove or ignore `.DS_Store`, `__pycache__/`, `*.pyc`, `node_modules/`, `.env*`, cookie/session files, local browser profiles, local databases, and raw key material.
   - Do not treat third-party or built-in content as publishable just because it is present.
   - Do not treat internal-only skills as public candidates just because they are user-authored.
   - If the user approves inclusion of third-party material, keep it under an explicit `third-party` boundary in the export plan and preserve origin and license context.
   - If the user wants a single public repo, keep the family structure explicit so cross-skill references remain stable after export.
   - In `apply-on-confirm` mode, apply these changes only to the staged export unless the user explicitly authorizes source edits.

5. Normalize publish-facing paths and references.
   - Read [references/path-and-ignore-rules.md](references/path-and-ignore-rules.md).
   - Rewrite `/Users/<name>/...`, `/home/<name>/...`, `C:\Users\...`, and `~/.codex/...` references in docs and skill instructions.
   - Prefer relative paths when the referenced file stays inside the exported bundle.
   - Prefer `$CODEX_HOME/skills/<skill>/...` when the target is an installed sibling skill and the reference should remain installation-relative.
   - Do not rewrite runtime storage code that intentionally uses `os.homedir()`, `APPDATA`, `XDG_DATA_HOME`, or explicit env overrides unless the user asked to change runtime behavior. That is runtime configuration, not a publish leak by itself.
   - If the user wants to avoid repeat remediation, sync generic security fixes back to the original skills as source of truth:
     - absolute path rewrites
     - personal-info redaction
     - removal of committed internal-host or corp-registry artifacts
   - Do not sync pure export-boundary decisions back to source unless the user asked:
     - excluding an internal-only skill from a public repo
     - moving a copied family under `third-party/`
     - splitting public and private exports

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
     - root `CODEX_SETUP.md`
     - root `LICENSE_DECISION.md`
     - prefilled `third-party/ORIGIN.md`
     - prefilled `third-party/LICENSES.md`
   - If stronger external evidence has been verified, record it in `third-party/review-evidence.json` before doc generation.
   - Run `python3 scripts/generate_export_docs.py --root <stage-export>` to derive these docs from the staged `SKILL.md` files, vendored package metadata, and optional review-evidence data.
   - If the user wants a formal repo skeleton instead of only a staging tree, promote the staged export into a dedicated publish-repo working copy and initialize Git there after doc generation. Do not auto-create the root `LICENSE`; leave that decision explicit in `LICENSE_DECISION.md`.
   - Read [references/repo-docs-and-attribution.md](references/repo-docs-and-attribution.md) when shaping the repo-facing docs.
   - If the user is updating an existing local publish repo rather than creating a fresh staging tree:
     - sync the changed skill roots into that working copy first
     - then regenerate repo-facing docs
     - then rerun the strict preflight scan in the publish repo
     - then review `git status --short` in that repo before any commit or push

7. Finish with a publish-readiness summary.
   - State what was included.
   - State what was excluded.
   - State the remaining blockers, if any.
   - Do not call the tree publish-ready if secret-like literals, absolute user paths, or runtime artifacts remain.
   - If a real secret is found, stop, rotate or revoke it, remove it from the export tree, and only then continue.

8. Finalize the local Git history in the export repo.
   - Review the effective Git identity before the first public commit:
     - run `python3 scripts/check_git_identity.py --root <export-repo> --strict`
     - if the effective `user.name` or `user.email` is private, set a repo-local public identity before committing
     - prefer a public display name plus a GitHub no-reply address or another intentionally public email
   - For updates to an existing public repo, create or reuse a PR branch before staging or committing.
     - prefer a `codex/<change-name>` branch
     - do not keep new publication commits only on `main`
     - if the current local change was prepared while checked out on `main`, branch from the current HEAD before the publish handoff continues
   - When syntax-checking Python helper scripts inside the export repo, prefer `python3 scripts/safe_py_compile.py <files...>` over raw `python3 -m py_compile`; the raw command leaves `__pycache__` in-tree and will trip the strict preflight scan.
   - Review `git status --short` before staging anything.
   - Do not stage ignored junk or generated dependency trees just because they are present in the working directory.
   - If ignored working-tree junk such as `node_modules/` still exists inside the export repo, clean or quarantine it before the final handoff.
   - Use `git add -A` only after the tree matches the intended publish boundary.
   - Write a factual commit message that describes the export change, boundary update, or security cleanup.
   - Verify the commit with `git show --stat --name-status --oneline -1`.
   - Keep this commit step inside the dedicated export repo or publish-repo working copy, not in the live source skills tree unless the user explicitly asked for that.

9. Execute the local publish handoff only after the export repo is clean.
   - Review `git remote -v` before the first push.
   - If no `origin` remote exists yet, create the GitHub repository outside this skill, then add `origin` deliberately in the export repo.
   - For public GitHub publication on machines that also use internal SSH identities, prefer an `https://github.com/...` remote or an explicit GitHub-only SSH host alias. Do not rely on the default SSH identity selection when internal and external keys differ.
   - When using an HTTPS remote, prefer GitHub CLI login such as `gh auth login --hostname github.com --git-protocol https --web` so credentials land in the OS keychain instead of being typed into terminal prompts for each push.
   - Prefer `python3 scripts/push_pr_handoff.py --root <export-repo> --base <default-branch>` to standardize the final local handoff.
     - use it without side-effect flags first to print the detected branch, push command, and PR handoff URL
     - then use `--push` when the branch is ready to publish
     - then use `--create-pr` only when `gh` is available and authenticated
     - if the branch has not been pushed yet, require `--push` before `--create-pr` instead of relying on a failing `gh pr create`
     - when no explicit PR title/body is provided, the helper should fall back to `gh pr create --fill-first` instead of failing in non-interactive mode
     - the helper should still print a compare URL for GitHub-only SSH host aliases, not only for plain `github.com` remotes
     - if the current branch is the base branch, allow only the explicit bootstrap case where that base branch does not exist on `origin` yet; do not allow normal PR handoff from an already-published base branch
     - do not treat an `ls-remote` failure as proof that the base branch is missing; bootstrap detection should succeed only on a confirmed “missing ref” result, not on network or auth errors
     - if `gh` is unavailable, fall back to the printed compare / PR URL and open the PR in the browser manually
   - For updates to an existing public repo, prefer:
     - `git push -u origin <pr-branch>`
     - open a pull request from `<pr-branch>` into the protected default branch
     - let the repository's review and merge rules decide when it lands on `main`
   - Reserve direct `main` pushes for explicit bootstrap cases such as a brand-new empty publish repo, not for normal updates to an already public skills repo.
   - Push only after:
     - the strict preflight scan is clean
     - provenance review is complete for intentionally included third-party units
     - `git status --short` is empty after the release commit
   - If GitHub push protection blocks the push, stop and treat it as a real blocker until the flagged content is removed or explained.
   - After the push, verify the published branch with `git ls-remote --heads origin <branch>` or an equivalent remote check.
   - Record the final local verification commands in `RELEASE_CHECKLIST.md` so the publish-repo is self-contained for the next run.

10. Decide whether post-publish Codex GitHub integration is appropriate.
   - Read [references/codex-github-maintenance.md](references/codex-github-maintenance.md) before recommending Codex cloud, `@codex`, or a Codex GitHub Action.
   - Read [references/codex-github-smoke-test.md](references/codex-github-smoke-test.md) when the user wants everything prepared except the account-side authorization clicks.
   - Read [references/codex-github-browser-troubleshooting.md](references/codex-github-browser-troubleshooting.md) when the user explicitly authorizes local browser-side help for ChatGPT, Codex, or GitHub setup.
   - Default to a conservative rule:
     - do not delegate unpublished, internal-only, or still-being-sanitized skill trees to Codex cloud or GitHub integration
     - do not expose local private policy files, internal-only skills, or mixed public/private trees to cloud maintenance flows
   - For a public skills repo that is already sanitized and intentionally shareable:
     - prefer Codex GitHub code review first
     - allow `@codex` or a Codex GitHub Action only after the repository boundary is already stable and public
     - generate `CODEX_SETUP.md` so the remaining manual steps are explicit and minimal
     - if the repo installs a Codex hard gate with auto-merge, keep direct auto-merge limited to trusted-maintainer-only submissions; require a current-head approval from the repository owner or another configured admin for anything else
     - if Codex leaves findings, keep any `@codex address that feedback` step human-invoked by a trusted maintainer rather than wiring a recursive auto-fix workflow
     - if the user wants Codex to write back to an existing PR branch, keep that as an explicit trusted-maintainer action on an already-public PR branch; ask Codex to update the current PR branch with a minimal patch and do not rely on this for unpublished or mixed-boundary trees
     - ensure `AGENTS.md` and the pull-request template keep Codex in review-first mode
     - prepare a smoke-test plan for a small docs-only PR, but stop before any account-side OAuth step or live `@codex` trigger that requires the user's confirmation
     - if the user explicitly authorizes browser-side assistance, prefer the same safe CDP pattern already used by local browser-automation skills:
       - launch an isolated Chrome profile instead of touching the default profile
       - keep login manual and in-tab; do not scrape cookies, localStorage, or browser credential files
       - restrict navigation to the minimum public hosts needed for setup, such as `chatgpt.com`, `github.com`, and `help.openai.com`
       - treat browser-side help as local troubleshooting only, not as a reason to broaden Codex cloud permissions
   - If the user asks about internal or pre-public repositories, keep the recommendation local-only by default:
     - Codex app, CLI, or IDE extension on the maintainer machine
     - no cloud delegation from this publication skill until a separate internal-security review explicitly allows it

## Boundary Rules

- Do not push directly from the live `~/.codex/skills` tree unless the user explicitly asks for that riskier path.
- Do not treat plain env-var names as leaked secrets by themselves.
- Do not print or preserve full suspected secret values in summaries; redact them.
- Do not auto-include `.system/` in a public export.
- Do not auto-include skills under a dedicated internal boundary such as `internal/` in a public export.
- Do not silently fold third-party content into `owned/` skill ownership; keep a `third-party` marker in reports and export structure decisions.
- If provenance is already known, prefer a physical `third-party/` directory boundary in the staged export instead of only tagging the report.
- Do not "fix" runtime credential storage code when the real issue is only a doc path or a committed runtime artifact.
- Do not recommend Codex cloud or GitHub-side maintenance for unpublished or internal skill repos from this skill's default path.
- Do not treat Git author and committer metadata as harmless; private names and emails in commit history are publish leaks too.
- Do not repurpose browser-side CDP help into general session scraping; keep any browser assistance on isolated profiles and the minimum public setup hosts only.
- Prefer a smaller public export with clean boundaries over a broader export with ambiguous ownership.

## Resources

- `scripts/resolve_local_publish_config.py`: resolve maintainer-local defaults such as the preferred publish repo and local private policy file without hardcoding them in the public skill
- `scripts/sync_incremental_update.py`: sync one or more local skills into the configured publish repo working copy for incremental update flows while keeping review-required roots and junk/runtime artifacts out by default
- `scripts/push_pr_handoff.py`: validate the current branch, print or run the push command, support GitHub-only SSH aliases, and either create the PR via `gh` or print the manual compare URL
- `scripts/check_git_identity.py`: verify repo-local git author metadata against local private policy before public commits
- `scripts/preflight_scan.py`: local scan for secret-like literals, local-path leaks, and junk artifacts
- `scripts/generate_export_docs.py`: generate staged `README.md`, acknowledgement docs, and prefilled third-party review manifests
- `scripts/safe_py_compile.py`: syntax-check Python helpers without leaving `__pycache__` in the repo tree
- `references/local-config.md`: private local config contract for repeated incremental publication work
- `references/classification-and-structure.md`: repo-shaping rules for public/private and repo-local/global splits
- `references/codex-github-browser-troubleshooting.md`: safe local browser/CDP pattern for helping with public Codex-on-GitHub setup after explicit user approval
- `references/codex-github-maintenance.md`: conservative recommendation for when Codex GitHub integration is appropriate after publication
- `references/codex-github-smoke-test.md`: minimal post-publish Codex connection and review smoke-test flow for a public repo
- `references/path-and-ignore-rules.md`: path rewrite rules and `.gitignore` baseline
- `references/security-baseline.md`: stricter shift-left security baseline for publication checks
- `references/repo-docs-and-attribution.md`: what the staged README and attribution docs should contain
