## Summary

- What changed?
- Why is it needed?

## Public Boundary Check

- [ ] No `.system/`, `internal/`, or `danger-*` content was introduced
- [ ] No local absolute paths, personal identifiers, internal hosts, or private policy values were introduced
- [ ] No `.env*`, cookies, browser profiles, key material, or local databases were introduced
- [ ] `owned/` and `third-party/` boundaries remain explicit
- [ ] Third-party attribution / provenance docs were updated if imported content changed

## Validation

- [ ] Ran `python3 owned/skills-github-publisher/scripts/preflight_scan.py --root . --strict --strict-provenance --local-policy-file "$CODEX_HOME/private/publish-policy.json"`

## Codex Review

- Recommended comment after opening the PR:

```text
@codex review

Focus on secret leakage, local path regressions, internal-only content, and ownership boundary mistakes between owned/ and third-party/.
```
