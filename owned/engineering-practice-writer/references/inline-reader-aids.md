# Inline Reader Aids

Read this file when the user wants the article to become easier to understand by adding background, concept explanations, examples, best practices, or misconception handling near the relevant sections.

The goal is not to flatten the whole article into tutorial tone. The goal is to reduce local cognitive jumps while preserving the article's core posture.

## What To Add

Use one or more of these reader aids when the source needs them:

- `background-primer`
  - explain why the concept appears now, what earlier limitation or context made it relevant
- `concept-clarifier`
  - define the term in plain language, then relate it to the current section
- `example-or-analogy`
  - give one concrete intuition, contrast, or miniature example
- `best-practice-extension`
  - add one local engineering practice tied to the mechanism being discussed
- `misconception-or-boundary`
  - explain what the term does not mean, or where the current explanation stops being valid

## Placement Rules

- Prefer placing the aid at the first point where the reader would otherwise stumble.
- Use a short inline paragraph when one clarification sentence or one compact block is enough.
- Use a small subsection only when the concept is a real prerequisite for the next several paragraphs.
- Do not move all explanations to the front matter unless the whole article is fundamentally an onboarding explainer.
- Do not push all explanations to the appendix if the section will still be confusing without them.

## Recommended Expansion Pattern

For a dense mechanism term, prefer this order:

1. What it is, in plain language.
2. Why it matters in the current section.
3. How it works at a mechanism level.
4. One concrete intuition, example, or contrast.
5. One best practice, pitfall, or boundary note.

This can be one paragraph or a short cluster of paragraphs. The shape depends on how much context the reader needs.

## Example: `KV Cache`

Bad:

- `KV Cache 可以显著优化推理性能。`

Better:

- `这里先补一个上下文。大模型在生成回答时，并不是一次性把整段话全部算完，而是按 token 逐步往后生成。`
- `KV Cache 的作用，就是把前面已经算过的注意力 Key/Value 结果缓存下来。这样模型在继续生成后续 token 时，不需要把前缀内容重新完整计算一遍。`
- `放到 AI Coding 或 Agent 场景里，它直接影响长上下文任务的响应速度和成本。上下文越长，重复计算越多，没有 cache 的代价就越明显。`
- `实践上需要注意一点：KV Cache 提升的是“重复利用已有前缀”的效率，它并不会自动解决上下文选择错误、提示词布局混乱、或者无关信息过多的问题。`

This example is intentionally simple. When the article already assumes strong reader knowledge, compress it; when the article is based on slides or talks, expand it.

## Best-Practice Extensions

When the user asks for adjacent best practices, tie them to the current section's mechanism:

- If the section explains `KV Cache`, the adjacent practice can be about reducing unnecessary prefix churn, stabilizing prompt layout, or avoiding repeated context invalidation.
- If the section explains `Prompt Cache`, the adjacent practice can be about prompt template stability and shared prefix reuse.
- If the section explains `Harness Engineering`, the adjacent practice can be about giving the agent a stable validation loop, explicit tool surfaces, and traceable feedback.

Do not add a disconnected list of generic best practices that could fit any article.

## Boundaries

- Reader aids should clarify the current mechanism, not replace the article's main structure.
- Do not fabricate implementation details, metrics, or historical claims just to make the explanation feel richer.
- When the task is a bounded editorial pass on a mature document, keep the additions local and semantically conservative.
- If adjacent practice is added beyond the source, make it clearly compatible with the source instead of pretending it was explicitly stated there.
