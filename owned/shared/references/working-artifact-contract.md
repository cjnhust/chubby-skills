# Working Artifact Contract

Read this reference whenever the current skill run will create intermediate artifacts that may be reused, reviewed, regenerated, or handed to another skill.

## Core Rules

- Before the flow starts, some caller must choose a working location and make it known to the current run.
- All intermediate artifacts and final outputs for that run should be written under that working location.
- Each skill may define its own internal subdirectory layout under that location.
- Only artifacts that cross skill boundaries need stable, explicit saved paths.
- Skill-private scratch files may use any layout, but they should still remain under the same working location when the flow is meant to be reproducible.
- Do not rely on unsaved chat context as the only copy of reusable prompts, outlines, notes, snapshots, or outputs.
- If a run is truly single-shot and produces no reusable intermediate artifacts, the skill may write the final output directly and skip extra scaffolding.

## Ownership

- A higher-level orchestration skill owns the root working location when one exists.
- In a direct invocation with no separate orchestrator, the current skill becomes the flow-local orchestrator for its own run and should choose one working location up front before persisting intermediates.
- A capability skill may create its own files and subdirectories inside the working location, but it does not own unrelated shared state outside its scope.
- A bridge skill may patch or create explicit target artifacts inside the working location, but it does not own root path policy, shared bundle policy, or downstream routing.

## Typical Cross-Skill Artifacts

- normalized source files or source snapshots
- style-authority files
- outline, storyboard, or diagram-spec files
- prompt files
- review notes
- generated outputs such as images, HTML, PDF, or slide assets
