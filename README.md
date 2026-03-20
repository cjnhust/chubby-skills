# Codex Skills Export

This repository stages a publishable subset of a larger local Codex skills tree.
It keeps user-owned skills and third-party skills under separate top-level boundaries so publication and review remain explicit.

## Layout

- `owned/`: skills authored or maintained in this collection.
- `third-party/`: externally authored or inherited skills kept under a separate review boundary.
- `third-party/ORIGIN.md`: source and upstream review manifest.
- `third-party/LICENSES.md`: redistribution and license review manifest.
- `THIRD_PARTY_ACKNOWLEDGEMENTS.md`: attribution and thanks for imported third-party skills.
- `SECURITY.md`: publishing-time security rules and disclosure guidance.
- `RELEASE_CHECKLIST.md`: final checks before creating the public GitHub repo or pushing.
- `CODEX_SETUP.md`: post-publish Codex connection steps and a review-first smoke test.
- `LICENSE_DECISION.md`: maintainer note for selecting the root repository license for `owned/` content.

## Status

- Secret, absolute-path, and junk-artifact checks pass on this staged export.
- Third-party provenance and license review are confirmed at repo level for this staged export.
- A root repository license file is present for this export.
- Built-in `.system/` skills and `danger-*` skills are intentionally excluded from this export.

## Source Families

- `Baoyu public repo skills`: 12 staged unit(s); origin `confirmed`, license `confirmed`; Imported SKILL.md files include homepage metadata pointing to sections inside the public JimLiu/baoyu-skills repository. Source: [https://github.com/JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills). Operator confirmed that this export uses the GitHub repository as the source basis, so repo-level license handling is used here instead of ClawHub registry release terms.
- `Baoyu inferred family extensions`: 3 staged unit(s); origin `confirmed`, license `confirmed`; These skills share the baoyu family naming and are referenced by neighboring imported baoyu skills, but the current staged copy does not include direct homepage metadata for them. Source: [https://github.com/JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills). Operator confirmed that these imported skills were sourced from the same GitHub repository at repo level, even though the staged copy does not carry direct per-skill homepage metadata.
- `Baoyu public repo packages`: 2 staged unit(s); origin `confirmed`, license `confirmed`; The public JimLiu/baoyu-skills repository has a packages/ directory listing baoyu-md and baoyu-chrome-cdp as package folders. Source: [https://github.com/JimLiu/baoyu-skills/tree/main/packages](https://github.com/JimLiu/baoyu-skills/tree/main/packages). Operator confirmed that these vendored units are accepted under the same GitHub repo-level source and license basis for this export.

## Included Owned Skills

- `engineering-practice-writer`: Rewrite or draft Chinese technical prose in a mature engineering-practice style.
- `engineering-story-pipeline`: Chain Chinese technical writing, diagrams, and slide-deck work into one pipeline by combining engineering-practice-writer with baoyu skills such as baoyu-format-markdown, baoyu-...
- `research-report-pipeline`: Orchestrate topic-based or URL-based Chinese technical research reports by confirming scope before expansion, collecting primary sources, building a source catalog and evidence...
- `skills-github-publisher`: Orchestrate safe publication of local Codex skills to GitHub.
- `writing-theme-bridge`: Read or recommend a writing posture from article content, user context, and an optional selected theme, then route drafting through the appropriate writing behavior.

## Included Third-Party Skills

- `baoyu-article-illustrator`: Analyzes article structure, identifies positions requiring visual aids, generates illustrations with Type × Style two-dimension approach. Current imported version marker: `1.56.1`. [source](https://github.com/JimLiu/baoyu-skills#baoyu-article-illustrator).
- `baoyu-comic`: Knowledge comic creator supporting multiple art styles and tones. Creates original educational comics with detailed panel layouts and sequential image generation. Current imported version marker: `1.56.1`. [source](https://github.com/JimLiu/baoyu-skills#baoyu-comic).
- `baoyu-compress-image`: Compresses images to WebP (default) or PNG with automatic tool selection. Current imported version marker: `1.56.1`. [source](https://github.com/JimLiu/baoyu-skills#baoyu-compress-image).
- `baoyu-content-pipeline`: Orchestrate non-trivial content ingestion and transformation requests by routing between webpage capture, X capture, translation, markdown cleanup, and HTML export while persist... inferred source family: [Baoyu inferred family extensions](https://github.com/JimLiu/baoyu-skills).
- `baoyu-cover-image`: Generates article cover images with 5 dimensions (type, palette, rendering, text, mood) combining 10 color palettes and 7 rendering styles. Supports cinematic (2.35:1), widescre... Current imported version marker: `1.56.1`. [source](https://github.com/JimLiu/baoyu-skills#baoyu-cover-image).
- `baoyu-format-markdown`: Formats plain text or markdown files with frontmatter, titles, summaries, headings, bold, lists, and code blocks. Current imported version marker: `1.56.1`. [source](https://github.com/JimLiu/baoyu-skills#baoyu-format-markdown).
- `baoyu-image-gen`: AI image generation with OpenAI, Google, OpenRouter, DashScope, Jimeng, Seedream and Replicate APIs. Supports text-to-image, reference images, aspect ratios, and batch generatio... Current imported version marker: `1.56.2`. [source](https://github.com/JimLiu/baoyu-skills#baoyu-image-gen).
- `baoyu-infographic`: Generates professional infographics with 21 layout types and 20 visual styles. Analyzes content, recommends layout×style combinations, and generates publication-ready infographics. Current imported version marker: `1.56.1`. [source](https://github.com/JimLiu/baoyu-skills#baoyu-infographic).
- `baoyu-markdown-to-html`: Converts Markdown to styled HTML with WeChat-compatible themes. Supports code highlighting, math, PlantUML, footnotes, alerts, infographics, and optional bottom citations for ex... Current imported version marker: `1.56.1`. [source](https://github.com/JimLiu/baoyu-skills#baoyu-markdown-to-html).
- `baoyu-slide-deck`: Generates professional slide deck images from content. Creates outlines with style instructions, then generates individual slide images. Current imported version marker: `1.56.1`. [source](https://github.com/JimLiu/baoyu-skills#baoyu-slide-deck).
- `baoyu-style-bridge`: Normalize a visual style brief or visual profile into explicit style artifacts by patching saved outline.md files, STYLE INSTRUCTIONS blocks, prompt files, or targeted workspace... inferred source family: [Baoyu inferred family extensions](https://github.com/JimLiu/baoyu-skills).
- `baoyu-translate`: Translates articles and documents between languages with three modes - quick (direct), normal (analyze then translate), and refined (analyze, translate, review, polish). Support... Current imported version marker: `1.56.1`. [source](https://github.com/JimLiu/baoyu-skills#baoyu-translate).
- `baoyu-url-to-markdown`: Fetch any URL and convert to markdown using Chrome CDP. Saves the rendered HTML snapshot alongside the markdown, uses an upgraded Defuddle pipeline with better web-component han... Current imported version marker: `1.58.1`. [source](https://github.com/JimLiu/baoyu-skills#baoyu-url-to-markdown).
- `baoyu-visual-pipeline`: Orchestrate non-trivial visual generation requests by choosing the right visual deliverable skill, normalizing style through baoyu-style-bridge when needed, materializing prompt... inferred source family: [Baoyu inferred family extensions](https://github.com/JimLiu/baoyu-skills).
- `baoyu-xhs-images`: Generates Xiaohongshu (Little Red Book) infographic series with 11 visual styles and 8 layouts. Breaks content into 1-10 cartoon-style images optimized for XHS engagement. Current imported version marker: `1.56.1`. [source](https://github.com/JimLiu/baoyu-skills#baoyu-xhs-images).

## Example Prompts

- `Use $skills-github-publisher to audit and prepare a local skills tree for safe GitHub publication.`
- `Use $engineering-story-pipeline to turn local notes into a Chinese technical article and slide deck.`
- `Use $research-report-pipeline to write a Chinese technical research report from a topic and source list.`
- `Use $baoyu-url-to-markdown to save a webpage as markdown.`
- `Use $baoyu-translate to translate an article into Chinese or English.`
- `Use $baoyu-cover-image to generate a cover image for an article.`

## Third-Party Skills Used By Owned Workflows

- `engineering-story-pipeline` currently references these third-party skills: `baoyu-article-illustrator`, `baoyu-comic`, `baoyu-content-pipeline`, `baoyu-cover-image`, `baoyu-format-markdown`, `baoyu-image-gen`, `baoyu-infographic`, `baoyu-markdown-to-html`, `baoyu-slide-deck`, `baoyu-style-bridge`, `baoyu-translate`, `baoyu-url-to-markdown`, `baoyu-visual-pipeline`.
- `research-report-pipeline` currently references these third-party skills: `baoyu-article-illustrator`, `baoyu-content-pipeline`, `baoyu-cover-image`, `baoyu-image-gen`, `baoyu-infographic`, `baoyu-url-to-markdown`.

## Vendored Components

- `third-party/baoyu-markdown-to-html/scripts/vendor/baoyu-md`: vendored package `baoyu-md` version `0.1.0`; covered by confirmed repo-level origin and license review for this export.
- `third-party/baoyu-url-to-markdown/scripts/vendor/baoyu-chrome-cdp`: vendored package `baoyu-chrome-cdp` version `0.1.0`; covered by confirmed repo-level origin and license review for this export.

## Acknowledgements

Thanks to the original author and maintainers of the Baoyu skill family. Current source references in the imported skills point to [JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills).
See [`THIRD_PARTY_ACKNOWLEDGEMENTS.md`](THIRD_PARTY_ACKNOWLEDGEMENTS.md) for the current attribution notes and review status.

## Post-Publish Maintenance

- Keep the initial sanitization and first public release local-first.
- If you later want Codex on GitHub, prefer PR review on this already public repository before broader cloud-side edit flows.
- Trigger Codex review exactly once per PR head: use repository auto review or reviewer request when available, and keep `@codex review` as the manual fallback instead of stacking both.
- Keep GitHub conversation resolution enabled so unresolved review threads block merge; if the head changes, wait for a fresh current-head review rather than relying on an older review result.
- If a trusted maintainer later wants Codex to write back to an existing PR branch, make that an explicit minimal-scope request on an already public PR branch rather than an automatic workflow loop.
- Do not use Codex GitHub maintenance for unpublished branches, internal-only content, or local private policy files.

## Maintainer Incremental Flow

- Pin one local publish working copy through the private `default_publish_repo` config and reuse that repo instead of creating a new staging directory for each update.
- Treat this repository as the publish mirror, not the authoring source of truth for skill bundles.
- Do not hand-edit files under `owned/<skill>/` or `third-party/<skill>/` in this repo. Make the change in the local source skill, then sync it out.
- Start repeated syncs with `python3 owned/skills-github-publisher/scripts/prepare_incremental_pr.py --skill-root /absolute/path/to/skill`, which refreshes the base branch, creates or reuses a PR branch, syncs the skill roots, writes a signed `.publish-sync/manifest.json` plus `.publish-sync/manifest.json.sig`, and reruns local checks.
- After reviewing and committing, use `python3 owned/skills-github-publisher/scripts/push_pr_handoff.py --base main` to inspect the push and PR handoff from the same fixed publish repo.
- PRs that change managed skill content now have to pass `publish-sync-guard`, which rejects direct edits that do not match the recorded signed sync manifest.
