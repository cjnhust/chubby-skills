# Writing Postures

Choose the writing posture from article content and communication intent before drafting.

## `serious-engineering`

Use when:

- technical deep dives where rigor matters more than drama
- formal engineering explanation that is neither a strict RFC nor a blog-style practice share
- mechanism-heavy articles that still read like prose rather than template-driven documents

Drafting behavior:

- use `engineering-practice-writer` directly
- business context, constraints, and tradeoffs first
- mechanism-heavy explanation
- restrained tone
- minimal rhetorical flourish
- keep prose continuity; do not force RFC template sections
- keep explanation first; do not lean on personal retrospective framing

Boundary:

- choose `serious-engineering` when the document should read like a rigorous technical article, deep-dive memo, or architecture explanation
- choose `rfc-document` when the document is primarily for proposal review, implementation alignment, specification, or migration decision-making
- choose `research-report` when the document should help the reader evaluate, try, or adopt a technology based on explicit sources, scenarios, pitfalls, and recommendations
- choose `practice-sharing` when the article is centered on one concrete evolution path, blog-style experience reconstruction, or personal/team practice
- the current Meituan technical-blog exemplar set belongs to `practice-sharing`, not to `serious-engineering`

## `research-report`

Use when:

- technical research reports
- technology selection reports
- URL/topic-based Chinese survey reports
- evidence-led technical synthesis that should end in practical guidance
- bounded evaluation work where readers need to decide whether and how to try, assess, or adopt the object

Drafting behavior:

- state object, scope, main question, and source boundary early
- give a bounded findings snapshot relatively early
- separate source evidence, synthesis, and recommendation
- include a first-pass SOP when the source supports it
- explicitly cover fit scenarios, non-fit scenarios, common pitfalls, costs, and operational constraints when relevant
- keep uncertainty, missing evidence, and source bias visible
- for open-source or source-available projects, treat implementation reading as part of the evaluation when it materially affects the judgment

Boundary:

- choose `research-report` when the document is primarily helping the reader understand, evaluate, or adopt an object under an explicit evidence boundary
- choose `editorial-analytic` when the document is more commentary-driven, trend-oriented, or comparative in a broader ecosystem sense
- choose `serious-engineering` when the document mainly explains how one system or mechanism works
- choose `rfc-document` when the document is proposing an internal change and must support review and implementation alignment

## `rfc-document`

Use when:

- RFCs
- architecture proposals
- design docs meant for review, alignment, or implementation
- spec-like documents where scope, semantics, and rollout must be explicit

Drafting behavior:

- start with summary, scope, and intended outcome
- separate motivation from detailed design
- make terminology, semantics, edge cases, and compatibility assumptions explicit
- include drawbacks, alternatives, and adoption or migration strategy when the source supports them
- prefer precise, review-friendly, testable language over narrative buildup

## `practice-sharing`

Use when:

- technical blogs
- personal technical practice sharing
- team experience retrospectives
- "我如何把 X 做成 Y" style engineering articles
- technical sharing drafts where one concrete object or workflow is the narrative center

Drafting behavior:

- start from the concrete object and the pressure around it
- explain how the problem grew before explaining the final design
- let abstraction emerge from one real chain of evolution
- keep a restrained practice voice rather than meta article framing
- preserve engineering detail, tradeoffs, and boundary conditions
- keep section openings attached to the object, phase, or design question being discussed
- move summary and methodology extraction behind the concrete chain rather than in front of it

## `launch-narrative`

Use when:

- release docs
- framework launch notes
- roadmap communication
- version storytelling with "what changed" and "why now"

Drafting behavior:

- start from the shift or pressure that made the release necessary
- create stronger section openings and transitions
- emphasize old vs new contrast more clearly
- keep technical rigor, but allow more momentum and stage presence
- avoid marketing hype and slogan language

## `lively-explainer`

Use when:

- tutorials
- onboarding docs
- concept explainers
- broad audience technical education

Drafting behavior:

- lower cognitive load
- break concepts into clearer steps
- add more examples and bridge sentences
- sound teacherly rather than institutional
- remain technically correct without becoming dry

## `editorial-analytic`

Use when:

- retrospectives
- ecosystem comparisons
- trend analysis
- research summaries with commentary

Drafting behavior:

- alternate evidence and interpretation more explicitly
- allow a slightly more editorial opening posture
- compare competing explanations or approaches
- keep claims anchored to facts and examples
- sound thoughtful, not opinionated for its own sake
- do not default to `editorial-analytic` when the reader mainly needs a structured adoption report with SOP, scenarios, pitfalls, and recommendation

## `comic-teaching`

Use when:

- knowledge should be delivered as sequence or scenes
- analogy and progressive reveal help comprehension
- later comic adaptation is likely

Drafting behavior:

- restructure into scene-ready beats
- use shorter conceptual units
- make transitions panel-friendly
- keep language clear enough to become captions or dialogue later
- do not turn the article into casual banter unless the user wants that

## Recommendation Output Format

```text
Recommended writing posture: <posture>
Reason: <why it fits the article>

Alternatives:
- <posture>: <short reason>
- <posture>: <short reason>
```
