# Document Workspace

Use one workspace per document or article so writing, style, prompts, and baoyu config stay attached to the same source of truth.

## Goals

- keep the whole pipeline reproducible
- avoid polluting global user preferences
- let later passes reuse one confirmed theme, writing posture, and visual configuration bundle

## Recommended Layout

For a source file `article.md`, create:

```text
article-workspace/
  source/
    source.md
    source-translated.md
  drafts/
    draft.md
    article.md
  notes/
    source-contract.md
    source-fidelity-check.md
    selection-bundle.md
    visual-inventory.md
    diagram-structures.md
    flow-closure.md
  .baoyu-skills/
    baoyu-slide-deck/EXTEND.md
    baoyu-article-illustrator/EXTEND.md
    baoyu-cover-image/EXTEND.md
    baoyu-comic/EXTEND.md
    baoyu-infographic/EXTEND.md
  prompts/
  illustrations/
  comic/
  cover-image/
  slide-deck/
  exports/
    article-final.md
```

Adjust the exact subdirectories when a skill already expects a stronger convention, but keep the same logical separation.

Inside a pipeline-owned workspace, `notes/selection-bundle.md` is the canonical decision file. Narrower notes such as `writing-selection.md` or `style-selection.md` are optional and mainly useful when a bridge skill is used standalone.

`notes/flow-closure.md` records whether the current pipeline pass is complete, paused for review, paused by scope, or blocked.

For mature source documents, `notes/source-contract.md` records the original thesis, section map, and figure anchors that must be preserved; `notes/source-fidelity-check.md` records whether the current draft still matches that contract closely enough to proceed.

`drafts/article.md` is the working source-of-truth draft. It may contain limited workflow-facing scaffolding while the article is still under review. Reader-facing delivery files should be cleaned and exported separately, for example as `exports/article-final.md`.

When inserting accepted visuals into either `drafts/article.md` or `exports/article-final.md`, use markdown paths relative to the article file, for example:

- `../illustrations/01-framework.png`
- `../cover-image/cover.jpg`

Do not write absolute filesystem paths into the article body.

If a placeholder-bearing draft later becomes a formal article with accepted images, preserve the approved Mermaid blocks or other structural diagram sources under `notes/diagram-structures.md` before removing those review aids from the final article.

## Naming Rule

- File source `foo.md` -> workspace `foo-workspace/`
- URL or pasted content -> `writing-workspace/{topic-slug}/`

## Execution Rule

Run downstream baoyu skills from the workspace root so the workspace-local `.baoyu-skills` takes effect.

## Persistence Rule

Do not treat theme selection, writing posture, style selection, or baoyu config as temporary session state. Persist them in this workspace, with `notes/selection-bundle.md` as the default source of truth.

Create workspace-local `.baoyu-skills/.../EXTEND.md` as soon as the selection bundle is confirmed when later visuals or deck work are plausible, even if the current pass stops at writing.

## Reuse Rule

If the user later says "继续补图", "继续出 PPT", or "继续改稿", reopen the same workspace and continue from its saved selection bundle and workspace-local configs.

Before resuming, read the previous `notes/flow-closure.md` so the next pass starts from the actual last stopping point rather than from a guessed state.

## Reader-Facing Rule

Before treating an article as a formal deliverable, remove or rewrite workspace-facing helper text such as:

- source-of-truth draft banners
- local path references like `../source/source.md`
- references to `notes/selection-bundle.md` or `notes/visual-inventory.md`
- "if later you want images or deck" process notes
- internal review or export reminders that are not part of the article itself

Also verify that markdown image links remain reader-facing:

- use relative paths that survive normal local markdown preview
- do not leak absolute workspace paths into the document body
