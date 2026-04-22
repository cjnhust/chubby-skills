# Selection Bundle

Use one canonical selection file per document workspace so theme, writing posture, and visual profile are confirmed together and reused by every later step.

## Purpose

- reduce repeated confirmation rounds
- keep writing and visuals aligned to the same narrative decision
- give later bridge skills one stable source of truth

## Canonical File

Save the bundle as:

```text
notes/selection-bundle.md
```

## Recommended Shape

```md
# Selection Bundle

- selected_theme: serious-engineering
- writing_posture: practice-sharing
- visual_profile: serious-engineering
- reader_profile: advanced-beginner
- explanation_depth: inline-expanded
- structure_preservation: strict
- annotation_mode: inline-callouts
- augmentation_modules:
  - background-primer
  - concept-clarifier
  - best-practice-extension
- visual_style_override: null
- source_boundary: source-plus-adjacent-practice
- confirmed: true

## Why This Fits

- This piece is mechanism-heavy, but the target reader still needs more concept scaffolding than a speaker-oriented sharing deck provides.
- The writing should stay restrained and evidence-led while explaining terms at the point of use.
- The visuals should stay structural, dark, and diagram-first.

## Alternatives Considered

- launch-narrative
  - Better for launch energy, but too staged for this document.
- editorial-analytic
  - Better for commentary, but weaker for system explanation.
- lively-explainer
  - Better for onboarding, but too soft for this audience.

## Notes

- If a later deliverable needs a controlled override, record it here before generation.
- Use this file as the default authority for workspace-local `.baoyu-skills` config and prompt patching.
- `reader_profile` records the intended prior-knowledge assumption for the draft.
- `explanation_depth` controls whether concept help stays minimal, inline-expanded, or section-expanded.
- `structure_preservation` records how strictly the source section order, headings, and figure positions should be preserved.
- `annotation_mode` records whether added help text should be woven into prose or exposed as explicit callouts.
- `augmentation_modules` records which reader aids should be materialized in the text, such as background primers, concept clarification, best-practice expansion, pitfalls, or misconceptions.
- `visual_profile` selects the reusable style family. `visual_style_override` captures an explicit user-provided style brief that should override the profile defaults without changing the profile's routing role.
- `source_boundary` makes it explicit whether the draft should stay source-only or may add adjacent best practices and concept scaffolding that are not verbatim in the source.
```

## Rules

- When `engineering-story-pipeline` owns the workflow, confirm this bundle once instead of asking separately for theme, writing posture, visual profile, and reader-support assumptions.
- `writing-theme-bridge` and `baoyu-style-bridge` should read this file first when it exists.
- Once the bundle is confirmed, materialize workspace-local `.baoyu-skills/.../EXTEND.md` for the likely downstream baoyu skills even if image generation is deferred.
- If the user gives an explicit style brief, save it in the bundle as a style override and let `baoyu-style-bridge` materialize that override into skill-specific config and prompt patches.
- Use `augmentation_modules` to decide whether the draft should insert inline concept explainers, short background primers, and adjacent best-practice notes near the relevant section instead of leaving them to an appendix.
- When `structure_preservation: strict` and `annotation_mode: inline-callouts`, preserve the source chapter order, headings, and image slots, then add reader aids as explicit labeled note blocks rather than silently rewriting them into the body.
- If one bridge is used standalone, it may still create a narrower note such as `writing-selection.md` or `style-selection.md`, but the pipeline should prefer `selection-bundle.md`.
