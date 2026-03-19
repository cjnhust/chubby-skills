---
name: engineering-story-pipeline
description: Chain Chinese technical writing, diagrams, and slide-deck work into one pipeline by combining engineering-practice-writer with baoyu skills such as baoyu-format-markdown, baoyu-cover-image, baoyu-article-illustrator, baoyu-slide-deck, and baoyu-image-gen. Use for all technical-writing requests around project documents, architecture notes, design proposals, technical articles, technical sharing drafts, technical research reports, polishing technical prose, or framework/RFC write-ups from local notes, files, or URLs, especially when the work may later need diagrams, cover images, or a slide deck. Also use when the user wants to keep one narrative across article and deck, or render Mermaid-like architecture and flow diagrams in one engineering visual system.
---

# Engineering Story Pipeline

Use this skill when the user wants one end-to-end technical storytelling workflow instead of isolated writing or image-generation steps.

Also read [../shared/references/family-orchestration-contract.md](../shared/references/family-orchestration-contract.md).
Also read [../shared/references/extend-ownership-contract.md](../shared/references/extend-ownership-contract.md).
Also read [../shared/references/transform-traceability-contract.md](../shared/references/transform-traceability-contract.md).
Also read [../shared/references/visual-source-preservation-contract.md](../shared/references/visual-source-preservation-contract.md).

## Scope

Pick only the deliverables the user asked for:

- source ingestion from URL or raw notes
- translation or localization into Chinese
- Chinese technical article or rewrite
- Chinese technical research report
- article cover image
- inline diagrams and illustrations
- slide outline
- slide images, PPTX, or PDF
- optional HTML export

This skill is the workspace-level orchestrator for the technical-story family. It owns:
- document workspace creation and reuse
- shared bundle persistence such as `notes/selection-bundle.md`
- downstream routing between writing, visual, and export skills
- deciding when request-scoped values stay as explicit artifacts versus workspace-local `.baoyu-skills/.../EXTEND.md`
- pass closure and next-step tracking

Bridge skills such as `writing-theme-bridge` and `baoyu-style-bridge` are advisors or normalizers. Capability skills such as `baoyu-image-gen`, `baoyu-cover-image`, `baoyu-infographic`, and `baoyu-markdown-to-html` should consume explicit artifacts and should not own the shared bundle or overall sequencing.

For isolated visual-only requests inside this family, prefer the request-level `baoyu-visual-pipeline` rather than dropping straight into a leaf renderer.
For isolated ingest/translate/format/export flows without larger narrative rewriting, prefer `baoyu-content-pipeline`.

## Working Directory Contract

Also read [../shared/references/working-artifact-contract.md](../shared/references/working-artifact-contract.md).

When this skill is the orchestrator for a document run, it owns the root working location and the shared cross-skill artifact paths for that run.

For local technical-writing requests, this skill should still trigger even if the user initially asks only for the document itself. In that case, enter pipeline mode but keep the default output conservative: produce the source-of-truth draft first, then prepare a visual inventory, and stop before image generation unless the user asks for visuals or the need is explicit.

Single-step technical writing is still part of this pipeline. The difference is only where execution stops.

For topic-based or URL-based research-report flows that need theme confirmation, source discovery, evidence synthesis, and scope control before drafting, prefer an upstream research orchestrator rather than starting directly from this pipeline.

## Workflow

0. Create the document workspace first.
   - Read `references/document-workspace.md`.
   - Also read `references/selection-bundle.md`.
   - Also read `references/flow-closure.md`.
   - Also read `references/source-fidelity-check.md` when the source is already a mature technical document.
   - Create one workspace per document or article.
   - This workspace stores:
     - source material
     - draft and rewrite artifacts
     - `selection-bundle.md`
     - `visual-inventory.md`
     - workspace-local `.baoyu-skills/.../EXTEND.md`
     - prompts, outlines, illustrations, deck outputs, and exports
   - Run downstream baoyu skills from the workspace root so they read the workspace-local `.baoyu-skills` first.

1. Normalize the source material into the workspace.
   - If the source is a webpage, ingest it with `baoyu-url-to-markdown` into the workspace.
   - If the source language is not the target language, or the material is bilingual, run `baoyu-translate` into the workspace before rewriting.
   - Materialize raw inputs into workspace files before heavy editing.
   - Keep raw source artifacts preserved alongside later rewrites, translations, and exports instead of silently replacing the only saved copy.
   - Strip credentials, tokens, secrets, and internal-only literals before they enter prompts, visuals, or shareable outputs.
   - For long technical material, preserve terminology early. Reuse glossary rules rather than retranslating key terms ad hoc.
   - Assess whether the source is already a mature, sectioned technical document. If it is, default the next drafting pass to preservation mode rather than full rewrite mode.
   - For a mature technical document, extract a lightweight source contract before rewriting. Save it under `notes/source-contract.md` and include at minimum:
     - original title and stated document positioning
     - the source's explicit question list or purpose list
     - top-level and major second-level section map
     - existing figure anchors, image positions, and diagram positions
     - claims or constraints that must not be reframed
     - which parts may tolerate presentation cleanup or local reorganization without changing review semantics

2. Build one selection bundle before drafting.
   - Read `references/theme-profiles.md`.
   - Also use `writing-theme-bridge` and `baoyu-style-bridge` as advisors when the default mapping is not obvious.
   - Analyze the normalized source and recommend:
     - one theme
     - one writing posture
     - one visual profile
     - two or three viable alternatives
   - Present one unified recommendation and ask for one confirmation unless the user has already locked the choices.
   - Save the result to `notes/selection-bundle.md` because this pipeline owns writing behavior, downstream skill routing, and workspace-local baoyu config.
   - If the user has already given an explicit visual style brief, keep the selected visual profile for routing purposes, but also persist that brief as a style override in `notes/selection-bundle.md` so downstream skills inherit the exact requested look.
   - Once the bundle is confirmed, call `baoyu-style-bridge` with explicit inputs from the bundle and explicit target artifacts. The pipeline decides whether any workspace-local `.baoyu-skills/.../EXTEND.md` materialization is needed.
   - Do not treat workspace-local `EXTEND.md` as mandatory. Keep request-scoped intent explicit unless stable reuse across later steps justifies local materialization.

3. Stabilize the narrative.
   - Start with `writing-theme-bridge`.
   - Use it to read `notes/selection-bundle.md` first and only recommend a posture separately if the bundle is missing or incomplete.
   - Route the actual drafting through `engineering-practice-writer` or the selected posture behavior.
   - If the source is already a mature technical document, treat this as a bounded editorial pass by default:
     - preserve the original thesis and scope
     - preserve major section order and heading semantics
     - preserve existing figure anchors and image positions conceptually
     - preserve explicit problem statements, question counts, and section contracts unless the user explicitly asked to rewrite them
     - avoid introducing new framing questions, merged sections, or synthesized summary structures unless the user explicitly asked for a larger rewrite
     - prefer sentence-level cleanup and local paragraph clarification over global reframing
     - limited presentation cleanup is allowed when it does not change the document's semantic contract, for example:
       - normalize heading wording or numbering
       - turn flat prose into tables or lists
       - split or merge nearby paragraphs inside the same review boundary
       - add adjacent Mermaid placeholders to clarify an existing image slot
   - Do not begin visual generation until the draft is structurally clear: scenario, problem, constraints, decision, tradeoffs, and outcome.
   - If the source is rough notes, first turn it into a sectioned draft or talk track.
   - Keep one article draft in the workspace as the source of truth for all later visuals and deck work.
   - Working drafts may include minimal workflow-facing scaffolding while the article is under review, but treat that as temporary.
   - Separate rewriting from formatting. Content decisions happen here; typography and publish formatting happen later.

4. Clean the article into a reader-facing deliverable before formal output.
   - Do not treat the first completed text pass as a reader-facing final by default when this pipeline is still expected to continue into visual planning, deck work, or later article illustration.
   - In pipeline mode, the default review artifact is the working draft under `drafts/article.md`, not `exports/article-final.md`.
   - If likely visuals have not yet gone through visual inventory and placeholder insertion, keep the article in working-draft state and review that version with the user first.
   - Before treating the article as a formal document, remove workspace-facing helper text such as:
     - source-of-truth draft banners
     - local workspace paths
     - references to `notes/selection-bundle.md` or `notes/visual-inventory.md`
     - "if later you want images or deck" process hints
   - Preserve only reader-facing navigation that belongs in the article itself.
   - Save the cleaned result as a reader-facing article, preferably under `exports/article-final.md`, or replace the working draft only after the user clearly wants the formal version to become canonical.
   - When accepted visuals are being integrated into the formal article:
     - remove review-only placeholder blocks and temporary review notes from the reader-facing version
     - keep the chosen image references in place near the approved section anchors
     - do not discard the approved Mermaid or node-edge source; preserve it under `notes/diagram-structures.md` or an equivalent saved artifact before cleaning the article

5. Run a source-fidelity check before visuals or formal export.
   - When the source started as a mature technical document, compare the current draft against `notes/source-contract.md`.
   - Save the check to `notes/source-fidelity-check.md`.
   - At minimum, verify:
     - the thesis and scope are still the same
     - explicit question lists or purpose statements were not expanded, collapsed, or reframed without approval
     - major section order and section boundaries were preserved unless the user asked for restructure
     - existing image anchors and figure positions were preserved or replaced only with adjacent placeholders
     - no new architecture claims, rollout constraints, or compatibility judgments were introduced unless traceable to source
     - any presentation-level reorganization still preserves the same review semantics and evidence flow
   - If the check fails, stop and revise the draft. Do not continue to visual generation, deck generation, or final export.

6. Build the visual inventory.
   - For each section, decide whether it needs: no visual, cover, infographic, flowchart, framework, comparison, timeline, comic, or slide-only visual.
   - Add visuals only where they clarify structure, sequence, tradeoffs, or metrics. Do not decorate.
   - For article-writing requests handled by this pipeline, do not skip this step just because the user has not yet explicitly asked to render images. If later visuals or deck work remain plausible, the first-pass draft should already expose where visuals would go.
   - Every concrete label, metric, API name, or claim that appears in a visual must be traceable to the source draft.
   - Existing figures or image anchors should remain near their original semantic location by default. Add placeholders adjacent to them or mark them for redraw, but do not silently relocate or replace them during the writing pass.
   - If the source already contains images, screenshots, diagrams, or legacy visuals, classify each one explicitly:
     - reuse as-is
     - use as a reference image for redraw
     - extract structure only and redraw from scratch
     - keep only in `source/` and exclude from reader-facing output
   - Record that decision in the visual inventory with a short reason.
   - For visuals that are likely to be generated later, insert a first-pass placeholder into the working article near the relevant section:
     - use a Mermaid block when the structure is already clear
     - use a compact placeholder or diagram spec when the structure still needs review
   - When the article is being shown to the user for a text review pass before image generation, show the placeholder-bearing working draft rather than a placeholder-free export.
   - Use the selected theme to decide the preferred visual branch:
     - `serious-engineering` -> `baoyu-article-illustrator`, `baoyu-slide-deck`, `baoyu-cover-image`
     - `launch-narrative` -> `baoyu-slide-deck`, `baoyu-cover-image`, `baoyu-article-illustrator`
     - `lively-explainer` -> `baoyu-article-illustrator`, optional `baoyu-comic`
     - `editorial-analytic` -> `baoyu-infographic`, `baoyu-slide-deck`, `baoyu-article-illustrator`
     - `comic-teaching` -> `baoyu-comic`
   - If `notes/selection-bundle.md` already fixes the visual profile, use it as the default authority. Revisit only when the user asks to change direction or a new deliverable requires a deliberate override.
   - Save the inventory in the workspace and reference the bundle rather than creating a second independent style decision.
   - If the user has only asked to start writing, stop here after saving the backlog.

7. Materialize workspace-local baoyu config and shared visual rules.
   - Before creating any image or slide outline, read `references/visual-system.md`.
   - Also read `references/writing-mechanics.md` when the task includes ingestion, translation, formatting, or export.
   - Use Chinese in all visible content unless a proper noun or API name must stay in English.
   - Before any baoyu visual generation, pass explicit inputs from `notes/selection-bundle.md` and the target prompt or outline artifacts to `baoyu-style-bridge`.
   - The bridge may patch prompt files directly or create targeted workspace-local `.baoyu-skills/.../EXTEND.md` files, but this pipeline owns the shared bundle and decides which downstream skills need materialization.
   - If `notes/selection-bundle.md` contains an explicit style override, pass that override as the top art-direction authority when invoking the bridge.
   - Before any final image generation, run `scripts/validate-style-propagation.js --workspace <workspace-dir>` and stop if it reports failures. Use `--strict` when warnings should also block generation.
   - Prefer these baoyu defaults as structural starting points, not as final style authority:
     - `baoyu-slide-deck --style blueprint --audience experts --lang zh`
     - `baoyu-article-illustrator --style blueprint`
     - `baoyu-cover-image --style blueprint`
     - `baoyu-image-gen` when exact prompt control or reference-based redraw is needed
   - If an existing image is being kept only as a reference, preserve it under `source/` or `references/` and do not treat it as the final reader-facing visual.

8. Draft and approve diagram placeholders before rendering them.
   - For architecture diagrams, framework diagrams, request-path visuals, and flowcharts, also read `references/diagram-contract.md`.
   - First write a compact diagram spec with: purpose, source anchors, node groups, arrows, emphasis, and exclusions.
   - Also write a Mermaid block or equivalent node-edge list for logic checking.
   - Put that Mermaid block or placeholder back into the working article near the section it belongs to, or store it as a clearly linked workspace artifact if the article would become unreadable.
   - Keep that structural source as canonical through later rendering. If you later derive prompt files from it, those prompts are secondary artifacts rather than replacements for the approved structure source.
   - Review the priority visuals with the user one by one or in a small ordered batch before any image generation starts.
   - Only after the structure is correct should you translate it into an illustrator prompt or image prompt.
   - Use `framework` for architecture, modules, and principles.
   - Use `flowchart` for lifecycle, pipelines, workflows, and request paths.

9. Generate article assets.
   - Choose the downstream skill family from the selected theme before generating:
     - structural diagrams, explainers, and technical assets -> `baoyu-article-illustrator`
     - editorial or data-dense summary visuals -> `baoyu-infographic`
     - character-based sequential teaching -> `baoyu-comic`
     - exact prompt-controlled diagrams -> `baoyu-image-gen`
   - Cover image:
     - Prefer `baoyu-cover-image` after the title and metaphor are stable.
     - Use `--quick` only when the concept is already settled.
   - Inline visuals:
     - Architecture or module relations -> `baoyu-article-illustrator --preset system-design`
     - APIs, metrics, technical deep-dives -> `baoyu-article-illustrator --preset tech-explainer`
     - Workflows and execution steps -> `baoyu-article-illustrator --type flowchart --style blueprint`
     - Tradeoff tables or option comparisons -> `baoyu-article-illustrator --type comparison --style blueprint`
   - Before generation, pass workspace `prompts/cover.md`, `prompts/NN-*.md`, `prompts/infographic.md`, `storyboard.md`, or `outline.md` through `baoyu-style-bridge`.
   - When an approved visual is based on an existing image:
     - use `baoyu-article-illustrator` or `baoyu-image-gen --ref` if the source image should guide composition or structure
     - redraw from the article's labels and diagram spec if the old image is semantically useful but visually incompatible
     - keep the original image only when its style, resolution, labeling, and permissions are acceptable for the final document
   - If the saved prompt files are too generic, edit them before generation. Do not rely on vague inline prompts.
   - Keep prompt files and outlines on disk. Prefer saved prompt artifacts over one-off inline generation.
   - After the first successful render of each priority visual, stop for a short review pass. Summarize observed deviations in structure, style, and readability, then let the user decide whether to keep, regenerate, or adjust prompts. Do not blindly auto-regenerate on style drift alone.
   - When the user approves a specific image version:
     - update `notes/visual-inventory.md` with the accepted status and chosen output path
     - if multiple first-pass or revised variants exist, record which file became canonical for the article
     - replace outdated first-pass image references in the working draft before any formal export

10. Generate the deck from the stabilized article.
   - Run `baoyu-slide-deck` only after the article and key visual decisions are stable.
   - Start with `--outline-only`.
   - Before drafting or editing the outline, read `references/deck-outline-contract.md`.
   - After `outline.md` and any slide prompts are created in the workspace, pass them through `baoyu-style-bridge`.
   - The outline must include a `STYLE INSTRUCTIONS` block derived from `references/visual-system.md`, not raw baoyu preset styling.
   - Keep the deck within 20 slides.
   - Page 1 must be a cover page. Final page must be a designed ending, not a generic thanks or Q&A slide.
   - After the first image pass, review the deck visually before broad regeneration or final merge. Prefer targeted prompt fixes over regenerating the whole deck by reflex.

11. Run a consistency pass.
   - Check that article, diagrams, cover, comic, infographic, and deck share the same palette, contrast model, emphasis rules, and typographic posture where appropriate.
   - Keep visuals flat, precise, and high-contrast unless the selected theme intentionally softens them.
   - If the article is becoming a formal deliverable, verify that no workspace-facing copy remains in the final reader-facing version.
   - If the article moved from placeholder review into accepted-image integration:
     - preserve the canonical diagram source under `notes/diagram-structures.md`
     - ensure the reader-facing article keeps only the chosen image references, not the review placeholder blocks or Mermaid review aids
     - ensure any accepted v2/v3 image replaced the older first-pass reference everywhere the article points to it
   - If the article is the primary deliverable, optionally run `baoyu-format-markdown` after content is frozen. Treat it as reader-facing formatting, not as a rewrite pass.
   - If the user wants a shareable article page, optionally run `baoyu-markdown-to-html`.
   - If the article was translated, do a final language-consistency pass on text-heavy images, diagrams, covers, and screenshots. Remind the user about mismatched image language instead of silently editing those visuals.

12. Close the current pipeline pass explicitly.
   - Read `references/flow-closure.md`.
   - Save `notes/flow-closure.md` with:
     - current status: `completed`, `paused-for-review`, `paused-by-scope`, or `blocked`
     - article status
     - visual status
     - deck status
     - export status
     - what completed in this pass
     - what was deferred
     - what is waiting on the user, if anything
     - the single best next action
   - Do not treat a pass as implicitly finished just because generation stopped.
   - When replying to the user, match the language in `notes/flow-closure.md` so the workspace state and the chat summary do not drift apart.

## Baoyu Traits to Preserve

- Source-first workflow: fetch or translate first, then rewrite, then format, then publish.
- Artifact discipline: preserve raw source, analysis, prompts, outlines, and final outputs in files.
- Review gates before expensive generation: outline before slides, prompt files before images.
- Terminology consistency for long technical content: keep glossary decisions stable across article, visuals, and deck.
- Data fidelity: do not summarize away numbers, names, or source-backed claims when moving into visuals.
- Formatting and export are separate from rewriting.

## Decision Rules

- If the user says "开始写", "整理项目技术文档", "写设计方案", "写架构文档", "写技术分享", "润色技术文稿", or equivalent local-document requests, trigger this skill instead of treating the task as isolated prose editing.
- Theme selection happens before writing and before visual generation.
- When this pipeline owns the task, theme, writing posture, and visual profile should be confirmed together once as a selection bundle.
- After the selection bundle is confirmed, materialize workspace-local baoyu config early instead of waiting for the first image-generation call.
- Before presenting a pipeline-owned article back to the user for review, ensure one of these is true:
  - the working draft already contains Mermaid blocks or structured visual placeholders for the likely visuals, and the flow is paused for review
  - visuals were explicitly ruled out for this pass, and the closure note makes that scope decision explicit
- Do not jump straight from text drafting to `exports/article-final.md` while visual inventory or placeholder review is still pending.
- All end-to-end technical storytelling requests should enter this pipeline first.
- Do not force isolated capability requests such as a single image, a single cover, a single infographic, or markdown-to-html conversion through this pipeline unless the user explicitly asks for shared document coordination. For visual-only request-level orchestration, prefer `baoyu-visual-pipeline`.
- Always create or reuse a document workspace before drafting or generation.
- If the source starts as a URL, begin normalization with `baoyu-url-to-markdown`.
- If the source is non-Chinese and the user wants Chinese output, begin normalization with `baoyu-translate`.
- If the source is already a mature technical document, default to preservation mode instead of rewrite-from-scratch mode.
- If the user only wants writing polish, complete Steps 0-5 and stop there when a mature source document is involved; otherwise complete Steps 0-3.
- If the user wants to start a technical document but has not yet asked for visuals or slides, complete Steps 0-6, save the backlog in the workspace, and stop before generation.
- If a later visual is likely, the first-pass article should already contain a Mermaid block or structured placeholder for it before any image generation begins.
- Do not go straight from visual inventory to rendered images. Require per-visual placeholder review first.
- After visual review, do not leave the workflow half-finished. If the user accepts chosen image versions and asks for the overall document, integrate the accepted files into the article, preserve the diagram source separately, and then produce `exports/article-final.md`.
- Do not silently carry old screenshots or legacy diagrams into the final article. Classify them first as reuse, reference, redraw, or source-only.
- If the user wants article plus visuals but no deck, stop after Step 9.
- If the user wants a deck from an existing article, start from Steps 6, 7, and 10 using that article's workspace.
- If a section has no concrete structure, process, or numbers to explain, do not force a diagram.
- Do not overwrite user-level baoyu preferences from this skill. Persist decisions in the document workspace instead.
- Bridge skills are advisors and normalizers. This pipeline owns shared bundle persistence and routing.
- Do not adopt feed-optimized or clickbait title patterns by default. If `baoyu-format-markdown` proposes titles or summaries, keep them subordinate to the article's engineering tone.
- Do not let workspace-facing helper text leak into the formal article, exported markdown, HTML, or deck source.
- End every pass with an explicit closure note instead of assuming the user knows whether the flow is done, paused, or blocked.
- Do not silently change the meaning, scope, section contract, or figure placement of a mature source document during the first drafting pass.
- Treat semantic drift in a mature source document as a workflow failure, not a stylistic variation.

## References

- Document workspace layout: `references/document-workspace.md`
- Unified selection bundle: `references/selection-bundle.md`
- Flow closure note: `references/flow-closure.md`
- Source fidelity guard: `references/source-fidelity-check.md`
- Theme profiles: `references/theme-profiles.md`
- Writing posture bridge: `../writing-theme-bridge/SKILL.md`
- Shared visual language: `references/visual-system.md`
- Diagram spec contract: `references/diagram-contract.md`
- Slide outline contract: `references/deck-outline-contract.md`
- Writing mechanics absorbed from baoyu workflows: `references/writing-mechanics.md`
- Scripted helpers:
  - `scripts/init-workspace.js`
  - `scripts/extract-source-contract.js`
  - `scripts/check-source-fidelity.js`
  - `scripts/materialize-workspace-baoyu-config.js`
