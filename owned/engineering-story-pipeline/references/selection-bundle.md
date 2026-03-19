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
- writing_posture: serious-engineering
- visual_profile: serious-engineering
- visual_style_override: null
- confirmed: true

## Why This Fits

- This piece is architecture-heavy, tradeoff-driven, and aimed at senior technical readers.
- The writing should stay restrained and evidence-led.
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
- `visual_profile` selects the reusable style family. `visual_style_override` captures an explicit user-provided style brief that should override the profile defaults without changing the profile's routing role.
```

## Rules

- When `engineering-story-pipeline` owns the workflow, confirm this bundle once instead of asking separately for theme, writing posture, and visual profile.
- `writing-theme-bridge` and `baoyu-style-bridge` should read this file first when it exists.
- Once the bundle is confirmed, materialize workspace-local `.baoyu-skills/.../EXTEND.md` for the likely downstream baoyu skills even if image generation is deferred.
- If the user gives an explicit style brief, save it in the bundle as a style override and let `baoyu-style-bridge` materialize that override into skill-specific config and prompt patches.
- If one bridge is used standalone, it may still create a narrower note such as `writing-selection.md` or `style-selection.md`, but the pipeline should prefer `selection-bundle.md`.
