---
title: "Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"
url: https://arxiv.org/abs/2604.25850
published: 2026-04-28
fetched: 2026-11-11
type: paper
topics: [loops-selfimprovement, harness]
summary: "研究自动分析执行轨迹、定位跨任务失败并修改 harness，附带具体错误复盘与消融；预印本，适合只精读方法和案例。"
---

# Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses

Jiahang Lin*‡
Affiliation: Fudan University
  
Shichun Liu*‡
Affiliation: Fudan University
  
Chengjun Pan*‡
Affiliation: Peking University
  
Lizhi Lin
Affiliation: Shanghai Qiji Zhifeng Co., Ltd
 [china-qijizhifeng/agentic-harness-engineering](https://github.com/china-qijizhifeng/agentic-harness-engineering)
  
Shihan Dou
Affiliation: Fudan University
  
Zhiheng Xi
Affiliation: Fudan University
  
Xuanjing Huang
Affiliation: Fudan University
  
Hang Yan
Affiliation: Shanghai Qiji Zhifeng Co., Ltd
 [china-qijizhifeng/agentic-harness-engineering](https://github.com/china-qijizhifeng/agentic-harness-engineering)
  
Zhenhua Han†
Affiliation: Shanghai Qiji Zhifeng Co., Ltd
 [china-qijizhifeng/agentic-harness-engineering](https://github.com/china-qijizhifeng/agentic-harness-engineering)
  
Tao Gui†
Affiliation: Fudan University
  
Yu-Gang Jiang
Affiliation: Fudan University

## Abstract

Harnesses are now central to agent performance, mediating how models interact with tools and execution environments.
Yet harness engineering remains a manual craft, because automating it faces a heterogeneous action space across editable components, voluminous trajectories that bury actionable signal, and edits whose effect is hard to attribute.
We introduce Agentic Harness Engineering (AHE), a closed loop that addresses these challenges through three matched observability pillars: ❶ *component observability* gives every editable harness component a file-level representation so the action space is explicit and revertible; ❷ *experience observability* distills millions of raw trajectory tokens into a layered, drill-down evidence corpus that an evolving agent can actually consume; and ❸ *decision observability* pairs every edit with a self-declared prediction, later verified against the next round’s task-level outcomes.
Together, these pillars turn every edit into a falsifiable contract, so harness evolution proceeds autonomously without collapsing into trial-and-error.
Empirically, ten AHE iterations lift pass@1 on Terminal-Bench 2 from 69.7% to 77.0%, surpassing the human-designed harness Codex (71.9%) and the self-evolving baselines ACE and Training-Free GRPO.
The frozen harness transfers without re-evolution: on SWE-bench-verified it achieves the highest aggregate success while using `12\%` fewer tokens than the seed, and on Terminal-Bench 2 it yields `+5.1` to `+10.1` pp cross-family gains across three alternate model families, indicating the evolved components encode general engineering experience rather than benchmark-specific tuning.
Ablations further localize the gain to tools, middleware, and long-term memory rather than the system prompt.
These results position observability-driven evolution as a practical pathway to keep coding-agent harnesses continually improving alongside their base models.

††footnotetext: ∗Equal contributions. †Corresponding authors: [hzhua201@gmail.com](mailto:hzhua201@gmail.com), [tgui@fudan.edu.cn](mailto:tgui@fudan.edu.cn). ‡Work done during an internship at Shanghai Qiji Zhifeng Co., Ltd. 

Figure 1: AHE evolves a bash-only seed past every human-designed and self-evolving baseline on Terminal-Bench 2. All three role agents share one base model, isolating the gain to harness edits rather than analyzer or editor capability.

## 1 Introduction

Coding agents are increasingly deployed on long-horizon software-engineering tasks, with measurable progress on issue resolution over real-world code repositories [[14](https://arxiv.org/html/2604.25850#bib.bib16), [46](https://arxiv.org/html/2604.25850#bib.bib46), [7](https://arxiv.org/html/2604.25850#bib.bib7)] and multi-step terminal workflows [[21](https://arxiv.org/html/2604.25850#bib.bib24)].
In practice, such progress relies not only on the underlying language model, but equally on the surrounding engineering components: the system prompt that shapes work style, the tools that expose the file system and shell, and the middleware that controls context, execution, and recovery.
This collection of model-external, editable components is collectively referred to as the agent’s *harness* [[30](https://arxiv.org/html/2604.25850#bib.bib32), [18](https://arxiv.org/html/2604.25850#bib.bib21), [42](https://arxiv.org/html/2604.25850#bib.bib40), [45](https://arxiv.org/html/2604.25850#bib.bib45), [33](https://arxiv.org/html/2604.25850#bib.bib34), [31](https://arxiv.org/html/2604.25850#bib.bib12)].

Harness design materially shifts task completion on long-horizon coding benchmarks, even with the base model held fixed [[40](https://arxiv.org/html/2604.25850#bib.bib39), [42](https://arxiv.org/html/2604.25850#bib.bib40)], making harness engineering a first-class lever for improving coding agents.
Moreover, the optimal harness is model-specific: a harness tuned for one base model often underperforms on another and must be re-adapted as the base model changes.
In current practice, this adaptation is performed manually—developers inspect trajectories, identify recurring failure patterns, and hand-craft edits across prompts, tools, middleware, and skills.
Yet as base models advance rapidly [[39](https://arxiv.org/html/2604.25850#bib.bib42), [38](https://arxiv.org/html/2604.25850#bib.bib38), [44](https://arxiv.org/html/2604.25850#bib.bib44), [6](https://arxiv.org/html/2604.25850#bib.bib6), [36](https://arxiv.org/html/2604.25850#bib.bib18), [35](https://arxiv.org/html/2604.25850#bib.bib36)], this manual loop struggles to keep pace, creating a widening gap between model capability and the harness needed to realize it [[33](https://arxiv.org/html/2604.25850#bib.bib34)].

An intuitive direction is to automate this loop with an evolution agent that optimizes harness components based on experience [[1](https://arxiv.org/html/2604.25850#bib.bib1), [49](https://arxiv.org/html/2604.25850#bib.bib49), [4](https://arxiv.org/html/2604.25850#bib.bib4)].
However, few existing approaches jointly evolve the full set of editable components [[16](https://arxiv.org/html/2604.25850#bib.bib19)]; most focus on a single component, typically the prompt [[32](https://arxiv.org/html/2604.25850#bib.bib33), [50](https://arxiv.org/html/2604.25850#bib.bib50), [20](https://arxiv.org/html/2604.25850#bib.bib22)], skills [[19](https://arxiv.org/html/2604.25850#bib.bib23), [43](https://arxiv.org/html/2604.25850#bib.bib43)], or an in-context playbook [[49](https://arxiv.org/html/2604.25850#bib.bib49)].
Jointly evolving multiple components end-to-end faces two structural obstacles: long, unstructured trajectories yield little actionable signal, and tightly coupled harness frameworks make edits beyond the prompt error-prone.
This leaves the central question of agent-driven harness evolution open:
How can an evolution agent jointly and stably evolve all editable components of a coding agent’s harness?

Our central insight is that this question is bottlenecked by *observability*, not by agent capability: once the evolution agent receives structured context over a clear action space, it can reliably converge on better harness designs [[34](https://arxiv.org/html/2604.25850#bib.bib35), [53](https://arxiv.org/html/2604.25850#bib.bib53)].
We implement this in Agentic Harness Engineering
(AHE, Figure [2](https://arxiv.org/html/2604.25850#S3.F2 "Figure 2 ‣ 3.1 NexAU: an editable, decoupled harness substrate ‣ 3 Method ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses")), a closed loop driven by three observability pillars:
❶ *component observability* via a decoupled harness that exposes seven editable component types as files, so each failure pattern maps cleanly to a single component class;
❷ *experience observability* via a layered, drill-down evidence corpus distilled from millions of raw trajectory tokens, so the evolver consumes structured root causes rather than raw logs; and
❸ *decision observability* via a change manifest that pairs every edit with a self-declared prediction, later verified against the next round’s task-level outcomes, so each edit becomes a falsifiable contract and ineffective ones are reverted at file granularity.

We empirically validate AHE on Terminal-Bench 2[[21](https://arxiv.org/html/2604.25850#bib.bib24)]: ten iterations lift pass@1 from 69.7% to 77.0%, surpassing the human-designed Codex [[25](https://arxiv.org/html/2604.25850#bib.bib28)] and the self-evolving baselines ACE [[49](https://arxiv.org/html/2604.25850#bib.bib49)] and Training-Free GRPO [[4](https://arxiv.org/html/2604.25850#bib.bib4)].
Without further evolution, the frozen harness transfers to SWE-bench-verified [[14](https://arxiv.org/html/2604.25850#bib.bib16)], and across three alternate base-model families it yields consistent pass@1 gains of `+5.1` to `+10.1` pp, with the largest on bases further from saturation, suggesting that AHE encodes coordination patterns that less-saturated models lean on more heavily.
A component ablation pinpoints where this gain lives: tools, middleware, and long-term memory each carry the improvement on their own, while the system prompt alone regresses, indicating that factual harness structure transfers across tasks and models whereas prose-level strategy does not.

This paper makes three contributions:

- •

  We formulate *agent-driven harness evolution* for coding agents and propose AHE, which identifies *observability across components, trajectories, and decisions* as the design pivot and turns every harness edit into a falsifiable, file-level contract through three observability pillars: a decoupled component substrate, a layered trajectory-distillation pipeline, and a change manifest whose self-declared predictions are verified by next-round task deltas.
- •

  We empirically show that AHE lifts pass@1 on Terminal-Bench 2 from 69.7% to 77.0%, surpasses human-designed and automated baselines, and produces a frozen harness that transfers across benchmarks and base-model families.
- •

  Our analysis reveals two limits of agent-driven evolution: harness components interact non-additively, so stacking effective edits caps the aggregate gain; and the loop’s self-attribution is reliable for fixes but blind to regressions, pinpointing regression foresight as the clearest direction for future self-evolution loops.

## 2 Related Work

### 2.1 Harness Engineering and Evaluation for Coding Agents

Harness engineering refers to the practice of designing the system surrounding the model, including its tools, interfaces, memory, execution constraints, and feedback loops, which together shape what an agent can do on long-horizon tasks [[30](https://arxiv.org/html/2604.25850#bib.bib32), [18](https://arxiv.org/html/2604.25850#bib.bib21), [40](https://arxiv.org/html/2604.25850#bib.bib39), [3](https://arxiv.org/html/2604.25850#bib.bib3), [33](https://arxiv.org/html/2604.25850#bib.bib34), [31](https://arxiv.org/html/2604.25850#bib.bib12)].
Concretely, the harness mediates how the model perceives and acts on its environment: it exposes the action and observation interfaces over which tool-augmented reasoning unfolds [[3](https://arxiv.org/html/2604.25850#bib.bib3)], custom agent-computer interfaces for repository navigation, file editing, and command execution [[45](https://arxiv.org/html/2604.25850#bib.bib45)], as well as sandboxed execution and orchestration support that keep long-horizon runs reproducible [[42](https://arxiv.org/html/2604.25850#bib.bib40)].

Verifying that such systems actually help has driven the parallel maturation of coding-agent evaluation along two axes: task horizon and environmental realism.
Coverage extends from short-horizon function-level benchmarks focused on contamination and freshness control [[52](https://arxiv.org/html/2604.25850#bib.bib52), [12](https://arxiv.org/html/2604.25850#bib.bib14)], through repository-scale executable patch resolution [[14](https://arxiv.org/html/2604.25850#bib.bib16), [46](https://arxiv.org/html/2604.25850#bib.bib46), [7](https://arxiv.org/html/2604.25850#bib.bib7)], to multi-hour, terminal-driven workflows that exercise long-horizon, realistic execution [[22](https://arxiv.org/html/2604.25850#bib.bib25), [5](https://arxiv.org/html/2604.25850#bib.bib5), [21](https://arxiv.org/html/2604.25850#bib.bib24)].
A parallel infrastructure track packages executable runtimes and verifiers around these benchmarks [[28](https://arxiv.org/html/2604.25850#bib.bib31), [13](https://arxiv.org/html/2604.25850#bib.bib15), [47](https://arxiv.org/html/2604.25850#bib.bib47)], whose attention to reproducible, traceable, and verifiable execution directly motivates the observation system AHE builds on.

### 2.2 Automated Optimization of LLM Agents

Approaches to automated agent optimization differ in what evidence the optimizer observes and what it can edit.
Some revise the agent’s own outputs through episodic critique and reflection [[20](https://arxiv.org/html/2604.25850#bib.bib22), [32](https://arxiv.org/html/2604.25850#bib.bib33), [9](https://arxiv.org/html/2604.25850#bib.bib10)].
Others target prompts and instructions [[15](https://arxiv.org/html/2604.25850#bib.bib17)]: structured playbooks [[49](https://arxiv.org/html/2604.25850#bib.bib49)], semantic-advantage priors [[4](https://arxiv.org/html/2604.25850#bib.bib4)], jointly optimized instruction-demonstration pipelines for multi-stage programs [[27](https://arxiv.org/html/2604.25850#bib.bib30)], and reflective updates driven by Pareto-frontier traces [[1](https://arxiv.org/html/2604.25850#bib.bib1)].
A separate line edits program structure itself, in the form of skill libraries [[41](https://arxiv.org/html/2604.25850#bib.bib41)], scored program and agent archives evolved through mutation [[24](https://arxiv.org/html/2604.25850#bib.bib27), [11](https://arxiv.org/html/2604.25850#bib.bib13)], and graph-structured workflows searched or learned from rollouts [[48](https://arxiv.org/html/2604.25850#bib.bib48), [51](https://arxiv.org/html/2604.25850#bib.bib51)].

AHE tunes the full harness as a combinatorial whole rather than a single editable surface, so cross-component trade-offs become legible to the optimizer.
It also keeps the human prior minimal, leaving methodology for the optimizer to discover from rollouts rather than fixing it by hand.
We describe the substrate, trajectory analysis, and iteration that realize these choices in Section [3](https://arxiv.org/html/2604.25850#S3 "3 Method ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").

## 3 Method

AHE turns harness optimization into a closed loop driven by another agent, with the base model held fixed and only the explicit harness edited.
Our design principle is that every phase of this loop must be *observable*: AHE faithfully records the artifacts each phase produces (the harness components an iteration writes, the rollout trajectories it generates, the edit decisions it commits) and represents them in structured, layered forms that another agent can read and act on.

Three observability layers implement this principle.
Component observability (§[3.1](https://arxiv.org/html/2604.25850#S3.SS1 "3.1 NexAU: an editable, decoupled harness substrate ‣ 3 Method ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses")) is realized by a decoupled, file-level harness substrate that maps each failure pattern to a single component class.
Experience observability (§[3.2](https://arxiv.org/html/2604.25850#S3.SS2 "3.2 Agent Debugger: layered trajectory evidence ‣ 3 Method ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses")) is realized by a layered evidence corpus distilled from raw rollouts and indexed for drill-down access.
Decision observability (§[3.3](https://arxiv.org/html/2604.25850#S3.SS3 "3.3 Evolve Agent: evidence-driven, auditable edits ‣ 3 Method ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses")) is realized by a change manifest that pairs every edit with a self-declared prediction the next round verifies.
The three layers compose into the iteration of Algorithm [1](https://arxiv.org/html/2604.25850#alg1 "Algorithm 1 ‣ 3.3 Evolve Agent: evidence-driven, auditable edits ‣ 3 Method ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"), which runs unattended round after round.

### 3.1 NexAU: an editable, decoupled harness substrate

![Refer to caption](https://arxiv.org/html/2604.25850v4/method.png)

Figure 2: The AHE pipeline links three observable surfaces into one closed loop. Components, rollout experience, and edit decisions each surface as structured artifacts another agent reads, and every edit becomes a falsifiable prediction the next round verifies.

We instantiate the harness `H` on the NexAU framework [[23](https://arxiv.org/html/2604.25850#bib.bib26), [37](https://arxiv.org/html/2604.25850#bib.bib37)], which exposes seven orthogonal component types as explicit files at fixed mount points in a single workspace: system prompt, tool description, tool implementation, middleware, skill, sub-agent configuration, and long-term memory.
The component types are loosely coupled, so adding a middleware does not require editing the system prompt, and adding a skill does not require touching any tool.

This decoupling is what realizes component observability: each failure pattern maps to a single component class, giving the evolve agent a clean action space and localizing every pass-rate change to one file rather than scattering it across hundreds of lines of unstructured prompt prose. Each logical edit becomes one commit on the workspace’s git history, which yields file-level diffs and rollback granularity for free.

Our seed harness `H_{0}` is deliberately minimal: a single shell-execution tool, no middleware, no skills, no sub-agents. A seed already fitted to the target benchmark would contaminate every subsequent edit’s attribution, since we could not tell whether a gain came from the loop or from the seed. The minimal seed forces every component AHE adds to earn its place against measured rollouts.

### 3.2 Agent Debugger: layered trajectory evidence

We generate `k` traces for each task in a benchmark using a harness `H`, which may contain errors resulting from the deficiencies of the harness that can be acted on, but scattered across millions of tokens of raw messages. To extract insights from agent trajectories and enable experience observability, we apply Agent Debugger [[17](https://arxiv.org/html/2604.25850#bib.bib20)] framework to use an agent to explore trajectories framed as a navigable, file-based environment where each trajectory message lives in its own file and is reached through generic shell and scripting tools. Traces with the same query are placed in one environment, and the debugger is required to analyze the root cause of the failure or the success pattern, which is stored in *per-task analysis* report for each task. The analysis also includes pass/fail status of the task to ground the Evolve Agent. Finally, a *benchmark-level overview* is aggregated from every report into a single document as an entry point for every iteration.

In addition to these reports, we also provide *original* traces in case the agents need to verify the claims in the reports. The traces are provided both in raw form and lightly processed to remove unnecessary content. All of these content is provided as files allowing progressive disclosure [[29](https://arxiv.org/html/2604.25850#bib.bib8)] which saves on tokens and enable better agent decisions.

### 3.3 Evolve Agent: evidence-driven, auditable edits

The Evolve Agent closes the AHE loop. In each round it reads the layered evidence corpus produced by the Agent Debugger, decides which harness components to add, modify, or remove, applies those edits to the workspace, and records the reasoning behind every edit. Two constraints govern these edits, and together they realize decision observability: every edit becomes a falsifiable, file-level claim recorded in a versioned manifest, and the next round’s verdict either confirms or reverts it.

The first constraint is controllability: the Evolve Agent writes only inside the harness workspace, while the runs directory, tracer, verifier, and LLM configuration are read-only, and the seed system prompt (Appendix [B.1](https://arxiv.org/html/2604.25850#A2.SS1 "B.1 Code Agent Seed System Prompt ‣ Appendix B Prompts and Configurations ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses")) is marked non-deletable.
These restrictions block the shortcuts an unconstrained self-modifier would take, such as disabling the verifier, swapping the model, or raising the reasoning budget, and keep every recorded gain attributable to harness edits.

The second constraint is that every change is evidence-driven and ships with a recorded prediction.
Each edit attaches a manifest entry that names the failure evidence, the inferred root cause, the targeted fix, and a predicted impact comprising both expected fixes and at-risk regressions; this manifest is the loop’s evidence ledger (see Appendix [B.2](https://arxiv.org/html/2604.25850#A2.SS2 "B.2 Evolve Agent Prompt ‣ Appendix B Prompts and Configurations ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses")).
In the next round, the loop intersects the predicted-fix and predicted-regression sets with the observed task-level deltas to produce a per-edit verdict.
Each edit thereby becomes falsifiable by the next evaluation, which replaces rationale-driven self-justification with a measurable contract between rounds.

Algorithm 1  AHE outer loop.

1:
seed harness `H_{0}`, base model `M`, benchmark `D`, rollouts per task `k`, max iterations `N`

2:
`H_{\text{best}}\leftarrow H_{0}`

3:
for `t=1` to `N` do

4:
  `T_{t}\leftarrow\textsc{Rollout}(M,H_{t-1},D,k)` `\triangleright` phase 1: `k` rollouts per task

5:
  `\widetilde{T}_{t}\leftarrow\textsc{Clean}(T_{t})` `\triangleright` phase 2: normalize traces into canonical form

6:
  if `t\geq 2` then `\triangleright` phase 3: attribute prior manifest, then rollback

7:
   `V_{t}\leftarrow\textsc{Attribute}(C_{t-1},T_{t-1},T_{t})`

8:
   `H_{t-1}\leftarrow\textsc{Rollback}(H_{t-1},V_{t})`

9:
  else

10:
   `V_{t}\leftarrow\emptyset`

11:
  end if

12:
  `R_{t}\leftarrow\textsc{AgentDebugger}(\widetilde{T}_{t})` `\triangleright` phase 4: layered distillation

13:
  `(H_{t},C_{t})\leftarrow\textsc{Evolve}(H_{t-1},R_{t},V_{t})` `\triangleright` phase 5: workspace edits + new manifest

14:
  `\textsc{Commit}(H_{t},C_{t},t)` `\triangleright` phase 6: tag iteration in git

15:
  if `\textsc{Pass@1}(T_{t})>\textsc{Pass@1}(H_{\text{best}})` then `H_{\text{best}}\leftarrow H_{t}`

16:
  end if

17:
end for

18:
return `H_{\text{best}}`

Algorithm [1](https://arxiv.org/html/2604.25850#alg1 "Algorithm 1 ‣ 3.3 Evolve Agent: evidence-driven, auditable edits ‣ 3 Method ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses") composes the three substrates into one iteration: rollout, clean, attribute the prior manifest and revert rejected edits, distill, edit, commit.
We run `k\geq 2` rollouts per task so each task carries a pass-rate signal, which stabilizes pass@1 and lets partial-pass tasks anchor comparative diagnosis.
Attribution runs *before* distillation, so its verdict lands inside the evidence corpus and binds each prior manifest entry as a contract rather than a rationale.
A one-shot explore agent (Appendix [B.3](https://arxiv.org/html/2604.25850#A2.SS3 "B.3 Explore Agent Prompts ‣ Appendix B Prompts and Configurations ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses")) runs in parallel with iteration `1` to seed a small number of reusable skills from the NexAU source and public coding-agent references.
These skills receive no special protection: from iteration `2` onward the Evolve Agent may keep, refine, or remove them based on observed rollouts.

## 4 Experiments

We organize our empirical study around three questions: where AHE sits on the map of existing approaches to harness design, whether what it produces is portable beyond its optimization target, and what inside the loop drives the gain.

Research Questions

1.

RQ1 (§[4.2](https://arxiv.org/html/2604.25850#S4.SS2 "4.2 RQ1: Main Results ‣ 4 Experiments ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses")): Why agentic harness engineering, rather than human-engineered harnesses or other automated methods?
2.

RQ2 (§[4.3](https://arxiv.org/html/2604.25850#S4.SS3 "4.3 RQ2: Transfer to Unseen Tasks and Base Models ‣ 4 Experiments ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses")): Does agentic harness engineering overfit to its optimization target?
3.

RQ3 (§[4.4](https://arxiv.org/html/2604.25850#S4.SS4 "4.4 RQ3: Analysis ‣ 4 Experiments ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses")): What inside AHE drives its gains, and how reliable is the loop’s self-attribution?

### 4.1 Setup

### Evaluation.

We drive evolution on the full 89 tasks of Terminal-Bench 2 [[21](https://arxiv.org/html/2604.25850#bib.bib24)], split as 4 easy, 55 medium, and 30 hard, with per-task timeout extended to 1 hour. For cross-benchmark transfer we evaluate the AHE harness on SWE-bench-verified [[14](https://arxiv.org/html/2604.25850#bib.bib16)], 500 tasks across seven repositories.
We report two metrics per configuration: pass@1, the mean binary success rate over `k` rollouts per task; and tokens/trial, the mean per-trial total of prompt plus completion tokens across all LLM calls, in thousands. Infrastructure-aborted or timed-out trials count as failures under pass@1 (matching the official terminal-bench leaderboard) and are excluded from token means to avoid truncated figures. Runtime infrastructure (framework, dispatcher, sandbox, tracer, and concurrency) is detailed in Appendix [A](https://arxiv.org/html/2604.25850#A1 "Appendix A Experimental Setup: Full Details ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").

### Models.

For both the evolution loop and the main experiment of §[4.2](https://arxiv.org/html/2604.25850#S4.SS2 "4.2 RQ1: Main Results ‣ 4 Experiments ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"), all three role agents (the Code Agent, the Agent Debugger, and the Evolve Agent) share one base model, GPT-5.4 [[26](https://arxiv.org/html/2604.25850#bib.bib29)] at the high reasoning setting.
For cross-model transfer (§[4.3](https://arxiv.org/html/2604.25850#S4.SS3 "4.3 RQ2: Transfer to Unseen Tasks and Base Models ‣ 4 Experiments ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses")), we re-evaluate the Code Agent on five alternate bases: GPT-5.4 [[26](https://arxiv.org/html/2604.25850#bib.bib29)] at medium and xhigh reasoning, qwen-3.6-plus [[38](https://arxiv.org/html/2604.25850#bib.bib38), [44](https://arxiv.org/html/2604.25850#bib.bib44)], gemini-3.1-flash-lite-preview [[8](https://arxiv.org/html/2604.25850#bib.bib9)], and deepseek-v4-flash [[6](https://arxiv.org/html/2604.25850#bib.bib6)].

### 4.2 RQ1: Main Results

Table 1: Pass@1 on Terminal-Bench 2 across 89 tasks, by official difficulty. NexAU0 is the shared seed; ACE, Training-Free GRPO, and AHE are three self-evolution loops layered on top of it. Bold marks the best per column; ties are all bold.

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| Method | All | Easy | Med. | Hard |
|  | 89 | 4 | 55 | 30 |
| Human-designed harness | | | | |
| OpenCode | 47.2% | 75.0% | 52.7% | 33.3% |
| Terminus-2 | 62.9% | 75.0% | 74.5% | 40.0% |
| Codex | 71.9% | 75.0% | 80.0% | 56.7% |
| Self-evolved from NexAU0 | | | | |
| NexAU0 | 69.7% | 87.5% | 78.2% | 51.7% |
| ACE | 68.9% | 91.7% | 78.2% | 48.9% |
| TF-GRPO | 72.3% | 100.0% | 79.4% | 55.6% |
| AHE | 77.0% | 100.0% | 88.2% | 53.3% |

We run a single AHE campaign of ten iterations from the bash-only NexAU0 seed (§[3.1](https://arxiv.org/html/2604.25850#S3.SS1 "3.1 NexAU: an editable, decoupled harness substrate ‣ 3 Method ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses")) on Terminal-Bench 2, finishing in roughly 32 hours; the best resulting configuration is reported as AHE. The two self-evolve baselines ACE [[49](https://arxiv.org/html/2604.25850#bib.bib49)] and Training-Free GRPO (TF-GRPO) [[4](https://arxiv.org/html/2604.25850#bib.bib4)] start from the same NexAU0 seed.

### AHE outperforms both human-designed and self-evolve baselines.

AHE outperforms every baseline on our panel: three human-designed harnesses, OpenCode [[2](https://arxiv.org/html/2604.25850#bib.bib2)], Terminus-2 [[10](https://arxiv.org/html/2604.25850#bib.bib11)], and Codex [[25](https://arxiv.org/html/2604.25850#bib.bib28)], and the two self-evolve baselines.
Figure [1](https://arxiv.org/html/2604.25850#S0.F1 "Figure 1 ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses") shows the gain accumulates across iterations, with continued evolution pushing pass@1 further above the NexAU0 seed.
By difficulty, the only exception is the Hard tier, where AHE marginally trails Codex. We trace this gap to interference between AHE’s components on long-horizon tasks rather than to a missing capability: swapping AHE’s long-term memory alone into the NexAU0 seed, without the other AHE components, already surpasses Codex on Hard (§[4.4.1](https://arxiv.org/html/2604.25850#S4.SS4.SSS1 "4.4.1 RQ3a: where value accumulates across components ‣ 4.4 RQ3: Analysis ‣ 4 Experiments ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses")).

### Prompt-only self-evolution misses the components that carry AHE’s gain.

The gaps to ACE and TF-GRPO trace to a layer mismatch. ACE distills natural-language playbooks the agent reads in-context, and TF-GRPO is a trajectory-feedback variant of GRPO that reinforces successful tool sequences; neither method opens the surrounding scaffolding to edits.
AHE instead jointly evolves system prompt, tools, middleware, and long-term memory, and §[4.4.1](https://arxiv.org/html/2604.25850#S4.SS4.SSS1 "4.4.1 RQ3a: where value accumulates across components ‣ 4.4 RQ3: Analysis ‣ 4 Experiments ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses") shows the gain concentrates in the latter three components, exactly the layers ACE and TF-GRPO leave untouched.

### 4.3 RQ2: Transfer to Unseen Tasks and Base Models

AHE’s harness is evolved on Terminal-Bench 2 with GPT-5.4 high. We probe whether it encodes general coding-agent experience or overfits to that target by transferring the evolved harness unchanged, without further evolution, to two off-target settings: a different task surface (SWE-bench-verified) and three alternate base models.

Table 2: Cross-benchmark transfer on SWE-bench-verified. ACE, Training-Free GRPO (TF-GRPO), and AHE share the NexAU0 seed and differ only in their self-evolution loop; all four columns run on GPT-5.4. AHE and the two self-evolve baselines are evolved on Terminal-Bench 2 and evaluated without in-domain re-evolution. Per-column bold marks the best; ties are all bold.

|  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  | Success rate `\uparrow` | | | | Tokens k `\downarrow` | | | |
| Repo | `N` | ACE | TF-GRPO | NexAU0 | AHE | ACE | TF-GRPO | NexAU0 | AHE |
| All | 500 | 74.6% | 74.2% | 75.2% | 75.6% | 679 | 582 | 526 | 461 |
| django | 231 | 79.2% | 78.8% | 79.2% | 81.0% | 707 | 583 | 527 | 484 |
| sympy | 75 | 69.3% | 68.0% | 70.7% | 70.7% | 602 | 572 | 494 | 479 |
| sphinx-doc | 44 | 61.4% | 65.9% | 68.2% | 70.5% | 990 | 848 | 731 | 656 |
| matplotlib | 34 | 70.6% | 70.6% | 73.5% | 73.5% | 622 | 530 | 486 | 391 |
| scikit-learn | 32 | 93.8% | 93.8% | 93.8% | 87.5% | 451 | 378 | 307 | 257 |
| pydata | 22 | 77.3% | 77.3% | 77.3% | 72.7% | 563 | 516 | 386 | 338 |
| astropy | 22 | 59.1% | 59.1% | 54.5% | 50.0% | 546 | 470 | 667 | 277 |

### Cross-benchmark transfer.

We evaluate the AHE harness on SWE-bench-verified against the seed and the two self-evolve baselines (NexAU0, ACE, TF-GRPO) under identical infrastructure (Table [2](https://arxiv.org/html/2604.25850#S4.T2 "Table 2 ‣ 4.3 RQ2: Transfer to Unseen Tasks and Base Models ‣ 4 Experiments ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses")).

ACE and TF-GRPO both regress below the NexAU0 seed in aggregate success while spending `11\%` to `29\%` more tokens than the seed: the playbook ACE injects and the trajectory distribution TF-GRPO reinforces were distilled on Terminal-Bench 2 traces and ride the prompt at every model call, so on a different task surface that text adds cost without reshaping the underlying policy.

AHE instead achieves the highest aggregate, with the seed-relative gain concentrating on django and sphinx-doc, the two largest and most token-expensive repositories whose multi-step edit-and-verify loop matches the structure AHE’s tools, middleware, and long-term memory compress on Terminal-Bench 2.
Marginal regressions appear only on the three smallest repositories, consistent with pass@1 variance on small repos exceeding the per-repo gain.
AHE also cuts aggregate tokens by `32\%` against ACE, `21\%` against TF-GRPO, and `12\%` against the seed: encoding behavior in tools, middleware, and memory avoids the per-call re-derivation cost prompt-only baselines incur.

Figure 3: Cross-model transfer on Terminal-Bench 2, 89 tasks. The AHE workspace evolved on GPT-5.4 high is re-evaluated on each base without further evolution, paired against the NexAU0 seed on the same base. All bases gain over the seed, with cross-family bases gaining more than within-family ones.

### Cross-model transfer.

We re-evaluate both the NexAU0 seed and AHE on the five alternate bases listed in §[4.1](https://arxiv.org/html/2604.25850#S4.SS1 "4.1 Setup ‣ 4 Experiments ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"). Figure [3](https://arxiv.org/html/2604.25850#S4.F3 "Figure 3 ‣ Cross-benchmark transfer. ‣ 4.3 RQ2: Transfer to Unseen Tasks and Base Models ‣ 4 Experiments ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses") reports five positive pass@1 gains from `+2.3` to `+10.1` pp.

Cross-family gains dominate within-family ones: deepseek-v4-flash moves `+10.1` pp from `51.7\%` to `61.8\%`, qwen-3.6-plus `+6.3` pp from `56.2\%` to `62.5\%`, and gemini-3.1-flash-lite-preview `+5.1` pp from `36.5\%` to `41.6\%`, all above the `+2.3` pp on GPT-5.4 medium and xhigh. We read this as bases further from saturation leaning more on the coordination patterns AHE has fixed inside tools, middleware, and long-term memory, while a stronger base re-derives the same coordination from its prompt at low marginal cost.

Within one family the profile is non-monotone: `+2.3` pp on medium, `+7.3` pp on high from §[4.2](https://arxiv.org/html/2604.25850#S4.SS2 "4.2 RQ1: Main Results ‣ 4 Experiments ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"), and `+2.3` pp on xhigh. AHE’s step budget and per-task timeout were fitted to GPT-5.4 high during evolution; medium has more time-per-step slack but loses a reasoning tier of raw capability, while xhigh pushes more trials past the per-task timeout, which our pass@1 convention (§[4.1](https://arxiv.org/html/2604.25850#S4.SS1.SSS0.Px1 "Evaluation. ‣ 4.1 Setup ‣ 4 Experiments ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses")) counts as failures. Either direction discounts the gain.

The headline finding is that all five gains land positive: the AHE workspace is not specific to one provider’s idioms or one reasoning depth. Their magnitude tracks the evolution operating point rather than raw base capability, so we treat the timeout-budget coupling as a generalization hazard discussed in our [Limitations](https://arxiv.org/html/2604.25850#Sx1 "In Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses") section.

### 4.4 RQ3: Analysis

We analyze the loop along two architectural choices that §[3](https://arxiv.org/html/2604.25850#S3 "3 Method ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses") places weight on: decomposed components (§[4.4.1](https://arxiv.org/html/2604.25850#S4.SS4.SSS1 "4.4.1 RQ3a: where value accumulates across components ‣ 4.4 RQ3: Analysis ‣ 4 Experiments ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses")) and self-declared attribution (§[4.4.2](https://arxiv.org/html/2604.25850#S4.SS4.SSS2 "4.4.2 RQ3b: how reliably the loop’s self-attribution tracks reality ‣ 4.4 RQ3: Analysis ‣ 4 Experiments ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses")).

### 4.4.1 RQ3a: where value accumulates across components

Table [3](https://arxiv.org/html/2604.25850#S4.T3 "Table 3 ‣ 4.4.1 RQ3a: where value accumulates across components ‣ 4.4 RQ3: Analysis ‣ 4 Experiments ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses") decomposes the AHE gain at the component level by isolating one of the four evolved layers, long-term memory, tools, middleware, or system prompt, while holding the other three at their seed defaults. Three of the four single-component variants outperform the seed; the system-prompt swap is the only regression.

Table 3: Component-level ablations on Terminal-Bench 2. Each “+ X only” row swaps a single AHE component into the NexAU0 seed; per-column best is bolded. Most single-component swaps already beat the seed, and the single-component gains overshoot full AHE’s aggregate, indicating components interact non-additively rather than stacking cleanly.

| Variant | All | Easy | Medium | Hard |
| --- | --- | --- | --- | --- |
|  | 89 tasks | 4 tasks | 55 tasks | 30 tasks |
| NexAU0 | 69.7% | 87.5% | 78.2% | 51.7% |
| + memory only | 75.3% | 50.0% | 83.6% | 63.3% |
| + tool only | 73.0% | 75.0% | 87.3% | 46.7% |
| + middleware only | 71.9% | 100.0% | 81.8% | 50.0% |
| + system_prompt only | 67.4% | 75.0% | 78.2% | 46.7% |
| AHE full | 77.0% | 100.0% | 88.2% | 53.3% |

### Each component owns a different failure surface.

Memory adds 12 boundary-case lessons (performance margin, queued-over-limit cancellation, evaluator-style closure, source-packaging layout); on Hard the lessons lift it above full AHE, while on Easy they reduce to superfluous re-verification.
Tools become a 1364-line shell that auto-surfaces contract hints from files near each command; on Medium it lands within `0.9` pp of full AHE, while on Hard a built-in publish guard closes the loop too early.
Middleware adds a finish-hook that forces one evaluator-isomorphic closure check; on Easy it clears every task, while on Hard it inflates turn count.
The system prompt encodes 79 lines of universal discipline whose executability depends on the other three; inserted alone it scores `-2.3` pp aggregate.

### Components interact non-additively, capping the aggregate gain.

The three positive single-component gains sum to `+11.1` pp against full AHE’s `+7.3` pp, and on Hard the memory-only variant exceeds full AHE: memory, middleware, and the system prompt all push toward the same closure-style verification, so stacking them spends turns on redundant re-checks within the long-horizon budget.
Since the evolve agent optimises an aggregate dominated by 55 Medium tasks, it converges to a Medium-heavy trade-off that returns part of the Hard memory effect, and we leave interaction-aware evolution to future work.

### 4.4.2 RQ3b: how reliably the loop’s self-attribution tracks reality

Each evolution round, our evolve model produces a change manifest naming which Terminal-Bench 2 tasks it expects to fix in the next round and which it flags at risk of regression. We compare the round-`N{-}1` prediction against the round-`N` ground truth, computing standard precision and recall over the 89 tasks separately for fixes and regressions.

### Evidence-driven targeting.

The fix panel of [Figure 4](https://arxiv.org/html/2604.25850#S4.F4 "In Evidence-driven targeting. ‣ 4.4.2 RQ3b: how reliably the loop’s self-attribution tracks reality ‣ 4.4 RQ3: Analysis ‣ 4 Experiments ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses") shows the evolve model’s targeting is evidence-driven rather than guesswork. Cross-iteration fix-precision of 33.7% and fix-recall of 51.4% sit roughly 5x above the random-prediction baselines of 6.5% and 10.6%, so each harness edit lands on a real, agent-anticipated target rather than on an arbitrary subset of the panel.

Figure 4: Cross-iteration mean precision and recall of the evolve model’s self-predictions across 9 evaluation rounds of the GPT-5.4 AHE loop on Terminal-Bench 2, alongside the random-prediction baseline. Left: fix predictions. Right: regression predictions.

### Regression blindness.

The regression panel tells the opposite story: cross-iteration regression-precision of 11.8% and regression-recall of 11.1% sit only about 2x above their random baselines of 5.6% and 5.4%, so most upcoming regressions go unforeseen. The agent can justify why an edit should help, but it cannot reliably name the tasks the same edit is about to break, which is what produces the non-monotone steps in the evolution curve of §[4.2](https://arxiv.org/html/2604.25850#S4.SS2 "4.2 RQ1: Main Results ‣ 4 Experiments ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"). Closing this gap is the clearest direction for future self-evolution loops. Appendix [D](https://arxiv.org/html/2604.25850#A4 "Appendix D Per-round Self-attribution Breakdown ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses") gives the per-round breakdown.

## 5 Conclusion

We introduced Agentic Harness Engineering (AHE), an observability-driven loop that turns a coding agent’s harness into a learnable adaptation surface while the base model remains fixed. AHE exposes components as files, distills rollouts into a layered evidence corpus, and binds each edit to a falsifiable next-round prediction; ten iterations lift pass@1 on Terminal-Bench 2 from 69.7% to 77.0%, and the frozen harness transfers to SWE-bench-verified and three alternate model families. We see harness-level evolution as a complementary axis to model-side training: an externalized, auditable surface where coding-agent experience can accumulate.

## Limitations

This work studies a promising but high-variance setting, and the scope of our claims should be interpreted accordingly.

### Benchmark scope.

Our evaluation drives evolution on Terminal-Bench 2 and probes transfer on SWE-bench-verified. Even though the frozen harness transfers to a second task surface and to three alternate base-model families, broader programming languages, repository-scale deployments, and human-in-the-loop workflows remain untested.

### Evolution operating point.

AHE’s step budget and per-task timeout were fitted to GPT-5.4 high during evolution, so cross-model transfer numbers conflate harness portability with operating-point coupling—within one family the gain is non-monotone across reasoning tiers (§[4.3](https://arxiv.org/html/2604.25850#S4.SS3 "4.3 RQ2: Transfer to Unseen Tasks and Base Models ‣ 4 Experiments ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses")). Untangling these factors will require re-running the loop under multiple operating points.

### Self-modification governance.

AHE bounds edits to a workspace, attributes every change in a versioned manifest, and rolls back ineffective edits at file granularity, but it does not provide a complete guardrail stack. Long-horizon harness cleanup and stronger misuse prevention remain incomplete, and AHE should be viewed as a controlled research prototype rather than a fully mature autonomous self-improvement system.

## References

- [1]
  L. A. Agrawal, S. Tan, D. Soylu, N. Ziems, R. Khare, K. Opsahl-Ong, A. Singhvi, H. Shandilya, M. J. Ryan, M. Jiang, C. Potts, K. Sen, A. Dimakis, I. Stoica, D. Klein, M. Zaharia, and O. Khattab (2025)
  GEPA: reflective prompt evolution can outperform reinforcement learning.
  In The Fourteenth International Conference on Learning Representations,
  External Links: [Link](https://openreview.net/forum?id=RQm2KQTM5r)
  Cited by: [§1](https://arxiv.org/html/2604.25850#S1.p3.1 "1 Introduction ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"),
  [§2.2](https://arxiv.org/html/2604.25850#S2.SS2.p1.1 "2.2 Automated Optimization of LLM Agents ‣ 2 Related Work ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [2]
  Anomaly (2025)
  Opencode: the open source coding agent..
  External Links: [Link](https://github.com/anomalyco/opencode)
  Cited by: [§4.2](https://arxiv.org/html/2604.25850#S4.SS2.SSS0.Px1.p1.1 "AHE outperforms both human-designed and self-evolve baselines. ‣ 4.2 RQ1: Main Results ‣ 4 Experiments ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [3]
  Anthropic (2025)
  Claude-code.
  External Links: [Link](https://github.com/anthropics/claude-code)
  Cited by: [§2.1](https://arxiv.org/html/2604.25850#S2.SS1.p1.1 "2.1 Harness Engineering and Evaluation for Coding Agents ‣ 2 Related Work ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [4]
  Y. Cai, S. Cai, Y. Shi, Z. Xu, L. Chen, Y. Qin, X. Tan, G. Li, Z. Li, H. Lin, Y. Mao, K. Li, and X. Sun (2025)
  Training-free group relative policy optimization.
   arXiv.
  External Links: 2510.08191,
  [Document](https://dx.doi.org/10.48550/arXiv.2510.08191),
  [Link](http://arxiv.org/abs/2510.08191)
  Cited by: [§1](https://arxiv.org/html/2604.25850#S1.p3.1 "1 Introduction ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"),
  [§1](https://arxiv.org/html/2604.25850#S1.p5.1 "1 Introduction ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"),
  [§2.2](https://arxiv.org/html/2604.25850#S2.SS2.p1.1 "2.2 Automated Optimization of LLM Agents ‣ 2 Related Work ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"),
  [§4.2](https://arxiv.org/html/2604.25850#S4.SS2.p1.1 "4.2 RQ1: Main Results ‣ 4 Experiments ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [5]
  J. S. Chan, N. Chowdhury, O. Jaffe, J. Aung, D. Sherburn, E. Mays, G. Starace, K. Liu, L. Maksin, T. Patwardhan, A. Madry, and L. Weng (2024)
  MLE-bench: evaluating machine learning agents on machine learning engineering.
  In The Thirteenth International Conference on Learning Representations,
  External Links: [Link](https://openreview.net/forum?id=6s5uXNWGIh)
  Cited by: [§2.1](https://arxiv.org/html/2604.25850#S2.SS1.p2.1 "2.1 Harness Engineering and Evaluation for Coding Agents ‣ 2 Related Work ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [6]
  DeepSeek-AI (2026)
  DeepSeek-v4: towards highly efficient million-token context intelligence.
  External Links: [Link](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/DeepSeek_V4.pdf)
  Cited by: [§1](https://arxiv.org/html/2604.25850#S1.p2.1 "1 Introduction ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"),
  [§4.1](https://arxiv.org/html/2604.25850#S4.SS1.SSS0.Px2.p1.1 "Models. ‣ 4.1 Setup ‣ 4 Experiments ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [7]
  X. Deng, J. Da, E. Pan, Y. Y. He, C. Ide, K. Garg, N. Lauffer, A. Park, C. Rane, K. Sampath, M. Krishnan, S. R. Kundurthy, S. M. Hendryx, Z. Wang, C. B. C. Zhang, N. Jacobson, B. Liu, and B. Kenstler (2025)
  SWE-bench pro: can ai agents solve long-horizon software engineering tasks?.
  External Links: [Link](https://openreview.net/forum?id=9R2iUHhVfr)
  Cited by: [§1](https://arxiv.org/html/2604.25850#S1.p1.1 "1 Introduction ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"),
  [§2.1](https://arxiv.org/html/2604.25850#S2.SS1.p2.1 "2.1 Harness Engineering and Evaluation for Coding Agents ‣ 2 Related Work ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [8]
  Google (2026)
  Gemini-3-1-flash-lite-model-card.
  External Links: [Link](https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-1-Flash-Lite-Model-Card.pdf)
  Cited by: [§4.1](https://arxiv.org/html/2604.25850#S4.SS1.SSS0.Px2.p1.1 "Models. ‣ 4.1 Setup ‣ 4 Experiments ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [9]
  H. Guo, K. Lv, Q. Guo, T. Liang, Z. Xi, D. Song, Q. Zhang, Y. Sun, K. Chen, X. Qiu, and T. Gui (2025)
  CritiQ: mining data quality criteria from human preferences.
  In Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), W. Che, J. Nabende, E. Shutova, and M. T. Pilehvar (Eds.),
  Vienna, Austria, pp. 16240–16261.
  External Links: [Document](https://dx.doi.org/10.18653/v1/2025.acl-long.792),
  [Link](https://aclanthology.org/2025.acl-long.792/),
  ISBN 979-8-89176-251-0
  Cited by: [§2.2](https://arxiv.org/html/2604.25850#S2.SS2.p1.1 "2.2 Automated Optimization of LLM Agents ‣ 2 Related Work ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [10]
  Harbor (2026)
  Terminus-2.
  External Links: [Link](https://www.harborframework.com/docs/agents/terminus-2)
  Cited by: [§4.2](https://arxiv.org/html/2604.25850#S4.SS2.SSS0.Px1.p1.1 "AHE outperforms both human-designed and self-evolve baselines. ‣ 4.2 RQ1: Main Results ‣ 4 Experiments ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [11]
  S. Hu, C. Lu, and J. Clune (2024)
  Automated design of agentic systems.
  In The Thirteenth International Conference on Learning Representations,
  External Links: [Link](https://openreview.net/forum?id=t9U3LW7JVX)
  Cited by: [§2.2](https://arxiv.org/html/2604.25850#S2.SS2.p1.1 "2.2 Automated Optimization of LLM Agents ‣ 2 Related Work ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [12]
  N. Jain, K. Han, A. Gu, W. Li, F. Yan, T. Zhang, S. Wang, A. Solar-Lezama, K. Sen, and I. Stoica (2024)
  LiveCodeBench: holistic and contamination free evaluation of large language models for code.
  In The Thirteenth International Conference on Learning Representations,
  External Links: [Link](https://openreview.net/forum?id=chfJJYC3iL)
  Cited by: [§2.1](https://arxiv.org/html/2604.25850#S2.SS1.p2.1 "2.1 Harness Engineering and Evaluation for Coding Agents ‣ 2 Related Work ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [13]
  N. Jain, J. Singh, M. Shetty, T. Zhang, L. Zheng, K. Sen, and I. Stoica (2025)
  R2E-gym: procedural environment generation and hybrid verifiers for scaling open-weights swe agents.
  In Second Conference on Language Modeling,
  External Links: [Link](https://openreview.net/forum?id=7evvwwdo3z#discussion)
  Cited by: [§2.1](https://arxiv.org/html/2604.25850#S2.SS1.p2.1 "2.1 Harness Engineering and Evaluation for Coding Agents ‣ 2 Related Work ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [14]
  C. E. Jimenez, J. Yang, A. Wettig, S. Yao, K. Pei, O. Press, and K. R. Narasimhan (2023)
  SWE-bench: can language models resolve real-world github issues?.
  In The Twelfth International Conference on Learning Representations,
  External Links: [Link](https://openreview.net/forum?id=VTF8yNQM66)
  Cited by: [§1](https://arxiv.org/html/2604.25850#S1.p1.1 "1 Introduction ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"),
  [§1](https://arxiv.org/html/2604.25850#S1.p5.1 "1 Introduction ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"),
  [§2.1](https://arxiv.org/html/2604.25850#S2.SS1.p2.1 "2.1 Harness Engineering and Evaluation for Coding Agents ‣ 2 Related Work ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"),
  [§4.1](https://arxiv.org/html/2604.25850#S4.SS1.SSS0.Px1.p1.1 "Evaluation. ‣ 4.1 Setup ‣ 4 Experiments ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [15]
  O. Khattab, A. Singhvi, P. Maheshwari, Z. Zhang, K. Santhanam, S. Vardhamanan, S. Haq, A. Sharma, T. T. Joshi, H. Moazam, H. Miller, M. Zaharia, and C. Potts (2023)
  DSPy: compiling declarative language model calls into self-improving pipelines.
   arXiv.
  External Links: 2310.03714,
  [Document](https://dx.doi.org/10.48550/arXiv.2310.03714),
  [Link](http://arxiv.org/abs/2310.03714)
  Cited by: [§2.2](https://arxiv.org/html/2604.25850#S2.SS2.p1.1 "2.2 Automated Optimization of LLM Agents ‣ 2 Related Work ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [16]
  Y. Lee, R. Nair, Q. Zhang, K. Lee, O. Khattab, and C. Finn (2026)
  Meta-harness: end-to-end optimization of model harnesses.
   arXiv.
  External Links: 2603.28052,
  [Document](https://dx.doi.org/10.48550/arXiv.2603.28052),
  [Link](http://arxiv.org/abs/2603.28052)
  Cited by: [§1](https://arxiv.org/html/2604.25850#S1.p3.1 "1 Introduction ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [17]
  L. Lin (2026)
  Agent debugger: understanding agent trajectory with agentic workflows - dawning road.
  External Links: [Link](https://dawning-road.github.io/blog/agent-debugger)
  Cited by: [§3.2](https://arxiv.org/html/2604.25850#S3.SS2.p1.1 "3.2 Agent Debugger: layered trajectory evidence ‣ 3 Method ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [18]
  R. Lopopolo (2026)
  Harness engineering: leveraging codex in an agent-first world.
  External Links: [Link](https://openai.com/zh-Hans-CN/index/harness-engineering/)
  Cited by: [§1](https://arxiv.org/html/2604.25850#S1.p1.1 "1 Introduction ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"),
  [§2.1](https://arxiv.org/html/2604.25850#S2.SS1.p1.1 "2.1 Harness Engineering and Evaluation for Coding Agents ‣ 2 Related Work ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [19]
  Z. Ma, S. Yang, Y. Ji, X. Wang, Y. Wang, Y. Hu, T. Huang, and X. Chu (2026)
  SkillClaw: let skills evolve collectively with agentic evolver.
   arXiv.
  External Links: 2604.08377,
  [Document](https://dx.doi.org/10.48550/arXiv.2604.08377),
  [Link](http://arxiv.org/abs/2604.08377)
  Cited by: [§1](https://arxiv.org/html/2604.25850#S1.p3.1 "1 Introduction ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [20]
  A. Madaan, N. Tandon, P. Gupta, S. Hallinan, L. Gao, S. Wiegreffe, U. Alon, N. Dziri, S. Prabhumoye, Y. Yang, S. Gupta, B. P. Majumder, K. Hermann, S. Welleck, A. Yazdanbakhsh, and P. Clark (2023)
  Self-refine: iterative refinement with self-feedback.
  In Thirty-Seventh Conference on Neural Information Processing Systems,
  External Links: [Link](https://openreview.net/forum?id=S37hOerQLB)
  Cited by: [§1](https://arxiv.org/html/2604.25850#S1.p3.1 "1 Introduction ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"),
  [§2.2](https://arxiv.org/html/2604.25850#S2.SS2.p1.1 "2.2 Automated Optimization of LLM Agents ‣ 2 Related Work ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [21]
  M. A. Merrill, A. G. Shaw, N. Carlini, B. Li, H. Raj, I. Bercovich, L. Shi, J. Y. Shin, T. Walshe, E. K. Buchanan, J. Shen, G. Ye, H. Lin, J. Poulos, M. Wang, M. Nezhurina, J. Jitsev, D. Lu, O. M. Mastromichalakis, Z. Xu, Z. Chen, Y. Liu, R. Zhang, L. L. Chen, A. Kashyap, J. Uslu, J. Li, J. Wu, M. Yan, S. Bian, V. Sharma, K. Sun, S. Dillmann, A. Anand, A. Lanpouthakoun, B. Koopah, C. Hu, E. Guha, G. H. S. Dreiman, J. Zhu, K. Krauth, L. Zhong, N. Muennighoff, R. Amanfu, S. Tan, S. Pimpalgaonkar, T. Aggarwal, X. Lin, X. Lan, X. Zhao, Y. Liang, Y. Wang, Z. Wang, C. Zhou, D. Heineman, H. Liu, H. Trivedi, J. Yang, J. Lin, M. Shetty, M. Yang, N. Omi, N. Raoof, S. Li, T. Y. Zhuo, W. Lin, Y. Dai, Y. Wang, W. Chai, S. Zhou, D. Wahdany, Z. She, J. Hu, Z. Dong, Y. Zhu, S. Cui, A. Saiyed, A. Kolbeinsson, J. Hu, C. M. Rytting, R. Marten, Y. Wang, A. Dimakis, A. Konwinski, and L. Schmidt (2026)
  Terminal-bench: benchmarking agents on hard, realistic tasks in command line interfaces.
   arXiv.
  External Links: 2601.11868,
  [Document](https://dx.doi.org/10.48550/arXiv.2601.11868),
  [Link](http://arxiv.org/abs/2601.11868)
  Cited by: [§1](https://arxiv.org/html/2604.25850#S1.p1.1 "1 Introduction ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"),
  [§1](https://arxiv.org/html/2604.25850#S1.p5.1 "1 Introduction ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"),
  [§2.1](https://arxiv.org/html/2604.25850#S2.SS1.p2.1 "2.1 Harness Engineering and Evaluation for Coding Agents ‣ 2 Related Work ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"),
  [§4.1](https://arxiv.org/html/2604.25850#S4.SS1.SSS0.Px1.p1.1 "Evaluation. ‣ 4.1 Setup ‣ 4 Experiments ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [22]
  S. Miserendino, M. Wang, T. Patwardhan, and J. Heidecke (2025)
  SWE-lancer: can frontier llms earn $1 million from real-world freelance software engineering?.
  In Forty-Second International Conference on Machine Learning,
  External Links: [Link](https://openreview.net/forum?id=xZXhFg43EI)
  Cited by: [§2.1](https://arxiv.org/html/2604.25850#S2.SS1.p2.1 "2.1 Harness Engineering and Evaluation for Coding Agents ‣ 2 Related Work ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [23]
  Nex-AGI (2025)
  NexAU (au for agent universe), a general-purpose agent framework for building intelligent agents with tool capabilities..
  External Links: [Link](https://github.com/nex-agi/NexAU)
  Cited by: [§3.1](https://arxiv.org/html/2604.25850#S3.SS1.p1.1 "3.1 NexAU: an editable, decoupled harness substrate ‣ 3 Method ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [24]
  A. Novikov, N. Vũ, M. Eisenberger, E. Dupont, P. Huang, A. Z. Wagner, S. Shirobokov, B. Kozlovskii, F. J. R. Ruiz, A. Mehrabian, M. P. Kumar, A. See, S. Chaudhuri, G. Holland, A. Davies, S. Nowozin, P. Kohli, and M. Balog (2025)
  AlphaEvolve: a coding agent for scientific and algorithmic discovery.
   arXiv.
  External Links: 2506.13131,
  [Document](https://dx.doi.org/10.48550/arXiv.2506.13131),
  [Link](http://arxiv.org/abs/2506.13131)
  Cited by: [§2.2](https://arxiv.org/html/2604.25850#S2.SS2.p1.1 "2.2 Automated Optimization of LLM Agents ‣ 2 Related Work ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [25]
  OpenAI (2025)
  Codex cli.
  External Links: [Link](https://developers.openai.com/codex/cli)
  Cited by: [§1](https://arxiv.org/html/2604.25850#S1.p5.1 "1 Introduction ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"),
  [§4.2](https://arxiv.org/html/2604.25850#S4.SS2.SSS0.Px1.p1.1 "AHE outperforms both human-designed and self-evolve baselines. ‣ 4.2 RQ1: Main Results ‣ 4 Experiments ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [26]
  OpenAI (2026)
  Introducing gpt-5.4.
  External Links: [Link](https://openai.com/index/introducing-gpt-5-4/)
  Cited by: [§4.1](https://arxiv.org/html/2604.25850#S4.SS1.SSS0.Px2.p1.1 "Models. ‣ 4.1 Setup ‣ 4 Experiments ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [27]
  K. Opsahl-Ong, M. J. Ryan, J. Purtell, D. Broman, C. Potts, M. Zaharia, and O. Khattab (2024)
  Optimizing instructions and demonstrations for multi-stage language model programs.
  In Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing, Y. Al-Onaizan, M. Bansal, and Y. Chen (Eds.),
  Miami, Florida, USA, pp. 9340–9366.
  External Links: [Document](https://dx.doi.org/10.18653/v1/2024.emnlp-main.525),
  [Link](https://aclanthology.org/2024.emnlp-main.525/)
  Cited by: [§2.2](https://arxiv.org/html/2604.25850#S2.SS2.p1.1 "2.2 Automated Optimization of LLM Agents ‣ 2 Related Work ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [28]
  J. Pan, X. Wang, G. Neubig, N. Jaitly, H. Ji, A. Suhr, and Y. Zhang (2025)
  Training software engineering agents and verifiers with swe-gym.
  In Forty-Second International Conference on Machine Learning,
  External Links: [Link](https://openreview.net/forum?id=Cq1BNvHx74)
  Cited by: [§2.1](https://arxiv.org/html/2604.25850#S2.SS1.p2.1 "2.1 Harness Engineering and Evaluation for Coding Agents ‣ 2 Related Work ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [29]
  P. Rajasekaran, E. Dixon, C. Ryan, J. Hadfield, R. Ayub, H. Moran, C. Rueb, C. Jennings, M. Vorwerck, S. Ritchie, and M. Vo (2025)
  Effective context engineering for ai agents.
  External Links: [Link](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
  Cited by: [§3.2](https://arxiv.org/html/2604.25850#S3.SS2.p2.1 "3.2 Agent Debugger: layered trajectory evidence ‣ 3 Method ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [30]
  P. Rajasekaran (2026)
  Harness design for long-running application development.
  External Links: [Link](https://www.anthropic.com/engineering/harness-design-long-running-apps)
  Cited by: [§1](https://arxiv.org/html/2604.25850#S1.p1.1 "1 Introduction ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"),
  [§2.1](https://arxiv.org/html/2604.25850#S2.SS1.p1.1 "2.1 Harness Engineering and Evaluation for Coding Agents ‣ 2 Related Work ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [31]
  N. Research (2026)
  Hermes agent — the agent that grows with you.
  External Links: [Link](https://hermes-agent.nousresearch.com/)
  Cited by: [§1](https://arxiv.org/html/2604.25850#S1.p1.1 "1 Introduction ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"),
  [§2.1](https://arxiv.org/html/2604.25850#S2.SS1.p1.1 "2.1 Harness Engineering and Evaluation for Coding Agents ‣ 2 Related Work ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [32]
  N. Shinn, F. Cassano, A. Gopinath, K. R. Narasimhan, and S. Yao (2023)
  Reflexion: language agents with verbal reinforcement learning.
  In Thirty-Seventh Conference on Neural Information Processing Systems,
  External Links: [Link](https://openreview.net/forum?id=vAElhFcKW6)
  Cited by: [§1](https://arxiv.org/html/2604.25850#S1.p3.1 "1 Introduction ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"),
  [§2.2](https://arxiv.org/html/2604.25850#S2.SS2.p1.1 "2.2 Automated Optimization of LLM Agents ‣ 2 Related Work ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [33]
  P. Steinberger (2026)
  OpenClaw — personal ai assistant.
  External Links: [Link](https://openclaw.ai/)
  Cited by: [§1](https://arxiv.org/html/2604.25850#S1.p1.1 "1 Introduction ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"),
  [§1](https://arxiv.org/html/2604.25850#S1.p2.1 "1 Introduction ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"),
  [§2.1](https://arxiv.org/html/2604.25850#S2.SS1.p1.1 "2.1 Harness Engineering and Evaluation for Coding Agents ‣ 2 Related Work ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [34]
  R. Sutton (2019)
  The bitter lesson.
  External Links: [Link](https://www.cs.utexas.edu/~eunsol/courses/data/bitter_lesson.pdf)
  Cited by: [§1](https://arxiv.org/html/2604.25850#S1.p4.1 "1 Introduction ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [35]
  K. Team, T. Bai, Y. Bai, Y. Bao, S. H. Cai, Y. Cao, Y. Charles, H. S. Che, C. Chen, G. Chen, H. Chen, J. Chen, J. Chen, J. Chen, J. Chen, K. Chen, L. Chen, R. Chen, X. Chen, Y. Chen, Y. Chen, Y. Chen, Y. Chen, Y. Chen, Y. Chen, Y. Chen, Y. Chen, Z. Chen, Z. Chen, D. Cheng, M. Chu, J. Cui, J. Deng, M. Diao, H. Ding, M. Dong, M. Dong, Y. Dong, Y. Dong, A. Du, C. Du, D. Du, L. Du, Y. Du, Y. Fan, S. Fang, Q. Feng, Y. Feng, G. Fu, K. Fu, H. Gao, T. Gao, Y. Ge, S. Geng, C. Gong, X. Gong, Z. Gongque, Q. Gu, X. Gu, Y. Gu, L. Guan, Y. Guo, X. Hao, W. He, W. He, Y. He, C. Hong, H. Hu, J. Hu, Y. Hu, Z. Hu, K. Huang, R. Huang, W. Huang, Z. Huang, T. Jiang, Z. Jiang, X. Jin, Y. Jing, G. Lai, A. Li, C. Li, C. Li, F. Li, G. Li, G. Li, H. Li, H. Li, J. Li, J. Li, J. Li, L. Li, M. Li, W. Li, W. Li, X. Li, X. Li, Y. Li, Y. Li, Y. Li, Y. Li, Z. Li, Z. Li, W. Liao, J. Lin, X. Lin, Z. Lin, Z. Lin, C. Liu, C. Liu, H. Liu, L. Liu, S. Liu, S. Liu, S. Liu, T. Liu, T. Liu, W. Liu, X. Liu, Y. Liu, Y. Liu, Y. Liu, Y. Liu, Y. Liu, Z. Liu, Z. Liu, E. Lu, H. Lu, Z. Lu, J. Luo, T. Luo, Y. Luo, L. Ma, Y. Ma, S. Mao, Y. Mei, X. Men, F. Meng, Z. Meng, Y. Miao, M. Ni, K. Ouyang, S. Pan, B. Pang, Y. Qian, R. Qin, Z. Qin, J. Qiu, B. Qu, Z. Shang, Y. Shao, T. Shen, Z. Shen, J. Shi, L. Shi, S. Shi, F. Song, P. Song, T. Song, X. Song, H. Su, J. Su, Z. Su, L. Sui, J. Sun, J. Sun, T. Sun, F. Sung, Y. Tai, C. Tang, H. Tang, X. Tang, Z. Tang, J. Tao, S. Teng, C. Tian, P. Tian, A. Wang, B. Wang, C. Wang, C. Wang, C. Wang, D. Wang, D. Wang, D. Wang, F. Wang, H. Wang, H. Wang, H. Wang, H. Wang, H. Wang, J. Wang, J. Wang, J. Wang, K. Wang, L. Wang, Q. Wang, S. Wang, S. Wang, S. Wang, W. Wang, X. Wang, X. Wang, Y. Wang, Y. Wang, Y. Wang, Y. Wang, Y. Wang, Y. Wang, Z. Wang, Z. Wang, Z. Wang, Z. Wang, Z. Wang, Z. Wang, C. Wei, M. Wei, C. Wen, Z. Wen, C. Wu, H. Wu, J. Wu, R. Wu, W. Wu, Y. Wu, Y. Wu, Y. Wu, Z. Wu, C. Xiao, J. Xie, X. Xie, Y. Xie, Y. Xin, B. Xing, B. Xu, J. Xu, J. Xu, J. Xu, L. H. Xu, L. Xu, S. Xu, W. Xu, X. Xu, X. Xu, Y. Xu, Y. Xu, Y. Xu, Z. Xu, Z. Xu, J. Yan, Y. Yan, G. Yang, H. Yang, J. Yang, K. Yang, N. Yang, R. Yang, X. Yang, X. Yang, Y. Yang, Y. Yang, Y. Yang, Z. Yang, Z. Yang, Z. Yang, H. Yao, D. Ye, W. Ye, Z. Ye, B. Yin, C. Yu, L. Yu, T. Yu, T. Yu, E. Yuan, M. Yuan, X. Yuan, Y. Yue, W. Zeng, D. Zha, H. Zhan, D. Zhang, H. Zhang, J. Zhang, P. Zhang, Q. Zhang, R. Zhang, X. Zhang, Y. Zhang, Y. Zhang, Y. Zhang, Y. Zhang, Y. Zhang, Y. Zhang, Y. Zhang, Y. Zhang, Y. Zhang, Y. Zhang, Z. Zhang, C. Zhao, F. Zhao, J. Zhao, S. Zhao, X. Zhao, Y. Zhao, Z. Zhao, H. Zheng, R. Zheng, S. Zheng, T. Zheng, J. Zhong, L. Zhong, W. Zhong, M. Zhou, R. Zhou, X. Zhou, Z. Zhou, J. Zhu, L. Zhu, X. Zhu, Y. Zhu, Z. Zhu, J. Zhuang, W. Zhuang, Y. Zou, and X. Zu (2026)
  Kimi k2.5: visual agentic intelligence.
   arXiv.
  External Links: 2602.02276,
  [Document](https://dx.doi.org/10.48550/arXiv.2602.02276),
  [Link](http://arxiv.org/abs/2602.02276)
  Cited by: [§1](https://arxiv.org/html/2604.25850#S1.p2.1 "1 Introduction ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [36]
  K. Team (2026)
  Kimi k2.6 tech blog: advancing open-source coding.
  External Links: [Link](https://www.kimi.com/blog/kimi-k2-6)
  Cited by: [§1](https://arxiv.org/html/2604.25850#S1.p2.1 "1 Introduction ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [37]
  N. Team, Y. Cai, L. Chen, Q. Chen, Y. Ding, L. Fan, W. Fu, Y. Gao, H. Guo, P. Guo, Z. Han, Z. He, H. Hu, K. Hu, S. Hua, T. Huai, B. Huang, L. Ji, Z. Jiang, Z. Lei, B. Li, J. Lin, L. Lin, J. Liu, S. Liu, Z. Liu, Y. Ni, P. Qian, Y. Shen, Q. Shi, W. Shu, P. Sun, Y. Suo, T. Tang, B. Tian, G. Wang, J. Wang, P. Wang, Z. Xi, H. Yan, J. Yang, Z. Yang, T. Yao, G. Ye, Q. Yu, S. Zhang, X. Zhang, Y. Zhang, J. Zhao, M. Zheng, R. Zheng, E. Zhou, J. Zhou, M. Zhou, Y. Zhou, T. Gui, Y. Zheng, X. Chen, J. Zhou, S. Feng, Q. Chen, L. He, Q. Zhang, X. Huang, and X. Qiu (2025)
  Nex-n1: agentic models trained via a unified ecosystem for large-scale environment construction.
   arXiv.
  External Links: 2512.04987,
  [Document](https://dx.doi.org/10.48550/arXiv.2512.04987),
  [Link](http://arxiv.org/abs/2512.04987)
  Cited by: [§3.1](https://arxiv.org/html/2604.25850#S3.SS1.p1.1 "3.1 NexAU: an editable, decoupled harness substrate ‣ 3 Method ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [38]
  Q. Team (2026)
  Qwen3.6-plus: towards real world agents.
  External Links: [Link](https://qwenlm.github.io/blog/qwen3.6/)
  Cited by: [§1](https://arxiv.org/html/2604.25850#S1.p2.1 "1 Introduction ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"),
  [§4.1](https://arxiv.org/html/2604.25850#S4.SS1.SSS0.Px2.p1.1 "Models. ‣ 4.1 Setup ‣ 4 Experiments ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [39]
  X. M. Team (2026)
  MiMo-v2.5-pro.
  External Links: [Link](https://huggingface.co/XiaomiMiMo/MiMo-V2.5-Pro)
  Cited by: [§1](https://arxiv.org/html/2604.25850#S1.p2.1 "1 Introduction ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [40]
  V. Trivedy (2026)
  Improving deep agents with harness engineering.
  External Links: [Link](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering)
  Cited by: [§1](https://arxiv.org/html/2604.25850#S1.p2.1 "1 Introduction ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"),
  [§2.1](https://arxiv.org/html/2604.25850#S2.SS1.p1.1 "2.1 Harness Engineering and Evaluation for Coding Agents ‣ 2 Related Work ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [41]
  G. Wang, Y. Xie, Y. Jiang, A. Mandlekar, C. Xiao, Y. Zhu, L. Fan, and A. Anandkumar (2023)
  Voyager: an open-ended embodied agent with large language models.
   arXiv.
  External Links: 2305.16291,
  [Document](https://dx.doi.org/10.48550/arXiv.2305.16291),
  [Link](http://arxiv.org/abs/2305.16291)
  Cited by: [§2.2](https://arxiv.org/html/2604.25850#S2.SS2.p1.1 "2.2 Automated Optimization of LLM Agents ‣ 2 Related Work ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [42]
  X. Wang, B. Li, Y. Song, F. F. Xu, X. Tang, M. Zhuge, J. Pan, Y. Song, B. Li, J. Singh, H. H. Tran, F. Li, R. Ma, M. Zheng, B. Qian, Y. Shao, N. Muennighoff, Y. Zhang, B. Hui, J. Lin, R. Brennan, H. Peng, H. Ji, and G. Neubig (2025)
  OpenHands: an open platform for ai software developers as generalist agents.
   arXiv.
  External Links: 2407.16741,
  [Document](https://dx.doi.org/10.48550/arXiv.2407.16741),
  [Link](http://arxiv.org/abs/2407.16741)
  Cited by: [§1](https://arxiv.org/html/2604.25850#S1.p1.1 "1 Introduction ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"),
  [§1](https://arxiv.org/html/2604.25850#S1.p2.1 "1 Introduction ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"),
  [§2.1](https://arxiv.org/html/2604.25850#S2.SS1.p1.1 "2.1 Harness Engineering and Evaluation for Coding Agents ‣ 2 Related Work ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [43]
  P. Xia, J. Chen, H. Wang, J. Liu, K. Zeng, Y. Wang, S. Han, Y. Zhou, X. Zhao, H. Chen, Z. Zheng, C. Xie, and H. Yao (2026)
  SkillRL: evolving agents via recursive skill-augmented reinforcement learning.
   arXiv.
  External Links: 2602.08234,
  [Document](https://dx.doi.org/10.48550/arXiv.2602.08234),
  [Link](http://arxiv.org/abs/2602.08234)
  Cited by: [§1](https://arxiv.org/html/2604.25850#S1.p3.1 "1 Introduction ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [44]
  A. Yang, A. Li, B. Yang, B. Zhang, B. Hui, B. Zheng, B. Yu, C. Gao, C. Huang, C. Lv, C. Zheng, D. Liu, F. Zhou, F. Huang, F. Hu, H. Ge, H. Wei, H. Lin, J. Tang, J. Yang, J. Tu, J. Zhang, J. Yang, J. Yang, J. Zhou, J. Zhou, J. Lin, K. Dang, K. Bao, K. Yang, L. Yu, L. Deng, M. Li, M. Xue, M. Li, P. Zhang, P. Wang, Q. Zhu, R. Men, R. Gao, S. Liu, S. Luo, T. Li, T. Tang, W. Yin, X. Ren, X. Wang, X. Zhang, X. Ren, Y. Fan, Y. Su, Y. Zhang, Y. Zhang, Y. Wan, Y. Liu, Z. Wang, Z. Cui, Z. Zhang, Z. Zhou, and Z. Qiu (2025)
  Qwen3 technical report.
   arXiv.
  External Links: 2505.09388,
  [Document](https://dx.doi.org/10.48550/arXiv.2505.09388),
  [Link](http://arxiv.org/abs/2505.09388)
  Cited by: [§1](https://arxiv.org/html/2604.25850#S1.p2.1 "1 Introduction ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"),
  [§4.1](https://arxiv.org/html/2604.25850#S4.SS1.SSS0.Px2.p1.1 "Models. ‣ 4.1 Setup ‣ 4 Experiments ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [45]
  J. Yang, C. E. Jimenez, A. Wettig, K. Lieret, S. Yao, K. R. Narasimhan, and O. Press (2024)
  SWE-agent: agent-computer interfaces enable automated software engineering.
  In The Thirty-Eighth Annual Conference on Neural Information Processing Systems,
  External Links: [Link](https://openreview.net/forum?id=mXpq6ut8J3&referrer=%5Bthe%20profile%20of%20Shunyu%20Yao%5D(%2Fprofile%3Fid%3D~Shunyu_Yao1))
  Cited by: [§1](https://arxiv.org/html/2604.25850#S1.p1.1 "1 Introduction ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"),
  [§2.1](https://arxiv.org/html/2604.25850#S2.SS1.p1.1 "2.1 Harness Engineering and Evaluation for Coding Agents ‣ 2 Related Work ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [46]
  J. Yang, C. E. Jimenez, A. L. Zhang, K. Lieret, J. Yang, X. Wu, O. Press, N. Muennighoff, G. Synnaeve, K. R. Narasimhan, D. Yang, S. Wang, and O. Press (2024)
  SWE-bench multimodal: do ai systems generalize to visual software domains?.
  In The Thirteenth International Conference on Learning Representations,
  External Links: [Link](https://openreview.net/forum?id=riTiq3i21b)
  Cited by: [§1](https://arxiv.org/html/2604.25850#S1.p1.1 "1 Introduction ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"),
  [§2.1](https://arxiv.org/html/2604.25850#S2.SS1.p2.1 "2.1 Harness Engineering and Evaluation for Coding Agents ‣ 2 Related Work ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [47]
  Y. Zeng, S. Li, D. Dong, R. Xu, Z. Chen, L. Zheng, Y. Li, Z. Zhou, H. Zhao, L. Tian, H. Xiao, T. Zhu, L. Hao, and J. Wu (2026)
  SWE-hub: a unified production system for scalable, executable software engineering tasks.
   arXiv.
  External Links: 2603.00575,
  [Document](https://dx.doi.org/10.48550/arXiv.2603.00575),
  [Link](http://arxiv.org/abs/2603.00575)
  Cited by: [§2.1](https://arxiv.org/html/2604.25850#S2.SS1.p2.1 "2.1 Harness Engineering and Evaluation for Coding Agents ‣ 2 Related Work ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [48]
  J. Zhang, J. Xiang, Z. Yu, F. Teng, X. Chen, J. Chen, M. Zhuge, X. Cheng, S. Hong, J. Wang, B. Zheng, B. Liu, Y. Luo, and C. Wu (2024)
  AFlow: automating agentic workflow generation.
  In The Thirteenth International Conference on Learning Representations,
  External Links: [Link](https://openreview.net/forum?id=z5uVAKwmjf)
  Cited by: [§2.2](https://arxiv.org/html/2604.25850#S2.SS2.p1.1 "2.2 Automated Optimization of LLM Agents ‣ 2 Related Work ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [49]
  Q. Zhang, C. Hu, S. Upasani, B. Ma, F. Hong, V. Kamanuru, J. Rainton, C. Wu, M. Ji, H. Li, U. Thakker, J. Zou, and K. Olukotun (2025)
  Agentic context engineering: evolving contexts for self-improving language models.
  In The Fourteenth International Conference on Learning Representations,
  External Links: [Link](https://openreview.net/forum?id=eC4ygDs02R)
  Cited by: [§1](https://arxiv.org/html/2604.25850#S1.p3.1 "1 Introduction ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"),
  [§1](https://arxiv.org/html/2604.25850#S1.p5.1 "1 Introduction ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"),
  [§2.2](https://arxiv.org/html/2604.25850#S2.SS2.p1.1 "2.2 Automated Optimization of LLM Agents ‣ 2 Related Work ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"),
  [§4.2](https://arxiv.org/html/2604.25850#S4.SS2.p1.1 "4.2 RQ1: Main Results ‣ 4 Experiments ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [50]
  A. Zhao, D. Huang, Q. Xu, M. Lin, Y. Liu, and G. Huang (2024)
  ExpeL: llm agents are experiential learners.
   arXiv.
  External Links: 2308.10144,
  [Document](https://dx.doi.org/10.48550/arXiv.2308.10144),
  [Link](http://arxiv.org/abs/2308.10144)
  Cited by: [§1](https://arxiv.org/html/2604.25850#S1.p3.1 "1 Introduction ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [51]
  W. Zhou, Y. Ou, S. Ding, L. Li, J. Wu, T. Wang, J. Chen, S. Wang, X. Xu, N. Zhang, H. Chen, and Y. E. Jiang (2024)
  Symbolic learning enables self-evolving agents.
   arXiv.
  External Links: 2406.18532,
  [Document](https://dx.doi.org/10.48550/arXiv.2406.18532),
  [Link](http://arxiv.org/abs/2406.18532)
  Cited by: [§2.2](https://arxiv.org/html/2604.25850#S2.SS2.p1.1 "2.2 Automated Optimization of LLM Agents ‣ 2 Related Work ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [52]
  T. Y. Zhuo, V. M. Chien, J. Chim, H. Hu, W. Yu, R. Widyasari, I. N. B. Yusuf, H. Zhan, J. He, I. Paul, S. Brunner, C. Gong, J. Hoang, A. R. Zebaze, X. Hong, W. Li, J. Kaddour, M. Xu, Z. Zhang, P. Yadav, N. Jain, A. Gu, Z. Cheng, J. Liu, Q. Liu, Z. Wang, B. Hui, N. Muennighoff, D. Lo, D. Fried, X. Du, H. de Vries, and L. V. Werra (2024)
  BigCodeBench: benchmarking code generation with diverse function calls and complex instructions.
  In The Thirteenth International Conference on Learning Representations,
  External Links: [Link](https://openreview.net/forum?id=YrycTjllL0)
  Cited by: [§2.1](https://arxiv.org/html/2604.25850#S2.SS1.p2.1 "2.1 Harness Engineering and Evaluation for Coding Agents ‣ 2 Related Work ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
- [53]
  G. Zunic (2026)
  The bitter lesson of agent harnesses.
  External Links: [Link](https://browser-use.com/posts/bitter-lesson-agent-harnesses)
  Cited by: [§1](https://arxiv.org/html/2604.25850#S1.p4.1 "1 Introduction ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").

## Appendix A Experimental Setup: Full Details

This appendix expands the condensed Setup in §[4.1](https://arxiv.org/html/2604.25850#S4.SS1 "4.1 Setup ‣ 4 Experiments ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses") with the formal metric definitions and the runtime infrastructure.

### Seed agent.

The seed configuration, denoted NexAU0, is a simple code agent built on the NexAU framework of §[3.1](https://arxiv.org/html/2604.25850#S3.SS1 "3.1 NexAU: an editable, decoupled harness substrate ‣ 3 Method ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses") that exposes only the bash tool to the model, with no skills, no middleware, and no long-term memory. Every iteration of the AHE outer loop edits this workspace, so all reported gains are measured against NexAU0 as the common starting point.

### Runtime infrastructure.

All runs use the NexAU framework of §[3.1](https://arxiv.org/html/2604.25850#S3.SS1 "3.1 NexAU: an editable, decoupled harness substrate ‣ 3 Method ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses") to instantiate the coding agent. Harbor dispatches tasks, isolates each rollout, and verifies pass/fail, with a 3600-second per-task timeout. Every rollout runs inside a fresh E2B remote sandbox, so shell side-effects cannot leak between tasks. InMemoryTracer records trajectories and mirrors them to Langfuse. The Agent Debugger executes at concurrency 16 with a 600-second per-task timeout.

### Hyperparameters.

Table [4](https://arxiv.org/html/2604.25850#A1.T4 "Table 4 ‣ Hyperparameters. ‣ Appendix A Experimental Setup: Full Details ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses") consolidates the operating points of the four agents and the outer loop, taken from the configuration snapshot of the reference run.

Table 4: Hyperparameters of the reference AHE run on Terminal-Bench 2, taken from the configuration snapshot of the run that produced the AHE numbers in Section [4.2](https://arxiv.org/html/2604.25850#S4.SS2 "4.2 RQ1: Main Results ‣ 4 Experiments ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"). All four agents share GPT-5.4 as the backing model and differ only in reasoning tier, sampling, and per-component limits.

|  |  |  |
| --- | --- | --- |
| Block | Hyperparameter | Value |
| Code Agent | Backing model | GPT-5.4 |
|  | Reasoning effort | high |
|  | Temperature | 0.7 |
|  | Top-`p` | 0.95 |
|  | Max context | 200,000 tokens |
|  | Max generation per turn | 32,000 tokens |
|  | Max model turns | 300 |
| Agent Debugger | Backing model | GPT-5.4 |
|  | Concurrent tasks | 16 |
|  | Per-task timeout | 600 s |
|  | Retry attempts | 3 |
|  | Retry backoff | 2 s |
| Evolve Agent | Backing model | GPT-5.4 |
|  | Reasoning effort | xhigh |
|  | Temperature | 0.7 |
|  | Max context | 200,000 tokens |
|  | Max generation per turn | 32,000 tokens |
|  | Max model turns | 500 |
|  | Skill packages | 3 |
|  | Context compaction threshold | 0.75 |
| Explore Agent | Backing model | GPT-5.4 |
|  | Reasoning effort | xhigh |
|  | Wall-clock budget | 60 min |
|  | Web sources | 10 |
|  | Code sources | 1 |
| Outer loop / dispatcher | Iterations `T` | 10 |
|  | Rollouts per task `k` | 2 |
|  | Concurrent rollouts | 96 |
|  | Sandbox | E2B remote |
|  | Sandbox lifetime | 3,600 s |
|  | Dataset | Terminal-Bench 2, 89 tasks |

### Terminal-bench difficulty labels.

The official terminal-bench-2 leaderboard00
0
<https://www.tbench.ai/benchmarks/terminal-bench-2> partitions the 89-task subset into 4 easy, 55 medium, and 30 hard tasks.

### pass@1.

For a configuration on a task set `D` with `k` rollouts per task, let `r_{i,j}\in\{0,1\}` denote the binary reward of rollout `j` on task `i`. The pass@1 score is the mean

|  |  |  |  |
| --- | --- | --- | --- |
|  | `\mathrm{pass@1}=\frac{1}{k|D|}\sum_{i=1}^{|D|}\sum_{j=1}^{k}r_{i,j}.` |  | (1) |

Trials that terminate on an infrastructure exception, such as a sandbox crash or API timeout, contribute `r=0` rather than being dropped, a strictly harsher convention than discarding failures that keeps our numbers comparable to the official terminal-bench leaderboard. The rollout count `k` varies across experiments; each table states it explicitly.

### Token cost and Succ/Mtok.

For token cost we count every LLM call as prompt plus completion across the rollout and report the mean over completed trials in thousands, denoted Tokens k; infrastructure-aborted trials are excluded to avoid truncated figures. To compare configurations that trade accuracy for cost we combine the two via

|  |  |  |  |
| --- | --- | --- | --- |
|  | `\mathrm{Succ/Mtok}=\frac{\mathrm{pass@1}\times 10^{6}}{\mathrm{mean\ tokens\ per\ trial}},` |  | (2) |

the expected number of successes per million tokens. The main paper reports pass@1 and Tokens k separately so each axis stays legible; Table [5](https://arxiv.org/html/2604.25850#A1.T5 "Table 5 ‣ Token cost and Succ/Mtok. ‣ Appendix A Experimental Setup: Full Details ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses") folds them into Succ/Mtok per repository on SWE-bench-verified, derived from the pass@1 and Tokens k columns of Table [2](https://arxiv.org/html/2604.25850#S4.T2 "Table 2 ‣ 4.3 RQ2: Transfer to Unseen Tasks and Base Models ‣ 4 Experiments ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").

Table 5: Cost-efficiency on SWE-bench-verified, reported as Succ/Mtok, the expected successes per million tokens. Values are derived from Table [2](https://arxiv.org/html/2604.25850#S4.T2 "Table 2 ‣ 4.3 RQ2: Transfer to Unseen Tasks and Base Models ‣ 4 Experiments ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses") as `\mathrm{pass@1}\times 10^{3}/\text{Tokens k}`. Higher is better. Per-row bold marks the best.

| Repo | `N` | ACE | TF-GRPO | NexAU0 | AHE |
| --- | --- | --- | --- | --- | --- |
| All | 500 | 1.10 | 1.27 | 1.43 | 1.64 |
| django | 231 | 1.12 | 1.35 | 1.50 | 1.67 |
| sympy | 75 | 1.15 | 1.19 | 1.43 | 1.48 |
| sphinx-doc | 44 | 0.62 | 0.78 | 0.93 | 1.07 |
| matplotlib | 34 | 1.14 | 1.33 | 1.51 | 1.88 |
| scikit-learn | 32 | 2.08 | 2.48 | 3.06 | 3.40 |
| pydata | 22 | 1.37 | 1.50 | 2.00 | 2.15 |
| astropy | 22 | 1.08 | 1.26 | 0.82 | 1.81 |

## Appendix B Prompts and Configurations

This appendix gathers the prompts that drive the AHE outer loop together with the seed code agent’s system prompt. The five blocks below reproduce the literal contents of the corresponding files in the public repository at <https://github.com/china-qijizhifeng/agentic-harness-engineering> as of the commit that produced the experiments in Section [4](https://arxiv.org/html/2604.25850#S4 "4 Experiments ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"). Jinja-style {{ var }} placeholders are filled in by the harness at runtime.

### B.1 Code Agent Seed System Prompt

The seed system prompt loaded into NexAU0 at iteration 1. It is intentionally minimal: a single tool, three behavioral rules, and three runtime-injected variables. Every iteration after iteration 1 may append rules to this file, and the case study in Appendix [C](https://arxiv.org/html/2604.25850#A3 "Appendix C Qualitative Case Study ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses") traces the first such append.

code_agent_simple/systemprompt.md

[⬇](data:text/plain;base64,WW91IHNvbHZlIHNvZnR3YXJlIHRhc2tzIGluIGEgbm9uLWludGVyYWN0aXZlIHNldHRpbmcuIFlvdXIgb25seSB0b29sIGlzICoqYHJ1bl9zaGVsbF9jb21tYW5kYCoqOiB1c2UgdGhlIHNoZWxsIHRvIGluc3BlY3QgdGhlIHJlcG8sIGVkaXQgZmlsZXMsIHJ1biBidWlsZHMvdGVzdHMsIGFuZCBmaW5pc2ggdGhlIHdvcmsuIERvIG5vdCBhc2sgdGhlIHVzZXIgcXVlc3Rpb25zLgoKLSBQcmVmZXIgc2hvcnQgcmVwbGllczsgdXNlIHRoZSB0b29sIGZvciBhY3Rpb25zLgotIEJlZm9yZSBjb21tYW5kcyB0aGF0IGRlbGV0ZSBvciBvdmVyd3JpdGUgaW1wb3J0YW50IGRhdGEsIHN0YXRlIGJyaWVmbHkgd2hhdCB0aGV5IGRvLgotIExvbmctcnVubmluZyBwcm9jZXNzZXM6IHVzZSBgaXNfYmFja2dyb3VuZDogdHJ1ZWAgb24gYHJ1bl9zaGVsbF9jb21tYW5kYCAoZG8gbm90IHVzZSBgJmAgaW4gdGhlIGNvbW1hbmQgc3RyaW5nKS4KCkRhdGU6IHt7IGRhdGUgfX0KVXNlcm5hbWU6IHt7IHVzZXJuYW1lIH19CldvcmtpbmcgRGlyOiB7eyB3b3JraW5nX2RpcmVjdG9yeSB9fQ==)
You solve software tasks in a non-interactive setting. Your only tool is **`run_shell_command`**: use the shell to inspect the repo, edit files, run builds/tests, and finish the work. Do not ask the user questions.

- Prefer short replies; use the tool for actions.
- Before commands that delete or overwrite important data, state briefly what they do.
- Long-running processes: use `is_background: true` on `run_shell_command` (do not use `&` in the command string).

Date: {{ date }}
Username: {{ username }}
Working Dir: {{ working_directory }}

### B.2 Evolve Agent Prompt

The Evolve Agent’s system prompt encodes the three hard contracts described in Section [3](https://arxiv.org/html/2604.25850#S3 "3 Method ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"): workspace-only controllability, evidence-driven changes, and the change-manifest deliverable. It also embeds the directory layout the agent must reason over and the JSON shape of the manifest.

evolve_agent/evolve_prompt.md

[⬇](data:text/plain;base64,eyUgc2V0IHdzID0gd29ya3NwYWNlX3BhdGggaWYgd29ya3NwYWNlX3BhdGggaXMgZGVmaW5lZCBlbHNlICJ3b3Jrc3BhY2UiICV9CllvdSBhcmUgdGhlIE5leEFVIEV2b2x1dGlvbiBFbmdpbmUgLS0gYSBtZXRhLWFnZW50IHRoYXQgaXRlcmF0ZXMgb24gYSBjb2RpbmcgYWdlbnQncyBoYXJuZXNzIHRvIG1heGltaXplICoqcGFzc0AxKiogKHNpbmdsZS1hdHRlbXB0IHN1Y2Nlc3MgcmF0ZSkgdGhyb3VnaCBldmlkZW5jZS1iYXNlZCBleHBlcmltZW50YXRpb24uIFlvdSBtYXkgbW9kaWZ5IGV4aXN0aW5nIGNvbXBvbmVudHMgb3IgY3JlYXRlIG5ldyBvbmVzICh0b29scywgbWlkZGxld2FyZSwgc2tpbGxzLCBzdWItYWdlbnRzLCBldGMuKSBhcyBuZWVkZWQuCgoKIyBDb3JlIFByaW5jaXBsZXMKCiMjIDEuIENvbnRyb2xsYWJpbGl0eQoKT25seSBgd29ya3NwYWNlL2AgaXMgeW91ciBwbGF5Z3JvdW5kLiBFdmVyeXRoaW5nIGVsc2UgaXMgcmVhZC1vbmx5IG9yIG9mZi1saW1pdHMuCgotIE1vZGlmeSBPTkxZIGZpbGVzIHVuZGVyIGB3b3Jrc3BhY2UvYAotIGBydW5zL2AgaXMgUkVBRCBPTkxZIC0tIHVzZSBpdCBmb3IgYW5hbHlzaXMsIG5ldmVyIHdyaXRlIHRvIGl0Ci0gRG8gTk9UIG1vZGlmeSBMTE0gY29uZmlnLCB0cmFjZXIsIHZlcmlmaWVyLCBvciBhbnkgaW5mcmFzdHJ1Y3R1cmUKLSBEbyBOT1QgZGVsZXRlIE9SSUdJTkFMIHN5c3RlbSBwcm9tcHQgcnVsZXMgKHRob3NlIGluIGl0ZXJhdGlvbiAxJ3MgYGlucHV0L3dvcmtzcGFjZS9gKQotIEZ1bGwgc2FmZXR5IGNvbnN0cmFpbnRzIGFyZSBhdCB0aGUgZW5kIG9mIHRoaXMgZG9jdW1lbnQKCiMjIDIuIEV2aWRlbmNlLURyaXZlbgoKKipFdmVyeSBjaGFuZ2UgbXVzdCBiZSB0cmFjZWFibGUgdG8gc3BlY2lmaWMgZmFpbHVyZSBldmlkZW5jZS4qKiBEbyBub3QgbWFrZSBjaGFuZ2VzIGJhc2VkIG9uIGludHVpdGlvbiwgc3BlY3VsYXRpb24sIG9yICJiZXN0IHByYWN0aWNlcyIgYWxvbmUuCgoqKkJlZm9yZSBtYWtpbmcgYW55IGNoYW5nZSwgeW91IG11c3QgaGF2ZToqKgoxLiAqKkZhaWx1cmUgZXZpZGVuY2UqKiAtLSB3aGljaCB0YXNrcyBmYWlsZWQsIGFuZCB3aGF0IHNwZWNpZmljYWxseSB3ZW50IHdyb25nIChmcm9tIGFuYWx5c2lzIHJlcG9ydHMgb3IgdHJhY2VzKQoyLiAqKlJvb3QgY2F1c2UqKiAtLSB3aHkgaXQgZmFpbGVkLCBub3QganVzdCB3aGF0IGZhaWxlZAozLiAqKlRhcmdldGVkIGZpeCoqIC0tIGEgY2hhbmdlIHRoYXQgZGlyZWN0bHkgYWRkcmVzc2VzIHRoZSByb290IGNhdXNlCjQuICoqUHJlZGljdGVkIGltcGFjdCoqIC0tIHdoaWNoIHRhc2tzIHRoaXMgc2hvdWxkIGZpeCwgYW5kIHdoaWNoIHRhc2tzIG1pZ2h0IGJlIGF0IHJpc2sKCgojIEVudmlyb25tZW50Cgp7JSBpZiB3cyAhPSAid29ya3NwYWNlIiAlfQo+ICoqV09SS1NQQUNFIFBBVEgqKjogWW91ciB3b3Jrc3BhY2UgaXMgYXQgYHt7IHdzIH19L2AgaW5zdGVhZCBvZiBgd29ya3NwYWNlL2AuIEFsbCBgd29ya3NwYWNlL2AgcmVmZXJlbmNlcyBiZWxvdyBhcHBseSB0byBge3sgd3MgfX0vYC4gVXNlIGB7eyB3cyB9fS9gIGluIGZpbGUgb3BlcmF0aW9ucywgZ2l0IGNvbW1hbmRzLCBhbmQgdGhlIHZhbGlkYXRpb24gY29tbWFuZC4KeyUgZW5kaWYgJX0KCj4gKipMb29wIGNvbnZlbnRpb24gKElNUE9SVEFOVCAtLSByZWFkIGJlZm9yZSBhbmFseXppbmcgYHJ1bnMvYCk6KioKPiBZb3UgYXJlIGN1cnJlbnRseSBpbiBsb29wICoqaXRlcmF0aW9uIGB7eyBpdGVyYXRpb24gfX1gKiouIEVhY2ggYHJ1bnMvaXRlcmF0aW9uX05OTi9gIGZvbGRlciBtaXhlcyAqKnR3byoqIGdlbmVyYXRpb25zIG9mIHdvcms6Cj4gLSBgaW5wdXQvYCBob2xkcyB3aGF0ICoqdGhlIHByZXZpb3VzIGxvb3AgKE5OTi0xKSoqIHByb2R1Y2VkIC0tIHRoaXMgaXMgdGhlIHdvcmtzcGFjZSB0aGF0IHdhcyBqdXN0IGV2YWx1YXRlZCB0aGlzIGxvb3AuIFRoZSBiZW5jaG1hcmssIGFuYWx5c2lzLCBhbmQgY2hhbmdlX2V2YWx1YXRpb24gaW5zaWRlIGBpbnB1dC9gIGFsbCBkZXNjcmliZSB0aGUgKipwcmV2aW91cyBsb29wJ3MqKiBjaGFuZ2VzLCBub3QgeW91cnMuCj4gLSBgZXZvbHZlL2AgaG9sZHMgd2hhdCAqKnRoaXMgbG9vcCAoTk5OKSoqIHdpbGwgcHJvZHVjZSAtLSB5b3VyIG5ldyBjaGFuZ2VzLCB3aGljaCB0aGUgbmV4dCBsb29wIChOTk4rMSkgd2lsbCBldmFsdWF0ZS4KPgo+IENvbmNyZXRlbHk6IHdoZW4geW91ciBxdWVyeSBzYXlzICJJdGVyYXRpb24ge3sgaXRlcmF0aW9uIH19IGV2YWx1YXRpb24gY29tcGxldGVkIiwgaXQgbWVhbnMgdGhlIGV2YWwgb2YgKippdGVyYXRpb24ge3sgaXRlcmF0aW9uIC0gMSB9fSdzIGNoYW5nZXMqKiBpcyBkb25lIChiYXNlbGluZSBpZiBge3sgaXRlcmF0aW9uIH19YCA9IDEpLiBZb3UgYXJlIG5vdyBtYWtpbmcgY2hhbmdlcyB0aGF0IHdpbGwgYmUgbGFiZWxlZCBpdGVyYXRpb24gYHt7IGl0ZXJhdGlvbiB9fWAgYW5kIGV2YWx1YXRlZCBuZXh0IGxvb3AuCgpgYGAKLi8gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIyB3b3JrX2RpciA9IGV4cGVyaW1lbnQgcm9vdAp8LS0ge3sgd3MgfX0vICAgICAgICAgICAgICAgICAgICAgICAgICAjICogTU9ESUZZIHRoZXNlIGZpbGVzCnwgICB8LS0gY29kZV9hZ2VudC55YW1sICAgICAgICAgICAgICAgICMgQWdlbnQgY29uZmlnICh0b29scywgbWlkZGxld2FyZSwgcGFyYW1zLCBzdWItYWdlbnRzKQp8ICAgfC0tIHN5c3RlbXByb21wdC5tZCAgICAgICAgICAgICAgICAjIFN5c3RlbSBwcm9tcHQgKEppbmphIHRlbXBsYXRlKQp8ICAgfC0tIExvbmdUZXJtTUVNT1JZLm1kICAgICAgICAgICAgICAjIExvbmctdGVybSBtZW1vcnkgKHBlcnNpc3RlbnQgY3Jvc3Mtc2Vzc2lvbiBrbm93bGVkZ2UsIE1PRElGSUFCTEUpCnwgICB8LS0gU2hvcnRUZXJtTUVNT1JZLm1kICAgICAgICAgICAgICMgU2hvcnQtdGVybSBtZW1vcnkgKG1hbmFnZWQgYnkgY29kZSBhZ2VudCBhdCBydW50aW1lLCBETyBOT1QgTU9ESUZZKQp8ICAgfC0tIHRvb2xfZGVzY3JpcHRpb25zLyAgICAgICAgICAgICAjIFRvb2wgWUFNTCBkZWZpbml0aW9ucwp8ICAgfC0tIHRvb2xzLyAgICAgICAgICAgICAgICAgICAgICAgICAjIFRvb2wgUHl0aG9uIGltcGxlbWVudGF0aW9ucwp8ICAgfC0tIG1pZGRsZXdhcmUvICAgICAgICAgICAgICAgICAgICAjIE1pZGRsZXdhcmUgUHl0aG9uIGltcGxlbWVudGF0aW9ucwp8ICAgfC0tIHNraWxscy8gICAgICAgICAgICAgICAgICAgICAgICAjIFNraWxsIHBhY2thZ2VzCnwgICBgLS0gc3ViX2FnZW50cy8gICAgICAgICAgICAgICAgICAgICMgU3ViLWFnZW50IGNvbmZpZ3MgKG9wdGlvbmFsLCB5b3UgbWF5IGNyZWF0ZSkKfAp8LS0gcnVucy8gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAjICogUkVBRCBPTkxZCnwgICBgLS0gaXRlcmF0aW9uX05OTi8KfCAgICAgICB8LS0gaW5wdXQvICAgICAgICAgICAgICAgICAgICAgIyBFdmVyeXRoaW5nIHRoaXMgaXRlcmF0aW9uIHN0YXJ0cyB3aXRoCnwgICAgICAgfCAgIHwtLSB3b3Jrc3BhY2UvICAgICAgICAgICAgICMgV29ya3NwYWNlIGJlaW5nIGV2YWx1YXRlZCB0aGlzIGxvb3AKfCAgICAgICB8ICAgfC0tIGJlbmNobWFyay8gICAgICAgICAgICAgIyBFdmFsIHJlc3VsdHMgZm9yIHRoZSB3b3Jrc3BhY2UgYWJvdmUKfCAgICAgICB8ICAgfCAgIGAtLSB7dGltZXN0YW1wfS8KfCAgICAgICB8ICAgfCAgICAgICB8LS0gcmVzdWx0Lmpzb24KfCAgICAgICB8ICAgfCAgICAgICBgLS0ge3Rhc2tfbmFtZX1fX3tpZH0vCnwgICAgICAgfCAgIHwgICAgICAgICAgIHwtLSBhZ2VudC9uZXhhdS50eHQKfCAgICAgICB8ICAgfCAgICAgICAgICAgfC0tIGFnZW50L25leGF1X2luX21lbW9yeV90cmFjZXIuY2xlYW5lZC5qc29uCnwgICAgICAgfCAgIHwgICAgICAgICAgIGAtLSB2ZXJpZmllci9yZXdhcmQudHh0CnwgICAgICAgfCAgIHwtLSBhbmFseXNpcy8gICAgICAgICAgICAgICMgKiogUHJlLWJ1aWx0IGZhaWx1cmUvc3VjY2VzcyBhbmFseXNpcyAoUkVBRCBUSElTIEZJUlNUKQp8ICAgICAgIHwgICB8ICAgfC0tIG92ZXJ2aWV3Lm1kCnwgICAgICAgfCAgIHwgICBgLS0gZGV0YWlsL3t0YXNrX25hbWV9Lm1kCnwgICAgICAgfCAgIHwtLSB2YXJpYW50X3NlbGVjdGlvbi5qc29uCnwgICAgICAgfCAgIGAtLSBjaGFuZ2VfZXZhbHVhdGlvbi5qc29uCnwgICAgICAgYC0tIGV2b2x2ZS8gICAgICAgICAgICAgICAgICAgICMgWU9VUiBvdXRwdXRzIHRoaXMgbG9vcAp8ICAgICAgICAgICB8LS0gZXZvbHZlX3N1bW1hcnkubWQKfCAgICAgICAgICAgfC0tIGNoYW5nZV9tYW5pZmVzdC5qc29uCnwgICAgICAgICAgIGAtLSB2YXJpYW50X04vCnwgICAgICAgICAgICAgICB8LS0gd29ya3NwYWNlLwp8ICAgICAgICAgICAgICAgYC0tIGV2b2x2ZV90cmFjZS5qc29uCnwKfC0tIGV2b2x1dGlvbl9oaXN0b3J5Lm1kICAgICAgICAgICAgICAgIyBDdW11bGF0aXZlIGhpc3Rvcnkgb2YgYWxsIGl0ZXJhdGlvbnMgKFJFQUQpCmAtLSBjb25maWdfc25hcHNob3QueWFtbCAgICAgICAgICAgICAgICMgSW5pdGlhbCBjb25maWcgKFJFQUQgT05MWSkKYGBgCgoKIyBDb21wb25lbnRzCgojIyBBdmFpbGFibGUgQ29tcG9uZW50IFR5cGVzCgp8IENvbXBvbmVudCB8IEZpbGVzIHwgQ2hhcmFjdGVyaXN0aWNzIHwgV2hlbiB0byB1c2UgfAp8LS0tLS0tLS0tLS18LS0tLS0tLXwtLS0tLS0tLS0tLS0tLS0tfC0tLS0tLS0tLS0tLS18CnwgKipTeXN0ZW0gUHJvbXB0KiogfCBgd29ya3NwYWNlL3N5c3RlbXByb21wdC5tZGAgfCBBZHZpc29yeSAtLSBhcHBsaWVzIHRvIGFsbCB0YXNrcyB8IEJlaGF2aW9yYWwgcnVsZXMsIHdvcmtmbG93IGd1aWRhbmNlIHwKfCAqKlRvb2wgRGVzY3JpcHRpb24qKiB8IGB3b3Jrc3BhY2UvdG9vbF9kZXNjcmlwdGlvbnMvKi50b29sLnlhbWxgIHwgQ28tbG9jYXRlZCB3aXRoIHRvb2wgLS0gbW9kZWwgcmVhZHMgd2hlbiBjYWxsaW5nIHwgQ2xhcmlmeSB0b29sIHVzYWdlLCBhZGQgZXhhbXBsZXMsIHdhcm4gYWJvdXQgcGl0ZmFsbHMgfAp8ICoqVG9vbCBJbXBsZW1lbnRhdGlvbioqIHwgYHdvcmtzcGFjZS90b29scy9gIHwgQ29udHJvbHMgdG9vbCBiZWhhdmlvciBkaXJlY3RseSB8IE5ldyBjYXBhYmlsaXRpZXMsIHNtYXJ0ZXIgZXJyb3IgaGFuZGxpbmcsIG91dHB1dCBmb3JtYXR0aW5nIHwKfCAqKk1pZGRsZXdhcmUqKiB8IGB3b3Jrc3BhY2UvbWlkZGxld2FyZS9gICsgYGNvZGVfYWdlbnQueWFtbGAgfCBIb29rcyBpbnRvIGFnZW50IGxvb3AgcGlwZWxpbmUgfCBJbnRlcmNlcHQvdHJhbnNmb3JtIGF0IGV4ZWN1dGlvbiBsZXZlbCB8CnwgKipTa2lsbCoqIHwgYHdvcmtzcGFjZS9za2lsbHMvYCArIGBjb2RlX2FnZW50LnlhbWxgIHwgT24tZGVtYW5kIC0tIGxvYWRlZCB3aGVuIHJlbGV2YW50IHwgUmV1c2FibGUgd29ya2Zsb3cgcGF0dGVybnMgfAp8ICoqU3ViLUFnZW50KiogfCBgd29ya3NwYWNlL3N1Yl9hZ2VudHMve25hbWV9L2AgKyBgY29kZV9hZ2VudC55YW1sYCB8IERlbGVnYXRlZCBleGVjdXRpb24gLS0gaXNvbGF0ZWQgY29udGV4dCB8IE9mZmxvYWQgc3BlY2lhbGl6ZWQgc3VidGFzayB0byBjaGlsZCBhZ2VudCB8CnwgKipMb25nLVRlcm0gTWVtb3J5KiogfCBgd29ya3NwYWNlL0xvbmdUZXJtTUVNT1JZLm1kYCB8IFBlcnNpc3RlbnQgY3Jvc3Mtc2Vzc2lvbiBrbm93bGVkZ2UgLS0gTU9ESUZJQUJMRSB8IFJlY29yZCByZWN1cnJpbmcgcGl0ZmFsbHMsIHByb3ZlbiBzdHJhdGVnaWVzLCBlbnZpcm9ubWVudCBxdWlya3MgfAp8ICoqU2hvcnQtVGVybSBNZW1vcnkqKiB8IGB3b3Jrc3BhY2UvU2hvcnRUZXJtTUVNT1JZLm1kYCB8IFNlc3Npb24tc2NvcGVkIHNjcmF0Y2ggLS0gRE8gTk9UIE1PRElGWSB8IF8ocmVhZC1vbmx5IGZvciBldm9sdmUgYWdlbnQpXyB8CgpBbGwgY29tcG9uZW50IHR5cGVzIGFyZSBlcXVhbGx5IHZhbGlkIGFuZCBpbXBvcnRhbnQuIENob29zZSB0aGUgb25lIHRoYXQgYmVzdCBmaXRzIHRoZSByb290IGNhdXNlLgoKIyMjIENob29zaW5nIHRoZSBSaWdodCBDb21wb25lbnQgTGV2ZWwKCkZvciBlYWNoIGZhaWx1cmUgcGF0dGVybiwgY29uc2lkZXIgKiphbGwqKiBjb21wb25lbnQgdHlwZXMgYWJvdmUgLS0gaW5jbHVkaW5nIGNyZWF0aW5nIG5ldyBvbmVzIC0tIGJlZm9yZSBkZWNpZGluZyB3aGVyZSB0byBmaXguCgoqKkFudGktcGF0dGVybjoqKiBJZiB0aGUgc2FtZSBmYWlsdXJlIGNsYXNzIHBlcnNpc3RzIGFjcm9zcyAyKyBpdGVyYXRpb25zIGRlc3BpdGUgZml4ZXMgYXQgb25lIGNvbXBvbmVudCBsZXZlbCwgdGhhdCBsZXZlbCBtYXkgYmUgdGhlIHdyb25nIGNob2ljZS4gUm9sbGJhY2sgdGhlIGluZWZmZWN0aXZlIGNoYW5nZSBhbmQgcmUtYXBwcm9hY2ggZnJvbSBhIGRpZmZlcmVudCBjb21wb25lbnQgbGV2ZWwuCgojIyBSZWdpc3RlcmluZyBOZXcgQ29tcG9uZW50cwoKKipDcmVhdGluZyBhIGZpbGUgaXMgTk9UIGVub3VnaCAtLSByZWdpc3RlciBpbiBgY29kZV9hZ2VudC55YW1sYDoqKgotIE5ldyB0b29sOiBjcmVhdGUgYC50b29sLnlhbWxgICsgUHl0aG9uIGltcGxlbWVudGF0aW9uICsgYWRkIGVudHJ5IHRvIGB0b29sczpgIGxpc3QKLSBOZXcgbWlkZGxld2FyZTogY3JlYXRlIFB5dGhvbiBjbGFzcyArIGFkZCBlbnRyeSB0byBgbWlkZGxld2FyZXM6YCBsaXN0IHdpdGggYGltcG9ydDpgIHBhdGggYW5kIGBwYXJhbXM6YAotIE5ldyBza2lsbDogY3JlYXRlIGBza2lsbHMve25hbWV9L1NLSUxMLm1kYCBmb2xkZXIgKyBhZGQgdG8gYHNraWxsczpgIGxpc3QKLSBOZXcgc3ViLWFnZW50OiBjcmVhdGUgYHN1Yl9hZ2VudHMve25hbWV9L2FnZW50LnlhbWxgICsgYWRkIHRvIGBzdWJfYWdlbnRzOmAgbGlzdC4gRnJhbWV3b3JrICoqYXV0by1pbmplY3RzKiogYFJlY2FsbFN1YkFnZW50YCB0b29sIC0tIGRvIE5PVCBhZGQgaXQgbWFudWFsbHkuCgojIyBIb3cgQ29kZSBHZXRzIExvYWRlZAoKVGhlIGNvbmZpZyBkaXJlY3RvcnkgaXMgYWRkZWQgdG8gYHN5cy5wYXRoYCBhdCBydW50aW1lOgotIGBiaW5kaW5nOiB0b29scy5maWxlX3Rvb2xzOnJlYWRfZmlsZWAgcmVzb2x2ZXMgdG8gYHdvcmtzcGFjZS90b29scy9maWxlX3Rvb2xzL3JlYWRfZmlsZS5weWAKLSBgaW1wb3J0OiBtaWRkbGV3YXJlLmxvbmdfdG9vbF9vdXRwdXQ6TG9uZ1Rvb2xPdXRwdXRNaWRkbGV3YXJlYCByZXNvbHZlcyB0byBgd29ya3NwYWNlL21pZGRsZXdhcmUvbG9uZ190b29sX291dHB1dC5weWAKLSBgaW1wb3J0OiBtaWRkbGV3YXJlLmNvbnRleHRfY29tcGFjdGlvbjpDb250ZXh0Q29tcGFjdGlvbk1pZGRsZXdhcmVgIHJlc29sdmVzIHRvIGB3b3Jrc3BhY2UvbWlkZGxld2FyZS9jb250ZXh0X2NvbXBhY3Rpb24vX19pbml0X18ucHlgCgojIyBMTE0gRW52aXJvbm1lbnQgVmFyaWFibGVzCgpBdCBydW50aW1lLCB0aGUgaGFybmVzcyBzZXRzIHRoZXNlIGVudmlyb25tZW50IHZhcmlhYmxlcyAqKmJlZm9yZSoqIHRoZSBjb2RlIGFnZW50IHN0YXJ0czoKCnwgVmFyaWFibGUgfCBEZXNjcmlwdGlvbiB8CnwtLS0tLS0tLS0tfC0tLS0tLS0tLS0tLS18CnwgYExMTV9BUElfS0VZYCB8IEFQSSBrZXkgZm9yIHRoZSBjdXJyZW50IExMTSBwcm92aWRlciB8CnwgYExMTV9CQVNFX1VSTGAgfCBCYXNlIFVSTCBmb3IgdGhlIExMTSBBUEkgZW5kcG9pbnQgfAp8IGBMTE1fTU9ERUxgIHwgTW9kZWwgaWRlbnRpZmllciAoZS5nLiBgZ3B0LTUuNGApIHwKCioqQWxsIGNvbXBvbmVudHMqKiAtLSBjb2RlIGFnZW50LCBzdWItYWdlbnRzLCBhbmQgbWlkZGxld2FyZSAtLSB1c2UgdGhlc2Ugc2FtZSBlbnYgdmFyczoKLSBJbiBhZ2VudCBZQU1MIGZpbGVzOiBgJHtlbnYuTExNX0FQSV9LRVl9YCwgYCR7ZW52LkxMTV9CQVNFX1VSTH1gLCBgJHtlbnYuTExNX01PREVMfWAKLSBJbiBtaWRkbGV3YXJlIFB5dGhvbiBjb2RlOiBgb3MuZW52aXJvblsiTExNX0FQSV9LRVkiXWAsIGV0Yy4KCioqRG8gTk9UIGhhcmRjb2RlIEFQSSBrZXlzLioqIEFsd2F5cyByZWZlcmVuY2UgZW52aXJvbm1lbnQgdmFyaWFibGVzLgoKIyMjIE1pZGRsZXdhcmUgY2FuIGNhbGwgTExNCgpNaWRkbGV3YXJlIGhhcyBhY2Nlc3MgdG8gdGhlIGFnZW50J3MgTExNIGNsaWVudCB2aWEgYE1vZGVsQ2FsbFBhcmFtc2AgaW4gdGhlIGB3cmFwX21vZGVsX2NhbGxgIGhvb2suIFVzZSBgTExNQ2FsbGVyYCB0byBtYWtlIHNpZGUtY2FsbHMgKGUuZy4gc3VtbWFyaXplIGNvbnRleHQsIGNsYXNzaWZ5IGVycm9ycywgZ2VuZXJhdGUgZHluYW1pYyBndWlkYW5jZSkuIFNlZSB0aGUgZXZvbHV0aW9uIGd1aWRlIHNraWxsIGZvciBmdWxsIEFQSSByZWZlcmVuY2UgYW5kIGV4YW1wbGVzLgoKIyMjIFN1Yi1BZ2VudHMgdXNlIHRoZSBzYW1lIExMTQoKU3ViLWFnZW50IFlBTUwgY29uZmlncyBzaG91bGQgdXNlIGAke2Vudi5MTE1fTU9ERUx9YCAvIGAke2Vudi5MTE1fQkFTRV9VUkx9YCAvIGAke2Vudi5MTE1fQVBJX0tFWX1gIGluIHRoZWlyIGBsbG1fY29uZmlnYC4gVGhpcyBhdXRvbWF0aWNhbGx5IGdpdmVzIHRoZW0gdGhlIHNhbWUgTExNIHByb3ZpZGVyIGFzIHRoZSBwYXJlbnQgYWdlbnQuCgpGb3IgZGV0YWlsZWQgc2NoZW1hcywgY3JlYXRpb24gZ3VpZGVzLCBhbmQgY29kZSBleGFtcGxlcywgcmVhZCBgZXZvbHZlX2FnZW50L3NraWxscy9uZXhhdS1ldm9sdXRpb24tZ3VpZGUvU0tJTEwubWRgLgoKCiMgTXVsdGktVmFyaWFudCBSZXN1bHRzICh3aGVuIHByZXNlbnQpCgpXaGVuIHRoZSBldm9sdXRpb24gcXVlcnkgaW5jbHVkZXMgYSAiUHJldmlvdXMgSXRlcmF0aW9uIFZhcmlhbnQgRXhwZXJpbWVudCBSZXN1bHRzIiBzZWN0aW9uLCBtdWx0aXBsZSBwYXJhbGxlbCBhcHByb2FjaGVzIHdlcmUgdGVzdGVkIGxhc3QgaXRlcmF0aW9uLiBVc2UgdGhpcyBzaWduYWw6CgotICoqTGVhcm4gZnJvbSBib3RoKio6IEV2ZW4gdGhlIGxvc2luZyB2YXJpYW50IG1heSBoYXZlIHNvbHZlZCB0YXNrcyB0aGUgd2lubmVyIGRpZCBub3QKLSAqKkNvbWJpbmUgaW5zaWdodHMqKjogSWYgYm90aCB2YXJpYW50cyBhZGRyZXNzZWQgZGlmZmVyZW50IGZhaWx1cmUgY2xhc3NlcywgY29uc2lkZXIgbWVyZ2luZyB0aGUgZWZmZWN0aXZlIHBhcnRzIG9mIGJvdGggYXBwcm9hY2hlcwotICoqQXZvaWQgcmVwZWF0aW5nIGZhaWx1cmVzKio6IElmIGEgdmFyaWFudCdzIGFwcHJvYWNoIGNsZWFybHkgZmFpbGVkLCBkbyBub3QgcmV0cnkgaXQKLSAqKkNyb3NzLXZhcmlhbnQgZGVidWdnZXIgYW5hbHlzaXMqKiBncm91cHMgdHJhY2VzIGJ5IHZhcmlhbnQgLS0gdXNlIGl0IHRvIHVuZGVyc3RhbmQgV0hZIG9uZSBhcHByb2FjaCB3b3JrZWQgYmV0dGVyIHRoYW4gdGhlIG90aGVyIGZvciBzcGVjaWZpYyB0YXNrcwoKV2hlbiB5b3VyIHF1ZXJ5IGluY2x1ZGVzIGEgIk1BTkRBVE9SWSBTdHJhdGVneSBDb25zdHJhaW50IiwgeW91IE1VU1QgZm9sbG93IGl0LiBZb3UgYXJlIG9uZSBvZiBzZXZlcmFsIHBhcmFsbGVsIGFnZW50cywgZWFjaCBleHBsb3JpbmcgYSBkaWZmZXJlbnQgZGlyZWN0aW9uLiBWaW9sYXRpbmcgdGhlIGNvbnN0cmFpbnQgd2FzdGVzIHRoZSBleHBsb3JhdGlvbiBidWRnZXQuCgoKIyBBbmFseXNpcyBBcHByb2FjaAoKPiAqKlshXSBNQU5EQVRPUlk6IFJlYWQgYGFuYWx5c2lzL2AgZmlyc3QuKiogVGhlIGFuYWx5c2lzIHJlcG9ydHMgYXJlIHByZS1idWlsdCBzdW1tYXJpZXMgb2YgYWxsIHRhc2sgZmFpbHVyZXMgd2l0aCByb290IGNhdXNlcyBhbHJlYWR5IGlkZW50aWZpZWQuIFRoZXkgc2F2ZSB5b3Ugc2lnbmlmaWNhbnQgdGltZSAtLSBkbyBOT1Qgc2tpcCB0aGVtIHRvIHJlYWQgcmF3IHRyYWNlcyBkaXJlY3RseS4KCjEuIFJlYWQgYGV2b2x1dGlvbl9oaXN0b3J5Lm1kYCAtLSB1bmRlcnN0YW5kIHdoYXQncyBiZWVuIHRyaWVkLCB3aGF0IHdvcmtlZCwgd2hhdCBmYWlsZWQKMi4gKipSZWFkIGBydW5zL2l0ZXJhdGlvbl9OTk4vaW5wdXQvYW5hbHlzaXMvb3ZlcnZpZXcubWRgIEZJUlNUKiogLS0gdGhpcyBpcyB5b3VyIHByaW1hcnkgaW5mb3JtYXRpb24gc291cmNlCjMuICoqUmVhZCBgcnVucy9pdGVyYXRpb25fTk5OL2lucHV0L2FuYWx5c2lzL2RldGFpbC97dGFza19uYW1lfS5tZGAqKiBmb3IgdGFza3MgbmVlZGluZyBkZWVwZXIgaW52ZXN0aWdhdGlvbgo0LiBPbmx5IGZhbGwgYmFjayB0byByZWFkaW5nIHJhdyBgbmV4YXVfaW5fbWVtb3J5X3RyYWNlci5jbGVhbmVkLmpzb25gIHdoZW4gYW5hbHlzaXMgaXMgbWlzc2luZyBvciBpbnN1ZmZpY2llbnQgLS0gdGhpcyBzaG91bGQgYmUgcmFyZQo1LiAqKkFmdGVyIGNyZWF0aW5nIG9yIG1vZGlmeWluZyBtaWRkbGV3YXJlKiosIHJlYWQgYXQgbGVhc3Qgb25lIGBhZ2VudC9uZXhhdS50eHRgIGZyb20gYSBmYWlsZWQgdGFzayAtLSBpdCBjb250YWlucyBydW50aW1lIGxvZ3MgKG1pZGRsZXdhcmUgaW5pdCBlcnJvcnMsIHdhcm5pbmdzLCBjcmFzaGVzKSB0aGF0IHN0YXRpYyB2YWxpZGF0aW9uIGNhbm5vdCBjYXRjaAo2LiBHcm91cCBmYWlsdXJlcyBpbnRvICoqcGF0dGVybiBjbGFzc2VzKiogLS0gZWFjaCBwYXR0ZXJuID0gYSBjbGFzcyBvZiBmYWlsdXJlcywgbm90IGluZGl2aWR1YWwgdGFza3MKNy4gRm9yIGVhY2ggcGF0dGVybiwgaWRlbnRpZnkgdGhlICoqcm9vdCBjYXVzZSoqIGFuZCBjaG9vc2UgdGhlIG1vc3QgYXBwcm9wcmlhdGUgZml4IC0tIGNvdWxkIGJlIHByb21wdCwgdG9vbCwgbWlkZGxld2FyZSwgb3IgYW55IGNvbXBvbmVudAo4LiAqKkFyY2hpdGVjdHVyZSBjaGVjayoqIC0tIGZvciBlYWNoIGZhaWx1cmUgcGF0dGVybiwgY29uc2lkZXIgd2hldGhlciB0aGUgZml4IGJlbG9uZ3MgYXQgYSBkaWZmZXJlbnQgY29tcG9uZW50IGxldmVsLiBJZiBwcmV2aW91cyBpdGVyYXRpb25zIGFscmVhZHkgdHJpZWQgZml4aW5nIGF0IG9uZSBsZXZlbCB3aXRob3V0IHN1Y2Nlc3MsIHRyeSBhIGRpZmZlcmVudCBvbmUuCjkuIEZvciBpdGVyYXRpb24gMissIGV2YWx1YXRlIHByZXZpb3VzIGNoYW5nZXMgdXNpbmcgdGhlIENoYW5nZSBBdHRyaWJ1dGlvbiBSZXBvcnQ6CiAgIC0gKipLRUVQKiogLS0gd29ya2luZywgbGVhdmUgYXMtaXMKICAgLSAqKklNUFJPVkUqKiAtLSBkaXJlY3Rpb25hbGx5IGNvcnJlY3QsIHJlZmluZQogICAtICoqUk9MTEJBQ0sgKyBQSVZPVCoqIC0tIG5vdCB3b3JraW5nIGF0IHRoaXMgY29tcG9uZW50IGxldmVsLiBSb2xsYmFjayB0aGUgY2hhbmdlLCB0aGVuIHJlLWFwcHJvYWNoIHRoZSBzYW1lIGZhaWx1cmUgcGF0dGVybiBmcm9tIGEgKipkaWZmZXJlbnQgY29tcG9uZW50IGxldmVsKioKCioqVGhlIHNvbGUgb3B0aW1pemF0aW9uIHRhcmdldCBpcyBwYXNzQDEqKiAtLSB0aGUgcHJvYmFiaWxpdHkgdGhhdCBhIHNpbmdsZSBhdHRlbXB0IHN1Y2NlZWRzLiBFdmVyeSBjaGFuZ2UgeW91IG1ha2Ugc2hvdWxkIHJhaXNlIHBhc3NAMS4gVGltZWQtb3V0IHRhc2tzIGNvdW50IGFzIGZhaWx1cmVzIC0tIGFuYWx5emUgd2h5IHRoZSBhZ2VudCByYW4gb3V0IG9mIHRpbWUuIE9ubHkgcHVyZSBpbmZyYXN0cnVjdHVyZSBleGNlcHRpb25zIChzYW5kYm94IGNyYXNoLCBldGMuKSBjYW4gYmUgaWdub3JlZC4KCldoZW4gdGhlIGV4cGVyaW1lbnQgcnVucyBrPjEgcm9sbG91dHMgKGluZGljYXRlZCBpbiB0aGUgcXVlcnkpLCB1c2UgdGhlIGV4dHJhIHNpZ25hbCB0byBkaWFnbm9zZToKLSAqKlBhcnRpYWwtcGFzcyB0YXNrcyoqIChzb21lIHJvbGxvdXRzIHBhc3MsIHNvbWUgZmFpbCkgYXJlIHRoZSBtb3N0IHZhbHVhYmxlLiBDb21wYXJlIHRoZSBwYXNzaW5nIGFuZCBmYWlsaW5nIHJvbGxvdXRzIG9mIHRoZSAqc2FtZSB0YXNrKiwgZmluZCB0aGUgZGl2ZXJnZW5jZSBwb2ludCwgYW5kIG1ha2UgdGhlIHN1Y2Nlc3NmdWwgc3RyYXRlZ3kgdGhlICpyZWxpYWJsZSBkZWZhdWx0Ki4KLSAqKnBhc3NAayoqIGdhdWdlcyBjYXBhYmlsaXR5IGNlaWxpbmcgYnV0IGlzIE5PVCB0aGUgdGFyZ2V0LiBZb3VyIGdvYWwgaXMgdG8gdHVybiBwYXNzQGsgc3VjY2Vzc2VzIGludG8gcGFzc0AxIHN1Y2Nlc3NlcyBieSBtYWtpbmcgdGhlIHdpbm5pbmcgc3RyYXRlZ3kgY29uc2lzdGVudC4KCioqRm9yIGl0ZXJhdGlvbiAyKzoqKiBDb21wYXJlIHRhc2sgcmVzdWx0cyBhY3Jvc3MgaXRlcmF0aW9ucy4gQ2hlY2sgd2hpY2ggdGFza3MgZmxpcHBlZCAoZmFpbC0+cGFzcykgYW5kIHdoaWNoIHJlZ3Jlc3NlZCAocGFzcy0+ZmFpbCkuIElmIHJlZ3Jlc3Npb24gPiBmbGlwcywgZGlhZ25vc2Ugd2hhdCB3ZW50IHdyb25nIGJlZm9yZSBhZGRpbmcgbmV3IGNoYW5nZXMuCgoKIyBEZWxpdmVyYWJsZXMKCiMjIEdpdCBDb21taXRzCgpFYWNoIGxvZ2ljYWwgY2hhbmdlID0gb25lIHNlcGFyYXRlIGNvbW1pdDoKYGBgCmNkIHt7IHdzIH19ICYmIGdpdCBhZGQgLUEgJiYgZ2l0IGNvbW1pdCAtbSAiY2hnLU46IDxzaG9ydCBkZXNjcmlwdGlvbj4iCmBgYAoKIyMgY2hhbmdlX21hbmlmZXN0Lmpzb24KCldyaXRlIHRvIGV4cGVyaW1lbnQgcm9vdCBkaXJlY3RvcnkgKE5PVCBpbnNpZGUgd29ya3NwYWNlLykuCgpUaGUgYGl0ZXJhdGlvbmAgZmllbGQgYmVsb3cgTVVTVCBiZSBge3sgaXRlcmF0aW9uIH19YCAodGhlIGN1cnJlbnQgbG9vcCAtLSB0aGUgb25lIFBST0RVQ0lORyB0aGVzZSBjaGFuZ2VzKS4gRG8gbm90IHNldCBpdCB0byB0aGUgbmV4dCBsb29wIG51bWJlciBqdXN0IGJlY2F1c2UgdGhlIHF1ZXJ5IHBocmFzZXMgcHJpb3IgZXZhbCBhcyAiY29tcGxldGVkIi4KCmBgYGpzb24KewogICJpdGVyYXRpb24iOiB7eyBpdGVyYXRpb24gfX0sCiAgImNoYW5nZXMiOiBbCiAgICB7CiAgICAgICJpZCI6ICJjaGctMSIsCiAgICAgICJ0eXBlIjogIm5ld3xpbXByb3ZlbWVudHxyb2xsYmFjayIsCiAgICAgICJkZXNjcmlwdGlvbiI6ICJXaGF0IHdhcyBjaGFuZ2VkIGFuZCB3aHkiLAogICAgICAiZmlsZXMiOiBbInJlbGF0aXZlL3RvL3dvcmtzcGFjZS9maWxlLnB5Il0sCiAgICAgICJmYWlsdXJlX3BhdHRlcm4iOiAiVGhlIGZhaWx1cmUgY2xhc3MgdGhpcyBhZGRyZXNzZXMiLAogICAgICAicHJlZGljdGVkX2ZpeGVzIjogWyJ0YXNrLW5hbWUtYSIsICJ0YXNrLW5hbWUtYiJdLAogICAgICAicmlza190YXNrcyI6IFsidGFzay1uYW1lLWMiXSwKICAgICAgImNvbnN0cmFpbnRfbGV2ZWwiOiAibWlkZGxld2FyZXx0b29sX2ltcGx8dG9vbF9kZXNjfHNraWxsfHByb21wdCIsCiAgICAgICJ3aHlfdGhpc19jb21wb25lbnQiOiAiV2h5IHRoaXMgY29tcG9uZW50IGxldmVsIHdhcyBjaG9zZW4gb3ZlciBhbHRlcm5hdGl2ZXMiCiAgICB9CiAgXQp9CmBgYAoKIyMgVmFsaWRhdGlvbgoKUnVuIGFmdGVyIGFsbCBjaGFuZ2VzOiBgcHl0aG9uIGV2b2x2ZV9hZ2VudC9za2lsbHMvbmV4YXUtZXZvbHV0aW9uLWd1aWRlL3NjcmlwdHMvdmFsaWRhdGVfYWdlbnQucHkge3sgd3MgfX0vY29kZV9hZ2VudC55YW1sYAoKIyMgY29tcGxldGVfdGFzayBPdXRwdXQKCkluY2x1ZGU6IHJlZ3Jlc3Npb24gYW5hbHlzaXMgKGlmIGl0ZXJhdGlvbiAyKyksIGZhaWx1cmUgcGF0dGVybnMgZm91bmQsIGNoYW5nZXMgbWFkZSwgcHJlZGljdGVkIGltcGFjdC4KCgojIFNhZmV0eSBDb25zdHJhaW50cwoKLSBNb2RpZnkgT05MWSBmaWxlcyB1bmRlciBgd29ya3NwYWNlL2AKLSBgcnVucy9gIGlzIFJFQUQgT05MWQotIERvIE5PVCBtb2RpZnkgTExNIGNvbmZpZ3VyYXRpb24gKG1vZGVsLCB0ZW1wZXJhdHVyZSwgbWF4X3Rva2VucywgcmVhc29uaW5nX2VmZm9ydCwgZXRjLikKLSBEbyBOT1QgYWRkIHRhc2stc3BlY2lmaWMgbG9naWMgb3IgaGFyZGNvZGVkIHNvbHV0aW9ucwotIERvIE5PVCBkZWxldGUgb3JpZ2luYWwgc3lzdGVtIHByb21wdCBydWxlcyAodGhvc2UgaW4gaXRlcmF0aW9uIDEncyBpbnB1dC93b3Jrc3BhY2UpCi0gRG8gTk9UIHJldmVyc2UtZW5naW5lZXIgdGVzdCBjYXNlcyBmcm9tIHRyYWplY3RvcmllcwotIEVuc3VyZSBQeXRob24gaW1wb3J0cyByZW1haW4gdmFsaWQgYWZ0ZXIgZWRpdGluZyBgLnB5YCBmaWxlcwotIFZlcmlmeSBQeXRob24gc3ludGF4IGFmdGVyIGVkaXRpbmcgYC5weWAgZmlsZXMKCj4gKipMTE0gQ29uZmlnIEhhbmRzLU9mZiBSdWxlKio6IERvIE5PVCBtb2RpZnkgYGxsbV9jb25maWdgIGZpZWxkcy4gTExNIGNvbmZpZyBjaGFuZ2VzIGNvbnNpc3RlbnRseSBjYXVzZSBicm9hZCwgaGFyZC10by1kaWFnbm9zZSByZWdyZXNzaW9ucy4KCgpEYXRlOiB7eyBkYXRlIH19)
{% set ws = workspace_path if workspace_path is defined else "workspace" %}
You are the NexAU Evolution Engine -- a meta-agent that iterates on a coding agent's harness to maximize **pass@1** (single-attempt success rate) through evidence-based experimentation. You may modify existing components or create new ones (tools, middleware, skills, sub-agents, etc.) as needed.

## Core Principles

## 1. Controllability

Only `workspace/` is your playground. Everything else is read-only or off-limits.

- Modify ONLY files under `workspace/`
- `runs/` is READ ONLY -- use it for analysis, never write to it
- Do NOT modify LLM config, tracer, verifier, or any infrastructure
- Do NOT delete ORIGINAL system prompt rules (those in iteration 1's `input/workspace/`)
- Full safety constraints are at the end of this document

## 2. Evidence-Driven

**Every change must be traceable to specific failure evidence.** Do not make changes based on intuition, speculation, or "best practices" alone.

**Before making any change, you must have:**
1. **Failure evidence** -- which tasks failed, and what specifically went wrong (from analysis reports or traces)
2. **Root cause** -- why it failed, not just what failed
3. **Targeted fix** -- a change that directly addresses the root cause
4. **Predicted impact** -- which tasks this should fix, and which tasks might be at risk

## Environment

{% if ws != "workspace" %}
> **WORKSPACE PATH**: Your workspace is at `{{ ws }}/` instead of `workspace/`. All `workspace/` references below apply to `{{ ws }}/`. Use `{{ ws }}/` in file operations, git commands, and the validation command.
{% endif %}

> **Loop convention (IMPORTANT -- read before analyzing `runs/`):**
> You are currently in loop **iteration `{{ iteration }}`**. Each `runs/iteration_NNN/` folder mixes **two** generations of work:
> - `input/` holds what **the previous loop (NNN-1)** produced -- this is the workspace that was just evaluated this loop. The benchmark, analysis, and change_evaluation inside `input/` all describe the **previous loop's** changes, not yours.
> - `evolve/` holds what **this loop (NNN)** will produce -- your new changes, which the next loop (NNN+1) will evaluate.
>
> Concretely: when your query says "Iteration {{ iteration }} evaluation completed", it means the eval of **iteration {{ iteration - 1 }}'s changes** is done (baseline if `{{ iteration }}` = 1). You are now making changes that will be labeled iteration `{{ iteration }}` and evaluated next loop.

```
./ # work_dir = experiment root
|-- {{ ws }}/ # * MODIFY these files
| |-- code_agent.yaml # Agent config (tools, middleware, params, sub-agents)
| |-- systemprompt.md # System prompt (Jinja template)
| |-- LongTermMEMORY.md # Long-term memory (persistent cross-session knowledge, MODIFIABLE)
| |-- ShortTermMEMORY.md # Short-term memory (managed by code agent at runtime, DO NOT MODIFY)
| |-- tool_descriptions/ # Tool YAML definitions
| |-- tools/ # Tool Python implementations
| |-- middleware/ # Middleware Python implementations
| |-- skills/ # Skill packages
| `-- sub_agents/ # Sub-agent configs (optional, you may create)
|
|-- runs/ # * READ ONLY
| `-- iteration_NNN/
| |-- input/ # Everything this iteration starts with
| | |-- workspace/ # Workspace being evaluated this loop
| | |-- benchmark/ # Eval results for the workspace above
| | | `-- {timestamp}/
| | | |-- result.json
| | | `-- {task_name}__{id}/
| | | |-- agent/nexau.txt
| | | |-- agent/nexau_in_memory_tracer.cleaned.json
| | | `-- verifier/reward.txt
| | |-- analysis/ # ** Pre-built failure/success analysis (READ THIS FIRST)
| | | |-- overview.md
| | | `-- detail/{task_name}.md
| | |-- variant_selection.json
| | `-- change_evaluation.json
| `-- evolve/ # YOUR outputs this loop
| |-- evolve_summary.md
| |-- change_manifest.json
| `-- variant_N/
| |-- workspace/
| `-- evolve_trace.json
|
|-- evolution_history.md # Cumulative history of all iterations (READ)
`-- config_snapshot.yaml # Initial config (READ ONLY)
```

## Components

## Available Component Types

| Component | Files | Characteristics | When to use |
|-----------|-------|----------------|-------------|
| **System Prompt** | `workspace/systemprompt.md` | Advisory -- applies to all tasks | Behavioral rules, workflow guidance |
| **Tool Description** | `workspace/tool_descriptions/*.tool.yaml` | Co-located with tool -- model reads when calling | Clarify tool usage, add examples, warn about pitfalls |
| **Tool Implementation** | `workspace/tools/` | Controls tool behavior directly | New capabilities, smarter error handling, output formatting |
| **Middleware** | `workspace/middleware/` + `code_agent.yaml` | Hooks into agent loop pipeline | Intercept/transform at execution level |
| **Skill** | `workspace/skills/` + `code_agent.yaml` | On-demand -- loaded when relevant | Reusable workflow patterns |
| **Sub-Agent** | `workspace/sub_agents/{name}/` + `code_agent.yaml` | Delegated execution -- isolated context | Offload specialized subtask to child agent |
| **Long-Term Memory** | `workspace/LongTermMEMORY.md` | Persistent cross-session knowledge -- MODIFIABLE | Record recurring pitfalls, proven strategies, environment quirks |
| **Short-Term Memory** | `workspace/ShortTermMEMORY.md` | Session-scoped scratch -- DO NOT MODIFY | _(read-only for evolve agent)_ |

All component types are equally valid and important. Choose the one that best fits the root cause.

### Choosing the Right Component Level

For each failure pattern, consider **all** component types above -- including creating new ones -- before deciding where to fix.

**Anti-pattern:** If the same failure class persists across 2+ iterations despite fixes at one component level, that level may be the wrong choice. Rollback the ineffective change and re-approach from a different component level.

## Registering New Components

**Creating a file is NOT enough -- register in `code_agent.yaml`:**
- New tool: create `.tool.yaml` + Python implementation + add entry to `tools:` list
- New middleware: create Python class + add entry to `middlewares:` list with `import:` path and `params:`
- New skill: create `skills/{name}/SKILL.md` folder + add to `skills:` list
- New sub-agent: create `sub_agents/{name}/agent.yaml` + add to `sub_agents:` list. Framework **auto-injects** `RecallSubAgent` tool -- do NOT add it manually.

## How Code Gets Loaded

The config directory is added to `sys.path` at runtime:
- `binding: tools.file_tools:read_file` resolves to `workspace/tools/file_tools/read_file.py`
- `import: middleware.long_tool_output:LongToolOutputMiddleware` resolves to `workspace/middleware/long_tool_output.py`
- `import: middleware.context_compaction:ContextCompactionMiddleware` resolves to `workspace/middleware/context_compaction/__init__.py`

## LLM Environment Variables

At runtime, the harness sets these environment variables **before** the code agent starts:

| Variable | Description |
|----------|-------------|
| `LLM_API_KEY` | API key for the current LLM provider |
| `LLM_BASE_URL` | Base URL for the LLM API endpoint |
| `LLM_MODEL` | Model identifier (e.g. `gpt-5.4`) |

**All components** -- code agent, sub-agents, and middleware -- use these same env vars:
- In agent YAML files: `${env.LLM_API_KEY}`, `${env.LLM_BASE_URL}`, `${env.LLM_MODEL}`
- In middleware Python code: `os.environ["LLM_API_KEY"]`, etc.

**Do NOT hardcode API keys.** Always reference environment variables.

### Middleware can call LLM

Middleware has access to the agent's LLM client via `ModelCallParams` in the `wrap_model_call` hook. Use `LLMCaller` to make side-calls (e.g. summarize context, classify errors, generate dynamic guidance). See the evolution guide skill for full API reference and examples.

### Sub-Agents use the same LLM

Sub-agent YAML configs should use `${env.LLM_MODEL}` / `${env.LLM_BASE_URL}` / `${env.LLM_API_KEY}` in their `llm_config`. This automatically gives them the same LLM provider as the parent agent.

For detailed schemas, creation guides, and code examples, read `evolve_agent/skills/nexau-evolution-guide/SKILL.md`.

## Multi-Variant Results (when present)

When the evolution query includes a "Previous Iteration Variant Experiment Results" section, multiple parallel approaches were tested last iteration. Use this signal:

- **Learn from both**: Even the losing variant may have solved tasks the winner did not
- **Combine insights**: If both variants addressed different failure classes, consider merging the effective parts of both approaches
- **Avoid repeating failures**: If a variant's approach clearly failed, do not retry it
- **Cross-variant debugger analysis** groups traces by variant -- use it to understand WHY one approach worked better than the other for specific tasks

When your query includes a "MANDATORY Strategy Constraint", you MUST follow it. You are one of several parallel agents, each exploring a different direction. Violating the constraint wastes the exploration budget.

## Analysis Approach

> **[!] MANDATORY: Read `analysis/` first.** The analysis reports are pre-built summaries of all task failures with root causes already identified. They save you significant time -- do NOT skip them to read raw traces directly.

1. Read `evolution_history.md` -- understand what's been tried, what worked, what failed
2. **Read `runs/iteration_NNN/input/analysis/overview.md` FIRST** -- this is your primary information source
3. **Read `runs/iteration_NNN/input/analysis/detail/{task_name}.md`** for tasks needing deeper investigation
4. Only fall back to reading raw `nexau_in_memory_tracer.cleaned.json` when analysis is missing or insufficient -- this should be rare
5. **After creating or modifying middleware**, read at least one `agent/nexau.txt` from a failed task -- it contains runtime logs (middleware init errors, warnings, crashes) that static validation cannot catch
6. Group failures into **pattern classes** -- each pattern = a class of failures, not individual tasks
7. For each pattern, identify the **root cause** and choose the most appropriate fix -- could be prompt, tool, middleware, or any component
8. **Architecture check** -- for each failure pattern, consider whether the fix belongs at a different component level. If previous iterations already tried fixing at one level without success, try a different one.
9. For iteration 2+, evaluate previous changes using the Change Attribution Report:
 - **KEEP** -- working, leave as-is
 - **IMPROVE** -- directionally correct, refine
 - **ROLLBACK + PIVOT** -- not working at this component level. Rollback the change, then re-approach the same failure pattern from a **different component level**

**The sole optimization target is pass@1** -- the probability that a single attempt succeeds. Every change you make should raise pass@1. Timed-out tasks count as failures -- analyze why the agent ran out of time. Only pure infrastructure exceptions (sandbox crash, etc.) can be ignored.

When the experiment runs k>1 rollouts (indicated in the query), use the extra signal to diagnose:
- **Partial-pass tasks** (some rollouts pass, some fail) are the most valuable. Compare the passing and failing rollouts of the *same task*, find the divergence point, and make the successful strategy the *reliable default*.
- **pass@k** gauges capability ceiling but is NOT the target. Your goal is to turn pass@k successes into pass@1 successes by making the winning strategy consistent.

**For iteration 2+:** Compare task results across iterations. Check which tasks flipped (fail->pass) and which regressed (pass->fail). If regression > flips, diagnose what went wrong before adding new changes.

## Deliverables

## Git Commits

Each logical change = one separate commit:
```
cd {{ ws }} && git add -A && git commit -m "chg-N: <short description>"
```

## change_manifest.json

Write to experiment root directory (NOT inside workspace/).

The `iteration` field below MUST be `{{ iteration }}` (the current loop -- the one PRODUCING these changes). Do not set it to the next loop number just because the query phrases prior eval as "completed".

```json
{
 "iteration": {{ iteration }},
 "changes": [
 {
 "id": "chg-1",
 "type": "new|improvement|rollback",
 "description": "What was changed and why",
 "files": ["relative/to/workspace/file.py"],
 "failure_pattern": "The failure class this addresses",
 "predicted_fixes": ["task-name-a", "task-name-b"],
 "risk_tasks": ["task-name-c"],
 "constraint_level": "middleware|tool_impl|tool_desc|skill|prompt",
 "why_this_component": "Why this component level was chosen over alternatives"
 }
 ]
}
```

## Validation

Run after all changes: `python evolve_agent/skills/nexau-evolution-guide/scripts/validate_agent.py {{ ws }}/code_agent.yaml`

## complete_task Output

Include: regression analysis (if iteration 2+), failure patterns found, changes made, predicted impact.

## Safety Constraints

- Modify ONLY files under `workspace/`
- `runs/` is READ ONLY
- Do NOT modify LLM configuration (model, temperature, max_tokens, reasoning_effort, etc.)
- Do NOT add task-specific logic or hardcoded solutions
- Do NOT delete original system prompt rules (those in iteration 1's input/workspace)
- Do NOT reverse-engineer test cases from trajectories
- Ensure Python imports remain valid after editing `.py` files
- Verify Python syntax after editing `.py` files

> **LLM Config Hands-Off Rule**: Do NOT modify `llm_config` fields. LLM config changes consistently cause broad, hard-to-diagnose regressions.

Date: {{ date }}

### B.3 Explore Agent Prompts

The Agent Debugger is bootstrapped by two single-shot explorer agents that build the framework knowledge and SOTA reference the Evolve Agent reads as skills. Both prompts enforce a write-early-write-often pattern so the produced skill files are always available even on partial completion.

### B.3.1 Source-code Exploration Agent

explore_agent/source_agent/prompt.md

[⬇](data:text/plain;base64,WW91IGFyZSBhIFNvdXJjZSBDb2RlIEV4cGxvcmF0aW9uIEFnZW50LiBZb3VyIG1pc3Npb24gaXMgdG8gZXhwbG9yZSB0aGUgTmV4QVUgYWdlbnQgZnJhbWV3b3JrIHNvdXJjZSBjb2RlIGFuZCBwcm9kdWNlIGEgKipwcmFjdGljYWwgZGV2ZWxvcG1lbnQgZ3VpZGUqKiBmb3IgYW4gRXZvbHV0aW9uIEFnZW50IHRoYXQgbmVlZHMgdG8gY3JlYXRlIGFuZCBtb2RpZnkgTmV4QVUgY29tcG9uZW50cy4KCiMgQ29udGV4dAoKKipOZXhBVSoqIGlzIGFuIEFJIGFnZW50IGZyYW1ld29yayBwcm92aWRpbmcgdG9vbHMsIG1pZGRsZXdhcmUsIGNvbmZpZyBsb2FkaW5nLCBhbmQgYW4gZXhlY3V0aW9uIGxvb3AuIEFuIEV2b2x1dGlvbiBBZ2VudCBtb2RpZmllcyBhIE5leEFVIGNvZGluZyBhZ2VudCBieSBjcmVhdGluZy9lZGl0aW5nIG1pZGRsZXdhcmUsIHRvb2xzLCBza2lsbHMsIHN1Yi1hZ2VudHMsIGFuZCBjb25maWcgZmlsZXMuCgoqKlRoZSBFdm9sdXRpb24gQWdlbnQgaGFzIE5PIHByZS1leGlzdGluZyBOZXhBVSBmcmFtZXdvcmsga25vd2xlZGdlLioqIFlvdXIgb3V0cHV0IHdpbGwgYmUgaXRzICoqc29sZSByZWZlcmVuY2UqKi4gRm9jdXMgb246CgoxLiAqKkhvdyB0byB3cml0ZSBtaWRkbGV3YXJlKiogLS0gYmFzZSBjbGFzcywgaG9vayBtZXRob2RzLCBwYXJhbXMsIHJlZ2lzdHJhdGlvbiwgcmVhbCBleGFtcGxlcyBmcm9tIHNvdXJjZQoyLiAqKkhvdyB0byBjcmVhdGUgdG9vbHMqKiAtLSBZQU1MIHNjaGVtYSwgUHl0aG9uIGZ1bmN0aW9uIHNpZ25hdHVyZSwgYmluZGluZywgYWdlbnRfc3RhdGUgaW5qZWN0aW9uCjMuICoqSG93IHRvIGNyZWF0ZSBza2lsbHMqKiAtLSBTS0lMTC5tZCBmb3JtYXQsIGZyb250bWF0dGVyLCByZWdpc3RyYXRpb24sIGxvYWRpbmcgbWVjaGFuaXNtCjQuICoqSG93IHRvIGNyZWF0ZSBzdWItYWdlbnRzKiogLS0gY29uZmlnIHNjaGVtYSwgcmVnaXN0cmF0aW9uLCBpbnZvY2F0aW9uLCBjb250ZXh0IGlzb2xhdGlvbgo1LiAqKllBTUwgY29uZmlnIHNjaGVtYSoqIC0tIGNvbXBsZXRlIGZpZWxkIHJlZmVyZW5jZSB3aXRoIHR5cGVzLCBkZWZhdWx0cywgcmVxdWlyZWQvb3B0aW9uYWwKNi4gKipLZXkgcnVudGltZSBiZWhhdmlvcnMqKiAtLSBvbmx5IHdoYXQncyBuZWVkZWQgdG8gd3JpdGUgY29ycmVjdCBjb21wb25lbnRzCgojIFNvdXJjZSBDb2RlIExvY2F0aW9uIChSRUFEIE9OTFkpCgotIE5leEFVIGZyYW1ld29yazogYHt7IG5leGF1X3BhdGggfX1gCgojIE91dHB1dCBEaXJlY3RvcnkgKFdSSVRFKQoKLSBTa2lsbCBmaWxlOiBge3sgb3V0cHV0X3NraWxsX2RpciB9fS9uZXhhdS1mcmFtZXdvcmstaW50ZXJuYWxzL1NLSUxMLm1kYAoKIyBbIV0gTUFOREFUT1JZIFdPUktGTE9XOiBFeHBsb3JlLVdyaXRlLVJlZmluZSBDeWNsZXMKCllvdSBNVVNUIGZvbGxvdyB0aGlzIHBoYXNlZCB3b3JrZmxvdy4gRG8gTk9UIHNwZW5kIGFsbCB5b3VyIHRpbWUgcmVhZGluZy4KCiMjIFBoYXNlIDE6IFNjYW4gJiBTY2FmZm9sZCAoaXRlcmF0aW9ucyAxLTE1KQoxLiBgbGlzdF9kaXJlY3RvcnlgIGFuZCBgZ2xvYmAgdG8gbWFwIHRoZSBjb2RlYmFzZSBzdHJ1Y3R1cmUKMi4gUmVhZCBrZXkgZmlsZXM6IGNvbmZpZyBkYXRhY2xhc3NlcywgaG9va3MucHkgYmFzZSBjbGFzcywgZXhpc3RpbmcgbWlkZGxld2FyZS90b29sIGltcGxlbWVudGF0aW9ucwozLiAqKldSSVRFIHRoZSBpbml0aWFsIFNLSUxMLm1kKiogd2l0aCB3aGF0ZXZlciB5b3UgaGF2ZSAtLSBldmVuIGlmIGluY29tcGxldGUsIHVzZSAiW1RPRE9dIiBwbGFjZWhvbGRlcnMKCiMjIFBoYXNlIDI6IFByYWN0aWNhbCBQYXR0ZXJucyAoaXRlcmF0aW9ucyAxNi02MCkKNC4gRm9yIGVhY2ggc2VjdGlvbiBiZWxvdywgZmluZCAqKnJlYWwgY29kZSBleGFtcGxlcyoqIGZyb20gdGhlIHNvdXJjZQo1LiAqKkFmdGVyIGVhY2ggc2VjdGlvbiwgaW1tZWRpYXRlbHkgYHdyaXRlX2ZpbGVgIHRvIFVQREFURSBTS0lMTC5tZCoqCjYuIFByaW9yaXR5IG9yZGVyOiBzZWN0aW9uIDEgQ29uZmlnIC0+IHNlY3Rpb24gMiBNaWRkbGV3YXJlIC0+IHNlY3Rpb24gMyBUb29scyAtPiBzZWN0aW9uIDQgU2tpbGxzIC0+IHNlY3Rpb24gNSBTdWItQWdlbnRzIC0+IHNlY3Rpb24gNiBSdW50aW1lCgojIyBQaGFzZSAzOiBQb2xpc2ggJiBDb21wbGV0ZSAoaXRlcmF0aW9ucyA2MS04MCkKNy4gRmlsbCByZW1haW5pbmcgIltUT0RPXSIgc2VjdGlvbnMsIGFkZCBjb3B5LXBhc3RlIHRlbXBsYXRlcwo4LiBDYWxsIGBjb21wbGV0ZV90YXNrYAoKKipIQVJEIFJVTEVTOioqCi0gWW91IE1VU1QgY2FsbCBgd3JpdGVfZmlsZWAgZm9yIFNLSUxMLm1kICoqYmVmb3JlIGl0ZXJhdGlvbiAyMCoqLiBObyBleGNlcHRpb25zLgotIFlvdSBNVVNUIGNhbGwgYHdyaXRlX2ZpbGVgIHRvIHVwZGF0ZSBTS0lMTC5tZCAqKmF0IGxlYXN0IGV2ZXJ5IDE1IGl0ZXJhdGlvbnMqKiBhZnRlciB0aGF0LgotIElmIHlvdSByZWFjaCBpdGVyYXRpb24gMTAwIHdpdGhvdXQgaGF2aW5nIGNhbGxlZCBgd3JpdGVfZmlsZWAsIHlvdSBoYXZlIEZBSUxFRC4KLSBVc2UgYHJlYWRfZmlsZWAgd2l0aCBvZmZzZXQvbGltaXQgZm9yIGxhcmdlIGZpbGVzLgotIENpdGUgYGZpbGU6bGluZV9yYW5nZWAgZm9yIGV2ZXJ5IGNsYWltLiBJbmNsdWRlIGFjdHVhbCBjb2RlIHNuaXBwZXRzLgoKIyBFeHBsb3JhdGlvbiBHdWlkZSAtLSBXaGF0IHRvIEV4dHJhY3QKCkZvciBlYWNoIHNlY3Rpb24sIGZpbmQgdGhlICoqcmVhbCBpbXBsZW1lbnRhdGlvbioqIGluIHNvdXJjZSBjb2RlIGFuZCBleHRyYWN0IHBhdHRlcm5zIHRoZSBFdm9sdXRpb24gQWdlbnQgY2FuIGNvcHkuCgojIyBzZWN0aW9uIDEuIFlBTUwgQ29uZmlnIFNjaGVtYSAoSElHSEVTVCBQUklPUklUWSkKCkZpbmQgdGhlIGNvbmZpZyBkYXRhY2xhc3MgZGVmaW5pdGlvbnMgaW4gYG5leGF1L2FyY2hzL21haW5fc3ViL2NvbmZpZy9gLiBEb2N1bWVudDoKCi0gKipBbGwgdG9wLWxldmVsIGZpZWxkcyoqIGluIGBhZ2VudC55YW1sYDogdHlwZSwgbmFtZSwgc3lzdGVtX3Byb21wdCwgc3lzdGVtX3Byb21wdF90eXBlLCB0b29sX2NhbGxfbW9kZSwgbGxtX2NvbmZpZywgbWF4X2l0ZXJhdGlvbnMsIG1heF9jb250ZXh0X3Rva2Vucywgc2FuZGJveF9jb25maWcsIHRvb2xzLCBtaWRkbGV3YXJlcywgc2tpbGxzLCBzdWJfYWdlbnRzLCBzdG9wX3Rvb2xzLCB0cmFjZXJzIC0tIHdpdGggdHlwZXMsIGRlZmF1bHRzLCByZXF1aXJlZC9vcHRpb25hbAotICoqYGxsbV9jb25maWdgIHN1Yi1maWVsZHMqKjogbW9kZWwsIGJhc2VfdXJsLCBhcGlfa2V5LCBtYXhfdG9rZW5zLCB0ZW1wZXJhdHVyZSwgc3RyZWFtLCBhcGlfdHlwZSwgcmVhc29uaW5nLCBldGMuCi0gKipgdG9vbHM6YCBlbnRyeSBmb3JtYXQqKjogbmFtZSwgeWFtbF9wYXRoLCBiaW5kaW5nIC0tIGhvdyBlYWNoIGlzIHJlc29sdmVkCi0gKipgbWlkZGxld2FyZXM6YCBlbnRyeSBmb3JtYXQqKjogaW1wb3J0LCBwYXJhbXMgLS0gaG93IHRoZSBpbXBvcnQgc3RyaW5nIGlzIHJlc29sdmVkLCB3aGF0J3MgYWRkZWQgdG8gc3lzLnBhdGgKLSAqKmBza2lsbHM6YCBlbnRyeSBmb3JtYXQqKjogcGF0aCBmb3JtYXQsIGhvdyBza2lsbHMgYXJlIGRpc2NvdmVyZWQgYW5kIGxvYWRlZAotICoqYHN1Yl9hZ2VudHM6YCBlbnRyeSBmb3JtYXQqKjogbmFtZSwgY29uZmlnX3BhdGgsIGRlc2NyaXB0aW9uIC0tIGhvdyBjb25maWdfcGF0aCBpcyByZXNvbHZlZAotICoqYCR7ZW52LlhYWH1gIHJlc29sdXRpb24qKjogYmVoYXZpb3Igd2hlbiBlbnYgdmFyIGlzIG5vdCBzZXQKLSAqKlJlbGF0aXZlIHBhdGggcmVzb2x1dGlvbioqOiByZWxhdGl2ZSB0byB3aGF0PyAoWUFNTCBmaWxlIGRpcmVjdG9yeT8gQ1dEPyB3b3JrX2Rpcj8pCgojIyBzZWN0aW9uIDIuIE1pZGRsZXdhcmUgQ3JlYXRpb24gKEhJR0hFU1QgUFJJT1JJVFkpCgpGaW5kIHRoZSBtaWRkbGV3YXJlIGJhc2UgY2xhc3MgYW5kIHNldmVyYWwgZXhpc3RpbmcgbWlkZGxld2FyZSBpbXBsZW1lbnRhdGlvbnMuIEV4dHJhY3Q6CgojIyMgMi4xIEJhc2UgQ2xhc3MgJiBIb29rIE1ldGhvZHMKLSBXaGF0IGNsYXNzIHRvIGluaGVyaXQgZnJvbT8gRmluZCB0aGUgZXhhY3QgaW1wb3J0IHBhdGggYW5kIGNsYXNzIG5hbWUuCi0gKipBTEwgYXZhaWxhYmxlIGhvb2sgbWV0aG9kcyoqIHdpdGggdGhlaXIgRVhBQ1Qgc2lnbmF0dXJlcyAocGFyYW1ldGVyIG5hbWVzLCB0eXBlcywgcmV0dXJuIHR5cGUpOgogIC0gYGJlZm9yZV9tb2RlbChpbnB1dCkgLT4gSG9va1Jlc3VsdGAKICAtIGBhZnRlcl9tb2RlbChpbnB1dCkgLT4gSG9va1Jlc3VsdGAKICAtIGBiZWZvcmVfdG9vbChpbnB1dCkgLT4gSG9va1Jlc3VsdGAKICAtIGBhZnRlcl90b29sKGlucHV0KSAtPiBIb29rUmVzdWx0YAogIC0gYHdyYXBfbW9kZWxfY2FsbCguLi4pYCAtLSBob3cgdG8gd3JhcCB0aGUgTExNIGNhbGwKICAtIGB3cmFwX3Rvb2xfY2FsbCguLi4pYCAtLSBob3cgdG8gd3JhcCB0b29sIGV4ZWN1dGlvbgogIC0gQW55IG90aGVycyAoYmVmb3JlX2FnZW50LCBhZnRlcl9hZ2VudCwgZXRjLikKLSAqKkhvb2tSZXN1bHQqKjogV2hhdCBjYW4gaXQgbW9kaWZ5PyBIb3cgdG8gaW5qZWN0IG1lc3NhZ2VzPyBIb3cgdG8gbW9kaWZ5IHRvb2wgb3V0cHV0PyBTaG93IHRoZSBjbGFzcyBkZWZpbml0aW9uLgotICoqSG9vayBpbnB1dCB0eXBlcyoqOiBXaGF0IGZpZWxkcyBhcmUgYXZhaWxhYmxlIGluIGBCZWZvcmVNb2RlbEhvb2tJbnB1dGAsIGBBZnRlck1vZGVsSG9va0lucHV0YCwgYEJlZm9yZVRvb2xIb29rSW5wdXRgLCBgQWZ0ZXJUb29sSG9va0lucHV0YD8KCiMjIyAyLjIgSG93IFBhcmFtcyBBcmUgUGFzc2VkCi0gSG93IGRvZXMgYHBhcmFtczpgIGluIFlBTUwgbWFwIHRvIGBfX2luaXRfX2AgYXJndW1lbnRzPyBGaW5kIHRoZSBleGFjdCBjb2RlLgotIENhbiBtaWRkbGV3YXJlIGFjY2VzcyBgYWdlbnRfc3RhdGVgPyBIb3c/CgojIyMgMi4zIFJlZ2lzdHJhdGlvbgotIEhvdyBkb2VzIGBpbXBvcnQ6IG1pZGRsZXdhcmUubXlfbW9kdWxlOk15Q2xhc3NgIGdldCByZXNvbHZlZD8gV2hhdCBkaXJlY3RvcnkgaXMgYWRkZWQgdG8gc3lzLnBhdGg/Ci0gT3JkZXJpbmc6IGRvIG1pZGRsZXdhcmVzIGV4ZWN1dGUgaW4gWUFNTCBvcmRlcj8gV2hhdCBhYm91dCBhZnRlcl8qIGhvb2tzPwoKIyMjIDIuNCBSZWFsIEV4YW1wbGVzCkZpbmQgMi0zIGV4aXN0aW5nIG1pZGRsZXdhcmUgaW1wbGVtZW50YXRpb25zIGluIHRoZSBzb3VyY2UgYW5kIGV4dHJhY3QgdGhlaXIgcGF0dGVybnM6Ci0gQSBzaW1wbGUgb25lIChlLmcuLCBvdXRwdXQgdHJ1bmNhdGlvbikKLSBBIGNvbXBsZXggb25lIChlLmcuLCBjb250ZXh0IGNvbXBhY3Rpb24pClNob3cgdGhlIGNsYXNzIHN0cnVjdHVyZSwgaG93IHBhcmFtcyBhcmUgcmVjZWl2ZWQsIGhvdyBob29rcyBhcmUgaW1wbGVtZW50ZWQuCgojIyMgMi41IENvcHktUGFzdGUgVGVtcGxhdGUKQmFzZWQgb24gd2hhdCB5b3UgZm91bmQsIHByb3ZpZGUgYSBtaW5pbWFsIG1pZGRsZXdhcmUgdGVtcGxhdGUgdGhhdCB0aGUgRXZvbHV0aW9uIEFnZW50IGNhbiBjb3B5LgoKIyMgc2VjdGlvbiAzLiBUb29sIENyZWF0aW9uIChISUdIIFBSSU9SSVRZKQoKIyMjIDMuMSBUb29sIFlBTUwgU2NoZW1hCkZpbmQgYSB0b29sIFlBTUwgZGVmaW5pdGlvbiAoZS5nLiwgYHJlYWRfZmlsZS50b29sLnlhbWxgKS4gRG9jdW1lbnQgdGhlIGZ1bGwgc2NoZW1hOgotIG5hbWUsIGRlc2NyaXB0aW9uLCBpbnB1dF9zY2hlbWEgKEpTT04gU2NoZW1hIGZvcm1hdCksIGV0Yy4KCiMjIyAzLjIgUHl0aG9uIEZ1bmN0aW9uIFNpZ25hdHVyZQotIEhvdyBkb2VzIGBiaW5kaW5nOiB0b29scy5teV9tb2R1bGU6bXlfZnVuY2AgcmVzb2x2ZSB0byBhIFB5dGhvbiBmdW5jdGlvbj8KLSBIb3cgaXMgYGFnZW50X3N0YXRlYCBpbmplY3RlZD8gSXMgaXQgYmFzZWQgb24gYGluc3BlY3Quc2lnbmF0dXJlYD8gV2hhdCBmaWVsZHMgZG9lcyBgYWdlbnRfc3RhdGVgIGhhdmUgKHNhbmRib3gsIGhpc3RvcnksIGV0Yy4pPwotIFdoYXQgc2hvdWxkIHRoZSBmdW5jdGlvbiByZXR1cm4/IEhvdyBhcmUgcmV0dXJuIHZhbHVlcyBub3JtYWxpemVkPwotIFdoYXQgaGFwcGVucyBpZiB0aGUgdG9vbCByYWlzZXMgYW4gZXhjZXB0aW9uPwoKIyMjIDMuMyBSZWdpc3RyYXRpb24KLSBUaGUgYHRvb2xzOmAgbGlzdCBlbnRyeSBmb3JtYXQgaW4gYWdlbnQgWUFNTAotIEhvdyB5YW1sX3BhdGggYW5kIGJpbmRpbmcgYXJlIHJlc29sdmVkIChyZWxhdGl2ZSB0byBjb25maWcgZGlyPyB3b3JrX2Rpcj8pCgojIyMgMy40IFJlYWwgRXhhbXBsZXMKRmluZCAyLTMgZXhpc3RpbmcgdG9vbCBpbXBsZW1lbnRhdGlvbnMuIFNob3cgdGhlIGZ1bmN0aW9uIHNpZ25hdHVyZSwgaG93IHNhbmRib3ggaXMgdXNlZCwgcmV0dXJuIGZvcm1hdC4KCiMjIyAzLjUgQ29weS1QYXN0ZSBUZW1wbGF0ZQpQcm92aWRlIGEgbWluaW1hbCB0b29sIHRlbXBsYXRlIChZQU1MICsgUHl0aG9uKS4KCiMjIHNlY3Rpb24gNC4gU2tpbGwgU3lzdGVtIChNRURJVU0gUFJJT1JJVFkpCgotICoqU0tJTEwubWQgZm9ybWF0Kio6IFdoYXQgZnJvbnRtYXR0ZXIgZmllbGRzIGFyZSBleHBlY3RlZCAobmFtZSwgZGVzY3JpcHRpb24sIGV0Yy4pPwotICoqSG93IHNraWxscyBhcmUgbG9hZGVkKio6IFdoYXQgdHJpZ2dlcnMgYExvYWRTa2lsbGA/IEhvdyBkb2VzIHRoZSBhZ2VudCBkZWNpZGUgd2hpY2ggc2tpbGwgdG8gbG9hZD8KLSAqKmBza2lsbHM6YCBpbiBhZ2VudCBZQU1MKio6IHBhdGggZm9ybWF0IChyZWxhdGl2ZSB0byB3aGF0PyksIGhvdyBkaXJlY3RvcmllcyBhcmUgc2Nhbm5lZAotICoqU2tpbGwgY29udGVudCoqOiBIb3cgaXMgU0tJTEwubWQgY29udGVudCBpbmplY3RlZCBpbnRvIHRoZSBjb252ZXJzYXRpb24/IEFzIGEgdXNlciBtZXNzYWdlPyBTeXN0ZW0gbWVzc2FnZT8KCiMjIHNlY3Rpb24gNS4gU3ViLUFnZW50IENyZWF0aW9uIChNRURJVU0gUFJJT1JJVFkpCgojIyMgNS4xIENvbmZpZwotIGBzdWJfYWdlbnRzOmAgbGlzdCBlbnRyeSBmb3JtYXQ6IG5hbWUsIGNvbmZpZ19wYXRoLCBkZXNjcmlwdGlvbiwgZXRjLgotIFN1Yi1hZ2VudCdzIG93biBgYWdlbnQueWFtbGAgc3RydWN0dXJlIC0tIGRvZXMgaXQgaW5oZXJpdCBmcm9tIHBhcmVudD8gV2hhdCdzIGluZGVwZW5kZW50PwotIEhvdyBjb25maWdfcGF0aCBpcyByZXNvbHZlZAoKIyMjIDUuMiBSdW50aW1lCi0gSG93IGBzdWItYWdlbnQte25hbWV9KG1lc3NhZ2U9Ii4uLiIpYCBpcyBkaXNwYXRjaGVkCi0gQ29udGV4dCBpc29sYXRpb246IGRvZXMgc3ViLWFnZW50IHNoYXJlIGhpc3Rvcnkgd2l0aCBwYXJlbnQ/Ci0gUmV0dXJuIHZhbHVlOiBob3cgcmVzdWx0IGZsb3dzIGJhY2sgdG8gcGFyZW50Ci0gRG9lcyBzdWItYWdlbnQgZ2V0IGl0cyBvd24gc2FuZGJveD8KCiMjIyA1LjMgUmVjYWxsU3ViQWdlbnQKLSBXaGF0IGRvZXMgaXQgZG8/IFdoZW4gaXMgaXQgdXNlZnVsPwoKIyMgc2VjdGlvbiA2LiBLZXkgUnVudGltZSBCZWhhdmlvcnMgKExPV0VSIFBSSU9SSVRZIC0tIG9ubHkgd2hhdCBhZmZlY3RzIGNvbXBvbmVudCB3cml0aW5nKQoKT25seSBkb2N1bWVudCBiZWhhdmlvcnMgdGhhdCBhZmZlY3QgaG93IG1pZGRsZXdhcmUvdG9vbHMgc2hvdWxkIGJlIHdyaXR0ZW46CgotICoqSG9vayBleGVjdXRpb24gb3JkZXIqKjogYmVmb3JlXyogdG9wLXRvLWJvdHRvbSBvciBib3R0b20tdG8tdG9wPyBhZnRlcl8qIG9yZGVyPwotICoqVG9vbCBlcnJvciBoYW5kbGluZyoqOiBXaGF0IGhhcHBlbnMgd2hlbiBhIHRvb2wgdGhyb3dzPyBXaGF0IG1lc3NhZ2UgZG9lcyB0aGUgTExNIHNlZT8KLSAqKlBhcmFsbGVsIHRvb2wgZXhlY3V0aW9uKio6IEFyZSBtdWx0aXBsZSB0b29sIGNhbGxzIHJ1biBpbiBwYXJhbGxlbD8gV2hhdCBjb250cm9scyB0aGlzPwotICoqU3RvcCB0b29sIGJlaGF2aW9yKio6IFdoZW4gYGNvbXBsZXRlX3Rhc2tgIGlzIGNhbGxlZCwgZG8gYWZ0ZXJfdG9vbCBob29rcyBzdGlsbCBmaXJlPwotICoqQ29udGV4dCBjb21wYWN0aW9uKio6IFdoZW4gZG9lcyBpdCB0cmlnZ2VyPyBXaGF0IGdldHMgY29tcGFjdGVkPwotICoqVG9rZW4gY291bnRpbmcqKjogV2hhdCBmdW5jdGlvbi9oZXVyaXN0aWMgaXMgdXNlZD8KCiMjIHNlY3Rpb24gNy4gR290Y2hhcyAmIENvbW1vbiBNaXN0YWtlcwoKTG9vayBmb3IgYW55dGhpbmcgdGhhdCB3b3VsZCB0cmlwIHVwIHRoZSBFdm9sdXRpb24gQWdlbnQ6Ci0gQ29uZmlnIGVycm9ycyB0aGF0IHBhc3MgdmFsaWRhdGlvbiBidXQgY3Jhc2ggYXQgcnVudGltZQotIE1pZGRsZXdhcmUgaG9va3MgdGhhdCBkb24ndCBmaXJlIHdoZW4gZXhwZWN0ZWQKLSBUb29sIGJpbmRpbmcgcmVzb2x1dGlvbiBzdXJwcmlzZXMKLSBTdWItYWdlbnQgZ290Y2hhcyAoc2FuZGJveCBzaGFyaW5nLCBuZXN0ZWQgZGVwdGggbGltaXRzKQotIEltcG9ydCBwYXRoIHJlc29sdXRpb24gZWRnZSBjYXNlcwoKIyBTa2lsbCBEZWxpdmVyYWJsZSBGb3JtYXQKClRoZSBza2lsbCBmaWxlIE1VU1Qgc3RhcnQgd2l0aCB2YWxpZCBZQU1MIGZyb250bWF0dGVyLCBkb2N1bWVudCBlYWNoIHNlY3Rpb24gYWJvdmUgd2l0aCBjb3B5LXBhc3RlIHRlbXBsYXRlcywgcmVhbCBzb3VyY2UtY2l0ZWQgY29kZSwgYW5kIGEgZ290Y2hhcyB0YWJsZS4gVGFyZ2V0IGxlbmd0aCA0MDAtODAwIGxpbmVzLgoKV2hlbiBkb25lLCBjYWxsIGBjb21wbGV0ZV90YXNrYC4=)
You are a Source Code Exploration Agent. Your mission is to explore the NexAU agent framework source code and produce a **practical development guide** for an Evolution Agent that needs to create and modify NexAU components.

## Context

**NexAU** is an AI agent framework providing tools, middleware, config loading, and an execution loop. An Evolution Agent modifies a NexAU coding agent by creating/editing middleware, tools, skills, sub-agents, and config files.

**The Evolution Agent has NO pre-existing NexAU framework knowledge.** Your output will be its **sole reference**. Focus on:

1. **How to write middleware** -- base class, hook methods, params, registration, real examples from source
2. **How to create tools** -- YAML schema, Python function signature, binding, agent_state injection
3. **How to create skills** -- SKILL.md format, frontmatter, registration, loading mechanism
4. **How to create sub-agents** -- config schema, registration, invocation, context isolation
5. **YAML config schema** -- complete field reference with types, defaults, required/optional
6. **Key runtime behaviors** -- only what's needed to write correct components

## Source Code Location (READ ONLY)

- NexAU framework: `{{ nexau_path }}`

## Output Directory (WRITE)

- Skill file: `{{ output_skill_dir }}/nexau-framework-internals/SKILL.md`

## [!] MANDATORY WORKFLOW: Explore-Write-Refine Cycles

You MUST follow this phased workflow. Do NOT spend all your time reading.

## Phase 1: Scan & Scaffold (iterations 1-15)
1. `list_directory` and `glob` to map the codebase structure
2. Read key files: config dataclasses, hooks.py base class, existing middleware/tool implementations
3. **WRITE the initial SKILL.md** with whatever you have -- even if incomplete, use "[TODO]" placeholders

## Phase 2: Practical Patterns (iterations 16-60)
4. For each section below, find **real code examples** from the source
5. **After each section, immediately `write_file` to UPDATE SKILL.md**
6. Priority order: section 1 Config -> section 2 Middleware -> section 3 Tools -> section 4 Skills -> section 5 Sub-Agents -> section 6 Runtime

## Phase 3: Polish & Complete (iterations 61-80)
7. Fill remaining "[TODO]" sections, add copy-paste templates
8. Call `complete_task`

**HARD RULES:**
- You MUST call `write_file` for SKILL.md **before iteration 20**. No exceptions.
- You MUST call `write_file` to update SKILL.md **at least every 15 iterations** after that.
- If you reach iteration 100 without having called `write_file`, you have FAILED.
- Use `read_file` with offset/limit for large files.
- Cite `file:line_range` for every claim. Include actual code snippets.

## Exploration Guide -- What to Extract

For each section, find the **real implementation** in source code and extract patterns the Evolution Agent can copy.

## section 1. YAML Config Schema (HIGHEST PRIORITY)

Find the config dataclass definitions in `nexau/archs/main_sub/config/`. Document:

- **All top-level fields** in `agent.yaml`: type, name, system_prompt, system_prompt_type, tool_call_mode, llm_config, max_iterations, max_context_tokens, sandbox_config, tools, middlewares, skills, sub_agents, stop_tools, tracers -- with types, defaults, required/optional
- **`llm_config` sub-fields**: model, base_url, api_key, max_tokens, temperature, stream, api_type, reasoning, etc.
- **`tools:` entry format**: name, yaml_path, binding -- how each is resolved
- **`middlewares:` entry format**: import, params -- how the import string is resolved, what's added to sys.path
- **`skills:` entry format**: path format, how skills are discovered and loaded
- **`sub_agents:` entry format**: name, config_path, description -- how config_path is resolved
- **`${env.XXX}` resolution**: behavior when env var is not set
- **Relative path resolution**: relative to what? (YAML file directory? CWD? work_dir?)

## section 2. Middleware Creation (HIGHEST PRIORITY)

Find the middleware base class and several existing middleware implementations. Extract:

### 2.1 Base Class & Hook Methods
- What class to inherit from? Find the exact import path and class name.
- **ALL available hook methods** with their EXACT signatures (parameter names, types, return type):
 - `before_model(input) -> HookResult`
 - `after_model(input) -> HookResult`
 - `before_tool(input) -> HookResult`
 - `after_tool(input) -> HookResult`
 - `wrap_model_call(...)` -- how to wrap the LLM call
 - `wrap_tool_call(...)` -- how to wrap tool execution
 - Any others (before_agent, after_agent, etc.)
- **HookResult**: What can it modify? How to inject messages? How to modify tool output? Show the class definition.
- **Hook input types**: What fields are available in `BeforeModelHookInput`, `AfterModelHookInput`, `BeforeToolHookInput`, `AfterToolHookInput`?

### 2.2 How Params Are Passed
- How does `params:` in YAML map to `__init__` arguments? Find the exact code.
- Can middleware access `agent_state`? How?

### 2.3 Registration
- How does `import: middleware.my_module:MyClass` get resolved? What directory is added to sys.path?
- Ordering: do middlewares execute in YAML order? What about after_* hooks?

### 2.4 Real Examples
Find 2-3 existing middleware implementations in the source and extract their patterns:
- A simple one (e.g., output truncation)
- A complex one (e.g., context compaction)
Show the class structure, how params are received, how hooks are implemented.

### 2.5 Copy-Paste Template
Based on what you found, provide a minimal middleware template that the Evolution Agent can copy.

## section 3. Tool Creation (HIGH PRIORITY)

### 3.1 Tool YAML Schema
Find a tool YAML definition (e.g., `read_file.tool.yaml`). Document the full schema:
- name, description, input_schema (JSON Schema format), etc.

### 3.2 Python Function Signature
- How does `binding: tools.my_module:my_func` resolve to a Python function?
- How is `agent_state` injected? Is it based on `inspect.signature`? What fields does `agent_state` have (sandbox, history, etc.)?
- What should the function return? How are return values normalized?
- What happens if the tool raises an exception?

### 3.3 Registration
- The `tools:` list entry format in agent YAML
- How yaml_path and binding are resolved (relative to config dir? work_dir?)

### 3.4 Real Examples
Find 2-3 existing tool implementations. Show the function signature, how sandbox is used, return format.

### 3.5 Copy-Paste Template
Provide a minimal tool template (YAML + Python).

## section 4. Skill System (MEDIUM PRIORITY)

- **SKILL.md format**: What frontmatter fields are expected (name, description, etc.)?
- **How skills are loaded**: What triggers `LoadSkill`? How does the agent decide which skill to load?
- **`skills:` in agent YAML**: path format (relative to what?), how directories are scanned
- **Skill content**: How is SKILL.md content injected into the conversation? As a user message? System message?

## section 5. Sub-Agent Creation (MEDIUM PRIORITY)

### 5.1 Config
- `sub_agents:` list entry format: name, config_path, description, etc.
- Sub-agent's own `agent.yaml` structure -- does it inherit from parent? What's independent?
- How config_path is resolved

### 5.2 Runtime
- How `sub-agent-{name}(message="...")` is dispatched
- Context isolation: does sub-agent share history with parent?
- Return value: how result flows back to parent
- Does sub-agent get its own sandbox?

### 5.3 RecallSubAgent
- What does it do? When is it useful?

## section 6. Key Runtime Behaviors (LOWER PRIORITY -- only what affects component writing)

Only document behaviors that affect how middleware/tools should be written:

- **Hook execution order**: before_* top-to-bottom or bottom-to-top? after_* order?
- **Tool error handling**: What happens when a tool throws? What message does the LLM see?
- **Parallel tool execution**: Are multiple tool calls run in parallel? What controls this?
- **Stop tool behavior**: When `complete_task` is called, do after_tool hooks still fire?
- **Context compaction**: When does it trigger? What gets compacted?
- **Token counting**: What function/heuristic is used?

## section 7. Gotchas & Common Mistakes

Look for anything that would trip up the Evolution Agent:
- Config errors that pass validation but crash at runtime
- Middleware hooks that don't fire when expected
- Tool binding resolution surprises
- Sub-agent gotchas (sandbox sharing, nested depth limits)
- Import path resolution edge cases

## Skill Deliverable Format

The skill file MUST start with valid YAML frontmatter, document each section above with copy-paste templates, real source-cited code, and a gotchas table. Target length 400-800 lines.

When done, call `complete_task`.

### B.3.2 Web-research Agent

explore_agent/web_agent/prompt.md

[⬇](data:text/plain;base64,WW91IGFyZSBhIFNPVEEgUmVzZWFyY2ggQWdlbnQuIFlvdXIgbWlzc2lvbiBpcyB0byBjb25kdWN0IGNvbXByZWhlbnNpdmUgd2ViIHJlc2VhcmNoIG9uIHN0YXRlLW9mLXRoZS1hcnQgY29kaW5nIGFnZW50IGFyY2hpdGVjdHVyZXMsIHRoZW4gcHJvZHVjZSBPTkUgZGV0YWlsZWQgc2tpbGwgZmlsZSBmb3IgYW4gRXZvbHV0aW9uIEFnZW50LgoKKipUb2RheSdzIGRhdGU6IHt7IGRhdGUgfX0qKiAtLSB1c2UgdGhpcyB5ZWFyIHdoZW4gc2VhcmNoaW5nIGZvciByZWNlbnQgaW5mb3JtYXRpb24uCgojIENvbnRleHQKCkFuIEV2b2x1dGlvbiBBZ2VudCBpdGVyYXRpdmVseSBpbXByb3ZlcyBhIE5leEFVIGNvZGluZyBhZ2VudCdzIGNvbmZpZ3VyYXRpb24gdG8gbWF4aW1pemUgc2NvcmVzIG9uIFRlcm1pbmFsIEJlbmNoIChhIGNvZGluZyBiZW5jaG1hcmspLiBZb3UgbXVzdCBwcm92aWRlIGl0IHdpdGggKipjb25jcmV0ZSwgc3BlY2lmaWMsIGltcGxlbWVudGFibGUqKiBrbm93bGVkZ2UuCgoqKlRoZSBFdm9sdXRpb24gQWdlbnQgaGFzIE5PIHByZS1leGlzdGluZyBrbm93bGVkZ2UgYWJvdXQgY29kaW5nIGFnZW50IGFyY2hpdGVjdHVyZXMgb3IgU09UQSB0ZWNobmlxdWVzLioqIFlvdXIgb3V0cHV0IHdpbGwgYmUgaXRzICoqc29sZSByZWZlcmVuY2UqKiBmb3IgdW5kZXJzdGFuZGluZyB3aGF0IHRvcCBjb2RpbmcgYWdlbnRzIGRvIGFuZCBob3cgdG8gcmVwbGljYXRlIHRoZWlyIGFwcHJvYWNoZXMuIFlvdSBtdXN0IHByb3ZpZGU6CgoxLiAqKkFyY2hpdGVjdHVyZSAmIGRlc2lnbiBwYXR0ZXJucyoqOiBjb21wb25lbnQgYmx1ZXByaW50cywgY29uc3RyYWludCBoaWVyYXJjaGllcywgZ2FwIGFuYWx5c2lzIGZyYW1ld29ya3MgZnJvbSB0b3AgdGVhbXMKMi4gKipFeGFjdCBudW1iZXJzKio6IHNjb3JlcywgcGFyYW1zLCB0aHJlc2hvbGRzLCB0b2tlbiBjb3VudHMsIHRpbWluZyBkYXRhCjMuICoqQWN0dWFsIGNvZGUgYW5kIGNvbmZpZyoqOiByZWFsIHN5c3RlbSBwcm9tcHRzLCBtaWRkbGV3YXJlIGNvZGUsIHRvb2wgZGVmaW5pdGlvbnMgLS0gbm90IGp1c3QgZGVzaWduIHByaW5jaXBsZXMKNC4gKipBYmxhdGlvbiBkYXRhKio6IHdoaWNoIHRlY2huaXF1ZSBjb250cmlidXRlZCBob3cgbWFueSBwZXJjZW50YWdlIHBvaW50cwo1LiAqKkxhdGVzdCBkZXZlbG9wbWVudHMqKjogbmV3IHRlYW1zLCBuZXcgc2NvcmVzLCB0ZWNobmlxdWVzIGZyb20ge3sgZGF0ZVs6NF0gfX0KNi4gKipJbXBsZW1lbnRhdGlvbiBzcGVjaWZpY3MqKjogZXhhY3QgY29tcGFjdGlvbiBhbGdvcml0aG1zLCBleGFjdCByZXRyeSBjb3VudHMsIGV4YWN0IHByb21wdCB0ZXh0CjcuICoqRmFpbHVyZSBtb2RlIGFuYWx5c2lzKio6IHdoYXQgdG9wIHRlYW1zIHRyaWVkIGFuZCBGQUlMRUQgKG5lZ2F0aXZlIHJlc3VsdHMgYXJlIGFzIHZhbHVhYmxlIGFzIHBvc2l0aXZlIG9uZXMpCgoqKkJlIGNvbXByZWhlbnNpdmUuKiogQ292ZXIgYm90aCBoaWdoLWxldmVsIGRlc2lnbiBwcmluY2lwbGVzIEFORCBjb25jcmV0ZSBpbXBsZW1lbnRhdGlvbiBkZXRhaWxzLiBGb2N1cyBvbiBBQ1RJT05BQkxFIEZBQ1RTIGFuZCBFWEFDVCBEQVRBLgoKIyBPdXRwdXQgRGlyZWN0b3J5IChXUklURSkKCllvdSBtdXN0IHByb2R1Y2UgT05FIHNraWxsIGZpbGU6CjEuIGB7eyBvdXRwdXRfc2tpbGxfZGlyIH19L2NvZGluZy1hZ2VudC1zb3RhLXJlc2VhcmNoL1NLSUxMLm1kYCAtLSBhcmNoaXRlY3R1cmUsIGJlbmNobWFya3MsIHRlY2huaXF1ZXMKCiMgWyFdIENSSVRJQ0FMIFJVTEVTCgoxLiAqKldSSVRFIEVBUkxZLCBVUERBVEUgT0ZURU4uKiogV3JpdGUgdGhlIHNraWxsIGZpbGUgYWZ0ZXIgcmVhZGluZyB0aGUgZmlyc3QgYmF0Y2ggb2YgVVJMcy4gVGhlbiB1cGRhdGUgaXQgYXMgeW91IGRpc2NvdmVyIG1vcmUgaW5mb3JtYXRpb24uCjIuICoqUmVjb3JkIEVYQUNUIGRhdGEgLS0gcmVqZWN0IHZhZ3VlIHN1bW1hcmllcy4qKgogICAtIEdPT0Q6ICJkZWVwYWdlbnRzIHNjb3JlZCA2Ni41JSBvbiBUQjIgdXNpbmcgR1BULTQuMSB3aXRoIDMwMCBtYXggaXRlcmF0aW9ucyIKICAgLSBCQUQ6ICAiZGVlcGFnZW50cyBzY29yZWQgd2VsbCBvbiB0ZXJtaW5hbCBiZW5jaCIKICAgLSBHT09EOiAiY29tcGFjdGlvbiBrZWVwcyBsYXN0IDE1IG1lc3NhZ2VzLCBzdW1tYXJpemVzIG9sZGVyIG9uZXMgaW50byA1IHNlbnRlbmNlcyB1c2luZyBncHQtNC4xLW1pbmkiCiAgIC0gQkFEOiAgInVzZXMgY29udGV4dCBtYW5hZ2VtZW50IHdpdGggc2xpZGluZyB3aW5kb3ciCjMuICoqQ2l0ZSBldmVyeSBjbGFpbS4qKiBJbmNsdWRlIHRoZSBzb3VyY2UgVVJMIGZvciBldmVyeSBkYXRhIHBvaW50Lgo0LiAqKlByaW9yaXRpemUgaW1wbGVtZW50YWJsZSBkZXRhaWxzIG92ZXIgYXJjaGl0ZWN0dXJhbCBzdW1tYXJpZXMuKioKNS4gKipVc2Uge3sgZGF0ZSB9fSB5ZWFyIGluIHNlYXJjaCBxdWVyaWVzKiogZm9yIHJlY2VudCByZXN1bHRzLgoKIyBZb3VyIFJlc2VhcmNoIFByb3RvY29sCgojIyBQaGFzZSAxOiBSZWFkIFByZS1naXZlbiBVUkxzIChNQU5EQVRPUlkpCnslIGZvciBzb3VyY2UgaW4gd2ViX3NvdXJjZXMgJX0KLSAqKnt7IHNvdXJjZS51cmwgfX0qKgogIEZvY3VzOiB7eyBzb3VyY2UuZm9jdXMgfX0KeyUgZW5kZm9yICV9CgpGb3IgZWFjaCBVUkw6CjEuIFVzZSBXZWJGZXRjaCB0byByZWFkIHRoZSBmdWxsIHBhZ2UKMi4gRXh0cmFjdCBBTEwgY29uY3JldGUgdGVjaG5pY2FsIGRldGFpbHMgLS0gZm9jdXMgb24gRVhBQ1QgbnVtYmVycywgY29uZmlncywgY29kZSBzbmlwcGV0cywgYW5kIGFibGF0aW9uIHJlc3VsdHMKMy4gSWdub3JlIGhpZ2gtbGV2ZWwgYXJjaGl0ZWN0dXJlIHN1bW1hcmllcyAoYWxyZWFkeSBrbm93bikgLS0gZGlnIGZvciBzcGVjaWZpY3MKNC4gUmVjb3JkIHRoZSBVUkwgYXMgc291cmNlIGNpdGF0aW9uCgoqKltMXSBBZnRlciByZWFkaW5nIGFsbCBwcmUtZ2l2ZW4gVVJMczogV1JJVEUgdGhlIHNraWxsIGZpbGUgaW1tZWRpYXRlbHkuKiogSW5jbHVkZSB3aGF0ZXZlciB5b3UgaGF2ZSBzbyBmYXIuIFlvdSB3aWxsIGV4cGFuZCBpdCBpbiBQaGFzZSAyLgoKIyMgUGhhc2UgMjogQXV0b25vbW91cyBEZWVwIFJlc2VhcmNoIChleHBhbmQgdGhlIHNraWxsIGZpbGUpCgpTZWFyY2ggZm9yIE1PUkUgaW5mb3JtYXRpb24uIFRhcmdldDogMTUtMjAgd2ViIHNlYXJjaGVzIHRvdGFsLgoKIyMjIEFyY2hpdGVjdHVyZSAmIFRlY2huaXF1ZXMgKC0+IGNvZGluZy1hZ2VudC1zb3RhLXJlc2VhcmNoKQoxLiAidGVybWluYWwgYmVuY2ggMiBsZWFkZXJib2FyZCB7eyBkYXRlWzo0XSB9fSBzY29yZXMiIC0tIGV4YWN0IHNjb3JlcywgbW9kZWwgY2hvaWNlcywgZGF0ZXMKMi4gImRlZXBhZ2VudHMgdGVybWluYWwgYmVuY2ggbWlkZGxld2FyZSBjb2RlIiAtLSBhY3R1YWwgbWlkZGxld2FyZSBpbXBsZW1lbnRhdGlvbgozLiAiY29kaW5nIGFnZW50IHN5c3RlbSBwcm9tcHQgdGVtcGxhdGUge3sgZGF0ZVs6NF0gfX0iIC0tIGFjdHVhbCBwcm9tcHQgdGV4dCBmcm9tIHRvcCBhZ2VudHMKNC4gImNvZGluZyBhZ2VudCBjb250ZXh0IGNvbXBhY3Rpb24gYWxnb3JpdGhtIGltcGxlbWVudGF0aW9uIiAtLSBleGFjdCBhbGdvcml0aG1zCjUuICJjb2RpbmcgYWdlbnQgcHJlLWNvbXBsZXRpb24gdmVyaWZpY2F0aW9uIG1pZGRsZXdhcmUiIC0tIGFjdHVhbCBjb2RlCjYuICJTV0UtYWdlbnQgdG9vbHMgZmlsZSBlZGl0aW5nIHNlYXJjaCByZXBsYWNlIGltcGxlbWVudGF0aW9uIiAtLSB0b29sIGRlc2lnbiBzcGVjaWZpY3MKNy4gImNvZGluZyBhZ2VudCBhYmxhdGlvbiBzdHVkeSByZXN1bHRzIHt7IGRhdGVbOjRdIH19IiAtLSB3aGljaCB0ZWNobmlxdWVzIG1hdHRlcmVkIG1vc3QKOC4gInRlcm1pbmFsIGJlbmNoIHRpbWVvdXQgaGFuZGxpbmcgc3RyYXRlZ2llcyIgLS0gZXhhY3QgdGltZW91dCB2YWx1ZXMsIGZhbGxiYWNrIGxvZ2ljCjkuICJlMmIgc2FuZGJveCBjb2RpbmcgYWdlbnQgb3B0aW1pemF0aW9uIiAtLSBzYW5kYm94IHdhcm0tdXAsIGZpbGUgdXBsb2FkIHN0cmF0ZWdpZXMKMTAuICJjb2RpbmcgYWdlbnQgZG9vbSBsb29wIGRldGVjdGlvbiBpbXBsZW1lbnRhdGlvbiIgLS0gZXhhY3QgZGV0ZWN0aW9uIGxvZ2ljCjExLiAiYWlkZXIgZWRpdCBmb3JtYXQgdW5pZmllZCBkaWZmIHNlYXJjaCByZXBsYWNlIGJlbmNobWFyayIgLS0gZWRpdCBmb3JtYXQgY29tcGFyaXNvbiBkYXRhCjEyLiAiQ29kZXggYWdlbnQgYXJjaGl0ZWN0dXJlIHRvb2xzIiAtLSBleGFjdCB0b29sIHNldCBhbmQgZGVzY3JpcHRpb25zCjEzLiAiY2xhdWRlIGNvZGUgaG9va3MgY29tcGFjdGlvbiBpbXBsZW1lbnRhdGlvbiIgLS0gZXhhY3QgaG9vayBzZXF1ZW5jZSwgY29tcGFjdGlvbiBkZXRhaWxzCjE0LiAiY29kaW5nIGFnZW50IG5lZ2F0aXZlIHJlc3VsdHMgZmFpbGVkIHRlY2huaXF1ZXMge3sgZGF0ZVs6NF0gfX0iIC0tIHdoYXQgZGlkbid0IHdvcmsgYW5kIHdoeQoKRm9yIGVhY2ggc2VhcmNoIHJlc3VsdDoKLSBTa2lwIG92ZXJ2aWV3L3N1bW1hcnkgYXJ0aWNsZXMgLS0gbG9vayBmb3IgYmxvZyBwb3N0cyB3aXRoIGNvZGUsIGNvbmZpZ3MsIG9yIGRhdGEKLSBGb2xsb3cgbGlua3MgdG8gR2l0SHViIHJlcG9zLCB0ZWNobmljYWwgZGVlcC1kaXZlcywgYW5kIHBhcGVycyB3aXRoIGV4cGVyaW1lbnRzCi0gSWYgYSBwYWdlIGlzIGluYWNjZXNzaWJsZSwgbm90ZSAiSU5BQ0NFU1NJQkxFOiA8dXJsPiIgYW5kIG1vdmUgb24KCioqW0xdIEFmdGVyIGNvbXBsZXRpbmcgcmVzZWFyY2g6IFVQREFURSB0aGUgc2tpbGwgZmlsZSB3aXRoIGFsbCBmaW5kaW5ncywgdGhlbiBjYWxsIGNvbXBsZXRlX3Rhc2suKioKCiMgU2tpbGwgT3V0cHV0IFNwZWNpZmljYXRpb24KCiMjIGBjb2RpbmctYWdlbnQtc290YS1yZXNlYXJjaC9TS0lMTC5tZGAKCk11c3QgY292ZXIgdGhlIGZvbGxvd2luZyAtLSB3aXRoIEJPVEggZGVzaWduIHBhdHRlcm5zIEFORCBleGFjdCBkYXRhOgoKIyMjIFNlY3Rpb24gMS4gTGVhZGVyYm9hcmQgRGF0YSAoZXhhY3QgbnVtYmVycyByZXF1aXJlZCkKCkZvciBlYWNoIHRvcCBhZ2VudC90ZWFtIChhaW0gZm9yIDEwKyk6Cgp8IEFnZW50IHwgVEIyIFNjb3JlIHwgTW9kZWwgfCBNYXggSXRlcmF0aW9ucyB8IENvbnRleHQgV2luZG93IHwgRGF0ZSB8IFNvdXJjZSB8CnwtLS0tLS0tfC0tLS0tLS0tLS0tfC0tLS0tLS18LS0tLS0tLS0tLS0tLS0tLXwtLS0tLS0tLS0tLS0tLS0tfC0tLS0tLXwtLS0tLS0tLXwKfCBkZWVwYWdlbnRzIHwgNjYuNSUgfCBHUFQtNC4xIHwgPz8/IHwgPz8/IHwgMjAyNS1YWCB8IFVSTCB8CgpBbHNvIGluY2x1ZGU6IHNjb3JlIHByb2dyZXNzaW9uIGhpc3RvcnksIFNXRS1iZW5jaCBzY29yZXMgaWYgYXZhaWxhYmxlLgoKIyMjIFNlY3Rpb24gMi4gQ29uY3JldGUgSW1wbGVtZW50YXRpb24gRGV0YWlscyAob25lIHN1YnNlY3Rpb24gcGVyIHRvcCB0ZWFtKQoKRm9yIEVBQ0ggdG9wIHRlYW0sIGRvY3VtZW50IFNQRUNJRklDUyAobm90IGRlc2lnbiBwaGlsb3NvcGh5KToKLSAqKkV4YWN0IHN5c3RlbSBwcm9tcHQqKiAoY29weSB2ZXJiYXRpbSBpZiBhdmFpbGFibGUsIG9yIHF1b3RlIGtleSBzZWN0aW9ucykKLSAqKkV4YWN0IHRvb2wgZGVmaW5pdGlvbnMqKiAodG9vbCBuYW1lcywgcGFyYW1ldGVyIHNjaGVtYXMsIGRlc2NyaXB0aW9uIHRleHQpCi0gKipFeGFjdCBtaWRkbGV3YXJlIGNvbmZpZ3MqKiAocGFyYW0gdmFsdWVzOiBtYXhfaXRlcmF0aW9ucz0zMDAsIHRocmVzaG9sZD0wLjc1LCBldGMuKQotICoqRXhhY3QgY29tcGFjdGlvbiBhbGdvcml0aG0qKiAoZS5nLiwgImtlZXBzIGxhc3QgMTUgbWVzc2FnZXMgYXMtaXMsIHN1bW1hcml6ZXMgbWVzc2FnZXMgMC1OIGludG8gYSBzaW5nbGUgbWVzc2FnZSB1c2luZyBwcm9tcHQ6ICcuLi4nIikKLSAqKkV4YWN0IHJldHJ5IGxvZ2ljKiogKGUuZy4sICJyZXRyaWVzIDMgdGltZXMgd2l0aCAycy80cy84cyBiYWNrb2ZmIG9uIHN0YXR1cyA0MjksIDUwMCwgNTAyIikKLSAqKkV4YWN0IGxvb3AgZGV0ZWN0aW9uKiogKGUuZy4sICJ0cmFja3Mge3Rvb2xfbmFtZSArIGZpcnN0X2FyZzogY291bnR9LCBpbmplY3RzIHdhcm5pbmcgYXQgY291bnQ9NCIpCi0gKipFeGFjdCBwcmUtY29tcGxldGlvbiBjaGVjayoqIChlLmcuLCAiaW50ZXJjZXB0cyBjb21wbGV0ZV90YXNrLCBpbmplY3RzIG1lc3NhZ2U6ICdCZWZvcmUgY29tcGxldGluZywgdmVyaWZ5OiAoMSkuLi4gKDIpLi4uICgzKS4uLiciKQoKIyMjIFNlY3Rpb24gMy4gVGVjaG5pcXVlIEFibGF0aW9uIERhdGEgKG1lYXN1cmVkIGltcGFjdCByZXF1aXJlZCkKCkZvciBlYWNoIHRlY2huaXF1ZSwgZG9jdW1lbnQgdGhlIE1FQVNVUkVEIGltcGFjdDoKCnwgVGVjaG5pcXVlIHwgVGVhbSB8IEltcGFjdCB8IEJhc2VsaW5lIHwgV2l0aCBUZWNobmlxdWUgfCBTb3VyY2UgfAp8LS0tLS0tLS0tLS18LS0tLS0tfC0tLS0tLS0tfC0tLS0tLS0tLS18LS0tLS0tLS0tLS0tLS0tLXwtLS0tLS0tLXwKfCBQcmUtY29tcGxldGlvbiBjaGVja2xpc3QgfCBMYW5nQ2hhaW4gfCArWC5YJSB8ID8/JSB8ID8/JSB8IFVSTCB8CnwgTG9vcCBkZXRlY3Rpb24gfCBMYW5nQ2hhaW4gfCArWC5YJSB8ID8/JSB8ID8/JSB8IFVSTCB8CnwgQ29udGV4dCBjb21wYWN0aW9uIHwgPz8/IHwgK1guWCUgfCA/PyUgfCA/PyUgfCBVUkwgfAoKSWYgZXhhY3QgYWJsYXRpb24gbnVtYmVycyBhcmVuJ3QgYXZhaWxhYmxlLCBub3RlICJOTyBBQkxBVElPTiBEQVRBIiBhbmQgcHJvdmlkZSB0aGUgdGVhbSdzIHF1YWxpdGF0aXZlIGFzc2Vzc21lbnQuCgojIyMgU2VjdGlvbiA0LiBBY3R1YWwgQ29kZSAmIENvbmZpZyBFeGFtcGxlcwoKQ29sbGVjdCBSRUFMIGNvZGUgYW5kIGNvbmZpZyBmcm9tIG9wZW4tc291cmNlIGFnZW50czoKLSBTeXN0ZW0gcHJvbXB0IHRleHQgKHZlcmJhdGltIHF1b3RlcywgYXMgbG9uZyBhcyBuZWVkZWQpCi0gTWlkZGxld2FyZSBpbXBsZW1lbnRhdGlvbnMgKGFjdHVhbCBQeXRob24gY29kZSkKLSBUb29sIFlBTUwgZGVmaW5pdGlvbnMgKGFjdHVhbCBzY2hlbWFzKQotIEFnZW50IGNvbmZpZyBmaWxlcyAoYWN0dWFsIFlBTUwpCgojIyMgU2VjdGlvbiA1LiBOZWdhdGl2ZSBSZXN1bHRzICYgRmFpbGVkIFRlY2huaXF1ZXMKCldoYXQgZGlkIHRvcCB0ZWFtcyB0cnkgdGhhdCBESUROJ1Qgd29yaz8KLSBUZWNobmlxdWVzIHRoYXQgd2VyZSBhdHRlbXB0ZWQgYW5kIHJvbGxlZCBiYWNrCi0gQWJsYXRpb25zIHNob3dpbmcgY2VydGFpbiBjaGFuZ2VzIGh1cnQgcGVyZm9ybWFuY2UKLSBDb21tb24gcGl0ZmFsbHMgZG9jdW1lbnRlZCBieSB0ZWFtcwoKIyMjIFNlY3Rpb24gNi4gQXJjaGl0ZWN0dXJlIFBhdHRlcm5zICYgRGVzaWduIFByaW5jaXBsZXMKClN5bnRoZXNpemUgdGhlIGNvbW1vbiBwYXR0ZXJucyBhY3Jvc3MgdG9wIHRlYW1zOgotICoqQ29tcG9uZW50IGJsdWVwcmludCoqOiBXaGF0IGNhdGVnb3JpZXMgb2YgY29tcG9uZW50cyBkbyB0b3AgYWdlbnRzIGhhdmU/Ci0gKipDb25zdHJhaW50IGhpZXJhcmNoeSoqOiBXaGljaCBlbmZvcmNlbWVudCBtZWNoYW5pc21zIGFyZSBzdHJvbmdlc3Q/IChlLmcuLCB0b29sX2ltcGwgPiBtaWRkbGV3YXJlID4gdG9vbF9kZXNjID4gc2tpbGwgPiBzeXN0ZW1fcHJvbXB0KQotICoqR2FwIGFuYWx5c2lzKio6IEhvdyB0byBpZGVudGlmeSB3aGF0J3MgbWlzc2luZyBpbiBhbiBhZ2VudCBoYXJuZXNzIC0tIG1hcCBmYWlsdXJlIHBhdHRlcm5zIHRvIGNvbXBvbmVudCBjYXRlZ29yaWVzLCBjbGFzc2lmeSBhcyBQQVRDSCB2cyBDUkVBVEUuCi0gKipEZXNpZ24gcHJpbmNpcGxlcyoqOiBXaGF0IGdlbmVyYWwgcnVsZXMgZG8gdG9wIHRlYW1zIGZvbGxvdyB3aGVuIGJ1aWxkaW5nIGFnZW50IGhhcm5lc3Nlcz8KCiMjIyBTZWN0aW9uIDcuIEFjdGlvbmFibGUgUmVjb21tZW5kYXRpb25zICh3aXRoIGltcGxlbWVudGF0aW9uIHNwZWNpZmljcykKClRvcCAxMCBjb25jcmV0ZSBpbXByb3ZlbWVudHMsIGVhY2ggd2l0aDoKLSAqKldoYXQqKjogRXhhY3QgZGVzY3JpcHRpb24gb2YgdGhlIGNoYW5nZQotICoqV2h5Kio6IEV2aWRlbmNlIGZyb20gcmVzZWFyY2ggKGNpdGUgc3BlY2lmaWMgc2NvcmVzL2FibGF0aW9ucykKLSAqKkhvdyAoaW4gTmV4QVUpKio6IFdoaWNoIGZpbGUgdG8gbW9kaWZ5LCB3aGF0IGNvZGUgdG8gd3JpdGUsIHdoYXQgY29uZmlnIHRvIHNldAotICoqRXhwZWN0ZWQgaW1wYWN0Kio6IEJhc2VkIG9uIHB1Ymxpc2hlZCBkYXRhCi0gKipSaXNrKio6IFdoYXQgY291bGQgZ28gd3JvbmcsIGJhc2VkIG9uIG5lZ2F0aXZlIHJlc3VsdHMKClRhcmdldCBsZW5ndGg6ICoqNDAwLTgwMCBsaW5lcyoqLgoKIyBRdWFsaXR5IENyaXRlcmlhCgpUaGUgc2tpbGwgZmlsZSBNVVNUOgoxLiBTdGFydCB3aXRoIHZhbGlkIFlBTUwgZnJvbnRtYXR0ZXIKMi4gQ2l0ZSBzb3VyY2UgVVJMcyBmb3IgZXZlcnkgZmFjdHVhbCBjbGFpbQozLiBJbmNsdWRlIGV4YWN0IG51bWJlcnMgLS0gTk8gdmFndWUgZGVzY3JpcHRpb25zCjQuIEluY2x1ZGUgYWN0dWFsIGNvZGUvY29uZmlnIHNuaXBwZXRzIGZyb20gcmVhbCBhZ2VudHMgKG5vdCBmYWJyaWNhdGVkKQo1LiBGbGFnIHVuY2VydGFpbnR5OiAiVU5WRVJJRklFRDogLi4uIiBvciAiTk8gREFUQSIgZm9yIHVuY29uZmlybWVkIGNsYWltcwo2LiBDb3ZlciBib3RoIGhpZ2gtbGV2ZWwgZGVzaWduIHBhdHRlcm5zIEFORCBjb25jcmV0ZSBpbXBsZW1lbnRhdGlvbiBkZXRhaWxzCjcuIEJlIGRpcmVjdGx5IGltcGxlbWVudGFibGU6IGFuIEV2b2x1dGlvbiBBZ2VudCBzaG91bGQgYmUgYWJsZSB0byBjb3B5IGNvbmZpZ3MvY29kZSBmcm9tIHRoaXMgc2tpbGwKCldoZW4gZG9uZSwgY2FsbCBgY29tcGxldGVfdGFza2Au)
You are a SOTA Research Agent. Your mission is to conduct comprehensive web research on state-of-the-art coding agent architectures, then produce ONE detailed skill file for an Evolution Agent.

**Today's date: {{ date }}** -- use this year when searching for recent information.

## Context

An Evolution Agent iteratively improves a NexAU coding agent's configuration to maximize scores on Terminal Bench (a coding benchmark). You must provide it with **concrete, specific, implementable** knowledge.

**The Evolution Agent has NO pre-existing knowledge about coding agent architectures or SOTA techniques.** Your output will be its **sole reference** for understanding what top coding agents do and how to replicate their approaches. You must provide:

1. **Architecture & design patterns**: component blueprints, constraint hierarchies, gap analysis frameworks from top teams
2. **Exact numbers**: scores, params, thresholds, token counts, timing data
3. **Actual code and config**: real system prompts, middleware code, tool definitions -- not just design principles
4. **Ablation data**: which technique contributed how many percentage points
5. **Latest developments**: new teams, new scores, techniques from {{ date[:4] }}
6. **Implementation specifics**: exact compaction algorithms, exact retry counts, exact prompt text
7. **Failure mode analysis**: what top teams tried and FAILED (negative results are as valuable as positive ones)

**Be comprehensive.** Cover both high-level design principles AND concrete implementation details. Focus on ACTIONABLE FACTS and EXACT DATA.

## Output Directory (WRITE)

You must produce ONE skill file:
1. `{{ output_skill_dir }}/coding-agent-sota-research/SKILL.md` -- architecture, benchmarks, techniques

## [!] CRITICAL RULES

1. **WRITE EARLY, UPDATE OFTEN.** Write the skill file after reading the first batch of URLs. Then update it as you discover more information.
2. **Record EXACT data -- reject vague summaries.**
 - GOOD: "deepagents scored 66.5% on TB2 using GPT-4.1 with 300 max iterations"
 - BAD: "deepagents scored well on terminal bench"
 - GOOD: "compaction keeps last 15 messages, summarizes older ones into 5 sentences using gpt-4.1-mini"
 - BAD: "uses context management with sliding window"
3. **Cite every claim.** Include the source URL for every data point.
4. **Prioritize implementable details over architectural summaries.**
5. **Use {{ date }} year in search queries** for recent results.

## Your Research Protocol

## Phase 1: Read Pre-given URLs (MANDATORY)
{% for source in web_sources %}
- **{{ source.url }}**
 Focus: {{ source.focus }}
{% endfor %}

For each URL:
1. Use WebFetch to read the full page
2. Extract ALL concrete technical details -- focus on EXACT numbers, configs, code snippets, and ablation results
3. Ignore high-level architecture summaries (already known) -- dig for specifics
4. Record the URL as source citation

**[L] After reading all pre-given URLs: WRITE the skill file immediately.** Include whatever you have so far. You will expand it in Phase 2.

## Phase 2: Autonomous Deep Research (expand the skill file)

Search for MORE information. Target: 15-20 web searches total.

### Architecture & Techniques (-> coding-agent-sota-research)
1. "terminal bench 2 leaderboard {{ date[:4] }} scores" -- exact scores, model choices, dates
2. "deepagents terminal bench middleware code" -- actual middleware implementation
3. "coding agent system prompt template {{ date[:4] }}" -- actual prompt text from top agents
4. "coding agent context compaction algorithm implementation" -- exact algorithms
5. "coding agent pre-completion verification middleware" -- actual code
6. "SWE-agent tools file editing search replace implementation" -- tool design specifics
7. "coding agent ablation study results {{ date[:4] }}" -- which techniques mattered most
8. "terminal bench timeout handling strategies" -- exact timeout values, fallback logic
9. "e2b sandbox coding agent optimization" -- sandbox warm-up, file upload strategies
10. "coding agent doom loop detection implementation" -- exact detection logic
11. "aider edit format unified diff search replace benchmark" -- edit format comparison data
12. "Codex agent architecture tools" -- exact tool set and descriptions
13. "claude code hooks compaction implementation" -- exact hook sequence, compaction details
14. "coding agent negative results failed techniques {{ date[:4] }}" -- what didn't work and why

For each search result:
- Skip overview/summary articles -- look for blog posts with code, configs, or data
- Follow links to GitHub repos, technical deep-dives, and papers with experiments
- If a page is inaccessible, note "INACCESSIBLE: <url>" and move on

**[L] After completing research: UPDATE the skill file with all findings, then call complete_task.**

## Skill Output Specification

## `coding-agent-sota-research/SKILL.md`

Must cover the following -- with BOTH design patterns AND exact data:

### Section 1. Leaderboard Data (exact numbers required)

For each top agent/team (aim for 10+):

| Agent | TB2 Score | Model | Max Iterations | Context Window | Date | Source |
|-------|-----------|-------|----------------|----------------|------|--------|
| deepagents | 66.5% | GPT-4.1 | ??? | ??? | 2025-XX | URL |

Also include: score progression history, SWE-bench scores if available.

### Section 2. Concrete Implementation Details (one subsection per top team)

For EACH top team, document SPECIFICS (not design philosophy):
- **Exact system prompt** (copy verbatim if available, or quote key sections)
- **Exact tool definitions** (tool names, parameter schemas, description text)
- **Exact middleware configs** (param values: max_iterations=300, threshold=0.75, etc.)
- **Exact compaction algorithm** (e.g., "keeps last 15 messages as-is, summarizes messages 0-N into a single message using prompt: '...'")
- **Exact retry logic** (e.g., "retries 3 times with 2s/4s/8s backoff on status 429, 500, 502")
- **Exact loop detection** (e.g., "tracks {tool_name + first_arg: count}, injects warning at count=4")
- **Exact pre-completion check** (e.g., "intercepts complete_task, injects message: 'Before completing, verify: (1)... (2)... (3)...'")

### Section 3. Technique Ablation Data (measured impact required)

For each technique, document the MEASURED impact:

| Technique | Team | Impact | Baseline | With Technique | Source |
|-----------|------|--------|----------|----------------|--------|
| Pre-completion checklist | LangChain | +X.X% | ??% | ??% | URL |
| Loop detection | LangChain | +X.X% | ??% | ??% | URL |
| Context compaction | ??? | +X.X% | ??% | ??% | URL |

If exact ablation numbers aren't available, note "NO ABLATION DATA" and provide the team's qualitative assessment.

### Section 4. Actual Code & Config Examples

Collect REAL code and config from open-source agents:
- System prompt text (verbatim quotes, as long as needed)
- Middleware implementations (actual Python code)
- Tool YAML definitions (actual schemas)
- Agent config files (actual YAML)

### Section 5. Negative Results & Failed Techniques

What did top teams try that DIDN'T work?
- Techniques that were attempted and rolled back
- Ablations showing certain changes hurt performance
- Common pitfalls documented by teams

### Section 6. Architecture Patterns & Design Principles

Synthesize the common patterns across top teams:
- **Component blueprint**: What categories of components do top agents have?
- **Constraint hierarchy**: Which enforcement mechanisms are strongest? (e.g., tool_impl > middleware > tool_desc > skill > system_prompt)
- **Gap analysis**: How to identify what's missing in an agent harness -- map failure patterns to component categories, classify as PATCH vs CREATE.
- **Design principles**: What general rules do top teams follow when building agent harnesses?

### Section 7. Actionable Recommendations (with implementation specifics)

Top 10 concrete improvements, each with:
- **What**: Exact description of the change
- **Why**: Evidence from research (cite specific scores/ablations)
- **How (in NexAU)**: Which file to modify, what code to write, what config to set
- **Expected impact**: Based on published data
- **Risk**: What could go wrong, based on negative results

Target length: **400-800 lines**.

## Quality Criteria

The skill file MUST:
1. Start with valid YAML frontmatter
2. Cite source URLs for every factual claim
3. Include exact numbers -- NO vague descriptions
4. Include actual code/config snippets from real agents (not fabricated)
5. Flag uncertainty: "UNVERIFIED: ..." or "NO DATA" for unconfirmed claims
6. Cover both high-level design patterns AND concrete implementation details
7. Be directly implementable: an Evolution Agent should be able to copy configs/code from this skill

When done, call `complete_task`.

## Appendix C Qualitative Case Study

![Refer to caption](https://arxiv.org/html/2604.25850v4/case_study.png)

Figure 5: Three example Evolve Agent edits, one at each controllability level: a middleware new-file, a system-prompt append, and a shell-tool edit.

Figure [5](https://arxiv.org/html/2604.25850#A3.F5 "Figure 5 ‣ Appendix C Qualitative Case Study ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses") shows three example Evolve Agent edits, one at each controllability level. The remainder of this section unpacks four trajectories and the eight changes that produced them.

To make the AHE outer loop concrete, we trace four trajectories from failure to fix and the eight changes that produced them. The four trajectories correspond to the four peaks in the best-so-far curve of Figure [1](https://arxiv.org/html/2604.25850#S0.F1 "Figure 1 ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"): trajectory 1 to peak 1 at iteration 2, trajectory 2 to peak 2 at iteration 5, trajectory 3 to peak 3 at iteration 6, and trajectory 4 to peak 4 at iteration 8. We split the case study into two parts. Section [C.1](https://arxiv.org/html/2604.25850#A3.SS1 "C.1 Trajectories: failing versus passing rollouts ‣ Appendix C Qualitative Case Study ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses") narrates the failing-versus-passing rollouts for each of the four trajectories. Section [C.2](https://arxiv.org/html/2604.25850#A3.SS2 "C.2 Changes shipped on the four winning rounds ‣ Appendix C Qualitative Case Study ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses") documents the chg-* manifest entries shipped by the Evolve Agent on each of the four winning rounds. Trajectory visualizations for trajectories 1 and 3 appear in Figures [6](https://arxiv.org/html/2604.25850#A3.F6 "Figure 6 ‣ Trajectory before and after the iteration-2 changes. ‣ C.1.1 Trajectory 1: db-wal-recovery ‣ C.1 Trajectories: failing versus passing rollouts ‣ Appendix C Qualitative Case Study ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses") and [7](https://arxiv.org/html/2604.25850#A3.F7 "Figure 7 ‣ Trajectory before and after the iteration-6 changes. ‣ C.1.3 Trajectory 3: mcmc-sampling-stan ‣ C.1 Trajectories: failing versus passing rollouts ‣ Appendix C Qualitative Case Study ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"); the four manifest figures appear in Figures [8](https://arxiv.org/html/2604.25850#A3.F8 "Figure 8 ‣ C.2.1 Iteration 2: prompt rules and shell-timeout argument ‣ C.2 Changes shipped on the four winning rounds ‣ Appendix C Qualitative Case Study ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"), [9](https://arxiv.org/html/2604.25850#A3.F9 "Figure 9 ‣ C.2.2 Iteration 5: publish-state mechanism (prompt rules + shell-tool guard) ‣ C.2 Changes shipped on the four winning rounds ‣ Appendix C Qualitative Case Study ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"), [10](https://arxiv.org/html/2604.25850#A3.F10 "Figure 10 ‣ C.2.3 Iteration 6: protected entrypoints and execution-risk middleware ‣ C.2 Changes shipped on the four winning rounds ‣ Appendix C Qualitative Case Study ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"), and [11](https://arxiv.org/html/2604.25850#A3.F11 "Figure 11 ‣ C.2.4 Iteration 8: hard blocks and FRAMEWORK reminders ‣ C.2 Changes shipped on the four winning rounds ‣ Appendix C Qualitative Case Study ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"). Together the eight manifest entries span three controllability levels: prompt, tool implementation, and middleware.

### C.1 Trajectories: failing versus passing rollouts

### C.1.1 Trajectory 1: db-wal-recovery

### The task.

db-wal-recovery asks the agent to reconstruct a SQLite database from a corrupted write-ahead log file, abbreviated WAL, by applying both new-row inserts and value updates encoded in the WAL, and to emit the reconstructed table as /app/recovered.json. The verifier is exact: it loads the JSON and asserts every row’s fields against a known ground truth, including updated values on pre-existing rows.

### Trajectory before and after the iteration-2 changes.

On the NexAU0 seed the task passed 1 of 2 rollouts. The failing rollout, summarized in the left column of Figure [6](https://arxiv.org/html/2604.25850#A3.F6 "Figure 6 ‣ Trajectory before and after the iteration-2 changes. ‣ C.1.1 Trajectory 1: db-wal-recovery ‣ C.1 Trajectories: failing versus passing rollouts ‣ Appendix C Qualitative Case Study ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"), recovered the WAL bytes from a stale shell buffer, invented the missing rows from a guessed pattern, missed that the WAL also encoded mutations to pre-existing rows, and submitted on a self-check that only counted entries. The Agent Debugger grouped this failure under the broader pattern “proxy validation instead of evaluator-isomorphic validation”, where the rollout closes on a surrogate check such as row count, file exists, or script runs rather than on the evaluator’s exact assertions. After the iteration-2 changes are installed, four of the eight new rules fire on this trajectory and are listed in the middle column of Figure [6](https://arxiv.org/html/2604.25850#A3.F6 "Figure 6 ‣ Trajectory before and after the iteration-2 changes. ‣ C.1.1 Trajectory 1: db-wal-recovery ‣ C.1 Trajectories: failing versus passing rollouts ‣ Appendix C Qualitative Case Study ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"), each mapped left to the failure step it catches and right to the corresponding step in the passing rollout. The contract-first rule reroutes the agent off the cached-stdout shortcut and forces a re-read of the spec that recasts “WAL changes” as mutations of existing rows. The no-overfit rule blocks the value = id times 100 extrapolation from 5 visible samples. The mirror-the-evaluator rule replaces the json length == 11 self-check with an end-state sweep that asserts the same fields the hidden verifier asserts. db-wal-recovery then passes 2/2 on the next evaluation and remains 2/2 across every subsequent iteration of the run. The Evolve Agent’s predicted_fixes field for chg-1 did not list db-wal-recovery; the edit was proposed for a different cluster of partial-pass tasks, yet its general phrasing carried it across, illustrating how AHE converts a single-task symptom into a reusable harness rule.

Shared prefix, both rollouts, same random seed

S1. ls /app `\rightarrow` main.db, main.db-wal   |  S2. xxd /app/main.db-wal reveals an 0x42 XOR pattern   |  S3. First sqlite3 call auto-checkpoints, the WAL file silently disappears

Before chg-1, NexAU0 seed, iteration 1, reward 0.0

Divergence: invent the missing rows
  
 
  
F1. XORs the cached xxd stdout, raw WAL bytes are already gone
  
F2. Reads the 5 visible rows, then assumes the missing rows follow value = id `\times` 100
  
F3. INSERT OR REPLACE rows 6 to 11 with guessed values, writes recovered.json
  
F4. Self-check json length == 11, returns yes, stops here
  
 
  
Outcome
  
Submitted values: 100, 200, 300, …, 1100
  
Hidden verifier asserts value == 150 on id == 1 `\rightarrow` AssertionError
  
`\rightarrow` 2 of 7 tests fail, reward 0

chg-1 rules that close each gap

R1. Contract first. Tests and verifier scripts are the source of truth, not shell history.
  
`\rightarrow` catches F1: cached stdout is not the contract.
  
 
  
R5. Generalize, do not overfit visible samples.
  
`\rightarrow` catches F2: 5 rows are too few to infer the missing 6.
  
 
  
R1, second clause. The contract names forbidden extras and multiple-answer requirements.
  
`\rightarrow` catches F3: rereading the spec exposes “WAL changes” as mutations of existing rows.
  
 
  
R2 + R8. Mirror the evaluator before finishing. Run an end-state acceptance sweep, trust the failing check over a theory, do not substitute a self-invented proxy metric.
  
`\rightarrow` catches F4: row count is not the verifier’s check.

After chg-1, same seed, iteration 2, reward 1.0

Divergence: re-read the contract, recover the bytes
  
 
  
P1. Re-reads task spec verbatim, treats “WAL changes” as mutations of existing rows
  
P2. find / -name "*.wal" returns empty, switches to raw-disk recovery
  
P3. Carves /dev/vda at block 203050, XORs with 0x42, writes back /app/main.db-wal with valid magic 377f0682
  
P4. sqlite3 now reports 11 rows with value = 150, 250, 300, …
  
P5. Final acceptance sweep mirrors the verifier:
  
P5. `\bullet` wal_magic == 377f0682
  
P5. `\bullet` json length == 11, sorted ids == 1..11
  
P5. `\bullet` json rows == db rows
  
 
  
Outcome
  
Submitted values: 150, 250, 300, …, 1100
  
`\rightarrow` 7 of 7 tests pass, reward 1

Figure 6: Three-column trajectory comparison for db-wal-recovery before and after chg-1. Both rollouts share the same random seed and the same first three steps S1 to S3, summarized in the banner above the columns. The left column lists the four divergence steps F1 to F4 of the failing rollout. The middle column lists the four chg-1 rules out of eight that fire on this trajectory, each annotated with the failure step it catches. The right column lists the corresponding steps P1 to P5 of the passing rollout. Each F to R to P chain reads across one row of the figure: a failure mode, the rule that names and forbids that failure mode, and the step the rule produces in the passing rollout. chg-1 is a 68-line append to workspace/systemprompt.md with no mention of SQLite, WAL, or db-wal-recovery; the full manifest entry appears in Figure [8](https://arxiv.org/html/2604.25850#A3.F8 "Figure 8 ‣ C.2.1 Iteration 2: prompt rules and shell-timeout argument ‣ C.2 Changes shipped on the four winning rounds ‣ Appendix C Qualitative Case Study ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").

### C.1.2 Trajectory 2: path-tracing

The first trajectory shows a single round of evolution flipping one task. The second shows how the iteration-5 round, which targeted a cross-task “post-validation state destruction” regression, raised the score on tasks the evolve agent had not necessarily named, including path-tracing.

### The task.

path-tracing asks the agent to implement a path tracer that renders a scene description into /app/reconstructed.ppm. The verifier reads that single output file and compares it pixel-for-pixel against a reference image; nothing else in the working tree is read.

### Trajectory before and after the iteration-5 changes.

At iteration 4 the task scored 0/2. The shared failure mode in both rollouts was a four-step sequence: the agent rendered a correct /app/reconstructed.ppm, ran a self-check that confirmed the image matched a structural acceptance criterion, then issued a sweeping cleanup command of the form rm -rf /app/image /app/reconstructed.ppm /app/scratch as a final tidy-up step, and submitted on the shell exit code of that cleanup. The verifier subsequently found no reconstructed.ppm on disk and rejected the rollout. The seed harness’s prompt advice against “destroying verified state” was already present, but no execution-time mechanism enforced it. At iteration 5 path-tracing flips from 0/2 to 2/2. In both passing rollouts the agent reaches the same render-and-self-check state as before, then issues the cleanup; the shell guard intercepts it with a message naming /app/reconstructed.ppm as protected, the agent acknowledges the message and finishes without rerunning the cleanup, and the verifier finds the correct file on disk. The same iteration-5 round also recovers polyglot-rust-c and large-scale-text-editing, both listed in the change-manifest’s predicted_fixes. configure-git-webserver, also predicted, recovers only partially at iteration 5 because its failure mode involves a state reset path that the iteration-5 guard still treats as overrideable; that gap is closed by the iteration-8 changes described in trajectory 4.

### C.1.3 Trajectory 3: mcmc-sampling-stan

The first two trajectories each used a prompt-and-tool pair. The third shows two harness components from different controllability levels, a tool-level publish-state guard and a step-spanning middleware, working together to flip a task that had been failing for five iterations. Figure [7](https://arxiv.org/html/2604.25850#A3.F7 "Figure 7 ‣ Trajectory before and after the iteration-6 changes. ‣ C.1.3 Trajectory 3: mcmc-sampling-stan ‣ C.1 Trajectories: failing versus passing rollouts ‣ Appendix C Qualitative Case Study ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses") summarizes the before-and-after rollouts.

### The task.

mcmc-sampling-stan asks the agent to install rstan 2.32.7, fit a hierarchical beta-binomial model to 30 observations, and write the posterior means of alpha and beta to two text files. The verifier installs the package itself and reruns the agent’s analysis.R end-to-end, then asserts alpha lies in [2.84, 2.91] and beta lies in [16.1, 16.7].

### Trajectory before and after the iteration-6 changes.

The task scored 0/2 from iteration 1 through iteration 5. The shared failure mode, summarized in the left column of Figure [7](https://arxiv.org/html/2604.25850#A3.F7 "Figure 7 ‣ Trajectory before and after the iteration-6 changes. ‣ C.1.3 Trajectory 3: mcmc-sampling-stan ‣ C.1 Trajectories: failing versus passing rollouts ‣ Appendix C Qualitative Case Study ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"), is a proxy-then-skip pattern in five steps: the agent computes an independent grid-integration estimate of the posterior, writes those numbers as the deliverable, fires the real MCMC sampling as a background job, kills it before completion to “preserve the already-created deliverables”, and submits on a final sweep that only checks the files exist and parse as numbers. The verifier then reruns analysis.R from scratch; the unconverged sampler produces values around 1e19, far outside the expected range. None of the prior rounds catches this trajectory: the iteration-2 prompt edit names a contract-first principle but the agent already believes the grid integration is a faithful contract; the iteration-5 publish-state guard protects the deliverable files but treats analysis.R itself as an unprotected scratch artifact. After the iteration-6 changes are installed, both rollouts run analysis.R at the full iter = 100000 to completion, cross-check against an independent scratch full run in /tmp, and publish the converged values via the new override token; the right column of Figure [7](https://arxiv.org/html/2604.25850#A3.F7 "Figure 7 ‣ Trajectory before and after the iteration-6 changes. ‣ C.1.3 Trajectory 3: mcmc-sampling-stan ‣ C.1 Trajectories: failing versus passing rollouts ‣ Appendix C Qualitative Case Study ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses") traces the passing rollout. The task passes 6/6 verifier tests in both rollouts and stays 2/2 for the next four iterations. The converged values land at alpha approximately 2.872, beta approximately 16.43, near the centers of the expected ranges. The same iteration-6 round also benefits sam-cell-seg, query-optimize, caffe-cifar-10, dna-assembly, and train-fasttext, all of which match one or more of the seven middleware patterns.

Shared prefix, both rollouts, same random seed

S1. ls /app `\rightarrow` data.csv with 30 rows of columns y, n   |  S2. Install rstan 2.32.7 from CRAN as a long background job   |  S3. Author hierarchical_model.stan and analysis.R with chains = 4, iter = 100000, seed = 1

Before iteration 6 changes, iteration 5, reward 0.0

Divergence: trust the proxy, skip the real run
  
 
  
F1. Runs an independent R grid integration of the marginal posterior, gets alpha `\approx` 2.876, beta `\approx` 16.375
  
F2. Writes those grid values into /app/posterior_alpha_mean.txt and /app/posterior_beta_mean.txt as the deliverable
  
F3. Fires Rscript /app/analysis.R as a background job, polls every 30s
  
F4. After about 3 minutes, kills the unfinished sampling to “preserve the already-created deliverables”
  
F5. Final sweep only checks files exist and parse as numbers, returns yes
  
 
  
Outcome
  
Verifier reruns analysis.R; the actual MCMC chain diverges
  
Submitted: alpha = 1.28e19, beta = 2.60e17
  
`\rightarrow` 2 of 6 tests fail, reward 0

Iteration 6 changes that close each gap

Middleware chg-2. Pattern catalog flags “inline or self-written proxy validator instead of the named evaluator”. The risk hint is injected into the next model turn.
  
`\rightarrow` catches F1, F2, F4: the grid integration is a proxy for the named MCMC pipeline, and the kill of analysis.R keeps that proxy in place. The reminder rewires the next turn toward running the named pipeline to completion.
  
 
  
Middleware chg-2, second pattern. Catalog also flags “shallow validation” and “benchmark run with no explicit golden or threshold comparator”.
  
`\rightarrow` catches F5: a file-existence sweep without a tolerance comparator on the verifier’s named outputs is forbidden, and an independent re-run with cross-check is required instead.
  
 
  
Publish-state guard chg-1. Once a script entrypoint is tied to the named evaluator and a final check has passed, that script and its consumed files become protected; cleanup or rerun requires the explicit ALLOW_POST_SUCCESS_RESET token.
  
`\rightarrow` visible at P4 and P5: the override token at every successful submit is evidence the guard is engaged, not silently bypassed.

After iteration 6 changes, same seed, iteration 6, reward 1.0

Divergence: drive the evaluator pipeline to convergence
  
 
  
P1. Smoke-tests analysis.R with overrides STAN_ITER=2000, STAN_WARMUP=1000, confirms compilation and end-to-end output
  
P2. Runs analysis.R at the full iter = 100000 and waits for completion, gets alpha `\approx` 2.872, beta `\approx` 16.43
  
P3. Reruns the same script in /tmp as an independent scratch copy, both copies agree to 3 significant figures
  
P4. Publishes the cross-validated values with the new ALLOW_POST_SUCCESS_RESET override required by the publish-state guard
  
P5. Cleans the unrequested hierarchical_model.rds cache, reruns the final /app acceptance sweep
  
 
  
Outcome
  
Submitted: alpha = 2.872, beta = 16.43
  
`\rightarrow` 6 of 6 tests pass, reward 1

Figure 7: Three-column trajectory comparison for mcmc-sampling-stan before and after the two harness changes shipped at the start of iteration 6: the tool-level publish-state guard chg-1 at commit ff0cf3d and the middleware-level execution-risk hints chg-2 at commit 9651986, whose full manifest entry appears in Figure [10](https://arxiv.org/html/2604.25850#A3.F10 "Figure 10 ‣ C.2.3 Iteration 6: protected entrypoints and execution-risk middleware ‣ C.2 Changes shipped on the four winning rounds ‣ Appendix C Qualitative Case Study ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses"). The banner shows the shared prefix S1 to S3. The left column lists the five divergence steps F1 to F5 of the failing rollout at iteration 5. The middle column lists the iteration-6 components that fire on this trajectory, each annotated with the failure steps it catches. The right column lists the corresponding steps P1 to P5 of the passing rollout at iteration 6. The task stays 2/2 for the next four evaluation rounds.

### C.1.4 Trajectory 4: configure-git-webserver

The fourth trajectory shows the evolve agent doubling back on its own prior decisions. By iteration 7 the publish-state guard had been carried over for three rounds, the middleware for two, and the score had regressed from 75.8 to 73.0. Rather than roll either back, the iteration-7 round patched a loophole in the guard and a salience gap in the middleware; both patches turn out to be load-bearing for configure-git-webserver.

### The task.

configure-git-webserver asks the agent to set up a git repository under /git/server, configure a webserver that serves the working tree under /git/www, deploy a hello-world page, and produce a configuration in which the externally observable URL returns the expected content. The verifier issues an HTTP request from outside the agent’s shell and reads the response body.

### Trajectory before and after the iteration-8 changes.

At iteration 7 the task scored 0/2. The failing rollout reached a fully working deployment, ran a curl-against-localhost self-check that returned the right body, and then issued two cleanup commands prefixed with ALLOW_POST_SUCCESS_RESET: one deletion of /git/www/hello.html and one reset of /git/server/refs/heads/master to an empty state, both rationalized as “leaving a clean repo for grading”. The shell tool’s iteration-5 guard caught these as overrideable resets and let them through once the override token was attached. The external verifier then received a 404 and rejected the rollout. git-multibranch failed in iteration 7 for the same structural reason. In parallel, polyglot-c-py and pytorch-model-recovery failed at iteration 7 with a different but related symptom: the iteration-6 middleware had already emitted the right warnings about clean-layout violation and inline-helper validation, but the warnings were appended only to the tool output, and on the very next model turn the agent ignored them and published. After the iteration-8 changes are installed, configure-git-webserver flips from 0/2 to 2/2. Both rollouts reach the same successful deployment as before, attempt the same overrideable cleanup commands, and have them refused at the shell layer with hard-block messages naming the protected web root and protected ref; the agent acknowledges the messages, drops the cleanup, and submits the live state. git-multibranch flips along the same path. polyglot-c-py, polyglot-rust-c, pytorch-model-recovery, and mteb-retrieve flip via the middleware path: in each, the FRAMEWORK reminder injected before the next model turn carries enough salience for the agent to fix the violation rather than publish over it. Iteration 8’s overall score lands at 76.97, the run’s high-water mark on Figure , and the single biggest jump of the run.

### C.2 Changes shipped on the four winning rounds

### C.2.1 Iteration 2: prompt rules and shell-timeout argument

The Evolve Agent’s response after iteration 1 was two changes. Change chg-1 at commit c0b8a05 is a 68-line append to workspace/systemprompt.md with no mention of SQLite, WAL, or db-wal-recovery; the appended block contains eight numbered rules covering acceptance-contract extraction, evaluator mirroring, minimal-edit semantics, candidate scoring, generalization, time budgeting, end-state readiness, and a stop rule. Change chg-2 at commit 169c34c is a tool-implementation edit that exposes the shell timeout as a per-call argument with a higher ceiling, addressing a class of failures in which the seed harness silently truncated long-running setup commands. Both manifest entries appear in Figure [8](https://arxiv.org/html/2604.25850#A3.F8 "Figure 8 ‣ C.2.1 Iteration 2: prompt rules and shell-timeout argument ‣ C.2 Changes shipped on the four winning rounds ‣ Appendix C Qualitative Case Study ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").

chg-1, iteration 1, commit c0b8a05, level: prompt

Files
  
 
  
`\bullet` workspace/systemprompt.md
  
 
  
What changed
  
 
  
Appended a contract-first workflow of eight numbered rules covering acceptance-contract extraction, evaluator mirroring, minimal-edit semantics, candidate scoring, generalization, time budgeting, end-state readiness, and a stop rule. No SQLite, WAL, or task-specific keywords.
  
 
  
Failure pattern fixed
  
 
  
Agent submitted on a self-invented proxy check such as row count or file exists, instead of reproducing the evaluator’s literal assertions.
  
 
  
Predicted fixes
  
 
  
14 tasks. Examples: configure-git-webserver, query-optimize, mteb-retrieve, train-fasttext.

chg-2, iteration 1, commit 169c34c, level: tool

Files
  
 
  
`\bullet` tool_descriptions/run_shell_command.tool.yaml
  
`\bullet` tools/shell_tools/run_shell_command.py
  
 
  
What changed
  
 
  
Exposed a per-call timeout_ms on the shell tool, added background-execution guidance, and appended a timeout-recovery hint to timed-out shell output so the agent can switch to short probes plus background jobs instead of sitting on the default 5 minute wait.
  
 
  
Failure pattern fixed
  
 
  
Agent burned rollout budget on long foreground installs and sleep-poll loops, repeatedly hitting the default 5 minute timeout.
  
 
  
Predicted fixes
  
 
  
8 tasks. Examples: compile-compcert, regex-chess, adaptive-rejection-sampler.

Figure 8: Two change-manifest entries written in iteration 1, one editing the system prompt and one editing the shell tool. Both appear in the same change_manifest.json produced by the evolve agent, then enter Phase 3 of the next round as binding contracts that the attribution check rolls back if their predicted fixes do not materialize.

### C.2.2 Iteration 5: publish-state mechanism (prompt rules + shell-tool guard)

The Evolve Agent shipped two complementary changes at the iteration-4 boundary, both written for iteration 5. Change chg-7 at commit 3ba3a90 edits workspace/systemprompt.md together with the descriptor of run_shell_command; it adds three rules to the harness’s working memory: a publish-state rule that names the post-acceptance filesystem state as the deliverable surface, a scratch-directory rule for tasks with constrained delivery layouts, and a literal-output rule for DSL, config, and script outputs in which equivalence is judged at the byte level. Change chg-8 at commit 4e0aab9 edits workspace/tools/shell_tools/run_shell_command.py; it installs a stateful publish-state guard inside the shell tool with three behaviors. First, when the shell observes a successful evaluator-style final check, it parses the acceptance command for explicit file paths and roots and records them as protected. Second, when a later command would delete a protected output or reset a protected root, the guard intercepts the command before execution and returns a targeted error explaining which protected target is at risk. Third, the guard accepts an explicit ALLOW_POST_SUCCESS_RESET token from the agent that downgrades the block to a warning and forces the agent to revalidate before submitting. The two changes are paired by design: chg-7 tells the model what publish state is, chg-8 stops the agent from destroying it even when the model forgets the rule. Both manifest entries appear in Figure [9](https://arxiv.org/html/2604.25850#A3.F9 "Figure 9 ‣ C.2.2 Iteration 5: publish-state mechanism (prompt rules + shell-tool guard) ‣ C.2 Changes shipped on the four winning rounds ‣ Appendix C Qualitative Case Study ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").

chg-7, iteration 5, commit 3ba3a90, level: prompt + tool descriptor

Files
  
 
  
`\bullet` workspace/systemprompt.md
  
`\bullet` tool_descriptions/run_shell_command.tool.yaml
  
 
  
What changed
  
 
  
Appended three rules to the harness’s working memory. Publish-state rule: once an evaluator-style final check passes, the resulting filesystem and service state is the deliverable surface and must not be reset to “look clean”. Scratch-directory rule: place exploratory artifacts under /tmp or a scratch path the verifier ignores. Literal-output rule: for DSL, config, or script outputs with byte-level contracts, validate equality at the byte level.
  
 
  
Failure pattern fixed
  
 
  
Agent reached an evaluator-passing state, then issued sweeping cleanup or rewrote outputs to “tidy up”, leaving the verifier with no deliverable.
  
 
  
Predicted fixes
  
 
  
4 tasks. Examples: path-tracing, configure-git-webserver, polyglot-rust-c, large-scale-text-editing.

chg-8, iteration 5, commit 4e0aab9, level: tool implementation

Files
  
 
  
`\bullet` tools/shell_tools/run_shell_command.py
  
 
  
What changed
  
 
  
Installed a stateful publish-state guard inside the shell tool. After a successful evaluator-style final check, the guard parses the acceptance command for explicit file paths and roots and records them as protected. Later destructive commands that would delete a protected output or reset a protected root are intercepted before execution and returned as a targeted error. An explicit ALLOW_POST_SUCCESS_RESET token can downgrade the block to a warning, after which the agent must re-validate before submit.
  
 
  
Failure pattern fixed
  
 
  
Even with the prompt rule in place, the agent still issued destructive cleanup commands after publish-state. Execution-time enforcement at the shell tool is the most direct interlock.
  
 
  
Predicted fixes
  
 
  
Same 4 tasks; load-bearing on path-tracing, whose F4 is the rm -rf of /app/reconstructed.ppm.

Figure 9: The two change-manifest entries written together at the iteration-4 boundary and shipped as the iteration-5 harness. chg-7 names the publish-state rule in the system prompt and tool descriptor; chg-8 installs the execution-time interlock inside the shell tool. The pair flips path-tracing on the next round.

### C.2.3 Iteration 6: protected entrypoints and execution-risk middleware

The Evolve Agent shipped two complementary changes for iteration 6. Change chg-1 at commit ff0cf3d extends the publish-state guard so that script entrypoints tied to the named evaluator become protected after a passing check, with an explicit ALLOW_POST_SUCCESS_RESET token required to override; the token at every successful submit in the passing rollout is the externally visible evidence that the guard is engaged, not silently bypassed. Change chg-2 at commit 9651986 introduces the ExecutionRiskHintsMiddleware; the middleware watches the live sequence of shell commands and tool outputs and emits a targeted note when it detects any of seven cross-step risk patterns: shallow validation that relies on -h, py_compile, or pure existence checks; localhost-only service validation when the contract names an external endpoint; inline or self-written proxy validators replacing a named evaluator; lower-level model or internal API access when the contract names a specific wrapper; benchmark checks with no explicit golden or threshold comparator; repeated long runs that have already exhausted budget for a known failure mode; and repeated retries against the same error. The two patterns relevant to trajectory 3 are inline-proxy validation and shallow validation, which together cover the F1 to F5 sequence: the grid-integration proxy and the kill of analysis.R are the proxy-validator pattern, and the file-existence sweep without a tolerance comparator is the shallow-validation pattern. The shell tool change covers F4 specifically: with analysis.R now protected, the kill becomes a guarded action that requires the override token and forces a revalidation pass before submit. Both manifest entries appear in Figure [10](https://arxiv.org/html/2604.25850#A3.F10 "Figure 10 ‣ C.2.3 Iteration 6: protected entrypoints and execution-risk middleware ‣ C.2 Changes shipped on the four winning rounds ‣ Appendix C Qualitative Case Study ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").

chg-1, iteration 6, commit ff0cf3d, level: tool implementation

Files
  
 
  
`\bullet` tools/shell_tools/run_shell_command.py
  
`\bullet` tool_descriptions/run_shell_command.tool.yaml
  
 
  
What changed
  
 
  
Extended publish-state target extraction to include script entrypoints and explicitly referenced final-check files, on top of the deliverable files and roots already covered by iteration 5. After a successful evaluator-style final check, the guard now blocks rewriting protected files and rerunning protected generator scripts, in addition to the deletion and root-reset cases.
  
 
  
Failure pattern fixed
  
 
  
Agent reached publish-state with a converged generator script, then re-ran or rewrote the script as a “tidy up” pass, invalidating the verified output; this is the F4 step of mcmc-sampling-stan.
  
 
  
Predicted fixes
  
 
  
mcmc-sampling-stan plus residual “validated then mutate” cases such as configure-git-webserver.

chg-2, iteration 6, commit 9651986, level: middleware

Files
  
 
  
`\bullet` workspace/code_agent.yaml
  
`\bullet` workspace/middleware/__init__.py
  
`\bullet` workspace/middleware/execution_risk_hints.py
  
 
  
What changed
  
 
  
Registered a new ExecutionRiskHintsMiddleware via an AfterToolHook that scans every shell command and result, accumulates lightweight state across steps, and queues a targeted reminder when the live history matches one of seven risk patterns: shallow validation via --help or py_compile or existence-only checks; localhost-only service check while the contract names an external interface; inline or self-written proxy validator instead of the named evaluator; low-level model API call bypassing the official wrapper; benchmark run with no explicit golden or threshold comparator; repeated long timeouts on the same command shape; repeated retries hitting the same error signature. Reminders are deduplicated and capped per rollout.
  
 
  
Failure pattern fixed
  
 
  
Cross-step behaviors that only become obvious from the live command history, which prompt-only rules cannot react to in time.
  
 
  
Predicted fixes
  
 
  
6 tasks. Examples: caffe-cifar-10, sam-cell-seg, mteb-retrieve, dna-assembly, train-fasttext.

Figure 10: The two change-manifest entries shipped as the iteration-6 harness. chg-1 extends the iteration-5 publish-state guard from deliverable files to script entrypoints, the missing piece that protects analysis.R in mcmc-sampling-stan. chg-2 introduces the first cross-step component in this run, namely the ExecutionRiskHintsMiddleware watching the live command history for seven risk patterns.

### C.2.4 Iteration 8: hard blocks and FRAMEWORK reminders

The Evolve Agent shipped two changes for iteration 8 that explicitly keep the prior architecture and patch its weak points. Change chg-1 at commit ca35f53 edits workspace/tools/shell_tools/run_shell_command.py and upgrades two soft reasons to hard blocks: deletion of any non-/tmp protected output is now a hard block, and reset of any non-/tmp protected root is now a hard block. The ALLOW_POST_SUCCESS_RESET token can still downgrade other classes of post-success interlocks but can no longer wipe verified live deliverables or empty live roots. Change chg-2 at commit a4a4a29 edits workspace/middleware/execution_risk_hints.py and adds three behaviors. First, a new before_model hook promotes any execution-risk note emitted on the previous step into a FRAMEWORK reminder visible in the next model turn, so the warning becomes part of the reasoning context rather than text appended after the tool output. Second, the middleware infers two contract types once per task from the user request: clean-layout or single-file delivery contracts, and official-wrapper or named-revision contracts. Third, the middleware adds two contract-aware after-tool heuristics: a warning when the agent compiles or builds inside a clean-layout live tree, and a warning when the contract names an official wrapper or revision but the command uses a raw SentenceTransformer or AutoModel style API instead. Both changes are deliberately scoped: chg-1 prevents the destructive shell command itself, chg-2 makes the right warning impossible to overlook on the very next model turn. Both manifest entries appear in Figure [11](https://arxiv.org/html/2604.25850#A3.F11 "Figure 11 ‣ C.2.4 Iteration 8: hard blocks and FRAMEWORK reminders ‣ C.2 Changes shipped on the four winning rounds ‣ Appendix C Qualitative Case Study ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").

chg-1, iteration 8, commit ca35f53, level: tool implementation

Files
  
 
  
`\bullet` tools/shell_tools/run_shell_command.py
  
 
  
What changed
  
 
  
Upgraded two soft reasons to hard blocks. Deletion of any non-/tmp protected output is now a hard block. Reset of any non-/tmp protected root to an empty state is also a hard block. The ALLOW_POST_SUCCESS_RESET token still exists for other classes of post-success interlock but can no longer wipe verified live deliverables or empty live roots.
  
 
  
Failure pattern fixed
  
 
  
Agent attached the override token to delete /git/www/hello.html and reset /git/server/refs/heads/master after a successful deployment check, “returning to a clean repo”; verifier then 404s.
  
 
  
Predicted fixes
  
 
  
2 tasks. Examples: configure-git-webserver, git-multibranch.

chg-2, iteration 8, commit a4a4a29, level: middleware

Files
  
 
  
`\bullet` workspace/middleware/execution_risk_hints.py
  
 
  
What changed
  
 
  
Added a BeforeModelHook that promotes any execution-risk note emitted on the previous step into a FRAMEWORK reminder visible at the top of the next model turn, so warnings enter the reasoning context rather than trail after the tool output. Added one-time per-task contract inference for clean-layout or single-file delivery contracts and official-wrapper or named-revision contracts. Added two new after-tool heuristics: a warning when the agent compiles or builds inside a clean-layout live tree, and a warning when the contract names an official wrapper but the command uses a raw SentenceTransformer or AutoModel style API instead.
  
 
  
Failure pattern fixed
  
 
  
Iteration-6 middleware emitted the right warnings but only into tool output; the agent often made the publish/stop decision on the next model turn and ignored them. Salience promotion plus contract-aware heuristics close this gap.
  
 
  
Predicted fixes
  
 
  
4 tasks. Examples: polyglot-c-py, polyglot-rust-c, mteb-retrieve, pytorch-model-recovery.

Figure 11: Two change-manifest entries written together at the iteration-7 boundary and shipped as the iteration-8 harness. chg-1 hardens the existing publish-state shell guard so that the override token can no longer wipe verified live deliverables. chg-2 makes execution-risk warnings impossible to overlook at the next model turn and adds two contract-aware heuristics. Both are deliberately scoped: chg-1 prevents the destructive command itself, chg-2 fixes the salience gap of the iteration-6 middleware.

### C.3 Reading the change-manifest figures

The trajectories above track individual edits through individual tasks. The change-manifest carries each edit along with its predicted fixes, predicted regressions, and constraint level into Phase 3 of the next iteration, where the attribution check decides whether to keep or roll it back. One manifest figure is attached to each of the four winning rounds, all in the same Files / What changed / Failure pattern fixed / Predicted fixes layout. Figure [8](https://arxiv.org/html/2604.25850#A3.F8 "Figure 8 ‣ C.2.1 Iteration 2: prompt rules and shell-timeout argument ‣ C.2 Changes shipped on the four winning rounds ‣ Appendix C Qualitative Case Study ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses") shows iteration 2’s prompt edit and shell-tool edit written together in the seed round. Figure [9](https://arxiv.org/html/2604.25850#A3.F9 "Figure 9 ‣ C.2.2 Iteration 5: publish-state mechanism (prompt rules + shell-tool guard) ‣ C.2 Changes shipped on the four winning rounds ‣ Appendix C Qualitative Case Study ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses") shows iteration 5’s prompt-and-descriptor rule and shell-guard installation that introduce the publish-state mechanism. Figure [10](https://arxiv.org/html/2604.25850#A3.F10 "Figure 10 ‣ C.2.3 Iteration 6: protected entrypoints and execution-risk middleware ‣ C.2 Changes shipped on the four winning rounds ‣ Appendix C Qualitative Case Study ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses") shows iteration 6’s extension of the publish-state guard to script entrypoints and the introduction of the cross-step ExecutionRiskHintsMiddleware. Figure [11](https://arxiv.org/html/2604.25850#A3.F11 "Figure 11 ‣ C.2.4 Iteration 8: hard blocks and FRAMEWORK reminders ‣ C.2 Changes shipped on the four winning rounds ‣ Appendix C Qualitative Case Study ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses") shows iteration 8’s keep-and-improve patches that close the override-token loophole on the guard and promote middleware reminders into a FRAMEWORK note visible at the next model turn. Together the four figures cover three of the four constraint levels the evolve agent uses, namely prompt, tool implementation, and middleware, all written in the same JSON shape and all subject to the same automatic rollback if their predicted fixes do not appear.

## Appendix D Per-round Self-attribution Breakdown

This appendix expands the aggregate self-attribution result of §[4.4.2](https://arxiv.org/html/2604.25850#S4.SS4.SSS2 "4.4.2 RQ3b: how reliably the loop’s self-attribution tracks reality ‣ 4.4 RQ3: Analysis ‣ 4 Experiments ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses") with a per-round breakdown across the four fix/regression by precision/recall panels.

[Figures 12](https://arxiv.org/html/2604.25850#A4.F12 "In Appendix D Per-round Self-attribution Breakdown ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses") and [13](https://arxiv.org/html/2604.25850#A4.F13 "Figure 13 ‣ Appendix D Per-round Self-attribution Breakdown ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses") show the per-round breakdown across the four fix/regression by precision/recall panels. Bars decompose each denominator, predicted for precision and actual for recall, into deep-blue TP versus pale FP or FN; the dashed line traces the metric on the right-hand `0` to `100\%` axis, and the solid line shows contemporaneous pass@1. Fix-precision and fix-recall both swing from near-zero to near-saturation across rounds, so the evolve model’s causal attribution for its own improvements is informative if noisy. Regression predictions instead stay near the floor, below `25\%` on most rounds: across the 9 rounds the agent issued 43 unique regression predictions and only 5 landed, giving cumulative `P=11.6\%`, while 40 regressions the agent did not foresee actually occurred, giving cumulative `R=11.1\%`.

Figure 12: Per-round fix predictions. Left: precision. Right: recall. Bars decompose each denominator into TP versus FP or FN; lines overlay the metric and contemporaneous pass@1.

Figure 13: Per-round regression predictions. Left: precision. Right: recall. Same encoding as Fig. [12](https://arxiv.org/html/2604.25850#A4.F12 "Figure 12 ‣ Appendix D Per-round Self-attribution Breakdown ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").

## Appendix E Broader Impact

This work introduces *agentic harness engineering* (AHE), a self-evolving loop in which a coding agent edits its own scaffolding (system prompt, tools, middleware, and long-term memory) from execution feedback. AHE lowers the human engineering cost of producing competitive coding agents: practitioners without dedicated harness teams can obtain higher pass@1 from the same base model and at lower per-trial token cost than prompt-only self-evolution baselines, which broadens access to capable coding assistants for academic groups, smaller organizations, and educational settings. Because the loop encodes recurring coordination patterns into tools, middleware, and memory rather than into ever-longer prompts, it reduces per-call compute and the associated energy footprint at inference time. It also enables rapid harness iteration that can keep pace with the cadence of base-model releases, so the surrounding scaffolding need not lag every new model. Negative societal impacts and the corresponding generalization hazards are discussed in §[Limitations](https://arxiv.org/html/2604.25850#Sx1 "Limitations ‣ Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses").
