# Visual Source Preservation Contract

Read this reference for visual-generation workflows when the user provides any primary visual intent such as:
- a raw image prompt
- a detailed visual description
- a Mermaid block
- a diagram spec
- a list of labels that must stay verbatim
- exclusions or "must not show" constraints
- reference images with explicit redraw intent

The goal is to prevent silent replacement of the user's visual source with an opaque derived prompt.

## Core Rule

The user-provided visual source is the canonical semantic input for the run.

Derived prompt files, normalized task narratives, or style-patched prompt artifacts may be added, but they must not silently replace the canonical source.

## What Must Be Preserved

Persist the raw source in a saved artifact whenever the flow is more than a one-shot inline render.

Examples:
- save the exact raw prompt text
- save the Mermaid block verbatim
- save the diagram spec verbatim
- save the user-provided label and exclusion list verbatim

## What Derived Artifacts May Do

Derived artifacts may:
- separate style rules from task content
- add rendering posture, palette, typography, and composition guidance
- reorganize the request for one specific downstream skill
- map the same structure into another deliverable's native format

Derived artifacts must not:
- drop semantic constraints without making that visible
- compress the user's structure into a smaller prose summary and treat that as the only source
- add semantic negations the user did not ask for, such as forbidding Mermaid syntax or removing a requested module
- replace exact labels or node relationships unless the user approved that change

## Final Render Rule

Before final rendering, at least one of these must be true:

1. the final prompt artifact contains the canonical user source verbatim
2. the final prompt artifact explicitly references the saved canonical source artifact and preserves its semantics

If a workflow needs a derived prompt narrative for the renderer, keep that narrative as a secondary artifact rather than the only surviving representation of the request.

## Mermaid And Diagram Rule

For Mermaid, node-edge lists, and diagram specs:
- keep the original structural source as a saved artifact
- treat it as the canonical structure source through review and rendering
- if you later create a prose prompt for a renderer, label that prose as derived from the canonical structure source
- do not silently convert the structure source into prose-only form and discard the original

## Review Rule

If the renderer output diverges, compare it against the canonical source first, not only against a derived prompt summary.

## Ownership

- The orchestrator decides where canonical and derived artifacts live.
- A bridge may patch style or target-format details, but it does not own the right to replace the canonical user source.
- A leaf renderer may consume derived prompt files, but the workflow should preserve the canonical source artifact whenever the request is non-trivial.
