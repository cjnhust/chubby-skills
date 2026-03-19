# Style Profiles

Choose profiles mainly from article content, argument posture, and reader experience, not from deliverable type alone.

## Selection Signals

Look at these content signals first:

- Is the article mainly about architecture, constraints, tradeoffs, and systems?
- Is it a release, launch, or directional announcement?
- Is it a tutorial, onboarding guide, or concept explainer?
- Is it benchmark-heavy, data-heavy, or research-summary-like?
- Is the tone restrained and serious, or energetic and audience-expanding?

## Profiles

### `serious-engineering`

Use when:

- architecture notes
- RFCs
- design proposals
- deep technical explainers
- migration plans
- benchmark or performance analysis with engineering authority

Signals:

- high rigor
- strong tradeoff discussion
- lots of module names, APIs, or constraints
- visuals should feel structural and exact

Visual posture:

- dark engineering minimalism
- strict grid
- flat 2D or wireframe diagrams
- orange accent used sparingly

Prompt cues:

- matte charcoal background
- gray-white body text
- orange only on focal path or changed module
- avoid scene-building and decorative metaphors unless the cover truly needs one

Primary reference:

- `$CODEX_HOME/skills/engineering-story-pipeline/references/visual-system.md`

### `launch-keynote`

Use when:

- release storytelling
- framework launch
- major version introduction
- roadmap or strategy talk

Signals:

- narrative momentum matters
- still technical, but with more stage presence
- cover and ending slides should feel poster-like

Visual posture:

- high contrast
- stronger headline hierarchy
- more dramatic poster composition
- still restrained, but with more visual momentum than `serious-engineering`

Prompt cues:

- stronger title scale
- bolder cover and ending slides
- cleaner, sharper stage-like compositions
- diagrams still remain structured, not flashy

### `lively-explainer`

Use when:

- tutorials
- onboarding docs
- concept explainers
- audience expansion pieces

Signals:

- article teaches more than it argues
- readability and approachability matter more than authority signaling
- diagrams can be friendlier, but should still stay clean

Visual posture:

- lighter emotional temperature
- cleaner explanatory segmentation
- less austere than `serious-engineering`
- still avoid gimmicks and visual noise

Prompt cues:

- more approachable spacing
- friendlier explanatory blocks
- clearer step-by-step emphasis
- diagrams may be slightly softer, but still flat and controlled

### `editorial-analytic`

Use when:

- research summary
- trend analysis
- ecosystem comparison
- technical retrospective with strong narrative framing

Signals:

- more editorial than tutorial
- medium to high data density
- argument benefits from diagram plus commentary balance

Visual posture:

- structured but more magazine-like
- strong typography
- clean chart language
- balanced density without playful cues

Prompt cues:

- typography-led layouts
- editorial sectioning
- clean chart-first framing
- diagrams should read like analytical exhibits, not classroom visuals

### `comic-teaching`

Use when:

- sequential storytelling makes the concept easier to learn
- the article naturally breaks into scenes or beats
- the user wants memorable teaching rather than report-like reading

Signals:

- explanation benefits from characters, analogy, or scenario progression
- the content is teachable through stepwise reveals
- educational retention matters more than institutional seriousness

Visual posture:

- comic panels
- controlled expressiveness
- educational clarity over pure spectacle
- memorable beats without losing factual precision

Prompt cues:

- panel-by-panel clarity
- stable character roles
- instructional beats
- no random comedic noise that distorts the technical point

## Recommendation Output Format

When recommending, present:

- `Recommended`: profile name + 1 short reason
- `Alternatives`: 2-3 profile names + 1 short reason each

Example:

```text
Recommended: serious-engineering
Reason: 这篇稿子核心在于架构约束、模块关系和设计取舍，视觉应优先服务结构清晰度，而不是情绪感染力。

Alternatives:
- launch-keynote: 如果你希望更像发布会分享而不是 RFC，封面和结尾会更有舞台感。
- editorial-analytic: 如果你想强化“行业分析/方法论复盘”的阅读感，可以选这个。
```
