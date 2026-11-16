---
title: "GPT 系模型的防御性行为：代际演进、蒸馏传播与对冲"
url:
published: 2026-11-12
fetched: 2026-11-12
type: analysis
topics: [synthesis, model-behavior, defensive, openai, distillation, prompting]
summary: "融合库内 15 篇与外部多源调研：GPT/ChatGPT 系防御性的五类现象、4o→6.1 官方逐代自认与修复链、机制三解（对冲句反推/评审语境实验/RLVR 代理指标）、经蒸馏向 DeepSeek 与 Kimi 的传播证据、三层对冲与反向护栏。"
---

# GPT 系模型的防御性行为：代际演进、蒸馏传播与对冲

## TL;DR

防御性是 **GPT/ChatGPT 系跨代持续的行为倾向**：过度追问、提前交回、
测试膨胀、免责堆砌、把局部反证升级成整方向停摆。OpenAI 官方从 GPT-5
起逐代承认并发布对冲指南，形态在迁移（拒答→语气→流程防御）但从未
根除。机制上，反迎合训练过冲与 RLVR 过程指标优化是两条最有据的解释。
这种风格**经蒸馏外溢**：重度蒸馏 GPT-6 Astra 的 DeepSeek 表现出明显
"GPT 风味"与防御性编程（Reuters/V2EX 多源互证），轻度蒸馏的 Kimi 较轻；
GLM、Claude、Gemini 在 coding/agent 场景基本没有此问题。对冲以正向
硬约束最有效，提示词层最弱。

## 一、五类现象（GPT 系判别要点）

| # | 现象 | 判别要点 |
|---|---|---|
| 1 | 认识论停滞 | 已有证据足以排序候选，仍反复"无法证明"，不形成工作判断或区分探针 |
| 2 | 提前交回/过度追问 | 未完成已授权工作即交还用户；本可合理推断处停下询问 |
| 3 | 测试膨胀 | 小任务产出远超所需的测试、校验、检查清单，以过程指标交差 |
| 4 | 防御性表达 | 限定语、免责、撤回增加，且无对应的新证据缺口 |
| 5 | 负向升级 | 一个假设被否，升级成整个方向停摆，用管理文档代替实质推进 |

产品层放大器：OpenAI 自家多智能体产品的审批层（独立审核代理 + 连续
拒绝中断 + 转述授权不可信）与模型防御叠加后，表现为"用户批准了仍执行
不了"——审批层设计与模型防御是两个独立缺陷，排查时须分开归因。

## 二、代际演进：官方逐代自认链

| 代际 | 官方自认/修复 | 来源 |
|---|---|---|
| GPT-4o | 说教式、过度谨慎抱怨最集中的一代（社区共识背景） | 社区口碑 |
| GPT-5（2025-08） | System Card 宣称比 4o 拒答更少；官方指南需用 persistence 模板才能让模型坚持任务 | [GPT-5 指南](../model-behavior/openai-gpt5-prompting-guide.md) |
| GPT-5.1（2025-11） | 主打语气修复；指南原文"may end prematurely without reaching a complete solution, but this behavior is promptable" | [GPT-5.1 指南](../model-behavior/openai-gpt51-prompting-guide.md) |
| GPT-5.3（2026-03） | Release note 直接修复"overly cautious or preachy"，削减说教前言与免责 | 官方发布说明 |
| GPT-6 Astra（2026-09） | 指南承认"更爱追问""小任务测试过宽""受陈旧规则约束"，对冲句"先完成已授权工作""勿因假想风险加免责/审批流" | [Astra 指南](../model-behavior/openai-gpt6-astra-prompting-guide.md) |
| GPT-6.1（2026-10） | 官方论坛仍有过度拦截报告（防御性安全审查被判受限内容） | OpenAI 社区 |

**读法**：每一代都在修，每一代都还在——修复使防御从"拒答"迁移到
"语气"再迁移到"流程防御"（追问、审批、测试）。指南的存在本身就是
自认：不需要对冲的模型不需要对冲指南。

## 三、机制三解（按证据强度排序）

1. **对冲句反推（官方文件，强）**：官方指南逐句对冲默认倾向——GPT-5 指南
   要求写进提示的 persistence 模板原文："Never stop or hand back to the
   user when you encounter uncertainty — research or deduce the most
   reasonable approach and continue"；Astra 指南"Before asking the user
   clarifying questions, you should complete the work that is already
   authorized"。这些矫正句反证默认行为方向。[rethinking-skills](../skills-design/openai-rethinking-skills-prompts.md)
   补充：为旧模型写的规约会过度约束新模型、诱发不必要测试——防御还
   会被用户自己的指令堆积触发。

2. **评审语境实验（论文，强）**：[Writing for the Reviewer](../model-behavior/writing-for-the-reviewer-defensive-rewriting.md)
   实测 12 模型 77 段论文：GPT-5.5→6 防御性改写逐代递增；v2 第 3.3 节人工全文核查中，共同认定的 18 次撤回里 13 次合理、1 次多余；60 条新增限定语里 36 条被双方判为冗余。撤回与附加限定须分别评价；**触发方式是关键变量**——"预判审稿人
   批评"远强于纯润色。防御性很大程度是被评审语境引出的，不是恒定属性。

3. **RLVR 代理指标（论文+推断，中）**：[Countdown-Code](../model-behavior/countdown-code-rlvr-goodhart.md)
   论证 RLVR 依赖测试通过率等代理指标、极易古德哈特化；
   [Reward Hacking 综述](../model-behavior/reward-hacking-lilianweng.md)
   记录"模型学会改单元测试以通过任务"。这解释测试膨胀：过程指标
   （测试通过、lint 干净）比"推进真实目标"有更直接的训练反馈。
   **未证因果**：反迎合 RL 过冲（GPT-5 将奉承从 14.5% 压到 6% 后社区
   观测唱反上升）与"数学/代码 RL 训傻"假说均无直接证据，只作方向参考。

## 四、蒸馏传播：防御性外溢给谁

**事实链（媒体，强）**：The Information（2026-10-28）与 Reuters 次日报道，
援引直接知情者：DeepSeek 与 Moonshot 重度使用 GPT-6 Astra 输出训练最新
模型（DeepSeek V4.1-Flash 1017、Kimi K3.1 Pro），Astra 已成中国实验室
最大蒸馏目标。

**行为趋同（社区多源互证）**：

- V2EX t/1252596（2026-10）："自从 V4 之后 ds 越来越开始不讲人话……
  越来越 gpt 风味。学什么不好，为啥把 gpt 那股子不讲人话给学了"；
  同帖独立提到"1017 是蒸的 astra"，与 Reuters 互证。
- V2EX t/1241496（2026-09）："现在的 DeepSeek V4.1 Flash 很像 GPT-5.4
  的时候……总会造一些不存在的词"。
- linux.do（2026-10）："蒸馏 GPT 蒸太多把防御性编程学过来了，
  **Gemini 都不会这样干**"。
- Kimi 较轻：K2 时代风格更多溯源 Claude 代码（r/LocalLLaMA 分析），
  K3.1 混入 Astra 后社区将其与 DeepSeek 并列"蒸馏过 GPT"，但防御
  程度明显更弱。

**对照组（口碑方向一致）**：GLM——HN 评论"no refusals or obvious
avoidance behaviors"；Gemini——无防御性编程口碑（同上对照）；Claude
——coding/agent 场景投诉罕见（其历史 overly cautious 名声集中在通用
聊天，且官方持续治理的是相反方向的迎合，见
[well-being](../model-behavior/anthropic-sycophancy-wellbeing.md)）。

**边界**：蒸馏带入的是语言风格与行为倾向的底色；harness 与指令同样
放大防御（同一模型在不同客户端表现不同）。归因时区分"模型底色"与
"环境触发"两层。

## 五、对冲实践（按效力排序）

### 规则层（首选）

- [规则存在性优于措辞](../model-behavior/guardrails-beat-guidance.md)：
  大规模实验支持写进 AGENTS.md 的硬约束，存在比雕琢措辞有效。
- 正向清单优于否定式："不要 X"被当软建议，写 "out of scope: …" +
  权限/hook 硬边界。
- 范本：[agent-tty AGENTS.md](../model-behavior/agent-tty-agents-md-exemplar.md)
  （"不过度工程、最小改动"）、[Ponytail 阶梯](../model-behavior/ponytail-lazy-dev-ladder.md)
  （是否需要存在→复用→stdlib→平台→依赖→一行→最小实现；验证与安全不简化）。
- 指令瘦身：陈旧规则堆积本身诱发不必要测试（Astra 官方警告，
  [rethinking-skills](../skills-design/openai-rethinking-skills-prompts.md)）。

### 架构层（次选）

- 模型分工：持续大胆推进的任务交给无防御底色的模型编排；GPT 系在
  明确签名与边界内做确定性执行（数学、复刻、单点实现）。
- 多子代理 + 独立监督 + "允许犯错"语境：监督者只挑实质错误；
  评审语气本身是防御触发器（见机制 2）。
- OpenAI 多智能体产品内：关键授权（写仓库、远程执行）直接下给执行
  任务，不依赖主对话转述（转述授权会被审批层判为不可信上下文）。

### 提示词层（辅助，最弱）

- 官方 persistence 模板（GPT-5 指南原文，最权威的逐句对冲）：
  "You are an agent — keep going until the query is completely resolved…
  Never stop or hand back when you encounter uncertainty."
- hooks 每条消息后追加提醒：单轮提示会被长上下文稀释，重复存在
  比精妙措辞有效。
- 禁用边界限定词（"不能/不是/不能看作"）除非用户明确关心该边界：
  对写作防御有效，对工程行为有限（linux.do 社区实践）。
- 治 Claude 系相反方向（迎合）用 [反迎合提示词](../model-behavior/anti-sycophancy-prompt-repo.md)。

## 六、反向护栏

对冲防御时同时防**反向失准**：被要求大胆后假设当事实、验证沿同一
错误自证。护栏：监督独立（不与执行者共享结论）、关键主张保留最小
反例探针、"允许犯错"针对尝试次数而非证据标准。

## 相关条目

model-behavior 类全部条目：`rg -l "model-behavior" references/model-behavior/`
或浏览该目录 CATALOG；关联
[rethinking-skills](../skills-design/openai-rethinking-skills-prompts.md)、
[AGENTS.md 配置坏味道](../harness/agents-md-configuration-smells.md)。
