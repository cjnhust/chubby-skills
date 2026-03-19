# Transform Traceability Contract

Read this reference for workflows that intentionally transform content, such as:
- capture -> markdown
- translate
- rewrite
- format
- export to HTML or other publish formats

The goal is not to forbid transformation. The goal is to keep each transformation traceable and reproducible.

## Core Rule

Transformation is allowed, but the workflow must preserve the source artifact and make the current derived source of truth explicit.

## Required Lineage

For multi-step flows:
- keep the raw source artifact
- write each significant transformed artifact as its own saved file
- make it clear which saved artifact is the current source of truth for the next stage

Do not rely on unsaved chat context as the only record of what changed between stages.

## When Rewriting Is Expected

Some flows are supposed to change wording or structure.

Examples:
- translation
- editorial rewriting
- reader-facing formatting
- HTML export preparation

In these flows, the important rule is not "never change the text". The important rule is:
- preserve the source
- make derived outputs explicit
- avoid silent, irreversible replacement of the earlier artifact

## In-Place Change Rule

Avoid mutating the only saved copy of a source artifact in place unless the user clearly asked for that behavior.

Prefer:
- `source.md`
- `translation.md`
- `article-draft.md`
- `article-final.md`
- `post-formatted.md`

over silently overwriting one file across multiple semantic stages.

## Review Rule

When the flow has a meaningful downstream cost, review the current derived source-of-truth artifact before the final export or expensive generation step.

Examples:
- review normalized markdown before HTML export
- review the article draft before generating visuals
- review translated copy before formatting and publishing

## Ownership

- The orchestrator decides the stage order and current source-of-truth artifact.
- Leaf skills may create derived artifacts, but should not pretend a transformation did not occur.
- If a later stage depends on an earlier transformed output, that dependency should point to a saved artifact, not to chat memory.
