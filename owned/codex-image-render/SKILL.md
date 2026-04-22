---
name: codex-image-render
description: Execute image rendering through Codex's built-in image_gen tool inside a Codex session. Consumes saved prompt files, raw prompts, reference images, and explicit output paths; renders one asset at a time and copies finals back into the workspace.
---

# Codex Image Render

Use this skill only as a leaf renderer when the current turn clearly exposes the built-in `image_gen` tool.

This skill does not own workspace creation, style normalization, prompt staging, review policy, or downstream routing. It only executes rendering through the built-in tool and saves outputs to explicit target paths.

Do not use this skill when the user explicitly asks for `provider`, `model`, `API`, `CLI`, `batchfile`, `jobs`, `json`, or the existing `baoyu-image-gen` script path. In those cases, return control to `baoyu-image-gen` so it can stay on its API/CLI path.

## Inputs

- saved prompt files and/or raw prompt
- optional reference images or edit targets
- explicit output path per asset

## Rules

- Require an explicit output path for every asset.
- Treat saved prompt files as the source of truth when they exist.
- For multiple assets, issue one built-in `image_gen` call per asset.
- For local reference images or edit targets that are not already visible in the conversation, load them with built-in `view_image` first so they are available to the built-in path.
- Support reference-image generation by capability equivalence. Do not describe it as CLI `--ref`.
- Do not promise `provider`, `model`, `batchfile`, `jobs`, `json`, or session semantics. This skill uses the built-in tool only.
- The built-in tool saves under `$CODEX_HOME/generated_images/...` by default. After generation, move or copy the selected result to the requested workspace path.
- Do not overwrite an existing output unless the caller or user explicitly asked for replacement. Otherwise create a sibling versioned filename.
- If the current turn does not actually expose built-in `image_gen`, stop and return control to the caller instead of guessing.

## Workflow

1. Confirm the current turn clearly has built-in `image_gen`.
2. Normalize prompt inputs.
   - If prompt files were supplied, read them and assemble the final prompt.
   - If only a raw prompt was supplied, normalize it without changing the requested semantics.
3. Normalize image inputs.
   - Label each image as `reference image` or `edit target`.
   - Load local files with `view_image` first when needed.
4. Call built-in `image_gen` once per asset.
5. Inspect the result, choose the intended final, and copy or move it from the default generated-images directory to the explicit output path.
6. Report the saved output path and prompt used back to the caller.
