# Workspace Config Templates

Use these inside a document workspace so all baoyu skills for that document receive the same style bias.

## `notes/selection-bundle.md`

```md
# Selection Bundle

- selected_theme: serious-engineering
- writing_posture: serious-engineering
- visual_profile: serious-engineering
- confirmed: true
- alternatives:
  - launch-keynote
  - editorial-analytic
- rationale: Core argument is architectural and tradeoff-heavy, so the writing and visuals should both prioritize structural clarity.
```

## `.baoyu-skills/baoyu-slide-deck/EXTEND.md`

```yaml
style: engineering-orange-dark
audience: experts
language: zh
review: true

custom_styles:
  engineering-orange-dark:
    texture: grid
    mood: dark
    typography: technical
    density: balanced
    description: "Dark engineering release style with orange accent and strict contrast"
```

## `.baoyu-skills/baoyu-article-illustrator/EXTEND.md`

```yaml
---
version: 1
preferred_style:
  name: engineering-orange-dark
  description: "Structural, dark, restrained, orange-accent engineering diagrams"
language: zh
default_output_dir: illustrations-subdir
custom_styles:
  - name: engineering-orange-dark
    description: "Dark engineering house style"
    color_palette:
      primary: ["#E5E5E5", "#FC5001"]
      background: "#0D0D0D"
      accents: ["#333333", "#404040"]
    visual_elements: "Flat 2D wireframes, strict grid, structural arrows only"
    typography: "Tight modern sans plus mono labels"
    best_for: "Architecture, framework, flowchart, technical explainer"
---
```

## `.baoyu-skills/baoyu-cover-image/EXTEND.md`

```yaml
---
version: 3
preferred_type: conceptual
preferred_palette: engineering-orange-dark
preferred_rendering: flat-vector
preferred_text: title-only
preferred_mood: balanced
default_aspect: "16:9"
language: zh
custom_palettes:
  - name: engineering-orange-dark
    description: "Dark engineering launch palette"
    colors:
      primary: ["#E5E5E5", "#FC5001"]
      background: "#0D0D0D"
      accents: ["#333333", "#404040"]
    decorative_hints: "No gradients, no glow, strict lines, technical poster composition"
    best_for: "Framework launch, architecture article, technical keynote cover"
---
```

## `.baoyu-skills/baoyu-comic/EXTEND.md`

```yaml
---
version: 2
preferred_art: ligne-claire
preferred_tone: neutral
preferred_layout: standard
preferred_aspect: "3:4"
language: zh
---
```

## `.baoyu-skills/baoyu-infographic/EXTEND.md`

```yaml
preferred_layout: dense-modules
preferred_style: technical-schematic
default_aspect_ratio: portrait
language: zh
```
