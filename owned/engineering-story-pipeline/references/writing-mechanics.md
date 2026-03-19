# Writing Mechanics Absorbed from Baoyu Skills

This reference captures the parts of `baoyu-skills` that are genuinely useful for technical writing workflows. Use it when the task includes source ingestion, translation, markdown cleanup, article packaging, or multi-stage article production.

## What to Preserve

### 1. Source Materialization

- Fetch URL sources into files before rewriting.
- Keep rendered snapshots and markdown captures when they exist.
- If the source is external and unstable, preserve a local working copy before analysis.

Primary source skills:
- `baoyu-url-to-markdown`

### 2. Translation Before Rewrite

- If the final article must be Chinese and the source is not, translate before polishing.
- For long technical documents, keep terminology stable through a glossary mindset instead of translating terms ad hoc in later passes.
- Preserve intermediate translation artifacts when the task is important or publication-bound.

Primary source skills:
- `baoyu-translate`

### 3. Analysis Before Formatting

- Separate content decisions from formatting decisions.
- Use reader-perspective analysis to identify structure, buried lists, definitions, tables, and formatting problems.
- Run formatting only after the content is stable enough that heading, summary, and layout decisions will not be invalidated immediately.

Primary source skills:
- `baoyu-format-markdown`

### 4. Artifact Discipline

Prefer file-based checkpoints over ephemeral chat-only state:

- raw source
- translated source
- analysis notes
- glossary or terminology notes
- article draft
- source images and their reuse decisions
- diagram specs
- prompt files
- slide outline
- final article and exported derivatives

This matters because article, visuals, and deck often evolve at different speeds.

### 5. Review Gates

Useful baoyu pattern:

- analyze first
- confirm structure or settings
- save outline or prompt files
- generate expensive assets only after the structure is stable

Apply this pattern to:

- article rewrites
- diagrams
- cover generation
- slide outlines
- legacy images that may be reused or redrawn

### 6. Data Fidelity and Secret Hygiene

- Keep all source-backed metrics, names, and claims traceable.
- Do not paraphrase numbers into softer summaries when they later feed charts or diagrams.
- Strip secrets, tokens, credentials, and internal-only literals from any working artifact that may be shared or passed to image generation.

### 7. Export as a Separate Concern

- `baoyu-markdown-to-html` is an export layer, not a writing layer.
- Use it after the article is done.
- If the content is Chinese, it can be worth running markdown formatting first so spacing and emphasis survive into HTML cleanly.
- Before export, strip workspace-facing prose, local path references, and process hints that were useful during drafting but should not appear in the formal article.

## What Not to Adopt as Default

- Feed-optimized, curiosity-gap-heavy title generation as the default for technical articles
- WeChat-specific publishing assumptions when the user only wants an internal doc or deck
- Auto-generating visuals before the article logic is stable
- Treating formatting as if it were substantive rewriting

## Default Pipeline Shape

1. ingest
2. translate if needed
3. rewrite for technical clarity
4. freeze source-of-truth article
5. clean the article into a reader-facing deliverable
6. derive diagrams and cover
7. derive deck outline
8. format or export only after content stabilizes
