# Codex GitHub Smoke Test

Use this note after a repository is already public, sanitized, and intentionally shareable.

## Goal

Prepare everything locally so the maintainer only needs to do the account-side GitHub authorization and one final human confirmation before the first Codex review.

## Keep The First Use Narrow

- Start with GitHub-side review on public pull requests.
- Do not start with cloud-side code generation or broad write permissions.
- Do not authorize internal repositories, mixed public/private trees, or repos that still depend on local private policy files.
- If you later test Codex writeback, keep it to one trusted-maintainer-only follow-up on an already-public PR branch and require minimal patch scope.
- Trigger Codex review only once per PR head. Use repository auto review or reviewer request when available, and keep one manual `@codex review` request as the fallback instead of stacking both.
- Treat the resulting current-head Codex pull-request review as the gate input; a standalone issue comment is not enough to satisfy the merge gate.

## Prepare In The Repo Before The User Clicks Anything

- Keep `AGENTS.md` explicit about public-boundary rules and review-first behavior.
- Keep the pull-request template explicit about publication checks and the intended Codex review focus.
- Generate a root `CODEX_SETUP.md` with:
  - the remaining manual account-side steps
  - the security posture for repository-scoped authorization
  - the first smoke-test procedure
  - the trusted-maintainer rule for any Codex hard-gate auto-merge path
- If a smoke test is planned, make it a small docs-only pull request.
- If browser-side troubleshooting is later needed, reuse the existing isolated-profile CDP pattern instead of touching the default browser profile.
- If Codex leaves findings during the smoke test, keep any `@codex address that feedback` follow-up manual; do not configure an automatic fix loop.
- If you want to test PR writeback after review succeeds, use one explicit trusted-maintainer comment such as `@codex fix the latest review feedback on this existing PR branch. Update this PR branch directly with the minimal patch and do not widen scope.`

## Manual Steps The User Must Still Perform

- Connect GitHub from ChatGPT or Codex.
- Authorize only the intended public repository or a minimal repository subset.
- If the UI exposes a Codex review toggle, enable review first and leave broader cloud editing disabled.
- If follow-up tasks are expected to update an existing PR, confirm the same repository is usable from Codex cloud instead of assuming the review toggle alone is sufficient.
- Confirm any privacy or training settings that matter for the user's account tier before proceeding.

## Smoke Test

Use a small public pull request and keep the prompt narrow. Preferred checks:

- secret leakage or local-path regressions
- accidental inclusion of internal-only content
- ownership-boundary mistakes between `owned/` and `third-party/`
- provenance or attribution regressions

Do not use the first smoke test to request architecture rewrites, bulk content changes, or edits on unpublished branches.

## Verification

After the user completes the account-side authorization:

- open a small pull request
- trigger Codex review through the current supported GitHub workflow
- if GitHub shows `@codex` as mentioned or subscribed but no review arrives, first confirm the repository is present in `https://chatgpt.com/codex/settings/code-review`
- if the repository is missing there, use `https://chatgpt.com/codex/settings/connectors` and the GitHub installation settings page to authorize the repository before retrying
- verify the review stays within the expected public repository boundary
- if the review output looks safe and relevant, keep the integration for future PR review
- if the review ignores the boundary or requests sensitive local context, stop and keep Codex local-only

## Latest-Head Review Loop

When Codex leaves findings on a PR and the maintainer pushes a fix:

- treat the latest PR head SHA as the only truth for whether a fix landed
- if Codex claims it committed a change but the PR head did not move, treat that as a task summary, not as a real GitHub writeback
- if the Codex UI shows a manual `Update branch` action, treat that as a required maintainer confirmation step
- if a previously reported finding is fixed on the latest head but the review thread stays open, manually resolve the thread
- after resolving stale threads, trigger one fresh current-head review through the same single trigger path already in use for the PR
- if GitHub reports a missing pull ref such as `refs/pull/<n>/head`, push a fresh branch head and recheck that ref before blaming repository policy or the review gate
