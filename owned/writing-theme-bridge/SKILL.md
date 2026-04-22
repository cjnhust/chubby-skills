---
name: writing-theme-bridge
description: Read or recommend a writing posture from article content, user context, and an optional selected theme, then route drafting through the appropriate writing behavior. Use when technical writing should adapt to different themes such as serious engineering, RFC documents, research reports, practice sharing, launch narrative, lively explainer, editorial analytic, or comic teaching, while keeping one factual source of truth. This skill may be called by an orchestration skill, but it does not own workspace planning, shared bundle persistence, or downstream routing.
---

# Writing Theme Bridge

Use this skill before drafting whenever the article's content should determine not only visuals, but also the writing posture itself.

Also read [../shared/references/family-orchestration-contract.md](../shared/references/family-orchestration-contract.md).

## Purpose

This skill is the bridge layer for the technical-story writing family. It does not replace `engineering-practice-writer` and it does not orchestrate document flow. It decides which writing posture the current article needs, or reads an already confirmed posture from an explicit input artifact, and then routes drafting through the right writing behavior. Shared bundle persistence and workspace sequencing belong to orchestration skills such as `engineering-story-pipeline`.

If this bridge will persist artifacts for a multi-step flow, also read [../shared/references/working-artifact-contract.md](../shared/references/working-artifact-contract.md). The caller owns the root working location; this skill decides only which posture artifacts to read, patch, or create.

## Workflow

1. Read explicit inputs first.
   - Prefer the source material, article intent, user style request, and any caller-provided theme or posture note.
   - If the caller provides `notes/selection-bundle.md` or another saved posture artifact, treat it as input state, not as state owned by this skill.
   - Determine:
     - rigor level
     - explanatory vs argumentative balance
     - whether the piece teaches, argues, launches, analyzes, or dramatizes
     - whether the article should feel restrained, spec-like, practice-led, staged, teacherly, editorial, or scene-based
     - whether dense concepts need local explanation at the point of use
     - whether the user wants adjacent best practices, pitfalls, or misconceptions added around key sections

2. Recommend a writing posture.
   - Read `references/writing-postures.md`.
   - If a caller-provided artifact already contains a confirmed writing posture, treat it as authoritative unless the user explicitly asks to revisit it.
   - If the caller already selected a theme, use that theme as the primary signal.
   - Produce:
     - one recommended posture
     - one recommended reader-support mode
     - one recommendation for whether the source should stay as preserved structure plus annotations
     - two or three alternatives
     - one-sentence rationale for each
   - When this skill runs standalone, ask the user to confirm unless the user has explicitly locked the posture or theme.
   - When this skill runs under an orchestration skill, return the recommendation to the caller or patch only the caller-specified artifact. Do not create or mutate `notes/selection-bundle.md` on your own.
   - Save the result to `notes/writing-selection.md` only when this bridge is used standalone, the user explicitly asks to persist the decision, or an audit trail is useful.

3. Route drafting.
   - `serious-engineering` -> use `engineering-practice-writer` directly.
   - `rfc-document` -> use `engineering-practice-writer` as the base engine, then apply the RFC / technical document constraints from `references/writing-postures.md`.
   - `research-report` -> use `engineering-practice-writer` as the base engine, then strengthen scope declaration, evidence boundaries, findings snapshot, first-pass SOP, fit / unfit analysis, constraints, and bounded recommendation.
   - `practice-sharing` -> use `engineering-practice-writer` as the base engine, then apply the practice-sharing constraints from `references/writing-postures.md`.
   - `launch-narrative` -> use `engineering-practice-writer` as the base engine, then apply the launch posture constraints from `references/writing-postures.md`.
   - `lively-explainer` -> use `engineering-practice-writer` as the base engine, then make the article more teacherly and cognitively lighter.
   - `editorial-analytic` -> use `engineering-practice-writer` as the base engine, then strengthen analysis framing and evidence-commentary balance.
   - `comic-teaching` -> use `engineering-practice-writer` as the base engine, then restructure into scene-ready, beat-sized teaching units.
   - If the piece is still fundamentally `serious-engineering`, `practice-sharing`, or `research-report` but some sections contain concept jumps, prefer inline reader aids over switching the whole draft to `lively-explainer`.
   - Recommended reader-support modes:
     - `minimal` -> keep definitions terse and only clarify blocking terms.
     - `inline-expanded` -> insert short background, concept clarification, and best-practice paragraphs near the first relevant section.
     - `section-expanded` -> allow short dedicated subsections for concepts that would otherwise overload the main section.
   - If the user wants the source to behave like an annotated edition rather than a rewrite, preserve the original chapter order and insert explicit labeled callouts for added explanations.

4. Preserve writing boundaries.
   - Do not invent facts, metrics, results, or historical context.
   - Keep one source-of-truth draft for downstream diagram, cover, comic, infographic, and deck work.
   - Formatting remains a later step. This skill only selects and applies writing posture.
   - Shared bundle persistence and workspace sequencing remain the caller's responsibility.

## Bridge Rules

- Theme selection and writing posture are related but not identical. Usually the theme implies the default posture, but explicit user preference can override it.
- Under the `serious-engineering` theme, prefer `rfc-document` when the source is an RFC, architecture proposal, or review-oriented technical document with explicit scope and migration concerns.
- Under the `serious-engineering` theme, prefer `research-report` when the source is an evidence-led evaluation whose main job is to help the reader understand, assess, try, or adopt a technology under an explicit source boundary.
- Under the `serious-engineering` theme, prefer `practice-sharing` instead of plain `serious-engineering` when the source is a personal or team practice retrospective, a technical blog, a technical sharing draft, or an evolution story centered on one concrete workflow or system object.
- Under the `editorial-analytic` theme, prefer `research-report` when the output should behave like a bounded evaluation memo with explicit evidence scope, first-pass validation guidance, fit boundaries, and recommendation rather than open-ended commentary.
- For concept-dense sharing drafts, do not switch to `lively-explainer` unless the user wants the entire document to become tutorial-like. Keep the stronger posture and add reader aids locally.
- If the user explicitly wants something closer to an annotation system, preserve headings, section order, and figure anchors first, then add reader aids as visibly marked additions.
- If a caller-provided posture artifact or shared bundle already exists, reuse it before asking the user again.
- `engineering-practice-writer` remains the default writer for serious engineering prose and the base engine for other postures.
- If the user gives a strong reference article, merge its style cues with the chosen posture instead of replacing the posture entirely.
- Writing posture should be selected mainly from article content and communication intent, not from output format alone.
- This skill consumes explicit inputs and returns explicit posture decisions. It does not own workspace creation, shared bundle mutation, or multi-step pipeline sequencing.

## References

- Writing postures: `references/writing-postures.md`
- Theme-to-posture mapping: `references/theme-mapping.md`
