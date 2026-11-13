# agent-knowledge

自迭代的 Agent 工程知识库，一个跨 harness 的 [Agent Skill](https://agentskills.io/)：
让 Codex、Claude Code、ZCode 等编程智能体在回答 agent/LLM 工程问题时，
**先检索本地知识库、渐进阅读、联网补新、顺手入库**，而不是只依赖模型
训练截止日的旧知识。

## 它解决什么问题

- 模型知识截止早，最新 harness/agent 工程实践（PTC、managed agents、
  loop engineering、模型防御性对冲……）不在训练集里；
- 收藏一堆文章没有用——智能体必须能**毫秒级检索到"标题里没有、正文里有"
  的那篇**，并按需读，而不是把索引全塞进上下文；
- 知识库自己会烂：索引手写漂移、序号错乱、重复入库、薄条目泛滥。

## 设计

```text
agent-knowledge/
├── SKILL.md               # 入口：触发描述、检索 SOP、渐进阅读、入库最短路径
├── references/
│   ├── ingest.md          # 入库规范：来源范围、七步流程、frontmatter 模板、硬性禁令
│   ├── <分类>/            # 正文全文，每篇头部单行 YAML frontmatter
│   │   └── CATALOG.md     # 脚本再生的一行/篇浏览目录（⭐ core 置顶）
│   └── synthesis/         # 自有综合文章：结论+证据表+死链校验的相对链接
└── scripts/
    ├── kb.py              # lint（字段/URL 去重/slug/正文下限/死链）+ catalog + stats
    └── fetch.py           # URL → Markdown（arXiv/官方 .md/PDF/HTML，附 frontmatter 模板）
```

核心机制：

- **frontmatter 即索引**：全部字段单行，`rg` 一条命令同时搜元数据与全文；
  无独立索引文件，无同步问题；
- **渐进阅读**：结构层（`rg "^#"`）→ 摘要层（`sed 1,12p`）→ 精读层，
  候选 3-10 篇，CATALOG 只做定位不做内容源；
- **core 必读**：每类 ≤3 篇 `priority: core`，CATALOG ⭐ 置顶，lint 防稀释；
- **synthesis 层**：融合 ≥3 篇的自有综合，固定骨架（TL;DR→机制→证据表→
  对冲→护栏→链接），脱项目上下文可读，死链由 lint 机器校验；
- **防熵硬门**：入库必须过 `kb.py lint`（URL 唯一、正文 ≥600 字节、
  type 枚举、slug 规范）；薄内容并入 synthesis 引用，不单独建条目；
  目录白名单外的文件须用户批准。

## 安装

```bash
git clone https://github.com/NonTrivialLiu/agent-knowledge ~/.agents/skills/agent-knowledge
# Claude Code / ZCode 软链复用同一份
ln -s ~/.agents/skills/agent-knowledge ~/.claude/skills/agent-knowledge
ln -s ~/.agents/skills/agent-knowledge ~/.zcode/skills/agent-knowledge
```

依赖：`rg`、`python3`；抓取用 `uv run scripts/fetch.py`（依赖由 inline
metadata 自动解析）。

## 内容自建

仓库**只含框架，不含语料**——正文是各自抓取的第三方全文，请按
`references/ingest.md` 的七步流程为自己的领域建库（去重 → 抓取 →
frontmatter → 分类 → lint → catalog）。首次建库可批量执行，随后由
智能体在日常使用中自迭代维护。

## 维护

```bash
python3 scripts/kb.py lint     # 全库体检（任何 ERROR 须修复）
python3 scripts/kb.py catalog  # 从 frontmatter 再生各分类 CATALOG.md
python3 scripts/kb.py stats    # 规模与 core 分布
```

## License

MIT
