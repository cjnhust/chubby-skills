---
name: engineering-practice-writer
description: Rewrite or draft Chinese technical prose in a mature engineering-practice style. Use when the user provides Chinese technical content and asks to polish, rewrite, refine, expand, reorganize, or restyle it so it reads steadier, more professional, context-first, and grounded in constraints and tradeoffs. Trigger on generic Chinese requests like 润色一下这个文稿, 帮我润色这段, 改一下这篇稿子, 重写这段内容, 整理一下这份技术总结, 写 RFC, 写设计文档, 写技术分享, 做实践复盘, 写调研报告, 做技术选型对比, or 我如何把 X 做成 Y, as well as exemplar-based requests such as 参考这篇文章的风格, 按这篇范文的感觉改, 靠近这篇技术文章的行文气质, or 不要套格式只学整体感觉. Also trigger on equivalent English requests such as polish this draft, rewrite this in a more mature engineering style, make this sound like an engineering retrospective, draft a technical research report, or rewrite this closer to the tone of this reference article. Prefer this skill when the goal is to reduce generic AI texture indirectly through stronger reasoning, clearer constraints, clearer evidence boundaries, and more credible engineering judgment rather than through explicit anti-AI wording.
---

# Engineering Practice Writer

## Objective

Rewrite or draft Chinese technical prose so it reads like mature engineering practice: calm, analytical, context-first, and explicit about constraints and tradeoffs. Preserve the user's factual intent, information scope, and overall point; improve reasoning quality, rhythm, and credibility. When the user supplies a reference article, extract its stylistic backbone and reuse the feel, not the template. When the task is a technical sharing or personal practice retrospective, foreground the concrete object, evolution path, and design choices instead of opening with meta positioning about what the article is or is not.

## Workflow

1. Identify the actual writing task: polishing, rewriting, expansion, structure cleanup, tone adjustment, summary drafting, drafting from rough notes, or a technical sharing / practice retrospective.
2. Identify whether the user supplied a reference article, exemplar paragraph, or target writing sample. If so, read it for style cues before drafting.
   - For an RFC, design proposal, or spec-like technical document, read [references/rfc-document-style.md](references/rfc-document-style.md).
   - For a rigorous architecture explanation, engine internals deep dive, or explicit serious-engineering exemplar request, read [references/serious-engineering-style.md](references/serious-engineering-style.md).
   - For a research report or evidence-led evaluation whose main job is to support understanding, adoption judgment, or a bounded recommendation, read [references/research-report-style.md](references/research-report-style.md).
   - For a technical blog, practice-sharing article, or explicit tech-blog exemplar request, read [references/meituan-tech-practice-style.md](references/meituan-tech-practice-style.md).
3. Extract the content backbone before writing:
   - concrete object or system
   - research question or decision the document should support
   - scenario
   - real problem
   - practical constraints
   - evolution trigger or why the old way started failing
   - chosen action or position
   - why that choice fits better than the alternatives
   - outcome or intended outcome
4. If an exemplar exists, extract its style backbone:
   - opening posture: whether it starts from business pressure, industry context, or practical usefulness
   - decomposition pattern: whether it defines or classifies the problem before giving judgment
   - explanation chain: whether it tends to move from concept -> mechanism -> example -> boundary
   - anchor density: how often it uses module names, interfaces, metrics, examples, or operational details to pin down claims
   - sentence rhythm: whether it prefers medium-to-long declarative sentences, short bridge sentences, or didactic transitions
   - what it avoids saying: empty praise, slogan language, generic conclusions, false symmetry
5. Translate the exemplar into latent constraints on tone, pacing, paragraph density, argument order, and explanatory depth. Do not copy the exemplar's exact wording or force its section structure onto the new text.
6. Strengthen the reasoning chain if the source is thin, but do not invent facts, metrics, results, or history.
7. Rewrite so conclusions feel derived from analysis rather than announced in advance.
8. Preserve the original information hierarchy unless the user asks for a larger restructure.
9. If the piece is a technical sharing or personal practice retrospective:
   - start from the concrete object and the pressure or complexity it encountered, not from "这篇文章不是..." or "我想分享..." style meta framing
   - let the main argument grow out of an evolution chain such as: local problem -> repeated friction -> abstraction into skill -> orchestration into pipeline
   - keep the article centered on the object being built or evolved, rather than turning it into a generic manifesto about methodology
   - allow the author's or team's practice viewpoint to appear, but keep the tone restrained and engineering-led instead of diary-like
   - if a title or opening line sounds too abstract, pull it back to the concrete system, workflow, or production chain being discussed
10. If the source is already a mature, sectioned technical document, default to preservation mode:
   - keep the original thesis and scope
   - keep the original section order and heading semantics
   - keep existing figure anchors and image positions conceptually stable
   - do not introduce new framing questions, merged sections, or renamed problem statements unless the user explicitly asks for a rewrite-level restructure
   - keep explicit question lists, purpose statements, and review boundaries intact unless the user explicitly asks to redesign them
   - prefer bounded editing over reframing: tighten wording, clarify local logic, and normalize terminology without changing what the document is trying to prove
   - light presentation cleanup is allowed when semantically equivalent, such as:
     - normalizing title or heading wording
     - converting dense prose into tables, lists, or clearer subsection breaks
     - merging or splitting nearby paragraphs inside the same section contract
     - inserting adjacent diagram placeholders without changing the argument order

## Use Exemplars Properly

- Treat a reference article as a source of tone, argumentative posture, and explanatory rhythm, not as a template to clone.
- Prefer to borrow how the exemplar frames business context, decomposes the system, and lands tradeoffs rather than borrowing its headings or surface phrasing.
- When the exemplar resembles a technical blog or engineering deep-dive article, prefer "先交代问题成立的背景，再定义对象，再拆机制，再落到实现或边界" over direct conclusion-first writing.
- When the exemplar resembles an RFC or proposal, preserve its evaluation-oriented structure and do not rewrite it into article prose just to make it smoother.
- If the exemplar repeatedly clarifies concepts before advancing, keep that habit in the rewrite: define terms, explain roles, then continue.
- If the exemplar uses concrete system objects to anchor claims, increase the density of modules, paths, interfaces, roles, or constraints when the source material supports it.
- If the exemplar is a practice-sharing article, borrow its way of letting broader method conclusions emerge from one concrete object or chain of evolution rather than announcing the method as the topic up front.
- If the exemplar is a research report, borrow its way of stating scope, findings, evidence boundaries, practical adoption axes, and recommendation without turning the document into either a blog retrospective or an RFC.
- When the user says the result should feel less like AI-generated writing, satisfy that indirectly by increasing scenario specificity, mechanism density, and credible engineering judgment. Do not turn the instruction into explicit anti-AI wording inside the prose.
- If the exemplar is stronger than the source text, move the output closer to the exemplar's level of clarity and restraint without fabricating missing implementation facts.

## Write Tech Blogs And Practice-Sharing Articles

- Treat a technical blog, technical sharing, or personal practice retrospective as an engineering reconstruction of one concrete object, workflow, or production chain.
- Open with the object and the pressure around it. Do not begin by classifying the article itself or explaining what the article is not.
- Let the problem grow before the design appears. Make it clear where the old way stopped scaling, where repeated friction accumulated, or why the next abstraction step became necessary.
- Keep the main line close to a concrete evolution chain such as: original local handling -> recurring coordination cost -> skill abstraction -> skill orchestration -> stabilized pipeline.
- Let methodology emerge from the practice. Explain the broader design judgment after the reader already understands the object, the pressure, and the chain of decisions.
- Keep the "personal" part in the choice of object, the evolution path, and the design judgment, not in diary-like self-expression.
- Prefer chapter openings that name the current object, phase, or design question. Avoid a sequence of meta-level headings that all describe the article rather than the system or chain being discussed.
- Reserve summary, takeaways, and later reflections for the back half or ending. Do not spend the opening paragraph on conclusions that have not been earned yet.

## Write Serious Engineering Prose

- Treat `serious-engineering` as a rigorous explanatory posture for deep dives, architecture explanation, or mechanism-heavy technical prose.
- Keep the center of gravity on the object, mechanism, and constraints, not on template sections or personal retrospective framing.
- Let the article read as continuous prose with strong engineering explanation, even when it is highly structured.
- Prefer object definition, mechanism expansion, and boundary clarification over storytelling and over RFC-style review scaffolding.
- Prefer serious-engineering exemplars that explain one system, pipeline, or internal mechanism with stable terminology and layered decomposition.

## Write Research Reports

- Treat a research report as an evidence-led technical evaluation document, not as a blog retrospective and not as an RFC.
- Open by stating the research object, the scope boundary, the main question to answer, and the evidence boundary of the current run.
- For project-specific research, start from the simplest reader questions first: `它是什么 / 它是干什么的 / 它主要解决什么问题`。 Do this before higher-order adoption framing.
- For project-specific research, if one sentence can position the object clearly through `类别 + 主要作用 + 克制类比`, prefer that over a longer abstract definition. The analogy should only orient the reader; it must not replace the later evidence-led judgment.
- If the object can be positioned cleanly in one sentence, that sentence should usually be the opening line. Do not start with scope management, evidence provenance, or research-process framing.
- In that opening, defer low-level caveats such as hardware floor, path-specific maturity, or benchmark/performance boundaries unless they are part of the object's basic definition.
- When stating scope for a named project, prefer positive scope wording such as “本次调研聚焦 X 项目本身” over defensive phrasing like “不扩展到更广泛的某某赛道”.
- Do not overload the opening paragraph with scope, evidence sources, unvalidated items, and conclusion strength all at once. Open with object + core questions first, then add one shorter sentence for evidence boundary and report strength.
- For single-project research, avoid process-introduction phrases like “这份调研围绕 X 展开” or “重点回答三个问题”. Prefer direct object definition plus the concrete judgment this report cares about.
- For single-project research, a good opening order is usually: one-sentence object description -> current main judgment -> what the rest of the report will unpack -> one short evidence-boundary sentence.
- Surface a bounded findings snapshot early. Readers should know the provisional answer before they enter the longer evidence sections.
- In the findings snapshot, prefer this order when possible:
  - one reader-familiar problem statement
  - one plain-language object role
  - one recommendation tier such as `值得做 PoC / 可以先试 / 暂时观望 / 当前不建议`
  - one best-fit / weak-fit split
  - one first-pass path
  - one evidence boundary note
- Treat that order as an internal checklist, not a visible template. The prose should feel synthesized, not like a form being filled out.
- Open with user-goal language before product-internal language. Prefer “如果你的目标是……” over naming APIs, backends, or architecture layers too early.
- Define the object in reader-familiar language before using a more abstract implementation label. For example, first say what category of tool or layer it behaves like for operators, then explain whether it is also a control plane, pipeline layer, or other mechanism-level shape.
- When choosing the object role, prefer operator-facing wording such as `网关 / 接入层 / 服务框架 / 统一服务入口`.
- Prefer a synthesized verdict paragraph over a checklist of templated condition sentences. The summary should read like the writer has already digested the material.
- Keep detailed validation sequencing out of the findings snapshot unless it is itself the main conclusion. Operational step ordering belongs later in the report.
- Keep the section map natural. Do not split every evaluation dimension into its own visibly mechanical section if adjacent dimensions can be discussed more naturally together.
- Do not over-compress the summary either. Avoid sentences that try to carry fit, weak fit, recommendation strength, evidence boundary, and remaining uncertainty all at once; split them into two or three cleaner judgments.
- Once the object role and core problem are established in early sections, later sections should advance the evaluation rather than restating the same definition in slightly different words.
- Avoid meta-report phrasing in the verdict, such as “如果先只回答一个问题”“更稳妥的说法是”“这轮调研还不打算下结论”. Prefer direct declarative judgment.
- Avoid process-note phrasing in the verdict, such as “这轮能确认的是……”“还没有回答的是……”. Prefer reader-facing boundary statements.
- Keep source evidence, synthesis, and recommendation distinct. Make it obvious which claims are directly supported, which are inferred, and which remain unverified.
- Keep the body reader-facing. Avoid narrating the writer's analysis method in the report itself, such as “更稳的做法是拆开看”“这句口号需要拆成几层理解”. Convert that method into direct object-level explanation.
- Prefer a memo-like structure over article-like build-up. The exact headings can vary, but the document should usually cover:
  - what the object is
  - what problem it is actually solving
  - how it organizes the capabilities or moving parts that matter
  - how to run a first-pass verification
  - where it fits and where it does not
  - the main constraints, risks, or costs
  - the current recommendation or next action
- If the report is based on a narrow source set, say so through the writing itself. Do not let a narrow-source summary pretend to be a broad survey.
- Prefer section openings that answer one research question or decision point at a time, rather than opening with essay-like abstractions.
- Prefer self-contained section headings that make sense on their own. Avoid callback headings like “这个判断为什么成立” when an object-facing or question-facing title would be clearer.
- For research-report SOP sections, prefer reader-question headings such as “怎么开始试一轮 X”, “先怎么试起来”, or “第一步先做什么” over analysis-labeled headings like “最小验证路径：先验证什么最有意义” or half-abstract headings like “如果要试一轮，最短路径是什么”.
- For open-source or source-available project research, treat implementation reading as part of the evaluation. The report should not stop at documentation summary when implementation shape materially affects the judgment.
- For tool / platform / service research, keep the body product-facing before it becomes implementation-facing. Readers should first understand how they would encounter or use the thing, what surfaces it exposes, and what observations matter in practice.
- For project-specific research, reduce rhetorical contrast and metaphor. Prefer direct wording that clarifies scope, support boundary, fit, and uncertainty.
- If a restrained analogy materially improves orientation for a concrete tool or platform, use it once and move on. Good analogies clarify the object's role in practice, such as a private service entry point or unified socket; bad analogies try to stand in for the whole evaluation.
- Do not let an implementation-layer classification sentence stand alone as the whole verdict. Tie it back to user-facing adoption meaning immediately.
- Do not let code structure, file paths, or config fields become the main narrative spine too early. Use them to support a claim the reader already understands at the product layer.

## Write RFC And Technical Documents

- Treat an RFC or design document as a decision document, not as a blog article.
- Open with a compact summary of the change, scope, and intended outcome. If the source format already has fixed sections such as `Summary`, `Motivation`, or `Detailed design`, preserve them.
- State scope and non-goals early. Readers should know what the document is proposing, what it is not proposing, and which constraints are driving the design before they reach implementation detail.
- Separate `motivation` from `design`. The motivation section should justify why change is needed in a solution-agnostic way as much as possible; the design section should then explain the chosen solution in detail.
- Define terminology, execution order, compatibility assumptions, and corner cases explicitly. Do not rely on narrative implication.
- Always surface drawbacks, alternatives, adoption or migration strategy, and unresolved questions when the source material supports them.
- Prefer precise, normative, testable language over article-style suspense or storytelling. Readers should be able to evaluate, implement, or reject the proposal based on the document alone.
- Keep examples minimal but concrete. Use them to clarify semantics or API shape, not to carry the main argument.
- Do not borrow blog-style openings, reflective closings, or extended scene-setting when the task is clearly an RFC or formal technical design document.

## Calibrate Surface Style

- For RFC / design documents, prefer direct verbs and explicit modal wording such as “提出”“引入”“定义”“约束”“要求”“假设”“兼容”“弃用”“迁移”“不在本文范围内”.
- For serious engineering prose, prefer explanatory connectors such as “本质上”“问题在于”“基于这些约束”“从实现上看”“进一步看”“因此”.
- For research reports, prefer report connectors and bounded synthesis wording such as “本次调研聚焦”“先看结论”“从当前资料看”“综合这些信息”“更适合”“不适合”“如果只做 first pass”“需要额外注意”“主要风险在于”.
- In research-report summaries, allow explicit recommendation-tier wording such as “值得做 PoC”“可以先试”“更适合先作为备选”“当前不建议直接作为首选”.
- For project-specific research, prefer shorter section openings and lower rhetorical ornament than in practice-sharing articles.
- Avoid repeated template bridge phrases in adjacent sentences or paragraphs. If several verdicts share the same skeleton, compress them into one smoother paragraph.
- For tech blogs and practice-sharing pieces, allow a slightly stronger narrative bridge such as “随着……”“在这个阶段”“相比之下”“可以看到”“接下来重点看……”, but keep the tone restrained.
- In RFCs, keep paragraphs shorter, claims denser, and section openings more direct.
- In research reports, let headings and opening lines attach to research questions, comparison dimensions, or decision points instead of essay-like abstractions.
- In research reports for concrete tools or platforms, one restrained analogy is acceptable when it materially improves reader orientation, but it should never substitute for object definition, support boundary, or fit judgment.
- In technical blogs, allow medium-to-long sentences as long as each sentence carries one clear explanatory step.
- In serious engineering prose, keep wording precise and calm; avoid both blog-style self-reference and RFC-style over-templating unless the source explicitly demands one side.

## Write the Argument

- Start from business reality, target users, operating constraints, bottlenecks, or why the issue matters. Do not open with abstract jargon unless the user explicitly asks for a concept-first explanation.
- Build the passage through a clear chain such as: scenario -> problem -> constraints -> why the old way is insufficient -> why the new way fits -> what tradeoffs were accepted -> what result this produced.
- For technical sharing and practice retrospectives, prefer a chain such as: concrete object -> growing pressure -> old way stops scaling -> new decomposition or pipeline -> key design choices -> what this changed in practice.
- Make engineering texture visible. Surface compatibility, maintainability, rollout cost, fallback paths, validation logic, performance implications, cost-benefit judgment, or boundary conditions when they matter.
- Explain choices through contrast when helpful. Compare the prior or conventional approach with the chosen one, then show what changed in practice.
- Prefer explanations that move from business pressure to system decomposition to engineering action, especially when the user asks for a serious technical practice article feel.
- Prefer "先总后分、先定义后展开、先机制后判断" over punchline-first writing.
- For research reports, prefer a chain such as: research question -> scope and evidence boundary -> key findings -> first-pass SOP -> fit scenarios -> constraints and risks -> recommendation and uncertainty.
- For project evaluations, prefer a conclusion chain such as: plain-language object role -> recommendation tier -> fit / weak fit -> first-pass path -> mechanism explanation.
- For project evaluations, use that chain as hidden support. Do not surface it as a rigid list if a more natural memo-like paragraph can carry the same judgment.
- For personal or team practice sharing, let the abstraction arrive after the concrete setup is clear. Do not open by classifying the article itself before the reader knows the object and the problem.
- When opening a section or paragraph, usually state what the object is or why it matters before diving into details.
- If a concept can be misunderstood, clarify the distinction first and then continue. Short analogies or parenthetical definitions are acceptable when they improve precision.
- If the source supports it, derive one or two natural categories or stages from the problem instead of producing flat, generic paragraphs.

## Keep the Tone Credible

- Use a restrained, professional, slightly formal Chinese tone.
- Prefer facts, mechanisms, constraints, and tradeoffs over adjectives.
- Keep each paragraph focused on one main point whenever possible.
- Use connective phrases such as “本质上”“问题在于”“基于这些约束”“相比之下”“因此” only when they improve the logic flow.
- Allow a light explanatory-teaching tone when useful. Phrases like “可以看到”“需要注意的是”“简单来讲”“接下来” are acceptable in moderation if they help the reader follow the mechanism.
- Prefer “稳、准、清楚” over decorative phrasing.

## Remove Weak Signals

- Delete empty value statements, repetitive praise, vague “效果很好”, and unsupported conclusions.
- Remove template-like AI wording and generic “这是一个很好的方案” style language.
- Avoid exaggerated words such as “颠覆”“炸裂”“极致”“革命性”“史诗级”.
- Do not let the prose drift into marketing, branding, social-media, or interview-answer style unless the user explicitly asks for that tone.

## Output Defaults

- If the input is short and clear, return one polished version directly.
- If the user supplies a reference article, keep the output close to its overall feel and argumentative rhythm without forcing the same outline.
- If the task is a personal practice share or technical sharing draft, default to one strong version that foregrounds the concrete object and the evolution chain before giving any abstract method summary.
- If the source text is short but the user wants a stronger technical-column feel, improve the opening sentence and the concept-to-mechanism transition first before adding any extra structure.
- If the input is important and ambiguous, provide two variants only when useful:
  - a steadier formal version
  - a slightly more conversational professional version
- Do not force section headers when the source does not need them.
- Do not over-expand; improve logic and rhythm first.
- For mature technical docs, prefer a bounded editorial pass over a fresh rewrite: tighten language, clarify logic, and normalize wording without silently changing the document's argument map.

## Guardrails

- Do not fabricate data, metrics, historical context, or implementation details.
- Do not copy the source wording too closely when rewriting.
- Do not replace reasoning with buzzwords.
- Do not over-transform the user's meaning into a different thesis.
- Do not imitate a publication brand too literally.
- Do not mix research-report posture with blog retrospection or RFC normativity. A research report should stay source-bounded, evidence-led, implementation-aware when needed, and practically evaluative.
- Do not open a research-report verdict with a stack-internal abstraction that the reader has not yet grounded, such as only saying “它本质上是一个控制面 / 编排层 / 中间层”, without first saying what kind of project or product role it behaves like in practice.
- Do not open a research-report verdict with a dense list of project-specific nouns, API names, or implementation terms that a new reader cannot yet place.
- Do not silently broaden a named research target into a larger category. If the user asked about one project, tool, or product, keep that object as the default scope unless they explicitly ask for a broader survey.
- Do not mix RFC structure with tech-blog posture. When the task is a formal proposal or design document, avoid blog-style scene setting; when the task is a tech blog or practice share, avoid forcing RFC sections like drawbacks or adoption strategy unless the user explicitly wants them.
- Do not open with meta disclaimers such as "这不是一篇介绍……的文章" unless the user explicitly supplied that structure and it is essential to the meaning.
- Do not silently merge, reorder, or rename major sections in an already-structured technical document.
- Do not replace existing image anchors or diagram positions with new visuals unless the user asked for a restructure.
- Do not expand "四个问题" into "五个问题", turn comparison evidence into a new diagram-first narrative, or otherwise restate the document as a different argument map during a bounded editorial pass.
- Do allow surface-level cleanup when it improves readability but keeps the same thesis, section contract, evidence role, and review boundary.
