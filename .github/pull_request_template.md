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
- [ ] If skill bundle files under `owned/<skill>/` or `third-party/<skill>/` changed, the change came from local source sync and `.publish-sync/manifest.json` was updated by the sync helper

## Codex Review

- [ ] Current head has received a Codex review
- [ ] All review threads are resolved before merge through GitHub conversation resolution
- Use one trigger path per head: repository auto review / reviewer request, or the manual fallback comment below. Do not stack both on the same head.
- The gate counts the resulting current-head Codex pull-request review. A standalone issue comment does not satisfy the gate.
- If you push another commit, wait for a fresh current-head review before merge.

Manual fallback comment if the repository is not already triggering Codex review:

```text
@codex review

Focus on secret leakage, local path regressions, internal-only content, and ownership boundary mistakes between owned/ and third-party/.
```
