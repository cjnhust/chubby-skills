# Codex GitHub Maintenance

Use this note when deciding whether a published skills repository should later use Codex on GitHub.

## Official Capability Review

The current OpenAI official docs show three relevant capabilities:

- Codex web can connect to GitHub, work on repository code, and create pull requests.
- GitHub issue and pull-request workflows can delegate to Codex with `@codex`.
- Codex can automatically review GitHub pull requests.
- OpenAI also provides a Codex GitHub Action for CI or shell-based automation.

Primary official references:

- https://developers.openai.com/codex/cloud
- https://help.openai.com/en/articles/11369540-codex-in-chatgpt
- https://openai.com/index/codex-now-generally-available/

## Conservative Recommendation For This Skill

This publication skill should default to security-first behavior:

- do not send unpublished skill trees to Codex cloud
- do not use `@codex` against internal-only or mixed public/private repositories
- do not expose local private policy files, internal-only skills, or pre-sanitization branches to GitHub-side Codex flows

For this skill, Codex GitHub integration is only a post-publication option.

## Recommended Order

1. Sanitize locally.
2. Confirm the public export boundary locally.
3. Publish the repository.
4. Only then consider GitHub-side Codex maintenance.

## Preferred First Use

If the repository is already intentionally public and stable:

- prefer Codex review on pull requests first
- then consider `@codex` or a Codex GitHub Action for follow-up maintenance

This order keeps the first GitHub-side use narrower and easier to audit.

## Not Covered By This Skill

This skill does not approve Codex cloud usage for internal repositories.
If the user wants Codex on internal code, that requires a separate internal-security and admin-controls review.
