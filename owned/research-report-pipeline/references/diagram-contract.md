# Research Diagram Contract

Use this contract before generating any report diagram, Mermaid block, placeholder, or rendered visual in `research-report-pipeline`.

The point is not only to validate layout. The point is to validate whether the visual deserves to exist at all, what research question it answers, and why it is the right visual for that section.

Also read `../../shared/references/visual-source-preservation-contract.md`.

## Core Rule

In research mode, a visual is justified only when it compresses a reader-facing judgment that is harder to hold in prose alone.

Do not create visuals just because the report is long, because the object has an architecture, or because “a diagram would look nice”.

Every planned visual must answer all four of these questions:

1. What reader question does this visual answer?
2. Why is that question important to the report's judgment or recommendation?
3. Why is a visual the right form instead of one paragraph or one table?
4. What should the visual explicitly leave out so it does not blur the argument?

If you cannot answer these cleanly, do not plan the visual yet.

## Mandatory Confirmation Rule

If `visual_strategy: auto-plan-and-review`, every visual still requires explicit user confirmation.

This includes:

- a single Mermaid diagram
- a “simple” framework diagram
- a visual that feels obvious from the text
- a visual that only restates one section heading

“Simple”, “low-risk”, “obvious”, or “already implied by the draft” do not count as approval.

Once a draft placeholder, draft Mermaid, or draft rendered image has been inserted into `drafts/report.md`, the pass must stop in a review state until the user confirms, skips, or asks for revision.

Do not export `exports/report-final.md` in the same turn that the first unapproved visual is introduced.

## Required Output Per Visual

Produce two artifacts per planned visual:

1. A compact diagram spec in `notes/diagram-structures.md`
2. A planning entry in `notes/visual-inventory.md`

The spec must capture the reasoning for the visual, not only the nodes.

## Diagram Spec Template

```md
## V01 <short title>

- title:
- purpose:
- research_question_answered:
- why_visual_not_prose:
- source_anchors:
- diagram_type: framework | flowchart | comparison | infographic
- reading_direction: left-to-right | top-to-bottom
- primary_focus:
- selection_logic:
  - why this visual is included
  - why it appears in this section
  - why it is not merged into another visual
- node_groups:
  - group:
    - node:
    - node:
- connectors:
  - A -> B: reason / payload / relation
- exclusions:
  - what is intentionally omitted
- approval_status: draft | approved | skipped
```

Add a Mermaid block or equivalent node-edge list after the spec when the structure is ready enough for review.

## Inventory Requirements

Each entry in `notes/visual-inventory.md` should include at minimum:

- `draft_anchor_heading`
- `purpose`
- `source_anchor`
- `render_via`
- `status`
- `research_question`
- `selection_logic`
- `exclusions`

The inventory is the “why this visual exists” log.
The diagram spec is the “what this visual contains” log.

Do not collapse those into one vague sentence.

## Mapping Rules

- Use `framework` when the reader needs a stable mental model of layers, modules, surfaces, or ownership boundaries.
- Use `flowchart` when the report needs to explain a SOP, evaluation path, adoption sequence, or lifecycle.
- Use `comparison` when the report's judgment depends on contrasting options, fit boundaries, or tradeoffs.
- Use `infographic` only when the main compression target is a dense capability, metric, or scenario matrix.

## Simplification Rules

- One visual should usually answer one main reader question.
- If one visual tries to explain object definition, SOP, and fit boundary at once, split it.
- Merge incidental helpers into grouped nodes if they do not change the recommendation.
- Prefer one main path plus at most two side branches.
- If a visual becomes too dense, split it before rendering; do not shrink it into unreadability.

## Research Integrity Rules

- Anchor every node and connector to evidence already present in `source/` or `notes/`.
- Do not introduce causal arrows that the sources do not support.
- Do not use visuals to smuggle in stronger certainty than the text can defend.
- If the report judgment is only docs-level, the visual must not imply code-confirmed mechanism detail.
- If a visual contains synthesis, make that synthesis explicit in the surrounding text and in the spec.

## Review Rule

Review the visual with the user in one of these forms:

1. placeholder
2. Mermaid
3. first-pass rendered image

Only after the user confirms may the status move from:

- `draft-placeholder` -> `approved-inline-mermaid` or `approved-rendered`
- `draft-inline-mermaid` -> `approved-inline-mermaid`
- `draft-rendered` -> `approved-rendered`

Do not self-upgrade a draft status.

## Final Integration Rule

When the user has confirmed the visual:

- keep the accepted structure source in `notes/diagram-structures.md`
- record the accepted state in `notes/visual-inventory.md`
- place the approved visual near the same reviewed section anchor
- remove review-only placeholder text from the reader-facing final export
