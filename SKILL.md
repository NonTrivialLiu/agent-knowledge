---
name: agent-knowledge
description: >-
  Agent/LLM 应用工程的本地全文知识库（harness、skills、context/memory、tools/PTC/MCP、
  runtime、multi-agent、evaluation、training、security、loops，规模见 kb.py stats），
  带检索、渐进阅读、联网补新与入库流程。Use when the user asks about agent
  engineering, harness design, AGENTS.md, skill authoring, context engineering,
  agent memory, tool calling/MCP, long-running agents, multi-agent systems, agent
  evaluation or training, or wants the latest practices beyond model knowledge, or
  asks to research/archive new articles on these topics. Also use when designing
  any agent framework, auto-research pipeline, or coding-agent workflow and you
  need prior art. Not for: 大模型训练理论本身、与 agent 工程无关的 ML 问题。
---

# agent-knowledge：Agent 工程知识库

跨 Codex / Claude Code / ZCode 共用的本地知识库：全文 Markdown（Anthropic、
OpenAI、Google、DeepSeek、LangChain、Cloudflare、METR、arXiv 等），每篇带单行
YAML frontmatter（title/url/published/fetched/type/topics/summary，部分含
priority: core）。权威元数据在 frontmatter；`references/<类>/CATALOG.md` 是脚本
再生的浏览视图（⭐ core 必读置顶）。

## 工作流

1. **本地检索 + 渐进阅读**（见下两节）。
2. **联网补新**：本地结果缺失、明显过旧（published 超一季）、或用户要"最新"
   时，联网搜增量（来源范围见 `references/ingest.md`）。
3. **遇到好文章就入库**：检索或联网中发现有具体机制、真实数据且库内缺失或
   更优的文章——入库是默认动作，按 ingest.md 七步走完再回答用户；仅当内容是
   重复转述、纯新闻稿或与库内已有篇目无增量差异时才跳过。

## 检索方法（先 rg，再 Read，绝不整库读）

frontmatter 全部单行，rg 一条命令可同时搜元数据与正文。**至少跑 2-3 组
关键词**（同义词、中→英翻译后的术语、相邻概念），合并去重得到候选集：

```bash
cd <本skill目录>
rg -i -l --no-heading "database agent" references/ -g '!CATALOG.md'   # 全文
rg -i "topics:.*(skill|trigger)" references/ -g '!CATALOG.md' -l      # 元数据
rg -i "summary:.*(压缩|compaction)" references/ -g '!CATALOG.md' -l   # 中文摘要
cat references/<类>/CATALOG.md                                        # 类目定位（单行/篇）
```

候选集先看 frontmatter 的 summary 过滤明显无关的；目标保留 **3-10 篇**进入
阅读——少于此数说明关键词太窄，换词再检索；回答横跨多主题时取上限。
候选中有 `type: analysis`（synthesis 综合文章）时优先读：它提供结论与机制
的融合分析，并相对链接到原始条目，可顺链精读。

分类：fundamentals 概念全景 · skills-design Skill 设计 · harness 工程方法/AGENTS.md ·
context-memory 上下文/记忆 · tools-execution 工具/PTC/MCP/沙盒 · runtime 长任务/运行时 ·
multi-agent 协作 · evaluation 评估/实证/成本 · training RL/环境/模型报告 ·
model-behavior 各代模型行为与提示词对冲 · reliability-security 注入/权限 ·
loops-selfimprovement Loop/自改进 · synthesis 自有综合。各类检索词明细见
`references/ingest.md` 分类表；交叉主题跨类召回靠 rg topics。

## 渐进阅读（按深度递进，不贪快也不全读）

1. **结构层**：`rg "^#{1,3} " <file>` 看标题骨架，判断该读哪几节。
2. **摘要层**：`sed -n '1,12p' <file>` 读 frontmatter summary 与开篇结论；
   有 TL;DR/Summary/结论节的直接跳读首尾。CATALOG 只做类目定位，
   不作为内容源。
3. **精读层**：只精读与当前任务直接相关的章节；⭐ core 文章值得整篇或读主干
   章节——它们是经过筛选的概念全景与权威叙述。

各篇按需选深度：概念性问题读 core 全文即可；工程实现问题精读 2-3 篇的
相关章节 + 扫其余候选的摘要层。回答时标注来源 `title (published)`。

## ⭐ core 必读机制

每类有 ≤3 篇 `priority: core`：该主题的概念全景文、权威规范或公认经典
（审定规则见 ingest.md）。进入一个新主题时，先读该类 CATALOG.md 的 ⭐ 条目
再读检索命中的具体篇目；跨主题任务每类 core 至少读到摘要层。core 由维护者
标注，Agent 不得自封。

## 入库（新增文章）

完整 SOP 见 `references/ingest.md`（来源范围、去重、抓取、frontmatter 模板、
分类表、硬性禁令）。最短路径：

```bash
rg -i "<url关键词>" references/                                   # 1 去重
uv run scripts/fetch.py URL --title "T" --published D \
  --out references/<类>/<slug>.md                                 # 2 抓取
# 3 补全 frontmatter（单行！）     4 python3 scripts/kb.py lint    # 5 校验
python3 scripts/kb.py catalog                                     # 6 再生目录
```

lint 不过不算入库；禁止手改 CATALOG.md；禁止序号文件名。

## 维护

- `python3 scripts/kb.py stats` 看规模与 core 分布；`lint` 全库体检；`catalog` 再生目录。
- 无定时任务：更新由用户触发或随检索工作流顺带完成。
- 本库真实文件在 `~/.agents/skills/agent-knowledge/`；`~/.claude/skills/`、
  `~/.zcode/skills/` 下是软链，不要在软链侧改结构。
