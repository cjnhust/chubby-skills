# Research Workspace

Use one workspace per research report.

## Canonical Structure

```text
<workspace>/
  source/
    raw/
      <slug>-captured.html
    normalized/
      <slug>.md
    source.md
    source-catalog.md
  notes/
    research-questions.md
    evidence-matrix.md
    code-verification.md
    fact-check.md
    selection-bundle.md
    diagram-structures.md
    visual-inventory.md
    flow-closure.md
  drafts/
    report.md
  exports/
    report-final.md
  prompts/
    V01.md
  illustrations/
    V01-first-pass.png
```

## Artifact Roles

- `source/source.md`
  - confirmed research object
  - scope boundary
  - user goal
  - what is explicitly out of scope
  - whether the object is `open-source`, `source-available`, or `docs-only`
  - whether code verification is required for finalization

- `source/source-catalog.md`
  - source title
  - URL
  - source type
  - why it matters
  - whether it is primary or supporting
  - when captured from the web, should also record:
    - raw artifact path
    - normalized markdown path
    - which one was cited for evidence extraction

- `notes/research-questions.md`
  - the concrete questions the report must answer
  - open questions or missing evidence

- `notes/evidence-matrix.md`
  - dimensions such as definition, SOP, scenario fit, pitfalls, costs, recommendation
  - source-backed findings for each dimension
  - explicit gaps or weak evidence

- `notes/code-verification.md`
  - required for open-source or source-available project reports
  - selective verification for source-available projects
  - tracks which high-impact docs claims were checked against implementation anchors
  - should use states such as `code-confirmed`, `code-suggested`, `docs-only`, `contradicted`, `not-checked`
  - should record a short mechanism summary when a checked claim is central to project differentiation
  - should capture whether the capability looks native, composed, config-driven, extension-driven, or still unclear
  - should stay narrow: verify a few adoption-critical claims, not the whole repository

- `notes/fact-check.md`
  - final factual review before export
  - should mark whether key support claims are confirmed, softened, removed, or limited by code-verification findings
  - should separate source-backed facts from synthesis or inference

- `notes/selection-bundle.md`
  - selected theme
  - writing posture, usually `research-report`
  - visual profile

- `drafts/report.md`
  - the current working draft with any placeholders or draft visuals awaiting review

- `notes/diagram-structures.md`
  - canonical Mermaid or node-edge source for approved diagrams
  - preserve this even if the final report later swaps them for rendered images

- `notes/visual-inventory.md`
  - planned figures after the report skeleton is accepted
  - should eventually record whether each visual becomes:
    - `draft-inline-mermaid`
    - `draft-rendered`
    - `approved-inline-mermaid`
    - `approved-rendered`
    - `skipped`
  - `draft-*` means prepared and inserted into the working draft, but still waiting for user confirmation
  - only `approved-*` or `skipped` states are final-export eligible
  - for project-specific reports, should usually contain a small explanatory set rather than only one architecture figure

- `notes/flow-closure.md`
  - current pass status and best next action

- `exports/report-final.md`
  - cleaned reader-facing final report
  - should not contain pipeline-internal notes or unresolved placeholder scaffolding

- `prompts/`
  - one prompt file per rendered visual when image generation is used

- `illustrations/`
  - first-pass and accepted rendered outputs

- `source/raw/`
  - rendered page captures or other source snapshots produced by leaf capture skills
  - prefer to preserve the original browser-materialized capture when the source came from a live webpage

- `source/normalized/`
  - markdown or cleaned derivatives used as the evidence-bearing source for synthesis
  - if a content-family leaf produced both raw and normalized artifacts, keep both instead of overwriting one with the other

## Scope Rule

- If the request names a project, product, library, or framework, write that exact scope into `source/source.md`.
- If broader comparison would materially change the report, confirm with the user before collecting broader sources.

## Capture Rule

- Reuse `baoyu-url-to-markdown` for direct webpage capture.
- Reuse `baoyu-content-pipeline` only when the report source also needs staged translation or normalization before research synthesis.
- The research pipeline should consume those source artifacts; it should not own a separate browser-capture implementation.

## Export Rule

- `drafts/report.md` is intermediate.
- Final delivery should be exported to `exports/report-final.md`.
- If diagrams are part of the explanation, the final export should include either approved Mermaid diagrams or accepted rendered visuals.
- Keep operator-facing reasoning in `source/` and `notes/`, not in the final report body.
- For source-available projects, the final report should not flatten all key project claims into docs-only prose when selective code verification materially changed the confidence level.
- For source-available projects, the final report should usually explain at least one implementation-level reading for the most important differentiating claim, if that claim materially influences adoption.
- For open-source or source-available project reports, final export should happen only after `notes/code-verification.md` is in a passing state.
- Final export should happen only after `notes/fact-check.md` has been updated from `pending` to a passing state.
- Final export should happen only after every planned visual in `notes/visual-inventory.md` is either `approved-inline-mermaid`, `approved-rendered`, or `skipped`.
- If visuals are already inserted into `drafts/report.md` but still waiting for confirmation, keep the pass in a review state rather than producing `exports/report-final.md`.
