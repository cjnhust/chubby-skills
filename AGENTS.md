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
- If a trusted maintainer explicitly asks Codex to fix feedback, keep the request limited to the current already-public PR branch and require minimal patch scope.

## Codex Review Mode

- Default to review-first usage on GitHub for this repository.
- Prefer `@codex review` on public pull requests rather than cloud-side code generation by default.
- A trusted maintainer may explicitly request one follow-up writeback on the current public PR branch with wording such as `@codex fix the latest review feedback on this existing PR branch. Update this PR branch directly with the minimal patch and do not widen scope.`
- Do not treat `@codex fix ...` as an automatic loop or as a substitute for the hard merge gate.
- Treat `codex-review-gate` as the hard merge gate when the workflow is present.
- Keep `main` in PR-only mode and let GitHub auto-merge after the gate succeeds.
- Review focus should stay on:
  - secret leakage or local-path regressions
  - ownership-boundary mistakes between `owned/` and `third-party/`
  - accidental inclusion of `.system/`, `internal/`, `danger-*`, or runtime credential artifacts
  - provenance or attribution regressions in third-party material
- Do not request Codex cloud work on unpublished branches that contain local-only policy values or other sensitive content.
