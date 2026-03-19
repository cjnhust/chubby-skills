---
name: baoyu-content-pipeline
description: Orchestrate non-trivial content ingestion and transformation requests by routing between webpage capture, X capture, translation, markdown cleanup, and HTML export while persisting intermediate artifacts and reviewing the normalized content before final export. Use when the user wants a multi-step flow such as save a page then translate it, translate and format a document, convert captured content into publish-ready markdown, or produce HTML from a staged markdown artifact rather than running a single leaf conversion in isolation.
---

# Baoyu Content Pipeline

Use this skill as the request-level orchestration layer for content ingestion, transformation, and export tasks.

Also read [../../owned/shared/references/family-orchestration-contract.md](../../owned/shared/references/family-orchestration-contract.md).
Also read [../../owned/shared/references/extend-ownership-contract.md](../../owned/shared/references/extend-ownership-contract.md).
Also read [../../owned/shared/references/transform-traceability-contract.md](../../owned/shared/references/transform-traceability-contract.md).

It is the family pipeline for the content-transformation family and owns sequencing for the current request:
- choosing the correct ingest or conversion branch
- establishing a working location when intermediate artifacts are needed
- deciding which saved artifact becomes the current source of truth
- deciding when request-scoped preferences stay explicit versus become request-local defaults
- routing between capture, translation, formatting, and export steps
- stopping to review the normalized content before final export or broad rewrite

It does not own article/deck narrative planning or document-level visual coordination. Those remain with `engineering-story-pipeline`.

## Entry Rules

Use this skill when the request includes one or more of these:

- fetch a URL or X post and then continue with additional processing
- translation plus formatting or export
- markdown cleanup before HTML export
- a staged publish flow where markdown should become the source of truth before export
- any request with reusable intermediate artifacts such as snapshots, translated markdown, formatted markdown, or HTML output

Do not use this skill for a true one-shot leaf action such as:
- save one webpage as markdown and stop
- translate one file directly and stop
- format one markdown file directly and stop
- convert one finalized markdown file to HTML and stop

If the request grows into technical article drafting, story structure, diagram planning, or deck coordination, hand off to `engineering-story-pipeline`.

## Working Artifact Contract

If the run creates intermediate artifacts, also read [../../owned/shared/references/working-artifact-contract.md](../../owned/shared/references/working-artifact-contract.md).

When this skill is the request-level orchestrator:
- it owns the root working location for the current content run
- it decides which artifacts must have stable cross-skill paths
- downstream leaf skills may choose their own internal layout under that working location

## Routing

Choose the target branch before running leaves:

- webpage capture -> `baoyu-url-to-markdown`
- X capture -> `baoyu-danger-x-to-markdown`
- translation -> `baoyu-translate`
- markdown cleanup/reader-facing normalization -> `baoyu-format-markdown`
- HTML export -> `baoyu-markdown-to-html`

Prefer the narrowest branch that satisfies the current stage, but keep one explicit saved markdown artifact as the source of truth between stages.

## Workflow

1. Normalize the request into explicit inputs.
   - Save the source URL, source file, target language, formatting intent, export target, and any user constraints.
   - If the flow is multi-step, persist those inputs in the working location instead of relying on chat memory.

2. Capture or materialize the source.
   - If the source is remote, run the appropriate capture leaf first.
   - Persist the captured markdown or source snapshot as the initial source artifact for the run.
   - Preserve that source artifact even when later stages translate, rewrite, format, or export derived versions.

3. Transform the content in stages.
   - Translate before formatting when both are requested.
   - Format reader-facing markdown before HTML export when layout cleanup is part of the request.
   - After each stage, update which saved markdown artifact is the current source of truth.
   - Keep current-run values such as one-off theme or terminology overrides explicit unless multiple downstream steps truly need a request-local saved default.
   - Prefer new saved derived artifacts for semantic stage changes over silently overwriting the only saved copy of the previous stage.

4. Review the normalized markdown before final export.
   - After capture/translation/formatting produces a candidate source-of-truth markdown, summarize visible issues in structure, terminology, readability, link handling, and publish readiness.
   - Let the user decide whether to keep it, refine it, or continue to export.
   - Prefer fixing the saved markdown artifact before regenerating downstream outputs.

5. Export only after the source artifact is accepted.
   - Invoke `baoyu-markdown-to-html` or other final leaf outputs only after the staged markdown is acceptable for export.

6. Finish or hand off.
   - If the user accepts the result, stop.
   - If the user wants another pass, keep the saved markdown artifact as the source of truth and rerun the necessary downstream stages.
   - If the work becomes a larger writing/storytelling task, move it to `engineering-story-pipeline`.

## Boundary Rules

- `baoyu-url-to-markdown`, `baoyu-danger-x-to-markdown`, `baoyu-translate`, `baoyu-format-markdown`, and `baoyu-markdown-to-html` are leaf capabilities in this family.
- Do not make those leaves own multi-step sequencing for capture -> translate -> format -> export.
- Review the normalized markdown artifact before final export when the request is multi-step.
