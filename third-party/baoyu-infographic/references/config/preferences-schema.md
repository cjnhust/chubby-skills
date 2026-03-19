# EXTEND.md Schema

Structure for user preferences in `.baoyu-skills/baoyu-infographic/EXTEND.md`.

## Full Schema

```yaml
preferred_layout: null          # Any built-in layout name or null for auto
preferred_style: null           # Any built-in style name, custom style name, or null for auto
default_aspect_ratio: landscape # landscape|portrait|square|<custom W:H>
language: auto                  # auto|zh|en|ja|etc.

custom_styles:
  engineering-minimalism:
    description: "User-defined infographic style"
    palette:
      primary: ["#E5E5E5", "#FC5001"]
      background: "#0D0D0D"
      accents: ["#333333", "#404040"]
    typography: "Tight sans + mono labels"
    composition: "Flat wireframe, strict grid, no decorative texture"
    prohibited: "No gradients, no glow, no dense background patterns"
```

## Field Reference

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `preferred_layout` | string | null | Built-in layout name or null for auto |
| `preferred_style` | string | null | Built-in style name, custom style name, or null for auto |
| `default_aspect_ratio` | string | `landscape` | Default aspect ratio |
| `language` | string | `auto` | Output language |
| `custom_styles` | map | `{}` | User-defined style definitions |

## Notes

- `preferred_style` may refer to a built-in infographic style or to a custom style defined under `custom_styles`.
- When a shared workspace style authority exists, it should be materialized here as a custom style instead of being left only in chat context.
