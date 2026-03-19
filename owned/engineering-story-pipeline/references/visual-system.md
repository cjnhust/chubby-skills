# Shared Visual System

Apply this visual system to article covers, inline diagrams, and slide decks. The goal is a Chinese technical storytelling style that feels close to modern React or React Native release presentations, but with a stricter engineering-document posture and `#FC5001` as the theme accent.

## Design Position

- Audience: senior technical readers, framework authors, architecture reviewers
- Tone: calm, precise, analytical, high-agency
- Primary metaphor: engineering blueprint meets release-keynote clarity
- Rendering family: flat 2D vector or wireframe diagram, never photorealistic or decorative

## House Style Block

Use or adapt this block whenever a deliverable needs a `STYLE INSTRUCTIONS` section:

```text
Design Aesthetic: Engineering Minimalism with release-keynote precision. Cold, exact, and structured. The visual language should feel like a high-end technical blueprint adapted for a modern framework launch deck.

Background Color: Matte charcoal black (#0D0D0D). Flat, texture-light, high contrast. No gradients, no glows, no glass effects.

Headline Typography Feel: Similar to Inter Tight or Helvetica Now Display. Tight, modern, neutral, large-scale, and capable of carrying the composition by itself.

Secondary Typography Feel: Similar to JetBrains Mono. Use for metrics, labels, technical terms, paths, and interface-like callouts.

Color Palette:
- Primary text: soft gray-white (#E5E5E5)
- Accent: signal orange (#FC5001)
- Panel/background support: deep gray (#333333)
- Borders and connectors: border gray (#404040)

Accent Usage Rule: Keep orange below 5 percent of the canvas. Use it only for current focus, changed modules, key numbers, active paths, or decisive calls to action.

Visual Elements:
- Fine wireframe lines and structural boxes in #404040
- Mostly unfilled panels; use orange solid fills only on the focal element
- Minimal bar charts or line charts with no decorative grid
- Strict alignment and modular spacing
- Triptych or grid-based composition when possible

Prohibited:
- Shadows, gradients, bloom, bevels, glassmorphism, glossy 3D
- Circuit-board wallpaper, pseudo-code texture, noisy futuristic backgrounds
- Tiny unreadable labels, dense paragraphs, fake depth, stock-photo realism

Output Qualities:
- Chinese-visible text by default
- Sharp PNG-friendly contrast
- Self-explanatory visuals that can be understood without a presenter
```

## Diagram Rules

Use these rules for architecture, framework, and flowchart visuals:

- Prefer clean boxes, lanes, and arrows over pictorial illustration.
- Use orange only for the primary path, changed path, bottleneck, key metric, or selected option.
- Keep the default diagram body in gray-white text on charcoal panels with gray connectors.
- Keep labels short and explicit. Use module names, API names, and phase names from the source material.
- Avoid more than 8 to 10 primary nodes unless the content truly requires density.
- Prefer left-to-right or top-to-bottom reading order. Avoid crossing lines when possible.
- For request or lifecycle paths, show only the essential branches. Do not visualize every edge case.

## Visual Mapping

- `framework`: modules, component relationships, layered architecture, mental models
- `flowchart`: request path, publish pipeline, troubleshooting sequence, lifecycle, onboarding
- `comparison`: tradeoff tables, migration options, old vs new architecture
- `infographic`: metrics, API surface, compatibility matrix, release deltas
- `cover`: metaphor or hero composition that signals the theme without becoming literal clip art

## Prompt Hints for Baoyu Outputs

- Prefer `blueprint` as the base style preset, then inject this house style where the prompt or outline allows extra detail.
- When using `baoyu-cover-image`, favor `conceptual`, `metaphor`, or `minimal`.
- When using `baoyu-article-illustrator`, favor `framework + blueprint`, `flowchart + blueprint`, or `infographic + blueprint`.
- When using `baoyu-slide-deck`, keep the preset as `blueprint`, but rewrite the generated style block so the accent becomes `#FC5001` and the mood stays dark, restrained, and technical.
