---
name: baoyu-article-illustrator
description: Analyzes article structure, identifies positions requiring visual aids, generates illustrations with Type × Style two-dimension approach. Use when user asks to "illustrate article", "add images", "generate images for article", or "为文章配图".
version: 1.56.2
metadata:
  openclaw:
    homepage: https://github.com/JimLiu/baoyu-skills#baoyu-article-illustrator
---

# Article Illustrator

Analyze articles, identify illustration positions, generate images with Type × Style consistency.

Also read [../../owned/shared/references/family-orchestration-contract.md](../../owned/shared/references/family-orchestration-contract.md).
Also read [../../owned/shared/references/extend-ownership-contract.md](../../owned/shared/references/extend-ownership-contract.md).
Also read [../../owned/shared/references/visual-source-preservation-contract.md](../../owned/shared/references/visual-source-preservation-contract.md).

This skill is a deliverable-specific leaf in the visual family. If the request includes routing, style-bridge preparation, references, multiple variants, or first-pass review, prefer `baoyu-visual-pipeline` as the entrypoint.
If you are already inside a document workspace and the request involves more than one image, Mermaid or diagram-spec sources, style-bridge preparation, or an explicit keep / regenerate review loop, stop and hand the request to `baoyu-visual-pipeline`. This skill may still be the chosen leaf after that routing.

## Two Dimensions

| Dimension | Controls | Examples |
|-----------|----------|----------|
| **Type** | Information structure | infographic, scene, flowchart, comparison, framework, timeline |
| **Style** | Visual aesthetics | notion, warm, minimal, blueprint, watercolor, elegant |

Combine freely: `--type infographic --style blueprint`

Or use presets: `--preset tech-explainer` → type + style in one flag. See [Style Presets](references/style-presets.md).

## Types

| Type | Best For |
|------|----------|
| `infographic` | Data, metrics, technical |
| `scene` | Narratives, emotional |
| `flowchart` | Processes, workflows |
| `comparison` | Side-by-side, options |
| `framework` | Models, architecture |
| `timeline` | History, evolution |

## Styles

See [references/styles.md](references/styles.md) for Core Styles, full gallery, and Type × Style compatibility.

## Shared Working Artifact Contract

If this run creates intermediate artifacts such as `outline.md`, prompt files, review notes, or staged images, also read [../../owned/shared/references/working-artifact-contract.md](../../owned/shared/references/working-artifact-contract.md). This skill may choose its own internal layout under the working location, but any artifact handed to another skill must have an explicit saved path.

## Mode Compatibility

When this skill says `AskUserQuestion`, use it if that tool is available in the current mode.

If it is not available, ask the same question set in one concise plain-text assistant message and wait for the user's reply before continuing.

## Workflow

```
- [ ] Step 1: Pre-check (EXTEND.md, references, config)
- [ ] Step 2: Analyze content
- [ ] Step 3: Confirm settings (AskUserQuestion)
- [ ] Step 4: Generate outline
- [ ] Step 5: Generate images
- [ ] Step 6: Finalize
```

### Step 1: Pre-check

**1.5 Load Preferences (EXTEND.md) ⛔ BLOCKING**

```bash
# macOS, Linux, WSL, Git Bash
test -f .baoyu-skills/baoyu-article-illustrator/EXTEND.md && echo "project"
test -f "${XDG_CONFIG_HOME:-$HOME/.config}/baoyu-skills/baoyu-article-illustrator/EXTEND.md" && echo "xdg"
test -f "$HOME/.baoyu-skills/baoyu-article-illustrator/EXTEND.md" && echo "user"
```

```powershell
# PowerShell (Windows)
if (Test-Path .baoyu-skills/baoyu-article-illustrator/EXTEND.md) { "project" }
$xdg = if ($env:XDG_CONFIG_HOME) { $env:XDG_CONFIG_HOME } else { "$HOME/.config" }
if (Test-Path "$xdg/baoyu-skills/baoyu-article-illustrator/EXTEND.md") { "xdg" }
if (Test-Path "$HOME/.baoyu-skills/baoyu-article-illustrator/EXTEND.md") { "user" }
```

| Result | Action |
|--------|--------|
| Found | Read, parse, display summary |
| Not found | ⛔ Run [first-time-setup](references/config/first-time-setup.md) |

Full procedures: [references/workflow.md](references/workflow.md#step-1-pre-check)

### Step 2: Analyze

| Analysis | Output |
|----------|--------|
| Content type | Technical / Tutorial / Methodology / Narrative |
| Purpose | information / visualization / imagination |
| Core arguments | 2-5 main points |
| Positions | Where illustrations add value |

**CRITICAL**: Metaphors → visualize underlying concept, NOT literal image.

Full procedures: [references/workflow.md](references/workflow.md#step-2-setup--analyze)

### Step 3: Confirm Settings ⚠️

**ONE AskUserQuestion, max 4 Qs. Q1-Q2 REQUIRED. Q3 required unless preset chosen, except for the single-technical-figure fast path below.**
If an upstream orchestrator has already fixed image count, style authority, or review policy in saved artifacts, reuse those saved decisions instead of re-inferring them locally.

**Single technical figure fast path**:
- Use this exception only when ALL of the following are already true:
  - the deliverable is one technical figure inside a research / engineering report
  - the single-figure scope is explicit because either the user asked for one image or an upstream plan / working artifact already fixed `image_count: 1`
  - there is no explicit style brief or reference image
  - asking multiple setup questions would add more friction than value
- Then default to:
  - `type: framework`
  - `density: minimal`
  - `style: blueprint`
  - `language: match article`
- Save those defaults in `outline.md` and continue to prompt construction.
- This fast path may skip low-value setup questions, but it may not decide image count on its own.
- If image count is still undecided, stay in normal planning / settings flow and resolve count before using this exception.
- Treat this as a low-ceremony exception for already-scoped one-image technical reports, not as a general bypass for multi-image illustration work.
- Never use this fast path for multi-image article batches or document-level visual review loops.

| Q | Options |
|---|---------|
| **Q1: Preset or Type** | [Recommended preset], [alt preset], or manual: infographic, scene, flowchart, comparison, framework, timeline, mixed |
| **Q2: Density** | minimal (1-2), balanced (3-5), per-section (Recommended), rich (6+) |
| **Q3: Style** | [Recommended], minimal-flat, sci-fi, hand-drawn, editorial, scene, poster, Other — **skip if preset chosen** |
| Q4: Language | When article language ≠ EXTEND.md setting |

Full procedures: [references/workflow.md](references/workflow.md#step-3-confirm-settings-)

### Step 4: Generate Outline

Save `outline.md` with frontmatter (type, density, style, image_count) and entries:

```yaml
## Illustration 1
**Position**: [section/paragraph]
**Purpose**: [why]
**Visual Content**: [what]
**Filename**: 01-infographic-concept-name.png
```

Full template: [references/workflow.md](references/workflow.md#step-4-generate-outline)

### Step 5: Generate Images

⛔ **BLOCKING: Prompt files MUST be saved before ANY image generation.**

**Execution strategy**: When multiple illustrations have saved prompt files and the task is now plain generation, prefer `baoyu-image-gen` batch mode (`build-batch.ts` → `--batchfile`) over spawning subagents. Use subagents only when each image still needs separate prompt iteration or creative exploration.

1. For each illustration, create a prompt file per [references/prompt-construction.md](references/prompt-construction.md)
2. Save to `prompts/NN-{type}-{slug}.md` with YAML frontmatter
3. Prompts **MUST** use type-specific templates with structured sections (ZONES / LABELS / COLORS / STYLE / ASPECT)
4. LABELS **MUST** include article-specific data: actual numbers, terms, metrics, quotes
5. **DO NOT** pass ad-hoc inline prompts to `--prompt` without saving prompt files first
6. Select generation skill, process references (`direct`/`style`/`palette`)
7. Apply watermark if EXTEND.md enabled
8. Generate from saved prompt files; retry once on failure
9. After the first successful batch or representative first-pass image, summarize visible deviations in style, structure, and readability before optional regeneration. Prefer targeted prompt fixes over blindly regenerating the whole batch.
10. When this skill is being used as a leaf under an orchestrator, hand the first-pass outputs back to that orchestrator for keep / regenerate review instead of treating leaf execution as overall completion.

If the user asked to generate images, do not fulfill the request with Mermaid-only or SVG-only output unless they explicitly asked for direct Mermaid / SVG export. Local diagrams may inform prompts, but they do not replace the rendering step.

Full procedures: [references/workflow.md](references/workflow.md#step-5-generate-images)

### Step 6: Finalize

Insert `![description]({relative-path}/NN-{type}-{slug}.png)` after paragraphs. Path computed relative to article file based on output directory setting.

```
Article Illustration Complete!
Article: [path] | Type: [type] | Density: [level] | Style: [style]
Images: X/N generated
```

## Output Directory

Output directory is determined by `default_output_dir` in EXTEND.md (set during first-time setup):

| `default_output_dir` | Output Path | Markdown Insert Path |
|----------------------|-------------|----------------------|
| `imgs-subdir` (default) | `{article-dir}/imgs/` | `imgs/NN-{type}-{slug}.png` |
| `same-dir` | `{article-dir}/` | `NN-{type}-{slug}.png` |
| `illustrations-subdir` | `{article-dir}/illustrations/` | `illustrations/NN-{type}-{slug}.png` |
| `independent` | `illustrations/{topic-slug}/` | `illustrations/{topic-slug}/NN-{type}-{slug}.png` (relative to cwd) |

All auxiliary files (outline, prompts) are saved inside the output directory:

```
{output-dir}/
├── outline.md
├── prompts/
│   └── NN-{type}-{slug}.md
└── NN-{type}-{slug}.png
```

When input is **pasted content** (no file path), always uses `illustrations/{topic-slug}/` with `source-{slug}.{ext}` saved alongside.

**Slug**: 2-4 words, kebab-case. **Conflict**: append `-YYYYMMDD-HHMMSS`.

## Modification

| Action | Steps |
|--------|-------|
| Edit | Update prompt → Regenerate → Update reference |
| Add | Position → Prompt → Generate → Update outline → Insert |
| Delete | Delete files → Remove reference → Update outline |

## References

| File | Content |
|------|---------|
| [references/workflow.md](references/workflow.md) | Detailed procedures |
| [references/usage.md](references/usage.md) | Command syntax |
| [references/styles.md](references/styles.md) | Style gallery |
| [references/style-presets.md](references/style-presets.md) | Preset shortcuts (type + style) |
| [references/prompt-construction.md](references/prompt-construction.md) | Prompt templates |
| [references/config/first-time-setup.md](references/config/first-time-setup.md) | First-time setup |
