# Flow Closure

Use one explicit closure note at the end of a pipeline run so the workspace records whether the current pass is complete, paused, or awaiting user review.

## Canonical File

Save the closure note as:

```text
notes/flow-closure.md
```

## Purpose

- make the current pipeline state unambiguous
- distinguish "finished for now" from "waiting on the next generation step"
- record what is completed, deferred, or still blocked

## Recommended Shape

```md
# Flow Closure

- status: paused-for-review
- article_status: working-draft-ready
- visual_status: placeholders-reviewed-pending-render
- deck_status: not-started
- export_status: not-requested

## Completed In This Pass

- Normalized source into workspace.
- Confirmed selection bundle.
- Produced working draft and reader-facing cleanup plan.
- Added Mermaid placeholders for the two priority visuals.

## Deferred

- Final image rendering
- Deck outline generation
- HTML export

## Waiting On

- User review of the article draft
- User approval of the diagram placeholders

## Next Recommended Action

- Review the article draft, then confirm whether to render the first comparison diagram.
```

## Status Values

- `completed`: the requested deliverables for this pass are done
- `paused-for-review`: the flow is waiting on user review or confirmation
- `paused-by-scope`: the requested scope was intentionally limited and the flow stopped cleanly
- `blocked`: the flow cannot continue until a missing dependency or decision is resolved

## Rules

- Do not end a pipeline pass without recording a closure state.
- The closure note should reflect the current pass, not the entire lifetime of the workspace.
- If the user requested only part of the full pipeline, `paused-by-scope` is valid and should not be treated as an error.
- If visual placeholders still need user review, prefer `status: paused-for-review`, `article_status: working-draft-ready`, and a non-final `export_status` such as `not-requested` or `deferred`.
- Do not mark the pass as fully `completed` just because a text draft exists when visual inventory or placeholder approval is still pending.
- If the user has accepted the chosen images, the article has been cleaned of review-only placeholders, and `exports/article-final.md` has been produced, `status: completed` is appropriate even if later optional deliverables such as deck or HTML remain deferred.
