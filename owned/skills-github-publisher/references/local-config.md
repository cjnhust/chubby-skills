# Local Config

Use a private local config when one maintainer repeatedly updates the same publish repo and wants to avoid retyping workstation paths in every run.

## Recommended Path

- `$CODEX_HOME/private/skills-github-publisher.json`
- fallback: `~/.codex/private/skills-github-publisher.json`

Keep this file outside the publish repo.

## Supported Keys

- `default_publish_repo`
  - absolute path to the preferred publish repo working copy
- `default_owned_root`
  - absolute path to the repo's `owned/` directory when incremental skill updates should land there
- `default_local_policy_file`
  - absolute path to the local private scan policy file, usually `$CODEX_HOME/private/publish-policy.json`

## Example

```json
{
  "default_publish_repo": "/path/to/chubby-skills",
  "default_owned_root": "/path/to/chubby-skills/owned",
  "default_local_policy_file": "/path/to/.codex/private/publish-policy.json"
}
```

## Rules

- Do not commit this file.
- Do not copy these absolute paths into `SKILL.md`, `README.md`, release docs, or shared shell snippets.
- Use it only to resolve local defaults for one maintainer machine.
- Incremental update flows should prefer syncing into the configured publish repo working copy instead of creating a new ad hoc staging tree each time.
- For repeat work on one publish repo, treat `default_publish_repo` as the fixed working copy and branch from there instead of creating a new sibling directory for every run.
- Treat that fixed publish repo as a mirror, not the authoring source of truth for skill bundle content.
- A good repeated flow is:
  1. `python3 scripts/prepare_incremental_pr.py --skill-root <absolute-skill-root> [...]`
  2. review and commit the PR branch changes in the fixed publish repo
  3. `python3 scripts/push_pr_handoff.py --base main`
