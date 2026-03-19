---
name: baoyu-visual-pipeline
description: Orchestrate non-trivial visual generation requests by choosing the right visual deliverable skill, normalizing style through baoyu-style-bridge when needed, materializing prompt artifacts, rendering a first pass, and then running a short review loop. Use when the user asks to generate images with explicit style briefs, reference images, multiple outputs, saved prompt files, platform-specific visuals such as covers, infographics, XHS series, comics, or iterative art direction rather than a one-shot raw prompt.
---

# Baoyu Visual Pipeline

Use this skill as the request-level orchestration layer for visual-only tasks.

Also read [../../owned/shared/references/family-orchestration-contract.md](../../owned/shared/references/family-orchestration-contract.md).
Also read [../../owned/shared/references/extend-ownership-contract.md](../../owned/shared/references/extend-ownership-contract.md).
Also read [../../owned/shared/references/visual-source-preservation-contract.md](../../owned/shared/references/visual-source-preservation-contract.md).

It is the family pipeline for the visual-generation family and owns sequencing for the current visual request:
- choosing the deliverable family
- establishing a working location when intermediate artifacts are needed
- deciding when `baoyu-style-bridge` must run
- deciding when request-scoped style intent stays explicit versus becomes local saved defaults
- ensuring prompt artifacts exist before final render
- stopping after first-pass output for a short review before broad regeneration

It does not own document-level bundle persistence or multi-deliverable article/deck coordination. Those remain with `engineering-story-pipeline`.

## Entry Rules

Use this skill when the request is any of the following:

- image generation with an explicit style brief or named aesthetic
- generation from references, Mermaid, saved prompt files, or redraw constraints
- multiple related images or variants
- deliverable-specific visual work such as cover image, infographic, comic, or XHS series
- any request where the user is likely to want a first pass, then a keep/regenerate decision

Do not use this skill for a trivial one-shot render such as a single raw prompt with no reusable style or intermediate artifacts. In that case, use `baoyu-image-gen` directly.

If the request expands into document writing, shared article/deck state, or cross-deliverable narrative coordination, hand off to `engineering-story-pipeline`.

## Working Artifact Contract

If the run creates intermediate artifacts, also read [../../owned/shared/references/working-artifact-contract.md](../../owned/shared/references/working-artifact-contract.md).

When this skill is the request-level orchestrator:
- it owns the root working location for the current visual run
- it decides which artifacts must have stable cross-skill paths
- downstream capability skills may choose their own internal layout under that working location

## Routing

Choose the target visual skill before final rendering:

- direct one-off render or redraw from finalized prompt files -> `baoyu-image-gen`
- article/document cover -> `baoyu-cover-image`
- dense information visual -> `baoyu-infographic`
- Xiaohongshu image series -> `baoyu-xhs-images`
- educational or narrative comic -> `baoyu-comic`
- article illustration set -> `baoyu-article-illustrator`
- slide deck images -> `baoyu-slide-deck`

Prefer the most specific visual skill that already matches the requested deliverable. Use `baoyu-image-gen` as the general leaf renderer, not as the default first stop for every visual request.

## Workflow

1. Normalize the request into explicit inputs.
   - Save the user brief, content source, reference images, and any structural source such as Mermaid or outline notes.
   - If the request is likely to need review, regeneration, or cross-skill handoff, persist those inputs in the working location instead of relying on chat memory.
   - Treat raw user visual descriptions, Mermaid blocks, diagram specs, verbatim labels, and exclusions as canonical source artifacts rather than disposable staging text.

2. Pick the target visual branch.
   - Decide whether the request is really a cover, infographic, comic, XHS series, slide deck, article illustration batch, or a direct image render.
   - Route into that skill family before any final image generation starts.

3. Materialize structure and prompt artifacts first.
   - If the target skill has an outline/spec/prompt stage, stop there first and let that skill create its saved artifacts.
   - Examples: `outline.md`, `storyboard.md`, `prompts/*.md`, `prompts/cover.md`, `prompts/infographic.md`.
   - Do not jump into final rendering before these artifacts exist when the chosen deliverable expects them.
   - If you create derived prompt narratives for rendering, keep the canonical visual source artifact alongside them instead of replacing it with prose-only summaries.

4. Resolve style authority before rendering.
   - If the user supplied an explicit style brief, reusable house style, or wants consistency across multiple outputs, call `baoyu-style-bridge` before the final image generation step.
   - The bridge should patch saved artifacts for the chosen deliverable.
   - Keep style authority explicit by default. Materialize workspace-local `.baoyu-skills/.../EXTEND.md` only when the current flow genuinely benefits from reusable local defaults.
   - Never start with `baoyu-image-gen` and then backtrack into `baoyu-style-bridge` as the primary path.
   - For deliverables with native visual systems, such as `baoyu-xhs-images`, preserve the deliverable-native base style and use the bridge only to map explicit external style authority into saved artifacts as refinements.
   - Preserve the user's configured or explicitly chosen image provider/model as the default rendering baseline. Do not silently switch models just because another model seems better suited to the content. Only suggest or force a switch when the user asks for it, a hard requirement is unsupported, or the current attempt already failed.

5. Render the first pass.
   - Invoke the chosen capability skill using the saved artifacts and explicit output paths from the working location.
   - When the chosen skill itself uses `baoyu-image-gen` as an internal renderer, treat that as a downstream leaf call rather than a separate orchestration decision.
   - Before rendering, verify that the final prompt artifacts still preserve or explicitly reference the canonical visual source rather than only a black-box rewrite.

6. Review before broad regeneration.
   - After the first successful render or representative first pass, summarize visible deviations in structure, style, readability, reference fidelity, and deliverable-specific differentiation.
   - Let the user decide whether to keep, adjust prompts, or selectively regenerate.
   - Prefer targeted prompt fixes and selective regeneration over rerunning the whole batch by reflex.

7. Finish or hand off.
   - If the user accepts the first pass, stop.
   - If the user wants another pass, keep the saved prompt artifacts as the source of truth and regenerate selectively.
   - If the request grows into document-level coordination, move the task to `engineering-story-pipeline`.

## Boundary Rules

- `baoyu-style-bridge` is a pre-render normalizer, not the owner of visual sequencing.
- `baoyu-image-gen` is a rendering capability. It should consume explicit prompt files or a direct raw prompt when no broader orchestration is needed.
- The existence of a style brief, prompt files, references, or regeneration intent is usually a signal to use this pipeline skill first.
- The absence of those signals may justify a direct `baoyu-image-gen` call.
