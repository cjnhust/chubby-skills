# Deck Outline Contract

Use this contract whenever the deliverable includes a slide outline or a full deck.

## Output Rules

- Slides are designed for reading and sharing, not only for live presentation.
- Every slide must be understandable without a presenter.
- Visible content should be Chinese unless a proper noun must stay in English.
- Keep the full deck within 20 slides.
- Slide 1 must be the cover page.
- The final slide must be a designed ending with meaning. Do not end with a generic thanks or Q&A slide.

## Required Preamble

Before slide entries, include a code block named `STYLE INSTRUCTIONS`.

- Base it on `references/visual-system.md`.
- Keep the orange accent as `#FC5001`.
- Preserve the dark, flat, high-contrast engineering aesthetic.

## Slide Entry Contract

Every slide must include these four sections in this order:

```text
// NARRATIVE GOAL
// KEY CONTENT
// VISUAL
// LAYOUT
```

## Writing Rules for Slides

- Use direct, confident, human language.
- Avoid `标题：副标题` style titles.
- Avoid slogan language and obvious AI filler.
- Keep claims traceable to the source material.
- If a data point is concrete, it must come from the source.
- Preserve enough context so designers can work from the outline without reopening the source.

## Visual Rules for Slides

- Cover and ending slides should use poster-like composition, not the same layout as content slides.
- Internal slides should prefer grid, triptych, or split layouts.
- Use typography, structure, and restrained charts before resorting to decorative illustration.
- If a slide contains a diagram, keep it compatible with the diagram rules in `references/diagram-contract.md`.

## Review Order

1. narrative arc
2. slide count
3. per-slide density
4. whether the style block still matches the shared visual system
