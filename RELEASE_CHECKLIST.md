# Release Checklist

Use this checklist before creating the public GitHub repository or pushing from this export.

## Required Checks

- Verify the root repository license still matches the intended scope of `owned/` content.
- Review `README.md`, `THIRD_PARTY_ACKNOWLEDGEMENTS.md`, `third-party/ORIGIN.md`, and `third-party/LICENSES.md` together.
- Keep `owned/` and `third-party/` boundaries explicit; do not fold imported skills into `owned/`.
- Re-run the strict preflight scan from the repository root.
- Keep maintainer-specific sensitive scan inputs only in a local private policy file, not in committed commands or repo docs.
- Review `git status --short` and make sure ignored junk such as `node_modules/` is not part of the final handoff.
- Verify `.system/` and `danger-*` skills are still excluded unless you intentionally reviewed them for publication.

## Commands

```bash
python3 owned/skills-github-publisher/scripts/preflight_scan.py --root . --strict --strict-provenance --local-policy-file "$CODEX_HOME/private/publish-policy.json"
git status --short
git init -b main  # only for a fresh local repo
git add .
git commit -m "Prepare public skills export"
git show --stat --name-status --oneline -1
git status --short
git remote -v
git remote add origin <your-github-repo-url>  # only if origin is not set yet
git push -u origin main
git ls-remote --heads origin main
```

## GitHub Setup

- Create the target GitHub repository with the intended visibility.
- Enable Secret Scanning and Push Protection before the first public push.
- Push only after the license decision, third-party manifests, and security scan are all in the expected state.
- If push protection blocks the push, treat it as a real blocker and fix the flagged content before retrying.

