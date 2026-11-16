---
title: "Benchmarking Long-Horizon Agent Context Compaction with CompactionBench"
url: https://www.microsoft.com/en-us/research/publication/benchmarking-long-horizon-agent-context-compaction-with-compactionbench/
published: 2026-11-09
fetched: 2026-11-11
type: engineering-blog
topics: [context-memory, microsoft, context, compaction, evaluation, long-running]
summary: "微软研究基于 Copilot 生产轨迹分析同步压缩、前缀缓存与耗时，提出 CompactionBench 和异步渐进压缩 APEC；预印本，研究数字限其样本。注意核对具体投稿日是否在11月11日之前。"
---

> 收录范围：Microsoft 发布页摘要；全文预印本见 https://www.preprints.org/manuscript/202611.0780/v1 ，本机抓取受限。

# Benchmarking Long-Horizon Agent Context Compaction with CompactionBench

- Banruo Liu
  ,
- [Haoran Qiu](https://www.microsoft.com/en-us/research/people/haoranqiu/)
  ,
- [Íñigo Goiri](https://www.microsoft.com/en-us/research/people/inigog/)
  ,
- Jingran Zhou
  ,
- [Rodrigo Fonseca](https://www.microsoft.com/en-us/research/people/rofons/)
  ,
- [Ricardo Bianchini](https://www.microsoft.com/en-us/research/people/ricardob/)
  ,
- Fan Lai
  ,
- [Esha Choukse](https://www.microsoft.com/en-us/research/people/eschouks/)

November 2026

Preprints.org

[DOI](https://dx.doi.org/10.20944/preprints202611.0780.v1) | [Preprint](https://www.preprints.org/manuscript/202611.0780/v1)

[Download BibTex](https://www.microsoft.com/en-us/research/publication/benchmarking-long-horizon-agent-context-compaction-with-compactionbench/bibtex/)

Long-running coding agents rely on context compaction to overcome finite LLM context windows. Existing harnesses typically perform compaction synchronously, placing expensive summarization on the critical path and disrupting prefix-cache reuse. We deep-dive into compaction behavior and costs by analyzing 13.5M GitHub Copilot agentic coding sessions from 3.2M users, comprising 760M LLM calls. Although only 7.8% of sessions trigger compaction, they ac- count for 44.2% of total token consumption. Compaction also causes substantial foreground delay and sharply reduces prefix-cache reuse. To enable systematic evaluation, we first introduce COMPACTIONBENCH, a benchmark that models software evolution as persistent, multi-turn coding sessions. It enables controlled evaluation of repeated compaction while preserving executable task-level evaluation and reflecting context-growth patterns observed in production. We then present APEC, an asynchronous progressive compaction mechanism that pre- pares fine-grained, indexed summaries in the background and appends them to a stable prefix, moving compaction work off the critical path while preserving prefix reuse. APEC is harness-agnostic and treats summarization as a black box. Evaluated across frontier models, APEC improves task quality while reducing total cost by up to 25.4% and agent execution time by 9.6%.

Opens in a new tab
