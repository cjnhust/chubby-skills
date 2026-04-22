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
    annotation-plan.md
    selection-bundle.md
    diagram-structures.md
    visual-inventory.md
    flow-closure.md
  drafts/
    report.md
    report-annotated.md
  exports/
    report-final.md
  prompts/
    V01.md
  illustrations/
    V01-first-pass.png
```

## Artifact Roles

- `source/source.md`
  - `scope_status: ambiguous | confirmed`
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
  - for commentary-like sources, should also record:
    - what class of voice it is, such as `upstream-confirmation`, `implementation-operator-signal`, `technical-commentary`, `media-narrative`, or `community-signal`
    - what it is suitable to support
    - what it should not be used to prove
  - when captured from the web, should also record:
    - `capture_status: artifacted | failed | not-required`
    - raw artifact path
    - normalized markdown path
    - which one was cited for evidence extraction
  - if `capture_status: failed`, should also record a short `capture_failure` note
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
  - `overall_result` should stay `pending` until the required selective checks are complete, then move to `pass`
  - selective verification for source-available projects
  - tracks which high-impact docs claims were checked against implementation anchors
  - should use states such as `code-confirmed`, `code-suggested`, `docs-only`, `contradicted`, `not-checked`
  - should record a short mechanism summary when a checked claim is central to project differentiation
  - should capture whether the capability looks native, composed, config-driven, extension-driven, or still unclear
  - should stay narrow: verify a few adoption-critical claims, not the whole repository

- `notes/fact-check.md`
  - final factual review before export
  - `overall_result` should stay `pending` until the near-final fact-check is done, then move to `pass`
  - should mark whether key support claims are confirmed, softened, removed, or limited by code-verification findings
  - should separate source-backed facts from synthesis or inference

- `notes/annotation-plan.md`
  - required only when `report_edition: annotated`
  - maps difficult sections to explicit note types and optional annotation figures
  - should preserve the main report spine instead of inventing a second article structure

- `notes/selection-bundle.md`
  - selected theme
  - writing posture, usually `research-report`
  - visual profile
  - visual strategy, usually `auto-plan-and-review` unless the user explicitly wants text-only output
  - `report_edition`, usually `standard` unless the user explicitly wants an annotated edition
  - `annotation_mode`, usually `none` unless the report is annotated
  - `annotation_visuals`, usually `none` unless the report is annotated
  - `reader_profile`, useful when the report must add concept scaffolding for less context-rich readers
  - `text_only_evidence`, required when `visual_strategy: text-only-by-user`

- `drafts/report.md`
  - the current working draft with any placeholders or draft visuals awaiting review
  - when inserting approved or draft visuals, use report-relative markdown paths such as `../illustrations/V01-first-pass.jpg`, not absolute filesystem paths
  - for multi-source reports, should be synthesis-first and organized by research questions, decision dimensions, or operator concerns rather than by source order
  - seed-article commentary should stay in a bounded subsection, not become the whole report skeleton
  - should follow the section spine defined in `notes/report-thesis.md`
  - in `standard` mode, does not need explanatory annotation blocks, but should still expose lightweight source visibility when strong cross-source judgments are made
  - in research-report mode, section headings should usually name a decision dimension, object role, risk, or operator concern rather than state the conclusion as a slogan-like contrast

- `drafts/report-annotated.md`
  - optional annotated-edition working draft
  - should preserve the same report thesis and section spine as `drafts/report.md`
  - should expose reader aids as explicit note blocks rather than silently merging all support into prose
  - if this file exists and `report_edition: annotated`, it becomes the preferred review artifact and default finalization source
  - this file is for explanatory notes and concept scaffolding, not merely for adding ordinary source citations

- `notes/diagram-structures.md`
  - canonical Mermaid or node-edge source for approved diagrams
  - must also capture the reasoning for each visual, not just the structure
  - for each visual, should record:
    - `research_question_answered`
    - `why_visual_not_prose`
    - `source_anchors`
    - `selection_logic`
    - `exclusions`
    - `approval_status`
  - preserve this even if the final report later swaps them for rendered images
  - for rendered visuals, treat this as structure source; the actual image should still come from a leaf visual skill unless the user explicitly asks for direct Mermaid export

- `notes/visual-inventory.md`
  - planned figures after the report skeleton is accepted
  - should record top-level planning fields before any downstream visual rendering begins:
    - `planning_status: pending | confirmed`
    - `image_count`
    - `count_decision_source: user | planner`
    - `count_rationale`
  - if the user did not specify image count, the planner should still make and record an explicit count decision before downstream rendering starts
  - a one-image plan should explain why one figure is sufficient for the report instead of silently assuming that a single architecture diagram is enough
  - should give each planned visual a deterministic placement key such as `draft_anchor_heading`
  - should record `render_via` so the rendered path stays attached to a leaf visual skill instead of drifting into an ad hoc renderer
  - should record `rendered_path` for every approved rendered visual
  - should record `prompt_artifacts` for every rendered visual so provenance does not disappear after export
  - should record `approval_source: user` before any draft state is promoted to `approved-*`
  - should also record why the visual exists, at minimum:
    - `research_question`
    - `selection_logic`
    - `exclusions`
  - should eventually record whether each visual becomes:
    - `draft-placeholder`
    - `draft-inline-mermaid`
    - `draft-rendered`
    - `approved-inline-mermaid`
    - `approved-rendered`
    - `skipped`
  - `draft-*` means prepared and inserted into the working draft, but still waiting for user confirmation
  - only `approved-*` or `skipped` states are final-export eligible
  - `approved-rendered` is reserved for leaf-skill image output that the user explicitly accepted; local SVG / Mermaid drafts are not interchangeable with this state
  - for project-specific reports, should usually contain a small explanatory set rather than only one architecture figure

- `notes/flow-closure.md`
  - current pass status and best next action

- `exports/report-final.md`
  - cleaned reader-facing final report
  - should not contain pipeline-internal notes or unresolved placeholder scaffolding
  - image links should remain relative to the report file so local markdown preview works outside the current machine path
  - for multi-source work, should read as one integrated document with a neutral descriptive title rather than inheriting a seed article's headline or rhetorical tone
  - when the report makes cross-source or recommendation-driving judgments, should retain a lightweight evidence trail in the reader-facing text even in `standard` mode

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
- If more than one plausible object matches the topic, record `scope_status: ambiguous` plus the candidate interpretations and stop before thesis-writing or drafting.

## Capture Rule

- Reuse `baoyu-url-to-markdown` for direct webpage capture.
- Reuse `baoyu-content-pipeline` only when the report source also needs staged translation or normalization before research synthesis.
- For any concrete URL that materially affects the report, content-family capture is the default evidence path and should be treated as mandatory unless the capture flow fails and that failure is recorded.
- The research pipeline should consume those source artifacts; it should not own a separate browser-capture implementation.

## Export Rule

- `drafts/report.md` is intermediate.
- `drafts/report-annotated.md` is also intermediate when annotated mode is enabled.
- Final delivery should be exported to `exports/report-final.md`.
- An existing `exports/report-final.md` from an older run does not by itself authorize an immediate answer. Refresh the current-pass source and notes artifacts before treating the workspace as complete.
- For multi-source work, final delivery should be a synthesis-first report, not a stitched set of source summaries.
- Final export should happen only after `notes/report-thesis.md` exists and the report body clearly follows it.
- If diagrams are part of the explanation, the final export should include either approved Mermaid diagrams or accepted rendered visuals.
- Keep operator-facing reasoning in `source/` and `notes/`, not in the final report body.
- For source-available projects, the final report should not flatten all key project claims into docs-only prose when selective code verification materially changed the confidence level.
- For source-available projects, the final report should usually explain at least one implementation-level reading for the most important differentiating claim, if that claim materially influences adoption.
- For open-source or source-available project reports, final export should happen only after `notes/code-verification.md` is in a passing state.
- Final export should happen only after `notes/fact-check.md` has been updated from `pending` to a passing state.
- Final export should happen only after `notes/visual-inventory.md` records a confirmed visual plan with explicit `image_count`, `count_decision_source`, and `count_rationale` whenever the run is not text-only-by-user.
- Final export should happen only after every planned visual in `notes/visual-inventory.md` is either `approved-inline-mermaid`, `approved-rendered`, or `skipped`.
- Final export should happen only after every `approved-rendered` item also records `render_via`, `rendered_path`, `prompt_artifacts`, and `approval_source: user`.
- If `notes/selection-bundle.md` keeps `visual_strategy: auto-plan-and-review`, final export should not close with every planned visual marked `skipped`; either at least one visual must be approved or the bundle must be changed to `text-only-by-user`.
- If `notes/selection-bundle.md` uses `visual_strategy: text-only-by-user`, it must also contain a non-null `text_only_evidence` entry showing the user's explicit text-only request. Silence about visuals is not sufficient.
- If visuals are already inserted into `drafts/report.md` but still waiting for confirmation, keep the pass in a review state rather than producing `exports/report-final.md`.
- If this turn introduced the first unapproved visual artifact for the pass, do not also produce `exports/report-final.md` in the same turn. The pass must stop for user review first, even when the visual is only a Mermaid block.
- If `report_edition: annotated`, final export should be based on `drafts/report-annotated.md` unless the bundle is explicitly changed back to `standard`.
- Only a successful `scripts/finalize-report.js --workspace <dir>` run should create or refresh `exports/report-final.md` and the completed/exported closure state.
