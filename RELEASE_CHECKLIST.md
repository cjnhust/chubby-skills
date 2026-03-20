# Release Checklist

Use this checklist before creating the public GitHub repository or pushing from this export.

## Required Checks

- Verify the root repository license still matches the intended scope of `owned/` content.
- Review `README.md`, `THIRD_PARTY_ACKNOWLEDGEMENTS.md`, `third-party/ORIGIN.md`, and `third-party/LICENSES.md` together.
- Keep `owned/` and `third-party/` boundaries explicit; do not fold imported skills into `owned/`.
- Re-run the strict preflight scan from the repository root.
- Verify the effective Git author identity is public-safe before committing or pushing.
- If managed skill bundle files changed, regenerate `.publish-sync/manifest.json` from the local sync flow before committing.
- Keep maintainer-specific sensitive scan inputs only in a local private policy file, not in committed commands or repo docs.
- Review `git status --short` and make sure ignored junk such as `node_modules/` is not part of the final handoff.
- Verify `.system/` and `danger-*` skills are still excluded unless you intentionally reviewed them for publication.
- Keep Codex GitHub maintenance disabled until the repository is already public, sanitized, and boundary-stable.

## Commands

```bash
python3 owned/skills-github-publisher/scripts/preflight_scan.py --root . --strict --strict-provenance --local-policy-file "$CODEX_HOME/private/publish-policy.json"
python3 owned/skills-github-publisher/scripts/check_git_identity.py --root . --strict --local-policy-file "$CODEX_HOME/private/publish-policy.json"
python3 owned/skills-github-publisher/scripts/publish_sync_manifest.py --root . --base-ref origin/main  # only when using the low-level sync path instead of prepare_incremental_pr.py
git config user.name "<public-name>"  # if the effective identity is still private
git config user.email "<public-email-or-github-noreply>"  # if the effective identity is still private
git status --short
git init -b main  # only for a fresh local repo
git switch -c codex/<change-name>  # for updates to an existing public repo
git add .
git commit -m "Prepare public skills export"
git show --stat --name-status --oneline -1
git status --short
git remote -v
gh auth login --hostname github.com --git-protocol https --web  # recommended for HTTPS remotes
git remote add origin <your-github-repo-url>  # prefer https://github.com/... for public repos when internal SSH keys also exist
python3 owned/skills-github-publisher/scripts/push_pr_handoff.py --root . --base main  # inspect push/PR handoff first
git push -u origin codex/<change-name>  # for updates to an existing public repo
gh pr create --base main --head codex/<change-name> --fill-first  # or open the PR in the GitHub UI
git ls-remote --heads origin codex/<change-name>
```

## GitHub Setup

- Create the target GitHub repository with the intended visibility.
- Prefer an HTTPS GitHub remote, or an explicit GitHub-only SSH alias, when the machine also carries separate internal SSH identities.
- Prefer GitHub CLI login or another OS-keychain-backed HTTPS credential flow over typing PATs into terminal prompts.
- Enable Secret Scanning and Push Protection before the first public push.
- For normal updates to an already public repo, push a PR branch and merge through pull request review rather than pushing directly to `main`.
- Treat `publish-sync-guard` as the source-of-truth gate for managed skill content and `codex-review-gate` as the review gate.
- If `gh` is not installed locally, use the helper script's printed compare URL and open the PR in the browser manually.
- Push only after the license decision, third-party manifests, and security scan are all in the expected state.
- If push protection blocks the push, treat it as a real blocker and fix the flagged content before retrying.
- If you later enable Codex on GitHub, start with PR review on the already public repository before allowing broader cloud-side edit flows.
- If a trusted maintainer later wants Codex to write back to an existing public PR branch, make that a one-off explicit request instead of wiring an automatic fix loop.
