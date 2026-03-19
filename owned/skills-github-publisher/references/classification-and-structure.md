# Classification And Structure

Use these rules when deciding what actually belongs in a publishable GitHub repo.

## Candidate Classes

### Public Candidate

The skill is user-authored and does not depend on unpublished local state.

Signals:

- no real credentials in files
- no runtime cookie/session artifacts committed
- no user-specific absolute paths in docs
- no dependency on unpublished sibling-only files unless they will ship together

### Repo-Local

The skill is tightly coupled to one source repository.

Signals:

- references repo-specific scripts, build commands, or source tree assumptions
- only makes sense inside one codebase
- would be broken or misleading if copied into a generic public repo

Default action:

- keep it in the source repo, or publish it as a clearly repo-bound skill family

### Private Or Review-Required

The skill may be publishable later, but not by default.

Signals:

- relies on browser cookies, reverse-engineered APIs, or sensitive account workflows
- may raise compliance or ToS questions
- mixes user-owned content with private operational details

Default action:

- keep it out of the first public export until the user confirms

### Built-In

The content is system-owned rather than user-authored.

Signals:

- lives under `.system/`

Default action:

- exclude from the public export until authorship is explicit

### Third-Party

The content is copied, vendored, or otherwise originates outside your own skill source.

Signals:

- copied from an upstream repo or package
- kept under `vendor/` or a similar boundary
- has separate license files or package-manager ownership markers
- should retain upstream attribution or license context

Default action:

- exclude from the public export until license and authorship are explicit
- if intentionally included later, mark it as `third-party` in reports and export structure decisions
- if provenance is already known and inclusion is intentional, place it under a physical `third-party/` directory boundary in the export tree by default

## Recommended Repo Shapes

### One Public Repo For Generic Skills

Use when the skill family is broadly reusable and mostly global.

Good fit:

- general-purpose writing, visual, utility, or publishing skills

Suggested shape when the repo mixes ownership:

```text
skills-repo/
├── owned/
│   └── ...
└── third-party/
    └── ...
```

### Keep Repo-Local Skills With The Source Repo

Use when the skill only makes sense next to one project.

Good fit:

- build, codegen, review, or validation skills tied to a single repository layout

### Split Public And Private Repos

Use when some skills are clearly safe to publish and others are not.

Good fit:

- one repo for public skills
- one private repo or local-only tree for `danger-*`, experimental, or operational skills
- optional separate handling for `third-party` material when attribution or redistribution needs a distinct review

If a family is known to be external, such as a maintained `baoyu-*` family, treat that as `third-party` even when the current on-disk folder name does not say so.

## Structural Rules

- Prefer a clean export repo over publishing directly from a live working directory.
- Keep sibling-relative references valid after export. If a skill depends on another published sibling, keep both in the exported structure or rewrite the reference.
- Do not let one public repo contain silent dependencies on files that only exist on your laptop.
- If multiple skills share common references, keep that shared directory inside the export tree and preserve stable relative paths.
- Do not silently merge `third-party` content into `owned/` skill ownership. Keep the `third-party` classification explicit in reports and release notes.
- Prefer a physical `third-party/` directory boundary when ownership is known in advance.
- For final public distribution, require provenance and license metadata for each intentionally included `third-party` or vendored unit.
- Acceptable evidence can be either local metadata files such as `ORIGIN.md`, `ATTRIBUTION.md`, `PROVENANCE.md`, `LICENSE`, `NOTICE`, or a subtree-level manifest plus per-unit license metadata.
- A bare `package.json` only counts when it actually includes usable source metadata such as `repository` or `homepage`, and usable license metadata such as `license`.
- Placeholder manifests with `TODO`, `pending`, `unknown`, or similar review markers are draft artifacts only and do not satisfy the publication gate.
