# Release Checklist

Use this checklist before creating the public GitHub repository or pushing from this export.

## Required Checks

- Choose the root repository license for `owned/` content and add `LICENSE` before public release.
- Review `README.md`, `THIRD_PARTY_ACKNOWLEDGEMENTS.md`, `third-party/ORIGIN.md`, and `third-party/LICENSES.md` together.
- Keep `owned/` and `third-party/` boundaries explicit; do not fold imported skills into `owned/`.
- Re-run the strict preflight scan from the repository root.
- Verify `.system/` and `danger-*` skills are still excluded unless you intentionally reviewed them for publication.

## Commands

```bash
python3 owned/skills-github-publisher/scripts/preflight_scan.py --root . --strict --strict-provenance
git init -b main
git add .
git status --short
```

## GitHub Setup

- Create the target GitHub repository with the intended visibility.
- Enable Secret Scanning and Push Protection before the first public push.
- Push only after the license decision, third-party manifests, and security scan are all in the expected state.

