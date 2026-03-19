---
name: baoyu-markdown-to-html
description: Converts Markdown to styled HTML with WeChat-compatible themes. Supports code highlighting, math, PlantUML, footnotes, alerts, infographics, and optional bottom citations for external links. Use when user asks for "markdown to html", "convert md to html", "md转html", "微信外链转底部引用", or needs styled HTML output from markdown.
version: 1.56.2
metadata:
  openclaw:
    homepage: https://github.com/JimLiu/baoyu-skills#baoyu-markdown-to-html
    requires:
      anyBins:
        - bun
        - npx
---

# Markdown to HTML Converter

Converts Markdown files to beautifully styled HTML with inline CSS, optimized for WeChat Official Account and other platforms.

Also read [../../owned/shared/references/family-orchestration-contract.md](../../owned/shared/references/family-orchestration-contract.md).
Also read [../../owned/shared/references/extend-ownership-contract.md](../../owned/shared/references/extend-ownership-contract.md).
Also read [../../owned/shared/references/transform-traceability-contract.md](../../owned/shared/references/transform-traceability-contract.md).

This skill is a leaf capability in the content-transformation family. If HTML export is the last stage of a larger capture/translate/format flow, prefer `baoyu-content-pipeline` as the entrypoint.

## Script Directory

**Agent Execution**: Determine this SKILL.md directory as `{baseDir}`. Resolve `${BUN_X}` runtime: if `bun` installed → `bun`; if `npx` available → `npx -y bun`; otherwise ask to install `bun`, install it, and continue. Do not silently replace this skill with ad hoc HTML conversion while still claiming the skill ran. Replace `{baseDir}` and `${BUN_X}` with actual values.

| Script | Purpose |
|--------|---------|
| `scripts/main.ts` | Main entry point |

## Preferences (EXTEND.md)

Check EXTEND.md existence (priority order):

```bash
# macOS, Linux, WSL, Git Bash
test -f .baoyu-skills/baoyu-markdown-to-html/EXTEND.md && echo "project"
test -f "${XDG_CONFIG_HOME:-$HOME/.config}/baoyu-skills/baoyu-markdown-to-html/EXTEND.md" && echo "xdg"
test -f "$HOME/.baoyu-skills/baoyu-markdown-to-html/EXTEND.md" && echo "user"
```

```powershell
# PowerShell (Windows)
if (Test-Path .baoyu-skills/baoyu-markdown-to-html/EXTEND.md) { "project" }
$xdg = if ($env:XDG_CONFIG_HOME) { $env:XDG_CONFIG_HOME } else { "$HOME/.config" }
if (Test-Path "$xdg/baoyu-skills/baoyu-markdown-to-html/EXTEND.md") { "xdg" }
if (Test-Path "$HOME/.baoyu-skills/baoyu-markdown-to-html/EXTEND.md") { "user" }
```

┌──────────────────────────────────────────────────────────────┬───────────────────┐
│                             Path                             │     Location      │
├──────────────────────────────────────────────────────────────┼───────────────────┤
│ .baoyu-skills/baoyu-markdown-to-html/EXTEND.md               │ Project directory │
├──────────────────────────────────────────────────────────────┼───────────────────┤
│ $HOME/.baoyu-skills/baoyu-markdown-to-html/EXTEND.md         │ User home         │
└──────────────────────────────────────────────────────────────┴───────────────────┘

┌───────────┬───────────────────────────────────────────────────────────────────────────┐
│  Result   │                                  Action                                   │
├───────────┼───────────────────────────────────────────────────────────────────────────┤
│ Found     │ Read, parse, apply settings                                               │
├───────────┼───────────────────────────────────────────────────────────────────────────┤
│ Not found │ Use defaults                                                              │
└───────────┴───────────────────────────────────────────────────────────────────────────┘

**EXTEND.md Supports**: Default theme | Custom CSS variables | Code block style

Treat these as this skill's direct defaults. If the current run needs a one-off shared theme or export posture, pass it explicitly from the orchestrator rather than reading another skill's `EXTEND.md` as hidden state.

## Shared Working Artifact Contract

If this run creates intermediate artifacts such as normalized markdown, review notes, staged citations, or auxiliary export files, also read [../../owned/shared/references/working-artifact-contract.md](../../owned/shared/references/working-artifact-contract.md). This skill may choose its own internal layout under the working location, but any artifact handed to another skill must have an explicit saved path.

## Mode Compatibility

When this skill says `AskUserQuestion`, use it if that tool is available in the current mode.

If it is not available, ask the same confirmation in one concise plain-text assistant message and wait for the user's reply before continuing.

## Workflow

### Step 0: Pre-check (Chinese Content)

**Condition**: Only execute if input file contains Chinese text.

**Detection**:
1. Read input markdown file
2. Check if content contains CJK characters (Chinese/Japanese/Korean)
3. If no CJK content → skip to Step 1

**Format Suggestion**:

If CJK content detected AND `baoyu-format-markdown` skill is available:

Use `AskUserQuestion` to ask whether to format first. Formatting can fix:
- Bold markers with punctuation inside causing `**` parse failures
- CJK/English spacing issues

**If user agrees**: Invoke `baoyu-format-markdown` skill to format the file, then use formatted file as input.

**If user declines**: Continue with original file.

### Step 1: Determine Theme

**Theme resolution order** (first match wins):
1. User explicitly specified theme (CLI `--theme` or conversation)
2. EXTEND.md `default_theme` (this skill's own EXTEND.md, checked in Step 0)
3. If none found → use AskUserQuestion to confirm

Do not read another skill's `EXTEND.md` as a hidden fallback. If an orchestration workflow wants a shared theme, it should pass that theme explicitly to this skill.

**If theme is resolved from EXTEND.md**: Use it directly, do NOT ask the user.

**If no default found**: Use AskUserQuestion to confirm:

| Theme | Description |
|-------|-------------|
| `default` (Recommended) | Classic - traditional layout, centered title with bottom border, H2 with white text on colored background |
| `grace` | Elegant - text shadow, rounded cards, refined blockquotes |
| `simple` | Minimal - modern minimalist, asymmetric rounded corners, clean whitespace |
| `modern` | Modern - large radius, pill-shaped titles, relaxed line height (pair with `--color red` for traditional red-gold style) |

### Step 1.5: Determine Citation Mode

**Default**: Off. Do not ask by default.

**Enable only if the user explicitly asks** for "微信外链转底部引用", "底部引用", "文末引用", or passes `--cite`.

**Behavior when enabled**:
- Ordinary external links are rendered with numbered superscripts and collected under a final `引用链接` section.
- `https://mp.weixin.qq.com/...` links stay as direct links and are not moved to the bottom.
- Bare links where link text equals URL stay inline.

### Step 2: Convert

```bash
${BUN_X} {baseDir}/scripts/main.ts <markdown_file> --theme <theme> [--cite]
```

### Step 3: Report Result

Display the output path from JSON result. If backup was created, mention it.

## Usage

```bash
${BUN_X} {baseDir}/scripts/main.ts <markdown_file> [options]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--theme <name>` | Theme name (default, grace, simple, modern) | default |
| `--color <name\|hex>` | Primary color: preset name or hex value | theme default |
| `--font-family <name>` | Font: sans, serif, serif-cjk, mono, or CSS value | theme default |
| `--font-size <N>` | Font size: 14px, 15px, 16px, 17px, 18px | 16px |
| `--title <title>` | Override title from frontmatter | |
| `--cite` | Convert external links to bottom citations, append `引用链接` section | false (off) |
| `--keep-title` | Keep the first heading in content | false (removed) |
| `--help` | Show help | |

**Color Presets:**

| Name | Hex | Label |
|------|-----|-------|
| blue | #0F4C81 | Classic Blue |
| green | #009874 | Emerald Green |
| vermilion | #FA5151 | Vibrant Vermilion |
| yellow | #FECE00 | Lemon Yellow |
| purple | #92617E | Lavender Purple |
| sky | #55C9EA | Sky Blue |
| rose | #B76E79 | Rose Gold |
| olive | #556B2F | Olive Green |
| black | #333333 | Graphite Black |
| gray | #A9A9A9 | Smoke Gray |
| pink | #FFB7C5 | Sakura Pink |
| red | #A93226 | China Red |
| orange | #D97757 | Warm Orange (modern default) |

**Examples:**

```bash
# Basic conversion (uses default theme, removes first heading)
${BUN_X} {baseDir}/scripts/main.ts article.md

# With specific theme
${BUN_X} {baseDir}/scripts/main.ts article.md --theme grace

# Theme with custom color
${BUN_X} {baseDir}/scripts/main.ts article.md --theme modern --color red

# Enable bottom citations for ordinary external links
${BUN_X} {baseDir}/scripts/main.ts article.md --cite

# Keep the first heading in content
${BUN_X} {baseDir}/scripts/main.ts article.md --keep-title

# Override title
${BUN_X} {baseDir}/scripts/main.ts article.md --title "My Article"
```

## Output

**File location**: Same directory as input markdown file.
- Input: `/path/to/article.md`
- Output: `/path/to/article.html`

**Conflict handling**: If HTML file already exists, it will be backed up first:
- Backup: `/path/to/article.html.bak-YYYYMMDDHHMMSS`

**JSON output to stdout:**

```json
{
  "title": "Article Title",
  "author": "Author Name",
  "summary": "Article summary...",
  "htmlPath": "/path/to/article.html",
  "backupPath": "/path/to/article.html.bak-20260128180000",
  "contentImages": [
    {
      "placeholder": "MDTOHTMLIMGPH_1",
      "localPath": "/path/to/img.png",
      "originalPath": "imgs/image.png"
    }
  ]
}
```

## Themes

| Theme | Description |
|-------|-------------|
| `default` | Classic - traditional layout, centered title with bottom border, H2 with white text on colored background |
| `grace` | Elegant - text shadow, rounded cards, refined blockquotes (by @brzhang) |
| `simple` | Minimal - modern minimalist, asymmetric rounded corners, clean whitespace (by @okooo5km) |
| `modern` | Modern - large radius, pill-shaped titles, relaxed line height (pair with `--color red` for traditional red-gold style) |

## Supported Markdown Features

| Feature | Syntax |
|---------|--------|
| Headings | `# H1` to `###### H6` |
| Bold/Italic | `**bold**`, `*italic*` |
| Code blocks | ` ```lang ` with syntax highlighting |
| Inline code | `` `code` `` |
| Tables | GitHub-flavored markdown tables |
| Images | `![alt](src)` |
| Links | `[text](url)`; add `--cite` to move ordinary external links into bottom references |
| Blockquotes | `> quote` |
| Lists | `-` unordered, `1.` ordered |
| Alerts | `> [!NOTE]`, `> [!WARNING]`, etc. |
| Footnotes | `[^1]` references |
| Ruby text | `{base|annotation}` |
| Mermaid | ` ```mermaid ` diagrams |
| PlantUML | ` ```plantuml ` diagrams |

## Frontmatter

Supports YAML frontmatter for metadata:

```yaml
---
title: Article Title
author: Author Name
description: Article summary
---
```

If no title is found, extracts from first H1/H2 heading or uses filename.

## Extension Support

Custom configurations via EXTEND.md. See **Preferences** section for paths and supported options.
