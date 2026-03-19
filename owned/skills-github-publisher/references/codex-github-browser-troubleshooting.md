# Codex GitHub Browser Troubleshooting

Use this note only when the user explicitly authorizes local browser-side help for ChatGPT, Codex, or GitHub setup.

## Existing Safe Pattern

Local CDP-capable skills in this environment already follow a conservative browser pattern:

- launch a fresh isolated Chrome profile
- keep login manual
- avoid reading cookies, local storage, session storage, or browser credential files
- stay on a narrow hostname allowlist
- delete or discard the temporary profile after the run unless the operator explicitly keeps it

Reuse that pattern here instead of inventing a looser one.

## What This Is Good For

- opening the relevant ChatGPT, Codex, GitHub, or Help Center pages
- checking whether the right public repository is visible after the user logs in
- verifying that a public PR comment or review trigger is present
- helping the user step through the setup when plain-text instructions are not enough

## What This Must Not Do

- do not attach to the user's default browser profile by default
- do not scrape cookies, OAuth tokens, local storage, or saved passwords
- do not expand from public setup sites into unrelated browsing
- do not use browser automation as a reason to access internal repositories or private policy files

## Allowed Host Scope

For public Codex-on-GitHub setup, keep browser-side help limited to the minimum public hosts:

- `chatgpt.com`
- `github.com`
- `help.openai.com`

Only widen this if the user explicitly asks and the destination is still public and relevant.

## Operator Posture

- prefer local-only troubleshooting first
- prefer an isolated profile over any attempt to reuse the user's long-lived logged-in browser state
- if the page requires login, pause for the user to log in manually, then resume local inspection
- if the browser flow still cannot be verified safely, stop and fall back to a human checklist
