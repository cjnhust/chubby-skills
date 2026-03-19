# Repo Docs And Attribution

Use these rules when shaping a staged export into something reviewable on GitHub.

## README

The staged export should have a root `README.md` that covers:

- what the repository contains
- why `owned/` and `third-party/` are separated
- which skills are included
- a few concrete example prompts
- which third-party skills are referenced by owned workflows
- current publication status, including unresolved provenance or license review

Keep this README factual. Do not claim the export is fully publish-ready while provenance or license review is still pending.

The staged export should also carry these repo-level helper docs:

- `SECURITY.md` with rules for secret handling, disclosure, and local preflight
- `RELEASE_CHECKLIST.md` with the minimum checks before GitHub push
- `LICENSE_DECISION.md` when the maintainer has not yet chosen the root license for `owned/` content

The release flow should also cover the local commit step:

- review the effective `git config user.name` and `git config user.email`
- treat private author or committer metadata as a publication leak, not as harmless local preference
- if needed, set a repo-local public identity before committing
- review `git status --short`
- ensure ignored junk such as `node_modules/` is not part of the final handoff
- stage the intended changes only
- create a factual commit message
- verify the commit with `git show --stat --name-status --oneline -1`

The same release flow should also cover the local publish handoff:

- review `git remote -v`
- add `origin` only after the target GitHub repository exists
- prefer an `https://github.com/...` remote, or an explicit GitHub-only SSH alias, when the machine also carries internal SSH identities
- for HTTPS remotes, prefer `gh auth login` or another OS-keychain-backed credential flow instead of pasting PATs into terminal prompts
- push with `git push -u origin main` only after local scans and provenance checks are clean
- verify the pushed branch with `git ls-remote --heads origin main` or an equivalent remote check
- keep real repository URLs, access tokens, and maintainer-specific sensitive scan inputs out of committed docs

If the maintainer wants Codex-based GitHub maintenance after publication:

- treat that as a post-publish decision, not part of the initial sanitization flow
- prefer GitHub-side code review on an already public and boundary-stable repo before enabling broader cloud edits
- do not recommend `@codex`, Codex web delegation, or a Codex GitHub Action for unpublished or internal-only repositories from this publication workflow

## Third-Party Attribution

If the export intentionally includes third-party skills:

- add a root acknowledgement document
- thank the original author or maintainers
- preserve uncertainty when the evidence is incomplete
- point reviewers to the current provenance and license manifests

Acceptable wording:

- "Current source references found in imported skill metadata point to ..."
- "Manual confirmation is still required before public release."

Avoid stronger claims than the local evidence supports.

## Provenance Autofill

The export may prefill review manifests from local evidence such as:

- `SKILL.md` metadata homepages
- version markers in frontmatter
- local `package.json` metadata for vendored units
- detected references from owned skills into third-party skills
- an optional `third-party/review-evidence.json` file that groups imported units by source family and records externally verified source or license evidence

Prefill is useful, but it is not confirmation.
Keep unresolved entries clearly marked as pending until the operator verifies origin and license details.

Suggested uses for `third-party/review-evidence.json`:

- record one public upstream repo for many imported skills
- attach repo-level license evidence without duplicating the same explanation on every row
- distinguish confirmed public-source members from only-inferred family members
- map vendored units to upstream package paths when the local vendored copy lacks its own metadata
- carry `origin_status` and `license_status` so generated review docs can switch between `pending` and confirmed repo-level decisions

When the operator confirms that an import came from a GitHub repo and wants to use repo-level license handling for the export:

- record that explicitly in `review-evidence.json`
- regenerate the staged review docs
- rerun strict provenance checks to verify the generated manifests no longer contain placeholder or pending markers

## Scope Boundary

- Generate or update publish-facing docs only in the staged export tree unless the user explicitly asks to modify source skills.
- Do not satisfy provenance or license gates with empty templates or TODO-only stubs.
- Do not auto-select a root repository license for `owned/` content unless the user explicitly asks for that choice.
- If the user wants a real repo skeleton, it is acceptable to promote the staged export into a separate publish-repo working copy and initialize Git there, but keep that step outside the live source skills tree.
