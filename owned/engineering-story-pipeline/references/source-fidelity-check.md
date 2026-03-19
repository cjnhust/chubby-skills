# Source Fidelity Check

Use this reference when the source already begins as a mature, sectioned technical document and the pipeline is doing a bounded editorial pass rather than a rewrite-from-scratch pass.

## Goal

Ensure the first draft still says the same thing as the source before the workflow continues to visuals, deck generation, or final export.

This check is about preserving the source document's semantic contract, not about forcing identical formatting.

## Required Artifacts

- `notes/source-contract.md`
- `drafts/article.md`
- `notes/source-fidelity-check.md`

## What the Source Contract Must Capture

- original title
- stated document purpose or positioning
- explicit question list, goal list, or non-goal list
- top-level section map
- major second-level section map when it defines review boundaries
- existing image anchors, figure positions, and diagram positions
- must-keep constraints or judgments

## Check Dimensions

The fidelity check should answer each item explicitly.

1. Thesis and scope
   - Does the draft still argue the same main point?
   - Did the rewrite introduce a broader or narrower mission than the source?

2. Problem framing
   - Did explicit question lists, problem statements, or purpose statements keep the same count and meaning?
   - Were new framing questions, new success criteria, or new decision axes introduced without source support?

3. Section contract
   - Were top-level sections preserved?
   - Were major sections merged, split, reordered, or renamed in a way that changes review boundaries?

4. Evidence and claim traceability
   - Are new claims traceable to the source?
   - Were old claims silently dropped or softened?

5. Figures and image anchors
   - Do existing images still appear at the same semantic spot?
   - If replaced by Mermaid or placeholders, are those placeholders adjacent to the original anchor rather than moved to a new narrative position?

## Allowed Deltas

These changes are acceptable when they do not alter the semantic contract:

- normalize title or heading wording without changing what the section is about
- add numbering to headings
- convert prose to lists or tables
- split one section into tighter local subsections, or merge adjacent micro-sections, as long as the same review boundary is preserved
- rewrite sentences for clarity, concision, or tone
- add Mermaid or visual placeholders adjacent to an existing image slot or section that already carries the same evidence role

## Not Allowed Without Approval

These count as semantic drift unless the user explicitly asked for them:

- changing the document's main thesis or scope
- changing explicit question counts, goal counts, or non-goal counts
- replacing an evidence-bearing image section with a different narrative device in a new location
- merging independent review sections such as compatibility, rollout, and rollback into one section when the source treated them separately
- introducing new architecture judgments, rollout logic, or compatibility claims that are not traceable to source

## Failure Conditions

The check fails if any of the following is true:

- the main thesis or scope changed
- explicit question counts changed without approval
- section boundaries changed without approval
- existing image anchors were replaced or moved without approval
- new architecture judgments or rollout conclusions were introduced without source backing
- the draft is still technically polished but no longer review-equivalent to the source

## Expected Outcome

`notes/source-fidelity-check.md` should end with one of:

- `pass`
- `pass with noted deltas`
- `fail`

If the result is `fail`, the pipeline must stop and revise the draft before continuing.
