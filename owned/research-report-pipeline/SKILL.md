---
name: research-report-pipeline
description: Orchestrate topic-based or URL-based Chinese technical research reports by confirming scope before expansion, collecting primary sources, building a source catalog and evidence matrix, then routing the final writing through writing-theme-bridge and engineering-practice-writer with the research-report posture. Use when the user asks for 调研报告, 技术选型报告, 方案对比, 基于 URL/主题的中文研究报告, benchmark summary, migration survey, or any report that should answer what the technology is, how to run a minimal SOP, what scenarios it fits, what pitfalls matter, and what recommendation follows.
---

# Research Report Pipeline

Use this skill when the user wants a research report rather than a plain article rewrite.

This skill is the upstream orchestrator for research-like work. It owns:

- topic scope confirmation before research expands
- source collection and source boundary control
- report-mode inference and thesis selection before drafting
- selective source-code verification for source-available projects when key claims materially affect adoption judgment
- research questions and evidence synthesis
- report-specific artifacts such as source catalog and evidence matrix
- final fact-check against claimed capabilities and support boundaries
- working-draft versus final-export distinction
- report diagrams and their canonical structure source
- first-pass report visual generation and review
- optional annotated-edition planning for concept-heavy reports
- handoff into the writing layer once the report skeleton is justified

It does not replace `writing-theme-bridge`, `engineering-practice-writer`, or visual leaf skills. It prepares the report workspace so those later steps have explicit inputs.

## When To Prefer This Skill

Use `research-report-pipeline` instead of jumping straight into `engineering-story-pipeline` when the request starts from:

- a short topic
- one or more URLs
- a named project / product / library to investigate
- a technology choice the user wants evaluated
- a benchmark, migration, or adoption question that needs explicit sources and recommendations

If the request is already a finished draft that only needs rewriting, stay with `engineering-story-pipeline` or `engineering-practice-writer`.

## Execution Contract

- When this skill triggers, the default behavior is to execute the full research flow end to end. Do not reinterpret a short request such as `调研下 X`, `看看 X`, `研究下 X`, or `分析 X` as permission to return a quick summary or an instant verdict.
- Do not switch from `research-report-pipeline` to an ad hoc “fast answer” mode just because the topic seems simple, the repo looks readable, or an old workspace already exists.
- If the topic is still ambiguous across multiple plausible objects, the run must stop at scope confirmation. Discovery notes are allowed, but `notes/report-thesis.md`, `drafts/report.md`, and any conclusion-oriented final answer are blocked until `source/source.md` records `- scope_status: confirmed`.
- If a matching workspace already exists, treat it as reusable scaffolding, not as proof that the report is already complete. Re-check scope, refresh source freshness where needed, update `source/source-catalog.md`, and rewrite `notes/fact-check.md` and `notes/flow-closure.md` for the current run before treating the workspace as current.
- If the report is source-available or open-source, selective code verification is part of the mandatory path, not an enhancement.
- If the request includes one or more concrete URLs that materially affect the report, content-family capture is an artifact gate, not a writing suggestion. Such URLs may not be treated as evidence-bearing primary sources until `source/source-catalog.md` records either capture artifacts or an explicit capture failure.
- A final answer may summarize the report outcome only after the required workspace artifacts and gates for this skill have been satisfied. Before that point, the skill is still in progress.
- If a hard blocker prevents completion, report the blocker explicitly and name the blocked artifact or gate. Do not silently downgrade the request into a polished summary, “quick notes”, or an apparently final research conclusion.

## Workflow

1. Confirm the research object before broadening.
   - If the user gives a short topic, determine whether it refers to:
     - one specific project or product
     - a broader category
     - a comparison set
     - an intentionally open survey area
   - If a named target can plausibly mean both a project and a broader category, default to the exact named target and confirm before expanding.
   - Do not broaden “project X” into “the whole X category” without explicit confirmation.
   - Record the scope state in `source/source.md` with `- scope_status: ambiguous | confirmed`.
   - If the scope is still ambiguous, record the candidate interpretations and stop before thesis-writing or reader-facing drafting.
   - Record the confirmed scope in `source/source.md`.

2. Build a research workspace.
   - Read `references/research-workspace.md`.
   - Prefer `scripts/init-workspace.js --topic <topic> --workspace <dir>` for deterministic workspace creation.
   - Preflight the JS runtime before calling helper scripts. Do not trust the agent wrapper shell's `PATH` by itself. First check whether the command is available in the user's actual `zsh` environment; only after that should you conclude installation is required. Prefer `node`; if `node` is unavailable but `bun` is available, `bun` is an acceptable fallback for these local helper scripts.
   - Create one workspace per report.
   - If the target workspace already exists, do not treat old report artifacts as current by default. Refresh the workspace state for the current pass and make sure any reused conclusions are re-grounded in current `source/` and `notes/` artifacts.
   - If `source/source.md` still says `scope_status: ambiguous`, keep the workspace in discovery mode. Do not create or refresh `notes/report-thesis.md` or `drafts/report.md` as if the report were already scoped.
   - Keep all source discovery, evidence notes, and drafts inside that workspace.

3. Collect primary sources.
   - Prefer official docs, repos, model cards, system cards, RFCs, product docs, or first-party blogs.
   - If the request includes one or more concrete URLs that will materially affect the report, capturing those URLs through `baoyu-url-to-markdown` or `baoyu-content-pipeline` is mandatory, not optional.
   - If the source starts from one or more plain URLs and the immediate need is to capture the page faithfully, reuse `baoyu-url-to-markdown` directly as the leaf capture skill.
   - If the URL source also needs translation, staged markdown cleanup, or a normalized publish-ready markdown before evidence extraction, then route through `baoyu-content-pipeline`.
   - If the chosen content-family leaf is blocked only because a runtime or required binary is missing, bootstrap that dependency or ask the user for installation confirmation first. Do not silently substitute `curl`, search snippets, or another ad hoc capture path while still treating the leaf capture requirement as satisfied.
   - Do not rebuild a second webpage capture path inside this skill. Reuse the existing content-family leaves instead of duplicating their browser, fallback, or artifact logic.
   - Generic browsing or search snippets may help discovery, recency checks, and source expansion, but they do not replace content-family capture for evidence-bearing URLs.
   - Save source links and short role notes in `source/source-catalog.md`.
   - If the source mix includes commentary-like material such as community posts, technical commentary blogs, media profiles, or founder / investor posts, record for each source what it is actually fit to support. At minimum distinguish whether it is usable for:
     - factual confirmation
     - implementation or operator signal
     - narrative context
     - explanation frame
   - Do not let commentary-like sources silently inherit the same evidentiary weight as official docs, source code, or first-party mechanism evidence.
   - Treat founder, investor, PR, or media-amplified narrative as evidence of public framing or expectation-setting, not as direct evidence of technical originality, capability depth, or reliability unless corroborated elsewhere.
   - When URL capture is involved, keep both of these as explicit source artifacts when available:
     - raw rendered capture under `source/raw/`
     - normalized markdown under `source/normalized/`
   - `source/source-catalog.md` should record which saved artifact paths became the evidence-bearing source for later synthesis.
   - If a cited URL could not be captured through the content-family leaf, record the failure mode explicitly in `source/source-catalog.md` instead of silently substituting a search snippet or memory-based summary.
   - A concrete URL may not enter the primary evidence path with `capture_status: artifacted` unless the catalog also records concrete artifact paths. If the capture failed, record `capture_status: failed` and a short `capture_failure` note instead of pretending the URL was fully materialized.
   - Keep the source boundary explicit. A one-URL report should not read like a many-source survey.

4. Infer the report mode and write the thesis before drafting.
   - Create `notes/report-thesis.md` before any reader-facing draft is treated as real drafting.
   - Infer the report mode from the request and source mix. Use one of these by default:
     - `project-assessment`: evaluate one named project / product / library
     - `enterprise-best-practice`: judge real-world value,泡沫,边界,落地方式, or recommended practice for operators
     - `comparative-evaluation`: compare multiple concrete options or approaches
     - `trend-analysis`: explain a broader market / architecture shift over time
     - `source-commentary`: only when the user explicitly wants commentary on one source's argument or rhetoric
   - If the request asks about `落地`, `最佳实践`, `边界`, `值不值得`, or `怎么做`, default to `enterprise-best-practice`.
   - If the request includes one source plus a broader topic, treat that source as evidence input by default, not as the report spine.
   - `notes/report-thesis.md` should at minimum declare:
     - `report_mode`
     - `target_reader`
     - `core_question`
     - `single_sentence_thesis`
     - `section_spine`
     - `source_integration_plan`
     - `non_goals`
   - Choose one single-sentence thesis that the final report can defend. If you cannot state the thesis in one sentence yet, the source work is not ready for drafting.
   - Choose a section spine based on the reader problem, not on source order. Good defaults are:
     - `what it is -> why it matters -> value -> hype -> boundary -> best practice`
     - `problem -> options -> evidence -> judgment -> SOP`
     - `claim -> mechanism -> risk -> recommendation`
   - Express the `section_spine` in source-neutral language. Major sections should answer reader problems, decision dimensions, or operator concerns rather than echoing a memorable phrase from one source.
   - If a phrase from one source survives cross-source validation, paraphrase it into neutral operator-facing wording before elevating it into the section spine. Keep the original slogan or rhetorical phrasing inside a bounded source-analysis subsection when needed.
   - Record explicit source roles in `source/source-catalog.md` using labels such as:
     - `seed`
     - `baseline`
     - `mechanism-evidence`
     - `case-study`
     - `counterexample`
     - `supporting`
   - When commentary-like sources are present, also decide whether each one is functioning mainly as:
     - `upstream-confirmation`
     - `implementation-operator-signal`
     - `technical-commentary`
     - `media-narrative`
     - `community-signal`
   - If a commentary-like source is only suitable as a weak signal, write that boundary down explicitly instead of letting it sound like a verified fact source.
   - The report thesis should decide what each source is *for* before drafting starts.

5. Run a selective code-reading pass for source-available projects.
   - If the research object is open-source or source-available, source reading is a required stage of the report, not an optional enhancement.
   - The requirement is selective, not exhaustive: verify the implementation shape behind the few claims that most affect adoption judgment.
   - Do not stop at docs-only restatement for the core selling points of a source-available project.
   - If a selling point is central to why the project is interesting, the report should try to answer not only “does docs claim this” but also “roughly how is this realized”.
   - Focus only on claims that materially affect adoption judgment, for example:
     - API compatibility
     - hardware floor such as CPU-only or no-GPU startup
     - multimodal breadth
     - model-family breadth
     - extension hooks such as plugins, backends, or adapters
     - auth, tenancy, or deployment posture
   - Decompose compound README or overview claims before verifying them. Split slogan-like lines into concrete adoption axes such as:
     - deployment posture
     - hardware requirement
     - capability breadth
     - model-family breadth
     - support boundary
   - Do selective code verification, not a full code audit. Usually 1-4 high-impact claims are enough, but skipping code reading entirely is not acceptable for a source-available project report.
   - For at least the top differentiating claims, also ask a mechanism-oriented question such as:
     - is this capability implemented by one model or by multiple backends behind one API
     - does it require explicit model config, YAML wiring, or feature-specific pipeline setup
     - is the capability native, composed, or delegated to an extension point
     - does the code shape suggest “works in some paths” or “first-class supported path”
   - Prefer the official repo and inspect concrete implementation anchors when feasible:
     - API route definitions
     - backend registries
     - model config loaders
     - plugin or extension entrypoints
     - feature-specific handlers
     - tests or examples that exercise the claim
   - Save the result to `notes/code-verification.md`.
   - Use these statuses:
     - `code-confirmed`
     - `code-suggested`
     - `docs-only`
     - `contradicted`
     - `not-checked`
   - Save a short mechanism note for each checked claim. The goal is not repo archaeology; it is to explain the implementation pattern at the level needed for adoption judgment.
   - If source inspection truly cannot be completed in the current run, the report should say that the run stopped at docs-level judgment and should not present itself as a complete project assessment.

6. Materialize research artifacts before writing.
   - Create:
     - `source/source.md`
     - `source/source-catalog.md`
     - `notes/research-questions.md`
     - `notes/evidence-matrix.md`
     - `notes/report-thesis.md`
     - `notes/code-verification.md`
     - `notes/fact-check.md`
     - `notes/annotation-plan.md`
   - `research-questions.md` should capture the concrete questions the report must answer.
   - `evidence-matrix.md` should map questions or dimensions to specific supporting sources and open gaps.
   - `report-thesis.md` is the bridge between evidence collection and reader-facing drafting. It should lock the report mode, the main claim, and the section spine.
   - `code-verification.md` should stay selective. Its purpose is to pressure-test a few adoption-critical claims for source-available projects, not to turn every report into a repository audit.
   - For open-source or source-available project reports, `code-verification.md` is required before the report can be treated as final.
   - `fact-check.md` should stay pending until the report is near-final. Use it to verify that claimed capabilities, support statements, and limitation statements are actually grounded in the collected sources.
   - `annotation-plan.md` is optional in standard mode and required only when the report is being prepared as an annotated edition.

7. Select the writing posture and report angle.
   - The default writing posture is `research-report`.
   - Use `writing-theme-bridge` only after the scope, source set, and `report-thesis.md` are stable enough to justify drafting.
   - Save a canonical `notes/selection-bundle.md` with:
     - selected theme
     - writing posture
     - visual profile
     - visual strategy
     - report edition
     - annotation mode
     - annotation visuals
     - reader profile
     - text-only evidence, when applicable
     - whether the report is source-bounded, comparative, or recommendation-led
   - Save a canonical `notes/visual-inventory.md` planning decision before downstream visual rendering begins.
   - `notes/visual-inventory.md` should explicitly record:
     - `planning_status`
     - `image_count`
     - `count_decision_source`
     - `count_rationale`
   - If the user did not specify image count, the planner must still decide and record it explicitly instead of silently collapsing the request to one image.
   - Downstream visual skills may refine prompts and rendering choices, but they may not infer `image_count: 1` on behalf of an undecided upstream plan.
   - For research reports, the default `visual_strategy` should be `auto-plan-and-review`.
   - `auto-plan-and-review` means at least one first-pass visual should come from a leaf visual skill before final export, unless the user explicitly asks for text-only output.
   - For research reports, the default `report_edition` should be `standard`.
   - Switch `report_edition` to `annotated` when the user explicitly wants a 更易懂版本, 批注版, 术语解释版, 带背景知识版, or a report that preserves the main spine while adding visible explanatory notes.
   - Treat `annotated` as the mode for explanatory reader aids such as inline callouts, terminology notes, concept scaffolding, and optional lightweight annotation figures. Do not use `annotated` as a synonym for ordinary source citation visibility.
   - When `report_edition` is `annotated`, default:
     - `annotation_mode: inline-callouts`
     - `annotation_visuals: lightweight-supporting-figures`
     - `reader_profile: advanced-beginner`
   - When `report_edition` is `standard`, default:
     - `annotation_mode: none`
     - `annotation_visuals: none`
   - In `standard` mode, explanatory note blocks are not required. However, source visibility is still required for multi-source judgment-heavy reports. The final report should expose a lightweight evidence trail for contested or synthesis-heavy claims, for example by:
     - adding compact source markers such as `（S01 / S03 / S04）` at paragraph or subsection granularity
     - adding short `来源：Sxx` lines after dense evidence paragraphs or tables
     - using a brief source-note sentence that points readers to `source/source-catalog.md`
   - Do not require footnote-style citations for every paragraph by default, but do not let `exports/report-final.md` read as citation-free opinion writing when the report makes cross-source judgments.
   - Switch `visual_strategy` to `text-only-by-user` only when the user explicitly asks for a text-only deliverable.
   - When `visual_strategy` is `text-only-by-user`, `notes/selection-bundle.md` must also record a non-null `text_only_evidence` field capturing the user's explicit request in quoted or paraphrased form.
   - Absence of a request for visuals does not count as a text-only request. A plain request such as “出个调研报告”“写个分析” or a URL/topic-based report request still defaults to `auto-plan-and-review`.

8. Draft the report.
   - Route drafting through `engineering-practice-writer`.
   - Treat `drafts/report.md` as the intermediate working draft, not as the final deliverable.
   - If `report_edition` is `annotated`, treat `drafts/report-annotated.md` as the primary review artifact instead of `drafts/report.md`.
   - For multi-source requests, default to a synthesis-first document rather than a source-by-source rewrite. The final report should read like one integrated judgment, not like stitched article notes.
   - Keep two distinct mechanisms separate while drafting:
     - explanatory annotations: only required in `annotated` mode
     - source markers / evidence visibility: still expected in `standard` mode when the report contains contested, cross-source, or recommendation-driving judgments
   - The draft must follow `notes/report-thesis.md`. If the thesis and the body drift apart, rewrite the thesis or the draft before proceeding.
   - Make the early `结论摘要` behave like an evaluation snapshot, not an architecture abstract. It should usually contain:
     - one reader-familiar problem statement
     - one plain-language object role
     - one recommendation tier
     - best-fit / weak-fit conditions
     - a first-pass validation path
     - an evidence-boundary note
   - Treat that list as an internal drafting checklist, not a visible template. The output should read like a digested memo, not a filled form.
   - Keep the first verdict understandable to someone who does not yet know the project's internal nouns. Delay API names, backend labels, and structure terms until the explanation sections.
   - Prefer 2-3 compact verdict paragraphs over a numbered checklist when the same judgment can be expressed more naturally in prose.
   - Do not let the summary drift into step-by-step validation sequencing. If verification order matters, explain it in the dedicated SOP / next-step section instead of in the top verdict.
   - Prefer operator-facing object roles such as `网关 / 接入层 / 服务框架 / 统一服务入口` before deeper mechanism labels.
   - Keep the section plan natural. Do not create one visibly mechanical section per evaluation dimension if those dimensions can be merged into a stronger decision-oriented chapter.
   - For multi-source reports, prefer using research questions, decision dimensions, or operator concerns as the section spine. Do not let source order become the default report structure unless the user explicitly asks for a source commentary.
   - For `enterprise-best-practice`, prefer a spine like:
     - the enterprise problem
     - real value
     - hype / false shortcuts
     - boundary conditions
     - recommended practice
   - In multi-source reports, top-level and second-level headings should stay source-neutral. Do not use a slogan, quote, or memorable phrase from one source as a standalone section heading unless the report mode is `source-commentary` or the section is explicitly a bounded analysis of that source.
   - In research-report mode, avoid verdict-style headings that pre-assert the conclusion, such as `X 强于 Y`, `A 与 B 不匹配`, or similar thesis sentences. Prefer dimension-facing headings like `技术定位`, `依赖关系`, `成本约束`, `适用边界`, or `外部技术观察`.
   - For `enterprise-best-practice`, every major section should justify itself as a decision question, practice dimension, or operator concern. If a section can only be justified by naming one seed source or repeating its framing, it likely belongs in a bounded case-study subsection rather than the main spine.
   - For `source-commentary`, keep the commentary on the source bounded and still separate source claims from final judgment.
   - Ensure the report answers, in some form:
     - what this thing is
     - how to run a minimal SOP
     - which scenarios it fits or does not fit
     - the main pitfalls, constraints, and costs
     - the bounded recommendation or next action
   - If the source set includes strong marketing or README selling lines, do not quote them back as one undifferentiated conclusion. Break them apart and analyze the parts that actually matter for adoption.
   - If the source set includes investment stories, founder narratives, or media amplification, use them mainly to explain expectation gaps, public framing, or adoption context. Do not drift into investor-motive analysis unless the user explicitly asks for that line of inquiry.
   - If the seed material is a talk recap, opinionated article, or rhetorical post, treat it as one input source rather than the narrative spine of the report. Extract its claims, test them against other sources, and rewrite the final report in neutral operator-facing language.
   - Do not reuse a seed article's headline, slogan, or argumentative framing as the final report title or first verdict unless the framing survives cross-source validation and is rewritten in neutral language.
   - Do not leak operator-facing or process-facing wording into the reader document. Phrases such as `用户提供的文章`, `这次调研里`, `本轮抓取`, `作为输入源`, or similar workflow narration belong in `source/` or `notes/`, not in the report body.
   - For multi-source research, the report title should usually be neutral and descriptive, such as `<topic> 调研报告`, `<topic> 方案分析`, or `<topic> 多来源综合判断`, rather than a catchy article-style hook.
   - For source-available projects, distinguish clearly among:
     - docs-claimed
     - code-confirmed
     - inferred from code shape
     - still unverified in this run
   - When a selling point is central to the report, add a compact implementation reading in the body or a nearby subsection:
     - what the project claims
     - what implementation pattern seems to support that claim
     - what still appears to require explicit configuration, backend choice, or operator setup
   - Keep evidence, synthesis, and recommendation distinguishable.
   - In `standard` mode, make the distinction legible in the reader-facing document itself. Do not rely only on workspace notes to preserve that distinction when the body contains strong judgments.
   - Keep operator-facing scope notes, source-boundary discussion, and pipeline reasoning in `source/` and `notes/`, not in the reader-facing report body.
   - Do not let the first verdict line rely only on implementation-layer vocabulary such as `control plane`, `orchestrator`, `mid-layer`, or `pipeline layer`. Ground the object in a reader-familiar product role first, then add the deeper mechanism reading.
   - If the user says the report feels off in structure, framing, mainline, or organization, treat that as a thesis-and-outline problem first. Re-check `report_mode`, `single_sentence_thesis`, and `section_spine` before editing local prose.
   - In that situation, revise `notes/report-thesis.md` and the section headings first. Do not patch body paragraphs alone while keeping a source-skewed outline.
   - If visuals are likely for this report, the review artifact should stay `drafts/report.md` until those draft visuals have gone through user review. Do not treat the first text-complete pass as a reader-facing final.
   - If `report_edition` is `annotated`, also read `references/research-annotation-mode.md` before drafting the user-facing artifact.
   - In annotated mode:
     - keep the report thesis and section spine unchanged
     - preserve the main reader-facing report structure
     - add explicit visible notes instead of silently weaving all explanations into the prose
     - prefer note types such as:
       - `AI 批注｜概念理解`
       - `AI 批注｜背景补充`
       - `AI 批注｜适用边界`
       - `AI 批注｜最佳实践`
       - `AI 批注｜常见误解`
     - when the note needs a flow or spatial aid, allow one lightweight annotation figure near the note
   - Create `notes/annotation-plan.md` before annotated drafting. It should map:
     - which section needs annotation
     - why the section is hard to read
     - which annotation type should be inserted
     - whether a lightweight annotation figure is needed
   - In annotated mode, do not turn the report into a second parallel article. Keep one main spine and treat annotations as support scaffolding.

9. Prepare visuals only after the report skeleton is accepted.
   - Before planning or generating any report visual, read `references/diagram-contract.md`.
   - Create `notes/visual-inventory.md` only after the report structure is stable.
   - For `project-assessment`, `enterprise-best-practice`, `comparative-evaluation`, and `trend-analysis`, do not default to a text-only review artifact. Unless the user has explicitly requested text-only output, auto-plan a first-pass visual set and insert reviewable placeholders or draft visuals back into `drafts/report.md`.
   - `auto-plan-and-review` is a hard review mode, not a suggestion. If there is any planned visual, the first text-complete pass is still a draft pass rather than a final-export pass.
   - A single Mermaid diagram still counts as a planned visual. Do not treat “simple”, “obvious”, “low-risk”, or “small enough to inline” as permission to skip the user confirmation gate.
   - In annotated mode, lightweight annotation figures still count as planned visuals when they are part of the explanatory system. Track them in `notes/visual-inventory.md` rather than treating them as ad hoc markdown decorations.
   - Prefer `scripts/materialize-visual-prompts.js --workspace <dir>` to scaffold prompt files from the visual inventory.
   - `notes/visual-inventory.md` should give each planned visual a deterministic insertion anchor such as `draft_anchor_heading` so the pipeline can put the review artifact back into `drafts/report.md` without ad hoc manual placement.
   - Every planned visual should also record:
     - `research_question`
     - `selection_logic`
     - `exclusions`
     - why the visual belongs in that section instead of being merged elsewhere
   - For project-specific or technology-specific reports, do not default to just one architecture diagram. Prefer a small explanatory visual set that helps the reader build a mental model of the whole object.
   - Prefer:
     - comparison tables or infographics for competitive evaluation
     - framework diagrams for system structure
     - flowcharts for SOP / quickstart paths
   - For a project or technology report, the default visual set should usually include 3-5 of these:
     - project positioning / architecture overview
     - minimal SOP / quickstart flow
     - module or capability map
     - fit / unfit scenario matrix
     - pitfalls / constraints / decision matrix
   - If the report is long enough, it is better to spread several narrower explanatory visuals across the sections than to force one overloaded infographic.
   - Save the canonical Mermaid or node-edge logic under `notes/diagram-structures.md`.
   - `notes/diagram-structures.md` must not be only raw Mermaid. For each visual, first write a compact diagram spec that states:
     - `research_question_answered`
     - `why_visual_not_prose`
     - `source_anchors`
     - `selection_logic`
     - `exclusions`
     - `approval_status`
   - Treat Mermaid as the canonical structure source or an inline review format, not as the default rendered-output path.
   - Route rendering only through atomic visual skills:
     - `baoyu-article-illustrator` for framework, flowchart, and comparison diagrams
     - `baoyu-infographic` for denser summary or matrix visuals
     - `baoyu-image-gen` when exact prompt control or redraw from an approved structure source is needed
     - `baoyu-cover-image` only if the report explicitly needs a cover image
   - If the user wants rendered images instead of inline Mermaid, first confirm or save the structure in `notes/diagram-structures.md`, then translate that structure into prompts and render through one of the leaf visual skills above.
   - Before final export, every planned visual should move through an explicit review gate:
     - `pending` -> not yet prepared
     - `draft-placeholder` -> placeholder block inserted into `drafts/report.md`, waiting for structure review
     - `draft-inline-mermaid` -> inserted into the working draft as a reviewable diagram, waiting for user confirmation
     - `draft-rendered` -> first-pass rendered image prepared, waiting for user confirmation
     - `approved-inline-mermaid` -> user accepted the Mermaid or structural diagram as-is
     - `approved-rendered` -> user accepted the rendered image version
     - `skipped` -> user explicitly decided this visual should not be included
   - Keep the visual flow explicit:
     - write or confirm `notes/visual-inventory.md`
     - make sure each planned visual has a `draft_anchor_heading`
     - record `render_via` on each planned visual so rendered output stays attached to a leaf visual skill
     - confirm diagram structure in `notes/diagram-structures.md`
     - materialize prompt files under `prompts/`
     - auto-insert either a review placeholder, a draft Mermaid, or a first-pass rendered visual into `drafts/report.md`
     - generate first-pass outputs under `illustrations/` when rendering is warranted
     - pause for review after the placeholder, draft Mermaid, or first-pass rendered visual has been inserted into `drafts/report.md`
     - only after user confirmation, record the approved file path or approved Mermaid state back into `notes/visual-inventory.md`
     - integrate the approved image or approved Mermaid into the final report before export
   - Same-turn rule: if this turn created the first unapproved visual artifact for the pass, stop in review state. Do not also export `exports/report-final.md` in that same turn.
   - Do not mark visuals as `skipped` merely because the current pass stopped at text drafting. `skipped` is only for explicit user choice, not for orchestration convenience.
   - Do not switch `visual_strategy` to `text-only-by-user` merely to satisfy the final-export gate. That mode is allowed only when `text_only_evidence` exists in `notes/selection-bundle.md`.
   - Do not self-mark a generated Mermaid block or rendered image as approved just because it looks reasonable locally. The confirmation step belongs to the user-facing review gate.
   - Do not assume that silence about the visual means acceptance. Acceptance requires an explicit user-facing confirmation step in the conversation.
   - The final report should include the approved diagrams or approved rendered visuals near the relevant sections. Do not stop at a text-only report if visuals were planned as part of the explanation.

10. Close the pass explicitly.
   - Before final export, run one explicit fact-check pass against the current draft.
   - Check at minimum:
     - feature claims that sound like official support
     - support boundaries and limitations
     - whether any code-verification result changes how a docs-level claim should be worded
     - whether a statement is source-backed, inferred, or still unverified
   - Prefer wording such as “官方资料显示支持……”“从当前资料可以确认……”“本次资料未看到明确支持……” over flat assertions when support is incomplete.
   - For source-available projects, prefer wording such as:
     - “官方资料宣称……；从当前代码结构看……”
     - “文档层面强调……，本轮未进一步核验源码”
     - “这项能力在文档中被强调，但本次只做到 docs-based 判断”
   - Final export is allowed only after every planned visual has been explicitly approved or skipped by the user.
   - If any planned visual is still `pending`, `draft-placeholder`, `draft-inline-mermaid`, or `draft-rendered`, the pass is still in review or blocked state. In that state, do not create or update `exports/report-final.md`, and do not mark `notes/flow-closure.md` as completed.
   - Before answering with a conclusion-oriented final message, run an explicit completion check against the workspace. Confirm at minimum that:
     - `source/source.md` exists and matches the actual scope
     - `source/source-catalog.md` exists and reflects the evidence-bearing sources for the current pass
     - `notes/report-thesis.md` exists and the draft follows it
     - `notes/evidence-matrix.md` exists and covers the main decision dimensions
     - `notes/code-verification.md` is complete enough for the source-availability level of the object
     - `notes/fact-check.md` is no longer pending
     - `notes/flow-closure.md` records the current status and next action
   - If any required artifact or gate is still missing, the pass is not complete. Report the missing gate explicitly instead of presenting a summary that reads like a finished report.
   - Export the cleaned reader-facing report to `exports/report-final.md`.
   - If `report_edition` is `annotated`, the exported file may still be `exports/report-final.md`, but it should be finalized from the annotated draft rather than silently falling back to the standard draft.
   - For multi-source work, `exports/report-final.md` must be a single integrated document that clearly separates source claims, cross-source evidence, and final judgment.
   - You must run `scripts/finalize-report.js --workspace <dir>` successfully before treating the pass as complete, before updating `notes/flow-closure.md` to a completed state, and before answering with a final message that reads like a finished report.
   - Treat `scripts/finalize-report.js` as the authoritative export gate. If it fails, surface the failing gate explicitly and keep the pass in draft / review / blocked state. Do not work around the failure by hand-writing `exports/report-final.md` or manually marking the flow closed.
   - Save `notes/flow-closure.md` with status, completed artifacts, deferred work, and next action.

## Guardrails

- Do not silently broaden the scope of a named project.
- Do not reinterpret a research request as permission to produce an instant-answer summary or a quick verdict outside the workspace flow.
- Do not collect broad comparison sources before scope confirmation.
- Do not let a single-source summary pretend to be a multi-source report.
- Do not treat an existing workspace or an old `exports/report-final.md` as sufficient justification to answer immediately. Refresh the evidence and closure artifacts for the current pass first.
- Do not cite a concrete URL-bearing source from search snippets alone when `baoyu-url-to-markdown` or `baoyu-content-pipeline` could have materialized the page into source artifacts.
- Do not start reader-facing drafting before `notes/report-thesis.md`, `source/source-catalog.md`, and `notes/evidence-matrix.md` all exist.
- Do not let evidence collection end without deciding what the report is *about*. A report without a single-sentence thesis is not ready to draft.
- Do not let source roles stay implicit when one source is rhetorical, one is a case study, and others are mechanism evidence.
- Do not reimplement webpage capture inside this skill when `baoyu-url-to-markdown` already covers the need.
- Do not route a simple “capture one page and stop” action through `baoyu-content-pipeline`; keep the direct leaf route when there is no staged translation or normalization need.
- Do not let a compound README slogan stand in for analysis. Break it into the concrete adoption axes it implies.
- Do not let a seed article's headline, source order, or rhetorical tone become the structure of a multi-source report.
- Do not let a source-specific slogan, quote, or memorable phrase become any top-level or second-level heading in a multi-source report unless it is clearly bounded as source commentary.
- Do not produce a final multi-source report that reads like “article summary plus a few supporting links”; the final document must integrate claims across sources into one reader-facing judgment.
- Do not mention the user, the current run, capture steps, or workspace process in the reader-facing report body unless the report is explicitly a methodology memo.
- Do not write a docs-level claim as if it were code-confirmed unless this run actually inspected the relevant implementation anchors.
- Do not let an abstract implementation label stand in for the whole recommendation. The report should tell the reader what category of tool this is for operators, whether it is worth a PoC, and under what fit boundaries.
- Do not turn “source available” into “must fully audit the repository”. Verification should stay selective and driven by adoption significance.
- Do not stop at “docs say it supports X” when the report is clearly being driven by a differentiating open-source selling point. Add at least one layer of mechanism judgment if the repo makes that feasible.
- Do not treat source reading as optional for an open-source or source-available project report. If the run never reached code-level verification, keep the output explicitly partial.
- Do not respond to user feedback about structure, framing, or mainline by only editing local prose; repair the thesis and section spine first if the outline has drifted toward one source.
- Do not confuse “implemented through backend composition and config” with “one hidden black-box capability”. If the implementation path matters, say so explicitly.
- Do not start polished drafting before `source-catalog.md` and `evidence-matrix.md` exist.
- Do not draft as if the object were settled while `source/source.md` still records `scope_status: ambiguous`.
- Do not treat searched snippets, raw webpage reads, or memory summaries as satisfying a required URL capture path when a content-family leaf should have materialized the source.
- Do not let unsupported or weakly supported capability claims survive into the final report.
- Do not treat `drafts/report.md` as the final deliverable.
- Do not let a missing artifact gate degrade into a polished answer. Missing gates must surface as a blocker, not as a shortcut to a “good enough” summary.
- Do not jump straight from a text-complete draft to `exports/report-final.md` while visual review is still pending.
- Do not self-upgrade `draft-inline-mermaid` or `draft-rendered` into an approved state without user confirmation.
- Do not reason that a Mermaid is “too simple to need review” or that inline structure equals automatic approval.
- Do not silently convert a likely-visual report into a text-only final by marking every planned visual as `skipped`; use `text-only-by-user` only when the user explicitly asked for that outcome, and record that evidence in `notes/selection-bundle.md`.
- Do not leave report diagrams in a planned-only state if the report has already moved to final export.
- Do not manually author or overwrite `exports/report-final.md` unless `scripts/finalize-report.js --workspace <dir>` has just succeeded in this pass.
- Do not manually set `notes/flow-closure.md` to a completed / exported state if the finalize script would still fail on visuals, fact-check, or code-verification gates.
- Do not invoke another orchestration pipeline for report visuals; this pipeline should call only leaf visual skills.
- Do not introduce a local Chrome / Mermaid-CLI rendering branch as the standard rendered-diagram path. If the user wants real rendered visuals, use the leaf visual skills and keep Mermaid only as structure source or review artifact unless the user explicitly asks for direct Mermaid export.
- Do not under-illustrate a project report when the object, SOP, module map, and decision boundary would all benefit from separate visuals.
- Do not confuse this report flow with RFC writing or practice-sharing blogging.

## References

- Workspace contract: `references/research-workspace.md`
- Diagram contract: `references/diagram-contract.md`
- Annotated research mode: `references/research-annotation-mode.md`
