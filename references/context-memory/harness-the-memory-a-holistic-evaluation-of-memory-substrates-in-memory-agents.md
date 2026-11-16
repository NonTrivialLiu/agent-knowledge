---
title: "Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"
url: https://arxiv.org/abs/2608.15008
published: 2026-08-15
fetched: 2026-11-11
type: paper
topics: [context-memory, memory, harness, multi-agent, evaluation]
summary: "统一 harness 下比较 11 种记忆方式、三种模型、四类基准及 26 项质量和成本指标；广泛检索有助事实问答，但可能分散行动任务的注意力。"
---

# Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents

Wei-Chieh Huang    Weizhi Zhang    Yuchen Wu    Yankai Chen    Eric Hanchen Jiang
Affiliation: University of Illinois Chicago  University of Washington  McGill University
Affiliation: MBZUAI  University of California, Los Angeles†Corresponding authors
  
Wooseong Yang    Yiwei Yang    Henry Peng Zou    Hanrong Zhang    Ying Nian Wu
Affiliation: MBZUAI  University of California, Los Angeles†Corresponding authors
  
Haolun Wu  Kai-Wei Chang  Philip S. Yu  Xue Liu  Aylin Caliskan
Affiliation: University of Illinois Chicago  University of Washington  McGill University
Affiliation: MBZUAI  University of California, Los Angeles†Corresponding authors

## Abstract

Memory is becoming core infrastructure for long-horizon LLM agents, yet existing evaluations offer limited guidance on which memory substrate, namely the underlying medium in which memory is represented and stored, should be used under different operating regimes. We introduce a unified suite of 26 performance and efficiency metrics, including auxiliary-LLM costs attributed to the write, read, and management stages, and apply it identically to 11 memory methods in a controlled harness that varies only the memory substrate. The methods cover dense and sparse indices, text records, structural stores, hierarchical stores, refinement-based memories, parametric updates, and activation-compatible context mechanisms, and we evaluate them with three backbone models on four benchmark suites spanning user-centric question answering and agent-centric decision-making. Our results show that no single substrate consistently dominates: broad retrieval benefits long-context factual QA, while excessive retrieval can harm sequential decision-making by shifting attention away from action-critical context. Scalability introduces a further routing axis, as substrates that perform well at moderate history lengths can become costly or brittle at longer horizons. These regime-dependent reversals make substrate selection a design axis. Choosing a substrate per observable operating regime improves over the best fixed substrate on our benchmarks, while query-level routing leaves most of the oracle headroom open. The findings provide empirical guidance for designing efficient, reliable, and regime-aware long-term memory for LLM agents. Code is available at <https://github.com/Jasonya/SubMem>.

## 1 Introduction

Foundation model agents are rapidly advancing from single-turn assistants into long-horizon settings that demand persistent memory: coding assistants resolving issues and developing code in real repositories [[1](https://arxiv.org/html/2608.15008v2#bib.bib1), [2](https://arxiv.org/html/2608.15008v2#bib.bib5)], web agents navigating realistic websites [[3](https://arxiv.org/html/2608.15008v2#bib.bib34)], personal companions tracking evolving user preferences across hundreds of sessions [[4](https://arxiv.org/html/2608.15008v2#bib.bib15), [5](https://arxiv.org/html/2608.15008v2#bib.bib108)], and scientific discovery agents refining hypotheses over iterative cycles [[6](https://arxiv.org/html/2608.15008v2#bib.bib3)]. Despite spanning vastly different domains, these agents share a common challenge: writing new experience into a persistent store, reading relevant knowledge at decision time, and managing an ever-growing memory under finite compute and storage budgets [[7](https://arxiv.org/html/2608.15008v2#bib.bib82)]. No single memory design excels at all three along the axes of accuracy, efficiency, and cost [[8](https://arxiv.org/html/2608.15008v2#bib.bib7), [9](https://arxiv.org/html/2608.15008v2#bib.bib8)]: a vector index writes cost-effectively but struggles with multi-hop retrieval [[10](https://arxiv.org/html/2608.15008v2#bib.bib40)]; a knowledge graph reasons relationally but requires orders of magnitude more LLM calls to construct (Appendix [B.5](https://arxiv.org/html/2608.15008v2#A2.SS5 "B.5 Memory Substrate and Method Exclusion ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")); a KV cache integrates tightly with the model but sacrifices scalability [[11](https://arxiv.org/html/2608.15008v2#bib.bib23)]. This diversity of trade-offs motivates the long-term goal of a universal, adaptive memory system that dynamically selects or composes substrates, namely the underlying media in which memory is represented and stored, depending on the query, the task, and the deployment constraints.

Designing such a system requires understanding when each substrate is preferable and,
critically, under what operating regime. Recent work on agent harnesses, the scaffolding around a model that decomposes tasks, manages context across sessions, and evaluates outputs, has shown that this scaffolding is often the primary lever for agent performance beyond raw model capability [[12](https://arxiv.org/html/2608.15008v2#bib.bib80), [13](https://arxiv.org/html/2608.15008v2#bib.bib81)]. The memory substrate is the infrastructure layer of any such harness: its design constrains every other harness decision, from write cost and read latency to whether stored knowledge is inspectable and how the system degrades as histories grow. Yet the same substrate can be the quality leader on one task and a strictly dominated choice
on another, so a universal harness should not commit to a single substrate at design time [[14](https://arxiv.org/html/2608.15008v2#bib.bib83)]. Selecting between substrates per regime then becomes a design axis of the harness. Producing the empirical signal for that selection requires *evaluating the harness itself*: isolating the memory substrate as a controlled variable while holding the rest of the scaffolding fixed, across regimes that stress fundamentally different memory operations.

Figure 1: Evaluation landscape of 52 memory-augmented LLM systems (2023–2026).
(a) Benchmark adoption: 62% of usage concentrates on
LoCoMo and LongMemEval. (b) Metric coverage: every system reports accuracy but
only 21% report any efficiency metric;
81% of systems use GPT-family backbones.
(c) Breadth and efficiency: half of
systems use a single benchmark with no efficiency metrics; no
system simultaneously achieves broad coverage and comprehensive
efficiency reporting.

Yet current evaluations provide almost no such signal. As shown in Figure [1](https://arxiv.org/html/2608.15008v2#S1.F1 "Figure 1 ‣ 1 Introduction ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"), a landscape analysis of 52 recent memory-augmented systems exposes three limitations that leave the path toward universal agent memory empirically ungrounded. First, evaluations are *benchmark-concentrated*: 62% of all benchmark and system pairs draw from just two dialogue-centric datasets, LoCoMo [[15](https://arxiv.org/html/2608.15008v2#bib.bib9)] and LongMemEval (LME) [[16](https://arxiv.org/html/2608.15008v2#bib.bib2)], while agentic tasks remain almost unexamined (Figure [1](https://arxiv.org/html/2608.15008v2#S1.F1 "Figure 1 ‣ 1 Introduction ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") a). Second, *metric and backbone coverage is narrow*: every system reports accuracy, but only 21% measure any efficiency dimension; management cost and compression ratio are unreported. Furthermore, 81% of systems use the GPT-family as their primary backbone,
making it impossible to disentangle substrate effects from model-specific behavior (Figure [1](https://arxiv.org/html/2608.15008v2#S1.F1 "Figure 1 ‣ 1 Introduction ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") b). Third, *evaluation scope is shallow*: half of all systems test on a single benchmark with zero efficiency metrics, and no system simultaneously achieves broad coverage and comprehensive efficiency reporting (Figure [1](https://arxiv.org/html/2608.15008v2#S1.F1 "Figure 1 ‣ 1 Introduction ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") c). The full per-system survey, inclusion criteria, and aggregate statistics are reported in
Appendix [A](https://arxiv.org/html/2608.15008v2#A1 "Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"). As a result, we know which system tops a given leaderboard in terms of accuracy, but not under what operating regime a different substrate would be preferable, precisely the selection signal that a regime-aware memory harness needs.

We close this gap with a controlled harness evaluation that isolates the memory substrate, the storage-and-access layer of the harness defined in Appendix [B.1](https://arxiv.org/html/2608.15008v2#A2.SS1 "B.1 Definition of a Memory Substrate ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"), as the sole experimental variable. Adopting the taxonomy of [[17](https://arxiv.org/html/2608.15008v2#bib.bib11)], we partition the design space into external memory (information in data structures outside the model) and internal memory (information encoded in model weights or activations), and implement 11 methods spanning all seven substrate families, as shown in Figure [2](https://arxiv.org/html/2608.15008v2#S1.F2 "Figure 2 ‣ 1 Introduction ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"). All substrates are evaluated on identical interaction histories under three backbones and four benchmarks covering both user-centric question answering and agent-centric decision-making.

The harness evaluation yields three findings. First, the optimal substrate *reverses* between regimes. On Qwen3-32B-AWQ, structural graphs lead dialogue QA but are Pareto-dominated on agentic tasks, while refinement memories lead embodied planning but trail on QA (Section [5.1](https://arxiv.org/html/2608.15008v2#S5.SS1 "5.1 Performance–Latency Tradeoffs Across Substrate Families ‣ 5 Discussion ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")). No substrate leads on quality in both regimes, since the quality end of the performance–latency frontier moves from M5 on QA to M7 on ALFWorld and M2 on BigCodeBench-Hard. Second, retrieving more entries helps QA but hurts agentic decisions, and an attention probe on one backbone suggests why: as retrieval depth grows, the model’s attention shifts away from the task context toward the retrieved block, which is exactly where the answer lives in QA but not in agentic tasks, where the policy needs to attend to the current observation instead (Section [5.2](https://arxiv.org/html/2608.15008v2#S5.SS2 "5.2 Retrieval Scaling Reverses Across Regimes ‣ 5 Discussion ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")). Third, a scalability study shows that the substrates whose quality grows most with history length, led by our harness approximation of skill bundles (M8), also pay the steepest latency growth, while only the flat indices stay cheap at long horizons (Section [5.3](https://arxiv.org/html/2608.15008v2#S5.SS3 "5.3 Scalability Under Growing Input Context ‣ 5 Discussion ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")). Together, these findings yield a regime-conditioned design rule, *trade read breadth for write depth* on agentic tasks (retrieve fewer entries per query and invest more in distilling and structuring memory at write time) while retrieving broadly on long-context QA, and a broader implication: no single substrate serves every regime, so substrate selection is a design axis of universal agent memory, whether it is realized as a multi-substrate or multi-agent system. Choosing a substrate per observable regime beats the best fixed substrate on our benchmarks, while finer query-level routing remains largely open (Appendix [E.3](https://arxiv.org/html/2608.15008v2#A5.SS3 "E.3 Substrate Routing ‣ Appendix E Additional Analyses ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")). Our contributions are summarized as follows:

- •

  A unified metric suite for agent memory. A suite of 26 performance and efficiency metrics applied identically to all 11 methods. It covers memory quality (compression ratio and the MAB LRU, TTL, and CR capabilities) and, to our knowledge, provides the first cost accounting that attributes auxiliary-LLM tokens and calls to the write, read, and management stages across substrate families.
- •

  A controlled, cross-regime harness evaluation. A comparison that isolates the memory substrate across 11 methods and seven substrate families of the external and internal taxonomy, three backbones, and four benchmarks spanning user-centric and agent-centric regimes. It maps each method onto a unified performance–latency landscape and identifies which substrate families are dominated under which operating regime.
- •

  A diagnostic study of retrieval scaling and context scalability. A
  retrieval-depth sweep paired with attention probing that diagnoses how retrieval breadth reshapes attention allocation across regimes, together with a scalability analysis that characterizes how each substrate family scales with input growth,
  yielding actionable design rules for regime-aware memory.

![Refer to caption](https://arxiv.org/html/2608.15008v2/submem_main.png)

Figure 2: Overview of the harness evaluation. 11 memory methods (M1–M11) spanning seven substrate families are evaluated on
identical interaction histories across four benchmarks, instrumented
with 26 metrics in two families (performance and efficiency).

## 2 Memory Substrates and Configuration

Memory system configurations are highly complex, with many tunable parameters and modular
design choices, so rather than asking which method is inherently superior, we examine which
configurations yield specific benefits and trade-offs under different task settings and
operating regimes, the empirical prerequisite for any universal memory system that
selects substrates dynamically.

### Substrate overview.

We study eleven memory substrates arranged into seven families ([Table 4](https://arxiv.org/html/2608.15008v2#A2.T4 "In Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") in Appendix [B](https://arxiv.org/html/2608.15008v2#A2 "Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")). On the external side, the eight methods span a structure spectrum.
 Flat Index: M1 Dense Vector and M2 Sparse
Vector [[18](https://arxiv.org/html/2608.15008v2#bib.bib12), [19](https://arxiv.org/html/2608.15008v2#bib.bib84)] require no LLM calls and establish
the retrieval floor.
 Text Record: M3 Gist
Index [[20](https://arxiv.org/html/2608.15008v2#bib.bib16)] adds write-side gisting and read-side page selection.
 Structural introduces relational links: M4
Evolving Notes [[21](https://arxiv.org/html/2608.15008v2#bib.bib6)] writes interlinked notes with evolution-triggered
rewrites, and M5 Dual-Level Graph [[22](https://arxiv.org/html/2608.15008v2#bib.bib48)] builds a dual-level
entity-relation graph.
 Hierarchical: M6 Hierarchical
Tree [[23](https://arxiv.org/html/2608.15008v2#bib.bib19), [24](https://arxiv.org/html/2608.15008v2#bib.bib18)] recursively clusters and summarizes memory into a
multi-level hierarchy retrieved via collapsed-tree dense search.
 Refinement distills experience rather than accumulating
it: M7 Distilled Strategies [[25](https://arxiv.org/html/2608.15008v2#bib.bib49)] judges trajectories and
extracts reusable strategies, and M8 Skill Bundles [[26](https://arxiv.org/html/2608.15008v2#bib.bib21)] clusters
experiences into skill bundles. On the internal side, the
 Weight family, M9 Adapter Tuning [[27](https://arxiv.org/html/2608.15008v2#bib.bib22)],
bakes knowledge into weights via fine-tuning, while the
 Activation family includes M10 Full Context and M11 Episode-Clustered Re-prefill [[28](https://arxiv.org/html/2608.15008v2#bib.bib24)], which
clusters turns into episodes and re-prefills selected episodes at read time. We report Zep [[29](https://arxiv.org/html/2608.15008v2#bib.bib17)], Mem0 [[30](https://arxiv.org/html/2608.15008v2#bib.bib13)], and
MemGPT [[31](https://arxiv.org/html/2608.15008v2#bib.bib14)] in an auxiliary-cost analysis (Appendix [B.5](https://arxiv.org/html/2608.15008v2#A2.SS5 "B.5 Memory Substrate and Method Exclusion ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")) rather than the main controlled comparison because their defining mechanisms are management and controller policies outside the single-variable frame, and their production pipelines introduce substantially different auxiliary-LLM budgets.

### Scope of the comparison.

We define a substrate by four properties, its representation and its write, read, and management operations (Appendix [B.1](https://arxiv.org/html/2608.15008v2#A2.SS1 "B.1 Definition of a Memory Substrate ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")). These mechanisms act at different stages of one pipeline and can be composed, so each comparison contrasts configured substrates under a shared harness rather than mutually exclusive replacements. Shared settings and per-substrate hyperparameters follow a fixed calibration protocol (Appendix [B.2](https://arxiv.org/html/2608.15008v2#A2.SS2 "B.2 Calibration Protocol ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")). Two methods are harness-compatible approximations of their reference systems. M8 replaces MemSkill’s PPO-trained controller with a zero-shot LLM over all skill bundles, and M11 replaces EpiCache’s in-place KV-cache edits with utterance-level re-prefill. Results reported for M8 and M11 refer to these approximations.

## 3 Experiment Design

Our goal is to isolate the implemented memory substrate family under a shared harness, backbone, prompting, and auxiliary-LLM setting. We ask two questions: (1) how much of an agent’s behavior, in terms of task performance and efficiency, is attributable to the substrate alone, and (2) whether that attribution is stable across
operating regimes. We test every substrate on both user-centric benchmarks, where the agent retrieves facts from long conversational histories, and agent-centric benchmarks, where the agent must execute precise action sequences. Three configurations are excluded by design: M7 only applies to trajectory-bearing agent-centric tasks (its strategy-distillation pipeline has no analog on dialogue inputs), M9 is incompatible with the A4B MoE routing in
Gemma-4-26B-A4B-IT, and M10 (full context) is omitted from both agent-centric benchmarks (ALFWorld and BigCodeBench-Hard) because the cumulative context exceeds every tested context window.

### Benchmarks.

We select four benchmarks that collectively span the user-centric and agent-centric divide. On the user-centric side, LoCoMo [[15](https://arxiv.org/html/2608.15008v2#bib.bib9)] provides ten multi-session dialogues with `1{,}986` questions across five categories, and MemoryAgentBench (MAB) [[32](https://arxiv.org/html/2608.15008v2#bib.bib28)] factors long-context memory into four capabilities, Accurate Retrieval (AR, instantiated on MemoryAgentBench’s LongMemEval-S∗ subset [[16](https://arxiv.org/html/2608.15008v2#bib.bib2)]), Long-Range Understanding (LRU), Test-Time Learning (TTL), and Conflict Resolution (CR); we additionally use CR as our scalability probe by sweeping content length. In the result tables we surface AR under its LongMemEval-S (LME-S) label as a separate column alongside the LRU, TTL, and CR capabilities. Together these benchmarks stress recall-oriented capabilities, the regime where broad retrieval helps. On the agentic side, ALFWorld [[33](https://arxiv.org/html/2608.15008v2#bib.bib31)] provides `134` valid-unseen embodied-planning tasks evaluated in a cross-episode regime (recovery from a shared pre-built bank of successes and failures), and BigCodeBench-Hard (BCB-Hard) [[34](https://arxiv.org/html/2608.15008v2#bib.bib32)] provides `148` code tasks graded with retrieval over a cross-task pool of successes and failures. These benchmarks stress the opposite regime, where retrieval noise is toxic and the substrate must distill experience into compact, high-precision representations. Full benchmark setups, capability definitions, and pool construction details are in
Appendix [C](https://arxiv.org/html/2608.15008v2#A3 "Appendix C Benchmark Setups and Bank Alignment ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"), which also maps each benchmark onto the stages of the memory lifecycle it exercises (Appendix [C.3](https://arxiv.org/html/2608.15008v2#A3.SS3 "C.3 Coverage of the Memory Lifecycle ‣ Appendix C Benchmark Setups and Bank Alignment ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")).

### Models, inference, and metrics.

The backbone models are Qwen3-8B, Qwen3-32B-AWQ [[35](https://arxiv.org/html/2608.15008v2#bib.bib99)], and Gemma-4-26B-A4B-IT [[36](https://arxiv.org/html/2608.15008v2#bib.bib100)], tested on all four benchmarks using vLLM [[37](https://arxiv.org/html/2608.15008v2#bib.bib101)] on `4{\times}`H200 GPUs, the single configuration behind every latency and wall-clock number we report. For consistency, the auxiliary LLM is fixed to gpt-4o-mini [[38](https://arxiv.org/html/2608.15008v2#bib.bib102)] across all methods that require one for memory writing, management, or input organization. LLM-as-a-judge evaluation also uses gpt-4o-mini with fixed judging templates, and three further judges agree substantially with its labels (Appendix [E.2](https://arxiv.org/html/2608.15008v2#A5.SS2 "E.2 LLM-Judge Agreement ‣ Appendix E Additional Analyses ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")). We instrument every run with the 26 metrics defined in Table [9](https://arxiv.org/html/2608.15008v2#A4.T9 "Table 9 ‣ Appendix D Metrics Definition and Assessment ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") in Appendix [D](https://arxiv.org/html/2608.15008v2#A4 "Appendix D Metrics Definition and Assessment ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"), organized into task-performance metrics and efficiency metrics, including benchmark-native primary metrics such as Pass@1 on BCB-Hard, task success on
ALFWorld, and SubEM on MAB, as well as storage, latency, token, call, total-time, and cost measurements.

### Ablations.

We isolate two design axes while holding the substrate implementation, backbone, and prompt template fixed. First, a top-`k` retrieval-breadth sweep on M1, M2, M4, and M6, plus M7 on ALFWorld: `k\in\{1,2,5,10,20\}` on LoCoMo and `k\in\{1,2,3,4,5\}` on ALFWorld, with a no-memory baseline that receives the same template with an empty retrieved block, so the curves attribute quality to retrieval rather than scaffolding. Second, a context-window stress on MAB CR under three conversation-length regimes (6K, 32K, 262K tokens) with the question pool, gold answers, and judge held constant. Together these ablations separate substrates whose advantage comes from retrieval breadth from those driven by recency-aware update semantics.

## 4 Results

We organize the results along the user-centric and agent-centric divide that defines our
harness. Table [1](https://arxiv.org/html/2608.15008v2#S4.T1 "Table 1 ‣ 4 Results ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") reports user-centric results on LoCoMo, LME-S, and MAB, where the substrate must surface relevant facts from accumulated dialogue history;
Table [2](https://arxiv.org/html/2608.15008v2#S4.T2 "Table 2 ‣ 4.1 User-centric Benchmark ‣ 4 Results ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") reports agent-centric results on ALFWorld and
BigCodeBench-Hard, where the substrate must inform sequential decisions without diluting
attention over action-critical context. Full per-metric breakdowns across all 26 metrics
are in Appendix [F](https://arxiv.org/html/2608.15008v2#A6 "Appendix F Full Tables ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"). The memory-quality metrics that the suite computes by one rule for every method already separate the substrates before the regime divide. On LME-S, the compression ratio `P_{5}` ranges from 1.00 for the verbatim flat stores (M1, M2) through 2.80 for M6 to 12.50 for M8 (Appendix [F.2](https://arxiv.org/html/2608.15008v2#A6.SS2 "F.2 Full Tables for the LongMemEval-S and MAB Benchmarks ‣ Appendix F Full Tables ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")), and the MAB columns of Table [1](https://arxiv.org/html/2608.15008v2#S4.T1 "Table 1 ‣ 4 Results ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") rank the substrates differently on LRU, TTL, and CR.

Table 1: Memory substrates on LoCoMo, LME-S, and MAB (LRU, TTL, CR). `P_{4}` `\uparrow`: LLM-judge score; `E_{15}` `\downarrow`: per-query latency (s). Within each model band, green and red mark the per-column best and worst; bold marks the per-model P4 winner on each benchmark.

|  |  |  |  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  | LoCoMo | | LME-S | | MAB LRU | | MAB TTL | | MAB CR | |
| Model | Sub. | Family | `P_{4}` `\uparrow` | `E_{15}` `\downarrow` | `P_{4}` `\uparrow` | `E_{15}` `\downarrow` | `P_{4}` `\uparrow` | `E_{15}` `\downarrow` | `P_{4}` `\uparrow` | `E_{15}` `\downarrow` | `P_{4}` `\uparrow` | `E_{15}` `\downarrow` |
| [Uncaptioned image] Qwen3-8B | External | | | | | | | | | | | |
| M1 | Flat | 0.561 | 0.77 | 0.478 | 7.30 | 0.578 | 9.94 | 0.560 | 0.92 | 0.270 | 1.65 |
| M2 | Flat | 0.470 | 0.33 | 0.480 | 1.75 | 0.620 | 3.23 | 0.470 | 0.33 | 0.270 | 1.39 |
| M3 | Text | 0.562 | 4.18 | 0.495 | 55.58 | 0.563 | 146.65 | 0.640 | 27.15 | 0.240 | 2.30 |
| M4 | Struct | 0.545 | 6.36 | 0.430 | 225.67 | 0.493 | 274.06 | 0.480 | 12.65 | 0.270 | 1.50 |
| M5 | Struct | 0.648 | 27.84 | 0.537 | 187.21 | 0.578 | 313.18 | 0.540 | 23.70 | 0.440 | 6.01 |
| M6 | Hier | 0.556 | 1.39 | 0.507 | 19.96 | 0.493 | 59.98 | 0.290 | 3.24 | 0.290 | 3.30 |
| M8 | Refine | 0.509 | 3.03 | 0.490 | 102.85 | 0.592 | 197.09 | 0.560 | 1.02 | 0.340 | 2.07 |
| Internal | | | | | | | | | | | |
| M9 | Weight | 0.379 | 1.76 | 0.250 | 51.50 | 0.300 | 85.00 | 0.220 | 8.50 | 0.260 | 1.95 |
| M10 | Act | 0.589 | 4.55 | 0.120 | 6.61 | 0.676 | 6.58 | 0.480 | 2.28 | 0.270 | 1.64 |
| M11 | Act | 0.307 | 2.03 | 0.090 | 14.61 | 0.634 | 21.30 | 0.560 | 0.56 | 0.240 | 1.76 |
| [Uncaptioned image] Qwen3-32B-AWQ | External | | | | | | | | | | | |
| M1 | Flat | 0.582 | 2.59 | 0.548 | 12.00 | 0.676 | 32.39 | 0.810 | 1.81 | 0.300 | 0.85 |
| M2 | Flat | 0.487 | 2.37 | 0.497 | 7.31 | 0.662 | 23.14 | 0.780 | 1.20 | 0.280 | 0.50 |
| M3 | Text | 0.586 | 6.47 | 0.560 | 67.42 | 0.775 | 477.97 | 0.850 | 94.29 | 0.270 | 1.19 |
| M4 | Struct | 0.452 | 8.70 | 0.490 | 234.00 | 0.535 | 278.93 | 0.710 | 17.18 | 0.290 | 2.35 |
| M5 | Struct | 0.683 | 29.22 | 0.627 | 194.08 | 0.578 | 333.95 | 0.630 | 26.02 | 0.310 | 3.00 |
| M6 | Hier | 0.573 | 5.20 | 0.593 | 20.27 | 0.577 | 73.16 | 0.330 | 3.77 | 0.270 | 1.13 |
| M8 | Refine | 0.533 | 5.53 | 0.533 | 106.78 | 0.592 | 228.66 | 0.810 | 1.93 | 0.320 | 1.08 |
| Internal | | | | | | | | | | | |
| M9 | Weight | 0.399 | 4.73 | 0.290 | 171.70 | 0.422 | 253.63 | 0.250 | 22.15 | 0.170 | 3.27 |
| M10 | Act | 0.669 | 16.25 | 0.190 | 22.98 | 0.620 | 27.43 | 0.760 | 2.43 | 0.270 | 0.51 |
| M11 | Act | 0.274 | 4.17 | 0.113 | 52.39 | 0.620 | 25.00 | 0.810 | 1.45 | 0.320 | 3.41 |
| [Uncaptioned image] Gemma-4-26B-A4B-IT | External | | | | | | | | | | | |
| M1 | Flat | 0.574 | 0.93 | 0.515 | 8.49 | 0.676 | 16.50 | 0.770 | 14.50 | 0.460 | 4.09 |
| M2 | Flat | 0.555 | 0.49 | 0.513 | 3.37 | 0.662 | 9.18 | 0.730 | 0.20 | 0.460 | 3.88 |
| M3 | Text | 0.599 | 4.81 | 0.530 | 31.78 | 0.720 | 238.78 | 0.750 | 36.21 | 0.430 | 3.67 |
| M4 | Struct | 0.476 | 6.61 | 0.523 | 230.39 | 0.535 | 267.00 | 0.720 | 16.12 | 0.460 | 3.97 |
| M5 | Struct | 0.719 | 25.95 | 0.667 | 190.93 | 0.451 | 332.94 | 0.720 | 25.79 | 0.550 | 8.23 |
| M6 | Hier | 0.592 | 1.42 | 0.593 | 17.19 | 0.507 | 62.76 | 0.250 | 22.00 | 0.400 | 6.50 |
| M8 | Refine | 0.554 | 3.22 | 0.537 | 103.80 | 0.535 | 228.16 | 0.770 | 1.68 | 0.500 | 2.82 |
| Internal | | | | | | | | | | | |
| M10 | Act | 0.688 | 5.17 | 0.110 | 6.91 | 0.577 | 10.38 | 0.460 | 1.36 | 0.450 | 4.24 |
| M11 | Act | 0.330 | 2.16 | 0.115 | 18.50 | 0.318 | 76.00 | 0.480 | 1.50 | 0.180 | 1.48 |

### 4.1 User-centric Benchmark

No single substrate wins every capability, ruling out single-substrate universal memory by
design.
Table [1](https://arxiv.org/html/2608.15008v2#S4.T1 "Table 1 ‣ 4 Results ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") shows that the best substrate changes with the capability being tested, and this pattern is broadly visible across backbones despite model-specific interactions. On LoCoMo and LME-S, M5 performs best across model bands, suggesting that combining entity-level graph traversal with chunk-level vector search is useful for fact retrieval over long dialogue histories. On MAB LRU, less lossy access mechanisms often perform better: M10 leads Qwen3-8B, while M3 leads Qwen3-32B-AWQ. On MAB TTL, M3 leads both Qwen bands and M1 and M8 share the Gemma-4 lead, whereas the M9 adapter-tuning implementation performs poorly because newly acquired facts are not directly inspectable or selectively queried. On MAB CR, M5 leads two of three models, consistent with the value of explicit update semantics for recency-sensitive conflicts. Cost separates otherwise competitive methods: M2 is consistently cheap, while M5 can be 10–100`\times` slower and is only worthwhile when its structural mechanism matches the task bottleneck.

Table 2: Memory substrates evaluated on ALFWorld-unseen and BigCodeBench-Hard. Within each model band, green marks the best substrate value on a metric, red marks the worst. `P_{\mathrm{avg}}` is the mean per-task partial-success score. Bold marks the per-model performance winner (TSR for ALFWorld, Pass@1 for BCB). M10 is omitted from both agent-centric benchmarks because the cumulative context exceeds the tested context windows; M9 is omitted from the Gemma-4 band because it is incompatible with the A4B MoE routing.

|  |  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  | ALFWorld-unseen | | | | | BigCodeBench-Hard | | |
| Model | Sub. | Family | TSR `\uparrow` | `\mathrm{Steps}\!\mid\!\mathcal{S}` `\downarrow` | `P_{\mathrm{avg}}` `\uparrow` | `E_{2}^{\mathrm{p90}}` `\downarrow` | `E_{15}` `\downarrow` | Pass@1 `\uparrow` | `E_{2}^{\mathrm{avg}}` `\downarrow` | `E_{15}` `\downarrow` |
| [Uncaptioned image] Qwen3-8B | - | NoMem | 5.7 | 12.2 | 13.5 | 13.2 | 488 | 8.1 | 3.8 | 4 |
| M1 | Flat | 5.2 | 5.9 | 6.6 | 16.1 | 672 | 9.5 | 5.0 | 5 |
| M2 | Flat | 6.7 | 6.0 | 9.4 | 15.7 | 647 | 10.1 | 4.9 | 5 |
| M3 | Text | 5.2 | 8.3 | 8.4 | 16.3 | 653 | 8.1 | 5.3 | 5 |
| M4 | Struct | 7.5 | 7.9 | 8.5 | 14.8 | 605 | 10.1 | 4.6 | 5 |
| M5 | Struct | 9.0 | 17.4 | 12.5 | 15.7 | 620 | 15.5 | 28.3 | 28 |
| M6 | Hier | 4.5 | 15.0 | 8.3 | 15.6 | 656 | 12.2 | 4.8 | 7 |
| M7 | Refine | 7.5 | 13.7 | 9.6 | 16.0 | 629 | 12.2 | 4.6 | 17 |
| M8 | Refine | 8.2 | 18.5 | 9.5 | 15.3 | 620 | 14.9 | 5.1 | 19 |
| M9 | Weight | 3.0 | 19.5 | 3.2 | 22.0 | 921 | 7.4 | 12.7 | 13 |
| M11 | Act | 11.9 | 14.2 | 14.5 | 13.5 | 553 | 13.5 | 16.8 | 17 |
| [Uncaptioned image] Qwen3-32B-AWQ | - | NoMem | 22.4 | 11.3 | 23.7 | 20.3 | 583 | 17.6 | 3.9 | 4 |
| M1 | Flat | 27.6 | 9.6 | 16.2 | 31.1 | 1.08k | 18.2 | 5.0 | 5 |
| M2 | Flat | 21.6 | 10.8 | 15.4 | 30.8 | 1.09k | 19.6 | 5.0 | 5 |
| M3 | Text | 26.9 | 9.9 | 21.8 | 30.3 | 950 | 18.2 | 5.4 | 8 |
| M4 | Struct | 26.9 | 12.4 | 24.3 | 28.6 | 816 | 17.6 | 4.9 | 20 |
| M5 | Struct | 23.1 | 11.4 | 23.0 | 27.4 | 851 | 16.2 | 31.2 | 31 |
| M6 | Hier | 23.9 | 9.9 | 22.8 | 26.8 | 817 | 16.2 | 4.4 | 7 |
| M7 | Refine | 32.1 | 11.1 | 29.9 | 27.2 | 716 | 17.6 | 4.3 | 21 |
| M8 | Refine | 22.4 | 12.4 | 21.3 | 28.0 | 886 | 13.5 | 4.6 | 22 |
| M9 | Weight | 29.9 | 12.1 | 27.4 | 21.4 | 612 | 14.2 | 14.6 | 15 |
| M11 | Act | 26.9 | 12.3 | 24.7 | 22.0 | 783 | 13.5 | 21.3 | 21 |
| [Uncaptioned image] Gemma-4-26B-A4B-IT | - | NoMem | 7.5 | 11.3 | 17.3 | 16.4 | 671 | 14.2 | 19.8 | 20 |
| M1 | Flat | 10.4 | 15.0 | 16.3 | 21.6 | 786 | 18.2 | 21.9 | 22 |
| M2 | Flat | 9.7 | 11.5 | 17.2 | 21.4 | 753 | 19.6 | 20.6 | 21 |
| M3 | Text | 10.4 | 14.8 | 14.9 | 20.5 | 781 | 14.2 | 23.4 | 23 |
| M4 | Struct | 8.2 | 14.5 | 13.9 | 22.5 | 942 | 18.9 | 22.4 | 23 |
| M5 | Struct | 4.5 | 8.5 | 9.4 | 19.9 | 749 | 20.9 | 45.6 | 46 |
| M6 | Hier | 10.4 | 11.4 | 18.1 | 21.1 | 741 | 18.9 | 24.3 | 28 |
| M7 | Refine | 8.2 | 10.1 | 17.8 | 21.1 | 788 | 16.9 | 24.1 | 37 |
| M8 | Refine | 8.2 | 12.5 | 18.5 | 20.1 | 763 | 18.2 | 21.2 | 26 |
| M11 | Act | 9.0 | 11.7 | 20.1 | 17.1 | 710 | 16.9 | 31.6 | 32 |

### 4.2 Agent-centric Benchmark

The same retrieval operation that sharpens code generation starves embodied
planning, splitting the agent-centric regime in two. On ALFWorld with the two Qwen backbones, the substrates that win
are those that *denoise* accumulated experience before it reaches the policy: M11, in its utterance-level re-prefill approximation of EpiCache,
doubles NoMem on Qwen3-8B by re-prefilling only the matched episode rather than the full trajectory buffer, and M7 achieves the table’s peak TSR of
`32.1\%` on Qwen3-32B-AWQ by distilling trajectories
into compact, reusable strategies, significantly above flat retrieval with M2 (`21.6\%`, exact McNemar `p{=}0.016`, Appendix [E.1](https://arxiv.org/html/2608.15008v2#A5.SS1 "E.1 Statistical Significance ‣ Appendix E Additional Analyses ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")). Both substrates share a common operation: they suppress
task-irrelevant tokens before retrieval, either by clustering raw turns into episodes
(M11) or by abstracting trajectories into reasoning templates (M7). Skill-based agent memories take the same route and store reusable skills distilled from past trajectories [[26](https://arxiv.org/html/2608.15008v2#bib.bib21), [39](https://arxiv.org/html/2608.15008v2#bib.bib104)]. Substrates that lack this denoising step show inconsistent gains across backbones. On Qwen3-32B-AWQ, flat retrievers range from slightly below NoMem (M2, 21.6 vs. 22.4) to well above it (M1, 27.6), and the text and structural stores (M3 26.9, M4 26.9, M5 23.1) likewise match or exceed NoMem, yet none close the gap to the refinement winner M7 (32.1). These gaps to NoMem lie within the bootstrap intervals of Appendix [E.1](https://arxiv.org/html/2608.15008v2#A5.SS1 "E.1 Statistical Significance ‣ Appendix E Additional Analyses ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"), so we read them as descriptive. On Qwen3-8B, however, flat retrievers straddle NoMem (M1 5.2 below, M2 6.7 above 5.7), and on Gemma-4 the flat, text, and hierarchical stores share the lead (10.4), suggesting that the value of raw-text retrieval on embodied planning is backbone-dependent rather than universally harmful. On embodied planning, retrieved trajectories compete for
attention with the current observation and admissible-action list, so on the Qwen backbones the substrate’s
value lies in noise removal rather than recall. Memories that compress raw
experience into actionable abstractions help most, while raw retrieval gains less because it dilutes the cue the policy
depends on. This is consistent with the action bottleneck reported for agentic RL, where the
training signal concentrates on the few action tokens of a trajectory [[40](https://arxiv.org/html/2608.15008v2#bib.bib105)].

On BigCodeBench-Hard the picture inverts because retrieved code snippets do not compete
with the task prompt, they extend it: a working solution to a related problem is reusable
scaffolding rather than a distractor. Retrieval therefore helps broadly on Qwen3-8B and Gemma-4, with M5 leading
both (`15.5\%` and `20.9\%` Pass@1) by surfacing structurally related
code through its graph and vector hybrid, and M2 lifts Pass@1 above NoMem on every
backbone. Yet the cost trade-off is steep: on Qwen3-32B-AWQ M2 (`19.6\%`) overtakes M5
(`16.2\%`) at roughly `1/6` the latency, and across backbones M5 pays 2 to 6 times the
inference cost of flat substrates, making it a strictly dominated choice when latency
matters. These Pass@1 gaps are small, so we read the BigCodeBench-Hard rankings as descriptive and rest the cost argument on the latency gaps. The two benchmarks therefore stress opposite memory operations: ALFWorld rewards
substrates that abstract noise away before retrieval, while BigCodeBench rewards
substrates that retrieve broadly without paying for abstraction, an asymmetry consistent
with the attention shift of Section [5.2](https://arxiv.org/html/2608.15008v2#S5.SS2 "5.2 Retrieval Scaling Reverses Across Regimes ‣ 5 Discussion ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").

Figure 3: Performance vs. latency across four benchmarks on Qwen3-32B-AWQ. (a) LoCoMo and (b) LongMemEval-S: absolute `P_{4}`. (c) ALFWorld-unseen and (d) BigCodeBench-Hard: `\Delta`-performance vs. inference-time overhead `E_{2}/E_{2}^{\mathrm{NoMem}}` (p90 in (c), mean in (d)) anchored at NoMem.

![Refer to caption](https://arxiv.org/html/2608.15008v2/subMem_K.png)

Figure 4: Retrieval breadth `k` scales oppositely on long-context QA versus sequential decision-making. Top: LoCoMo (Qwen3-8B, `n{=}1986`, `k{\in}\{1,2,5,10,20\}`). Bottom: ALFWorld-unseen (Qwen3-32B-AWQ, `n{=}134`, `k{\in}\{1,2,3,4,5\}`). green when the trend is in the preferred direction, red otherwise. Panel (f) shows mean steps over all episodes, unlike `P_{10}`, which averages successful episodes only. Black dashed lines mark NoMem, shown as No Memory baseline in the legend.

## 5 Discussion

### 5.1 Performance–Latency Tradeoffs Across Substrate Families

Figure [3](https://arxiv.org/html/2608.15008v2#S4.F3 "Figure 3 ‣ 4.2 Agent-centric Benchmark ‣ 4 Results ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") plots every memory substrate against its per-query latency under a shared Qwen3-32B-AWQ backbone. Panels (a, b) report absolute `P_{4}` on
long-form dialog QA; panels (c, d) re-anchor at NoMem so the y-axis becomes the gain over
no-memory and the x-axis the inference-time overhead `E_{2}/E_{2}^{\mathrm{NoMem}}` (p90 on ALFWorld, mean on BCB-Hard).

Disjoint Pareto frontiers across regimes.
The QA frontier (a, b) rises from the flat indices through M6, and through M3 and M10 on LoCoMo, to M5, which wins at `10` to `30\times` the latency of the
baselines. M6’s plotted latency is dominated by a one-off tree
build absorbed by the first query (Appendix [F](https://arxiv.org/html/2608.15008v2#A6 "Appendix F Full Tables ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")), and
its steady-state per-query cost is comparable to the Flat baselines. The agentic frontier (c, d) ends elsewhere, at flat retrieval on BCB-Hard (M2, `+2.0`% at `1.28\times`
overhead) and at the adapter M9 (`+7.5`% at `1.05\times`) and refinement-based distillation M7 (`+9.7`% at `1.34\times`) on ALFWorld.
That the quality ends of the two frontiers share *no* substrate confirms the divide of
Section [4.2](https://arxiv.org/html/2608.15008v2#S4.SS2 "4.2 Agent-centric Benchmark ‣ 4 Results ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"): the regimes reward fundamentally different operations,
recall over a stored corpus versus concise procedural cues, so a substrate engineered for
one provides no advantage at the other. Read as an allocation rule, a QA deployment moves along its frontier from the flat indices through M6 to M5, which buys the highest `P_{4}` at 10 to 30 times the baseline latency, while an agentic deployment relies on M2 for code reuse and on M7 for embodied planning.

Cost is heavy-tailed and frequently unrewarded.
Additional latency rarely buys quality monotonically: on LME-S, M4 at `234` s underperforms
M2 at `7.3` s, and M9 at `172` s buys little quality (`P_{4}{=}0.29`). The asymmetry sharpens on
agentic tasks, where M5, M9, and M11 incur `3.7` to `8.0` times overhead on BCB-Hard while
landing strictly below NoMem (`\Delta`Pass@1 between `-1.4`% and `-4.1`%). Substrate
cost therefore reflects mechanism complexity rather than expected gain: heavy machinery
earns its overhead only when its mechanism aligns with the task bottleneck, and turns into
pure tax otherwise. Attributing cost to stages changes the picture further. M4 and M5 spend most of their run time in the write phase (`E_{14}` of roughly 68–70K s and 56–58K s on LME-S, against mostly under 5K s for M1, M2, and M10; Appendix [F.2](https://arxiv.org/html/2608.15008v2#A6.SS2 "F.2 Full Tables for the LongMemEval-S and MAB Benchmarks ‣ Appendix F Full Tables ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")), so read-side accounting alone understates their cost. Because M9 pays for adapter training in GPU time while most other substrates pay in auxiliary-LLM tokens, we report wall-clock (`E_{14}`) and token counts (`E_{12}`) on separate axes rather than converting them into one currency. Family labels predict performance only weakly (Flat is mediocre on QA
yet leads BCB-Hard; Refine spans M7 best on ALFWorld and M8 near the bottom on two
panels), ruling out family-level routing and motivating the per-substrate analysis we
develop next.

### 5.2 Retrieval Scaling Reverses Across Regimes

Figure [4](https://arxiv.org/html/2608.15008v2#S4.F4 "Figure 4 ‣ 4.2 Agent-centric Benchmark ‣ 4 Results ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") sweeps retrieval depth `k` on LoCoMo with Qwen3-8B and on ALFWorld with Qwen3-32B-AWQ. On LoCoMo, `P_{4}` at `k{=}20` exceeds `P_{4}` at `k{=}1` for every substrate: each
retrieval raises the chance of surfacing a gold evidence turn, and surplus context is
passively ignorable because factual QA only requires the model to *find and extract*.
On ALFWorld the sign flips: task success *falls* with `k` (M7 falls by about seven points between
`k{=}1` and `k{=}5`, while the flat retrievers M1 and M2 fall below the no-memory baseline of `22.4\%`), and
mean steps per episode rise slightly (panel f). Because the dashed mean trend and its shaded band flip sign
between the two sweeps, which also differ in backbone, retrieval breadth rather than any individual substrate carries the reversal. The mean trend rises at every step on LoCoMo and stays below its `k{=}1` value at every larger depth on ALFWorld, where M7 leads at every depth, so the reversal is not tied to one retrieval depth (Appendix [B.2](https://arxiv.org/html/2608.15008v2#A2.SS2 "B.2 Calibration Protocol ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")).

![Refer to caption](https://arxiv.org/html/2608.15008v2/attn_region_heatmap.png)

Figure 5: Response-token attention under M1 retrieval for (a) LoCoMo and (b) ALFWorld.

Retrieval shifts attention in both regimes, but its consequence depends on where the answer
lives. As shown in Figure [5](https://arxiv.org/html/2608.15008v2#S5.F5 "Figure 5 ‣ 5.2 Retrieval Scaling Reverses Across Regimes ‣ 5 Discussion ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"), we probe the attention of the response tokens of
Qwen3-8B (eager attention, upper-half layers, head-summed mass) under M1
retrieval and bin attention into four regions: System, Retrieved, task Context
(transcript, trajectory, observation, admissible actions), and Cue (question and
next-action prompt). On *both* tasks, growing `k` funnels mass out of Context into
Retrieved (LoCoMo: `0.34\!\to\!0.10` vs. `0.05\!\to\!0.66`; ALFWorld:
`0.19\!\to\!0.17` vs. `0.34\!\to\!0.44`): the mechanism is identical, what differs is
which region carries the answer. On LoCoMo the load-bearing facts live in the retrieved
utterances, so siphoning attention toward them is precisely the desired behavior and
`P_{4}` rises. On ALFWorld the load-bearing region is the observation and admissible-action
list, so the same shift starves the decision and TSR falls; Cue mass also loses
`\approx 4`% between `k{=}1` and `k{=}5`. The probe covers one backbone and M1, so it is consistent with the TSR decline of the Qwen3-32B-AWQ sweep rather than a test of it. The implication for memory design is that retrieval
breadth is not a universal hyperparameter but a regime-conditioned one: any routing
decision should be informed by whether the prompt’s answer lives in retrieved memory or in
the task context window.

### 5.3 Scalability Under Growing Input Context

Scalability is a third routing axis: substrates that win at moderate scale can
become costly at long horizons, and vice versa. Figure [6](https://arxiv.org/html/2608.15008v2#S5.F6 "Figure 6 ‣ 5.3 Scalability Under Growing Input Context ‣ 5 Discussion ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") sweeps
content length on MAB Conflict Resolution from 6K to 262K tokens. Most external substrates
improve with scale: M8 climbs from `0.32` to `0.51` and M5 from `0.31` to `0.47`, because
longer histories give their write-side abstraction and entity-relation updates more
material to disambiguate which fact is current. Quality and cost grow together. The refinement family, represented here by the harness approximation M8, gains the most quality
but also the most latency, from about 1 s at 6K to about 98 s at 262K, the highest in the sweep,
because every refined bundle is prefilled at read time.

Figure 6: MAB CR scalability on Qwen3-32B-AWQ: `P_{4}` (bars, left) and per-query latency (lines, right, log) at 6K, 32K, 262K tokens.

The structural M4 and M5 and the full-context M10 reach 60 to 75 s at 262K, and only the flat indices stay under 10 s. Among the internal substrates, M10 also gains in quality (`0.27{\to}0.48`), although at 262K its buffer exceeds the context window and truncation keeps only the most recent entries, which on this recency task drops superseded facts; M9 stays at 0.17–0.22, lacking any mechanism for selective temporal update.
History depth is a selection signal beyond the current query.
Beyond regime (Section [5.1](https://arxiv.org/html/2608.15008v2#S5.SS1 "5.1 Performance–Latency Tradeoffs Across Substrate Families ‣ 5 Discussion ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")) and retrieval depth
(Section [5.2](https://arxiv.org/html/2608.15008v2#S5.SS2 "5.2 Retrieval Scaling Reverses Across Regimes ‣ 5 Discussion ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")), the substrates whose quality grows most with history (M8, M5, M10) pay one to two orders of magnitude more latency at 262K, while the flat indices stay cheap but gain less. A
substrate optimal for short sessions can thus become a liability over a long-running
agent’s lifetime.

No Substrate Wins Alone: Composition Is a Path to Universal Memory

The three diagnostic axes of Sections [5.1](https://arxiv.org/html/2608.15008v2#S5.SS1 "5.1 Performance–Latency Tradeoffs Across Substrate Families ‣ 5 Discussion ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")–[5.3](https://arxiv.org/html/2608.15008v2#S5.SS3 "5.3 Scalability Under Growing Input Context ‣ 5 Discussion ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")
converge: no single substrate can simultaneously serve recall over long histories, action
selection under attention pressure, and graceful scaling to long horizons, because these
regimes reward qualitatively different operations. A more promising path than a better single
substrate is a *multi-substrate or multi-agent memory system* composed by role, in which
refinement substrates curate *abstractions*,
structural and text
substrates hold *facts*, and activation and
flat substrates preserve raw *experience*. Substrate selection is therefore a design axis of the
harness. Choosing a substrate per observable regime beats the best fixed substrate on our benchmarks, and an ideal selector over two or three heterogeneous substrates shows how much a finer router could still gain (Appendices [E.3](https://arxiv.org/html/2608.15008v2#A5.SS3 "E.3 Substrate Routing ‣ Appendix E Additional Analyses ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") and [E.4](https://arxiv.org/html/2608.15008v2#A5.SS4 "E.4 Multi-Substrate Portfolios ‣ Appendix E Additional Analyses ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")).

## 6 Related Work

### Memory-augmented LLM agents.

Agent memory systems span a broad substrate design space, from external stores (vector
indices, text buffers, knowledge graphs, hierarchies, episodic narratives, distilled skill
memories [[41](https://arxiv.org/html/2608.15008v2#bib.bib4), [31](https://arxiv.org/html/2608.15008v2#bib.bib14), [30](https://arxiv.org/html/2608.15008v2#bib.bib13), [29](https://arxiv.org/html/2608.15008v2#bib.bib17), [42](https://arxiv.org/html/2608.15008v2#bib.bib25), [23](https://arxiv.org/html/2608.15008v2#bib.bib19), [24](https://arxiv.org/html/2608.15008v2#bib.bib18), [43](https://arxiv.org/html/2608.15008v2#bib.bib103), [26](https://arxiv.org/html/2608.15008v2#bib.bib21)])
to internal stores (parametric updates [[27](https://arxiv.org/html/2608.15008v2#bib.bib22)] and KV-cache
activations [[11](https://arxiv.org/html/2608.15008v2#bib.bib23), [28](https://arxiv.org/html/2608.15008v2#bib.bib24)]), with hybrids combining
several [[8](https://arxiv.org/html/2608.15008v2#bib.bib7), [44](https://arxiv.org/html/2608.15008v2#bib.bib26), [45](https://arxiv.org/html/2608.15008v2#bib.bib27)]. Most systems commit to a
fixed configuration at design time; we instead isolate the substrate as the experimental
variable and identify when each is preferable.

### Memory evaluation benchmarks and practices.

Existing benchmarks cover user-centric [[15](https://arxiv.org/html/2608.15008v2#bib.bib9), [16](https://arxiv.org/html/2608.15008v2#bib.bib2), [32](https://arxiv.org/html/2608.15008v2#bib.bib28), [46](https://arxiv.org/html/2608.15008v2#bib.bib106), [47](https://arxiv.org/html/2608.15008v2#bib.bib107)]
and agent-centric settings [[33](https://arxiv.org/html/2608.15008v2#bib.bib31), [34](https://arxiv.org/html/2608.15008v2#bib.bib32), [48](https://arxiv.org/html/2608.15008v2#bib.bib33)], but
the two regimes are typically evaluated in isolation, and evaluations emphasize end-task
accuracy while omitting deployment-critical dimensions such as write cost, latency,
storage, and management overhead. Our harness addresses both gaps; details are in
Appendix [G](https://arxiv.org/html/2608.15008v2#A7 "Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").

## 7 Conclusion

We presented a unified metric suite and a controlled harness evaluation of agent memory across 11 substrates, three
backbones, four benchmarks, and 26 metrics. The optimal substrate *reverses* between
long-form QA and agentic decision-making and shifts again with history depth. These reversals make substrate selection a design axis. Choosing a substrate per observable regime beats the best fixed substrate on our benchmarks, a router that reads only the question embedding gains on LoCoMo when its training data come from the same conversations, and most of the gap to an oracle selector remains open.

## Acknowledgments and Disclosure of Funding

We thank the anonymous reviewers for their constructive feedback. This work is supported by the BDSC Lab at the University of Illinois Chicago through U.S. National Science Foundation (NSF) grant POSE-2346158. It is also supported in part by NSF CAREER Award 2337877; the Schmidt Sciences Award on AI & Advanced Computing through the Science of Trustworthy AI program; and the University of Washington Tech Policy Lab. Any opinions, findings, conclusions, or recommendations expressed in this material are those of the authors and do not necessarily reflect those of the NSF or Schmidt Sciences.

## References

- [1]
  Y. Zhang, H. Ruan, Z. Fan, and A. Roychoudhury (2024)
  AutoCodeRover: autonomous program improvement.
  In Proceedings of the 33rd ACM SIGSOFT International Symposium on Software Testing and Analysis,
  pp. 1592–1604.
  Cited by: [§1](https://arxiv.org/html/2608.15008v2#S1.p1.1 "1 Introduction ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [2]
  C. Miao, H. P. Zou, Y. Li, Y. Chen, Y. Wang, F. Wang, Y. Li, W. Yang, B. He, X. Zhang, et al. (2026)
  RECODE-H: a benchmark for research code development with interactive human feedback.
  In The Fourteenth International Conference on Learning Representations,
  Cited by: [§1](https://arxiv.org/html/2608.15008v2#S1.p1.1 "1 Introduction ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [3]
  S. Zhou, F. F. Xu, H. Zhu, X. Zhou, R. Lo, A. Sridhar, X. Cheng, T. Ou, Y. Bisk, D. Fried, et al. (2024)
  WebArena: a realistic web environment for building autonomous agents.
  In The Twelfth International Conference on Learning Representations,
  Cited by: [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px2.p1.1 "Memory evaluation benchmarks. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§1](https://arxiv.org/html/2608.15008v2#S1.p1.1 "1 Introduction ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [4]
  W. Zhong, L. Guo, Q. Gao, H. Ye, and Y. Wang (2024)
  MemoryBank: enhancing large language models with long-term memory.
  In Proceedings of the AAAI Conference on Artificial Intelligence,
  Vol. 38, pp. 19724–19731.
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.5.1 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§1](https://arxiv.org/html/2608.15008v2#S1.p1.1 "1 Introduction ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [5]
  W. Zhang, W. Huang, Y. Liang, L. Jiang, Z. Wang, L. Yang, Z. Li, Y. Wu, H. Zhang, Y. Wang, et al. (2026)
  JARVIS-Bench: benchmarking personal intelligence agents on long-horizon real-user daily traces.
  In NeurIPS 2026 Workshop on Human-AI Coevolution,
  Cited by: [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px2.p1.1 "Memory evaluation benchmarks. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§1](https://arxiv.org/html/2608.15008v2#S1.p1.1 "1 Introduction ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [6]
  S. Ren, C. Xie, P. Jian, Z. Ren, C. Leng, and J. Zhang (2025)
  Towards scientific intelligence: a survey of LLM-based scientific agents.
  arXiv preprint arXiv:2503.24047.
  Cited by: [§1](https://arxiv.org/html/2608.15008v2#S1.p1.1 "1 Introduction ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [7]
  Z. Xiong, Y. Lin, W. Xie, P. He, Z. Liu, J. Tang, H. Lakkaraju, and Z. Xiang (2026)
  How memory management impacts LLM agents: an empirical study of experience-following behavior.
  In Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers),
  pp. 623–645.
  Cited by: [§1](https://arxiv.org/html/2608.15008v2#S1.p1.1 "1 Introduction ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [8]
  Z. Li, C. Xi, C. Li, D. Chen, B. Chen, S. Song, S. Niu, H. Wang, J. Yang, C. Tang, et al. (2025)
  MemOS: a memory OS for AI system.
  arXiv preprint arXiv:2507.03724.
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.5.8 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px1.p2.1 "Memory-augmented LLM agents. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§1](https://arxiv.org/html/2608.15008v2#S1.p1.1 "1 Introduction ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§6](https://arxiv.org/html/2608.15008v2#S6.SS0.SSS0.Px1.p1.1 "Memory-augmented LLM agents. ‣ 6 Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [9]
  Z. Zhou, A. Qu, Z. Wu, S. Kim, A. Prakash, D. Rus, J. Zhao, B. K. H. Low, and P. P. Liang (2026)
  MEM1: learning to synergize memory and reasoning for efficient long-horizon agents.
  In The Fourteenth International Conference on Learning Representations,
  Cited by: [§1](https://arxiv.org/html/2608.15008v2#S1.p1.1 "1 Introduction ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [10]
  B. Jiménez Gutiérrez, Y. Shu, Y. Gu, M. Yasunaga, and Y. Su (2024)
  HippoRAG: neurobiologically inspired long-term memory for large language models.
  Advances in Neural Information Processing Systems 37, pp. 59532–59569.
  Cited by: [§A.2](https://arxiv.org/html/2608.15008v2#A1.SS2.SSS0.Px3.p1.1 "Base-model concentration. ‣ A.2 Aggregate statistics ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.10.1 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§1](https://arxiv.org/html/2608.15008v2#S1.p1.1 "1 Introduction ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [11]
  Y. Li, Y. Huang, B. Yang, B. Venkitesh, A. Locatelli, H. Ye, T. Cai, P. Lewis, and D. Chen (2024)
  SnapKV: LLM knows what you are looking for before generation.
  Advances in Neural Information Processing Systems 37, pp. 22947–22970.
  Cited by: [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px1.p2.1 "Memory-augmented LLM agents. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§1](https://arxiv.org/html/2608.15008v2#S1.p1.1 "1 Introduction ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§6](https://arxiv.org/html/2608.15008v2#S6.SS0.SSS0.Px1.p1.1 "Memory-augmented LLM agents. ‣ 6 Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [12]
  L. Pan, L. Zou, S. Guo, J. Ni, and H. Zheng (2026)
  Natural-language agent harnesses.
  arXiv preprint arXiv:2603.25723.
  Cited by: [§1](https://arxiv.org/html/2608.15008v2#S1.p2.1 "1 Introduction ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [13]
  N. D. Bui (2026)
  Building effective AI coding agents for the terminal: scaffolding, harness, context engineering, and lessons learned.
  arXiv preprint arXiv:2603.05344.
  Cited by: [§1](https://arxiv.org/html/2608.15008v2#S1.p2.1 "1 Introduction ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [14]
  G. Zhang, H. Ren, C. Zhan, Z. Zhou, J. Wang, H. Zhu, W. Zhou, and S. Yan (2026)
  MemEvolve: meta-evolution of agent memory systems.
  In Forty-third International Conference on Machine Learning,
  Cited by: [§1](https://arxiv.org/html/2608.15008v2#S1.p2.1 "1 Introduction ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [15]
  A. Maharana, D. Lee, S. Tulyakov, M. Bansal, F. Barbieri, and Y. Fang (2024)
  Evaluating very long-term conversational memory of LLM agents.
  In Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers),
  pp. 13851–13870.
  Cited by: [§A.1](https://arxiv.org/html/2608.15008v2#A1.SS1.p2.1 "A.1 Inclusion criteria and data collection ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§C.3](https://arxiv.org/html/2608.15008v2#A3.SS3.SSS0.Px2.p2.1 "User-centric benchmarks. ‣ C.3 Coverage of the Memory Lifecycle ‣ Appendix C Benchmark Setups and Bank Alignment ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px2.p1.1 "Memory evaluation benchmarks. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§1](https://arxiv.org/html/2608.15008v2#S1.p3.1 "1 Introduction ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§3](https://arxiv.org/html/2608.15008v2#S3.SS0.SSS0.Px1.p1.1 "Benchmarks. ‣ 3 Experiment Design ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§6](https://arxiv.org/html/2608.15008v2#S6.SS0.SSS0.Px2.p1.1 "Memory evaluation benchmarks and practices. ‣ 6 Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [16]
  D. Wu, H. Wang, W. Yu, Y. Zhang, K. Chang, and D. Yu (2025)
  LongMemEval: benchmarking chat assistants on long-term interactive memory.
  In The Thirteenth International Conference on Learning Representations,
  Cited by: [§A.1](https://arxiv.org/html/2608.15008v2#A1.SS1.p2.1 "A.1 Inclusion criteria and data collection ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [1st item](https://arxiv.org/html/2608.15008v2#A3.I1.i1.p1.1 "In MemoryAgentBench (MAB). ‣ C.1 Benchmark Setups and Capability Definitions ‣ Appendix C Benchmark Setups and Bank Alignment ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§C.3](https://arxiv.org/html/2608.15008v2#A3.SS3.SSS0.Px2.p3.1 "User-centric benchmarks. ‣ C.3 Coverage of the Memory Lifecycle ‣ Appendix C Benchmark Setups and Bank Alignment ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§D.2](https://arxiv.org/html/2608.15008v2#A4.SS2.SSS0.Px4.p1.1 "P4: LLM Judge. ‣ D.2 Performance metrics ‣ Appendix D Metrics Definition and Assessment ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px2.p1.1 "Memory evaluation benchmarks. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§1](https://arxiv.org/html/2608.15008v2#S1.p3.1 "1 Introduction ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§3](https://arxiv.org/html/2608.15008v2#S3.SS0.SSS0.Px1.p1.1 "Benchmarks. ‣ 3 Experiment Design ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§6](https://arxiv.org/html/2608.15008v2#S6.SS0.SSS0.Px2.p1.1 "Memory evaluation benchmarks and practices. ‣ 6 Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [17]
  W. Huang, W. Zhang, Y. Liang, Y. Bei, Y. Chen, T. Feng, X. Pan, Z. Tan, Y. Wang, T. Wei, et al. (2026)
  A survey of agent memory in the second half: towards self-evolving and long-horizon agents.
  Transactions on Machine Learning Research.
  Note: Survey Certification
  Cited by: [Appendix A](https://arxiv.org/html/2608.15008v2#A1.p1.1 "Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§B.1](https://arxiv.org/html/2608.15008v2#A2.SS1.SSS0.Px1.p1.2 "Definition. ‣ B.1 Definition of a Memory Substrate ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§C.3](https://arxiv.org/html/2608.15008v2#A3.SS3.p1.1 "C.3 Coverage of the Memory Lifecycle ‣ Appendix C Benchmark Setups and Bank Alignment ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§1](https://arxiv.org/html/2608.15008v2#S1.p4.1 "1 Introduction ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [18]
  L. Xiong, C. Xiong, Y. Li, K. Tang, J. Liu, P. N. Bennett, J. Ahmed, and A. Overwijk (2021)
  Approximate nearest neighbor negative contrastive learning for dense text retrieval.
  In International Conference on Learning Representations,
  Cited by: [Table 4](https://arxiv.org/html/2608.15008v2#A2.T4.18.3.2.1.1 "In Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Table 5](https://arxiv.org/html/2608.15008v2#A2.T5.4.3.1.1.1 "In Component provenance. ‣ B.1 Definition of a Memory Substrate ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§2](https://arxiv.org/html/2608.15008v2#S2.SS0.SSS0.Px1.p1.1 "Substrate overview. ‣ 2 Memory Substrates and Configuration ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [19]
  S. Robertson and H. Zaragoza (2009)
  The probabilistic relevance framework: BM25 and beyond.
  Foundations and Trends in Information Retrieval 3, pp. 333–389.
  Cited by: [Table 4](https://arxiv.org/html/2608.15008v2#A2.T4.18.4.2.1.1 "In Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Table 5](https://arxiv.org/html/2608.15008v2#A2.T5.4.4.1.1.1 "In Component provenance. ‣ B.1 Definition of a Memory Substrate ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§2](https://arxiv.org/html/2608.15008v2#S2.SS0.SSS0.Px1.p1.1 "Substrate overview. ‣ 2 Memory Substrates and Configuration ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [20]
  K. Lee, X. Chen, H. Furuta, J. Canny, and I. Fischer (2024)
  A human-inspired reading agent with gist memory of very long contexts.
  In Forty-first International Conference on Machine Learning,
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.14.1 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§B.3](https://arxiv.org/html/2608.15008v2#A2.SS3.SSS0.Px3.p1.1 "M3: Gist Index (Text Record). ‣ B.3 External Substrates ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Table 4](https://arxiv.org/html/2608.15008v2#A2.T4.18.5.2.1.1 "In Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Table 5](https://arxiv.org/html/2608.15008v2#A2.T5.4.5.1.1.1 "In Component provenance. ‣ B.1 Definition of a Memory Substrate ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§2](https://arxiv.org/html/2608.15008v2#S2.SS0.SSS0.Px1.p1.1 "Substrate overview. ‣ 2 Memory Substrates and Configuration ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [21]
  W. Xu, Z. Liang, K. Mei, H. Gao, J. Tan, and Y. Zhang (2025)
  A-Mem: agentic memory for LLM agents.
  Advances in Neural Information Processing Systems 38, pp. 20004–20031.
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.16.1 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§B.3](https://arxiv.org/html/2608.15008v2#A2.SS3.SSS0.Px4.p1.1 "M4: Evolving Notes (Structural). ‣ B.3 External Substrates ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Table 4](https://arxiv.org/html/2608.15008v2#A2.T4.18.6.2.1.1 "In Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Table 5](https://arxiv.org/html/2608.15008v2#A2.T5.4.6.1.1.1 "In Component provenance. ‣ B.1 Definition of a Memory Substrate ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px3.p1.1 "Empirical evaluation practices in agent memory. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§2](https://arxiv.org/html/2608.15008v2#S2.SS0.SSS0.Px1.p1.1 "Substrate overview. ‣ 2 Memory Substrates and Configuration ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [22]
  Z. Guo, L. Xia, Y. Yu, T. Ao, and C. Huang (2025)
  LightRAG: simple and fast retrieval-augmented generation.
  In Findings of the Association for Computational Linguistics: EMNLP 2025,
  pp. 10746–10761.
  Cited by: [§B.3](https://arxiv.org/html/2608.15008v2#A2.SS3.SSS0.Px5.p1.1 "M5: Dual-Level Graph (Structural). ‣ B.3 External Substrates ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Table 4](https://arxiv.org/html/2608.15008v2#A2.T4.18.7.2.1.1 "In Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Table 5](https://arxiv.org/html/2608.15008v2#A2.T5.4.7.1.1.1 "In Component provenance. ‣ B.1 Definition of a Memory Substrate ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§2](https://arxiv.org/html/2608.15008v2#S2.SS0.SSS0.Px1.p1.1 "Substrate overview. ‣ 2 Memory Substrates and Configuration ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [23]
  P. Sarthi, S. Abdullah, A. Tuli, S. Khanna, A. Goldie, and C. D. Manning (2024)
  RAPTOR: recursive abstractive processing for tree-organized retrieval.
  In The Twelfth International Conference on Learning Representations,
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.13.1 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§B.3](https://arxiv.org/html/2608.15008v2#A2.SS3.SSS0.Px6.p1.1 "M6: Hierarchical Tree (Hierarchical). ‣ B.3 External Substrates ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Table 4](https://arxiv.org/html/2608.15008v2#A2.T4.18.8.2.1.1 "In Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Table 5](https://arxiv.org/html/2608.15008v2#A2.T5.4.8.1.1.1 "In Component provenance. ‣ B.1 Definition of a Memory Substrate ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px1.p1.1 "Memory-augmented LLM agents. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§2](https://arxiv.org/html/2608.15008v2#S2.SS0.SSS0.Px1.p1.1 "Substrate overview. ‣ 2 Memory Substrates and Configuration ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§6](https://arxiv.org/html/2608.15008v2#S6.SS0.SSS0.Px1.p1.1 "Memory-augmented LLM agents. ‣ 6 Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [24]
  H. Sun, S. Zeng, and B. Zhang (2026)
  H-MEM: hierarchical memory for high-efficiency long-term reasoning in LLM agents.
  In Proceedings of the 19th Conference of the European Chapter of the Association for Computational Linguistics (Volume 1: Long Papers),
  pp. 341–350.
  Cited by: [Table 4](https://arxiv.org/html/2608.15008v2#A2.T4.18.8.2.1.1 "In Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px1.p1.1 "Memory-augmented LLM agents. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§2](https://arxiv.org/html/2608.15008v2#S2.SS0.SSS0.Px1.p1.1 "Substrate overview. ‣ 2 Memory Substrates and Configuration ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§6](https://arxiv.org/html/2608.15008v2#S6.SS0.SSS0.Px1.p1.1 "Memory-augmented LLM agents. ‣ 6 Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [25]
  S. Ouyang, J. Yan, I. Hsu, Y. Chen, K. Jiang, Z. Wang, R. Han, L. T. Le, S. Daruki, X. Tang, et al. (2026)
  ReasoningBank: scaling agent self-evolving with reasoning memory.
  In The Fourteenth International Conference on Learning Representations,
  Cited by: [§A.2](https://arxiv.org/html/2608.15008v2#A1.SS2.SSS0.Px1.p1.1 "Benchmark concentration. ‣ A.2 Aggregate statistics ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§B.3](https://arxiv.org/html/2608.15008v2#A2.SS3.SSS0.Px7.p1.1 "M7: Distilled Strategies (Refinement). ‣ B.3 External Substrates ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Table 4](https://arxiv.org/html/2608.15008v2#A2.T4.18.9.2.1.1 "In Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Table 5](https://arxiv.org/html/2608.15008v2#A2.T5.4.9.1.1.1 "In Component provenance. ‣ B.1 Definition of a Memory Substrate ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§2](https://arxiv.org/html/2608.15008v2#S2.SS0.SSS0.Px1.p1.1 "Substrate overview. ‣ 2 Memory Substrates and Configuration ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [26]
  H. Zhang, Q. Long, J. Bao, T. Feng, W. Zhang, H. Yue, and W. Wang (2026)
  MemSkill: learning and evolving memory skills for self-evolving agents.
  arXiv preprint arXiv:2602.02474.
  Cited by: [§B.3](https://arxiv.org/html/2608.15008v2#A2.SS3.SSS0.Px8.p1.1 "M8: Skill Bundles (Refinement). ‣ B.3 External Substrates ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Table 4](https://arxiv.org/html/2608.15008v2#A2.T4.18.10.2.1.1 "In Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Table 5](https://arxiv.org/html/2608.15008v2#A2.T5.4.10.1.1.1 "In Component provenance. ‣ B.1 Definition of a Memory Substrate ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px1.p2.1 "Memory-augmented LLM agents. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§2](https://arxiv.org/html/2608.15008v2#S2.SS0.SSS0.Px1.p1.1 "Substrate overview. ‣ 2 Memory Substrates and Configuration ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§4.2](https://arxiv.org/html/2608.15008v2#S4.SS2.p1.1 "4.2 Agent-centric Benchmark ‣ 4 Results ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§6](https://arxiv.org/html/2608.15008v2#S6.SS0.SSS0.Px1.p1.1 "Memory-augmented LLM agents. ‣ 6 Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [27]
  L. Zhang, L. Zhang, S. Shi, X. Chu, and B. Li (2023)
  LoRA-FA: efficient and effective low rank representation fine-tuning.
  arXiv preprint arXiv:2308.03303.
  Cited by: [§B.4](https://arxiv.org/html/2608.15008v2#A2.SS4.SSS0.Px1.p1.1 "M9: Adapter Tuning (Weight). ‣ B.4 Internal Substrates ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Table 4](https://arxiv.org/html/2608.15008v2#A2.T4.18.12.2.1.1 "In Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Table 5](https://arxiv.org/html/2608.15008v2#A2.T5.4.12.1.1.1 "In Component provenance. ‣ B.1 Definition of a Memory Substrate ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px1.p2.1 "Memory-augmented LLM agents. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§2](https://arxiv.org/html/2608.15008v2#S2.SS0.SSS0.Px1.p1.1 "Substrate overview. ‣ 2 Memory Substrates and Configuration ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§6](https://arxiv.org/html/2608.15008v2#S6.SS0.SSS0.Px1.p1.1 "Memory-augmented LLM agents. ‣ 6 Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [28]
  M. Kim, A. Kundu, H. Kim, R. Dixit, and M. Cho (2026)
  EpiCache: episodic KV cache management for long-term conversation on resource-constrained environments.
  In Forty-third International Conference on Machine Learning,
  Cited by: [§B.4](https://arxiv.org/html/2608.15008v2#A2.SS4.SSS0.Px3.p1.1 "M11: Episode-Clustered Re-prefill (Activation). ‣ B.4 Internal Substrates ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Table 4](https://arxiv.org/html/2608.15008v2#A2.T4.18.14.2.1.1 "In Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Table 5](https://arxiv.org/html/2608.15008v2#A2.T5.4.14.1.1.1 "In Component provenance. ‣ B.1 Definition of a Memory Substrate ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px1.p2.1 "Memory-augmented LLM agents. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§2](https://arxiv.org/html/2608.15008v2#S2.SS0.SSS0.Px1.p1.1 "Substrate overview. ‣ 2 Memory Substrates and Configuration ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§6](https://arxiv.org/html/2608.15008v2#S6.SS0.SSS0.Px1.p1.1 "Memory-augmented LLM agents. ‣ 6 Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [29]
  P. Rasmussen, P. Paliychuk, T. Beauvais, J. Ryan, and D. Chalef (2025)
  Zep: a temporal knowledge graph architecture for agent memory.
  arXiv preprint arXiv:2501.13956.
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.22.8 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§B.1](https://arxiv.org/html/2608.15008v2#A2.SS1.SSS0.Px5.p1.1 "Production systems outside this frame. ‣ B.1 Definition of a Memory Substrate ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§B.5](https://arxiv.org/html/2608.15008v2#A2.SS5.p1.1 "B.5 Memory Substrate and Method Exclusion ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Table 7](https://arxiv.org/html/2608.15008v2#A2.T7.2.4.2.1 "In B.5 Memory Substrate and Method Exclusion ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px1.p1.1 "Memory-augmented LLM agents. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px3.p1.1 "Empirical evaluation practices in agent memory. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Appendix H](https://arxiv.org/html/2608.15008v2#A8.p1.1 "Appendix H Limitations ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§2](https://arxiv.org/html/2608.15008v2#S2.SS0.SSS0.Px1.p1.1 "Substrate overview. ‣ 2 Memory Substrates and Configuration ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§6](https://arxiv.org/html/2608.15008v2#S6.SS0.SSS0.Px1.p1.1 "Memory-augmented LLM agents. ‣ 6 Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [30]
  P. Chhikara, D. Khant, S. Aryan, T. Singh, and D. Yadav (2025)
  Mem0: building production-ready AI agents with scalable long-term memory.
  In ECAI 2025,
  Frontiers in Artificial Intelligence and Applications.
  External Links: [Document](https://dx.doi.org/10.3233/faia251160)
  Cited by: [§A.2](https://arxiv.org/html/2608.15008v2#A1.SS2.SSS0.Px2.p1.1 "Metric coverage. ‣ A.2 Aggregate statistics ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.2.8 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§B.1](https://arxiv.org/html/2608.15008v2#A2.SS1.SSS0.Px5.p1.1 "Production systems outside this frame. ‣ B.1 Definition of a Memory Substrate ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§B.5](https://arxiv.org/html/2608.15008v2#A2.SS5.p1.1 "B.5 Memory Substrate and Method Exclusion ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Table 7](https://arxiv.org/html/2608.15008v2#A2.T7.2.3.2.1 "In B.5 Memory Substrate and Method Exclusion ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§D.2](https://arxiv.org/html/2608.15008v2#A4.SS2.SSS0.Px4.p1.1 "P4: LLM Judge. ‣ D.2 Performance metrics ‣ Appendix D Metrics Definition and Assessment ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px1.p1.1 "Memory-augmented LLM agents. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px3.p2.1 "Empirical evaluation practices in agent memory. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Appendix H](https://arxiv.org/html/2608.15008v2#A8.p1.1 "Appendix H Limitations ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§2](https://arxiv.org/html/2608.15008v2#S2.SS0.SSS0.Px1.p1.1 "Substrate overview. ‣ 2 Memory Substrates and Configuration ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§6](https://arxiv.org/html/2608.15008v2#S6.SS0.SSS0.Px1.p1.1 "Memory-augmented LLM agents. ‣ 6 Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [31]
  C. Packer, S. Wooders, K. Lin, V. Fang, S. G. Patil, I. Stoica, and J. E. Gonzalez (2023)
  MemGPT: towards LLMs as operating systems.
  arXiv preprint arXiv:2310.08560.
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.3.1 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§B.1](https://arxiv.org/html/2608.15008v2#A2.SS1.SSS0.Px5.p1.1 "Production systems outside this frame. ‣ B.1 Definition of a Memory Substrate ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§B.5](https://arxiv.org/html/2608.15008v2#A2.SS5.p1.1 "B.5 Memory Substrate and Method Exclusion ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Table 7](https://arxiv.org/html/2608.15008v2#A2.T7.2.2.2.1 "In B.5 Memory Substrate and Method Exclusion ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px1.p1.1 "Memory-augmented LLM agents. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Appendix H](https://arxiv.org/html/2608.15008v2#A8.p1.1 "Appendix H Limitations ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§2](https://arxiv.org/html/2608.15008v2#S2.SS0.SSS0.Px1.p1.1 "Substrate overview. ‣ 2 Memory Substrates and Configuration ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§6](https://arxiv.org/html/2608.15008v2#S6.SS0.SSS0.Px1.p1.1 "Memory-augmented LLM agents. ‣ 6 Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [32]
  Y. Hu, Y. Wang, and J. McAuley (2026)
  Evaluating memory in LLM agents via incremental multi-turn interactions.
  In The Fourteenth International Conference on Learning Representations,
  Cited by: [§A.2](https://arxiv.org/html/2608.15008v2#A1.SS2.SSS0.Px1.p1.1 "Benchmark concentration. ‣ A.2 Aggregate statistics ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [1st item](https://arxiv.org/html/2608.15008v2#A3.I1.i1.p1.1 "In MemoryAgentBench (MAB). ‣ C.1 Benchmark Setups and Capability Definitions ‣ Appendix C Benchmark Setups and Bank Alignment ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§C.3](https://arxiv.org/html/2608.15008v2#A3.SS3.SSS0.Px2.p1.1 "User-centric benchmarks. ‣ C.3 Coverage of the Memory Lifecycle ‣ Appendix C Benchmark Setups and Bank Alignment ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§C.3](https://arxiv.org/html/2608.15008v2#A3.SS3.SSS0.Px2.p4.1 "User-centric benchmarks. ‣ C.3 Coverage of the Memory Lifecycle ‣ Appendix C Benchmark Setups and Bank Alignment ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px2.p1.1 "Memory evaluation benchmarks. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§3](https://arxiv.org/html/2608.15008v2#S3.SS0.SSS0.Px1.p1.1 "Benchmarks. ‣ 3 Experiment Design ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§6](https://arxiv.org/html/2608.15008v2#S6.SS0.SSS0.Px2.p1.1 "Memory evaluation benchmarks and practices. ‣ 6 Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [33]
  M. Shridhar, X. Yuan, M. Côté, Y. Bisk, A. Trischler, and M. Hausknecht (2021)
  ALFWorld: aligning text and embodied environments for interactive learning.
  In International Conference on Learning Representations,
  Cited by: [§C.3](https://arxiv.org/html/2608.15008v2#A3.SS3.SSS0.Px3.p1.1 "Agent-centric benchmarks. ‣ C.3 Coverage of the Memory Lifecycle ‣ Appendix C Benchmark Setups and Bank Alignment ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§E.1](https://arxiv.org/html/2608.15008v2#A5.SS1.SSS0.Px4.p1.1 "Sample sizes. ‣ E.1 Statistical Significance ‣ Appendix E Additional Analyses ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px2.p2.1 "Memory evaluation benchmarks. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§3](https://arxiv.org/html/2608.15008v2#S3.SS0.SSS0.Px1.p1.1 "Benchmarks. ‣ 3 Experiment Design ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§6](https://arxiv.org/html/2608.15008v2#S6.SS0.SSS0.Px2.p1.1 "Memory evaluation benchmarks and practices. ‣ 6 Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [34]
  T. Y. Zhuo, V. M. Chien, J. Chim, H. Hu, W. Yu, R. Widyasari, I. N. B. Yusuf, H. Zhan, J. He, I. Paul, et al. (2025)
  BigCodeBench: benchmarking code generation with diverse function calls and complex instructions.
  In The Thirteenth International Conference on Learning Representations,
  Cited by: [§C.3](https://arxiv.org/html/2608.15008v2#A3.SS3.SSS0.Px3.p2.1 "Agent-centric benchmarks. ‣ C.3 Coverage of the Memory Lifecycle ‣ Appendix C Benchmark Setups and Bank Alignment ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§E.1](https://arxiv.org/html/2608.15008v2#A5.SS1.SSS0.Px4.p1.1 "Sample sizes. ‣ E.1 Statistical Significance ‣ Appendix E Additional Analyses ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px2.p2.1 "Memory evaluation benchmarks. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§3](https://arxiv.org/html/2608.15008v2#S3.SS0.SSS0.Px1.p1.1 "Benchmarks. ‣ 3 Experiment Design ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§6](https://arxiv.org/html/2608.15008v2#S6.SS0.SSS0.Px2.p1.1 "Memory evaluation benchmarks and practices. ‣ 6 Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [35]
  A. Yang, A. Li, B. Yang, B. Zhang, B. Hui, B. Zheng, B. Yu, C. Gao, C. Huang, C. Lv, et al. (2025)
  Qwen3 technical report.
  arXiv preprint arXiv:2505.09388.
  Cited by: [§3](https://arxiv.org/html/2608.15008v2#S3.SS0.SSS0.Px2.p1.1 "Models, inference, and metrics. ‣ 3 Experiment Design ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [36]
  Gemma Team (2026)
  Gemma 4 technical report.
  arXiv preprint arXiv:2607.02770.
  Cited by: [§3](https://arxiv.org/html/2608.15008v2#S3.SS0.SSS0.Px2.p1.1 "Models, inference, and metrics. ‣ 3 Experiment Design ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [37]
  W. Kwon, Z. Li, S. Zhuang, Y. Sheng, L. Zheng, C. H. Yu, J. Gonzalez, H. Zhang, and I. Stoica (2023)
  Efficient memory management for large language model serving with PagedAttention.
  In Proceedings of the 29th Symposium on Operating Systems Principles,
  pp. 611–626.
  Cited by: [§3](https://arxiv.org/html/2608.15008v2#S3.SS0.SSS0.Px2.p1.1 "Models, inference, and metrics. ‣ 3 Experiment Design ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [38]
  OpenAI (2024)
  GPT-4o mini: advancing cost-efficient intelligence.
  Note: <https://openai.com/index/gpt-4o-mini-advancing-cost-efficient-intelligence/>
  Cited by: [§3](https://arxiv.org/html/2608.15008v2#S3.SS0.SSS0.Px2.p1.1 "Models, inference, and metrics. ‣ 3 Experiment Design ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [39]
  R. Xu, T. Yang, and W. Huang (2026)
  HyperSkill: self-evolving LLM agents via hypergraph-structured skill memory.
  arXiv preprint arXiv:2608.16114.
  Cited by: [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px1.p2.1 "Memory-augmented LLM agents. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§4.2](https://arxiv.org/html/2608.15008v2#S4.SS2.p1.1 "4.2 Agent-centric Benchmark ‣ 4 Results ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [40]
  L. He, J. Zhu, Y. Zhou, Z. Gu, J. Liu, W. Huang, H. P. Zou, D. Wipf, P. S. Yu, and Q. Wu (2026)
  Resolving action bottleneck: agentic reinforcement learning informed by token-level energy.
  arXiv preprint arXiv:2605.14558.
  Cited by: [§4.2](https://arxiv.org/html/2608.15008v2#S4.SS2.p1.1 "4.2 Agent-centric Benchmark ‣ 4 Results ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [41]
  J. S. Park, J. O’Brien, C. J. Cai, M. R. Morris, P. Liang, and M. S. Bernstein (2023)
  Generative agents: interactive simulacra of human behavior.
  In Proceedings of the 36th Annual ACM Symposium on User Interface Software and Technology,
  pp. 1–22.
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.2.1 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px1.p1.1 "Memory-augmented LLM agents. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§6](https://arxiv.org/html/2608.15008v2#S6.SS0.SSS0.Px1.p1.1 "Memory-augmented LLM agents. ‣ 6 Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [42]
  D. Jiang, Y. Li, G. Li, and B. Li (2026)
  MAGMA: a multi-graph based agentic memory architecture for AI agents.
  In Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers),
  pp. 36848–36865.
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.27.1 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px1.p1.1 "Memory-augmented LLM agents. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§6](https://arxiv.org/html/2608.15008v2#S6.SS0.SSS0.Px1.p1.1 "Memory-augmented LLM agents. ‣ 6 Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [43]
  Y. Zhou, X. Guo, B. Bayar, and S. H. Sengamedu (2026)
  Amory: building coherent narrative-driven agent memory through agentic reasoning.
  In Proceedings of the 19th Conference of the European Chapter of the Association for Computational Linguistics (Volume 1: Long Papers),
  pp. 3926–3938.
  Cited by: [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px1.p1.1 "Memory-augmented LLM agents. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§6](https://arxiv.org/html/2608.15008v2#S6.SS0.SSS0.Px1.p1.1 "Memory-augmented LLM agents. ‣ 6 Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [44]
  C. Latimer, N. Boschi, A. Neeser, C. Bartholomew, G. Srivastava, X. Wang, and N. Ramakrishnan (2025)
  Hindsight is 20/20: building agent memory that retains, recalls, and reflects.
  arXiv preprint arXiv:2512.12818.
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.20.1 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px1.p2.1 "Memory-augmented LLM agents. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§6](https://arxiv.org/html/2608.15008v2#S6.SS0.SSS0.Px1.p1.1 "Memory-augmented LLM agents. ‣ 6 Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [45]
  Y. Wang and X. Chen (2025)
  MIRIX: multi-agent memory system for LLM-based agents.
  arXiv preprint arXiv:2507.07957.
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.10.8 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px1.p2.1 "Memory-augmented LLM agents. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§6](https://arxiv.org/html/2608.15008v2#S6.SS0.SSS0.Px1.p1.1 "Memory-augmented LLM agents. ‣ 6 Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [46]
  W. Zhang, X. Wei, W. Huang, Z. Hui, C. Wang, M. Gong, and P. S. Yu (2026)
  MemoryCD: benchmarking long-context user memory of LLM agents for lifelong cross-domain personalization.
  In ICLR 2026 Workshop on Lifelong Agents: Learning, Aligning, Evolving,
  Cited by: [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px2.p1.1 "Memory evaluation benchmarks. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§6](https://arxiv.org/html/2608.15008v2#S6.SS0.SSS0.Px2.p1.1 "Memory evaluation benchmarks and practices. ‣ 6 Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [47]
  E. Ma, Y. Zhou, W. Huang, J. Yang, H. Ma, Z. Wang, C. Li, C. Miao, P. S. Yu, and Z. Wang (2026)
  MemAudit: auditing long-term agent memory via hidden user-state recovery.
  arXiv preprint arXiv:2606.24595.
  Cited by: [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px3.p1.1 "Empirical evaluation practices in agent memory. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§6](https://arxiv.org/html/2608.15008v2#S6.SS0.SSS0.Px2.p1.1 "Memory evaluation benchmarks and practices. ‣ 6 Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [48]
  C. E. Jimenez, J. Yang, A. Wettig, S. Yao, K. Pei, O. Press, and K. Narasimhan (2024)
  SWE-bench: can language models resolve real-world GitHub issues?.
  In The Twelfth International Conference on Learning Representations,
  Cited by: [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px2.p2.1 "Memory evaluation benchmarks. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§6](https://arxiv.org/html/2608.15008v2#S6.SS0.SSS0.Px2.p1.1 "Memory evaluation benchmarks and practices. ‣ 6 Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [49]
  Y. Hu, S. Liu, Y. Yue, G. Zhang, B. Liu, F. Zhu, J. Lin, H. Guo, S. Dou, Z. Xi, et al. (2025)
  Memory in the age of AI agents.
  arXiv preprint arXiv:2512.13564.
  Cited by: [Appendix A](https://arxiv.org/html/2608.15008v2#A1.p1.1 "Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [50]
  M. Guo, Q. Jiao, X. Liu, J. Pang, R. Yang, N. Xu, L. Che, H. Xue, Z. Wang, X. Cai, et al. (2026)
  Seeing, maintaining, and learning: the evolution of multimodal agent memory.
  arXiv preprint arXiv:2610.19366.
  Cited by: [Appendix A](https://arxiv.org/html/2608.15008v2#A1.p1.1 "Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [51]
  Y. Wang, R. Takanobu, Z. Liang, Y. Mao, Y. Hu, J. McAuley, and X. Wu (2025)
  Mem-`\alpha`: learning memory construction via reinforcement learning.
  arXiv preprint arXiv:2509.25911.
  Cited by: [§A.2](https://arxiv.org/html/2608.15008v2#A1.SS2.SSS0.Px1.p1.1 "Benchmark concentration. ‣ A.2 Aggregate statistics ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§A.2](https://arxiv.org/html/2608.15008v2#A1.SS2.SSS0.Px3.p1.1 "Base-model concentration. ‣ A.2 Aggregate statistics ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.3.8 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [52]
  Z. Fountas, M. Benfeghoul, A. Oomerjee, F. Christopoulou, G. Lampouras, H. B. Ammar, and J. Wang (2025)
  Human-inspired episodic memory for infinite context LLMs.
  In The Thirteenth International Conference on Learning Representations,
  Cited by: [§A.2](https://arxiv.org/html/2608.15008v2#A1.SS2.SSS0.Px1.p1.1 "Benchmark concentration. ‣ A.2 Aggregate statistics ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.9.1 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [53]
  J. Wang, R. Zhao, W. Wei, Y. Wang, M. Yu, J. Zhou, J. Xu, and L. Xu (2026)
  ComoRAG: a cognitive-inspired memory-organized RAG for stateful long narrative reasoning.
  In Proceedings of the AAAI Conference on Artificial Intelligence,
  Vol. 40, pp. 33557–33565.
  Cited by: [§A.2](https://arxiv.org/html/2608.15008v2#A1.SS2.SSS0.Px1.p1.1 "Benchmark concentration. ‣ A.2 Aggregate statistics ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.17.1 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [54]
  H. Yu, T. Chen, J. Feng, J. Chen, W. Dai, Q. Yu, Y. Zhang, W. Ma, J. Liu, M. Wang, et al. (2026)
  MemAgent: reshaping long-context LLM with multi-conv RL-based memory agent.
  In The Fourteenth International Conference on Learning Representations,
  Cited by: [§A.2](https://arxiv.org/html/2608.15008v2#A1.SS2.SSS0.Px1.p1.1 "Benchmark concentration. ‣ A.2 Aggregate statistics ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§A.2](https://arxiv.org/html/2608.15008v2#A1.SS2.SSS0.Px3.p1.1 "Base-model concentration. ‣ A.2 Aggregate statistics ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.4.8 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [55]
  J. Fang, X. Deng, H. Xu, Z. Jiang, Y. Tang, Z. Xu, S. Deng, Y. Yao, M. Wang, S. Qiao, et al. (2026)
  LightMem: lightweight and efficient memory-augmented generation.
  In The Fourteenth International Conference on Learning Representations,
  Cited by: [§A.2](https://arxiv.org/html/2608.15008v2#A1.SS2.SSS0.Px2.p1.1 "Metric coverage. ‣ A.2 Aggregate statistics ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.22.1 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px3.p2.1 "Empirical evaluation practices in agent memory. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [56]
  S. Sarin, L. Singh, B. Sarmah, and D. Mehta (2025)
  Memoria: a scalable agentic memory framework for personalized conversational AI.
  In 2025 5th International Conference on AI-ML-Systems (AIMLSystems),
  pp. 32–39.
  Cited by: [§A.2](https://arxiv.org/html/2608.15008v2#A1.SS2.SSS0.Px2.p1.1 "Metric coverage. ‣ A.2 Aggregate statistics ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.6.8 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [57]
  J. Wang and J. Han (2025)
  PropRAG: guiding retrieval with beam search over proposition paths.
  In Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing,
  pp. 6212–6227.
  Cited by: [§A.2](https://arxiv.org/html/2608.15008v2#A1.SS2.SSS0.Px3.p1.1 "Base-model concentration. ‣ A.2 Aggregate statistics ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.15.8 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [58]
  X. Wang, S. Wang, Y. Zhu, and B. Liu (2025)
  R`{}^{3}`Mem: bridging memory retention and retrieval via reversible compression.
  In Findings of the Association for Computational Linguistics: ACL 2025,
  pp. 4541–4557.
  Cited by: [§A.2](https://arxiv.org/html/2608.15008v2#A1.SS2.SSS0.Px3.p1.1 "Base-model concentration. ‣ A.2 Aggregate statistics ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.16.8 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [59]
  S. Yan, X. Yang, Z. Huang, E. Nie, Z. Ding, Z. Li, X. Ma, J. Bi, K. Kersting, J. Z. Pan, H. Schütze, V. Tresp, and Y. Ma (2026)
  Memory-R1: enhancing large language model agents to manage and utilize memories via reinforcement learning.
  In Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers),
  pp. 12805–12825.
  Cited by: [§A.2](https://arxiv.org/html/2608.15008v2#A1.SS2.SSS0.Px3.p1.1 "Base-model concentration. ‣ A.2 Aggregate statistics ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§A.2](https://arxiv.org/html/2608.15008v2#A1.SS2.SSS0.Px4.p1.1 "Joint coverage. ‣ A.2 Aggregate statistics ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.8.8 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [60]
  Y. Du, B. Wang, Y. Xiang, Z. Wang, W. Huang, B. Xue, B. Liang, X. Zeng, F. Mi, H. Bai, et al. (2026)
  Memory-T1: reinforcement learning for temporal reasoning in multi-session agents.
  In The Fourteenth International Conference on Learning Representations,
  Cited by: [§A.2](https://arxiv.org/html/2608.15008v2#A1.SS2.SSS0.Px3.p1.1 "Base-model concentration. ‣ A.2 Aggregate statistics ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.9.8 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [61]
  S. Wang, E. Yu, O. Love, T. Zhang, T. Wong, S. Scargall, and C. Fan (2026)
  MemMachine: a ground-truth-preserving memory system for personalized AI agents.
  arXiv preprint arXiv:2604.04853.
  Cited by: [§A.2](https://arxiv.org/html/2608.15008v2#A1.SS2.SSS0.Px4.p1.1 "Joint coverage. ‣ A.2 Aggregate statistics ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.24.8 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [62]
  J. Lu, S. An, M. Lin, G. Pergola, Y. He, D. Yin, X. Sun, and Y. Wu (2023)
  MemoChat: tuning LLMs to use memos for consistent long-range open-domain conversation.
  arXiv preprint arXiv:2308.08239.
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.4.1 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [63]
  Q. Wang, Y. Fu, Y. Cao, S. Wang, Z. Tian, and L. Ding (2025)
  Recursively summarizing enables long-term dialogue memory in large language models.
  Neurocomputing 639, pp. 130193.
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.6.1 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [64]
  B. Wang, X. Liang, J. Yang, H. Huang, Z. Wu, S. Wu, Z. Ma, and Z. Li (2025)
  SCM: enhancing large language model with self-controlled memory framework.
  In International Conference on Database Systems for Advanced Applications,
  pp. 188–203.
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.7.1 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [65]
  J. Kang, M. Ji, Z. Zhao, and T. Bai (2025)
  Memory OS of AI agent.
  In Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing,
  pp. 25961–25970.
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.7.8 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [66]
  T. Wang, M. Tao, R. Fang, H. Wang, S. Wang, Y. E. Jiang, and W. Zhou (2024)
  AI persona: towards life-long personalization of LLMs.
  arXiv preprint arXiv:2412.13103.
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.8.1 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [67]
  H. Li, C. Yang, A. Zhang, Y. Deng, X. Wang, and T. Chua (2025)
  Hello again! LLM-powered personalized agent for long-term dialogue.
  In Proceedings of the 2025 Conference of the Nations of the Americas Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers),
  pp. 5259–5276.
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.11.1 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [68]
  G. Zhang, B. Wang, Y. Ma, D. Zhao, and Z. Yu (2025)
  A multi-memory segment system for generating high-quality long-term memory content in agents.
  arXiv preprint arXiv:2508.15294v3.
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.11.8 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [69]
  A. Rezazadeh, Z. Li, W. Wei, and Y. Bao (2025)
  From isolated conversations to hierarchical schemas: dynamic tree memory representation for LLMs.
  In The Thirteenth International Conference on Learning Representations,
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.12.1 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [70]
  W. Ma, J. Nan, W. Wu, and Y. Chen (2025)
  What deserves memory: adaptive memory distillation for LLM agents.
  arXiv preprint arXiv:2508.03341.
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.12.8 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [71]
  P. Wang, M. Tian, J. Li, Y. Liang, Y. Wang, Q. Chen, T. Wang, Z. Lu, J. Ma, Y. E. Jiang, et al. (2025)
  O-Mem: omni memory system for personalized, long horizon, self-evolving agents.
  arXiv preprint arXiv:2511.13593.
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.13.8 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [72]
  N. Kim, K. T. Ong, Y. Hwang, M. Kang, I. Jihn, G. Kim, M. Kim, and J. Yeo (2025)
  PRINCIPLES: synthetic strategy memory for proactive dialogue agents.
  In Findings of the Association for Computational Linguistics: EMNLP 2025,
  pp. 21329–21368.
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.14.8 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [73]
  K. T. Ong, N. Kim, M. Gwak, H. Chae, T. Kwon, Y. Jo, S. Hwang, D. Lee, and J. Yeo (2025)
  Towards lifelong dialogue agents via timeline-based memory management.
  In Proceedings of the 2025 Conference of the Nations of the Americas Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers),
  pp. 8631–8661.
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.15.1 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [74]
  A. Tian, Y. Lu, X. Fan, C. Wang, L. Zhou, Y. Zhang, and Y. Liu (2026)
  RGMem: renormalization group-inspired memory evolution for language agents.
  In Forty-third International Conference on Machine Learning,
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.17.8 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [75]
  B. Y. Yan, C. Li, H. Qian, S. Lu, and Z. Liu (2025)
  General agentic memory via deep research.
  arXiv preprint arXiv:2511.18423.
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.18.1 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [76]
  Z. Tan, J. Yan, I. Hsu, R. Han, Z. Wang, L. Le, Y. Song, Y. Chen, H. Palangi, G. Lee, et al. (2025)
  In prospect and retrospect: reflective memory management for long-term personalized dialogue agents.
  In Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers),
  pp. 8416–8439.
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.18.8 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [77]
  Z. Ye, J. Huang, W. Chen, and Y. Zhang (2026)
  H-Mem: hybrid multi-dimensional memory management for long-context conversational agents.
  In Proceedings of the 19th Conference of the European Chapter of the Association for Computational Linguistics (Volume 1: Long Papers),
  pp. 7756–7775.
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.19.1 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [78]
  Z. Pan, Q. Wu, H. Jiang, X. Luo, H. Cheng, D. Li, Y. Yang, C. Lin, H. V. Zhao, L. Qiu, et al. (2025)
  SeCom: on memory construction and retrieval for personalized conversational agents.
  In The Thirteenth International Conference on Learning Representations,
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.19.8 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [79]
  Y. Wu, Y. Zhang, S. Liang, and Y. Liu (2025)
  SGMem: sentence graph memory for long-term conversational agents.
  arXiv preprint arXiv:2509.21212.
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.20.8 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [80]
  B. Jiménez Gutiérrez, Y. Shu, W. Qi, S. Zhou, and Y. Su (2025)
  From RAG to memory: non-parametric continual learning for large language models.
  In International Conference on Machine Learning,
  pp. 21497–21515.
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.21.1 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [81]
  S. Zhou and J. Han (2025)
  A simple yet strong baseline for long-term conversational memory of LLM agents.
  arXiv preprint arXiv:2511.17208.
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.21.8 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [82]
  Z. Huang, Z. Tian, Q. Guo, F. Zhang, Y. Zhou, D. Jiang, Z. Xie, and X. Zhou (2026)
  LiCoMemory: lightweight and cognitive agentic memory for efficient long-term reasoning.
  In Findings of the Association for Computational Linguistics: ACL 2026,
  pp. 36842–36858.
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.23.1 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [83]
  Y. Yu, L. Yao, Y. Xie, Q. Tan, J. Feng, Y. Li, and L. Wu (2026)
  Agentic memory: learning unified long-term and short-term memory management for large language model agents.
  In Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers),
  pp. 21457–21483.
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.24.1 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [84]
  C. Hu, X. Gao, Z. Zhou, D. Xu, Y. Bai, X. Li, H. Zhang, T. Li, C. Zhang, L. Bing, et al. (2026)
  EverMemOS: a self-organizing memory operating system for structured long-horizon reasoning.
  In Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers),
  pp. 45836–45853.
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.25.1 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [85]
  L. C. Borro, L. A. Macarini, G. Tindall, M. Montero, and A. B. Struck (2026)
  Memori: a persistent memory layer for efficient, context-aware LLM agents.
  arXiv preprint arXiv:2603.19935.
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.25.8 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [86]
  P. Daftari, K. Patel, S. Kapale, J. George, and S. Surendira (2026)
  Cognis: context-aware memory for conversational AI agents.
  arXiv preprint arXiv:2604.19771.
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.26.1 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [87]
  Y. Hu, J. Liu, J. Tan, Y. Zhu, and Z. Dou (2026)
  Memory matters more: event-centric memory as a logic map for agent searching and reasoning.
  In Findings of the Association for Computational Linguistics: ACL 2026,
  pp. 22389–22407.
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.26.8 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [88]
  A. Tian, Y. Li, X. Li, H. Zhen, L. Chen, X. Yu, Z. Dong, and M. Yuan (2026)
  SwiftMem: fast agentic memory via query-aware indexing.
  arXiv preprint arXiv:2601.08160.
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.27.8 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [89]
  M. Su, Y. Guo, Z. Hou, L. Bai, Z. Li, Y. Zhang, G. Yin, W. Lin, X. Jin, J. Guo, et al. (2026)
  Beyond dialogue time: temporal semantic memory for personalized LLM agents.
  In Findings of the Association for Computational Linguistics: ACL 2026,
  pp. 29935–29951.
  Cited by: [Table 3](https://arxiv.org/html/2608.15008v2#A1.T3.14.1.28.8 "In A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [90]
  Z. Zhang, Q. Dai, X. Bo, C. Ma, R. Li, X. Chen, J. Zhu, Z. Dong, and J. Wen (2025)
  A survey on the memory mechanism of large language model-based agents.
  ACM Transactions on Information Systems 43 (6), pp. 1–47.
  Cited by: [§B.1](https://arxiv.org/html/2608.15008v2#A2.SS1.SSS0.Px1.p1.2 "Definition. ‣ B.1 Definition of a Memory Substrate ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [91]
  Y. Wu, S. Liang, C. Zhang, Y. Wang, Y. Zhang, H. Guo, et al. (2025)
  From human memory to AI memory: a survey on memory mechanisms in the era of LLMs.
  arXiv preprint arXiv:2504.15965.
  Cited by: [§B.1](https://arxiv.org/html/2608.15008v2#A2.SS1.SSS0.Px1.p1.2 "Definition. ‣ B.1 Definition of a Memory Substrate ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [92]
  Y. Du, W. Huang, D. Zheng, Z. Wang, S. Montella, M. Lapata, et al. (2025)
  Rethinking memory in LLM based agents: representations, operations, and emerging topics.
  arXiv preprint arXiv:2505.00675.
  Cited by: [§B.1](https://arxiv.org/html/2608.15008v2#A2.SS1.SSS0.Px1.p1.2 "Definition. ‣ B.1 Definition of a Memory Substrate ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§C.3](https://arxiv.org/html/2608.15008v2#A3.SS3.p1.1 "C.3 Coverage of the Memory Lifecycle ‣ Appendix C Benchmark Setups and Bank Alignment ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [93]
  P. Du (2026)
  Memory for autonomous LLM agents: mechanisms, evaluation, and emerging frontiers.
  arXiv preprint arXiv:2603.07670.
  Cited by: [§B.1](https://arxiv.org/html/2608.15008v2#A2.SS1.SSS0.Px1.p1.2 "Definition. ‣ B.1 Definition of a Memory Substrate ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [94]
  D. Jiang, Y. Li, S. Wei, J. Yang, A. Kishore, A. Zhao, et al. (2026)
  Anatomy of agentic memory: taxonomy and empirical analysis of evaluation and system limitations.
  arXiv preprint arXiv:2602.19320.
  Cited by: [§B.1](https://arxiv.org/html/2608.15008v2#A2.SS1.SSS0.Px1.p1.2 "Definition. ‣ B.1 Definition of a Memory Substrate ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [95]
  Z. Xi, Y. Ding, W. Chen, B. Hong, H. Guo, J. Wang, X. Guo, D. Yang, C. Liao, W. He, et al. (2025)
  AgentGym: evaluating and training large language model-based agents across diverse environments.
  In Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers),
  pp. 27914–27961.
  Cited by: [§C.1](https://arxiv.org/html/2608.15008v2#A3.SS1.SSS0.Px3.p1.1 "ALFWorld. ‣ C.1 Benchmark Setups and Capability Definitions ‣ Appendix C Benchmark Setups and Bank Alignment ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§C.2](https://arxiv.org/html/2608.15008v2#A3.SS2.SSS0.Px1.p1.1 "ALFWorld. ‣ C.2 Bank–Test Semantic Alignment for ALFWorld and BCB-Hard ‣ Appendix C Benchmark Setups and Bank Alignment ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"),
  [§C.3](https://arxiv.org/html/2608.15008v2#A3.SS3.SSS0.Px3.p1.1 "Agent-centric benchmarks. ‣ C.3 Coverage of the Memory Lifecycle ‣ Appendix C Benchmark Setups and Bank Alignment ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [96]
  S. Yao, J. Zhao, D. Yu, N. Du, I. Shafran, K. Narasimhan, and Y. Cao (2023)
  ReAct: synergizing reasoning and acting in language models.
  In The Eleventh International Conference on Learning Representations,
  Cited by: [§E.1](https://arxiv.org/html/2608.15008v2#A5.SS1.SSS0.Px4.p1.1 "Sample sizes. ‣ E.1 Statistical Significance ‣ Appendix E Additional Analyses ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [97]
  N. Shinn, F. Cassano, A. Gopinath, K. Narasimhan, and S. Yao (2023)
  Reflexion: language agents with verbal reinforcement learning.
  In Advances in Neural Information Processing Systems,
  Cited by: [§E.1](https://arxiv.org/html/2608.15008v2#A5.SS1.SSS0.Px4.p1.1 "Sample sizes. ‣ E.1 Statistical Significance ‣ Appendix E Additional Analyses ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [98]
  T. Feng, C. Ye, F. Yu, T. Luo, J. Xu, X. Xu, et al. (2026)
  ElasticMem: latent memory as a learnable resource for LLM agents.
  arXiv preprint arXiv:2605.30690.
  Cited by: [§E.1](https://arxiv.org/html/2608.15008v2#A5.SS1.SSS0.Px4.p1.1 "Sample sizes. ‣ E.1 Statistical Significance ‣ Appendix E Additional Analyses ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [99]
  A. M. Sharifloo, M. Heydari, P. Kazerooni, D. Maninger, and M. Mezini (2025)
  Where do LLMs still struggle? An in-depth analysis of code generation benchmarks.
  In Proceedings of the 2nd IEEE/ACM International Conference on AI-powered Software (AIware), Data and Benchmark Track,
  Cited by: [§E.1](https://arxiv.org/html/2608.15008v2#A5.SS1.SSS0.Px4.p1.1 "Sample sizes. ‣ E.1 Statistical Significance ‣ Appendix E Additional Analyses ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [100]
  S. Wang, Q. Guo, K. Zhao, Y. Zhang, X. Li, X. Li, et al. (2025)
  CodeBoost: boosting code LLMs by squeezing knowledge from code snippets with RL.
  arXiv preprint arXiv:2508.05242.
  Cited by: [§E.1](https://arxiv.org/html/2608.15008v2#A5.SS1.SSS0.Px4.p1.1 "Sample sizes. ‣ E.1 Statistical Significance ‣ Appendix E Additional Analyses ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [101]
  P. Qin, R. Zhang, Q. Cao, and P. Xie (2026)
  DAJ: data-reweighted LLM judge for test-time scaling in code generation.
  arXiv preprint arXiv:2601.22230.
  Cited by: [§E.1](https://arxiv.org/html/2608.15008v2#A5.SS1.SSS0.Px4.p1.1 "Sample sizes. ‣ E.1 Statistical Significance ‣ Appendix E Additional Analyses ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [102]
  J. R. Landis and G. G. Koch (1977)
  The measurement of observer agreement for categorical data.
  Biometrics 33 (1), pp. 159–174.
  Cited by: [§E.2](https://arxiv.org/html/2608.15008v2#A5.SS2.SSS0.Px3.p1.1 "Reading the values. ‣ E.2 LLM-Judge Agreement ‣ Appendix E Additional Analyses ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [103]
  L. Zheng, W. Chiang, Y. Sheng, S. Zhuang, Z. Wu, Y. Zhuang, et al. (2023)
  Judging LLM-as-a-judge with MT-Bench and Chatbot Arena.
  In Advances in Neural Information Processing Systems, Datasets and Benchmarks Track,
  Cited by: [§E.2](https://arxiv.org/html/2608.15008v2#A5.SS2.SSS0.Px3.p1.1 "Reading the values. ‣ E.2 LLM-Judge Agreement ‣ Appendix E Additional Analyses ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [104]
  A. S. Thakur, K. Choudhary, V. S. Ramayapally, S. Vaidyanathan, and D. Hupkes (2025)
  Judging the judges: evaluating alignment and vulnerabilities in LLMs-as-judges.
  In Proceedings of the Fourth Workshop on Generation, Evaluation and Metrics (GEM`{}^{2}`),
  pp. 404–430.
  Cited by: [§E.2](https://arxiv.org/html/2608.15008v2#A5.SS2.SSS0.Px3.p1.1 "Reading the values. ‣ E.2 LLM-Judge Agreement ‣ Appendix E Additional Analyses ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [105]
  Z. He, Y. Wang, C. Zhi, Y. Hu, T. Chen, L. Yin, Z. Chen, T. A. Wu, S. Ouyang, Z. Wang, et al. (2026)
  MemoryArena: benchmarking agent memory in interdependent multi-session agentic tasks.
  arXiv preprint arXiv:2602.16313.
  Cited by: [§E.5](https://arxiv.org/html/2608.15008v2#A5.SS5.p1.1 "E.5 Supplementary Evaluation on MemoryArena ‣ Appendix E Additional Analyses ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [106]
  K. Lin, C. Snell, Y. Wang, C. Packer, S. Wooders, I. Stoica, and J. E. Gonzalez (2025)
  Sleep-time compute: beyond inference scaling at test-time.
  arXiv preprint arXiv:2504.13171.
  Cited by: [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px1.p2.1 "Memory-augmented LLM agents. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [107]
  H. Zhang, S. Fan, H. P. Zou, Y. Chen, Z. Wang, J. Zhou, C. Li, W. Huang, Y. Yao, K. Zheng, et al. (2026)
  CoEvoSkills: self-evolving agent skills via co-evolutionary verification.
  In Conference on Language Modeling (COLM),
  Cited by: [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px1.p2.1 "Memory-augmented LLM agents. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [108]
  E. Ma, C. Miao, Y. Chen, J. Yang, L. Fang, K. Zheng, H. Zhang, M. Xu, X. Yu, C. Li, et al. (2026)
  SkillNEO: non-elitist evolutionary optimization of agent skills.
  arXiv preprint arXiv:2610.20926.
  Cited by: [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px1.p2.1 "Memory-augmented LLM agents. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [109]
  H. Tan, Z. Zhang, C. Ma, X. Chen, Q. Dai, and Z. Dong (2025)
  MemBench: towards more comprehensive evaluation on the memory of LLM-based agents.
  In Findings of the Association for Computational Linguistics: ACL 2025,
  pp. 19336–19352.
  Cited by: [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px2.p1.1 "Memory evaluation benchmarks. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [110]
  Y. Shen, D. Pei, Y. Guo, J. Wang, Y. Guo, Z. Zhang, Q. Jia, J. Zhou, and G. Zhai (2026)
  EvolMem: a cognitive-driven benchmark for multi-session dialogue memory.
  arXiv preprint arXiv:2601.03543.
  Cited by: [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px2.p1.1 "Memory evaluation benchmarks. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [111]
  S. Yao, N. Shinn, P. Razavi, and K. R. Narasimhan (2025)
  `\tau`-bench: a benchmark for tool-agent-user interaction in real-world domains.
  In The Thirteenth International Conference on Learning Representations,
  Cited by: [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px2.p1.1 "Memory evaluation benchmarks. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").
- [112]
  Q. Li, S. Dou, K. Shao, C. Chen, and H. Hu (2026)
  Evaluating scoring bias in LLM-as-a-judge.
  In International Conference on Database Systems for Advanced Applications,
  pp. 19–34.
  Cited by: [Appendix G](https://arxiv.org/html/2608.15008v2#A7.SS0.SSS0.Px3.p2.1 "Empirical evaluation practices in agent memory. ‣ Appendix G Additional Related Work ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").

## Appendix A Landscape of LLM Memory-Augmented Systems

This appendix expands the motivation in Section [1](https://arxiv.org/html/2608.15008v2#S1 "1 Introduction ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") with the full survey of
52 memory-augmented LLM systems released between early 2023 and April 2026. We
document not the mechanisms of individual systems, which are catalogued by the recent
surveys of agentic memory [[17](https://arxiv.org/html/2608.15008v2#bib.bib11), [49](https://arxiv.org/html/2608.15008v2#bib.bib37), [50](https://arxiv.org/html/2608.15008v2#bib.bib111)], but how the current
work evaluates them. The result is shown in Table [3](https://arxiv.org/html/2608.15008v2#A1.T3 "Table 3 ‣ A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").

### A.1 Inclusion criteria and data collection

From this collection, we included papers that (a) propose a
novel memory method with an associated substrate or architecture, (b) report evaluation on
at least one memory benchmark, and (c) have a publicly available preprint. We excluded
survey papers, benchmark-only papers, and systems assessed only qualitatively. For each
candidate, we independently verified the arXiv identifier, title, year of first public
preprint, and evaluation setting against primary sources, discarding entries whose benchmarks or backbone
models could not be reliably confirmed.

For each system we record four evaluation dimensions.
(i) Benchmarks, grouped into six canonical categories:
LC=LoCoMo [[15](https://arxiv.org/html/2608.15008v2#bib.bib9)],
LME=LongMemEval [[16](https://arxiv.org/html/2608.15008v2#bib.bib2)],
MH=multi-hop QA (HotPotQA, MuSiQue, 2WikiMQA),
DS=DialSim, DMR=DMR, Other=other (MSC, Carecall, Conversation
Chronicles, MT-Bench+, Time-Dialog, RULER, NarrativeQA, PopQA, NQ, LongBench,
`\infty`-Bench, ESConv, PersuasionForGood, MemoryAgentBench, PersonaMem, custom
evaluations, …).
(ii) Performance metrics (A=accuracy, P=per-type breakdown).
(iii) Efficiency metrics (T=token usage, L=latency,
R=runtime, M=memory footprint, K=API-call count); only numeric
reports count. The five-dimension scheme used here is the most that any prior system
reports; the harness in Section [3](https://arxiv.org/html/2608.15008v2#S3 "3 Experiment Design ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") extends this to 15 efficiency metrics
(`E_{1}`–`E_{15}`) covering write, read, and management phases separately, together with
aggregate token, call, and latency totals.
(iv) Base LLM family: G for GPT-series (GPT-3.5/4/4o/4.1/5, including
*-mini* variants) or O for non-GPT open-source models (Llama, Qwen, DeepSeek,
…).

### A.2 Aggregate statistics

### Benchmark concentration.

Of 76 benchmark–system pairs in the 52 curated papers, LoCoMo accounts for 29 (38%) and
LongMemEval for 18 (24%), together covering 62% of adopted benchmarks. Adding DMR (2)
and DialSim (1) pushes the dialogue-centric share to 66%. The multi-hop QA cluster
contributes 4 pairs, drawn mainly from the HippoRAG/PropRAG lineage. The residual “Other”
category (22) is heterogeneous but, on closer inspection, remains overwhelmingly
dialogue-based: MSC, Carecall, Conversation Chronicles, MT-Bench+, and PersonaMem are all
multi-session dialogue benchmarks; MemoryAgentBench [[32](https://arxiv.org/html/2608.15008v2#bib.bib28)], adopted
as a primary evaluation by Mem-`\alpha` [[51](https://arxiv.org/html/2608.15008v2#bib.bib38)], is likewise a
multi-turn dialogue memory benchmark that re-packages QA, classification, and
summarization over incremental context. Only ReadAgent, RAPTOR,
EM-LLM [[52](https://arxiv.org/html/2608.15008v2#bib.bib39)], ComoRAG [[53](https://arxiv.org/html/2608.15008v2#bib.bib57)], and
MemAgent [[54](https://arxiv.org/html/2608.15008v2#bib.bib46)] target non-dialogue long-document settings (QuALITY,
NarrativeQA, LongBench, `\infty`-Bench, RULER). None of the 52 systems that evaluate on a
memory benchmark also reports an evaluation on agent-centric task execution. Memory systems
evaluated only on agent benchmarks, such as ReasoningBank [[25](https://arxiv.org/html/2608.15008v2#bib.bib49)],
fall outside criterion (b) and are therefore not in Table [3](https://arxiv.org/html/2608.15008v2#A1.T3 "Table 3 ‣ A.3 Trends over time ‣ Appendix A Landscape of LLM Memory-Augmented Systems ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"). Our
harness evaluates every substrate on ALFWorld and BigCodeBench-Hard next to the memory
benchmarks.

### Metric coverage.

Every system (100%) reports end-task accuracy and 35 (67%) also report a per-type
breakdown. By contrast, only 11 (21%) report any efficiency metric: latency (12%),
token consumption (10%), runtime (4%), memory footprint (4%), and API-call count (2%),
with zero reports of management cost or compression ratio.
LightMem [[55](https://arxiv.org/html/2608.15008v2#bib.bib10)] is the sole system to report four efficiency dimensions
simultaneously (token, latency, runtime, and API-call count);
Mem0 [[30](https://arxiv.org/html/2608.15008v2#bib.bib13)] and Memoria [[56](https://arxiv.org/html/2608.15008v2#bib.bib43)] each report two; the
remainder report one or none.

### Base-model concentration.

42 of 52 systems (81%) use a GPT-family model as their primary backbone, typically
GPT-4o-mini for extraction combined with GPT-4o or GPT-4.1-mini for generation.
The non-GPT systems span at least four lineages: the HippoRAG / PropRAG / R3Mem family
on multi-hop QA [[10](https://arxiv.org/html/2608.15008v2#bib.bib40), [57](https://arxiv.org/html/2608.15008v2#bib.bib71), [58](https://arxiv.org/html/2608.15008v2#bib.bib42)], the RL line
including Memory-R1 and Memory-T1 on Llama-3.1-8B and
Qwen-2.5 [[59](https://arxiv.org/html/2608.15008v2#bib.bib44), [60](https://arxiv.org/html/2608.15008v2#bib.bib45)],
Mem-`\alpha` on Qwen3-4B [[51](https://arxiv.org/html/2608.15008v2#bib.bib38)], and MemAgent on Qwen-2.5 with
RL [[54](https://arxiv.org/html/2608.15008v2#bib.bib46)].

### Joint coverage.

Figure [1](https://arxiv.org/html/2608.15008v2#S1.F1 "Figure 1 ‣ 1 Introduction ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")(c) projects each system onto the *benchmark breadth*
`\times` *efficiency depth* plane. 26 of 52 systems (50%) occupy the origin cell
`(1,0)`, a single benchmark with no efficiency metric. Only two
systems [[59](https://arxiv.org/html/2608.15008v2#bib.bib44), [61](https://arxiv.org/html/2608.15008v2#bib.bib47)] evaluate on three or more benchmarks, and
only LightMem reports three or more efficiency dimensions. No system occupies the
upper-right region `({\geq}3,{\geq}3)` that would indicate broad coverage together with
comprehensive efficiency reporting.

### A.3 Trends over time

The 2026 cohort does not close the evaluation gap. Only 2 of 9 (22%) report any
efficiency metric, statistically indistinguishable from the pre-2026 cohort. Per-type
breakdowns, however, have become near-universal: 9 of 9 2026 systems (100%) report them,
up from 60% in pre-2026 work. The field has converged on fine-grained accuracy analysis
as a standard but treats efficiency as an afterthought, an asymmetry we identify as the
single largest obstacle to principled substrate routing of the kind that universal
agent memory would need.

Table 3: Landscape of 52 memory-augmented LLM systems (2023–2026).
Year: first public preprint.
Benchmark codes: LC = LoCoMo, LME = LongMemEval, MH = Multi-hop QA, DS = DialSim, DMR = DMR.
Metric codes: A = accuracy, P = per-type, T = token, L = latency, R = runtime, M = memory size, K = API calls.
#B: distinct benchmarks used.
#E: efficiency dimensions reported (bold `{\geq}2`).
Base: G = GPT-series, O = open-source.
Summary: 81% GPT-family; 62% of benchmark pairs on LC + LME; only 21% report any efficiency metric; no system reaches `{\geq}3` benchmarks `\times` `{\geq}3` efficiency dimensions.

|  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| System | Year | Bench. | Metrics | #B | #E | Base | System | Year | Bench. | Metrics | #B | #E | Base |
| Generative Agents [[41](https://arxiv.org/html/2608.15008v2#bib.bib4)] | 2023 | Other | A | 1 | 0 | G | Mem0 [[30](https://arxiv.org/html/2608.15008v2#bib.bib13)] | 2025 | LC | A, P, T, L | 1 | 2 | G |
| MemGPT [[31](https://arxiv.org/html/2608.15008v2#bib.bib14)] | 2023 | DMR | A | 1 | 0 | G | Mem-`\alpha` [[51](https://arxiv.org/html/2608.15008v2#bib.bib38)] | 2025 | Other | A, P, M | 1 | 1 | O |
| MemoChat [[62](https://arxiv.org/html/2608.15008v2#bib.bib50)] | 2023 | Other | A | 1 | 0 | G | MemAgent [[54](https://arxiv.org/html/2608.15008v2#bib.bib46)] | 2025 | Other | A | 1 | 0 | O |
| MemoryBank [[4](https://arxiv.org/html/2608.15008v2#bib.bib15)] | 2023 | Other | A | 1 | 0 | G | MemOS [[8](https://arxiv.org/html/2608.15008v2#bib.bib7)] | 2025 | LC, LME | A, P | 2 | 0 | G |
| RSum [[63](https://arxiv.org/html/2608.15008v2#bib.bib51)] | 2023 | Other | A | 1 | 0 | G | Memoria [[56](https://arxiv.org/html/2608.15008v2#bib.bib43)] | 2025 | LME | A, T, L | 1 | 2 | G |
| SCM [[64](https://arxiv.org/html/2608.15008v2#bib.bib52)] | 2023 | Other | A | 1 | 0 | G | MemoryOS [[65](https://arxiv.org/html/2608.15008v2#bib.bib66)] | 2025 | LC | A, P | 1 | 0 | G |
| AI PERSONA [[66](https://arxiv.org/html/2608.15008v2#bib.bib53)] | 2024 | Other | A | 1 | 0 | G | Memory-R1 [[59](https://arxiv.org/html/2608.15008v2#bib.bib44)] | 2025 | LC, LME, Other | A, P | 3 | 0 | O |
| EM-LLM [[52](https://arxiv.org/html/2608.15008v2#bib.bib39)] | 2024 | Other | A, P | 1 | 0 | O | Memory-T1 [[60](https://arxiv.org/html/2608.15008v2#bib.bib45)] | 2025 | LC, Other | A, P | 2 | 0 | O |
| HippoRAG [[10](https://arxiv.org/html/2608.15008v2#bib.bib40)] | 2024 | MH | A, P | 1 | 0 | O | MIRIX [[45](https://arxiv.org/html/2608.15008v2#bib.bib27)] | 2025 | LC, Other | A, P, M | 2 | 1 | G |
| LD-Agent [[67](https://arxiv.org/html/2608.15008v2#bib.bib54)] | 2024 | Other | A, P | 1 | 0 | G | MMS [[68](https://arxiv.org/html/2608.15008v2#bib.bib67)] | 2025 | LC | A, P | 1 | 0 | G |
| MemTree [[69](https://arxiv.org/html/2608.15008v2#bib.bib55)] | 2024 | Other | A | 1 | 0 | G | Nemori [[70](https://arxiv.org/html/2608.15008v2#bib.bib68)] | 2025 | LC, LME | A, P | 2 | 0 | G |
| RAPTOR [[23](https://arxiv.org/html/2608.15008v2#bib.bib19)] | 2024 | Other | A | 1 | 0 | G | O-Mem [[71](https://arxiv.org/html/2608.15008v2#bib.bib69)] | 2025 | LC, LME | A, P | 2 | 0 | G |
| ReadAgent [[20](https://arxiv.org/html/2608.15008v2#bib.bib16)] | 2024 | Other | A | 1 | 0 | G | PRINCIPLES [[72](https://arxiv.org/html/2608.15008v2#bib.bib70)] | 2025 | Other | A | 1 | 0 | G |
| THEANINE [[73](https://arxiv.org/html/2608.15008v2#bib.bib56)] | 2024 | Other | A | 1 | 0 | G | PropRAG [[57](https://arxiv.org/html/2608.15008v2#bib.bib71)] | 2025 | MH, Other | A, P | 2 | 0 | O |
| A-Mem [[21](https://arxiv.org/html/2608.15008v2#bib.bib6)] | 2025 | LC, DS | A, P, T | 2 | 1 | G | R3Mem [[58](https://arxiv.org/html/2608.15008v2#bib.bib42)] | 2025 | Other | A | 1 | 0 | O |
| ComoRAG [[53](https://arxiv.org/html/2608.15008v2#bib.bib57)] | 2025 | Other | A | 1 | 0 | G | RGMem [[74](https://arxiv.org/html/2608.15008v2#bib.bib72)] | 2025 | LC, Other | A, P | 2 | 0 | G |
| GAM [[75](https://arxiv.org/html/2608.15008v2#bib.bib59)] | 2025 | LC | A | 1 | 0 | G | RMM [[76](https://arxiv.org/html/2608.15008v2#bib.bib73)] | 2025 | LC | A, P | 1 | 0 | G |
| H-Mem [[77](https://arxiv.org/html/2608.15008v2#bib.bib58)] | 2025 | LC | A, P, R | 1 | 1 | O | SeCom [[78](https://arxiv.org/html/2608.15008v2#bib.bib74)] | 2025 | LC | A, P | 1 | 0 | G |
| Hindsight [[44](https://arxiv.org/html/2608.15008v2#bib.bib26)] | 2025 | LC, LME | A, P | 2 | 0 | G | SGMem [[79](https://arxiv.org/html/2608.15008v2#bib.bib75)] | 2025 | LC, LME | A, P | 2 | 0 | G |
| HippoRAG 2 [[80](https://arxiv.org/html/2608.15008v2#bib.bib41)] | 2025 | MH | A, P | 1 | 0 | O | EMem [[81](https://arxiv.org/html/2608.15008v2#bib.bib76)] | 2025 | LC, LME | A, P | 2 | 0 | G |
| LightMem [[55](https://arxiv.org/html/2608.15008v2#bib.bib10)] | 2025 | LC, LME | A, P, T, L, R, K | 2 | 4 | G | Zep [[29](https://arxiv.org/html/2608.15008v2#bib.bib17)] | 2025 | DMR, LME | A, P, L | 2 | 1 | G |
| LiCoMemory [[82](https://arxiv.org/html/2608.15008v2#bib.bib60)] | 2025 | LC, LME | A, P, L | 2 | 1 | G |  |  |  |  |  |  |  |
| Agentic Memory [[83](https://arxiv.org/html/2608.15008v2#bib.bib61)] | 2026 | LC | A, P | 1 | 0 | G | MemMachine [[61](https://arxiv.org/html/2608.15008v2#bib.bib47)] | 2026 | LC, LME, MH | A, P, T | 3 | 1 | G |
| EverMemOS [[84](https://arxiv.org/html/2608.15008v2#bib.bib62)] | 2026 | LC, LME | A, P | 2 | 0 | G | Memori [[85](https://arxiv.org/html/2608.15008v2#bib.bib78)] | 2026 | LC | A, P | 1 | 0 | G |
| Cognis [[86](https://arxiv.org/html/2608.15008v2#bib.bib63)] | 2026 | LC, LME | A, P | 2 | 0 | G | MMM [[87](https://arxiv.org/html/2608.15008v2#bib.bib77)] | 2026 | LC, LME | A, P | 2 | 0 | G |
| MAGMA [[42](https://arxiv.org/html/2608.15008v2#bib.bib25)] | 2026 | LC, LME | A, P | 2 | 0 | G | SwiftMem [[88](https://arxiv.org/html/2608.15008v2#bib.bib64)] | 2026 | LC, LME | A, P, L | 2 | 1 | G |
|  |  |  |  |  |  |  | TSM [[89](https://arxiv.org/html/2608.15008v2#bib.bib65)] | 2026 | LC, LME | A, P | 2 | 0 | G |

## Appendix B Memory Substrate Implementation Details

Table 4: Memory substrate configurations. TF: training-free (✓) or requires weight modification (✗). LLM: auxiliary LLM required (✓) beyond final-answer generation. ‡ attention-guided utterance selection with re-prefill (Qwen3 hybrid-attention adaptation). § zero-shot LLM controller in place of PPO.

|  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
| Family | Method | TF | LLM | Write | Read | Mgmt |
| External Memory | | | | | | |
| Flat Index | M1  Dense Vector [[18](https://arxiv.org/html/2608.15008v2#bib.bib12)] | ✓ | ✗ | Encode; add to index | Dense top-`k` | — |
|  | M2  Sparse Vector [[19](https://arxiv.org/html/2608.15008v2#bib.bib84)] | ✓ | ✗ | Tokenize; append to BM25 | Sparse top-`k` | — |
| Text Record | M3  Gist Index [[20](https://arxiv.org/html/2608.15008v2#bib.bib16)] | ✓ | ✓ | LLM gist per page; index gists | LLM selects pages to expand | Text de-dup |
| Structural | M4  Evolving Notes [[21](https://arxiv.org/html/2608.15008v2#bib.bib6)] | ✓ | ✓ | LLM note per write; build links | ANN `+` link expansion | Evolution-triggered neighbour rewrites |
|  | M5  Dual-Level Graph [[22](https://arxiv.org/html/2608.15008v2#bib.bib48)] | ✓ | ✓ | LLM extracts entities `+` relations; build KG | KG `+` vector hybrid (mix mode) | Lazy batch indexing; cached graph |
| Hierarchical | M6  Hierarchical Tree [[23](https://arxiv.org/html/2608.15008v2#bib.bib19), [24](https://arxiv.org/html/2608.15008v2#bib.bib18)] | ✓ | ✓ | Embed; cluster into a four-level tree with LLM summaries | Collapsed-tree top-`k`; all levels | Top-level de-dup; decay |
| Refinement | M7  Distilled Strategies [[25](https://arxiv.org/html/2608.15008v2#bib.bib49)] | ✓ | ✓ | LLM judges; distills strategies; MaTTS | Dense over strategies; top-1 | Trajectory judge; strategy de-dup |
|  | M8  Skill Bundles [[26](https://arxiv.org/html/2608.15008v2#bib.bib21)]§ | ✓ | ✓ | Cluster experiences into bundles | Zero-shot LLM; all bundles prefilled | Merge and prune on overflow |
| Internal Memory | | | | | | |
| Weight | M9  Adapter Tuning [[27](https://arxiv.org/html/2608.15008v2#bib.bib22)] | ✗ | ✓ | LLM QA pairs; LoRA answer-only loss | Direct generation on base `+` adapter | — |
| Activation | M10  Full Context | ✓ | ✗ | Append to buffer | Concatenate; generate | Truncate at window |
|  | M11  Episode-Clustered Re-prefill [[28](https://arxiv.org/html/2608.15008v2#bib.bib24)]‡ | ✓ | ✗ | Cluster into episodes; keep 25% | Match to centroid; re-prefill episode | Episodic clustering; budgeting |

This appendix provides full implementation details for each of the eleven memory
substrates summarized in Section [2](https://arxiv.org/html/2608.15008v2#S2 "2 Memory Substrates and Configuration ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") and listed in
[Table 4](https://arxiv.org/html/2608.15008v2#A2.T4 "In Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"). It opens with the definition of a memory substrate and the calibration protocol shared by all substrates.

### B.1 Definition of a Memory Substrate

### Definition.

We use the term memory substrate for the storage-and-access layer of an agent harness.
It sits between the frozen backbone model and the agent controller, and
Section [1](https://arxiv.org/html/2608.15008v2#S1 "1 Introduction ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") introduces it as the infrastructure layer of the harness. A
substrate is specified by four properties.

1. 1.

   Representation. The form in which past experience is persisted, such as
   raw text, dense or sparse vectors, structured notes, an entity-relation graph,
   hierarchical summaries, distilled strategies or skill bundles, adapter weights, or
   context and activation state.
2. 2.

   Write. How an incoming interaction is encoded and committed to that
   representation.
3. 3.

   Read. How, given a query, the substrate surfaces stored content back into
   the model’s context, or, for parametric substrates, into its weights or activations.
4. 4.

   Management. How stored content is consolidated, updated, deduplicated, or
   forgotten over time.

This usage follows the write, read, and management decomposition of recent surveys and
taxonomies of agent memory [[90](https://arxiv.org/html/2608.15008v2#bib.bib86), [91](https://arxiv.org/html/2608.15008v2#bib.bib87), [92](https://arxiv.org/html/2608.15008v2#bib.bib88), [93](https://arxiv.org/html/2608.15008v2#bib.bib85), [94](https://arxiv.org/html/2608.15008v2#bib.bib89), [17](https://arxiv.org/html/2608.15008v2#bib.bib11)]. The partition into
external substrates, which keep information in data structures outside the model, and
internal substrates, which keep it in weights or activations, is taken from
[Huang et al. [17]](https://arxiv.org/html/2608.15008v2#bib.bib11) and is the one used in Table [4](https://arxiv.org/html/2608.15008v2#A2.T4 "Table 4 ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").

### Scope.

The substrate is the only component we vary. Above it, the prompt template, the
scaffolding, the final answer call, and the auxiliary LLM are held fixed. Below it, the
backbone weights are held fixed, with the qualifications that follow from the definition
itself. M9 is a weight change, so its write operation updates an adapter rather than an
external store. M10 and M11 are context or activation changes, so their read operation
fills the prompt or the KV cache rather than returning retrieved entries. This isolation
makes substrate-level effects more attributable than a comparison of complete systems
would allow. Where the evaluated method is a harness-compatible approximation of its
reference, we say so explicitly. This applies to M8 and M11, whose deviations are
described in their own paragraphs later in this appendix and noted in Appendix [H](https://arxiv.org/html/2608.15008v2#A8 "Appendix H Limitations ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").

### Complementarity.

Retrieval is a read-stage operation, and distillation is a write-stage choice about how
experience is stored. The two co-occur inside one pipeline. M7 distills trajectories into
strategies at write time and retrieves the single most relevant strategy at read time, in
the same way that M1 and M2 retrieve raw entries. What the study varies is therefore
mainly the storage and representation strategy (raw text in M1 and M2, gists in M3, notes
in M4, a graph in M5, a tree in M6, distilled strategies in M7, skill bundles in M8,
weights in M9, and context or activation state in M10 and M11), with the read interface
held fixed where applicable. Several of these mechanisms can be composed inside one system
rather than being mutually exclusive alternatives. A comparison between two rows of
Table [4](https://arxiv.org/html/2608.15008v2#A2.T4 "Table 4 ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") therefore identifies which configured substrate is preferable
under an operating regime, not a universally superior replacement. Some pairs are close
substitutes, for example M1 and M2, which share a representation family and a read
interface. Comparisons across stages, for example a parametric substrate against a
retrieval index, are best read as contrasts between design choices under the shared
harness.

### Component provenance.

Table [5](https://arxiv.org/html/2608.15008v2#A2.T5 "Table 5 ‣ Component provenance. ‣ B.1 Definition of a Memory Substrate ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") records, for each substrate, where each component comes from. R
marks a component taken from the reference implementation, or from the standard baseline
for M1, M2, and M10, which have no single reference system. H marks a component
standardized by the harness. A marks an approximation of the reference mechanism, and a
dash marks a component that is not part of the method. The harness standardizes the
backbone, the prompt template, the answer call, the auxiliary LLM (gpt-4o-mini),
the embedding encoder (text-embedding-3-small), the judge, decoding, and the
agent controller loop that calls write and read and produces the answer, for every method,
so the Controller column is H in every row. Because the encoder is shared, the dense
indices of M1, M4, M5, M6, and M7 are built with the harness encoder rather than with the
encoders of their reference implementations. Two read components are approximations. M8
replaces MemSkill’s PPO-trained controller with a zero-shot LLM that reads all refined
skill bundles prefilled into the prompt, while its skill-evolution pipeline, and therefore
its write and management components, follow the reference. M11 replaces EpiCache’s
in-place KV-cache edits with utterance-level re-prefill of the selected episode, while its
attention-based episode scoring and its 25% token budget follow the reference. Its
model-state entry is marked A for the same reason, since the harness fills the context
rather than the KV cache. M6 keeps
RAPTOR’s tree construction but defers it to the first read call, a scheduling choice that
leaves the mechanism unchanged and moves the one-off build cost into the first query
(Table [20](https://arxiv.org/html/2608.15008v2#A6.T20 "Table 20 ‣ Token accounting and memory quality. ‣ F.2 Full Tables for the LongMemEval-S and MAB Benchmarks ‣ Appendix F Full Tables ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")). Management is a dash for M1, M2, and M9, for which no
management operation on stored content is defined, although Appendix [D](https://arxiv.org/html/2608.15008v2#A4 "Appendix D Metrics Definition and Assessment ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")
books the adapter training steps of M9 under the management phase for cost attribution. The marks describe the provenance of mechanisms. The
values of the settings behind them are listed in Table [6](https://arxiv.org/html/2608.15008v2#A2.T6 "Table 6 ‣ Per-substrate settings. ‣ B.2 Calibration Protocol ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").

Table 5: Provenance of each substrate component. R: reference implementation. H: standardized by the harness. A: approximated. —: not part of the method. †: built at the first read call.

|  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
| Method | Stored representation | Write | Read | Mgmt | Model state | Controller |
| External Memory | | | | | | |
| M1 Dense Vector [[18](https://arxiv.org/html/2608.15008v2#bib.bib12)] | 1536-d dense embeddings of entries | R | R | — | — | H |
| M2 Sparse Vector [[19](https://arxiv.org/html/2608.15008v2#bib.bib84)] | BM25 inverted index over entries | R | R | — | — | H |
| M3 Gist Index [[20](https://arxiv.org/html/2608.15008v2#bib.bib16)] | one-sentence gist per page (indexed), original pages fetched on expansion | R | R | R | — | H |
| M4 Evolving Notes [[21](https://arxiv.org/html/2608.15008v2#bib.bib6)] | notes with description, keywords, tags, and semantic links | R | R | R | — | H |
| M5 Dual-Level Graph [[22](https://arxiv.org/html/2608.15008v2#bib.bib48)] | entity-relation graph plus chunk vector index | R | R | R | — | H |
| M6 Hierarchical Tree [[23](https://arxiv.org/html/2608.15008v2#bib.bib19)] | multi-level summary tree over raw entries | R† | R | R | — | H |
| M7 Distilled Strategies [[25](https://arxiv.org/html/2608.15008v2#bib.bib49)] | distilled reasoning strategies | R | R | R | — | H |
| M8 Skill Bundles [[26](https://arxiv.org/html/2608.15008v2#bib.bib21)] | skill bundles | R | A | R | — | H |
| Internal Memory | | | | | | |
| M9 Adapter Tuning [[27](https://arxiv.org/html/2608.15008v2#bib.bib22)] | LoRA adapter (`r{=}8`) | R | R | — | R, weights | H |
| M10 Full Context | raw history buffer | R | R | R | R, context | H |
| M11 Episode-Clustered Re-prefill [[28](https://arxiv.org/html/2608.15008v2#bib.bib24)] | episode clusters under a 25% token budget | R | A | R | A, context (re-prefill) | H |

### Production systems outside this frame.

Appendix [B.5](https://arxiv.org/html/2608.15008v2#A2.SS5 "B.5 Memory Substrate and Method Exclusion ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") reports Mem0 [[30](https://arxiv.org/html/2608.15008v2#bib.bib13)],
Zep [[29](https://arxiv.org/html/2608.15008v2#bib.bib17)], and MemGPT [[31](https://arxiv.org/html/2608.15008v2#bib.bib14)] separately. Their
defining mechanisms are management or controller policies that sit outside this
single-variable frame. Mem0 arbitrates between add, update, delete, and no-op operations
over extracted facts. Zep maintains a temporal knowledge graph with fact invalidation.
MemGPT runs a paging controller over its context tiers. M3 and M5 share parts of the
storage representation with these systems but not these policies, so results for M3 and
M5 are not results for Mem0, Zep, or MemGPT.

### B.2 Calibration Protocol

### Rule.

Two rules govern how substrates are configured. The shared experimental frame is
standardized, so that a difference between two substrates cannot come from the frame.
Every substrate-specific hyperparameter takes the value of its reference implementation,
so that no benchmark-specific tuning is done for any substrate.

### Standardized settings.

The frame fixes the following settings.

- •

  Backbones. Qwen3-8B, Qwen3-32B-AWQ, and Gemma-4-26B-A4B-IT, served with vLLM
  (Section [3](https://arxiv.org/html/2608.15008v2#S3 "3 Experiment Design ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")).
- •

  Decoding. Greedy decoding with temperature `0.0` and top-p `1.0`, at most
  `512` new tokens, and seed `42`.
- •

  Auxiliary LLM. gpt-4o-mini for every write-stage and management
  operation that calls an LLM.
- •

  Embedding encoder. text-embedding-3-small (1536 dimensions) for
  every substrate that embeds text.
- •

  Chunking. Inputs that arrive as a single text blob rather than as turns
  are split into 500-word chunks before they are written.
- •

  Judge. gpt-4o-mini at temperature `0` with the fixed templates of
  Appendix [D](https://arxiv.org/html/2608.15008v2#A4 "Appendix D Metrics Definition and Assessment ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").

### Per-substrate settings.

Table [6](https://arxiv.org/html/2608.15008v2#A2.T6 "Table 6 ‣ Per-substrate settings. ‣ B.2 Calibration Protocol ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") lists, for each substrate, the settings this paper states and
the source of each value. Harness marks a value fixed by the shared frame. Reference marks
the value of the reference implementation. Deviation marks one of the two documented
departures from a reference, the M8 read and the M11 read.

Table 6: Substrate-specific settings stated in this paper and the source of each value (Harness: shared frame. Reference: reference implementation. Deviation: documented departure). On LoCoMo, M1, M2, M4, and M6 read `k{=}10` entries.

|  |  |  |  |
| --- | --- | --- | --- |
| Method | Setting | Value | Source |
| External Memory | | | |
| M1 Dense Vector | Encoder | text-embedding-3-small, cosine similarity | Harness |
| M2 Sparse Vector | Scoring | BM25 over tokenized entries | Reference |
| M3 Gist Index | Write | one gist per page (about 500 words per page) | Reference |
|  | Read | LLM selects the pages to expand | Reference |
| M4 Evolving Notes | Write | LLM note (description, keywords, tags) and cosine links | Reference |
|  | Read | top-`k` notes by cosine, then link expansion | Reference |
|  | Management | evolution-triggered neighbor rewrites, consolidated every 100 evolutions | Reference |
| M5 Dual-Level Graph | Read | KG and vector hybrid (mix mode), reciprocal rank fusion | Reference |
|  | Management | lazy batch indexing with a cached graph | Reference |
| M6 Hierarchical Tree | Construction | recursive clustering and LLM summaries into a four-level tree, built at the first read call | Reference |
|  | Read | collapsed-tree top-`k` over all levels | Reference |
| M7 Distilled Strategies | Write | trajectory judge and MaTTS distillation | Reference |
|  | Read | top-1 strategy by dense similarity | Reference |
| M8 Skill Bundles | Write and mgmt | skill evolution (clustering, summarization, merging, pruning on overflow; bank capped at 12 skills) | Reference |
|  | Read | zero-shot LLM over all prefilled bundles | Deviation |
| Internal Memory | | | |
| M9 Adapter Tuning | Adapter | LoRA-FA, rank `r{=}8` | Reference |
|  | Training signal | answer-only loss on auxiliary-LLM QA pairs | Reference |
| M10 Full Context | Management | truncation at the context window | Reference |
| M11 Episode-Clustered Re-prefill | Budget | 4 episodes, 25% of utterances kept per episode | Reference |
|  | Read | utterance-level re-prefill of the matched episode | Deviation |

### Consequence.

Taking each hyperparameter from its reference implementation has one consequence for how
the tables should be read. Even at the same `k` the retrieved budget differs across
substrates, because the retrieved unit is an entry for M1 and M2, a note for M4, a tree
node for M6, and a strategy for M7, and the retrieved-token metric `E_{7}` records this
difference directly. Each comparison in Tables [1](https://arxiv.org/html/2608.15008v2#S4.T1 "Table 1 ‣ 4 Results ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")
and [2](https://arxiv.org/html/2608.15008v2#S4.T2 "Table 2 ‣ 4.1 User-centric Benchmark ‣ 4 Results ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") is therefore a comparison between configured methods as
their authors specify them, not between mechanisms at a matched budget. The `k` sweep of
Section [5.2](https://arxiv.org/html/2608.15008v2#S5.SS2 "5.2 Retrieval Scaling Reverses Across Regimes ‣ 5 Discussion ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") is the matched-depth reading for the substrates that
expose `k`.

### Sensitivity to retrieval depth.

Figure [4](https://arxiv.org/html/2608.15008v2#S4.F4 "Figure 4 ‣ 4.2 Agent-centric Benchmark ‣ 4 Results ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") is the one setting in which substrates are compared at matched
depth, and it also shows which conclusions are robust to the depth chosen. The sweep
covers LoCoMo with Qwen3-8B for M1, M2, M4, and M6 at `k\in\{1,2,5,10,20\}` (`n{=}1986`) and
ALFWorld with Qwen3-32B-AWQ for M1, M2, M4, M6, and M7 at `k\in\{1,2,3,4,5\}` (`n{=}134`). On
LoCoMo, `P_{4}` at `k{=}20` is above `P_{4}` at `k{=}1` for every swept substrate, and the
cross-substrate mean trend rises at every step of the sweep. On ALFWorld, the
cross-substrate mean trend stays below its `k{=}1` value at every larger depth. TSR at `k{=}5` is below TSR at `k{=}1` for
M1, M2, M6, and M7, and M4 is the only swept substrate whose `k{=}5` value is not clearly
below its `k{=}1` value. M7 stays above every other swept substrate and above the no-memory
baseline of `22.4\%` at every depth, falling by about seven points between `k{=}1` and
`k{=}5` (Section [5.2](https://arxiv.org/html/2608.15008v2#S5.SS2 "5.2 Retrieval Scaling Reverses Across Regimes ‣ 5 Discussion ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")), with its margin over the next substrate
narrowing at the larger depths. Within the sweep, the lead of M7 therefore does not depend on
the depth, and the two regimes disagree across the tested depths
rather than crossing at one setting. The per-query retrieved tokens (`E_{7}`, panels c and
g) differ across substrates at every `k`, which is the budget mismatch of the
previous paragraph measured directly. The paper contains no sweep over chunk granularity,
so the sensitivity of the user-centric results to the 500-word chunk size is not
characterized here.

### B.3 External Substrates

### M1: Dense Vector (Flat Index).

Each incoming utterance is encoded into a 1536-dimensional embedding via OpenAI text-embedding-3-small and appended to a flat index. At read time, the query is embedded with the same encoder and the top-`k` nearest neighbours are returned by cosine similarity. No LLM is invoked during write or read. No management operation is defined; the index grows monotonically.

### M2: Sparse Vector (Flat Index).

Each utterance is tokenized and appended to a BM25 inverted index. At read time, the query is tokenized and scored against all entries via BM25. No LLM is invoked.
No management operation is defined.

### M3: Gist Index (Text Record).

Implements ReadAgent [[20](https://arxiv.org/html/2608.15008v2#bib.bib16)]. At write time, an auxiliary LLM generates a one-sentence gist summary for each page of the input and indexes these gists. At read time, the same LLM reads all gists and selects which pages to expand to their full original text; the expanded pages are concatenated as context for the final answer. Management consists of text-level deduplication over stored gists. The two-stage read pipeline (gist filter then page expand) means read cost scales with the number of stored pages, which becomes expensive on long histories.

### M4: Evolving Notes (Structural).

Implements A-Mem [[21](https://arxiv.org/html/2608.15008v2#bib.bib6)]. At write time,
an auxiliary LLM generates a structured note (with contextual description,
keywords, and tags) for each incoming message, then computes cosine
similarity between the new note’s dense embedding and existing notes to
establish semantic links. At read time, the query embedding is matched
against stored notes via cosine similarity, returning the top-k most
relevant notes; the result set is further expanded by following the
note-level links established at write time. Management is triggered by
an evolution detector: when a new note significantly updates an existing
one, the LLM rewrites the affected neighbours to maintain consistency.

### M5: Dual-Level Graph (Structural).

Implements LightRAG [[22](https://arxiv.org/html/2608.15008v2#bib.bib48)]. At write time, an auxiliary LLM extracts entities and relations from the input and builds a knowledge graph (KG) alongside a chunk-level vector index. At read time, queries are routed through a hybrid mode that combines KG traversal (entity and relation matching) with dense vector search over the chunk store, merging results via reciprocal rank fusion. Management uses lazy batch indexing: the KG and vector index are rebuilt periodically rather than incrementally, with a cached graph serving queries between rebuilds.

### M6: Hierarchical Tree (Hierarchical).

Implements RAPTOR [[23](https://arxiv.org/html/2608.15008v2#bib.bib19)]. Incoming entries are embedded at write time; on the first read call,
entries are recursively clustered and each cluster is summarised by
an auxiliary LLM to form
the next level of the tree, with clustering and summarization repeated until
the tree has four levels. The resulting four-level tree contains
the raw entries at the leaves and progressively more abstract summaries at
higher internal nodes. At read time, we use RAPTOR’s collapsed-tree variant:
nodes from every level are flattened into a single dense index and the query
embedding selects the top-`k` most relevant nodes regardless of depth, so
fine-grained leaves and coarse summaries compete for the same retrieval
slots.
In our implementation, clustering and summarisation are deferred to
the first read call (lazy construction); write() only embeds
and appends entries, and the one-off build cost is therefore absorbed
by the first query (see Tab. [20](https://arxiv.org/html/2608.15008v2#A6.T20 "Table 20 ‣ Token accounting and memory quality. ‣ F.2 Full Tables for the LongMemEval-S and MAB Benchmarks ‣ Appendix F Full Tables ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")).
Management performs top-level deduplication and temporal decay,
removing or demoting summary nodes superseded by more recent entries.

### M7: Distilled Strategies (Refinement).

Implements ReasoningBank [[25](https://arxiv.org/html/2608.15008v2#bib.bib49)]. At write time, an auxiliary LLM judges each completed trajectory (success or failure), then distills the judgment into a structured, reusable reasoning strategy via memory-aware test-time scaling (MaTTS). Strategies are indexed via dense embedding. At read time, the query is embedded and the most relevant strategy is retrieved. Management performs trajectory-level judging and strategy deduplication: redundant or superseded strategies are merged or pruned.

### M8: Skill Bundles (Refinement).

Implements MemSkill [[26](https://arxiv.org/html/2608.15008v2#bib.bib21)] with one deviation. We
keep the online skill-evolution pipeline (clustering, summarisation,
merging, pruning), so M8 incurs the write- and management-side LLM
cost reported in the efficiency tables. We replace only the
PPO-trained controller that originally selects a single skill bundle
at read time with a zero-shot LLM: all refined skill bundles are
prefilled into the prompt, and the model attends to the full skill
set when generating the answer for the current query. We make this
swap because no other substrate involves RL training, and keeping M8
RL-driven would make its training cost dominate the efficiency axis.

### B.4 Internal Substrates

### M9: Adapter Tuning (Weight).

Implements LoRA-FA [[27](https://arxiv.org/html/2608.15008v2#bib.bib22)]. At write time, an auxiliary LLM synthesizes question-answer pairs from the incoming content (e.g., Q: “Where does the user live?” A: “San Francisco”). A LoRA adapter (`r{=}8`) is then fine-tuned on these pairs using answer-only loss on the base model. At read time, the query is passed directly to the base model with the adapter applied; no explicit retrieval step occurs.

### M10: Full Context (Activation).

The full-history concatenation baseline. At write time, each incoming message is appended
verbatim to a running buffer. At read time, the entire buffer is concatenated and passed
as context to the model for generation. Management consists solely of truncation: when
the buffer exceeds the model’s context window, the oldest entries are dropped. This
substrate establishes the “raw history retention” reference point against which all
other substrates are compared. We omit M10 from ALFWorld evaluation because cumulative
trajectory text exceeds the context window of every backbone we test.

### M11: Episode-Clustered Re-prefill (Activation).

Implements EpiCache [[28](https://arxiv.org/html/2608.15008v2#bib.bib24)] with one deviation (marked ‡ in [Table 4](https://arxiv.org/html/2608.15008v2#A2.T4 "In Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")). At write time, past conversational turns are clustered into episodic groups, and a token budget of 25% is applied (only the top quarter of tokens per episode are retained). At read time, the query is encoded and matched to episode centroids; the best-matching episode is re-prefilled into the KV cache for generation.

Deviation from reference. The original EpiCache edits the KV cache in place using custom attention kernels. Qwen3’s hybrid attention architecture (mixing full attention and sliding-window attention across layers) is not supported by the authors’ released kernels. Our implementation preserves the paper’s attention-based episode scoring but applies it at the level of whole utterances: the selected episode’s utterances are re-prefilled into the context rather than surgically inserted into the KV cache. This changes the read-time mechanism (re-prefill vs. in-place edit) but preserves the core design principle of episodic selection with budget constraints.

### B.5 Memory Substrate and Method Exclusion

We considered three additional substrates, MemGPT [[31](https://arxiv.org/html/2608.15008v2#bib.bib14)], Mem0 [[30](https://arxiv.org/html/2608.15008v2#bib.bib13)], and Zep [[29](https://arxiv.org/html/2608.15008v2#bib.bib17)], which are widely cited as production-grade memory systems but which we exclude from the main comparison because their defining mechanisms are policies outside the single-variable frame and because of their auxiliary-LLM budget. [Table 7](https://arxiv.org/html/2608.15008v2#A2.T7 "In B.5 Memory Substrate and Method Exclusion ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") reports the auxiliary-LLM cost each substrate incurs on a single end-to-end LoCoMo run (ten conversations, 1,986 queries, GPT-4o-mini aux model), measured with the same harness used for every substrate in [Table 4](https://arxiv.org/html/2608.15008v2#A2.T4 "In Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"). Embedding calls and embedding latency are excluded because they are served by a local FAISS index shared across runs.

Table 7: Auxiliary-LLM cost on a full LoCoMo run (ten conversations, 1,986 queries; GPT-4o-mini aux model, embedding excluded). Costs are one to two orders of magnitude above the lightest retrieval baselines (e.g. M2 BM25 issues zero aux-LLM calls and finishes in roughly ten minutes).

|  |  |  |  |
| --- | --- | --- | --- |
| Substrate | Method | Auxiliary LLM calls | Execution time |
| Text Record | MemGPT [[31](https://arxiv.org/html/2608.15008v2#bib.bib14)] | 2,739 | 16.3 h |
| Text Record | Mem0 [[30](https://arxiv.org/html/2608.15008v2#bib.bib13)] | 8,984 | 11.8 h |
| Hierarchical | Zep [[29](https://arxiv.org/html/2608.15008v2#bib.bib17)] | 7,624 | 23.1 h |

These three systems are LLM-call-heavy by design: every write triggers multiple auxiliary calls (entity extraction, fact deduplication, conflict resolution, temporal invalidation, agent tool dispatch), and every read fires further reranker, summary, or agent-loop calls. On a single LoCoMo run this manifests as roughly 2,700 to 9,000 auxiliary LLM calls per substrate and wall-clock budgets of 11 to 23 hours, one to two orders of magnitude above the lighter retrieval baselines.

Because the goal of our evaluation is a controlled cross-substrate ablation rather than a production-cost benchmark, we report these systems here as a production-cost reference and exclude them from the main comparison. Their defining mechanisms are policies rather than storage layers. Mem0 arbitrates every extracted fact with add, update, delete, or no-op operations, Zep maintains a temporal knowledge graph that invalidates superseded facts, and MemGPT lets the model page content between memory tiers through function calls. These policies sit outside the single-variable frame of Appendix [B.1](https://arxiv.org/html/2608.15008v2#A2.SS1 "B.1 Definition of a Memory Substrate ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"). Lighter substrates in [Table 4](https://arxiv.org/html/2608.15008v2#A2.T4 "In Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") share parts of their storage representation (per-input text distillation in M3, entity and relation indexing in M5, a record store in M3) but not their management or control policies, so results for M3 and M5 should not be read as results for Mem0, Zep, or MemGPT. Including the three systems would also dominate the wall-clock and token-count columns by an order of magnitude and obscure the architectural differences our evaluation is designed to surface.

## Appendix C Benchmark Setups and Bank Alignment

This appendix expands the benchmark descriptions in Section [3](https://arxiv.org/html/2608.15008v2#S3 "3 Experiment Design ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") with full
capability definitions, evaluation splits, and pool construction details, and audits the
semantic alignment between the offline retrieval banks and their evaluation pools for the
two agent-centric benchmarks.

### C.1 Benchmark Setups and Capability Definitions

### LoCoMo.

The benchmark provides ten multi-session dialogues with `1{,}986`
questions across five categories, serving as an aggregate quality indicator that mixes
hardness dimensions within a single benchmark.

### MemoryAgentBench (MAB).

MAB factors long-context memory into four capabilities:

- •

  Accurate Retrieval (AR), measured on the LongMemEval-S∗
  split [[16](https://arxiv.org/html/2608.15008v2#bib.bib2), [32](https://arxiv.org/html/2608.15008v2#bib.bib28)], requires the substrate to locate relevant
  information within a massive history. MAB builds this split by concatenating the
  LongMemEval chat history into five long dialogues of about `355`K tokens each and asks
  `300` questions over them; the asterisk is MAB’s label for this reformulated split.
- •

  Long-Range Understanding (LRU) tests whether the substrate preserves signal
  as content grows.
- •

  Test-Time Learning (TTL) requires the agent to classify newly acquired
  patterns, implicitly demanding that stored knowledge be inspectable, a capability that
  parametric substrates fundamentally lack.
- •

  Conflict Resolution (CR) presents contradictory facts at different time
  points and tests whether the substrate surfaces the most recent version. We additionally
  use CR as our scalability probe by sweeping content length.

### ALFWorld.

The benchmark provides `134` valid-unseen embodied-planning tasks
under a binary environment reward. We report a cross-episode regime in which every method
receives the same offline bank consisting of `100` AgentGym successes [[95](https://arxiv.org/html/2608.15008v2#bib.bib79)]
combined with `100` Qwen3-32B-AWQ real failures (stressing recovery, as the agent must
bootstrap from a pre-built memory).

### BigCodeBench-Hard.

The benchmark provides `148` code tasks graded under real
pytest execution. Each method is populated once from an offline pool of cross-task
solutions and harvested failures, with Hard-set overlap removed before any run. Retrieved
entries are rendered as labelled Successful and Failed blocks prepended to
the official instruction prefix. BCB-Hard stresses both accumulation (encoding a diverse
solution pool without drowning retrieval signal) and staleness (distinguishing current
successes from outdated failures).

### C.2 Bank–Test Semantic Alignment for ALFWorld and BCB-Hard

A retrieval-memory benchmark is meaningful only if its offline bank is *semantically
related* to its evaluation pool. If the two come from disjoint distributions, every
substrate is reduced to retrieving unrelated text and the rankings degenerate to base-model
noise. We verify here that the offline banks we use for ALFWorld and BCB-Hard both carry
strong, statistically distinguishable semantic alignment with their evaluation pools.

We embed every goal/instruction with text-embedding-3-small (`1536`-D,
`\ell_{2}`-normalized) and report the nearest-neighbor cosine similarity from each test item
to the corresponding bank. As a null baseline we replace the bank with i.i.d. Gaussian
unit-norm vectors and recompute nearest cosines; this is the similarity that random
retrieval would surface.

### ALFWorld.

The bank holds `200` trajectories (`100` AgentGym successes [[95](https://arxiv.org/html/2608.15008v2#bib.bib79)] `+` `100`
Qwen3-32B-AWQ real failures, balanced across the six task types). The evaluation pool is
the canonical `n{=}134` valid_unseen split. Nearest-bank cosine for the test goals:

- •

  mean `=\mathbf{0.879}`, median `=0.881`, min `=0.568`;
- •

  top-`5` mean cosine `=0.761` (the test goal is close to a *neighbourhood* of
  bank items, not a single outlier);
- •

  distribution: `30.6\%` in `[0.95,1.00]`, `35.8\%` in `[0.85,0.95)`, `22.4\%` in
  `[0.75,0.85)`, `6.0\%` in `[0.65,0.75)`, `5.2\%` in `[0.00,0.65)`.
- •

  Random-bank control: mean `=0.068`, an order of magnitude below the
  real bank.

Every test goal therefore has a structurally analogous example in the bank, typically the
same task type with a different target object/receptacle. The bank excludes the
valid_unseen environment instances themselves, so the alignment is
template-level rather than instance-level. Substrates can borrow *strategy*
(e.g. “go to drawer, open it, take key, go to desk”), not the answer.

### BigCodeBench-Hard.

The cross-task BCB pool (cross-task solution snippets harvested from non-Hard tasks plus
failures collected during preliminary runs) provides retrieval items for `n{=}148` Hard
instructions. The Hard-set overlap is removed before any run
(Appendix [C.1](https://arxiv.org/html/2608.15008v2#A3.SS1 "C.1 Benchmark Setups and Capability Definitions ‣ Appendix C Benchmark Setups and Bank Alignment ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")).
Nearest-bank cosine on the Hard split:

- •

  mean `=\mathbf{0.594}`, median `=0.586`, min `=0.303`;
- •

  top-`5` mean cosine `=0.526`;
- •

  `25\%` of Hard tasks have a bank example with cos `\geq 0.65` (concrete reusable
  scaffolding such as “download files via FTP and parse” `\to` “connect to S3 and
  parse”), `40\%` in `[0.55,0.65)` (shared library or pattern, e.g. requests/json/pandas idioms), and `35\%` below `0.55`
  (genuinely out-of-pool).
- •

  Random-bank control: mean `=0.061`, again an order of magnitude below
  the real bank.

BCB-Hard’s lower mean cosine vs. ALFWorld is expected, because code instructions span a much
larger surface area (different libraries, data sources, signatures) than the templated
goals of ALFWorld, so a diverse cross-task pool can match each Hard task at most along an
abstract dimension (library family, control-flow pattern). Crucially the alignment is still
ten-times the random null and concentrated in the `[0.55,0.85]` regime that semantic
encoders typically reserve for “same topic, different surface form”.

### Summary.

Both banks pass the basic sanity check that a memory benchmark requires. The retrieval
target distribution overlaps the evaluation distribution well above chance, so substrate
differences in Tab. [2](https://arxiv.org/html/2608.15008v2#S4.T2 "Table 2 ‣ 4.1 User-centric Benchmark ‣ 4 Results ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") reflect their use of *available* signal
rather than their luck against an unrelated bank. ALFWorld provides high-density
alignment (`0.88` mean cosine, `30\%` near-duplicate templates), exposing pure
strategy-transfer ability; BCB-Hard provides moderate, broadly distributed
alignment (`0.59` mean cosine), stressing diverse-pool encoding and cross-task
generalisation. The two benchmarks therefore probe complementary memory regimes within the
same evaluation framework.

### C.3 Coverage of the Memory Lifecycle

The memory of a long-running agent passes through more operations than retrieval. Content
is written while the agent works, stored facts are updated or superseded, contradictions
are resolved, long inputs are consolidated, and some content is eventually forgotten or
deleted [[92](https://arxiv.org/html/2608.15008v2#bib.bib88), [17](https://arxiv.org/html/2608.15008v2#bib.bib11)]. The four benchmarks of
Section [3](https://arxiv.org/html/2608.15008v2#S3 "3 Experiment Design ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") exercise only part of this lifecycle, and the parts they exercise
differ from one benchmark to the next. This subsection states, for each benchmark, which
demands it places on the substrate and which it does not.

### Lifecycle demands.

Table [8](https://arxiv.org/html/2608.15008v2#A3.T8 "Table 8 ‣ Lifecycle demands. ‣ C.3 Coverage of the Memory Lifecycle ‣ Appendix C Benchmark Setups and Bank Alignment ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") rates each benchmark on eight demands. *Incremental
writing* (Incr. write) asks whether memory is written while the task is being performed,
with reads interleaved between writes. *Update* asks whether a stored fact is later
replaced by a newer value that the agent must use. *Conflict* asks whether the store
holds contradictory statements that the agent must resolve. *Consolidate* asks whether
the answer requires integrating content spread over a long input rather than locating a few
items. *Temporal* asks whether the task requires reasoning over times, dates, or
order. *Cross-session* asks whether the current query or decision depends on content
from an earlier session or episode. *Past failures* asks whether memory holds failed
attempts that the agent must learn from or avoid. *Forget* asks whether the benchmark
rewards removing or suppressing stored content. A filled mark denotes a demand the
benchmark was built to test, a half mark denotes a demand that is present but incidental or
only partly tested, and an empty mark denotes a demand the benchmark does not place. Where
a benchmark’s original protocol and our harness differ, the mark follows the harness as
run.

Table 8: Memory-lifecycle demands exercised by each benchmark as run in the harness.
 primary demand,
 partial or indirect,
 not exercised.

|  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Benchmark | Incr.  write | Update | Conflict | Consolidate | Temporal | Cross-  session | Past  failures | Forget |
| User-centric | | | | | | | | |
| LoCoMo |  |  |  |  |  |  |  |  |
| LME-S (MAB AR) |  |  |  |  |  |  |  |  |
| MAB LRU |  |  |  |  |  |  |  |  |
| MAB TTL |  |  |  |  |  |  |  |  |
| MAB CR |  |  |  |  |  |  |  |  |
| Agent-centric | | | | | | | | |
| ALFWorld |  |  |  |  |  |  |  |  |
| BCB-Hard |  |  |  |  |  |  |  |  |

### User-centric benchmarks.

In the harness every conversation or stream is written in full before its questions are
asked (write phase, then read phase, Appendix [D](https://arxiv.org/html/2608.15008v2#A4 "Appendix D Metrics Definition and Assessment ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")), and MemoryAgentBench
specifies the same protocol, in which chunks are absorbed one by one and the questions
follow the last chunk [[32](https://arxiv.org/html/2608.15008v2#bib.bib28)]. Writing is therefore incremental in arrival
order, but no read is interleaved with the writes, which is why all five user-centric rows
carry a half mark for incremental writing.

LoCoMo [[15](https://arxiv.org/html/2608.15008v2#bib.bib9)] asks `1{,}986` questions over ten multi-session
dialogues in five categories, namely single-hop, multi-hop, temporal reasoning,
open-domain knowledge, and adversarial. The temporal category tests temporal reasoning
directly, multi-hop questions synthesize evidence from several sessions, and single-hop
questions target one session within a dialogue of up to 35 sessions, so temporal reasoning
and cross-session dependence are primary. Consolidation is partial because multi-hop
synthesis spans a few turns and LoCoMo’s event-summarization task is not part of the
suite. No category targets a changed fact or a contradiction, the adversarial category
tests abstention on unanswerable questions, and nothing rewards forgetting.

LME-S inherits LongMemEval’s question types [[16](https://arxiv.org/html/2608.15008v2#bib.bib2)], namely information
extraction, multi-session reasoning, knowledge updates, temporal reasoning, and abstention,
and the judge rubric dispatches on these labels (Appendix [D](https://arxiv.org/html/2608.15008v2#A4 "Appendix D Metrics Definition and Assessment ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")).
Temporal-reasoning questions make temporal reasoning primary, and multi-session reasoning
questions, which draw on several sessions of one history, make cross-session dependence
primary. Knowledge-update questions ask for the current value of a fact that changed across
sessions, so update is primary, and because the older and newer statements conflict,
contradiction handling is exercised indirectly. Multi-session reasoning questions aggregate
or compare facts across sessions, which exercises consolidation partially within histories
of roughly `355`K tokens.

The remaining three MAB capabilities are built from long inputs split into chunks of a
single stream, so their cross-session dependence is across chunks rather than across
separately delimited sessions, and we mark it partial. LRU is defined as integrating
information distributed across the entire sequence [[32](https://arxiv.org/html/2608.15008v2#bib.bib28)], which is
consolidation in the strict sense. TTL requires classifying new inputs from labeled
examples spread over the stream, so consolidation is partial, and because the examples are
correct labels rather than the agent’s own errors, learning from failures is not exercised.
CR presents a fact and a later rewritten version that contradicts it and asks for the
newest version, so update and contradiction handling are primary. Recency is signaled by a
serial-number cue rather than by dates (Appendix [F](https://arxiv.org/html/2608.15008v2#A6 "Appendix F Full Tables ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")), which we count as
partial temporal reasoning. MemoryAgentBench frames this capability as revising or
overwriting stored information in the face of contradictory
evidence [[32](https://arxiv.org/html/2608.15008v2#bib.bib28)], and a substrate can satisfy it without removing
anything, so forgetting is exercised only indirectly. The scalability probe sweeps CR
content from 6K to 262K tokens (Section [5.3](https://arxiv.org/html/2608.15008v2#S5.SS3 "5.3 Scalability Under Growing Input Context ‣ 5 Discussion ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")), which raises the cost of
locating the newest fact but does not turn the task into consolidation.

### Agent-centric benchmarks.

In the cross-episode ALFWorld regime [[33](https://arxiv.org/html/2608.15008v2#bib.bib31)], every
substrate starts from the same offline bank of `100` AgentGym successes [[95](https://arxiv.org/html/2608.15008v2#bib.bib79)]
and `100` Qwen3-32B-AWQ failures, so the current episode depends on earlier episodes and half of
the bank records failures, which makes cross-session dependence and learning from failures
primary.
Trajectories completed during the run accumulate in memory (Appendix [F](https://arxiv.org/html/2608.15008v2#A6 "Appendix F Full Tables ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")),
but the bank is in place before the first episode and recovery from it is what the regime
tests, so we mark incremental writing partial. Consolidation is partial because the bank
must be encoded before use, and refinement substrates compress it into strategies or skill
bundles while flat substrates store it raw (Appendix [B](https://arxiv.org/html/2608.15008v2#A2 "Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")).

BCB-Hard [[34](https://arxiv.org/html/2608.15008v2#bib.bib32)] populates memory once from an offline pool of cross-task
solutions and harvested failures before any run, so incremental writing is not exercised.
Consolidation is partial because the pool must be encoded before use, as in the
cross-episode ALFWorld regime. Retrieved entries are rendered as labeled Successful and Failed blocks
(Appendix [C](https://arxiv.org/html/2608.15008v2#A3 "Appendix C Benchmark Setups and Bank Alignment ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")), which makes learning from failures primary. We read the
staleness demand stated there, distinguishing current successes from outdated failures, as
a partial form of update, since no stored entry is ever rewritten. The `148` tasks are
independent single-turn problems and the pool comes from other tasks, so cross-session
dependence is partial. In both agent-centric benchmarks the bank that the regime tests is
built from other runs. On cross-episode ALFWorld the agent’s own completed trajectories join
the store as the run proceeds, but no task is built to depend on them.

### What the suite does not exercise.

Four parts of the lifecycle lie outside the suite. The first is deliberate forgetting or
deletion. No benchmark asks the agent to forget or delete on instruction, and the update
and conflict items only require that superseded facts not surface at read time, which is
why the Forget column holds no filled mark. The second is revision of memory over an
evolving long-running project. The update items in LME-S and MAB CR replace single facts
inside a fixed history, whereas a project rewrites earlier entries as its goals and
artifacts change. The third is self-correction of stored memory across many sessions, in
which the agent detects and repairs its own earlier errors. None of the benchmarks scores
such repairs. The fourth is agentic work built so that later sessions depend on memory the
agent itself wrote in earlier sessions. No benchmark in the main suite is built this way, and the supplementary MemoryArena evaluation of Appendix [E.5](https://arxiv.org/html/2608.15008v2#A5.SS5 "E.5 Supplementary Evaluation on MemoryArena ‣ Appendix E Additional Analyses ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") covers such tasks on one backbone and two domains. The
cross-session dependence of the agent-centric rows comes from banks built by other runs, the
trajectories that accumulate during the cross-episode ALFWorld run enter memory incidentally
rather than by benchmark design, and the dependence of the user-centric rows comes from
dialogue histories written before any question is asked.

## Appendix D Metrics Definition and Assessment

This appendix expands Table [9](https://arxiv.org/html/2608.15008v2#A4.T9 "Table 9 ‣ Appendix D Metrics Definition and Assessment ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") with full mathematical
definitions, evaluation protocols, and applicability notes for every
metric we report. We organize the discussion by the two families
introduced in the main text: *Performance* (§[D.2](https://arxiv.org/html/2608.15008v2#A4.SS2 "D.2 Performance metrics ‣ Appendix D Metrics Definition and Assessment ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")) and
*Efficiency* (§[D.3](https://arxiv.org/html/2608.15008v2#A4.SS3 "D.3 Efficiency metrics ‣ Appendix D Metrics Definition and Assessment ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")). Where a metric is benchmark-specific, we
state the reporting convention used by that benchmark; where a metric is
substrate-level (All in the table), we describe how we compute
it uniformly across the four benchmarks. Within the performance family, the compression ratio P5 and the MAB capability scores (LRU, TTL, and CR) form the memory-quality group, which we compute by one rule for every method (P5 is undefined for M9 to M11, which keep no textual store).

Table 9: Metric taxonomy for evaluating memory substrates. Two families:
Performance (P1–P6, P8–P12) captures answer accuracy and retrieval quality;
Efficiency (E1–E15) captures latency, storage, LLM call costs, and aggregate
totals. The Benchmark column records which benchmarks officially report each
metric. Abbreviations: LC = LoCoMo, MA = MemoryAgentBench,
ALF = ALFWorld, BC = BigCodeBench-Hard; All denotes
substrate-level metrics applicable across all four. Arrows indicate the preferred
direction.

|  |  |  |  |
| --- | --- | --- | --- |
| ID | Metric | Definition | Benchmark |
| Performance: answer accuracy and retrieval quality | | | |
| P1 `\uparrow` | Exact Match | `\mathbf{1}[\mathtt{norm}(\hat{y})=\mathtt{norm}(y)]`; lowercase, strip articles, punctuation, whitespace | LC |
| P2 `\uparrow` | Token F1 | Harmonic mean of token level precision and recall between `\mathtt{norm}(\hat{y})` and `\mathtt{norm}(y)` | LC |
| P3 `\uparrow` | BLEU 1 | Clipped unigram precision with brevity penalty: `\mathrm{BP}\cdot\sum_{w}\min(c_{w}^{\hat{y}},c_{w}^{y})/|\hat{y}|` | LC |
| P4 `\uparrow` | LLM Judge | LLM labels the answer CORRECT/WRONG given `(q,y,\hat{y})`; fraction correct in `[0,1]` | LC, MA |
| P5 | Compression Ratio | `|\text{input tokens}|/|\text{stored tokens}|`; larger values indicate more lossy compression (unsigned) | All |
| P6 `\uparrow` | Recall@`k` | `|\mathcal{G}\cap\mathcal{R}|/|\mathcal{G}|`; coverage of gold evidence dia_ids | LC |
| P8 `\uparrow` | Task Success | Fraction of episodes where all goal conditions are satisfied (binary per episode); ALFWorld primary metric | ALF |
| P9 `\uparrow` | GC Success | Fraction of individual sub goal conditions satisfied (ALFRED inherited) | ALF |
| P10 `\downarrow` | Steps to Goal | Environment actions per successful episode; auxiliary efficiency signal, not officially reported by ALFWorld | ALF |
| P11 `\uparrow` | Pass@1 | Unit test pass rate under greedy decoding; BigCodeBench primary metric | BC |
| P12 `\uparrow` | SubEM | `\mathbf{1}[\mathtt{norm}(y)\subseteq\mathtt{norm}(\hat{y})]`; substring exact match. MA primary metric for Accurate Retrieval and Conflict Resolution | MA |
| Efficiency: latency, storage, LLM call costs, and aggregate totals | | | |
| E1 `\downarrow` | Memory Size | Memory unit’s data structures in bytes; for parametric methods (M9), includes edited weights or adapter size | All |
| E2 `\downarrow` | Inference Time | Total per query wall time: read() `+` generate(); mean, p50, p90 (ms) | All |
| E3 `\downarrow` | Write Latency | Per message write() wall time; mean, p50, p90 (ms) | All |
| E4 `\downarrow` | Retrieval Latency | Per query read() wall time; mean, p50, p90 (ms) | All |
| E5 `\downarrow` | Write Tokens | LLM tokens consumed during the write phase (input `+` output) | All |
| E6 `\downarrow` | Write Calls | Number of LLM calls during the write phase | All |
| E7 | Retrieved Tokens | Tokens surfaced by memory to support answer generation | All |
| E8 `\downarrow` | Read Tokens | LLM tokens consumed during read phase calls (input `+` output) | All |
| E9 `\downarrow` | Read Calls | Number of LLM calls during the read phase | All |
| E10 `\downarrow` | Mgmt. Tokens | LLM tokens for memory management (dedup, update, delete, conflict resolution) | All |
| E11 `\downarrow` | Mgmt. Calls | Number of LLM calls for memory management | All |
| E12 `\downarrow` | Total Tokens | Aggregate auxiliary-LLM tokens across phases: `E_{5}+E_{8}+E_{10}` (excludes retrieved tokens `E_{7}`) | All |
| E13 `\downarrow` | Total Calls | Aggregate LLM calls across phases: `E_{6}+E_{9}+E_{11}` | All |
| E14 `\downarrow` | Total Wall-clock | End-to-end run time across the benchmark (s); includes write, read, and management phases | All |
| E15 `\downarrow` | Per-query Latency | `E_{14}/n_{q}`, the principal cost reported in the main tables (s/query) | All |

  

### D.1 Notation

Throughout we let `q` denote a query, `y` the gold answer, and `\hat{y}`
the predicted answer. For retrieval based substrates, we write
`\mathcal{R}=\{r_{1},\ldots,r_{k}\}` for the set of items returned by
read`(q)` at retrieval depth `k`, and `\mathcal{G}` for the set
of gold evidence identifiers (in LoCoMo, dialogue dia_ids). The text
normalisation operator
`\mathtt{norm}(\cdot)` lowercases the input, strips a fixed list of
articles (`\{`a, an, the`\}`), removes punctuation, and
collapses whitespace; this is the SQuAD style normaliser shared by
LoCoMo and MemoryAgentBench.

A *conversation* (LoCoMo) or *stream* (MemoryAgentBench)
generates a sequence of write calls followed by a batch of
read calls. We refer to the union of write calls as
the *write phase* and to the per query read`\to`generate
loop as the *read phase*. Substrates that perform asynchronous
maintenance (for example, A Mem evolution or MemSkill clustering)
accumulate this work in a third *management phase*, whose LLM
tokens and calls enter E10 and E11 and whose wall-clock enters E14. The
adapter training steps of M9 are booked in the same phase. They issue
no LLM call, so they contribute to E14 and E15 only.

### D.2 Performance metrics

### P1: Exact Match.

`\textrm{EM}(\hat{y},y)=\mathbf{1}[\mathtt{norm}(\hat{y})=\mathtt{norm}(y)]`.
We average over all queries in the benchmark and report a single scalar
in `[0,1]`. EM is the classical short answer metric; it is brittle to
paraphrase and therefore complementary to P2, P3, and P4.

### P2: Token F1.

Let `T(\cdot)` tokenise on whitespace after `\mathtt{norm}`. With
`P=|T(\hat{y})\cap T(y)|/|T(\hat{y})|` and
`R=|T(\hat{y})\cap T(y)|/|T(y)|`, F1`=2PR/(P+R)`. We use multiset
intersection so that repeated tokens contribute proportionally. Empty
`T(\hat{y})` contributes F1`=0`.

### P3: BLEU 1.

`\textrm{BLEU}\,1=\mathrm{BP}\cdot\sum_{w\in T(\hat{y})}\min(c_{w}^{\hat{y}},c_{w}^{y})/|T(\hat{y})|`, where `c_{w}^{x}` counts
occurrences of `w` in `x` and the brevity penalty is
`\mathrm{BP}=\min(1,\exp(1-|T(y)|/|T(\hat{y})|))`. P3 differs from P2
in two ways: it ignores recall, and it applies BP to discourage
truncated answers.

### P4: LLM Judge.

A judge model `J` receives the query `q`, the gold answer `y`, and
the model’s answer `\hat{y}` and labels the answer as CORRECT or
WRONG. P4 reports the fraction of CORRECT labels across the
evaluation set. We use gpt-4o-mini at temperature `0` with
deterministic templates that vary only by benchmark family: LoCoMo
and MemoryAgentBench use the binary rubric introduced by Mem0
[[30](https://arxiv.org/html/2608.15008v2#bib.bib13)]; LongMemEval uses the original authors’ per-question-type
rubric, which dispatches to one of four variants (standard,
temporal-reasoning, knowledge-update,
abstention) based on the question’s type label
[[16](https://arxiv.org/html/2608.15008v2#bib.bib2)]. The full templates are reproduced verbatim
in the released code repository. The judge sees only `(q,y,\hat{y})`, not the retrieved evidence or memory trace, so P4 measures answer
correctness, not retrieval grounding.

### P5: Compression Ratio.

`\textrm{P5}=N_{\text{input}}/N_{\text{stored}}`, where
`N_{\text{input}}` is the total tokens passed to write across
the whole benchmark and `N_{\text{stored}}` is the total tokens
materialised in the substrate’s persistent store after writes
complete. Larger P5 means the substrate discards more raw text in
favour of summaries or compressed structures. P5`=1` means lossless
caching; P5`<1` means the substrate *expands* the raw stream
(for example, when notes, graph records, or summary nodes are stored
alongside the raw entries, as for M4, M5, and M6 on LoCoMo). P5 is
unsigned: which direction is
“better” depends on the downstream use, hence no arrow in the table.

### P6: Recall@`k`.

`\textrm{Recall@}k=|\mathcal{G}\cap\mathcal{R}|/|\mathcal{G}|`. For
LoCoMo we resolve `\mathcal{R}` to gold dia_ids by finding,
for each retrieved chunk, the smallest dialogue message span that
covers it. P6 is reported for LoCoMo only. Queries with
`|\mathcal{G}|=0` (for example, adversarial or unanswerable items) are
excluded.

### P8: ALFWorld Task Success.

Per ALFWorld convention, an episode is successful iff every goal
condition specified by the PDDL goal predicate is satisfied at the
final step or earlier. P8 is the unweighted mean over the 134-episode
valid_unseen test split. We follow the official evaluator
(alfworld.agents.environment.AlfredTWEnv) and use a
max_steps=50 cap.

### P9: ALFWorld GC Success.

For each episode, GC Success is the fraction of individual sub goal
predicates achieved (numerator), divided by the total predicates
(denominator). The episode level GC contribution can therefore be
non zero even when P8 is zero. We report the macro average over
episodes, matching ALFRED’s reporting convention.

### P10: Steps to Goal.

For each successful episode (P8`=1`), we record the number of
environment steps; P10 is the mean over successes, with the count of
successes reported alongside for context. Failed episodes are
*excluded*, not penalised, so P10 is a conditional efficiency
measure and should not be compared across substrates with very
different P8. The Steps column of Table [22](https://arxiv.org/html/2608.15008v2#A6.T22 "Table 22 ‣ Backbone dependence and internal-memory families. ‣ F.3 Full Tables for ALFWorld ‣ Appendix F Full Tables ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")
is a different quantity, the mean number of environment steps per
episode over all 134 episodes, successes and failures alike.

### P11: BigCodeBench Pass@1.

We sample one greedy completion (`T=0`) per problem and execute it
against the per problem unit test suite inside the official
bigcodebench.eval sandbox. P11 is the fraction of problems
that pass all tests. We use the instruct variant of
BigCodeBench Hard and the calibrated=False evaluator so that
imports are the substrate’s responsibility.

### `P_{\mathrm{avg}}`: Partial success.

Tables [2](https://arxiv.org/html/2608.15008v2#S4.T2 "Table 2 ‣ 4.1 User-centric Benchmark ‣ 4 Results ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") and [22](https://arxiv.org/html/2608.15008v2#A6.T22 "Table 22 ‣ Backbone dependence and internal-memory families. ‣ F.3 Full Tables for ALFWorld ‣ Appendix F Full Tables ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")
report `P_{\mathrm{avg}}`, the mean per-task partial-success score on
ALFWorld, next to the binary task success.

### P12: SubEM.

`\textrm{SubEM}(\hat{y},y)=\mathbf{1}[\mathtt{norm}(y)\subseteq\mathtt{norm}(\hat{y})]`, where `\subseteq` is contiguous substring
containment after normalisation. SubEM is MemoryAgentBench’s primary
metric for the Accurate Retrieval (AR) and Conflict Resolution (CR)
capabilities; it is more lenient than EM for tasks where the gold is a
short fact embedded in a longer free form answer.

### D.3 Efficiency metrics

All wall-clock and latency measurements are taken on a single
configuration, vLLM serving on `4{\times}`H200 GPUs. Tokens are counted
with the substrate’s own tokenizer (for example, the Qwen3 BPE for
Qwen3 substrates, or cl100k_base for OpenAI API substrates).
Latencies are measured per event. The tables print the mean, and the
p90 where a column is marked p90; Table [2](https://arxiv.org/html/2608.15008v2#S4.T2 "Table 2 ‣ 4.1 User-centric Benchmark ‣ 4 Results ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")
prints the p90 of E2 on ALFWorld and the mean on BigCodeBench-Hard.

Online versus offline cost. The metrics keep online inference
apart from memory construction and training. E2 covers only the online
read`\to`generate path of a query, and E3 and E4
time the write and read calls separately. E14 and E15 include every
phase, so they also carry memory construction, index building, the
auxiliary-LLM calls of the write and management phases, the one-off
tree build that M6 defers to its first query, and the adapter training
steps of M9, which we book under the management phase for cost attribution
(Appendix [D.1](https://arxiv.org/html/2608.15008v2#A4.SS1 "D.1 Notation ‣ Appendix D Metrics Definition and Assessment ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")). Auxiliary-LLM calls go to the
gpt-4o-mini API, so they add wall-clock time without using
the local GPUs. Embedding tokens are excluded from E8.

### E1: Memory Size.

The disk or RAM resident bytes occupied by the substrate’s data
structures after the write phase has completed. For RAG style
substrates this is the size of the vector index plus any auxiliary
metadata; for graph substrates we add the on disk DB
(neo4j or kuzu) directory size. For parametric
substrates we report the trainable parameter footprint:
the LoRA adapter size for M9. E1 is comparable across families because all
substrates eventually have to store their state on disk to support
out of process evaluation.

### E2: Inference Time.

Per query read`(q)\to`generate wall time, end to end,
including any context assembly. We exclude the model load time
(amortised) and any benchmark side overhead.

### E3: Write Latency.

Per write call. For substrates that batch writes
(for example, ReadAgent’s gisting), we attribute the batch wall time
to the constituent calls in proportion to their input length so that
the distribution is well defined.

### E4: Retrieval Latency.

Per read call, excluding the downstream
generate call. For substrates with no retrieval
(full context, parametric), E4 is undefined and excluded from
aggregates.

### E5: Write Tokens.

Sum of input plus output tokens across all LLM calls issued during the
write phase. Embedding only substrates (M1, M2) have E5`=0`.

### E6: Write Calls.

Number of LLM completions issued during the write phase. We count
each chat completion request as one call regardless of streaming.

### E7: Retrieved Tokens.

The token count of the context block surfaced by read to the
generator. This is informational rather than directional (no arrow):
larger E7 buys more recall but inflates E8 downstream.

### E8: Read Tokens.

LLM tokens consumed during the read phase, summed across the generator
call and any reader side LLM calls (for example, ReadAgent’s lookup or
RAPTOR’s re ranking). Excludes embedding tokens.

### E9: Read Calls.

LLM call count for the read phase, by the same convention as E6.

### E10: Management Tokens.

LLM tokens consumed by maintenance work that is neither
write nor read attributable: A Mem evolution, MemSkill
re clustering, and similar. Substrates
without maintenance loops have E10`=0`.

### E11: Management Calls.

LLM call count for the management phase, by the same convention as E6.

### D.4 Aggregation and reporting conventions

Per query versus per conversation. P1 to P4, P6, and P12 are
per query metrics; we report the unweighted mean over all queries in
the benchmark. P8 to P11 are per episode or per problem; we report the
unweighted mean over episodes or problems. E2 to E4 latencies are
per event; the tables report the empirical mean, and the p90 of E2
where a column is marked p90.

Sub domain breakdowns. For LoCoMo the tables report the
aggregate over the five question types (single hop, multi hop,
temporal, open domain, adversarial). For MemoryAgentBench we report
each capability (AR, TTL, LRU, CR) separately because the capabilities
target different sub skills.

Cross substrate comparability. A small number of
metric`\times`substrate cells are undefined: P6 and E4 are
not defined for full context or parametric substrates (no retrieval
set); E5, E6, E10, and E11 are zero by construction for embedding only
substrates. We render undefined cells as “–” in the result tables
rather than imputing zeros, since a zero would bias direction aware
aggregates.

Statistical uncertainty. The main tables report point estimates
from single greedy runs. The sample sizes are
`n{=}1986` for LoCoMo, `n{=}300` for LME-S, `n{=}134` for ALFWorld, and
`n{=}148` for BCB-Hard, so one task is worth 0.75 TSR points on ALFWorld
and 0.68 Pass@1 points on BCB-Hard. Appendix [E.1](https://arxiv.org/html/2608.15008v2#A5.SS1 "E.1 Statistical Significance ‣ Appendix E Additional Analyses ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")
reports bootstrap confidence intervals and a paired exact McNemar test
for the ALFWorld comparison, the rerun stability of the scores, and the
reading resolution that these sample sizes give.

## Appendix E Additional Analyses

This appendix reports the statistical uncertainty of the main tables, the judge-agreement
study, the routing and portfolio analyses, and a supplementary evaluation on MemoryArena.

### E.1 Statistical Significance

The main-text tables and the full tables of Appendix [F](https://arxiv.org/html/2608.15008v2#A6 "Appendix F Full Tables ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") report point
estimates from single greedy runs (Appendix [D](https://arxiv.org/html/2608.15008v2#A4 "Appendix D Metrics Definition and Assessment ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")). This subsection quantifies
the uncertainty behind the agent-centric comparison that the main text builds on, where the
per-task outcome is binary and the sample sizes are among the smallest in the study, and it
states how stable the point estimates are under rerunning.

### Method.

For each compared substrate we compute a 95% confidence interval for its task success rate by
bootstrapping over benchmark instances. We resample the 134 games with replacement,
recompute the task success rate on each resample, and report the resulting 95%
bootstrap interval. To compare two substrates we run an exact McNemar test on their
paired per-game outcomes. The test conditions on the games where the two substrates
disagree, which makes it the appropriate paired test for two binary scorers evaluated
on the same instances. We test the ALFWorld-unseen cell of
Table [2](https://arxiv.org/html/2608.15008v2#S4.T2 "Table 2 ‣ 4.1 User-centric Benchmark ‣ 4 Results ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") with Qwen3-32B-AWQ (`n{=}134` games), which carries the
table’s peak TSR.

Table 10: Bootstrap 95% confidence intervals and the exact McNemar test for the
ALFWorld-unseen cell of Table [2](https://arxiv.org/html/2608.15008v2#S4.T2 "Table 2 ‣ 4.1 User-centric Benchmark ‣ 4 Results ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"). Scores are percentages.

|  |  |  |  |
| --- | --- | --- | --- |
| Cell | Substrate | TSR [95% CI] | Exact McNemar `p` |
| ALFWorld-unseen | M7 | 32.1 [24.6, 40.3] | 0.016 (M7 vs. M2) |
| Qwen3-32B-AWQ, `n{=}134` | M2 | 21.6 [14.9, 29.1] |

### Results.

The comparison that the main text builds on is significant. On ALFWorld-unseen with
Qwen3-32B-AWQ, M7 reaches a TSR of 32.1 [24.6, 40.3] against 21.6 [14.9, 29.1] for M2, and the
exact McNemar test on the 134 paired outcomes gives `p{=}0.016`.

### Rerun stability.

With generation at temperature 0, reruns reproduce M2 and M10 bit for bit, and the
residual variation of the remaining substrates between reruns is at most 0.02 on the
`[0,1]` scale. The best and worst substrates in every column of
Table [1](https://arxiv.org/html/2608.15008v2#S4.T1 "Table 1 ‣ 4 Results ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") are separated by 0.1 or more, so that separation is not
decoding noise. Orderings among substrates whose scores lie within 0.02 of each other, such
as M1 and M2 on LME-S with Qwen3-8B (0.478 against 0.480), are within the rerun variation
and should not be read as rankings.

### Sample sizes.

Long-horizon agentic tasks are expensive to evaluate. Every ALFWorld game is a
multi-step episode under a 50-step cap and every BCB-Hard task executes a
unit-test suite, so evaluation sets with hundreds rather than thousands of instances are
the norm, and we use the full standard splits rather than subsamples. The 134-game
valid_unseen split of ALFWorld [[33](https://arxiv.org/html/2608.15008v2#bib.bib31)] is the evaluation
set used by ReAct [[96](https://arxiv.org/html/2608.15008v2#bib.bib90)], Reflexion [[97](https://arxiv.org/html/2608.15008v2#bib.bib91)], and
ElasticMem [[98](https://arxiv.org/html/2608.15008v2#bib.bib92)]. The 148-task BCB-Hard
subset [[34](https://arxiv.org/html/2608.15008v2#bib.bib32)] is the split used by
[Sharifloo et al. [99]](https://arxiv.org/html/2608.15008v2#bib.bib93), CodeBoost [[100](https://arxiv.org/html/2608.15008v2#bib.bib94)], and
DAJ [[101](https://arxiv.org/html/2608.15008v2#bib.bib95)]. At these sizes one task corresponds to 0.75 TSR points on
ALFWorld and 0.68 Pass@1 points on BCB-Hard, which is the resolution at which a single
agent-centric cell of Table [2](https://arxiv.org/html/2608.15008v2#S4.T2 "Table 2 ‣ 4.1 User-centric Benchmark ‣ 4 Results ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") can be read. Gaps of a few points
on either benchmark amount to a handful of tasks. The intervals in Table [10](https://arxiv.org/html/2608.15008v2#A5.T10 "Table 10 ‣ Method. ‣ E.1 Statistical Significance ‣ Appendix E Additional Analyses ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") extend roughly seven to eight points on
either side of the estimate. Of the ALFWorld pairs we report only M7 against M2. The
4.5-point gap between M7 and M1 (27.6) lies inside these interval widths, so we make no
claim that M7 beats M1. The sample sizes of the LoCoMo and LME-S
cells are listed in Appendix [D](https://arxiv.org/html/2608.15008v2#A4 "Appendix D Metrics Definition and Assessment ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"). The retrieval-depth sweep of
Section [5.2](https://arxiv.org/html/2608.15008v2#S5.SS2 "5.2 Retrieval Scaling Reverses Across Regimes ‣ 5 Discussion ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") and the content-length sweep of
Section [5.3](https://arxiv.org/html/2608.15008v2#S5.SS3 "5.3 Scalability Under Growing Input Context ‣ 5 Discussion ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") are likewise read from point estimates.

### E.2 LLM-Judge Agreement

`P_{4}`, the LLM-judge score of Table [1](https://arxiv.org/html/2608.15008v2#S4.T1 "Table 1 ‣ 4 Results ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"), is produced by
gpt-4o-mini under the templates described in Appendix [D](https://arxiv.org/html/2608.15008v2#A4 "Appendix D Metrics Definition and Assessment ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"). This
subsection measures how much of `P_{4}` depends on that particular judge.

### Protocol.

We draw 595 predictions from LoCoMo, LME-S, and MAB CR, balanced between the two
labels CORRECT and WRONG, and re-score every prediction with fresh calls to four
judges, namely gpt-4o-mini itself, gpt-4.1-mini, gpt-4.1-nano, and
gpt-5-nano. Each judge sees only the question, the gold answer, and the
prediction, never the retrieved evidence or the identity of the substrate that produced
the prediction. Agreement is measured against the production gpt-4o-mini
labels that enter Table [1](https://arxiv.org/html/2608.15008v2#S4.T1 "Table 1 ‣ 4 Results ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"). Because the first judge is the
production judge re-run with fresh calls rather than re-read from cached labels, its row
measures test-retest stability, and the other three rows measure agreement across model
generations.

Table [11](https://arxiv.org/html/2608.15008v2#A5.T11 "Table 11 ‣ Protocol. ‣ E.2 LLM-Judge Agreement ‣ Appendix E Additional Analyses ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") reports the per-judge agreement and Cohen’s `\kappa`.

Table 11: Agreement of four judges with the production gpt-4o-mini labels on
595 label-balanced predictions from LoCoMo, LME-S, and MAB CR.

|  |  |  |  |
| --- | --- | --- | --- |
| Judge | Family | Agreement | Cohen’s `\kappa` |
| gpt-4o-mini (fresh calls) | GPT-4o | 95.8% | 0.89 |
| gpt-4.1-mini | GPT-4.1 | 92.6% | 0.85 |
| gpt-4.1-nano | GPT-4.1 | 91.0% | 0.82 |
| gpt-5-nano | GPT-5 | 83.6% | 0.67 |

### Results.

The fresh gpt-4o-mini run agrees with its own production labels on 95.8% of
the items (Cohen’s `\kappa{=}0.89`), so the `P_{4}` score is stable under re-querying. The
two GPT-4.1 judges agree with the production labels on 92.6% and 91.0% of the items
(`\kappa{=}0.85` and `0.82`), and gpt-5-nano on 83.6% (`\kappa{=}0.67`).
Across all four judges, Fleiss’ `\kappa` is 0.73 and the judges are unanimous on 75%
of the items. By benchmark, the four-judge `\kappa` is 0.89 on LME-S, 0.76 on MAB CR,
and 0.68 on LoCoMo. Because the sample is label-balanced rather than drawn per
substrate, we did not recompute substrate rankings under the alternative judges.

### Reading the values.

On the scale of [Landis and Koch [102]](https://arxiv.org/html/2608.15008v2#bib.bib96), `\kappa` between 0.61
and 0.80 is substantial and `\kappa` above 0.80 is almost perfect, so the three
GPT-4-series judges fall in the almost-perfect band while gpt-5-nano and
the four-judge Fleiss’ `\kappa` fall in the substantial band. The values sit at or
above the agreement levels reported for LLM judges elsewhere. On MT-Bench, GPT-4 agrees
with human judges on 85% of the non-tie pairwise votes, where human judges agree with
one another on 81% [[103](https://arxiv.org/html/2608.15008v2#bib.bib97)]. Judging the Judges [[104](https://arxiv.org/html/2608.15008v2#bib.bib98)]
measures alignment with Scott’s `\pi` rather than Cohen’s `\kappa` and finds that only
the strongest judges (GPT-4 Turbo, Llama-3 70B, and Llama-3.1 70B) reach `\pi` of 0.87 to
0.88 against human annotators, who reach 0.96 among themselves. Those studies measure
judge-human agreement on other tasks, whereas ours measures judge-judge agreement on
our own predictions, so the comparison locates our values rather than certifying them.

### Evaluation coupling.

gpt-4o-mini is also the auxiliary LLM for memory writing and management in
every substrate that needs one (Section [3](https://arxiv.org/html/2608.15008v2#S3 "3 Experiment Design ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")), so the production judge and
the memory writer are the same model. The three other judges come from later model
generations and agree substantially with it, which limits how much of `P_{4}` can be
specific to that one judge, and the appendix tables report judge-free scores (`P_{1}`, `P_{2}`,
`P_{3}`, and `P_{12}`) next to `P_{4}`, while the agent-centric benchmarks are scored by environment
reward and unit-test execution without any judge. All four judges, however, come from a
single provider, so a human or cross-provider check of `P_{4}` remains outside this study.

### E.3 Substrate Routing

The regime-dependent reversals of Section [4](https://arxiv.org/html/2608.15008v2#S4 "4 Results ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") and
Section [5](https://arxiv.org/html/2608.15008v2#S5 "5 Discussion ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") make substrate selection a design axis in its own
right. This subsection asks whether the selection can be automated per query. By a
router we mean a dispatcher placed in front of a pool of candidate substrates.
When a query arrives, the router decides which substrate serves it, and that
substrate alone produces the answer. A router is therefore a selection policy and
not a new memory mechanism, and it is deployable only under two conditions. It may
read only what exists when the query arrives, namely the query itself and the
fitted policy, never the gold annotation and never which substrate turns out to be
right. It must also be judged against the alternative a practitioner would
otherwise choose, which is deploying the single best fixed substrate on the same
held-out queries. The quantity we report is accordingly the accuracy of the routed
system, not the accuracy of the routing decision.

### Setup.

All routers are evaluated on LoCoMo with Qwen3-8B, the setting of
Table [1](https://arxiv.org/html/2608.15008v2#S4.T1 "Table 1 ‣ 4 Results ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"), over its `1{,}986` questions, with the substrates
of that table as the candidate pool. We split the questions
into five folds, fit every router on the training folds, score it on the held-out
fold, and read the fixed baseline off the same fold, so router and baseline are
always compared on identical questions. Per-question correctness is the `P_{4}` judge
label of the paper runs (Appendix [D](https://arxiv.org/html/2608.15008v2#A4 "Appendix D Metrics Definition and Assessment ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")). We evaluate four routers.

- •

  Multi-class. One classifier over the whole substrate set,
  trained to predict which substrate answers a given question correctly. We run
  it twice, once over TF-IDF features and once over dense query embeddings.
- •

  Nearest neighbors. No fitted model. The query is embedded, its
  25 most similar training questions are retrieved, and the query is sent to the
  substrate that answered those neighbors best.
- •

  Per-substrate outcome. One binary classifier per substrate, each
  trained to predict whether that substrate will answer the question correctly.
  At inference the query goes to the substrate with the highest predicted
  probability. Supervision is dense, since every substrate contributes a label on
  every training question, and no tie between two correct substrates has to be
  broken.
- •

  Predicted question type. A classifier predicts the LoCoMo
  question category from the query and routes to the substrate that wins that
  category on the training folds.

Two reference rows replace the predicted category with the gold category, and
the whole policy with a per-instance oracle that picks a correct substrate
whenever one exists. Neither is observable at inference.
Table [12](https://arxiv.org/html/2608.15008v2#A5.T12 "Table 12 ‣ Setup. ‣ E.3 Substrate Routing ‣ Appendix E Additional Analyses ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") reports the held-out accuracy of every router next to the
best fixed substrate.

Table 12: Query-level routing on LoCoMo with Qwen3-8B (`1{,}986` questions, five
folds). Held-out `P_{4}` of the routed system and its difference from the best fixed substrate.

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| Router | Prediction target | Features | Held-out `P_{4}` | vs. best fixed |
| Best fixed substrate (M5) | none | none | 0.648 | — |
| Multi-class | winning substrate | TF-IDF | 0.591 | `-0.057` |
| Multi-class | winning substrate | embeddings | 0.588 | `-0.060` |
| Nearest neighbors (25) | none | embeddings | 0.650 | `+0.002` |
| Per-substrate outcome | correctness of each substrate | embeddings | 0.671 | `\mathbf{+0.023}` |
| Predicted question type | question category | embeddings | 0.613 | `-0.035` |
| Gold question type (reference) | given, not predicted | none | 0.689 | `+0.041` |
| Per-instance oracle (reference) | given, not predicted | none | 0.93 | `+0.28` |

### Results.

The per-substrate router is the only router that clears the fixed baseline by a
margin, 0.671 against 0.648, and it does so in all five folds. On paired
per-question outcomes it is correct where the fixed choice is wrong 223 times
against 179 the other way, which gives an exact McNemar `p{=}0.032` and a paired
bootstrap 95% interval on the difference of `[+0.003,+0.042]`. The
nearest-neighbor router matches the baseline (0.650) and the remaining routers
fall below it. The prediction target matters more than the features. Holding the
target fixed and swapping TF-IDF for embeddings moves the multi-class score from
0.591 to 0.588, while holding the features fixed and changing the target from
naming the winner to asking each substrate whether it will answer moves the score
from 0.588 to 0.671. The multi-class target keeps one substrate per question and
discards the outcomes of all others, and it forces an arbitrary choice whenever
several substrates answer correctly. The per-substrate target uses every outcome
and never breaks a tie. The multi-class result is therefore a negative result
about that target, not about query-level routing. The winning router needs only
the question embedding, one embedding call per query with no LLM call and no
annotation.

### Regime-level routing.

A deployed service knows whether it answers long-context questions or drives an
agent loop, so routing on the operating regime costs nothing to observe. Because the
per-regime winners differ in Tables [1](https://arxiv.org/html/2608.15008v2#S4.T1 "Table 1 ‣ 4 Results ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")
and [2](https://arxiv.org/html/2608.15008v2#S4.T2 "Table 2 ‣ 4.1 User-centric Benchmark ‣ 4 Results ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"), choosing one substrate per regime beats any single fixed
substrate on our benchmarks. The choice is read off the same results, so this is an
in-sample comparison rather than a held-out test.
Within LoCoMo, routing on the annotated question category reaches 0.689 against
0.648 (gold question type row of Table [12](https://arxiv.org/html/2608.15008v2#A5.T12 "Table 12 ‣ Setup. ‣ E.3 Substrate Routing ‣ Appendix E Additional Analyses ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")), but the annotation is
not available at inference, so this row bounds what a perfect type predictor
could deliver rather than describing a deployable router.

### Selection.

Everything is fitted inside the training folds. No hyperparameter is tuned on any
fold. The classifiers are logistic regression at library defaults, and the 25 neighbors
of the nearest-neighbor router were fixed before any result was seen.
Re-selecting the best fixed substrate inside each training fold picks the same
substrate (M5) in every fold and leaves the baseline unchanged to three decimals.

### Split protocol.

The folds above are a random partition of the `1{,}986` questions under a fixed
seed and are not grouped by conversation, so questions from the same conversation
can appear in both the training and the held-out folds. LoCoMo has ten
conversations (Section [3](https://arxiv.org/html/2608.15008v2#S3 "3 Experiment Design ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")). Table [13](https://arxiv.org/html/2608.15008v2#A5.T13 "Table 13 ‣ Split protocol. ‣ E.3 Substrate Routing ‣ Appendix E Additional Analyses ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") repeats
the comparison with conversation-grouped folds and with leave-one-conversation-out
splits, where the held-out questions always come from conversations the router
has never seen.

Table 13: Per-substrate router against the best fixed substrate (M5) under three split
protocols on LoCoMo with Qwen3-8B, with the exact McNemar `p` and the folds the router wins.

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| Protocol | Router | Best fixed | Difference | Test |
| Question-level, random folds (reported) | 0.671 | 0.648 | `+0.023` | `p{=}0.032`, 5 of 5 folds |
| Conversation-grouped, 5 folds | 0.661 | 0.648 | `+0.013` | `p{=}0.22`, 3 of 5 folds |
| Leave-one-conversation-out, 10 folds | 0.649 | 0.648 | `+0.001` | `p{=}0.96`, 5 of 10 folds |

The gain shrinks to `+0.013` under conversation-grouped folds and disappears under
leave-one-conversation-out, and neither difference is significant. The gain is
therefore specific to the question-level protocol, and we narrow the claim
accordingly. Routing helps a deployment that has accumulated outcomes over its own
traffic and routes new questions from the same conversations. We do not claim
transfer to conversations the router has never seen.

### Summary.

Four points follow. Regime-dependent reversals make substrate selection a real
design axis. Choosing a substrate per observable regime gains in-sample. A router that uses
only the question embedding beats the best fixed substrate under the
question-level protocol at low inference cost. Transfer to unseen conversations
and closing the gap to the per-instance oracle (0.93) remain open.

### E.4 Multi-Substrate Portfolios

Routing picks one substrate per query from a pool. A complementary question is
how large the pool has to be. We run a small portfolio of substrates side by side
and ask what an ideal per-query selector over that portfolio would achieve. A
portfolio covers an instance when at least one member solves it, so each coverage
value below is exactly the accuracy an ideal per-instance selector over that
portfolio would reach. Coverage is computed from the per-instance outcomes of the
paper runs, namely the per-query `P_{4}` judge labels on LoCoMo, LME-S, and MAB CR,
per-task success on ALFWorld, and per-task Pass@1 on BCB-Hard, with each
substrate’s run matched to its cell in Table [1](https://arxiv.org/html/2608.15008v2#S4.T1 "Table 1 ‣ 4 Results ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") or
Table [2](https://arxiv.org/html/2608.15008v2#S4.T2 "Table 2 ‣ 4.1 User-centric Benchmark ‣ 4 Results ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"). Portfolios are picked by greedy set cover,
which coincides with the exhaustive optimum at sizes two and three on every
benchmark. Table [14](https://arxiv.org/html/2608.15008v2#A5.T14 "Table 14 ‣ E.4 Multi-Substrate Portfolios ‣ Appendix E Additional Analyses ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") lists the best single substrate, the best
portfolios of size two and three, and the coverage of the full substrate pool.

Table 14: Coverage of substrate portfolios, equal to the accuracy of an ideal per-instance
selector over the portfolio. Units follow Tables [1](https://arxiv.org/html/2608.15008v2#S4.T1 "Table 1 ‣ 4 Results ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") and [2](https://arxiv.org/html/2608.15008v2#S4.T2 "Table 2 ‣ 4.1 User-centric Benchmark ‣ 4 Results ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").

|  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
| Benchmark (`n`) | Backbone | Best single | Size 2 | Size 3 | All substrates |
| LoCoMo (1986) | Qwen3-8B | M5 0.648 | {M10, M4} 0.746 | {M10, M4, M9} 0.825 | 0.93 |
| LME-S (300) | Qwen3-8B | M5 0.537 | {M5, M8} 0.660 | {M2, M5, M8} 0.700 | 0.743 |
| MAB CR (100) | Qwen3-8B | M5 0.440 | {M5, M6} 0.560 | {M5, M6, M1} 0.580 | 0.580 |
| ALFWorld (134) | Qwen3-8B | M11 11.9 | {M11, M4} 19.4 | {M11, M4, M8} 23.9 | 34.3 |
| BCB-Hard (148) | Gemma-4 | M5 20.9 | {M5, M8} 28.4 | {M4, M5, M8} 29.7 | 29.7 |

Small heterogeneous portfolios suffice everywhere. Two substrates add between
0.098 and 0.123 of coverage over the best single substrate on the three dialogue
benchmarks and 7.5 points on each agentic benchmark. Three substrates close the
whole gap between the best single substrate and the full pool on BCB-Hard and
MAB CR, 79% of it on LME-S, 63% on LoCoMo, and 54% on ALFWorld. The members
mix families. Every size-two portfolio pairs two different families, and four of
the five size-three portfolios span three families, so heterogeneity rather than
standalone strength drives the complementarity. M4, which is never the per-model
performance winner in Table [1](https://arxiv.org/html/2608.15008v2#S4.T1 "Table 1 ‣ 4 Results ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") or
Table [2](https://arxiv.org/html/2608.15008v2#S4.T2 "Table 2 ‣ 4.1 User-centric Benchmark ‣ 4 Results ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"), enters the LoCoMo, ALFWorld, and BCB-Hard
portfolios because it solves instances the leaders miss.

Coverage is an upper bound that assumes a perfect selector, and
Appendix [E.3](https://arxiv.org/html/2608.15008v2#A5.SS3 "E.3 Substrate Routing ‣ Appendix E Additional Analyses ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") measures how much of it a deployable router recovers.

### E.5 Supplementary Evaluation on MemoryArena

MemoryArena [[105](https://arxiv.org/html/2608.15008v2#bib.bib112)] builds agentic tasks from ordered subtasks that span
several sessions, so later subtasks depend on information gathered in earlier ones. This is one of the four parts of the memory lifecycle that our main benchmarks do not exercise (Appendix [C.3](https://arxiv.org/html/2608.15008v2#A3.SS3 "C.3 Coverage of the Memory Lifecycle ‣ Appendix C Benchmark Setups and Bank Alignment ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")). We run every substrate and the benchmark’s own BM25 memory
baseline on two of its domains, formal reasoning in mathematics (40 tasks) and group travel planning (270 tasks). The baseline is MemoryArena’s own BM25 memory, whereas M2 is our BM25 substrate behind the benchmark’s memory interface (Appendix [B](https://arxiv.org/html/2608.15008v2#A2 "Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")), so the two differ in how entries are written and retrieved. The task agent is Qwen3-8B at temperature 0, the benchmark
environments use GPT-4.1-mini with step limits of 10 and 30, and the auxiliary LLM and the
embedding encoder are those of the main experiments, so the substrate is the only change across runs apart from a larger completion budget for M9 on travel planning (`4{,}096` tokens against `1{,}024`). Memory is written session by session. On travel planning each substrate also keeps the first `4{,}000` characters of the opening observation of a task, because the shared trip specification appears only
there, and the injected memory is capped at `20{,}000` characters. We report the benchmark’s
metrics. The success rate (SR) counts tasks whose final subtask is solved, the progress score
(PS) is the fraction of subtasks solved, and the soft progress score (sPS) also credits
partially satisfied constraints. Following the benchmark, we use sPS for travel planning, where
PS is near zero for every method.

Table 15: Supplementary evaluation on MemoryArena with the Qwen3-8B agent. Formal
reasoning in mathematics reports SR and PS over 40 tasks, and group travel planning reports
sPS (%) over 270 tasks. BM25 is the benchmark’s own memory baseline. Bold marks the best value per column.

|  |  |  |  |
| --- | --- | --- | --- |
|  | Mathematics | | Travel planning |
| Substrate | SR | PS | sPS (%) |
| BM25 (benchmark baseline) | 0.150 | 0.175 | 3.82 |
| M1 Dense Vector | 0.075 | 0.092 | 3.99 |
| M2 Sparse Vector | 0.000 | 0.094 | 3.51 |
| M3 Gist Index | 0.050 | 0.124 | 3.56 |
| M4 Evolving Notes | 0.200 | 0.170 | 3.29 |
| M5 Dual-Level Graph | 0.075 | 0.157 | 2.58 |
| M6 Hierarchical Tree | 0.050 | 0.163 | 3.15 |
| M7 Distilled Strategies | 0.050 | 0.131 | 2.76 |
| M8 Skill Bundles | 0.050 | 0.156 | 3.12 |
| M9 Adapter Tuning | 0.100 | 0.162 | 3.69 |
| M10 Full Context | 0.225 | 0.176 | 3.45 |
| M11 Episode-Clustered Re-prefill | 0.075 | 0.151 | 2.93 |

All scores in Table [15](https://arxiv.org/html/2608.15008v2#A5.T15 "Table 15 ‣ E.5 Supplementary Evaluation on MemoryArena ‣ Appendix E Additional Analyses ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") are low. On mathematics the full-context M10 and the structural M4 solve the most
tasks, 9 and 8 of 40 against 6 for the BM25 baseline, while their progress scores (0.176 and
0.170) stay level with the baseline (0.175). One task moves SR by 0.025, so we read these
rankings as descriptive. On travel planning every method stays between 2.6% and 4.0% sPS, so
this domain does not separate the substrates for an agent of this size. Interdependent
multi-session tasks therefore remain hard for every substrate family at this scale.

## Appendix F Full Tables

### F.1 Full Tables for the LoCoMo Benchmark

### Substrate family vs. accuracy and cost.

The three
appendix tables sort the ten substrates into a clear ordering by
family. The Flat family (M1, M2) requires no auxiliary
LLM at any phase, stores the raw utterance set (`P_{5}{=}1.00`), and
lands at the cheap end of the curve, with M2 at 0.33 s/query and M1
at 0.77 s/query carrying the dense encoder advantage of `+0.09` `P_{4}`
on Qwen3-8B. The Text and Structural families (M3, M4, M5) all push
auxiliary LLM tokens into the pipeline, but where they spend that
budget matters more than how much. M3 concentrates LLM work in the
per-query page-select call (`E_{8}{=}8.2`M, one call per query) and
recovers M1-level `P_{4}` with a `5.3\times` store compression. M4 spends
mostly on note generation at write (`E_{5}{=}4.6`M) and on the
evolution loop at management (`E_{10}{=}3.2`M), giving one of the smallest
stores in the family (178K) at the cost of one of the lowest `P_{6}`
Recall@`k` values (0.465).
M5 is the most LLM-intensive substrate by a wide margin
(`E_{12}{=}51`M, `E_{15}{=}28` s/query on Qwen3-8B) yet posts the top
`P_{4}` of the Qwen3-8B band (0.648)
by raising the LLM-judge score, not retrieval recall. The
Hierarchical and Refinement families invert this trade-off. M6
pays modest write-time tree summarization (`E_{5}{=}382`K) and
zero read-phase LLM yet lands the highest `P_{6}` Recall@`k` in the table (0.797),
because the collapsed tree exposes nodes at every layer for the
embedding search. M8 sits between M6 and M5 in cost but
trails M6 by 4 to 5 `P_{4}` points because prefilling every skill bundle
dilutes the model’s attention over the one relevant to the query.

### Backbone dependence and internal-memory families.

The
relative ordering on `P_{4}` is mostly preserved across the three
backbones, and the leading substrate’s margin over the flat baselines
is robust to model size. M5’s `+0.09` `P_{4}` lead over M1 on Qwen3-8B holds
at `+0.10` on Qwen3-32B-AWQ and widens to `+0.15` on Gemma-4; M3’s parity with
M1 holds across all three; M2 trails M1 on every backbone. The
internal-memory families illustrate the limits of backbone-only
solutions. The Weight family (M9) collapses on LoCoMo
regardless of host (`P_{1}` EM `<` 0.025). Single-pass adapter tuning
over QA pairs is not enough for the recall-style questions LoCoMo
asks. The Activation family (M10, M11) shows the
sharpest backbone dependence in the table. M10 reaches the highest `P_{4}`
among the Activation family on Qwen3-32B-AWQ (0.669), just behind structural
M5 (0.683), by paying about `6\times` the per-query latency of M1. Its
gain over M1 narrows to `+0.03` on Qwen3-8B, where the smaller model
under-utilizes long contexts, and widens to `+0.11` on Gemma-4 at
`5.6\times` the latency of M1.
M11 is the only substrate that exhibits clear inverse scaling,
with `P_{4}` dropping from 0.307 on Qwen3-8B to 0.274 on Qwen3-32B-AWQ,
consistent with the episode clustering selecting a less relevant
episode on the larger backbone. We did not isolate the cause.
Together, these results suggest that the recall-heavy
structure of LoCoMo rewards retrieval substrates that pair a
faithful textual store (`P_{5}` near 1) with broad retrieval coverage,
and that auxiliary LLM cost translates into
accuracy only when the LLM work targets the actual retrieval
bottleneck rather than synthesis quality on top of it.

Table 16: LoCoMo performance metrics per substrate and backbone (`P_{1}` to `P_{4}`, `P_{6}`).

|  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Model | Sub. | Family | `P_{1}` EM | `P_{2}` F1 | `P_{3}` BLEU-1 | `P_{4}` Judge | `P_{6}` Recall@`k` |
| Qwen3-8B | M1 | Flat | 0.273 | 0.466 | 0.285 | 0.561 | 0.696 |
| M2 | Flat | 0.283 | 0.436 | 0.241 | 0.470 | 0.595 |
| M3 | Text | 0.190 | 0.366 | 0.269 | 0.562 | 0.620 |
| M4 | Struct | 0.226 | 0.435 | 0.216 | 0.545 | 0.465 |
| M5 | Struct | 0.196 | 0.381 | 0.252 | 0.648 | 0.455 |
| M6 | Hier | 0.251 | 0.436 | 0.276 | 0.556 | 0.797 |
| M8 | Refine | 0.301 | 0.456 | 0.252 | 0.509 | 0.615 |
| M9 | Weight | 0.019 | 0.099 | 0.071 | 0.379 | – |
| M10 | Act | 0.159 | 0.342 | 0.285 | 0.589 | – |
| M11 | Act | 0.066 | 0.161 | 0.138 | 0.307 | – |
| Qwen3-32B-AWQ | M1 | Flat | 0.208 | 0.408 | 0.328 | 0.582 | 0.696 |
| M2 | Flat | 0.187 | 0.352 | 0.272 | 0.487 | 0.595 |
| M3 | Text | 0.173 | 0.368 | 0.289 | 0.586 | 0.620 |
| M4 | Struct | 0.165 | 0.320 | 0.240 | 0.452 | 0.465 |
| M5 | Struct | 0.134 | 0.329 | 0.286 | 0.683 | 0.455 |
| M6 | Hier | 0.192 | 0.387 | 0.307 | 0.573 | 0.797 |
| M8 | Refine | 0.190 | 0.365 | 0.281 | 0.533 | 0.615 |
| M9 | Weight | 0.024 | 0.101 | 0.082 | 0.399 | – |
| M10 | Act | 0.190 | 0.412 | 0.337 | 0.669 | – |
| M11 | Act | 0.035 | 0.118 | 0.095 | 0.274 | – |
| Gemma-4-26B | M1 | Flat | 0.329 | 0.513 | 0.311 | 0.574 | 0.696 |
| M2 | Flat | 0.302 | 0.451 | 0.257 | 0.555 | 0.595 |
| M3 | Text | 0.303 | 0.484 | 0.300 | 0.599 | 0.620 |
| M4 | Struct | 0.310 | 0.405 | 0.232 | 0.476 | 0.465 |
| M5 | Struct | 0.203 | 0.451 | 0.271 | 0.719 | 0.455 |
| M6 | Hier | 0.310 | 0.483 | 0.292 | 0.592 | 0.797 |
| M8 | Refine | 0.335 | 0.482 | 0.241 | 0.554 | 0.615 |
| M10 | Act | 0.300 | 0.515 | 0.308 | 0.688 | – |
| M11 | Act | 0.085 | 0.181 | 0.149 | 0.330 | – |

Table 17: LoCoMo latency and compression per substrate and backbone (`E_{2}` to `E_{4}`, `E_{14}`, `E_{15}`, `P_{5}`).

|  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Model | Sub. | Family | `E_{2}` (ms/q) | `E_{3}` (ms/wr) | `E_{4}` (ms/rd) | `E_{14}` (s) | `E_{15}` (s/q) | `P_{5}` |
| Qwen3-8B | M1 | Flat | 522 | 199 | 226 | 1,534 | 0.77 | 1.00 |
| M2 | Flat | 302 | 0 | 1 | 660 | 0.33 | 1.00 |
| M3 | Text | 2,292 | 1,663 | 781 | 8,293 | 4.18 | 5.29 |
| M4 | Struct | 169 | 6,210 | 9 | 12,638 | 6.36 | 0.71 |
| M5 | Struct | 20,680 | 5,116 | 9,610 | 55,290 | 27.84 | 0.44 |
| M6 | Hier | 683 | 641 | 195 | 2,758 | 1.39 | 0.62 |
| M8 | Refine | 431 | 2,570 | 179 | 6,019 | 3.03 | 1.09 |
| M9 | Weight | 335 | 1,400 | – | 3,498 | 1.76 | – |
| M10 | Act | 4,132 | – | – | 9,027 | 4.55 | – |
| M11 | Act | 1,848 | – | – | 4,037 | 2.03 | – |
| Qwen3-32B-AWQ | M1 | Flat | 2,174 | 194 | 648 | 5,142 | 2.59 | 1.00 |
| M2 | Flat | 2,153 | 0 | 1 | 4,703 | 2.37 | 1.00 |
| M3 | Text | 4,379 | 1,623 | 1,100 | 12,852 | 6.47 | 5.19 |
| M4 | Struct | 2,289 | 6,358 | 12 | 17,269 | 8.70 | 0.72 |
| M5 | Struct | 21,949 | 5,221 | 9,586 | 58,025 | 29.22 | 0.43 |
| M6 | Hier | 2,650 | 653 | 610 | 10,327 | 5.20 | 0.60 |
| M8 | Refine | 2,707 | 2,600 | 166 | 10,991 | 5.53 | 1.11 |
| M9 | Weight | 860 | 3,800 | – | 9,386 | 4.73 | – |
| M10 | Act | 14,774 | – | – | 32,275 | 16.25 | – |
| M11 | Act | 3,790 | – | – | 8,280 | 4.17 | – |
| Gemma-4-26B | M1 | Flat | 667 | 200 | 188 | 1,850 | 0.93 | 1.00 |
| M2 | Flat | 445 | 0 | 1 | 972 | 0.49 | 1.00 |
| M3 | Text | 2,870 | 1,664 | 1,018 | 9,555 | 4.81 | 5.37 |
| M4 | Struct | 394 | 6,145 | 11 | 13,129 | 6.61 | 0.73 |
| M5 | Struct | 18,982 | 5,135 | 9,444 | 51,544 | 25.95 | 0.43 |
| M6 | Hier | 712 | 626 | 174 | 2,822 | 1.42 | 0.61 |
| M8 | Refine | 600 | 2,572 | 166 | 6,388 | 3.22 | 1.06 |
| M10 | Act | 4,698 | – | – | 10,263 | 5.17 | – |
| M11 | Act | 1,967 | – | – | 4,297 | 2.16 | – |

Table 18: LoCoMo storage, token, and call accounting per substrate (`E_{1}`, `E_{5}` to `E_{13}`).

|  |  |  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Sub. | Family | `E_{1}` | `E_{5}` | `E_{6}` | `E_{7}` | `E_{8}` | `E_{9}` | `E_{10}` | `E_{11}` | `E_{12}` | `E_{13}` |
| M1 | Flat | 3.59M | 0 | 0 | 889.8K | 0 | 0 | 0 | 0 | 0 | 0 |
| M2 | Flat | 173.7K | 0 | 0 | 806.6K | 0 | 0 | 0 | 0 | 0 | 0 |
| M3 | Text | 257.4K | 311.8K | 390 | 11.52M | 8.23M | 2,040 | 0 | 0 | 8.54M | 2,430 |
| M4 | Struct | 177.6K | 4.59M | 3,268 | 96.2K | 0 | 0 | 3.16M | 2,312 | 7.75M | 5,580 |
| M5 | Struct | 167.8K | 33.0M | 9,860 | 6.00M | 17.8M | 3,980 | 0 | 0 | 50.8M | 13,840 |
| M6 | Hier | 4.33M | 381.8K | 910 | 1.87M | 0 | 0 | 127.8K | 190 | 509.6K | 1,100 |
| M8 | Refine | 3.40M | 1.46M | 481 | 806.2K | 2.94M | 2,037 | 242.9K | 51 | 4.64M | 2,569 |
| M9 | Weight | host-dep | – | – | – | – | – | – | – | – | – |
| M10 | Act | 101.2K | – | – | 60.9M | – | – | – | – | – | – |
| M11 | Act | 100.7K | – | – | 15.3M | – | – | – | – | – | – |

### F.2 Full Tables for the LongMemEval-S and MAB Benchmarks

### Substrate family vs. accuracy and cost.

Table [19](https://arxiv.org/html/2608.15008v2#A6.T19 "Table 19 ‣ Token accounting and memory quality. ‣ F.2 Full Tables for the LongMemEval-S and MAB Benchmarks ‣ Appendix F Full Tables ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") reports the benchmark-native SubEM
(`P_{12}`), whereas Table [1](https://arxiv.org/html/2608.15008v2#S4.T1 "Table 1 ‣ 4 Results ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") reports the judge
score `P_{4}`. The TTL leader differs between the two metrics (M3 by
`P_{4}` on the two Qwen backbones, M8 by `P_{12}` on all three). The three
appendix tables sort the ten substrates evaluated on LongMemEval-S
(LME-S) and the three MAB sub-benchmarks, LRU (detective_qa,
long-range understanding), TTL (icl_banking77_5900shot_balance,
test-time learning), and CR (factconsolidation_sh_6k,
conflict resolution), into a clear ordering by family. The Flat
family (M1, M2) requires no auxiliary LLM at any phase,
stores the raw conversation slots (`P_{5}{=}1.00`), and lands at the
cheap end of every column. M2 finishes LME-S at 1.75 s/query on
Qwen3-8B and TTL in under a second per query on Qwen3-8B and
Gemma-4, while M1 carries the dense-encoder advantage of at
least `+0.05` `P_{12}` on LME-S, widening on the larger backbones. The
Text family (M3) flips the trade-off. Gist generation pays
`E_{5}{=}437`K tokens at write and another `5.0`M retrieved tokens at
read time, but on TTL banking77, where the answer is a single
class id and the gist matches almost surface-form, it climbs to
a high TTL score on Qwen3-8B (`P_{12}{=}0.840`, still below M8’s 0.960)
and stays there across stronger backbones (0.860 / 0.798). The
Structural family splits cleanly. M4 concentrates LLM work in note
evolution at write (`E_{5}{=}4.4`M, `E_{6}{=}1310` calls), trails M1 on
LME-S `P_{12}` by about `0.08` despite a `6.2\times` store compression,
and falls behind on CR on the two larger backbones, where the
evolved notes do not preserve the temporal serial-number cue the
benchmark relies on (M4 CR `P_{12}{=}0.140` on Qwen3-32B-AWQ and `0.080`
on Gemma-4). M5 is the most LLM-intensive substrate by a wide
margin (`E_{5}{=}10.3`M, `E_{2}{\approx}8.5` s/query on Qwen3-8B) and only
matches the flat M1 on LME-S SubEM (`P_{12}`), its higher
LLM-judge score not reflecting better retrieval recall. The Hierarchical
(M6) and Refinement families invert this trade-off. M6 pays
modest write-time tree summarization (`E_{5}{=}280`K) and posts one of the
highest LME-S `P_{2}` scores (`0.176` on
Qwen3-32B-AWQ, just behind M1’s `0.180`). M8 sits between M6 and M5 in cost but takes
the TTL `P_{12}` lead (0.96 / 0.94 / 0.95 across backbones),
confirming that skill bundles transfer cleanly when the downstream
task is itself few-shot ICL.

### Backbone dependence and internal-memory families.

The
relative ordering on `P_{12}` is mostly preserved across the three
backbones. M5’s LME-S advantage over M1 shows up only on the LLM-judge
score, growing from `+0.06` on Qwen3-8B to `+0.15` on Gemma-4, while
on SubEM the two stay within `0.02`. On TTL, by
contrast, M3’s lead over the Flat baselines is largest on Qwen3-8B
(`+0.27` over M1) and narrows on stronger backbones as the flat
stores themselves improve, while M8 keeps a commanding TTL `P_{12}` score
across all three (0.96 / 0.94 / 0.95). The internal-memory
families illustrate the limits of backbone-only solutions on dialog
QA. The Weight family (M9) collapses on LME-S regardless of
host (`P_{12}\leq 0.10`). Single-pass adapter tuning over QA pairs is
not enough for the recall-style preference questions LME-S asks,
and the same weakness reappears on CR (`P_{12}=0.16` on both Qwen backbones),
where conflicts hinge on serial-number-encoded recency that the
adapter cannot represent. The Activation family (M10, M11) shows the
sharpest *task* dependence in the table. Both substrates
collapse on LME-S long contexts (M10 `P_{12}\leq 0.137`, M11
`P_{12}\leq 0.234`) because the selected episode (M11) or the truncated
buffer (M10) omits distant single-utterance evidence, but on TTL
classification, where the relevant ICL examples are recent,
M11 climbs back to within `0.10` of the Flat substrates (its `P_{12}`
reaches `0.820` on Qwen3-32B-AWQ). M9, in contrast, gains
nothing from scale on CR, because the LoRA adapter encodes a
fixed-schema mapping that does not benefit from the larger backbone’s
better in-context routing. Its `P_{12}` stays flat at `0.16` across both
Qwen backbones, while every external substrate except M4 gains
`0.16` to `0.25` from Qwen3-8B to Gemma-4.
Together, these results suggest that LME-S rewards substrates with a
faithful, well-covered textual store, that TTL is dominated by
prompt-format alignment rather than
retrieval recall, and that auxiliary LLM cost (M5, M8) translates
into accuracy only on benchmarks (TTL, CR) whose answer surface
aligns with the substrate’s generative format.

### Storage and latency trade-offs.

Table [20](https://arxiv.org/html/2608.15008v2#A6.T20 "Table 20 ‣ Token accounting and memory quality. ‣ F.2 Full Tables for the LongMemEval-S and MAB Benchmarks ‣ Appendix F Full Tables ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") confirms three structural patterns.
First, `E_{1}` partitions the substrates into three storage tiers
that are nearly model-independent. Light stores (`\leq 80` KB) belong to the Activation family (M10, M11), which keeps only
episode centroids or chunk pointers; mid stores
(1.6–9.7 MB) to the Flat and Text families and M4; and
heavy stores (`{\sim}`22–32 MB, plus M9’s 80–320 MB
adapter) to M5, the Hierarchical and Refinement families, and
Weight. Second, `E_{2}` shifts with backbone size (roughly
`2` to `4\times` up from Qwen3-8B to Qwen3-32B-AWQ, then about
`0.5\times` down on Gemma-4), so the
*substrate-induced* latency overhead (the within-band spread
of `E_{2}`) is what differentiates the substrates. M5
pays `2` to `5\times` the per-query inference of M1/M2 because
its read path interleaves entity-graph traversal and chunk-level
vector search with the generator. M6 is the one apparent
exception. Our implementation defers tree construction to the
first read() call, so the first query absorbs the entire
one-off build cost, inflating `E_{2,\mathrm{mean}}`, `E_{14}`,
and `E_{15}` on every backbone (M6 is the only substrate with
`E_{2,\mathrm{p90}}<E_{2,\mathrm{mean}}`), while its
steady-state `E_{2,\mathrm{p90}}` is comparable to the Flat
baselines. Third, `E_{14}` separates substrates whose total cost
is dominated by *write* (M4 at `{\sim}`68–70K s and M5 at
`{\sim}`56–58K s across backbones, driven by per-write note
evolution and entity extraction) from those dominated by
*read* (M1, M2, and M10, mostly under 5K s). Since write
phases are amortizable across model swaps but read phases are
not, the per-query inference time `E_{2}` is the more reliable
cross-substrate efficiency signal.

### Token accounting and memory quality.

Table [21](https://arxiv.org/html/2608.15008v2#A6.T21 "Table 21 ‣ Token accounting and memory quality. ‣ F.2 Full Tables for the LongMemEval-S and MAB Benchmarks ‣ Appendix F Full Tables ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") cleanly separates the three
substrate families by their LLM-token profile. Flat (M1,
M2) substrates record only the
retrieved-token channel (`E_{7}`) and invoke no auxiliary LLM at write or
management time, so `E_{5}=E_{6}=E_{10}=E_{11}=0` and `E_{13}=0`;
the Activation substrates (M10, M11) likewise use no auxiliary
LLM and are shown as ‘–’ in the token-phase columns.
Refinement / Structural / Text substrates push 0.4–10.4M
tokens through the construct phase (`E_{5}`). M5 dominates
at 10.3M with 2,371 calls because it runs both
entity-extraction and relation-extraction passes per chunk, while
M6 is the cheapest of the auxiliary-LLM substrates at 280K
/ 80 calls thanks to log-depth tree clustering. The `P_{5}` column
exposes the storage-vs-compression trade-off. `P_{5}` ranges from 1.00
(M1/M2, verbatim stores) through 2.80 (M6, mild
summarization) to 12.50 (M8, highly abstracted skill
bundles). The dashed `P_{5}` entries for M9 / M10 / M11 reflect that
these substrates have no textual store on which compression can be
defined, a structural limitation rather than missing data.

Table 19: `P_{12}` (SubEM), `P_{2}` (F1), and `P_{3}` (BLEU-1) per substrate and backbone on LongMemEval-S and the three MAB capabilities.

|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  | LME-S | | | MAB LRU | | | MAB TTL | | | MAB CR | | |
| Model | ID | Family | `P_{12}` | `P_{2}` | `P_{3}` | `P_{12}` | `P_{2}` | `P_{3}` | `P_{12}` | `P_{2}` | `P_{3}` | `P_{12}` | `P_{2}` | `P_{3}` |
| Qwen3-8B | M1 | Flat | 0.390 | 0.170 | 0.113 | 0.592 | 0.491 | 0.417 | 0.570 | 0.476 | 0.405 | 0.330 | 0.211 | 0.171 |
| M2 | Flat | 0.340 | 0.170 | 0.114 | 0.606 | 0.527 | 0.448 | 0.480 | 0.399 | 0.340 | 0.280 | 0.188 | 0.155 |
| M3 | Text | 0.123 | 0.047 | 0.029 | 0.549 | 0.479 | 0.407 | 0.840 | 0.544 | 0.462 | 0.270 | 0.192 | 0.163 |
| M4 | Struct | 0.303 | 0.145 | 0.094 | 0.465 | 0.419 | 0.356 | 0.490 | 0.468 | 0.397 | 0.290 | 0.121 | 0.103 |
| M5 | Struct | 0.380 | 0.160 | 0.103 | 0.549 | 0.491 | 0.417 | 0.580 | 0.468 | 0.397 | 0.500 | 0.362 | 0.308 |
| M6 | Hier | 0.357 | 0.162 | 0.111 | 0.521 | 0.419 | 0.356 | 0.290 | 0.246 | 0.210 | 0.270 | 0.171 | 0.138 |
| M8 | Refine | 0.373 | 0.159 | 0.101 | 0.592 | 0.503 | 0.427 | 0.960 | 0.570 | 0.484 | 0.310 | 0.272 | 0.231 |
| M9 | Weight | 0.083 | 0.082 | 0.058 | 0.239 | 0.192 | 0.163 | 0.170 | 0.167 | 0.142 | 0.160 | 0.108 | 0.089 |
| M10 | Act | 0.090 | 0.075 | 0.053 | 0.648 | 0.575 | 0.488 | 0.140 | 0.130 | 0.111 | 0.270 | 0.161 | 0.124 |
| M11 | Act | 0.202 | 0.111 | 0.065 | 0.592 | 0.539 | 0.458 | 0.560 | 0.468 | 0.397 | 0.050 | 0.037 | 0.032 |
| Qwen3-32B-AWQ | M1 | Flat | 0.443 | 0.180 | 0.122 | 0.634 | 0.575 | 0.488 | 0.820 | 0.689 | 0.585 | 0.280 | 0.134 | 0.093 |
| M2 | Flat | 0.377 | 0.163 | 0.109 | 0.620 | 0.563 | 0.478 | 0.790 | 0.663 | 0.564 | 0.270 | 0.136 | 0.091 |
| M3 | Text | 0.225 | 0.124 | 0.072 | 0.704 | 0.658 | 0.560 | 0.860 | 0.722 | 0.614 | 0.280 | 0.158 | 0.120 |
| M4 | Struct | 0.357 | 0.160 | 0.106 | 0.521 | 0.455 | 0.387 | 0.680 | 0.666 | 0.566 | 0.140 | 0.072 | 0.049 |
| M5 | Struct | 0.460 | 0.159 | 0.104 | 0.592 | 0.491 | 0.417 | 0.620 | 0.510 | 0.433 | 0.440 | 0.191 | 0.127 |
| M6 | Hier | 0.413 | 0.176 | 0.117 | 0.577 | 0.623 | 0.529 | 0.340 | 0.281 | 0.238 | 0.280 | 0.135 | 0.090 |
| M8 | Refine | 0.403 | 0.166 | 0.111 | 0.577 | 0.503 | 0.427 | 0.940 | 0.790 | 0.672 | 0.310 | 0.162 | 0.115 |
| M9 | Weight | 0.100 | 0.098 | 0.065 | 0.408 | 0.359 | 0.305 | 0.324 | 0.318 | 0.270 | 0.160 | 0.086 | 0.059 |
| M10 | Act | 0.137 | 0.087 | 0.061 | 0.606 | 0.527 | 0.448 | 0.760 | 0.646 | 0.549 | 0.270 | 0.128 | 0.085 |
| M11 | Act | 0.080 | 0.080 | 0.056 | 0.592 | 0.515 | 0.438 | 0.820 | 0.689 | 0.585 | 0.230 | 0.122 | 0.086 |
| Gemma-4-26B | M1 | Flat | 0.433 | 0.200 | 0.135 | 0.662 | 0.575 | 0.488 | 0.770 | 0.629 | 0.535 | 0.520 | 0.267 | 0.223 |
| M2 | Flat | 0.357 | 0.180 | 0.122 | 0.662 | 0.673 | 0.572 | 0.730 | 0.620 | 0.527 | 0.520 | 0.248 | 0.202 |
| M3 | Text | 0.223 | 0.123 | 0.071 | 0.352 | 0.275 | 0.234 | 0.798 | 0.616 | 0.524 | 0.520 | 0.304 | 0.259 |
| M4 | Struct | 0.353 | 0.166 | 0.111 | 0.521 | 0.455 | 0.387 | 0.690 | 0.616 | 0.524 | 0.080 | 0.068 | 0.058 |
| M5 | Struct | 0.453 | 0.192 | 0.129 | 0.535 | 0.383 | 0.326 | 0.720 | 0.612 | 0.520 | 0.660 | 0.294 | 0.214 |
| M6 | Hier | 0.397 | 0.175 | 0.118 | 0.493 | 0.431 | 0.366 | 0.250 | 0.212 | 0.181 | 0.480 | 0.228 | 0.182 |
| M8 | Refine | 0.373 | 0.164 | 0.108 | 0.549 | 0.455 | 0.387 | 0.950 | 0.807 | 0.686 | 0.470 | 0.327 | 0.278 |
| M10 | Act | 0.063 | 0.045 | 0.039 | 0.577 | 0.579 | 0.492 | 0.460 | 0.391 | 0.332 | 0.500 | 0.263 | 0.222 |
| M11 | Act | 0.234 | 0.129 | 0.075 | 0.572 | 0.443 | 0.376 | 0.702 | 0.616 | 0.524 | 0.050 | 0.050 | 0.043 |

Table 20: LongMemEval-S storage and latency per substrate and backbone.

|  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Model | ID | Family | `E_{1}` | `E_{2,\mathrm{mean}}` | `E_{2,\mathrm{p90}}` | `E_{14}` | `E_{15}` |
| Qwen3-8B | M1 | Flat | 9.7M | 2,075 | 4,602 | 2,191 | 7.30 |
| M2 | Flat | 2.7M | 1,747 | 3,580 | 525 | 1.75 |
| M3 | Text | 4.5M | 4,500 | 9,000 | 16,674 | 55.58 |
| M4 | Struct | 1.6M | 1,828 | 4,233 | 67,702 | 225.67 |
| M5 | Struct | 32.0M | 8,500 | 18,000 | 56,162 | 187.21 |
| M6 | Hier | 27.5M | 19,956 | 5,195 | 5,987 | 19.96 |
| M8 | Refine | 22.7M | 1,869 | 4,392 | 30,855 | 102.85 |
| M9 | Weight | 80.0M | 2,400 | 5,000 | 15,451 | 51.50 |
| M10 | Act | 60K | 3,744 | 5,539 | 1,983 | 6.61 |
| M11 | Act | 80K | 1,900 | 4,200 | 4,382 | 14.61 |
| Qwen3-32B-AWQ | M1 | Flat | 9.7M | 7,413 | 18,100 | 3,600 | 12.00 |
| M2 | Flat | 2.7M | 7,307 | 18,824 | 2,193 | 7.31 |
| M3 | Text | 4.5M | 16,076 | 32,153 | 20,226 | 67.42 |
| M4 | Struct | 1.6M | 7,070 | 18,019 | 70,200 | 234.00 |
| M5 | Struct | 32.0M | 18,000 | 35,000 | 58,225 | 194.08 |
| M6 | Hier | 27.5M | 20,271 | 17,816 | 6,082 | 20.27 |
| M8 | Refine | 23.4M | 6,149 | 15,192 | 32,034 | 106.78 |
| M9 | Weight | 320M | 8,500 | 19,000 | 51,511 | 171.70 |
| M10 | Act | 60K | 14,650 | 28,022 | 6,894 | 22.98 |
| M11 | Act | 80K | 7,000 | 17,000 | 15,717 | 52.39 |
| Gemma-4-26B | M1 | Flat | 9.7M | 4,149 | 8,550 | 2,546 | 8.49 |
| M2 | Flat | 2.7M | 3,372 | 6,501 | 1,012 | 3.37 |
| M3 | Text | 4.5M | 8,998 | 17,996 | 9,534 | 31.78 |
| M4 | Struct | 1.6M | 3,805 | 9,027 | 69,116 | 230.39 |
| M5 | Struct | 32.0M | 12,000 | 23,000 | 57,280 | 190.93 |
| M6 | Hier | 27.5M | 17,189 | 9,007 | 5,157 | 17.19 |
| M8 | Refine | 21.7M | 3,124 | 6,540 | 31,140 | 103.80 |
| M10 | Act | 60K | 3,340 | 3,945 | 2,073 | 6.91 |
| M11 | Act | 80K | – | – | 5,550 | 18.50 |

Table 21: LongMemEval-S token usage and compression per substrate and backbone (`E_{5}` to `E_{7}`, `E_{12}`, `E_{13}`, `P_{5}`).

|  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Model | ID | Family | `E_{5}` | `E_{6}` | `E_{7}` | `E_{12}` | `E_{13}` | `P_{5}` |
| Qwen3-8B | M1 | Flat | 0 | 0 | 101K | 0 | 0 | 1.00 |
| M2 | Flat | 0 | 0 | 153K | 0 | 0 | 1.00 |
| M3 | Text | 437K | 671 | 5.0M | 5.3M | 731 | 4.50 |
| M4 | Struct | 4.4M | 1310 | 108K | 4.4M | 1310 | 6.20 |
| M5 | Struct | 10.3M | 2371 | 375K | 10.4M | 2431 | 3.80 |
| M6 | Hier | 280K | 80 | 46K | 280K | 80 | 2.80 |
| M8 | Refine | 1.8M | 1752 | 21K | 2.78M | 3504 | 12.50 |
| M9 | Weight | – | – | – | – | – | – |
| M10 | Act | – | – | 1.9M | – | – | – |
| M11 | Act | – | – | 250K | – | – | – |
| Qwen3-32B-AWQ | M1 | Flat | 0 | 0 | 101K | 0 | 0 | 1.00 |
| M2 | Flat | 0 | 0 | 153K | 0 | 0 | 1.00 |
| M3 | Text | 437K | 671 | 5.0M | 5.3M | 731 | 4.50 |
| M4 | Struct | 4.4M | 1310 | 108K | 4.4M | 1310 | 6.20 |
| M5 | Struct | 10.4M | 2369 | 385K | 10.4M | 2429 | 3.80 |
| M6 | Hier | 280K | 80 | 46K | 280K | 80 | 2.80 |
| M8 | Refine | 1.8M | 1752 | 20K | 2.78M | 3504 | 12.50 |
| M9 | Weight | – | – | – | – | – | – |
| M10 | Act | – | – | 1.9M | – | – | – |
| M11 | Act | – | – | 250K | – | – | – |
| Gemma-4-26B | M1 | Flat | 0 | 0 | 104K | 0 | 0 | 1.00 |
| M2 | Flat | 0 | 0 | 158K | 0 | 0 | 1.00 |
| M3 | Text | 437K | 671 | 5.0M | 5.3M | 731 | 4.50 |
| M4 | Struct | 4.4M | 1310 | 111K | 4.4M | 1310 | 6.20 |
| M5 | Struct | 10.4M | 2377 | 379K | 10.4M | 2437 | 3.80 |
| M6 | Hier | 280K | 80 | 46K | 280K | 80 | 2.80 |
| M8 | Refine | 1.9M | 1752 | 23K | 2.98M | 3504 | 12.50 |
| M9 | Weight | – | – | – | – | – | – |
| M10 | Act | – | – | 422K | – | – | – |
| M11 | Act | – | – | 250K | – | – | – |

### F.3 Full Tables for ALFWorld

### Substrate family vs. task success and cost.

The three
appendix tables sort the ten substrates evaluated on ALFWorld by
family. The Flat family (M1, M2) shows that retrieval-only memory is
backbone-dependent on ALFWorld. M1 trails NoMem on Qwen3-8B (5.2
vs. 5.7 TSR) but rises above it on Qwen3-32B-AWQ (27.6 vs. 22.4) and
Gemma-4 (10.4 vs. 7.5). M2 stays within about two points of
NoMem on every backbone (6.7, 21.6, and 9.7) at zero write cost. The
Text and Structural families (M3, M4, M5) recover modest gains on
Qwen3-32B-AWQ (M3 26.9, M4 26.9, M5 23.1 vs. NoMem 22.4) by paying
auxiliary LLM tokens during write, M3 and M4 spending 0.4 to 1.6
million tokens on gist or note generation and M5 running an entity
extraction loop of about 1.4 million tokens over roughly 400 calls. On Qwen3-8B and Gemma-4 the same substrates move NoMem by
a few points in either direction (M5 9.0 vs. 5.7 on Qwen3-8B, 4.5
vs. 7.5 on Gemma-4), suggesting that the bottleneck is action
planning rather than retrieval recall. The Hierarchical M6 shares the
lead only on Gemma-4 (10.4, tied with M1 and M3), falls below
NoMem on Qwen3-8B (4.5 vs. 5.7), and edges above it on Qwen3-32B-AWQ
(23.9 vs. 22.4).
The Refinement family separates its two members on the strongest
backbone. M7 is the top substrate on Qwen3-32B-AWQ (TSR 32.1, 9.7 points
above NoMem) because its skill-distillation prompts encode the goal
decomposition structure that ALFWorld rewards, whereas M8 trails M7
by 9.7 TSR points despite a similar per-write latency (`E_{3}` of about
2.6 s), which we attribute to prefilling every skill bundle diluting
the model’s attention over the goal-relevant one.

### Backbone dependence and internal-memory families.

Backbone size dominates the absolute TSR. Qwen3-32B-AWQ’s strongest
external substrate (M7 32.1) is more than three times Qwen3-8B’s (M5 9.0),
while Gemma-4 sits between (M1, M3, M6 each at 10.4). The
internal-memory families illustrate the limits of backbone-only
solutions. The Weight family (M9) is among the substrates that clearly
exceed NoMem on Qwen3-32B-AWQ (29.9 vs. 22.4, second only to M7) because
adapter tuning on demonstration trajectories captures action-grounded
patterns that pure text retrieval cannot. The same M9 collapses on
Qwen3-8B (3.0 TSR), where the smaller backbone overfits the LoRA
pairs, and it is excluded on Gemma-4 because it is incompatible
with the A4B MoE routing. The Activation family (M11) exceeds NoMem
on every backbone, most sharply on Qwen3-8B (11.9 vs. 5.7, roughly
double), because re-prefilling only
the matched episode keeps the prompt short and preserves the action
policy while keeping the persistent store small (around 6.9 thousand
bytes).
We omit M10 from the ALFWorld evaluation because
the cumulative trajectory text across the 134 task suite exceeds the
context window of every backbone we test. Naively concatenating
prior trajectories drives input length past 128 thousand tokens by
task 30 to 40 and forces aggressive truncation, which destroys the
comparison. Any reported M10 number on ALFWorld would reflect a
truncation policy rather than the substrate. The lighter M11 sidesteps
this problem by re-prefilling only the matched episode (around 120
thousand retrieved tokens across the run), which fits inside a single
context window per task. Together, these results suggest that ALFWorld
is dominated by action policy grounding rather than retrieval recall,
that the largest gains on the strongest backbone come from the
refinement (M7) and weight (M9) substrates, and that on the weaker backbones the gains
over NoMem are small (at most 6.2 points, M11 on Qwen3-8B) and come
from different substrates.

Table 22: ALFWorld-unseen performance per substrate and backbone. `P_{8}` TSR is in percent, Steps is the mean over all 134 episodes, and `P_{10}` counts successful episodes only.

|  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
| Model | Sub. | Family | `P_{8}` TSR (%) | Steps | `P_{10}` Steps`\mid\mathcal{S}` | `P_{\mathrm{avg}}` |
| Qwen3-8B | – | NoMem | 5.7 | 47.0 | 12.2 | 13.5 |
| M1 | Flat | 5.2 | 47.7 | 5.9 | 6.6 |
| M2 | Flat | 6.7 | 47.0 | 6.0 | 9.4 |
| M3 | Text | 5.2 | 47.8 | 8.3 | 8.4 |
| M4 | Struct | 7.5 | 46.9 | 7.9 | 8.5 |
| M5 | Struct | 9.0 | 47.1 | 17.4 | 12.5 |
| M6 | Hier | 4.5 | 48.4 | 15.0 | 8.3 |
| M7 | Refine | 7.5 | 47.3 | 13.7 | 9.6 |
| M8 | Refine | 8.2 | 47.4 | 18.5 | 9.5 |
| M9 | Weight | 3.0 | 49.1 | 19.5 | 3.2 |
| M11 | Act | 11.9 | 45.7 | 14.2 | 14.5 |
| Qwen3-32B-AWQ | – | NoMem | 22.4 | 41.6 | 11.3 | 23.7 |
| M1 | Flat | 27.6 | 39.6 | 9.6 | 16.2 |
| M2 | Flat | 21.6 | 41.4 | 10.8 | 15.4 |
| M3 | Text | 26.9 | 39.4 | 9.9 | 21.8 |
| M4 | Struct | 26.9 | 39.5 | 12.4 | 24.3 |
| M5 | Struct | 23.1 | 41.1 | 11.4 | 23.0 |
| M6 | Hier | 23.9 | 40.2 | 9.9 | 22.8 |
| M7 | Refine | 32.1 | 37.5 | 11.1 | 29.9 |
| M8 | Refine | 22.4 | 41.6 | 12.4 | 21.3 |
| M9 | Weight | 29.9 | 38.7 | 12.1 | 27.4 |
| M11 | Act | 26.9 | 39.5 | 12.3 | 24.7 |
| Gemma-4-26B | – | NoMem | 7.5 | 47.1 | 11.3 | 17.3 |
| M1 | Flat | 10.4 | 46.3 | 15.0 | 16.3 |
| M2 | Flat | 9.7 | 46.3 | 11.5 | 17.2 |
| M3 | Text | 10.4 | 46.3 | 14.8 | 14.9 |
| M4 | Struct | 8.2 | 47.1 | 14.5 | 13.9 |
| M5 | Struct | 4.5 | 48.1 | 8.5 | 9.4 |
| M6 | Hier | 10.4 | 46.0 | 11.4 | 18.1 |
| M7 | Refine | 8.2 | 46.7 | 10.1 | 17.8 |
| M8 | Refine | 8.2 | 46.9 | 12.5 | 18.5 |
| M11 | Act | 9.0 | 46.6 | 11.7 | 20.1 |

Table 23: ALFWorld-unseen latency and storage per substrate and backbone (`E_{1}` in bytes, `E_{2}` to `E_{4}` in ms, `E_{14}` in s, `E_{15}` in s/episode).

|  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Model | Sub. | Family | `E_{1}` | `E_{2}` | `E_{2,\text{p90}}` | `E_{3}` | `E_{4}` | `E_{14}` | `E_{15}` |
| Qwen3-8B | – | NoMem | 0 | 12,728 | 13,200 | – | – | 65,392 | 488 |
| M1 | Flat | 2.17M | 14,086 | 16,104 | 188 | 220 | 90,048 | 672 |
| M2 | Flat | 1.49M | 13,747 | 15,692 | 0 | 1 | 86,698 | 647 |
| M3 | Text | 1.43M | 13,655 | 16,318 | 1,620 | 754 | 87,502 | 653 |
| M4 | Struct | 942K | 12,903 | 14,843 | 6,134 | 9 | 81,070 | 605 |
| M5 | Struct | 532K | 13,167 | 15,702 | 5,021 | 9,412 | 83,080 | 620 |
| M6 | Hier | 25.1M | 13,539 | 15,641 | 624 | 191 | 87,904 | 656 |
| M7 | Refine | 3.90M | 13,297 | 15,988 | 2,519 | 175 | 84,286 | 629 |
| M8 | Refine | 5.27M | 13,069 | 15,300 | 2,521 | 173 | 83,080 | 620 |
| M9 | Weight | 15.3M | 18,757 | 22,002 | 1,400 | – | 123,414 | 921 |
| M11 | Act | 6.9K | 12,728 | 13,500 | – | – | 74,102 | 553 |
| Qwen3-32B-AWQ | – | NoMem | 0 | 20,100 | 20,300 | – | – | 78,122 | 583 |
| M1 | Flat | 2.17M | 20,500 | 31,100 | 192 | 644 | 144,720 | 1,080 |
| M2 | Flat | 1.49M | 20,300 | 30,800 | 0 | 1 | 146,060 | 1,090 |
| M3 | Text | 1.43M | 20,900 | 30,300 | 1,603 | 1,087 | 127,300 | 950 |
| M4 | Struct | 942K | 20,600 | 28,600 | 6,284 | 12 | 109,344 | 816 |
| M5 | Struct | 532K | 20,736 | 27,400 | 5,154 | 9,477 | 114,034 | 851 |
| M6 | Hier | 25.1M | 20,400 | 26,800 | 642 | 600 | 109,478 | 817 |
| M7 | Refine | 3.90M | 20,200 | 27,200 | 2,575 | 165 | 95,944 | 716 |
| M8 | Refine | 5.27M | 20,500 | 28,000 | 2,571 | 164 | 118,724 | 886 |
| M9 | Weight | 41.9M | 15,825 | 21,400 | 3,800 | – | 82,008 | 612 |
| M11 | Act | 6.9K | 20,100 | 22,000 | – | – | 104,922 | 783 |
| Gemma-4-26B | – | NoMem | 0 | 16,060 | 16,400 | – | – | 89,914 | 671 |
| M1 | Flat | 2.17M | 16,800 | 21,600 | 195 | 184 | 105,324 | 786 |
| M2 | Flat | 1.49M | 16,500 | 21,400 | 0 | 1 | 100,902 | 753 |
| M3 | Text | 1.43M | 16,857 | 20,466 | 1,649 | 1,009 | 104,654 | 781 |
| M4 | Struct | 942K | 20,007 | 22,517 | 6,089 | 11 | 126,228 | 942 |
| M5 | Struct | 532K | 15,564 | 19,906 | 5,089 | 9,358 | 100,366 | 749 |
| M6 | Hier | 25.1M | 16,114 | 21,099 | 619 | 173 | 99,294 | 741 |
| M7 | Refine | 3.90M | 16,866 | 21,107 | 2,542 | 161 | 105,592 | 788 |
| M8 | Refine | 5.27M | 16,269 | 20,148 | 2,544 | 159 | 102,242 | 763 |
| M11 | Act | 6.9K | 16,031 | 17,100 | – | – | 95,140 | 710 |

Table 24: ALFWorld-unseen token accounting per substrate on Qwen3-32B-AWQ (`E_{5}` to `E_{13}`).

|  |  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Sub. | Family | `E_{5}` | `E_{6}` | `E_{7}` | `E_{8}` | `E_{9}` | `E_{10}` | `E_{11}` | `E_{12}` | `E_{13}` |
| M1 | Flat | 0 | 0 | 264K | 0 | 0 | 0 | 0 | 0 | 0 |
| M2 | Flat | 0 | 0 | 268K | 0 | 0 | 0 | 0 | 0 | 0 |
| M3 | Text | 372K | 200 | 8.14M | 1.84M | 1,340 | 0 | 0 | 2.21M | 1,540 |
| M4 | Struct | 1.62M | 199 | 134K | 0 | 0 | 480K | 380 | 2.10M | 579 |
| M5 | Struct | 1.42M | 385 | 261 | 1.21M | 770 | 0 | 0 | 2.63M | 1,155 |
| M6 | Hier | 357K | 460 | 134K | 0 | 0 | 84.6K | 92 | 442K | 552 |
| M7 | Refine | 398K | 200 | 183K | 0 | 0 | 0 | 0 | 398K | 200 |
| M8 | Refine | 931K | 577 | 13.5K | 0 | 0 | 277K | 380 | 1.21M | 957 |
| M9 | Weight | – | – | 0 | – | – | – | – | – | – |
| M11 | Act | – | – | 118K | – | – | – | – | – | – |

### F.4 Full Tables for BigCodeBench-Hard

Tables [25](https://arxiv.org/html/2608.15008v2#A6.T25 "Table 25 ‣ F.4 Full Tables for BigCodeBench-Hard ‣ Appendix F Full Tables ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"), [26](https://arxiv.org/html/2608.15008v2#A6.T26 "Table 26 ‣ F.4 Full Tables for BigCodeBench-Hard ‣ Appendix F Full Tables ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"), and
[27](https://arxiv.org/html/2608.15008v2#A6.T27 "Table 27 ‣ F.4 Full Tables for BigCodeBench-Hard ‣ Appendix F Full Tables ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") report the per-substrate performance and
compression, latency and storage, and token accounting on
BigCodeBench-Hard for the three backbones, behind the BCB-Hard columns
of Table [2](https://arxiv.org/html/2608.15008v2#S4.T2 "Table 2 ‣ 4.1 User-centric Benchmark ‣ 4 Results ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents") and the discussion in
Section [4.2](https://arxiv.org/html/2608.15008v2#S4.SS2 "4.2 Agent-centric Benchmark ‣ 4 Results ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents").

Table 25: BigCodeBench-Hard performance and compression per substrate and backbone (Pass@1 in percent, `P_{5}`).

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| Model | Sub. | Family | Pass@1 `\uparrow` | `P_{5}` |
| Qwen3-8B | – | NoMem | 8.1 | – |
| M1 | Flat | 9.5 | 1.000 |
| M2 | Flat | 10.1 | 1.000 |
| M3 | Text | 8.1 | 1.964 |
| M4 | Struct | 10.1 | 0.982 |
| M5 | Struct | 15.5 | 0.817 |
| M6 | Hier | 12.2 | 0.820 |
| M7 | Refine | 12.2 | 5.705 |
| M8 | Refine | 14.9 | 4.432 |
| M9 | Weight | 7.4 | – |
| M11 | Act | 13.5 | – |
| Qwen3-32B-AWQ | – | NoMem | 17.6 | – |
| M1 | Flat | 18.2 | 1.000 |
| M2 | Flat | 19.6 | 1.000 |
| M3 | Text | 18.2 | 1.995 |
| M4 | Struct | 17.6 | 0.910 |
| M5 | Struct | 16.2 | 0.786 |
| M6 | Hier | 16.2 | 0.799 |
| M7 | Refine | 17.6 | 2.261 |
| M8 | Refine | 13.5 | 3.575 |
| M9 | Weight | 14.2 | – |
| M11 | Act | 13.5 | – |
| Gemma-4-26B | – | NoMem | 14.2 | – |
| M1 | Flat | 18.2 | 1.000 |
| M2 | Flat | 19.6 | 1.000 |
| M3 | Text | 14.2 | 2.444 |
| M4 | Struct | 18.9 | 0.982 |
| M5 | Struct | 20.9 | 0.813 |
| M6 | Hier | 18.9 | 0.813 |
| M7 | Refine | 16.9 | 1.102 |
| M8 | Refine | 18.2 | 4.471 |
| M11 | Act | 16.9 | – |

Table 26: BigCodeBench-Hard latency and storage.

|  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Model | Sub. | Family | `E_{1}` | `E_{2}` | `E_{2,\text{p90}}` | `E_{3}` | `E_{4}` | `E_{14}` | `E_{15}` |
| Qwen3-8B | – | NoMem | 0 | 3,800 | 4,940 | – | – | 592 | 4 |
| M1 | Flat | 1.32M | 4,976 | 6,631 | 199 | 183 | 776 | 5.2 |
| M2 | Flat | 245K | 4,853 | 6,600 | 0.1 | 3 | 718 | 4.9 |
| M3 | Text | 305K | 5,300 | 6,890 | 6,853 | 46 | 784 | 5.3 |
| M4 | Struct | 150K | 4,642 | 6,432 | 137 | 138 | 747 | 5.0 |
| M5 | Struct | 239K | 28,273 | 36,700 | 8,779 | 12,432 | 4,184 | 28.3 |
| M6 | Hier | 3.42M | 4,764 | 6,234 | 1,444 | 184 | 994 | 6.7 |
| M7 | Refine | 990K | 4,638 | 6,256 | 9,029 | 183 | 2,519 | 17.0 |
| M8 | Refine | 1.22M | 5,053 | 6,825 | 10,440 | 197 | 2,836 | 19.2 |
| M9 | Weight | 14.6M | 12,700 | 16,510 | – | – | 1,924 | 13 |
| M11 | Act | 151K | 16,800 | 21,840 | – | – | 2,516 | 17 |
| Qwen3-32B-AWQ | – | NoMem | 0 | 3,900 | 5,070 | – | – | 592 | 4 |
| M1 | Flat | 1.32M | 5,000 | 6,500 | 256 | 225 | 740 | 5 |
| M2 | Flat | 245K | 5,000 | 6,500 | 0.1 | 3 | 740 | 5 |
| M3 | Text | 296K | 5,400 | 7,020 | 9,309 | 1,843 | 1,184 | 8 |
| M4 | Struct | 150K | 4,900 | 6,370 | 12,460 | 376 | 2,960 | 20 |
| M5 | Struct | 249K | 31,221 | 28,239 | 7,888 | 14,723 | 4,621 | 31.2 |
| M6 | Hier | 3.50M | 4,400 | 5,720 | 1,995 | 220 | 1,036 | 7 |
| M7 | Refine | 1.93M | 4,300 | 5,590 | 12,994 | 195 | 3,108 | 21 |
| M8 | Refine | 1.14M | 4,600 | 5,980 | 12,447 | 186 | 3,256 | 22 |
| M9 | Weight | 38.0M | 14,600 | 18,980 | – | – | 2,220 | 15 |
| M11 | Act | 161K | 21,300 | 27,690 | – | – | 3,152 | 21.3 |
| Gemma-4-26B | – | NoMem | 0 | 19,800 | 25,740 | – | – | 2,960 | 20 |
| M1 | Flat | 1.32M | 21,916 | 28,533 | 213 | 289 | 3,286 | 22.2 |
| M2 | Flat | 245K | 20,602 | 27,860 | 0.0 | 2 | 3,049 | 20.6 |
| M3 | Text | 272K | 23,400 | 30,420 | 18,378 | 30 | 3,463 | 23.4 |
| M4 | Struct | 150K | 22,375 | 31,073 | 173 | 92 | 3,372 | 22.8 |
| M5 | Struct | 240K | 45,595 | 47,436 | 8,194 | 13,087 | 6,748 | 45.6 |
| M6 | Hier | 3.47M | 24,310 | 33,614 | 2,717 | 251 | 4,141 | 28.0 |
| M7 | Refine | 3.13M | 24,149 | 31,513 | 8,921 | 317 | 5,460 | 36.9 |
| M8 | Refine | 894K | 21,186 | 29,832 | 3,593 | 312 | 3,854 | 26.0 |
| M11 | Act | 115K | 31,600 | 41,080 | – | – | 4,736 | 32 |

Table 27: BigCodeBench-Hard token accounting per substrate and backbone (`E_{5}` to `E_{13}`).

|  |  |  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Model | Sub. | Family | `E_{5}` | `E_{6}` | `E_{7}` | `E_{8}` | `E_{9}` | `E_{10}` | `E_{11}` | `E_{12}` | `E_{13}` |
| Qwen3-8B | – | NoMem | – | – | 0 | – | – | – | – | – | – |
| M1 | Flat | 0 | 0 | 2.29M | 0 | 0 | 0 | 0 | 0 | 0 |
| M2 | Flat | 0 | 0 | 2.26M | 0 | 0 | 0 | 0 | 0 | 0 |
| M3 | Text | 55.9K | 36 | 2.80M | 2.84M | 148 | 0 | 0 | 2.90M | 184 |
| M4 | Struct | 0 | 0 | 2.16M | 0 | 0 | 0 | 0 | 0 | 0 |
| M5 | Struct | 0 | 0 | 40.7K | 116K | 148 | 0 | 0 | 116K | 148 |
| M6 | Hier | 44.7K | 82 | 1.14M | 0 | 0 | 11.5K | 16 | 56.2K | 98 |
| M7 | Refine | 244K | 200 | 593K | 0 | 0 | 0 | 0 | 244K | 200 |
| M8 | Refine | 308K | 200 | 550K | 0 | 0 | 146K | 200 | 454K | 400 |
| M9 | Weight | – | – | 0 | – | – | – | – | – | – |
| M11 | Act | – | – | 1.44M | – | – | – | – | – | – |
| Qwen3-32B-AWQ | – | NoMem | – | – | 0 | – | – | – | – | – | – |
| M1 | Flat | 0 | 0 | 2.29M | 0 | 0 | 0 | 0 | 0 | 0 |
| M2 | Flat | 0 | 0 | 2.26M | 0 | 0 | 0 | 0 | 0 | 0 |
| M3 | Text | 55.6K | 36 | 2.76M | 2.81M | 148 | 0 | 0 | 2.86M | 184 |
| M4 | Struct | 524K | 199 | 286K | 0 | 0 | 0 | 0 | 524K | 199 |
| M5 | Struct | 0 | 0 | 41.7K | 121K | 148 | 0 | 0 | 121K | 148 |
| M6 | Hier | 45.1K | 86 | 575K | 0 | 0 | 13.5K | 24 | 58.6K | 110 |
| M7 | Refine | 245K | 200 | 91.6K | 0 | 0 | 0 | 0 | 245K | 200 |
| M8 | Refine | 293K | 200 | 84.8K | 0 | 0 | 148K | 200 | 441K | 400 |
| M9 | Weight | – | – | 0 | – | – | – | – | – | – |
| M11 | Act | – | – | 1.48M | – | – | – | – | – | – |
| Gemma-4-26B | – | NoMem | – | – | 0 | – | – | – | – | – | – |
| M1 | Flat | 0 | 0 | 2.29M | 0 | 0 | 0 | 0 | 0 | 0 |
| M2 | Flat | 0 | 0 | 2.26M | 0 | 0 | 0 | 0 | 0 | 0 |
| M3 | Text | 52.2K | 36 | 2.26M | 2.30M | 148 | 0 | 0 | 2.35M | 184 |
| M4 | Struct | 0 | 0 | 2.16M | 0 | 0 | 0 | 0 | 0 | 0 |
| M5 | Struct | 0 | 0 | 40.1K | 177K | 148 | 0 | 0 | 177K | 148 |
| M6 | Hier | 44.4K | 82 | 1.14M | 0 | 0 | 12.6K | 24 | 57.0K | 106 |
| M7 | Refine | 161K | 200 | 901K | 0 | 0 | 0 | 0 | 161K | 200 |
| M8 | Refine | 204K | 200 | 705K | 0 | 0 | 129K | 200 | 333K | 400 |
| M11 | Act | – | – | 1.30M | – | – | – | – | – | – |

## Appendix G Additional Related Work

### Memory-augmented LLM agents.

The design space of agent memory has expanded rapidly along multiple substrate axes.
On the retrieval side, early systems such as Generative Agents [[41](https://arxiv.org/html/2608.15008v2#bib.bib4)] and MemGPT [[31](https://arxiv.org/html/2608.15008v2#bib.bib14)] store raw observations in flat vector indices or paged text buffers and retrieve them via embedding similarity or explicit memory paging.
These designs provide a simple and general interface for long-term recall, but they often rely on shallow similarity matching and provide limited structure for multi-hop reasoning, conflict handling, or memory maintenance.
Subsequent work shifts toward more structured representations.
Mem0 [[30](https://arxiv.org/html/2608.15008v2#bib.bib13)] distills conversations into atomic facts, Zep [[29](https://arxiv.org/html/2608.15008v2#bib.bib17)] and MAGMA [[42](https://arxiv.org/html/2608.15008v2#bib.bib25)] build temporal or multi-graph knowledge stores, and RAPTOR [[23](https://arxiv.org/html/2608.15008v2#bib.bib19)] and H-MEM [[24](https://arxiv.org/html/2608.15008v2#bib.bib18)] organize memory into multi-level hierarchies.
Amory [[43](https://arxiv.org/html/2608.15008v2#bib.bib103)] constructs episodic narratives from conversational fragments with offline agentic reasoning and retrieves memories through coherence-driven reasoning over the narrative structure.
These systems improve inspectability and abstraction, but they also introduce additional design choices around write-time summarization, graph construction, entity resolution, hierarchy depth, and retrieval traversal.

More recently, refinement-based and internal-memory substrates have emerged.
Sleep-time compute [[106](https://arxiv.org/html/2608.15008v2#bib.bib20)] uses offline computation to pre-generate useful future responses, while MemSkill [[26](https://arxiv.org/html/2608.15008v2#bib.bib21)] abstracts procedural experience into reusable skill entries for self-evolving agents.
HyperSkill [[39](https://arxiv.org/html/2608.15008v2#bib.bib104)] stores subtask steps and reusable skills in a hypergraph, ranks skills by co-occurrence across retrieved trajectories, and periodically prunes low-utility nodes and merges redundant skills.
Related work on skill evolution treats agent skills as reusable procedural artifacts and improves them with execution or verifier feedback [[107](https://arxiv.org/html/2608.15008v2#bib.bib109), [108](https://arxiv.org/html/2608.15008v2#bib.bib110)].
On the internal-memory side, SnapKV [[11](https://arxiv.org/html/2608.15008v2#bib.bib23)] and EpiCache [[28](https://arxiv.org/html/2608.15008v2#bib.bib24)] manage KV-cache activations through attention-guided eviction or episodic clustering, while adapter-based approaches store memory in parametric form by fine-tuning low-rank adapters on the accumulated content. Our M9 builds on LoRA-FA [[27](https://arxiv.org/html/2608.15008v2#bib.bib22)], a parameter-efficient fine-tuning method.
Several recent systems combine multiple substrates into broader memory operating systems or multi-agent memory architectures [[8](https://arxiv.org/html/2608.15008v2#bib.bib7), [44](https://arxiv.org/html/2608.15008v2#bib.bib26), [45](https://arxiv.org/html/2608.15008v2#bib.bib27)].
Despite this diversity, most systems commit to a fixed substrate configuration at design time and evaluate that configuration in a narrow task regime.
Our work complements these efforts by isolating the substrate as the experimental variable and providing a controlled empirical comparison of when each substrate family is preferable.

### Memory evaluation benchmarks.

Existing benchmarks span both user-centric [[109](https://arxiv.org/html/2608.15008v2#bib.bib29), [110](https://arxiv.org/html/2608.15008v2#bib.bib30)] and agent-centric [[3](https://arxiv.org/html/2608.15008v2#bib.bib34), [111](https://arxiv.org/html/2608.15008v2#bib.bib35)] memory demands, but they remain largely siloed within each regime.
On the user-centric side, LoCoMo [[15](https://arxiv.org/html/2608.15008v2#bib.bib9)] evaluates long-term conversational memory across five question types in dialogues averaging roughly 9K tokens over up to 35 sessions.
LongMemEval [[16](https://arxiv.org/html/2608.15008v2#bib.bib2)] scales memory evaluation to very long interaction histories and tests abilities such as information seeking, knowledge updates, abstention, and temporal reasoning.
MemoryAgentBench [[32](https://arxiv.org/html/2608.15008v2#bib.bib28)] frames memory evaluation as incremental multi-turn interaction, covering accurate retrieval, long-range understanding, test-time learning, and conflict resolution.
MemoryCD [[46](https://arxiv.org/html/2608.15008v2#bib.bib106)] derives a cross-domain memory benchmark from years of real user behavior in the Amazon Review dataset and evaluates four personalization tasks across twelve domains.
JARVIS-Bench [[5](https://arxiv.org/html/2608.15008v2#bib.bib108)] builds on 28 to 44 days of real users’ multimodal daily traces, augmented with synthetic trajectory expansions, to benchmark personal intelligence agents across an input ladder from no memory to lifelong memory.
Together, these benchmarks stress whether a memory system can preserve and retrieve relevant user information over long histories.

On the agent-centric side, ALFWorld [[33](https://arxiv.org/html/2608.15008v2#bib.bib31)] requires multi-step household planning from text-based observations and admissible actions, BigCodeBench [[34](https://arxiv.org/html/2608.15008v2#bib.bib32)] evaluates code generation with compositional function calls and realistic execution-based grading, and SWE-bench [[48](https://arxiv.org/html/2608.15008v2#bib.bib33)] tests repository-level bug fixing where memory of codebase structure and previous patches may be useful.
These benchmarks stress a different regime: the agent must execute precise action or code-generation decisions, and retrieved information can be harmful when it distracts from the current observation, instruction, or execution context.
This user-centric/agent-centric divide exposes fundamentally different retrieval dynamics.
User-centric tasks often benefit from returning more candidate facts, while agent-centric tasks can degrade when imprecise retrieval dilutes attention over action-critical context.
However, existing evaluations rarely test the same set of memory substrates across both regimes under controlled conditions.
Our work bridges this gap by evaluating the same substrate configurations across benchmarks from both sides of the spectrum.

### Empirical evaluation practices in agent memory.

The metrics reported by existing memory systems provide an incomplete picture of substrate behavior.
Nearly all systems report some form of end-task accuracy, token F1, exact match, task success, pass rate, or LLM-as-a-judge score, but the dimensions that govern deployment feasibility are often omitted.
Write cost, including the number of LLM calls and tokens consumed during memory construction, is rarely measured systematically.
Management cost, including the overhead of deduplication, conflict resolution, summarization, graph maintenance, and memory rewriting, is likewise underreported, even in systems such as A-Mem [[21](https://arxiv.org/html/2608.15008v2#bib.bib6)] and Zep [[29](https://arxiv.org/html/2608.15008v2#bib.bib17)], whose architectures explicitly include management operations.
Compression ratio, which quantifies how much information each stored token preserves, has also not been consistently measured across substrates.
MemAudit [[47](https://arxiv.org/html/2608.15008v2#bib.bib107)] raises a complementary concern, namely that the stored memory itself is rarely audited because evaluation mostly goes through downstream behavior. It evaluates memory as a post-interaction artifact, reconstructing a hidden user state from what the agent stores, and finds that task completion and recoverable memory behave as distinct capabilities.

Among efficiency dimensions that are occasionally reported, coverage remains sparse.
The most complete prior comparison is that of Mem0 [[30](https://arxiv.org/html/2608.15008v2#bib.bib13)], which compares seven memory systems and fourteen RAG configurations head to head on LoCoMo and reports search and total latency at p50 and p95 together with the tokens retrieved per query. Its per-method accounting is read-side. The token-consumption metric counts the tokens retrieved as answer context, which underlies the reported saving of more than 90% token cost relative to full context, and per-turn write and management calls are not reported separately. A stored-memory token budget is given for three systems and shows how large construction can be, since Zep’s memory graph exceeds 600k tokens per conversation against roughly 26k tokens for the raw conversation. Zep reports latency and token cost without a cross-substrate accounting of memory construction. LightMem [[55](https://arxiv.org/html/2608.15008v2#bib.bib10)] separates total from purely online test-time token usage and API calls, but does not attribute costs to the write, read, and management stages. Our metrics attribute tokens and calls to the write (E5, E6), read (E8, E9), and management (E10, E11) stages and add storage (E1) and wall-clock (E14), which gives, to our knowledge, the first stage-attributed cost accounting across substrate families.
This metric narrowness means that a substrate consuming a large number of auxiliary LLM calls can appear indistinguishable from a substrate requiring no auxiliary calls when both are evaluated only by downstream accuracy.
In addition, even the accuracy metrics that are commonly reported may be less stable than assumed.
Recent work [[112](https://arxiv.org/html/2608.15008v2#bib.bib36)] shows that reordering score rubrics or altering reference answer quality in LLM-as-a-judge prompts can disrupt scoring stability across judge models, yet published memory evaluations often use different judge prompts and scoring configurations.
Our work fills these gaps by measuring task performance, computational efficiency, and memory quality across all substrate configurations under a single controlled setup.

## Appendix H Limitations

We exclude MemGPT [[31](https://arxiv.org/html/2608.15008v2#bib.bib14)], Mem0 [[30](https://arxiv.org/html/2608.15008v2#bib.bib13)], and
Zep [[29](https://arxiv.org/html/2608.15008v2#bib.bib17)] because their defining mechanisms are policies outside
the single-variable frame and their auxiliary-LLM cost is one to two orders of
magnitude above the lighter substrates (Appendix [B.5](https://arxiv.org/html/2608.15008v2#A2.SS5 "B.5 Memory Substrate and Method Exclusion ‣ Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")). M8 and
M11 are harness-compatible approximations of MemSkill and EpiCache
(Appendix [B](https://arxiv.org/html/2608.15008v2#A2 "Appendix B Memory Substrate Implementation Details ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")), and a shared harness can disadvantage methods that
rely on their own controller or prompts. The agent-centric benchmarks have 134 and 148
tasks and the main tables report single greedy runs, so apart from the significant
ALFWorld refinement comparison (Appendix [E.1](https://arxiv.org/html/2608.15008v2#A5.SS1 "E.1 Statistical Significance ‣ Appendix E Additional Analyses ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")) we read small gaps as
descriptive. The `P_{4}` judge, gpt-4o-mini, is also the auxiliary LLM and was
checked only against three other judges from the same provider, not against human labels
(Appendix [E.2](https://arxiv.org/html/2608.15008v2#A5.SS2 "E.2 LLM-Judge Agreement ‣ Appendix E Additional Analyses ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")). Routing gains are in-sample at the regime level, and the
query-level router, tested on LoCoMo with one backbone, gains only on questions from
conversations it saw in training (Appendix [E.3](https://arxiv.org/html/2608.15008v2#A5.SS3 "E.3 Substrate Routing ‣ Appendix E Additional Analyses ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")). Finally, none of our main benchmarks is built so that later sessions depend on memory the agent wrote in earlier ones (Appendix [C.3](https://arxiv.org/html/2608.15008v2#A3.SS3 "C.3 Coverage of the Memory Lifecycle ‣ Appendix C Benchmark Setups and Bank Alignment ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")). The supplementary MemoryArena evaluation of such tasks covers one backbone and two domains (Appendix [E.5](https://arxiv.org/html/2608.15008v2#A5.SS5 "E.5 Supplementary Evaluation on MemoryArena ‣ Appendix E Additional Analyses ‣ Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents")).

## Appendix I Broader Impacts

This work provides empirical guidance for designing memory systems for long-horizon LLM
agents. More efficient and reliable agent memory could reduce the energy use of agentic
deployments, improve consistency in long-running personal companions and coding assistants,
and give future memory research a controlled evaluation framework to build on.
Better-functioning long-term memory could also enable more persistent agentic surveillance or
more convincing persona simulations. We view these as derivative risks of foundation-model
agents in general rather than risks specific to substrate evaluation, and we release no new
model or dataset that would directly enable misuse.

## Appendix J Declaration of LLM Usage

LLMs were used by the authors only for routine writing assistance, such as grammar
polishing, phrasing refinement, and LaTeX formatting. They were not used to generate
research ideas, design experiments, analyze results, or produce any of the empirical
findings reported in this paper. All scientific contributions, including the harness
design, substrate implementations, metric taxonomy, and analysis, are the original
work of the authors.
