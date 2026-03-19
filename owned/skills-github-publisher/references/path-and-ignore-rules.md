# Path And Ignore Rules

Use these rules when turning a local skill tree into a publishable repo.

## Path Rewrite Rules

### Replace User-Specific Absolute Paths In Docs

Bad:

- `/Users/<user>/.codex/skills/writing-theme-bridge/SKILL.md`
- `~/.codex/skills/engineering-story-pipeline/references/visual-system.md`

Good when the target ships in the same bundle:

- `../writing-theme-bridge/SKILL.md`
- `../engineering-story-pipeline/references/visual-system.md`

Good when the target is an installed sibling skill:

- `$CODEX_HOME/skills/writing-theme-bridge/SKILL.md`

## Do Not Rewrite Legitimate Runtime Storage Code By Reflex

These are often acceptable in scripts:

- `os.homedir()`
- `APPDATA`
- `XDG_DATA_HOME`
- configurable `*_DATA_DIR`, `*_COOKIE_PATH`, or similar env overrides

Those patterns are runtime storage decisions. They are not publish leaks unless:

- a real local path is hardcoded in committed code or docs
- runtime data files have already been committed

## Ignore Baseline

Start with this baseline in the export repo:

```gitignore
.DS_Store
__pycache__/
*.pyc
node_modules/
.env
.env.*
.npmrc
.pypirc
.netrc
.dockercfg
cookies.json
consent.json
sessions/
chrome-profile/
.aws/
.ssh/
.kube/
id_rsa
id_dsa
id_ecdsa
id_ed25519
*.db
*.sqlite
*.pem
*.key
*.p12
*.pfx
*.kdbx
*.ovpn
```

## Secret Review Heuristics

Usually safe:

- env-var names such as `OPENAI_API_KEY`
- placeholder values such as `your_key_here`, `example-token`, `dummy-secret`

Not safe:

- concrete bearer tokens
- private keys
- real cookie or session files
- hardcoded passwords or API keys
- hardcoded `Authorization`, `X-API-Key`, or `Cookie` headers
- URIs containing embedded credentials such as `https://user:pass@host`
- internal-only hosts or corp-network registries such as `docs.corp.*` or `npm.corp.*`
- personal identifiers the maintainer marked as non-public

When uncertain, redact the value in summaries and treat the file as blocked for public export until reviewed.

For maintainer-specific sensitive blocklists:

- keep them in a local private file such as `$CODEX_HOME/private/publish-policy.json`
- allow that file to carry exact literals, regexes, and extra secret/internal-host detection rules
- do not commit that file
- do not put the raw sensitive values into shared shell history, README examples, or public skill docs

## Security Change Policy

Default order:

1. scan and report
2. propose redacted fixes
3. wait for user confirmation
4. apply the approved fixes to the staged export

If the user explicitly wants to avoid repeated cleanup work, sync generic security hygiene fixes back to the original skills as well:

- absolute path rewrites
- personal-info redaction
- removal of leaked lockfiles or other committed internal-host artifacts

Do not sync pure export-boundary decisions back to source unless the user asked for that too:

- excluding an internal-only skill from a public repo
- moving content under `third-party/`
- splitting one export into separate public/private repos

Only skip step 3 when the user explicitly asked for an apply pass rather than an audit pass.
