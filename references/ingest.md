# 入库与维护 SOP（Agent 必读）

> 本文件是 agent-knowledge 的唯一入库规范。执行任何"抓新文章 / 补条目 / 更新知识库"任务时，逐步照做，不自由发挥。

## 何时入库

**遇到好文章就入库——这是默认动作，不需要请示。**触发场景：

- 检索或联网中发现：有具体机制、真实数据、且库内缺失或比已有篇目更优的文章。
- 用户问到 agent / LLM 应用工程问题，本地结果缺失、过旧（`published` 超过约一个季度）或质量不足时。
- 用户明确要求"调研 / 补充新资料"时。

跳过的唯一理由：纯重复转述、纯新闻稿、与库内已有篇目没有可说清的增量差异。

## 值得抓的来源

- 头部厂商工程博客：Anthropic (anthropic.com/engineering, /research, alignment.anthropic.com)、OpenAI (openai.com/index, developers.openai.com/blog)、Google (research.google, developers.googleblog)、DeepSeek、Microsoft Research、Cloudflare、LangChain、HuggingFace。
- 一线团队与个人博客（历史证明高质量）：humanlayer.com、arize.com、metr.org、cognition.com、manus.im、normaltech.ai、trychroma.com、kimi.com/blog、alexzhang13.github.io、kaiyuanliu04.github.io。
- 论文：arXiv（cs.AI / cs.CL / cs.SE）、ACL Anthology、PMLR。
- 发现渠道：Hacker News、arXiv 新 listings、上述博客的 RSS。优秀博客不限于大厂——判断标准是"有具体机制或真实数据"，不是名气。
- 产品官方文档（platform.claude.com、developers.openai.com、agentskills.io）只在规范/接口需要权威参照时入库，type 用 `docs`。

## 入库七步

1. **去重**：`rg -i "<url 或核心标题>" <本skill根目录>/references/`。已有则跳过；同主题已有更优文则只在确有增量时新增。
2. **抓取**：
   - 首选 `uv run scripts/fetch.py URL --title "标题" --published YYYY-MM-DD --out references/<分类>/<slug>.md`（自动带 frontmatter 模板）。
   - fetch.py 失败（JS 渲染、403、付费墙）时：改用 harness 的 WebFetch/内置浏览器读原文，人工整理成 Markdown；PDF 论文用 MinerU（同级同名派生目录模式）。
3. **补全 frontmatter**（模板见下；**所有字段必须单行**，这是 rg 检索的前提）。
4. **分类**：按下表选一个主类目录；交叉主题靠 `topics` 多标签召回，不靠挪文件。
5. **命名**：slug = 标题转小写连字符英文，≤90 字符；**禁止序号前缀**。
6. **校验**：`python3 scripts/kb.py lint`——报 ERROR 必须修复后才算入库完成。
7. **再生目录**：`python3 scripts/kb.py catalog`，确认新条目出现在对应 CATALOG.md。

## frontmatter 模板与字段规则

```yaml
---
title: "原文标题（保留英文原题）"
url: https://...
published: 2026-01-02      # 找不到就留空串或不写
fetched: 2026-11-11        # 抓取日
type: engineering-blog     # paper / engineering-blog / docs / abstract / analysis
topics: [主类名, 来源方, 关键词2-3个]   # 全小写；第一个词 = 所在目录名
summary: "一行中文（≤120字）：这条内容比库里已有的多了什么"
---
```

- summary 是给"未来的 Agent 扫目录"看的判断依据，写增量，不写客套概括。
- 拿不到全文只有摘要时 `type: abstract`，并在 summary 标注"仅摘要，全文 403/付费"。
- `priority: core` 是必读标记，**由维护者（用户确认）审定，Agent 不得自封**。
  界定标准（满足其一且每类 ≤3 篇）：
  1. 概念全景文：一篇讲透一个主题域、叙述全面经得起时间（如 building
     effective agents、components of agent memory）；
  2. 权威规范：官方格式/接口的权威参照（如 agentskills.io specification）；
  3. 公认经典：被库内多篇引用或反复印证的一手工程叙述。
  core 满了要新增必须先请用户替换哪篇。

## 分类目录

| 目录 | 收什么 | 典型检索词 |
|---|---|---|
| fundamentals | 概念框架、全景入门、术语体系 | workflow vs agent, 12-factor, scaffold |
| skills-design | Skill/插件/指令包的设计、规范、评测 | skill, frontmatter, description, 触发 |
| harness | Harness 工程方法、AGENTS.md、架构约束、工程经验 | harness, AGENTS.md, 架构, taste |
| context-memory | 上下文工程、压缩、跨会话记忆、KV cache | context, compaction, memory, dream |
| tools-execution | 工具接口、PTC/MCP、代码执行、沙盒 | tool, PTC, MCP, code mode, sandbox |
| runtime | 长任务、托管运行时、恢复、平台、基础设施 | long-running, session, checkpoint |
| multi-agent | 多 Agent 协作、编排、失败模式 | multi-agent, orchestration, swarm |
| evaluation | 评估、基准、实证研究、成本、生产率测量 | eval, benchmark, cost, METR |
| training | RL、训练环境、世界模型、模型报告、模型-harness 适配 | RL, world model, adapter, K2.5 |
| model-behavior | 各家各代模型的行为倾向与提示词实践：防御性、迎合、过度拒答、测试膨胀、官方指南 | defensive, sycophancy, prompting, openai, anthropic, google, deepseek |
| reliability-security | 可靠性、注入、权限、红队 | injection, CaMeL, red-team, reliability |
| loops-selfimprovement | Loop 工程、自改进、经验复用、递归 | loop, trigger, self-improve, RLM |
| synthesis | 自有综合文章（见下方"synthesis 规范"） | synthesis + 相关类名 |

## synthesis 规范（自有综合文章）

`references/synthesis/` 收**自己写的**跨来源综合分析，与外部正文（只读）不同：

- **准入**：必须融合 ≥3 篇库内条目或第一手实验，回答一个明确问题（问题写进 title 或首行）；
  摘要拼盘是 CATALOG 的职责，不收。
- **自包含**：脱离任何项目与个人上下文可读——不出现具体项目名、对话过程、个人遭遇；
  项目案例须泛化为机制描述。
- **固定骨架**：TL;DR（一句话结论）→ 机制分析 → 证据表（主张|证据|强度|链接）→
  可操作对冲 → 相关条目（相对路径链接，lint 校验死链）。
- **可修订**：外部正文禁止改动；synthesis 允许随新证据重写，重写保持自包含与骨架，
  `published` 更新为修订日。
- **防稀释**：新写前先 `rg -i "<问题关键词>" references/synthesis/` 查重，
  同一问题更新旧文，不开新篇。

## 硬性禁令（防熵）

- **正文下限**：条目必须有实质全文（≥600 字节，lint 强制）。社区讨论、
  新闻报道抓不到全文时，其要点与引句**并入 synthesis 作为引用素材**，
  不单独建薄条目；`abstract` 仅限学术发布页摘要。
- **目录白名单**：skill 根只允许 `SKILL.md`、`references/ingest.md`、
  `scripts/`、`references/<分类>/`（各含正文与再生 CATALOG.md）。
  新增任何其他文件须用户批准。
- 禁止编辑已入库文章的正文；发现内容过时只能在 summary 或 CATALOG 层面加注。
- 禁止手写/手改 CATALOG.md——它永远由 `kb.py catalog` 再生。
- 禁止序号前缀文件名、禁止中文文件名。
- 禁止移动已入库文件（链接稳定性）；确需移动时全库 `rg` 修复引用。
- URL 是唯一去重键；lint 报 url 重复时不许加"副本"绕过。
