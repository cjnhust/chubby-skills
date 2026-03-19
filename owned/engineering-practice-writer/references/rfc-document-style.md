# RFC Document Style

在用户要求“写 RFC”“写设计文档”“按 proposal 风格来写”“更像规范文档/技术方案”时，读取本文件。

本文档提炼的是 React Native proposals 模板及其实例文章所体现的共同写法，而不是要求照抄标题或章节名：

- `0000-template.md`
- `0744-well-defined-event-loop.md`

## 总体判断

这类文档的核心目标不是“把一件事讲得有故事性”，而是“让读者可以基于同一份文档评估、实现、质疑或接受一个提案”。

因此，它的写法天然强调：

- scope 清晰
- motivation 与 design 分离
- terminology 明确
- drawbacks、alternatives、adoption 被正面展开
- unresolved questions 被显式列出

## 可执行的风格维度

### 1. 先给 Summary，再展开正文

- 开头先说清提案是什么、目标是什么、作用范围是什么。
- 如果文档有固定模板，优先保留模板而不是改写成博客式引入。

迁移规则：

- 不要用长篇背景替代 Summary。
- 第一段就让读者知道提案边界，不要把真正的主张藏到后文。

### 2. Motivation 先讲问题和约束，不急着讲方案

- Motivation 的价值在于，让读者即使不接受当前方案，也能理解真正需要解决的问题。
- 这一段要尽量从 use case、约束、现有问题、期望结果出发，而不是把解决方案提前塞进去。

迁移规则：

- 如果草稿一进入 Motivation 就开始讲方案细节，先把它拆回问题、约束和目标。
- 把“为什么要改”与“准备怎么改”分开。

### 3. Detailed design 要够具体，足以评审和实现

- 设计部分是正文主体，需要讲清概念模型、执行顺序、边界条件、兼容性和角落案例。
- 术语要先定义，流程要能被追踪，语义要能被验证。

迁移规则：

- 不要把 design 写成一句话结论加零散例子。
- 如果方案依赖执行顺序或语义保证，显式列出来。

### 4. Drawbacks、Alternatives、Adoption 不是装饰

- 这些章节不是礼貌性补充，而是 RFC 的核心可信度来源。
- 一个成熟的提案必须同时说明代价、替代路径、迁移方式和可能的 rollout 策略。

迁移规则：

- 如果草稿只有收益没有代价，补 drawbacks。
- 如果草稿没有解释为什么不用别的方案，补 alternatives。
- 如果草稿会影响现有用户、系统或 API，补 adoption 或 migration。

### 5. 语气要规范、可审查、可反驳

- 写法偏克制、直接、精确，不靠渲染和修辞推动阅读。
- 读者通常是评审者、实现者或受影响方，因此文档必须方便他们质疑和核对。

迁移规则：

- 少用“显然”“非常优雅”“很好地解决了”这类判断词。
- 多用可验证描述，例如行为变化、范围约束、兼容性前提和预期影响。

### 6. 词汇和文风要偏“评审语体”

- 常见的有效词汇是：提案、目标、范围、非目标、约束、语义、兼容性、迁移、替代方案、假设、风险、影响、回滚、实现、规范、要求。
- 常见的有效动词是：提出、引入、定义、限制、对齐、弃用、迁移、支持、移除、要求、允许、不保证。
- 句子通常更短、更直接，更像“给评审者和实现者看的说明”，而不是“带读者进入一个故事”。
- 小结型句子可以有，但应服务于评审判断，例如“该方案会带来以下兼容性变化”，而不是“可以看到这是一个更优雅的方向”。

迁移规则：

- 优先把抽象判断翻译成显式 scope、行为变化和影响说明。
- 当一个句子同时承担背景、方案、评价三件事时，把它拆开。
- 能写成“X 将会…… / X 不再…… / Y 需要……”时，不要写成模糊感受句。

## 与技术博客的边界

- RFC 不是经验分享文章，不需要靠背景铺垫建立阅读兴趣。
- RFC 可以有动机，但不需要博客式的“问题是怎么一步步长出来的”叙事节奏。
- RFC 的主要价值是帮助评审和落地，不是帮助读者理解作者的实践历程。
- RFC 可以追求清晰，但不需要追求散文式顺滑或强阅读节奏。

## 不要做的事

- 不要把 RFC 写成故事化长文。
- 不要把 summary、motivation、design 混成一个连续散文段落。
- 不要省略 drawbacks、alternatives、adoption，只留下“方案本身”。
- 不要用模糊、宣传式、情绪化语言替代设计判断。
- 不要让读者读完整篇还不知道 scope、非目标和兼容性影响。

## 快速判断

如果改写后的文档满足下面这些特征，通常就更接近 RFC / 技术文档写法：

- 开头很快说清 summary 和 scope
- motivation 与 design 被明确分开
- 设计细节足够支撑评审和实现
- drawbacks、alternatives、adoption 被正面展开
- 术语、语义和边界条件是显式的
- 语气克制、精确、方便反驳与核对

## Sources

- https://github.com/retyui/discussions-and-proposals/tree/0e2dc7bc978393b7766bb48784f6e37397015b31/proposals
- https://github.com/retyui/discussions-and-proposals/blob/0e2dc7bc978393b7766bb48784f6e37397015b31/proposals/0000-template.md
- https://github.com/retyui/discussions-and-proposals/blob/0e2dc7bc978393b7766bb48784f6e37397015b31/proposals/0744-well-defined-event-loop.md
- https://github.com/retyui/discussions-and-proposals/blob/0e2dc7bc978393b7766bb48784f6e37397015b31/proposals/0607-dom-traversal-and-layout-apis.md
- https://github.com/retyui/discussions-and-proposals/blob/0e2dc7bc978393b7766bb48784f6e37397015b31/proposals/0759-react-native-frameworks.md
- https://github.com/retyui/discussions-and-proposals/blob/0e2dc7bc978393b7766bb48784f6e37397015b31/proposals/0979-modern-api-abortcontroller.md
