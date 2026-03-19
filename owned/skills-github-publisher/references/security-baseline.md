# Security Baseline

Use this baseline for publication prechecks.

## Intent

This skill uses a shift-left security posture:

- catch problems before publication
- keep secrets and runtime credentials out of the repo
- treat remediation as reviewable work, not silent cleanup

## External Baseline Sources

- NIST SSDF
  - security should be integrated early in the development lifecycle instead of deferred to release time
  - publication checks should be part of the preparation workflow, not a last-minute afterthought
- OWASP Secrets Management guidance
  - secrets should not be hardcoded in source or left in developer-owned files inside the repo
  - secrets should be replaced by environment- or platform-managed access paths, not copied into skills
- GitHub secret scanning and push protection
  - repositories should detect and block provider and non-provider leaked secret patterns before they are pushed
  - auth headers, bearer/basic credentials, webhook URLs, and credential-bearing URIs are all worth pre-push screening

## Local Publication Rules Derived From That Baseline

- block hardcoded secrets and private keys
- block hardcoded auth headers, JWT-like tokens, webhook secrets, and credential-bearing URIs
- block quoted and unquoted secret-like assignments when they are not obvious placeholders or env-var references
- block committed runtime credential artifacts such as cookies, sessions, browser profiles, `.env*`, `.npmrc`, `.pypirc`, `.netrc`, SSH keys, and local cloud credential directories
- block user-specific absolute paths in committed docs and scripts
- keep third-party ownership explicit and separate from `owned/` content
- for publish-ready exports, require origin and license metadata for each intentionally included `third-party` or vendored unit
- do not treat placeholder manifests, TODO checklists, or `pending` review stubs as satisfying provenance or license review
- default to audit first, then apply approved fixes
