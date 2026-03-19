# Codex Setup

Use this note after the repository is already public and sanitized.
The goal is to keep the first Codex-on-GitHub use limited to review on public pull requests.

## Already Prepared In This Repo

- `AGENTS.md` keeps Codex in review-first mode and restates the public-boundary rules.
- `.github/pull_request_template.md` keeps publication checks explicit for every PR.
- `SECURITY.md` and `RELEASE_CHECKLIST.md` keep local policy files, internal-only content, and runtime credentials out of the repo.

## Manual Steps You Still Need To Do

1. In ChatGPT or Codex, connect GitHub and authorize only this public repository or the smallest possible repository subset.
2. If the UI exposes Codex review settings, enable review first and leave broader cloud editing disabled.
3. If repository indexing is delayed, retry after a short wait and use the current GitHub import or refresh flow exposed by the product.
4. Confirm any account-level privacy or training settings that matter for your plan before you rely on the integration.

## First Smoke Test

- Use a small docs-only pull request.
- Keep the diff small enough that you can still verify every line manually after the review comes back.
- Trigger Codex review through the currently supported GitHub flow for your account.
- Keep the review focus narrow:
  - secret leakage or local-path regressions
  - accidental inclusion of internal-only content
  - ownership-boundary mistakes between `owned/` and `third-party/`
  - provenance or attribution regressions

Suggested review request:

```text
@codex review

Focus on secret leakage, local path regressions, internal-only content, and ownership boundary mistakes between owned/ and third-party/.
```

## Stop Conditions

- Do not use Codex GitHub flows on unpublished branches that still carry local-only policy values.
- Do not authorize internal repositories from this public-repo setup path.
- If the first review asks for local private files or ignores the public boundary, disable the GitHub-side flow and keep Codex local-only.
