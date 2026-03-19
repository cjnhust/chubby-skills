# Chubby Skills Repo Guide

This repository is intentionally public.
Keep publication safety and ownership boundaries explicit.

## Public Boundary

- Do not add `.system/`, `internal/`, or `danger-*` content.
- Do not commit local private policy files, `.env*`, cookies, browser profiles, local databases, or key material.
- Do not reintroduce local absolute paths, maintainer-only identifiers, or internal hostnames.

## Ownership Layout

- `owned/` contains user-owned skills maintained in this repository.
- `third-party/` contains imported external skills and vendored units.
- Do not silently fold `third-party/` content into `owned/`.
- Keep `third-party/ORIGIN.md`, `third-party/LICENSES.md`, and `THIRD_PARTY_ACKNOWLEDGEMENTS.md` aligned with any third-party updates.

## Validation

Run this before pushing:

```bash
python3 owned/skills-github-publisher/scripts/preflight_scan.py --root . --strict --strict-provenance --local-policy-file "$CODEX_HOME/private/publish-policy.json"
```

## Maintenance Posture

- Prefer small, reviewable changes.
- Keep initial sanitization and sensitive cleanup local-first.
- If using Codex on GitHub, prefer PR review before broader cloud-side edit flows.
