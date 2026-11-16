---
title: "Recursive Agent Harnesses"
url: https://arxiv.org/abs/2606.13643
published: 2026-06-11
fetched: 2026-11-11
type: paper
topics: [loops-selfimprovement, harness]
summary: "把 RLM 的递归单位从模型调用扩展成有工具、文件和规划的完整 harness；父 agent 用代码并发启动子 harness。"
---

# Recursive Agent Harnesses

Elias Lumer
Affiliation: PricewaterhouseCoopers, U.S.
email: [elias.lumer@pwc.com](mailto:elias.lumer@pwc.com)
, 
Sahil Sen
Affiliation: PricewaterhouseCoopers, U.S.
email: [sahil.s.sen@pwc.com](mailto:sahil.s.sen@pwc.com)
, 
Kevin Paul
Affiliation: PricewaterhouseCoopers, U.S.
 and 
Vamse Kumar Subbiah
Affiliation: PricewaterhouseCoopers, U.S.

© none

## Abstract.

Recursive language models (RLMs) showed that recursion over model calls is an
effective strategy for long-context reasoning, and production coding agents have
begun to write code that spawns subagents at scale, most recently in Anthropic’s
dynamic workflows. We name and study the pattern between these two lines of work,
where the recursive unit is a full agent harness with filesystem tools, code
execution, and planning rather than a model call with no tools. We call this the
Recursive Agent Harness (RAH) and frame it as *harness recursion*, the
code-first extension to the *model recursion* of RLMs. A parent agent generates
and runs an executable script that spawns subagent harnesses in parallel for
fine-grained workloads and uses structured function calls for small subtasks. We
provide a controlled evaluation on long-context reasoning. With the backbone held
fixed at GPT-5 to match the published Codex and RLM baselines, RAH improves the Codex
coding-agent baseline from 71.75% to 81.36% on Oolong-Synthetic (199 samples, 13
context-length buckets up to 4M tokens), a gain attributable to the harness rather
than the model. With a stronger backbone, Claude Sonnet 4.5, the same design reaches
89.77%.

### Keywords:

Multi-Agent Systems, Long-Context Reasoning, Harness Recursion,
Code as Action, LLM Benchmarking, Oolong

![Refer to caption](https://arxiv.org/html/2606.13643v1/rah_architecture.png)

Figure 1. The Recursive Agent Harness (RAH). A parent agent selects between
code-execution spawning (writing an executable script that spawns
subagents in parallel) and JSON tool-call spawning
(for 1–5 entries). Subagents carry the same spawning capability
as their parent, enabling recursive decomposition bounded by a configurable
depth limit.

## 1. Introduction

Modern coding agents operate within an *agent harness*, the tools, filesystem, context
engineering, and orchestration that turn an LLM into a working agent
([Yang et al., 2024](https://arxiv.org/html/2606.13643#bib.bib1); [Jimenez et al., 2024](https://arxiv.org/html/2606.13643#bib.bib2); [Yao et al., 2023b](https://arxiv.org/html/2606.13643#bib.bib16); [Lumer et al., 2026a](https://arxiv.org/html/2606.13643#bib.bib13)). These harnesses navigate documents
far beyond a single context window
([Nakano et al., 2021](https://arxiv.org/html/2606.13643#bib.bib3); [Schick et al., 2023](https://arxiv.org/html/2606.13643#bib.bib4); [Qin et al., 2024](https://arxiv.org/html/2606.13643#bib.bib17)). Yet when a task requires
per-entry LLM reasoning across thousands of independent entries, the harness does not
*recurse*. It cannot spawn subagents that carry its own tools
([Liu et al., 2024a](https://arxiv.org/html/2606.13643#bib.bib20); [Lee et al., 2024](https://arxiv.org/html/2606.13643#bib.bib21)). When an agent
recurses over a long-context task, should the recursive unit be a model call with no tools or a full
harness?

Each approach has a different blind spot. Coding agents reduce per-entry reasoning to regex heuristics.
Even with full filesystem access, their context windows cannot accommodate thousands of
entries simultaneously, forcing them to skip entry-level LLM reasoning entirely
([Sumers et al., 2024](https://arxiv.org/html/2606.13643#bib.bib18); [Mialon et al., 2023](https://arxiv.org/html/2606.13643#bib.bib19)).
Conversely, recursive language models (RLMs) compose model calls recursively over sub-slices
of long inputs, performing reasoning that scales with the number of slices
([Zhang et al., 2026](https://arxiv.org/html/2606.13643#bib.bib6)). RLMs name and validate recursion over model calls, and recent
production systems extend the same instinct to code that spawns subagents ([Anthropic, 2026](https://arxiv.org/html/2606.13643#bib.bib31)).
We ask how far this pattern goes when the recursive unit is the full harness, and we name
and measure it. Benchmarks designed for long-context reasoning, such as Oolong,
expose the gap that motivates the comparison. Coding agents score low because of regex-limited
per-entry reasoning, while RLMs score low because of absent tool access.

We name this pattern the Recursive Agent Harness (RAH) and study it as a system
that spawns a full harness per entry through executable code
(Figure [1](https://arxiv.org/html/2606.13643#S0.F1 "Figure 1 ‣ Recursive Agent Harnesses")). Consider a concrete instance, an Oolong document
containing 1,772 labeled key–value pairs spread across 536K tokens. A coding agent
writes a single script that loops regex matches over the document, and an RLM recursively
partitions the context but has no file access. RAH’s parent agent instead writes a
script that issues one Task() per entry and runs them in parallel, and each call
resolves to an independent subagent harness with its own
context window, filesystem, and LLM call. Because the spawning logic is ordinary program code
rather than a fixed recursive-call convention or a schema-defined tool,
the parent can parametrize concurrency, per-entry instructions, and output paths in the same
language it uses for all other reasoning, and scale to entry counts that exhaust any
function-call budget.

RAH is evaluated on 199 randomly sampled instances from Oolong-Synthetic
([Cao et al., 2026](https://arxiv.org/html/2606.13643#bib.bib9)), stratified across all 13 context-length buckets from 1K to 4M
tokens, using GPT-5 as the backbone to match the Codex baseline. With the model held fixed,
RAH improves the Codex result from 71.75% to 81.36%, which attributes the gain to the
harness rather than the model. Gains are consistent across all context-length buckets
including 4M tokens.

### Scope of contribution.

We make three contributions. First, we name *Recursive Agent Harnesses* and define
*harness recursion*, the use of a full agent harness rather than a model call with no tools as
the recursive unit, and situate it as the code-first extension to the model recursion of
RLMs ([Zhang et al., 2026](https://arxiv.org/html/2606.13643#bib.bib6)). Second, we provide a controlled evaluation on long-context
reasoning with the backbone held fixed, so any difference is attributable to the harness
rather than the model. Third, we report results on Oolong-Synthetic across answer types and
context lengths, and relate the pattern to Anthropic’s dynamic
workflows ([Anthropic, 2026](https://arxiv.org/html/2606.13643#bib.bib31)), which adopt the same code-driven spawning in
production. The mechanism, code execution plus subagent spawning, is built from established
primitives ([Wang et al., 2024](https://arxiv.org/html/2606.13643#bib.bib28); [Zhang et al., 2026](https://arxiv.org/html/2606.13643#bib.bib6); [Wu et al., 2023](https://arxiv.org/html/2606.13643#bib.bib5)). Our contribution is naming the
pattern and evaluating it, not inventing the primitives.

## 2. Related Work

Cao et al. ([Cao et al., 2026](https://arxiv.org/html/2606.13643#bib.bib9)) apply a single coding agent that extracts per-entry answers with regex heuristics inside one context window, building off of previous work demonstrating the power of text-based search ([Sen et al., 2026b](https://arxiv.org/html/2606.13643#bib.bib12); [Sen et al., 2026a](https://arxiv.org/html/2606.13643#bib.bib27)). RAH instead spawns a subagent harness per entry or per group of entries, each with its own context window and tools, so a subagent can apply regex, reasoning, or both and cross-check the two rather than committing to regex alone.
Zhang et al. ([Zhang et al., 2026](https://arxiv.org/html/2606.13643#bib.bib6)) introduce recursive language models and establish that model recursion is an effective approach for long-context tasks, reaching 64.38% on Oolong-Synthetic. RAH treats harness recursion as the natural complement to their model recursion, extending the same axis they open by adding tool access and per-entry subagent reasoning. RAH does not replace model recursion. It asks what changes when the recursive unit is upgraded from a model call with no tools to a full harness, an axis that RLMs opened.
Minions ([Narayan et al., 2025](https://arxiv.org/html/2606.13643#bib.bib29)) and related orchestration frameworks fan work out to multiple worker models, and CodeAct ([Wang et al., 2024](https://arxiv.org/html/2606.13643#bib.bib28)) shows that writing and executing code is an effective agent action. RAH brings these together for long-context reasoning and provides the first controlled benchmark comparison against model recursion.
Anthropic’s dynamic workflows let a coding agent write a script that orchestrates subagents at scale and execute the orchestration as code rather than turn by turn ([Anthropic, 2026](https://arxiv.org/html/2606.13643#bib.bib31)). This is the same code-first spawning that RAH studies, and its arrival in a production system corroborates that recursion over agent harnesses is becoming a default strategy for tasks that exceed a single context window. We frame the pattern in the lineage of recursive language models rather than as a product workflow, treat it as model-agnostic and open to any harness, and contribute the controlled evaluation against model recursion that a product feature does not provide.

Lambda-RLM ([Roy et al., 2026](https://arxiv.org/html/2606.13643#bib.bib7)) decomposes long-context tasks through a deterministic pipeline with fixed structure and no tool access. RAH instead encodes spawning as an executable script that the parent generates at runtime, adapting structure to the workload rather than applying a predetermined schema.
AGENTHIVE ([Anonymous, 2026](https://arxiv.org/html/2606.13643#bib.bib11)) treats agent spawning as a first-class tool primitive defined in a schema. RAH encodes spawning directly in executable code, which lets the parent parametrize concurrency, output paths, and subagent instructions in the same language it uses for all other reasoning.
Parallel function calling ([Kim et al., 2024](https://arxiv.org/html/2606.13643#bib.bib23)) reduces latency by co-scheduling independent tool calls. RAH generalizes this idea to the level of entire agent invocations, spawning thousands of subagent harnesses rather than lightweight function calls.

Multi-agent conversation frameworks such as AutoGen ([Wu et al., 2023](https://arxiv.org/html/2606.13643#bib.bib5)) and AgentVerse ([Chen et al., 2024](https://arxiv.org/html/2606.13643#bib.bib22)) coordinate agents through shared message threads. RAH instead isolates each subagent’s context to prevent interference and enable deterministic aggregation through shared output files.
Embodied open-ended agents such as Voyager ([Wang et al., 2023](https://arxiv.org/html/2606.13643#bib.bib25)) show that LLMs can write and execute programs as a form of persistent skill acquisition. RAH applies the same code-as-action insight to parallel document processing rather than sequential exploration.
MemGPT ([Packer et al., 2023](https://arxiv.org/html/2606.13643#bib.bib24)) addresses context limits by paging between main and external memory within a single agent. RAH instead distributes work across independent subagents, avoiding shared state entirely and scaling to entry counts that exceed what any paging scheme can address.
AgentBench ([Liu et al., 2024b](https://arxiv.org/html/2606.13643#bib.bib26)) provides a multi-environment benchmark for evaluating LLMs as agents. Oolong complements AgentBench by focusing on aggregation over millions of tokens, a workload not covered by existing agent benchmarks.

## 3. Recursive Agent Harness

### 3.1. Overview

RAH makes the full agent harness, rather than a model call with no tools, the recursive unit (Figure [1](https://arxiv.org/html/2606.13643#S0.F1 "Figure 1 ‣ Recursive Agent Harnesses")).
RAH treats code as a first-class action rather than a fixed tool schema, following the code-as-action view that writing and running a program is a more expressive way to orchestrate tools than emitting one structured call at a time ([Wang et al., 2024](https://arxiv.org/html/2606.13643#bib.bib28)).
A parent agent receives the full task and inspects the document to determine workload size.
It spawns subagents through one primitive that the harness exposes two ways.
The baseline path is standard JSON tool calling, where the parent emits a structured call and the harness runs the subagent.
JSON tool calling is capped by the per-turn parallel tool-call budget.
RAH’s contribution is the code-execution path, where the parent writes an executable script that instantiates subagents and runs them in parallel through its shell tool.
The code-execution path bypasses the per-turn cap and scales to thousands of subagent harnesses in parallel.
It is a harness primitive, not a system-prompt convention.
Every subagent carries the same tools and spawning capability as its parent, so the decomposition is recursive rather than one level of fan-out.

### 3.2. Code-Execution Spawning

For fine-grained workloads, the parent agent writes a self-contained script in which each subagent task is instantiated as a Task() object and all tasks are collected into a single asynchronous call that runs them in parallel. The number of subagents is set by the workload rather than any fixed cap, since it is simply a parameter in the generated code.
RAH is implemented with the LangChain agent framework package ([LangChain, 2022](https://arxiv.org/html/2606.13643#bib.bib10)). The approach is otherwise independent of the implementation language. Our system emits Python and runs subagents under asyncio.gather, but any general-purpose language with concurrency primitives would serve.
The parent executes the script through its shell tool and receives only the aggregated stdout output once all subagents complete. Intermediate subagent reasoning, tool calls, and filesystem writes are invisible to the parent.
The script path sidesteps a practical constraint. JSON tool calling is bounded by the API’s per-turn tool-call limit, whereas a script executed in a subprocess carries no such restriction, so spawning scale is controlled by the workload rather than the provider’s protocol.
Each subagent is a full agent harness equipped with read_file, write_file, ls, glob, grep, execute, and web search, along with a planning step before execution. It operates inside an isolated workspace with no access to the parent context or to peer subagents.
The parent collects results by reading a shared output file that all subagents write to upon completion, avoiding any inter-process communication overhead.

### 3.3. JSON Tool-Call Spawning

For subtasks of one to five entries, the parent calls the Task tool directly as a structured function call, passing entry content and instructions as arguments without generating an intermediate script.
Subagents spawned through JSON tool calling carry identical tool access and planning capability to those spawned through scripts, so the quality of per-entry reasoning is path-independent.
The parent selects the spawning path automatically based on entry count, ensuring that script-generation overhead is incurred only when the parallelism benefit justifies it.

### 3.4. Subagent Architecture

Subagents run an agent loop, alternating between planning, tool use, and reflection until a stopping condition is met ([Wei et al., 2022](https://arxiv.org/html/2606.13643#bib.bib14); [Yao et al., 2023a](https://arxiv.org/html/2606.13643#bib.bib15)).
Each subagent receives a bounded context with its assigned entry, relevant document excerpts, and output-format instructions. No shared memory or communication channel exists between sibling subagents, so each subagent reasons independently.
Each subagent is itself a full harness with the same tools, planning, and spawning capability as its parent, so the recursive unit is a harness rather than a model call. A subagent that meets a complex entry can write its own script and spawn grandchild harnesses, which makes the decomposition genuinely recursive rather than one level of fan-out.
Recursion depth is bounded by a configurable limit (default 3), which prevents unbounded tree growth while allowing multi-level decomposition when the workload warrants it.
The output of each subagent is a structured JSON record written to a designated path, which the parent script aggregates into a final answer after all subagent tasks resolve.

## 4. Experiments

### 4.1. Experimental Setup

We evaluate harness recursion on long-context reasoning to answer two questions. First,
does making the harness the recursive unit improve over coding agents and over model
recursion? Second, how does performance vary by answer type and context length?
Oolong is a long-context reasoning benchmark that tests whether a model can aggregate
information distributed across millions of tokens rather than retrieve a single salient
span ([Bertsch et al., 2025](https://arxiv.org/html/2606.13643#bib.bib8)), a setting on which frontier models score below 50% at 128K
context. Evaluation uses 199 samples drawn from the Oolong-Synthetic validation split
([Cao et al., 2026](https://arxiv.org/html/2606.13643#bib.bib9)), stratified across all 13 context-length buckets ranging
from 1K to 4M tokens (average 629K tokens per instance).
The sample size preserves the benchmark’s bucket distribution while remaining
tractable under the per-instance agent cost.
RAH is compared against three baselines reported by Cao et al. ([Cao et al., 2026](https://arxiv.org/html/2606.13643#bib.bib9)). These are a
full-context baseline that feeds the entire document to a frontier model
(Oolong Score 59.22%), an RLM configuration (64.38%), and a coding-agent
configuration using Codex-style reasoning with no retriever (71.75%), which
represents the strongest prior result on this split. All prior results evaluate on the same 199-sample protocol.
Scoring follows the Oolong protocol, using exact match for LABEL, COMPARISON, USER,
and DATE answer types and `0.75^{|y-\hat{y}|}` for NUMERIC responses, which
rewards near-miss predictions on continuous quantities. The reported Oolong Score is a
micro-average over the 199 instances. We pair point estimates with 95% bootstrap
confidence intervals from 10,000 resamples of the per-instance scores.
RAH uses GPT-5 (gpt-5-2025-08-07) for the parent agent, every subagent, and the
answer-extraction call, matching the Codex baseline exactly, so any performance difference
is attributable to the harness architecture rather than model choice. The second
configuration uses Claude Sonnet 4.5 (claude-sonnet-4-5-20250929) as the backbone.
All runs use temperature zero. Final answers are extracted from subagent output through a
separate call using a fixed prompt asking for the answer in the exact format specified by
the question (Appendix [C](https://arxiv.org/html/2606.13643#A3 "Appendix C Answer-Extraction Prompt ‣ Recursive Agent Harnesses")). Because every answer passes through this GPT-5 extraction step while the
backbone under test is also GPT-5, the extractor and the system share a model family. Final
scoring is deterministic, using exact match and the numeric formula above rather than a model
judge, so the extraction step only maps raw output to the answer format and does not assign
scores. Raw outputs are typically already in that format, for example Label: spam,
which limits the influence of the extractor. We did not run a separate human validation of the
extraction step and note it as a limitation.

### 4.2. Main Results

Table 1. Oolong Score on Oolong-Synthetic (199 samples, 13 context-length
buckets, GPT-5 backbone). Bold indicates best.
The full-context, RLM ([Zhang et al., 2026](https://arxiv.org/html/2606.13643#bib.bib6)), and Codex baseline scores
are all as measured and reported by Cao et al. ([Cao et al., 2026](https://arxiv.org/html/2606.13643#bib.bib9)).

| Method | Oolong Score |
| --- | --- |
| Full-context baseline | 59.22% |
| RLM ([Zhang et al., 2026](https://arxiv.org/html/2606.13643#bib.bib6)) | 64.38% |
| Codex, No Retriever ([Cao et al., 2026](https://arxiv.org/html/2606.13643#bib.bib9)) | 71.75% |
| RAH, GPT-5 (ours) | 81.36% |
| RAH, Sonnet 4.5 (ours) | 89.77% |

![Refer to caption](https://arxiv.org/html/2606.13643v1/rah_results.png)

Figure 2. Oolong Score on Oolong-Synthetic (199 samples), mirroring
Table [1](https://arxiv.org/html/2606.13643#S4.T1 "Table 1 ‣ 4.2. Main Results ‣ 4. Experiments ‣ Recursive Agent Harnesses"). The three baselines all use a GPT-5 backbone and are
reported by Cao et al. ([Cao et al., 2026](https://arxiv.org/html/2606.13643#bib.bib9)). With the backbone matched to Codex
at GPT-5, RAH improves on the strongest prior result (dashed line), and the same design
reaches 89.77% on Claude Sonnet 4.5.

Table [1](https://arxiv.org/html/2606.13643#S4.T1 "Table 1 ‣ 4.2. Main Results ‣ 4. Experiments ‣ Recursive Agent Harnesses") and Figure [2](https://arxiv.org/html/2606.13643#S4.F2 "Figure 2 ‣ 4.2. Main Results ‣ 4. Experiments ‣ Recursive Agent Harnesses") summarize the main results.
Holding the backbone fixed at GPT-5, RAH improves the strongest prior result,
the Codex coding agent, from 71.75% to 81.36%. Because both use GPT-5, this
controlled comparison attributes the difference to the harness rather than the
model. The same model that scores 71.75% with a regex loop scores 81.36% when
the recursive unit is a full harness. Treating the published baselines as fixed
reference points, since we do not have their per-instance scores, a bootstrap over the
199 RAH scores places the gain at `+9.61` points over Codex (95% CI `[4.2,14.8]`) and
`+16.98` over RLM (95% CI `[11.5,22.0]`), and both intervals exclude zero. The overall
score is 81.36% (95% CI `[76.0,86.5]`). RAH also moves well past RLM, which reaches
64.38% in this setting where it cannot open files, run code, or call external
services, showing that tool access and filesystem navigation complement recursive
LLM invocation. The design scales with the backbone as well, reaching 89.77% on
Claude Sonnet 4.5, which suggests that harness recursion compounds with model
quality rather than substituting for it. Every RAH instance produced a
Task() script, so all samples followed the code-execution path, reflecting
that Oolong-Synthetic workloads uniformly exceed the five-entry threshold for the
JSON tool-calling path.

### 4.3. Per-Category Analysis

Table 2. RAH Oolong Score by answer type on the 199-sample evaluation set.
`n` denotes the number of instances of each type. Intervals are 95% bootstrap CIs.

| Answer Type | Score | 95% CI | `n` |
| --- | --- | --- | --- |
| USER | 87.27% | [78.2, 94.5] | 55 |
| COMPARISON | 89.29% | [78.6, 100.0] | 28 |
| LABEL | 86.54% | [76.9, 94.2] | 52 |
| DATE | 60.00% | [20.0, 100.0] | 5 |
| NUMERIC | 69.33% | [57.9, 80.1] | 59 |
| Overall | 81.36% | [76.0, 86.5] | 199 |

Table [2](https://arxiv.org/html/2606.13643#S4.T2 "Table 2 ‣ 4.3. Per-Category Analysis ‣ 4. Experiments ‣ Recursive Agent Harnesses") breaks results down by answer type.
Semantic types (USER, COMPARISON, LABEL) all exceed 86%, confirming that
subagents produce reliable reasoning regardless of where in the
4M-token context the relevant key–value pairs reside.
NUMERIC performance degrades to 69.33% because the `0.75^{|y-\hat{y}|}`
scoring function penalizes off-by-`k` predictions compoundingly. An answer
off by one unit receives 0.75 and off by two receives 0.5625. This penalty
amplifies small counting errors into a visible score gap even when subagent
reasoning is correct. DATE (`n=5`) should be interpreted
cautiously given the small sample.

### 4.4. Per-Context-Length Analysis

Table 3. RAH Oolong Score across all 13 context-length buckets (`n{=}14`–`16` per bucket).
The Codex baseline is 71.75% flat across all buckets.

| Context | GPT-5 | Sonnet 4.5 |
| --- | --- | --- |
| 1K | 100.0% | 93.8% |
| 2K | 93.8% | 90.6% |
| 4K | 94.1% | 94.1% |
| 8K | 94.5% | 96.9% |
| 16K | 93.0% | 90.6% |
| 32K | 86.7% | 90.4% |
| 64K | 92.3% | 100.0% |
| 131K | 73.3% | 87.6% |
| 262K | 57.1% | 92.0% |
| 524K | 80.0% | 86.7% |
| 1M | 53.3% | 80.0% |
| 2M | 66.7% | 86.7% |
| 4M | 66.7% | 76.7% |

Table [3](https://arxiv.org/html/2606.13643#S4.T3 "Table 3 ‣ 4.4. Per-Context-Length Analysis ‣ 4. Experiments ‣ Recursive Agent Harnesses") reports scores across all 13 context-length buckets.
Sonnet 4.5 remains above 86% through 524K tokens and above 76% through 4M,
with no monotone degradation. The 64K bucket reaches 100% and 262K outperforms
131K, which indicates that entry-count distribution within each bucket matters as much
as raw document length. GPT-5 follows the same broad pattern at lower magnitudes,
with a pronounced dip at 262K and 1M driven by NUMERIC-heavy instances. Both
configurations exceed the 71.75% Codex baseline at the majority of context
lengths including 4M tokens. Per-bucket estimates rest on 14 to 16 instances and carry
wide intervals. The 1M bucket, for example, is 53.3% with a 95% CI of `[26.7,80.0]`,
so we read bucket-level numbers as trends rather than precise points.

### 4.5. Cost and Latency

The cost of RAH scales with the number of subagents the parent chooses to spawn, which the
parent sets by deciding how many entries each subagent handles rather than fixing one
subagent per entry. The dominant recurring cost is each subagent re-reading the shared
document context. Prompt caching addresses this directly, since every subagent shares a
common context prefix, and prior work reports that caching can cut token cost by up to
80% on long-horizon agentic workloads ([Lumer et al., 2026b](https://arxiv.org/html/2606.13643#bib.bib30)). Latency is bounded by
parallelism rather than by the count of subagents, because the parent’s generated script
runs all subagents in parallel and waits only for the slowest
to return. We did not instrument exact token and wall-clock profiles for the GPT-5
configuration and leave precise cost characterization to future work.

### 4.6. Failure Modes

Three patterns account for most of the lost score. First, on a small number of instances
the parent answered directly without writing a spawning script, which collapses RAH to a
single coding agent and discards the per-entry reasoning the harness provides. These cases
concentrate at longer context lengths, where the parent is more likely to treat the task as
retrieval. Second, NUMERIC questions lose score even when subagent reasoning is sound,
because the `0.75^{|y-\hat{y}|}` function penalizes an off-by-one count down to 0.75 and an
off-by-two count down to 0.5625. Third, answer types with few instances, such as DATE with
`n=5`, show high variance, so a single incorrect response moves the reported score by a
large amount and the 60.00% DATE figure reflects sample size more than a systematic
weakness.

### 4.7. Choosing a Recursion Strategy

The recursive unit is the deciding factor when choosing among recursion strategies.
Table [4](https://arxiv.org/html/2606.13643#S4.T4 "Table 4 ‣ 4.7. Choosing a Recursion Strategy ‣ 4. Experiments ‣ Recursive Agent Harnesses") contrasts the options. Coding agents pair a full harness with no
recursion and suit navigation over modest entry counts. Model recursion recurses over bare
model calls without tools and suits decomposition where tool use is unnecessary. Dynamic
workflows spawn subagents from a script and suit repeatable orchestration at scale. Harness
recursion makes the full harness the recursive unit, which suits per-entry reasoning at scale
where each entry may need tools.

Table 4. Recursion strategies by recursive unit.

| Strategy | Recursive unit | Strengths |
| --- | --- | --- |
| Coding agent | none (single harness) | navigation, few entries |
| Model recursion (RLM) | model call, no tools | decomposition without tools |
| Dynamic workflows | subagent from a script | repeatable orchestration |
| Harness recursion (RAH) | full agent harness | per-entry reasoning at scale |

## 5. Limitations

The evaluation is limited to Oolong-Synthetic. Generalization to Oolong-Real and to
domains where per-entry evidence is more ambiguous or less literally present in the
context remains an open question. The failure modes above also bound the result, in
particular the parent occasionally skipping spawning at long context lengths and the
NUMERIC scoring penalty that understates reasoning quality on continuous-quantity tasks.
RAH further depends on the parent agent reliably generating syntactically correct spawning
scripts, and exact token and latency profiles for the GPT-5 configuration remain
uninstrumented. We do not ablate individual design choices such as recursion depth, the
number of entries per subagent, or the code-execution versus tool-call spawning path.
Isolating their contributions is left to future work.

## 6. Conclusion

We name and evaluate the Recursive Agent Harness (RAH), the pattern of recursing over a full
agent harness rather than a model call with no tools. Long-context reasoning requires both
large-scale document navigation and per-entry LLM reasoning across thousands of independent
entries, and prior approaches provide only one. Coding agents reduce per-entry reasoning to
regex heuristics, while recursive language models lack filesystem access, code execution, and
external tools. Using GPT-5 to match the Codex baseline, RAH improves the strongest prior
result from 71.75% to 81.36% with no change in model, which attributes the gain to the
harness rather than the model. The pattern is already appearing in production systems such as
dynamic workflows. Our aim is to name it, place it in the lineage of recursive language models,
and measure it. The design should transfer to other settings that decompose into independent
per-entry subtasks over a corpus larger than the context window, such as multi-document
question answering and review of large document sets, which we leave to future work alongside
a characterization of the cost-quality tradeoff.

## Code and Data Availability

The Recursive Agent Harness implementation and the evaluation and scoring scripts will be
released shortly. The Oolong-Synthetic data and the published baseline numbers are due to
Cao et al. ([Cao et al., 2026](https://arxiv.org/html/2606.13643#bib.bib9)) and Zhang et al. ([Zhang et al., 2026](https://arxiv.org/html/2606.13643#bib.bib6)). The parent, subagent,
and answer-extraction prompts are reproduced in full in Appendices [A](https://arxiv.org/html/2606.13643#A1 "Appendix A Parent Agent Prompt ‣ Recursive Agent Harnesses"),
[B](https://arxiv.org/html/2606.13643#A2 "Appendix B Subagent Prompts ‣ Recursive Agent Harnesses"), and [C](https://arxiv.org/html/2606.13643#A3 "Appendix C Answer-Extraction Prompt ‣ Recursive Agent Harnesses").

## References

- Anonymous (2026)
  Anonymous
  AGENTHIVE: a composable multi-agent framework with first-class delegation.
  Note: ACL ARR 2026 January submission. openreview.net/forum?id=BYiwNYYixO.
  Authors are anonymous (double-blind). Replace with deanonymized authors
  upon publication.
  Cited by: [§2](https://arxiv.org/html/2606.13643#S2.p2.1 "2. Related Work ‣ Recursive Agent Harnesses").
- Anthropic (2026)
  Anthropic
  Orchestrate subagents at scale with dynamic workflows.
  Note: <https://code.claude.com/docs/en/workflows>Claude Code documentation, research preview. Accessed 2026-06-06
  Cited by: [§1](https://arxiv.org/html/2606.13643#S1.SS0.SSS0.Px1.p1.1 "Scope of contribution. ‣ 1. Introduction ‣ Recursive Agent Harnesses"),
  [§1](https://arxiv.org/html/2606.13643#S1.p2.1 "1. Introduction ‣ Recursive Agent Harnesses"),
  [§2](https://arxiv.org/html/2606.13643#S2.p1.1 "2. Related Work ‣ Recursive Agent Harnesses").
- Bertsch et al. (2025)
  A. Bertsch, A. Pratapa, T. Mitamura, G. Neubig, and M. R. Gormley
  Oolong: evaluating long context reasoning and aggregation capabilities.
  arXiv preprint arXiv:2511.02817.
  Note: arXiv:2511.02817
  Cited by: [§4.1](https://arxiv.org/html/2606.13643#S4.SS1.p1.1 "4.1. Experimental Setup ‣ 4. Experiments ‣ Recursive Agent Harnesses").
- Cao et al. (2026)
  W. Cao, X. Yin, B. Dhingra, and S. Zhou
  Coding agents are effective long-context processors.
  arXiv preprint arXiv:2603.20432.
  Note: arXiv:2603.20432
  Cited by: [§1](https://arxiv.org/html/2606.13643#S1.p4.1 "1. Introduction ‣ Recursive Agent Harnesses"),
  [§2](https://arxiv.org/html/2606.13643#S2.p1.1 "2. Related Work ‣ Recursive Agent Harnesses"),
  [Figure 2](https://arxiv.org/html/2606.13643#S4.F2 "In 4.2. Main Results ‣ 4. Experiments ‣ Recursive Agent Harnesses"),
  [Figure 2](https://arxiv.org/html/2606.13643#S4.F2.4 "In 4.2. Main Results ‣ 4. Experiments ‣ Recursive Agent Harnesses"),
  [§4.1](https://arxiv.org/html/2606.13643#S4.SS1.p1.1 "4.1. Experimental Setup ‣ 4. Experiments ‣ Recursive Agent Harnesses"),
  [Table 1](https://arxiv.org/html/2606.13643#S4.T1 "In 4.2. Main Results ‣ 4. Experiments ‣ Recursive Agent Harnesses"),
  [Table 1](https://arxiv.org/html/2606.13643#S4.T1.4 "In 4.2. Main Results ‣ 4. Experiments ‣ Recursive Agent Harnesses"),
  [Table 1](https://arxiv.org/html/2606.13643#S4.T1.5.4.1 "In 4.2. Main Results ‣ 4. Experiments ‣ Recursive Agent Harnesses"),
  [Code and Data Availability](https://arxiv.org/html/2606.13643#Sx1.p1.1 "Code and Data Availability ‣ Recursive Agent Harnesses").
- Chen et al. (2024)
  W. Chen, Y. Su, J. Zuo, C. Yang, C. Yuan, C. Qian, C. Chan, Y. Qin, Y. Lu, R. Xie, Z. Liu, M. Sun, and J. Zhou
  AgentVerse: facilitating multi-agent collaboration and exploring emergent behaviors.
  In International Conference on Learning Representations,
  Note: arXiv:2308.10848
  Cited by: [§2](https://arxiv.org/html/2606.13643#S2.p3.1 "2. Related Work ‣ Recursive Agent Harnesses").
- Jimenez et al. (2024)
  C. E. Jimenez, J. Yang, A. Wettig, S. Yao, K. Pei, O. Press, and K. Narasimhan
  SWE-bench: can language models resolve real-world GitHub issues?.
  In International Conference on Learning Representations,
  Note: arXiv:2310.06770
  Cited by: [§1](https://arxiv.org/html/2606.13643#S1.p1.1 "1. Introduction ‣ Recursive Agent Harnesses").
- Kim et al. (2024)
  S. Kim, S. Moon, R. Tabrizi, N. Lee, M. W. Mahoney, K. Keutzer, and A. Gholami
  An LLM compiler for parallel function calling.
  In International Conference on Machine Learning,
  Note: arXiv:2312.04511
  Cited by: [§2](https://arxiv.org/html/2606.13643#S2.p2.1 "2. Related Work ‣ Recursive Agent Harnesses").
- LangChain (2022)
  LangChain
  LangChain.
  External Links: [Link](https://www.langchain.com/)
  Cited by: [§3.2](https://arxiv.org/html/2606.13643#S3.SS2.p1.1 "3.2. Code-Execution Spawning ‣ 3. Recursive Agent Harness ‣ Recursive Agent Harnesses").
- Lee et al. (2024)
  J. Lee, A. Ing, Z. Dai, S. Narang, K. Guu, B. Pitchford, M. Chang, S. Wan, R. Tanno, C. D. Freeman, S. de Jong, A. Gretton, and M. Joshi
  Can long-context language models subsume retrieval, RAG, SQL, and more?.
  In Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics,
  Note: arXiv:2406.13121
  Cited by: [§1](https://arxiv.org/html/2606.13643#S1.p1.1 "1. Introduction ‣ Recursive Agent Harnesses").
- Liu et al. (2024a)
  N. F. Liu, K. Lin, J. Hewitt, A. Paranjape, M. Bevilacqua, F. Petroni, and P. Liang
  Lost in the middle: how language models use long contexts.
  Transactions of the Association for Computational Linguistics 12, pp. 157–173.
  Note: arXiv:2307.03172
  Cited by: [§1](https://arxiv.org/html/2606.13643#S1.p1.1 "1. Introduction ‣ Recursive Agent Harnesses").
- Liu et al. (2024b)
  X. Liu, H. Yu, H. Zhang, Y. Xu, X. Lei, H. Lai, Y. Gu, H. Ding, K. Men, K. Yang, S. Zhang, X. Deng, A. Zeng, Z. Du, C. Zhang, S. Shen, T. Fu, Y. Liu, Z. Yao, R. Zhang, J. Jia, J. Tang, Y. Liu, and Y. Dong
  AgentBench: evaluating LLMs as agents.
  In International Conference on Learning Representations,
  Note: arXiv:2308.03688
  Cited by: [§2](https://arxiv.org/html/2606.13643#S2.p3.1 "2. Related Work ‣ Recursive Agent Harnesses").
- Lumer et al. (2026a)
  E. Lumer, A. Gulati, F. Nizar, D. Hedroits, A. Mehta, H. Hwangbo, V. K. Subbiah, P. H. Basavaraju, and J. A. Burke
  Tool and agent selection for large language model agents in production: a survey.
  In 2026 IEEE Conference on Artificial Intelligence (CAI),
  pp. 701–708.
  Cited by: [§1](https://arxiv.org/html/2606.13643#S1.p1.1 "1. Introduction ‣ Recursive Agent Harnesses").
- Lumer et al. (2026b)
  E. Lumer, F. Nizar, A. Jangiti, K. Frank, A. Gulati, M. Phadate, and V. K. Subbiah
  Don’t break the cache: an evaluation of prompt caching for long-horizon agentic tasks.
  arXiv preprint arXiv:2601.06007.
  Cited by: [§4.5](https://arxiv.org/html/2606.13643#S4.SS5.p1.1 "4.5. Cost and Latency ‣ 4. Experiments ‣ Recursive Agent Harnesses").
- Mialon et al. (2023)
  G. Mialon, R. Dessì, M. Lomeli, C. Nalmpantis, R. Pasunuru, R. Raileanu, B. Rozière, T. Schick, J. Dwivedi-Yu, A. Celikyilmaz, E. Grave, Y. LeCun, and T. Scialom
  Augmented language models: a survey.
  Transactions on Machine Learning Research.
  Note: arXiv:2302.07842
  Cited by: [§1](https://arxiv.org/html/2606.13643#S1.p2.1 "1. Introduction ‣ Recursive Agent Harnesses").
- Nakano et al. (2021)
  R. Nakano, J. Hilton, S. Balaji, J. Wu, L. Ouyang, C. Kim, C. Hesse, S. Jain, V. Kosaraju, W. Saunders, X. Jiang, K. Cobbe, T. Eloundou, G. Krueger, K. Button, M. Knight, B. Chess, and J. Schulman
  WebGPT: browser-assisted question-answering with human feedback.
  arXiv preprint arXiv:2112.09332.
  Cited by: [§1](https://arxiv.org/html/2606.13643#S1.p1.1 "1. Introduction ‣ Recursive Agent Harnesses").
- Narayan et al. (2025)
  A. Narayan, D. Biderman, S. Eyuboglu, A. May, S. Linderman, J. Zou, and C. Re
  Minions: cost-efficient collaboration between on-device and cloud language models.
  External Links: 2502.15964,
  [Link](https://arxiv.org/abs/2502.15964)
  Cited by: [§2](https://arxiv.org/html/2606.13643#S2.p1.1 "2. Related Work ‣ Recursive Agent Harnesses").
- Packer et al. (2023)
  C. Packer, S. Wooders, K. Lin, V. Fang, S. G. Patil, I. Stoica, and J. E. Gonzalez
  MemGPT: towards LLMs as operating systems.
  arXiv preprint arXiv:2310.08560.
  Cited by: [§2](https://arxiv.org/html/2606.13643#S2.p3.1 "2. Related Work ‣ Recursive Agent Harnesses").
- Qin et al. (2024)
  Y. Qin, S. Liang, Y. Ye, K. Zhu, L. Yan, Y. Lu, Y. Lin, X. Cong, X. Tang, B. Qian, S. Zhao, L. Hong, R. Tian, R. Xie, J. Zhou, M. Gerstein, D. Li, Z. Liu, and M. Sun
  ToolLLM: facilitating large language models to master 16000+ real-world APIs.
  In International Conference on Learning Representations,
  Note: arXiv:2307.16789
  Cited by: [§1](https://arxiv.org/html/2606.13643#S1.p1.1 "1. Introduction ‣ Recursive Agent Harnesses").
- Roy et al. (2026)
  A. Roy, R. Tutunov, X. Ji, M. Zimmer, and H. Bou-Ammar
  The Y-combinator for LLMs: solving long-context rot with `\lambda`-calculus.
  arXiv preprint arXiv:2603.20105.
  Note: Submitted 20 Mar 2026.
  Cited by: [§2](https://arxiv.org/html/2606.13643#S2.p2.1 "2. Related Work ‣ Recursive Agent Harnesses").
- Schick et al. (2023)
  T. Schick, J. Dwivedi-Yu, R. Dessì, R. Raileanu, M. Lomeli, L. Zettlemoyer, N. Cancedda, and T. Scialom
  Toolformer: language models can teach themselves to use tools.
  In Advances in Neural Information Processing Systems,
  Note: arXiv:2302.04761
  Cited by: [§1](https://arxiv.org/html/2606.13643#S1.p1.1 "1. Introduction ‣ Recursive Agent Harnesses").
- Sen et al. (2026a)
  S. Sen, A. Kasturi, E. Lumer, A. Gulati, and V. K. Subbiah
  Is grep all you need? how agent harnesses reshape agentic search.
  arXiv preprint arXiv:2605.15184.
  External Links: [Link](https://arxiv.org/abs/2605.15184)
  Cited by: [§2](https://arxiv.org/html/2606.13643#S2.p1.1 "2. Related Work ‣ Recursive Agent Harnesses").
- Sen et al. (2026b)
  S. Sen, E. Lumer, A. Gulati, and V. K. Subbiah
  Chronos: temporal-aware conversational agents with structured event retrieval for long-term memory.
  arXiv preprint arXiv:2603.16862.
  Cited by: [§2](https://arxiv.org/html/2606.13643#S2.p1.1 "2. Related Work ‣ Recursive Agent Harnesses").
- Sumers et al. (2024)
  T. R. Sumers, S. Yao, K. Narasimhan, and T. L. Griffiths
  Cognitive architectures for language agents.
  Transactions on Machine Learning Research.
  Note: arXiv:2309.02427
  Cited by: [§1](https://arxiv.org/html/2606.13643#S1.p2.1 "1. Introduction ‣ Recursive Agent Harnesses").
- Wang et al. (2023)
  G. Wang, Y. Xie, Y. Jiang, A. Mandlekar, C. Xiao, Y. Zhu, L. Fan, and A. Anandkumar
  Voyager: an open-ended embodied agent with large language models.
  arXiv preprint arXiv:2305.16291.
  Cited by: [§2](https://arxiv.org/html/2606.13643#S2.p3.1 "2. Related Work ‣ Recursive Agent Harnesses").
- Wang et al. (2024)
  X. Wang, Y. Chen, L. Yuan, Y. Zhang, Y. Li, H. Peng, and H. Ji
  Executable code actions elicit better LLM agents.
  External Links: 2402.01030,
  [Link](https://arxiv.org/abs/2402.01030)
  Cited by: [§1](https://arxiv.org/html/2606.13643#S1.SS0.SSS0.Px1.p1.1 "Scope of contribution. ‣ 1. Introduction ‣ Recursive Agent Harnesses"),
  [§2](https://arxiv.org/html/2606.13643#S2.p1.1 "2. Related Work ‣ Recursive Agent Harnesses"),
  [§3.1](https://arxiv.org/html/2606.13643#S3.SS1.p1.1 "3.1. Overview ‣ 3. Recursive Agent Harness ‣ Recursive Agent Harnesses").
- Wei et al. (2022)
  J. Wei, X. Wang, D. Schuurmans, M. Bosma, B. Ichter, F. Xia, E. Chi, Q. Le, and D. Zhou
  Chain-of-thought prompting elicits reasoning in large language models.
  In Advances in Neural Information Processing Systems,
  Note: arXiv:2201.11903
  Cited by: [§3.4](https://arxiv.org/html/2606.13643#S3.SS4.p1.1 "3.4. Subagent Architecture ‣ 3. Recursive Agent Harness ‣ Recursive Agent Harnesses").
- Wu et al. (2023)
  Q. Wu, G. Bansal, J. Zhang, Y. Wu, B. Li, E. Zhu, L. Jiang, X. Zhang, S. Zhang, J. Liu, A. H. Awadallah, R. W. White, D. Burger, and C. Wang
  AutoGen: enabling next-gen LLM applications via multi-agent conversation.
  External Links: 2308.08155,
  [Link](https://arxiv.org/abs/2308.08155)
  Cited by: [§1](https://arxiv.org/html/2606.13643#S1.SS0.SSS0.Px1.p1.1 "Scope of contribution. ‣ 1. Introduction ‣ Recursive Agent Harnesses"),
  [§2](https://arxiv.org/html/2606.13643#S2.p3.1 "2. Related Work ‣ Recursive Agent Harnesses").
- Yang et al. (2024)
  J. Yang, C. E. Jimenez, A. Wettig, K. Lieret, S. Yao, K. Narasimhan, and O. Press
  SWE-agent: agent-computer interfaces enable automated software engineering.
  In Advances in Neural Information Processing Systems,
  Note: arXiv:2405.15793
  Cited by: [§1](https://arxiv.org/html/2606.13643#S1.p1.1 "1. Introduction ‣ Recursive Agent Harnesses").
- Yao et al. (2023a)
  S. Yao, D. Yu, J. Zhao, I. Shafran, T. L. Griffiths, Y. Cao, and K. Narasimhan
  Tree of thoughts: deliberate problem solving with large language models.
  In Advances in Neural Information Processing Systems,
  Note: arXiv:2305.10601
  Cited by: [§3.4](https://arxiv.org/html/2606.13643#S3.SS4.p1.1 "3.4. Subagent Architecture ‣ 3. Recursive Agent Harness ‣ Recursive Agent Harnesses").
- Yao et al. (2023b)
  S. Yao, J. Zhao, D. Yu, N. Du, I. Shafran, K. Narasimhan, and Y. Cao
  ReAct: synergizing reasoning and acting in language models.
  In International Conference on Learning Representations,
  Note: arXiv:2210.03629
  Cited by: [§1](https://arxiv.org/html/2606.13643#S1.p1.1 "1. Introduction ‣ Recursive Agent Harnesses").
- Zhang et al. (2026)
  A. L. Zhang, T. Kraska, and O. Khattab
  Recursive language models.
  External Links: 2512.24601,
  [Link](https://arxiv.org/abs/2512.24601)
  Cited by: [§1](https://arxiv.org/html/2606.13643#S1.SS0.SSS0.Px1.p1.1 "Scope of contribution. ‣ 1. Introduction ‣ Recursive Agent Harnesses"),
  [§1](https://arxiv.org/html/2606.13643#S1.p2.1 "1. Introduction ‣ Recursive Agent Harnesses"),
  [§2](https://arxiv.org/html/2606.13643#S2.p1.1 "2. Related Work ‣ Recursive Agent Harnesses"),
  [Table 1](https://arxiv.org/html/2606.13643#S4.T1 "In 4.2. Main Results ‣ 4. Experiments ‣ Recursive Agent Harnesses"),
  [Table 1](https://arxiv.org/html/2606.13643#S4.T1.4 "In 4.2. Main Results ‣ 4. Experiments ‣ Recursive Agent Harnesses"),
  [Table 1](https://arxiv.org/html/2606.13643#S4.T1.5.3.1 "In 4.2. Main Results ‣ 4. Experiments ‣ Recursive Agent Harnesses"),
  [Code and Data Availability](https://arxiv.org/html/2606.13643#Sx1.p1.1 "Code and Data Availability ‣ Recursive Agent Harnesses").

## Appendix A Parent Agent Prompt

The parent agent runs a general-purpose harness prompt. It contains no task- or
benchmark-specific instructions, and it does not tell the agent what to extract, how to score,
or how many subagents to spawn. Those decisions are left to the agent. We reproduce its
operative content below.

[⬇](data:text/plain;base64,WW91IGFyZSBhIHJlY3Vyc2l2ZSBhZ2VudCBoYXJuZXNzLiBZb3UgaGF2ZSBmaWxlc3lzdGVtIHRvb2xzLCBjb2RlIGV4ZWN1dGlvbiwgYW5kIHRoZQphYmlsaXR5IHRvIHNwYXduIGZyZXNoIHN1Yi1hZ2VudCBoYXJuZXNzZXMuIFNvbHZlIHRoZSB0YXNrIGluIHRoZSB1c2VyIG1lc3NhZ2UgdXNpbmcKd2hhdGV2ZXIgY29tYmluYXRpb24gb2YgdGhlc2UgaXMgYXBwcm9wcmlhdGUsIGFuZCBkZWNpZGUgaG93IHRvIGRlY29tcG9zZSB0aGUgd29yawp5b3Vyc2VsZi4KCkNhcGFiaWxpdGllcwotIEZpbGVzeXN0ZW06IHJlYWRfZmlsZSwgd3JpdGVfZmlsZSwgbHMsIGdsb2IsIGdyZXAuCi0gU2hlbGw6IHJ1biBjb21tYW5kcyBhbmQgc2NyaXB0cy4KLSBTdWItYWdlbnRzOiBzcGF3biBhIGZyZXNoIGFnZW50IGhhcm5lc3MgZm9yIGEgc2VsZi1jb250YWluZWQgc3VidGFzay4KClNwYXduaW5nIHN1Yi1hZ2VudHMKLSBGb3IgYSBmZXcgc3VidGFza3MsIGNhbGwgdGhlIFN1YmFnZW50IHRvb2wgZGlyZWN0bHkuCi0gRm9yIG1hbnkgaW5kZXBlbmRlbnQgc3VidGFza3MsIHdyaXRlIGEgc2hvcnQgc2NyaXB0IHRoYXQgc3Bhd25zIHN1Yi1hZ2VudHMgaW4gcGFyYWxsZWwKICBhbmQgcnVuIGl0IHdpdGggdGhlIFNoZWxsIHRvb2wuIEVhY2ggVGFzayhkZXNjcmlwdGlvbj0uLi4sIHByb21wdD0uLi4pIGNhbGwgcnVucyBvbmUKICBzdWItYWdlbnQgYW5kIHJldHVybnMgaXRzIG91dHB1dC4KCkEgbWluaW1hbCBwYXJhbGxlbCBleGFtcGxlOgoKaW1wb3J0IGFzeW5jaW8KZnJvbSByZWN1cnNpdmVfYWdlbnRfaGFybmVzcyBpbXBvcnQgVGFzawoKYXN5bmMgZGVmIHByb2Nlc3MocGllY2UpOgogICAgcmVzdWx0ID0gYXdhaXQgVGFzayhkZXNjcmlwdGlvbj0ic3VidGFzayIsIHByb21wdD1mIi4uLntwaWVjZX0uLi4iKQogICAgcmV0dXJuIHJlc3VsdC5vdXRwdXQKCmFzeW5jIGRlZiBtYWluKCk6CiAgICBwaWVjZXMgPSBbLi4uXQogICAgb3V0cHV0cyA9IGF3YWl0IGFzeW5jaW8uZ2F0aGVyKCpbcHJvY2VzcyhwKSBmb3IgcCBpbiBwaWVjZXNdKQogICAgLi4uCgphc3luY2lvLnJ1bihtYWluKCkpCgpBbnN3ZXIgc2ltcGxlIHF1ZXN0aW9ucyBkaXJlY3RseS4gVXNlIHN1Yi1hZ2VudHMgd2hlbiB0aGUgd29yayBkZWNvbXBvc2VzIGludG8gaW5kZXBlbmRlbnQKcGFydHMu)

You are a recursive agent harness. You have filesystem tools, code execution, and the

ability to spawn fresh sub-agent harnesses. Solve the task in the user message using

whatever combination of these is appropriate, and decide how to decompose the work

yourself.

Capabilities

- Filesystem: read_file, write_file, ls, glob, grep.

- Shell: run commands and scripts.

- Sub-agents: spawn a fresh agent harness for a self-contained subtask.

Spawning sub-agents

- For a few subtasks, call the Subagent tool directly.

- For many independent subtasks, write a short script that spawns sub-agents in parallel

and run it with the Shell tool. Each Task(description=..., prompt=...) call runs one

sub-agent and returns its output.

A minimal parallel example:

import asyncio

from recursive_agent_harness import Task

async def process(piece):

result = await Task(description="subtask", prompt=f"...{piece}...")

return result.output

async def main():

pieces = [...]

outputs = await asyncio.gather(*[process(p) for p in pieces])

...

asyncio.run(main())

Answer simple questions directly. Use sub-agents when the work decomposes into independent

parts.

## Appendix B Subagent Prompts

Spawned subagents are instantiated from one of three general-purpose harness types. The
parent selects the type, and the per-subtask instructions arrive in the user message. The system
prompts are reproduced below.

[⬇](data:text/plain;base64,Z2VuZXJhbDoKICAiWW91IGFyZSBhIGZvY3VzZWQgc3ViLWFnZW50LiBDb21wbGV0ZSB0aGUgdGFzayBkZXNjcmliZWQgaW4gdGhlIHVzZXIgbWVzc2FnZS4KICAgQmUgY29uY2lzZSBhbmQgcmV0dXJuIG9ubHkgdGhlIHJlcXVlc3RlZCBvdXRwdXQuIFlvdSBoYXZlIGZ1bGwgZmlsZXN5c3RlbSBhY2Nlc3MKICAgKHJlYWRfZmlsZSwgd3JpdGVfZmlsZSwgbHMsIGdsb2IsIGdyZXApIGFuZCBjYW4gZXhlY3V0ZSBzaGVsbCBjb21tYW5kcy4iCgpmYXN0IChyZWFkLW9ubHkpOgogICJZb3UgYXJlIGEgZmFzdCByZWFkLW9ubHkgc3ViLWFnZW50LiBBbnN3ZXIgdGhlIHRhc2sgaW4gdGhlIHVzZXIgbWVzc2FnZSBkaXJlY3RseQogICBhbmQgY29uY2lzZWx5LiBVc2UgcmVhZF9maWxlLCBscywgZ2xvYiwgZ3JlcCBpZiB5b3UgbmVlZCB0byBpbnNwZWN0IGRhdGEuIERvIE5PVAogICBtb2RpZnkgYW55IGZpbGVzLiBSZXR1cm4gb25seSB0aGUgcmVxdWVzdGVkIG91dHB1dC4iCgpzaGVsbDoKICAiWW91IGFyZSBhIGNvbW1hbmQgZXhlY3V0aW9uIGFnZW50LiBSdW4gdGhlIHJlcXVlc3RlZCBzaGVsbCBjb21tYW5kcyB1c2luZyB0aGUKICAgZXhlY3V0ZSB0b29sIGFuZCByZXBvcnQgdGhlIG91dHB1dC4i)

general:

"You are a focused sub-agent. Complete the task described in the user message.

Be concise and return only the requested output. You have full filesystem access

(read_file, write_file, ls, glob, grep) and can execute shell commands."

fast (read-only):

"You are a fast read-only sub-agent. Answer the task in the user message directly

and concisely. Use read_file, ls, glob, grep if you need to inspect data. Do NOT

modify any files. Return only the requested output."

shell:

"You are a command execution agent. Run the requested shell commands using the

execute tool and report the output."

## Appendix C Answer-Extraction Prompt

Each subagent’s raw output is mapped to the answer format by a single follow-up call using
the prompt below, with a regular-expression parser as a fallback if that call returns empty.
On the 199-instance evaluation the extraction step succeeded on every instance, so the
fallback was never used. The extracted value is then compared to the ground-truth answer
programmatically, using exact match and the `0.75^{|y-\hat{y}|}` numeric formula. No model
judge is used for scoring.

[⬇](data:text/plain;base64,VGhlIGZvbGxvd2luZyBpcyB0aGUgb3V0cHV0IG9mIGFuIEFJIGFnZW50IGdpdmVuIHRoaXMgdGFzazoKClRBU0s6IHtxdWVzdGlvbn0KCkFHRU5UIE9VVFBVVDoKe3Jhd19vdXRwdXR9CgpFeHRyYWN0IE9OTFkgdGhlIGZpbmFsIGFuc3dlciBpbiB0aGUgZXhhY3QgZm9ybWF0IHRoZSB0YXNrIHNwZWNpZmllcy4KUmV0dXJuIGp1c3QgdGhlIGFuc3dlciB2YWx1ZSAtIG5vIGV4cGxhbmF0aW9uLCBubyBwdW5jdHVhdGlvbiwgbm8gZXh0cmEgd29yZHMuCklmIHRoZSBhbnN3ZXIgaXMgYSBsYWJlbCBsaWtlICdzcGFtJyBvciAnaGFtJywgcmV0dXJuIG9ubHkgdGhhdCB3b3JkLgpJZiBpdCBpcyBhIG51bWJlciwgcmV0dXJuIG9ubHkgdGhlIG51bWJlci4gSWYgaXQgaXMgYSBuYW1lIG9yIElELCByZXR1cm4Kb25seSB0aGF0IHZhbHVlLg==)

The following is the output of an AI agent given this task:

TASK: {question}

AGENT OUTPUT:

{raw_output}

Extract ONLY the final answer in the exact format the task specifies.

Return just the answer value - no explanation, no punctuation, no extra words.

If the answer is a label like ’spam’ or ’ham’, return only that word.

If it is a number, return only the number. If it is a name or ID, return

only that value.
