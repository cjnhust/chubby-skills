# EXTEND Ownership Contract

Read this reference whenever a skill family uses `EXTEND.md`, workspace-local `.baoyu-skills/.../EXTEND.md`, or any other saved preference layer in addition to explicit task artifacts.

The goal is to keep stable defaults, request-scoped intent, and pipeline-local materialization separate.

## Three Buckets

### 1. Direct Defaults

These are stable preferences owned by one skill's own `EXTEND.md`.

Examples:
- `baoyu-image-gen` provider, model, quality, aspect ratio
- `baoyu-url-to-markdown` default output directory or media-download preference
- `baoyu-translate` default target language, glossary, or default mode
- `baoyu-markdown-to-html` default theme

Rules:
- Read only the current skill's own `EXTEND.md`.
- Treat these values as defaults for this skill's execution behavior, not as hidden cross-skill intent.
- An explicit user request, CLI flag, or saved task artifact may override them for the current run.
- A pipeline may suggest changes to these defaults, but it must not silently rewrite or replace the user's stable defaults.

### 2. Request-Scoped Explicit Inputs

These belong to the current run and should stay explicit.

Examples:
- a confirmed style authority
- a shared theme passed into one export run
- a one-off target audience, glossary override, or review posture
- a current run's diagram structure, prompt narrative, or redraw constraint

Rules:
- Do not hide request-scoped intent in an unrelated skill's `EXTEND.md`.
- Prefer explicit saved artifacts, prompt files, notes, or direct flags for values that are specific to the current run.
- If multiple skills need the same request-scoped value, the orchestrator should persist one explicit source of truth and pass it forward.

### 3. Pipeline-Materialized Local Defaults

These are run-local or workspace-local defaults written by an orchestrator so downstream skills can reuse them during the current flow.

Examples:
- workspace-local `.baoyu-skills/<skill>/EXTEND.md` created for one document pipeline
- request-local visual style defaults materialized for several downstream visual leaves
- a local theme/config layer written for one staged export flow

Rules:
- The orchestrator decides whether this layer is needed.
- Materialize local defaults only when reuse across multiple downstream steps is worth the extra state.
- Keep them scoped to the current request or workspace. Do not silently overwrite the user's home-level defaults.
- Bridges may patch or create targeted local `EXTEND.md` files only when the caller asked for that materialization.

## Resolution Order

When multiple layers exist, resolve in this order:

1. explicit user request, CLI flag, or saved task artifact for the current run
2. pipeline-materialized local default for the current request or workspace
3. the skill's own direct `EXTEND.md` default
4. built-in skill fallback

## Ownership Rules

- The family pipeline or workspace orchestrator may decide when to create local `EXTEND.md` files, but it does not own the user's persistent home defaults.
- A bridge may normalize or patch target files, including local `EXTEND.md`, but it does not own the policy for when that layer should exist.
- A leaf skill may read its own `EXTEND.md` and explicit inputs. It should not read another skill's `EXTEND.md` as a hidden fallback.
- Runtime defaults such as provider/model are not the same as style authority, narrative intent, or cross-skill art direction.

## Practical Guidance

- Use direct defaults for stable personal or project preferences.
- Use explicit artifacts for current-run intent that must stay inspectable.
- Use local materialized defaults only when the pipeline needs reusable saved state across several downstream steps.
- If a pipeline believes another model, theme, or preset may work better, surface that as a suggestion unless a hard requirement forces a change.
