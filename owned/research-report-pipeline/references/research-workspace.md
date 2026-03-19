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
    report-thesis.md
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
  - whether the source is a `seed`, `baseline`, `mechanism-evidence`, `case-study`, `counterexample`, or `supporting` input to the final judgment
  - whether it is primary or supporting
  - when captured from the web, should also record:
    - raw artifact path
    - normalized markdown path
    - which one was cited for evidence extraction
  - if a URL source could not be captured through the content-family leaf, should record the failure mode explicitly instead of silently substituting search snippets

- `notes/research-questions.md`
  - the concrete questions the report must answer
  - open questions or missing evidence

- `notes/evidence-matrix.md`
  - dimensions such as definition, SOP, scenario fit, pitfalls, costs, recommendation
  - source-backed findings for each dimension
  - where helpful, separate `source claim`, `cross-source check`, and `report judgment`
  - explicit gaps or weak evidence

- `notes/report-thesis.md`
  - required before real drafting begins
  - should lock:
    - `report_mode`
    - `target_reader`
    - `core_question`
    - `single_sentence_thesis`
    - `section_spine`
    - `source_integration_plan`
    - `non_goals`
  - should explain what each major source is doing in the final judgment, especially when one source is rhetorical and others are mechanism evidence

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
  - visual strategy, usually `auto-plan-and-review` unless the user explicitly wants text-only output
  - `text_only_evidence`, required when `visual_strategy: text-only-by-user`

- `drafts/report.md`
  - the current working draft with any placeholders or draft visuals awaiting review
  - when inserting approved or draft visuals, use report-relative markdown paths such as `../illustrations/V01-first-pass.jpg`, not absolute filesystem paths
  - for multi-source reports, should be synthesis-first and organized by research questions, decision dimensions, or operator concerns rather than by source order
  - seed-article commentary should stay in a bounded subsection, not become the whole report skeleton
  - should follow the section spine defined in `notes/report-thesis.md`

- `notes/diagram-structures.md`
  - canonical Mermaid or node-edge source for approved diagrams
  - preserve this even if the final report later swaps them for rendered images
  - for rendered visuals, treat this as structure source; the actual image should still come from a leaf visual skill unless the user explicitly asks for direct Mermaid export

- `notes/visual-inventory.md`
  - planned figures after the report skeleton is accepted
  - should give each planned visual a deterministic placement key such as `draft_anchor_heading`
  - should record `render_via` so the rendered path stays attached to a leaf visual skill instead of drifting into an ad hoc renderer
  - should eventually record whether each visual becomes:
    - `draft-placeholder`
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
  - image links should remain relative to the report file so local markdown preview works outside the current machine path
  - for multi-source work, should read as one integrated document with a neutral descriptive title rather than inheriting a seed article's headline or rhetorical tone

- `prompts/`
  - one prompt file per rendered visual when image generation is used
  - for diagrams, prompts should usually be derived from `notes/diagram-structures.md`, not invented separately
  - prompt materialization should preserve the intended leaf visual skill from `notes/visual-inventory.md`

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
- For any concrete URL that materially affects the report, content-family capture is the default evidence path and should be treated as mandatory unless the capture flow fails and that failure is recorded.
- The research pipeline should consume those source artifacts; it should not own a separate browser-capture implementation.

## Export Rule

- `drafts/report.md` is intermediate.
- Final delivery should be exported to `exports/report-final.md`.
- For multi-source work, final delivery should be a synthesis-first report, not a stitched set of source summaries.
- Final export should happen only after `notes/report-thesis.md` exists and the report body clearly follows it.
- If diagrams are part of the explanation, the final export should include either approved Mermaid diagrams or accepted rendered visuals.
- Keep operator-facing reasoning in `source/` and `notes/`, not in the final report body.
- For source-available projects, the final report should not flatten all key project claims into docs-only prose when selective code verification materially changed the confidence level.
- For source-available projects, the final report should usually explain at least one implementation-level reading for the most important differentiating claim, if that claim materially influences adoption.
- For open-source or source-available project reports, final export should happen only after `notes/code-verification.md` is in a passing state.
- Final export should happen only after `notes/fact-check.md` has been updated from `pending` to a passing state.
- Final export should happen only after every planned visual in `notes/visual-inventory.md` is either `approved-inline-mermaid`, `approved-rendered`, or `skipped`.
- If `notes/selection-bundle.md` keeps `visual_strategy: auto-plan-and-review`, final export should not close with every planned visual marked `skipped`; either at least one visual must be approved or the bundle must be changed to `text-only-by-user`.
- If `notes/selection-bundle.md` uses `visual_strategy: text-only-by-user`, it must also contain a non-null `text_only_evidence` entry showing the user's explicit text-only request. Silence about visuals is not sufficient.
- If visuals are already inserted into `drafts/report.md` but still waiting for confirmation, keep the pass in a review state rather than producing `exports/report-final.md`.
