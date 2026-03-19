# Security Policy

This repository publishes Codex skills and helper scripts. It is prepared for source sharing, not for storing runtime credentials, browser state, or local machine secrets.

## Never Commit

- Real API keys, access tokens, cookies, session exports, browser profiles, local databases, or raw private-key material.
- `.env` files or machine-local overrides containing non-placeholder credentials.
- Built-in `.system/` skills or `danger-*` skills unless they have been intentionally exported and separately reviewed.

## Safe Patterns

- Keep credentials in environment variables or a local secret manager.
- Keep third-party material inside `third-party/` with explicit origin and license review.
- Keep maintainer-specific sensitive scan inputs in a local private policy file such as `$CODEX_HOME/private/publish-policy.json`, not in committed docs or shared shell snippets.
- Prefer redacted examples such as `your_token_here` instead of live values.

## Reporting

If you find a leaked secret or sensitive local path:

1. Do not paste the raw value into a public issue.
2. Rotate or revoke the credential first if it is real.
3. Contact the maintainer privately with redacted evidence and affected file paths.

## Local Preflight

Run the staged export scan before public release:

```bash
python3 owned/skills-github-publisher/scripts/preflight_scan.py --root . --strict --strict-provenance --local-policy-file "$CODEX_HOME/private/publish-policy.json"
```

After creating the GitHub repository, enable Secret Scanning and Push Protection before the first public push.
