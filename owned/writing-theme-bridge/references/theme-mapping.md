# Theme to Writing Posture Mapping

This file defines the default mapping when `engineering-story-pipeline` has already selected a theme.

| Theme | Default Writing Posture |
|-------|--------------------------|
| `serious-engineering` | `serious-engineering` |
| `launch-narrative` | `launch-narrative` |
| `lively-explainer` | `lively-explainer` |
| `editorial-analytic` | `editorial-analytic` |
| `comic-teaching` | `comic-teaching` |

## Special Case

- When the selected theme is `serious-engineering` but the article is an RFC, architecture proposal, or review-oriented design document, prefer `rfc-document` as the writing posture.
- When the selected theme is `serious-engineering` but the article is clearly an evidence-led evaluation, selection report, migration/adoption assessment, or bounded research memo, prefer `research-report` as the writing posture.
- When the selected theme is `serious-engineering` but the article is clearly a personal or team practice retrospective, a technical sharing draft, or a “我如何把 X 做成 Y” style piece, prefer `practice-sharing` as the writing posture.
- When the selected theme is `editorial-analytic` but the output should read like a structured evaluation memo with explicit evidence boundary, first-pass SOP, fit scenarios, pitfalls, and bounded recommendations, prefer `research-report` as the writing posture.

## Override Rule

The theme sets the default writing posture, but the user may override it when:

- they want a less formal or more formal treatment
- the same topic will be turned into different deliverables
- they provide a strong exemplar that clearly implies a different posture
