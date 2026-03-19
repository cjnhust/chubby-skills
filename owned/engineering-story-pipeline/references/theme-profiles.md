# Theme Profiles

Themes are selected from article content and user context before writing and visual generation. A theme affects:

- writing posture
- visual profile
- preferred downstream skills
- which asset types should be emphasized or avoided

## Selection Rule

Choose one recommended theme and 2-3 alternatives based on:

- what the article is trying to do
- how serious or expressive it should feel
- whether it teaches, argues, launches, compares, or dramatizes
- whether sequential storytelling is useful

## Themes

### `serious-engineering`

Use when:

- RFCs
- architecture docs
- design proposals
- technical deep dives
- benchmark or migration docs
- technology evaluation and adoption reports
- technical sharing or engineering practice retrospectives

Writing posture:

- restraint
- constraints and tradeoffs first
- mechanism-heavy explanation
- minimal rhetorical flourish
- use `rfc-document` when the piece is a formal proposal or technical document meant for review and implementation
- use `research-report` when the piece is an evidence-led evaluation that should help the reader understand, try, compare, or adopt the object under an explicit scope and evidence boundary
- use `practice-sharing` instead of plain `serious-engineering` when the piece reconstructs how one concrete workflow, system, or production chain evolved in practice

Visual profile:

- `serious-engineering`

Preferred skills:

- `engineering-practice-writer`
- `baoyu-article-illustrator`
- `baoyu-slide-deck`
- `baoyu-cover-image`

Avoid by default:

- `baoyu-comic`

### `launch-narrative`

Use when:

- release docs
- launch stories
- roadmap decks
- framework evolution or strategy communication

Writing posture:

- still technical, but more momentum and staging
- stronger section openings
- higher narrative contrast between old and new

Visual profile:

- `launch-keynote`

Preferred skills:

- `engineering-practice-writer`
- `baoyu-slide-deck`
- `baoyu-cover-image`
- `baoyu-article-illustrator`

### `lively-explainer`

Use when:

- tutorials
- onboarding docs
- concept explainers
- broad audience education

Writing posture:

- teacherly
- clearer segmentation
- more examples and transitions
- easier cognitive load than `serious-engineering`

Visual profile:

- `lively-explainer`

Preferred skills:

- `engineering-practice-writer`
- `baoyu-article-illustrator`
- `baoyu-slide-deck`

Optional skill:

- `baoyu-comic` when a sequential teaching format would help

### `editorial-analytic`

Use when:

- trend analysis
- technical retrospectives
- ecosystem comparison
- research summaries
- topic-based research overviews with commentary

Writing posture:

- analytical, reflective, slightly editorial
- balances argument and evidence
- supports denser charts and commentary
- use `research-report` instead of plain `editorial-analytic` when the output should be a structured evaluation memo with first-pass SOP, scenario fit, pitfalls, and recommendations

Visual profile:

- `editorial-analytic`

Preferred skills:

- `engineering-practice-writer`
- `baoyu-infographic`
- `baoyu-slide-deck`
- `baoyu-article-illustrator`

### `comic-teaching`

Use when:

- the article teaches via sequence, analogy, or narrative beats
- character-based explanation would reduce complexity
- the user explicitly wants a comic or highly sequential explainer

Writing posture:

- scene-based
- concise beats
- dialogue-ready chunks
- educational, but more playful and memorable

Visual profile:

- `comic-teaching`

Preferred skills:

- `engineering-practice-writer`
- `baoyu-comic`

Optional skills:

- `baoyu-slide-deck` for a later talk version

## Recommendation Output Format

```text
Recommended theme: <theme>
Reason: <why it fits the article's content and intent>

Alternatives:
- <theme>: <short reason>
- <theme>: <short reason>
```
