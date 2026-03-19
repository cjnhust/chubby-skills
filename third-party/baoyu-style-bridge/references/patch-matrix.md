# Artifact Patch Matrix

## baoyu-slide-deck `outline.md`

Patch:

- replace `STYLE INSTRUCTIONS`
- rewrite any palette description that leans blue or generic corporate
- keep slide narrative and structure, but align the visual language to the house style

Check:

- cover slide reads like a poster
- ending slide is designed, not generic
- body slides remain grid- or triptych-based

## baoyu-slide-deck `prompts/NN-slide-*.md`

Patch:

- background color language
- accent color language
- typography feel
- prohibited effects
- chart and diagram rules

Remove:

- glow
- cinematic haze
- decorative blueprints used as wallpaper

## baoyu-article-illustrator `prompts/NN-*.md`

Patch:

- `STYLE`
- `COLORS`
- `ZONES`
- any decorative or playful cues that fight the engineering tone

Keep:

- article-specific labels
- metrics
- API names
- node and arrow structure

## baoyu-comic `storyboard.md` and `prompts/NN-*.md`

Patch:

- art and tone selection
- layout pacing
- instructional or dramatic intensity
- whether panels should feel educational, launch-like, or playful

Keep:

- factual sequence
- stable character roles if already defined
- technical terms and teaching logic

## baoyu-cover-image `prompts/cover.md`

Patch:

- palette
- rendering language
- decorative hints
- metaphor direction

Keep:

- title and subtitle intent
- chosen aspect ratio
- reference images if present

## Workspace-Local `.baoyu-skills` Configs

Use when the same style should stay attached to one document workspace across repeated runs.

- `baoyu-slide-deck`: define a custom style name
- `baoyu-article-illustrator`: define a custom style and preferred style notes
- `baoyu-cover-image`: define a custom palette
