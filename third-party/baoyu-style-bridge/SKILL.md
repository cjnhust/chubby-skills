---
name: baoyu-style-bridge
description: Normalize a visual style brief or visual profile into explicit style artifacts by patching saved outline.md files, STYLE INSTRUCTIONS blocks, prompt files, or targeted workspace-local .baoyu-skills EXTEND.md configs before image generation. Use when baoyu-cover-image, baoyu-article-illustrator, baoyu-slide-deck, baoyu-infographic, baoyu-xhs-images, or baoyu-image-gen outputs should follow a confirmed style authority rather than stock presets. This skill may be called by an orchestration skill, but it does not own workspace planning, selection bundles, or downstream routing.
---

# Baoyu Style Bridge

Use this skill between baoyu's content-structure generation and its final image generation whenever the default baoyu aesthetic is not the intended final style.

Also read [../shared/references/family-orchestration-contract.md](../shared/references/family-orchestration-contract.md).
Also read [../shared/references/extend-ownership-contract.md](../shared/references/extend-ownership-contract.md).
Also read [../shared/references/visual-source-preservation-contract.md](../shared/references/visual-source-preservation-contract.md).

## Purpose

This skill is the bridge layer for the visual family. It does not replace baoyu and it does not orchestrate document flow. It recommends or normalizes visual style, then writes explicit style artifacts that downstream skills can consume. Higher-level workflow ownership such as workspace creation, shared bundle persistence, and downstream routing belongs to orchestration skills such as `engineering-story-pipeline` or `baoyu-visual-pipeline`.

If this bridge will persist artifacts for a multi-step flow, also read [../shared/references/working-artifact-contract.md](../shared/references/working-artifact-contract.md). The caller owns the root working location; this skill decides only the target artifact files it patches or creates for style execution.

## Inputs

Any of these explicit inputs:

- `baoyu-slide-deck` `outline.md`
- `baoyu-slide-deck` `prompts/NN-slide-*.md`
- `baoyu-article-illustrator` `prompts/NN-*.md`
- `baoyu-infographic` `structured-content.md` and `prompts/infographic.md`
- `baoyu-comic` `storyboard.md` and `prompts/NN-*.md`
- `baoyu-cover-image` `prompts/cover.md`
- `baoyu-xhs-images` `outline.md` and `prompts/NN-*.md`
- direct `baoyu-image-gen` prompt files
- raw user style brief plus a task description when no prompt files exist yet
- optional workspace-local `.baoyu-skills/.../EXTEND.md`
- optional caller-provided style note such as `notes/style-selection.md`
- optional caller-provided shared bundle such as `notes/selection-bundle.md`

## Workflow

1. Read explicit style and content inputs first.
   - Prefer an explicit user style brief, caller-provided style note, saved style authority file, or the target prompt files that need patching.
   - If the caller provides a shared artifact such as `notes/selection-bundle.md`, treat it as one source artifact, not as state owned by this skill.
   - Use the stabilized article draft, visual inventory, talk track, audience note, or target deliverable only when they are relevant to the current style decision.
   - Determine:
     - technical rigor level
     - emotional temperature
     - data density
     - whether the piece is a proposal, deep dive, explainer, launch, benchmark, or retrospective
     - whether visuals should feel structural, editorial, energetic, or instructional

2. Recommend a style profile.
   - Read `references/style-profiles.md`.
   - If a caller-provided artifact already contains a confirmed visual profile, treat it as authoritative unless the user explicitly asks to revisit it.
   - If the user already supplied an explicit style brief or named style and is not asking for alternatives, skip recommendation and normalize that brief into the style authority instead of weakening it through re-interpretation.
   - Score candidate profiles based on content and user context, not deliverable type alone.
   - Produce:
     - one recommended profile
     - two or three alternatives
     - one-sentence rationale for each
   - When this skill runs standalone, ask the user to confirm the profile unless the user has explicitly locked one in.
   - When this skill runs under an orchestration skill, return the recommendation to the caller or patch only the caller-specified artifact. Do not create or mutate `notes/selection-bundle.md` on your own.
   - Save the result to `notes/style-selection.md` only when this bridge is used standalone, the user explicitly asks to persist the decision, or an audit trail is genuinely useful.

3. Identify the artifact type.
   - Deck outline or slide prompt
   - Article illustration prompt
   - Comic storyboard or comic page prompt
   - Cover prompt
   - workspace-local baoyu config

4. Load the style authority.
   - Read the chosen profile in `references/style-profiles.md`.
   - If the caller provides a canonical house-style file for the current task, use that file as the style authority.
   - If the user explicitly asks for the engineering-minimalism / blueprint technical-document look with matte charcoal background and `#FC5001` accent, normalize that request into a dedicated style-authority artifact for the current task instead of depending on unrelated pipeline state.
   - Otherwise read `references/default-house-style.md`.
   - If the user provided a newer style brief for the current task, it overrides the profile defaults.

5. Materialize only the requested targets.
   - Read `references/workspace-config-templates.md`.
   - If the current task is standalone direct generation, create only the local style-authority prompt file and patch only the target prompt files for this deliverable.
   - If the current task runs inside a document workspace and the caller explicitly asks for workspace materialization, write or update only the affected `.baoyu-skills/<skill>/EXTEND.md` files.
   - Do not create or rewrite local `EXTEND.md` files just because this bridge runs early. That decision belongs to the orchestrator.
   - Do not create unrelated baoyu configs just because they might be useful later.
   - When the user has provided an explicit style brief, materialize it as skill-appropriate custom style or palette entries and mark those entries as the saved defaults for the affected skills.
   - If the style is intended to be reused across projects, also write or update a global style prompt under `$HOME/.baoyu-skills/baoyu-image-gen/prompt-library/<style-slug>.md`.
   - Use the global style prompt for reusable aesthetic rules and keep document-specific narrative in workspace-local prompt files.

6. Patch saved artifacts, not ephemeral memory only.
   - Do not treat style normalization as permission to replace the canonical semantic source for the image.
   - For `outline.md`, replace the `STYLE INSTRUCTIONS` block and normalize any slide-level style drift.
   - For slide prompt files, rewrite palette, background, typography feel, diagram posture, and prohibited effects.
   - For article illustration prompt files, rewrite `STYLE`, `COLORS`, `ZONES`, and effect language so diagrams stay structural and label-driven.
   - For infographic prompt files, rewrite layout styling, palette, typography posture, and prohibited effects so the infographic inherits the same style authority instead of drifting back to gallery defaults.
   - For comic storyboard or prompt files, rewrite art, tone, layout, and scene posture so the comic matches the chosen theme rather than default comic energy.
   - For cover prompts, rewrite palette/rendering/decorative hints so the result reads like a technical launch poster rather than a generic tech poster.
   - For `baoyu-xhs-images`, preserve the chosen XHS-native `style` / `layout` / `preset` base, then patch `outline.md` and saved prompt files so any explicit style authority is expressed as refinements rather than replacing the skill's native social-platform visual grammar.
   - For direct `baoyu-image-gen` usage without upstream artifacts, create two saved prompt files before generation:
     - one style authority file
     - one task narrative file
     Then route final generation through `--promptfiles <style-file> <task-file>`.
   - If the user supplied raw visual content such as a prompt paragraph, Mermaid block, or diagram spec, preserve that source as its own saved artifact instead of collapsing it into the derived task narrative only.

7. Verify target artifacts before generation or regeneration.
   - Chosen profile cues are present in the saved artifacts that downstream generation will actually read.
   - Conflicting preset-native cues are removed.
   - Diagrams are structural or expressive in the way the chosen profile intends.
   - Slide deck cover and ending remain distinct from body slides.
   - If an image has already been generated, do not auto-judge pass or fail here. Hand off to the generating skill or caller for a concise human-readable review summary and let the user decide whether to regenerate.

## Effectiveness Contract

Style is considered applied only when it has been written into artifacts that downstream generation actually reads.

- For `baoyu-slide-deck`, that means the saved `outline.md` `STYLE INSTRUCTIONS` block and any slide prompt files.
- For `baoyu-article-illustrator`, that means saved prompt files under `prompts/`.
- For `baoyu-infographic`, that means saved `prompts/infographic.md`.
- For `baoyu-cover-image`, that means saved `prompts/cover.md`.
- For `baoyu-xhs-images`, that means the saved `outline.md` and prompt files under `prompts/`.
- For direct `baoyu-image-gen`, that means the exact files passed via `--promptfiles`.
- Workspace-local `.baoyu-skills/.../EXTEND.md` is effective only when the downstream skill explicitly reads and uses it as an input to prompt creation or option selection.
- Shared bundle artifacts such as `notes/selection-bundle.md` are orchestration-owned metadata. They are not the final executable style source of truth unless a caller explicitly extracts their contents into target prompt files or targeted configs.

If a style brief remains only in chat memory and is not materialized into one of these saved artifacts, treat the workflow as incomplete.

## Bridge Rules

- Never trust a baoyu preset as the final authority when the project has a content-driven visual profile.
- Style recommendation should be driven mainly by article content and narrative posture, then adjusted by explicit user preference.
- Do not treat provider/model defaults in `EXTEND.md` as art-direction defaults.
- When the user gives an explicit style brief, preserve it as the authority instead of replacing it with a looser inferred house style.
- When an explicit style brief exists, propagate it into each participating skill's saved config or prompt artifact instead of leaving it as chat-only context.
- Do not silently rewrite or compress the user's semantic visual source while applying style. Style normalization may add rendering guidance, but it must not become a black-box semantic rewrite layer.
- If a caller-provided shared bundle or style note already exists, reuse it before asking the user again.
- Deliverable type can influence execution details, but it must not be the primary style selector.
- This skill consumes explicit style inputs and outputs explicit style artifacts. It does not own workspace creation, backlog planning, or downstream routing.
- Only orchestration skills may own or mutate shared bundle artifacts such as `notes/selection-bundle.md`.
- Materialize workspace-local baoyu config only when the current task or caller explicitly requires workspace-level reuse.
- Always patch saved files before generation or regeneration.
- Prefer document workspaces over repository-wide config when the style belongs to one article or one article family.
- Prefer a global prompt-library file when the style is a reusable personal or team visual system that should survive across projects.
- If exact structural fidelity matters more than baoyu's workflow, patch the prompt and then route final generation through `baoyu-image-gen`.

## References

- Default house style: `references/default-house-style.md`
- Content-driven style profiles: `references/style-profiles.md`
- Artifact patch matrix: `references/patch-matrix.md`
- Workspace config templates: `references/workspace-config-templates.md`
