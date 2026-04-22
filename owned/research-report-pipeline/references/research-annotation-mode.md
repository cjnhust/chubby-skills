# Research Annotation Mode

Read this file when the user wants a research report that stays structurally coherent as a report, but becomes easier to read through explicit annotations.

This is not a second parallel report. It is the same report spine with visible explanatory support.

## When To Use

Use annotated mode when the user asks for things like:

- 更好理解
- 批注版
- 术语解释版
- 带背景知识
- 保留主线但补注释

Especially good fits:

- concept-heavy AI / infrastructure reports
- project evaluations with many internal nouns
- framework / platform investigations where the verdict is easier than the mechanism
- reports whose early sections are likely to lose readers without local concept scaffolding

## What To Preserve

- the report thesis
- section spine
- top-level and major second-level headings
- the final recommendation structure

Annotated mode should make the report easier to read, not turn it into a new article with a different argument.

## Recommended Note Types

- `AI 批注｜概念理解`
  - what the concept is
  - a useful engineering analogy
  - the boundary of that analogy when needed
- `AI 批注｜背景补充`
  - why this concept matters in the report
  - what earlier context the reader may be missing
- `AI 批注｜适用边界`
  - where the technology fits
  - where the conclusion should not be overextended
- `AI 批注｜最佳实践`
  - local operator guidance
  - implementation or adoption advice
- `AI 批注｜常见误解`
  - when the concept is routinely misread or oversold

## Placement Rules

- Put the note immediately after the paragraph or bullet where the reader is most likely to stumble.
- Do not collect all notes into a giant appendix if local placement would be clearer.
- Keep notes compact; the report body is still the main narrative.

## Visual Rules

When the note needs a flow or structural picture:

- use one lightweight annotation figure near the note
- prefer Mermaid for:
  - architecture slices
  - request / control flow
  - evaluation structure
  - quickstart or SOP path
- treat the annotation figure as part of the report's visual plan; record it in `notes/visual-inventory.md`

## Example Pattern

```md
## 2. 这类框架到底在解决什么问题

<report paragraph>

> [!NOTE]
> AI 批注｜概念理解
> 可以先把它理解成一个“带任务编排能力的 Agent runtime”。
> 如果类比传统工程，它有点像把工作流引擎、工具调用层和状态管理层绑在一起。
> 这个类比只适合帮助理解职责范围，不代表它真的等同于某个固定工作流系统。

> [!TIP]
> AI 批注｜适用边界
> 如果你的场景以固定 SOP 为主，这类框架通常更容易发挥价值；
> 如果场景高度探索性而且工具面变化很大，框架本身的约束也可能成为负担。
```

## Guardrails

- Do not let annotations replace source-backed judgment.
- Do not use annotations to smuggle in unsupported conclusions.
- Do not rewrite the report spine just because some sections are hard to read.
- Keep the notes attached to the report's decision questions, not to random interesting facts.
