---
title: "When Continual Learning Moves to Memory: A Study of Experience Reuse in LLM Agents"
url: https://arxiv.org/abs/2604.27003
published: 2026-04-29
fetched: 2026-11-11
type: paper
topics: [context-memory, memory, multi-agent]
summary: "从稳定性—可塑性角度研究外部经验检索，区分经验表征和组织方式；观察抽象过程经验、负迁移以及旧知识遗忘的取舍。"
---

# When Continual Learning Moves to Memory: A Study of Experience Reuse in LLM Agents

Qisheng Hu
  
Quanyu Long
  
Wenya Wang
Affiliation: Nanyang Technological University
Email: qisheng001@e.ntu.edu.sg

## Abstract

Memory-augmented LLM agents offer an appealing shortcut to continual learning: rather than updating model parameters, they accumulate experience in external memory, seemingly sidestepping the stability–plasticity dilemma of parametric learning. We show that this challenge does not disappear but resurfaces at the memory level. Under a limited context window, old and new experiences compete during retrieval, relocating the continual-learning bottleneck from parameter updates to memory access. To study this phenomenon, we introduce a `(k,v)` framework that disentangles two fundamental design axes of external memory: how experience is *represented* and how it is *organized* for retrieval. Across sequential-task experiments in ALFWorld and BabyAI, we find that abstract procedural memories transfer more reliably than detailed trajectories, while negative transfer disproportionately harms the hard cases. Moreover, finer-grained memory organization is not universally beneficial: designs that yield strong forward transfer can simultaneously induce severe forgetting. Together, these results reveal that external memory does not resolve the continual-learning problem; it reshapes it into a problem of memory representation and retrieval design.

## 1 Introduction

A growing body of work equips LLM agents with external memory, from retrieval-augmented language models ([Borgeaud et al., 2022](https://arxiv.org/html/2604.27003v1#bib.bib23); [Wang et al., 2023b](https://arxiv.org/html/2604.27003v1#bib.bib15)) to agent systems that store and reuse experience across interactions ([Zhong et al., 2024](https://arxiv.org/html/2604.27003v1#bib.bib4); [Shinn et al., 2023](https://arxiv.org/html/2604.27003v1#bib.bib1); [Wang et al., 2023a](https://arxiv.org/html/2604.27003v1#bib.bib2); [Packer et al., 2023](https://arxiv.org/html/2604.27003v1#bib.bib13); [Zhao et al., 2024](https://arxiv.org/html/2604.27003v1#bib.bib3); [Xu et al., 2025](https://arxiv.org/html/2604.27003v1#bib.bib17)). Such designs are appealing because they appear to sidestep a central challenge of learning from sequential experience: rather than forcing old and new knowledge into the same model weights, the agent can preserve and reuse past experience in an external memory and continue accumulating new experience online.
This makes memory-augmented agents especially relevant to continual learning (CL), whose core setting assumes sequentially arriving data and ongoing adaptation over time. In this sense, the online nature of LLM agent memory is not merely compatible with CL but inherently instantiates its streaming requirement.
Moreover, because old experience can remain stored while new experience is continuously added, one might expect memory-augmented agents to enjoy both strong *stability*, in the sense of retaining previously acquired capability through stored memories, and strong *plasticity*, in the sense of adapting to new tasks by incorporating new experience into memory.

![Refer to caption](https://arxiv.org/html/2604.27003v1/fig/CL_Paradigm.png)

Figure 1: Evaluation protocol for the `A\to B` direction. The agent first learns a stream of Task A instances from empty memory, then continues with a stream of Task B instances while reusing the accumulated memory.

However, external memory does not eliminate the continual-learning challenge but instead relocates it.
In parametric CL, the central difficulty is interference in weight space: learning new tasks can overwrite knowledge useful for old ones, leading to the well-known stability–plasticity dilemma ([Kirkpatrick et al., 2017](https://arxiv.org/html/2604.27003v1#bib.bib7); [Lopez-Paz and Ranzato, 2017](https://arxiv.org/html/2604.27003v1#bib.bib8); [Wang et al., 2024a](https://arxiv.org/html/2604.27003v1#bib.bib9)).
In memory-augmented agents, past experience can in principle be *stored* without overwriting parameters, but old experience is only useful if it can be effectively *retrieved* and inserted into the model’s limited context window at the right time.
Once tasks arrive sequentially, old and new experiences therefore still compete: the continual-learning bottleneck shifts from how to store knowledge to which experience is retrieved, reused, and prioritized under a limited retrieval budget.
Concretely, irrelevant memories may be recalled, introducing *retrieval pollution*; useful experiences may be displaced by other retrieved items under a finite context window, creating *context competition*; and as the memory store grows across tasks, relevant experience may become harder to identify, resulting in *memory dilution*.

Despite rapid progress in memory design, we still lack a controlled understanding of how external memory behaves under sequential task shift.
Recent surveys organize the design space of memory-equipped agents ([Zhang et al., 2025](https://arxiv.org/html/2604.27003v1#bib.bib24)), and recent work has begun to frame richer retrieval as a form of non-parametric continual learning ([Gutiérrez et al., 2025](https://arxiv.org/html/2604.27003v1#bib.bib19)).
However, much of the current literature primarily demonstrates improved performance within a task or a task family, rather than evaluating the core questions that define continual learning as a learning problem: does accumulated experience support transfer to future tasks, or does it induce negative transfer? Does new experience preserve or degrade performance on earlier tasks?
In other words, although many memory-agent systems are continuous in operation, far fewer study continual learning in the classical sense.

In this paper, we study memory-augmented online learning through a continual-learning lens.
Using controlled task sequences in ALFWorld ([Shridhar et al., 2020](https://arxiv.org/html/2604.27003v1#bib.bib5)) and BabyAI ([Chevalier-Boisvert et al., 2018](https://arxiv.org/html/2604.27003v1#bib.bib6)), we measure not only within-task improvement but also transfer and forgetting across tasks, focusing on two fundamental design axes: how experience is *represented* (from raw episodic trajectories to abstract procedural insights) and how it is *organized* (memory granularity and retrieval frequency).
We further leverage subset-level diagnostic analyses that localize where negative transfer arises. Our central findings are:

- •

  Abstraction shapes whether memory helps or hurts. Raw trajectories tend to hinder adaptation to new tasks, while abstract insights are safer to reuse and can reduce forgetting of earlier tasks.
- •

  Negative transfer concentrates on hard cases. Cross-task retrieval disproportionately harms cases the agent cannot yet solve on its own, while cases it already handles are comparatively robust.
- •

  Finer-grained memory organization is not universally better. Both finer storage granularity and more frequent retrieval can help or hurt, depending on the diversity of stored experience and the structure of the target task.
- •

  A stability–plasticity trade-off can emerge through retrieval. The design that well supports adaptation to a new task can simultaneously cause significant forgetting of an earlier one.

## 2 Framework & Experimental Setup

### 2.1 Agent Memory as Continual Learning

Our experimental paradigm consists of two sequential phases, Task A and Task B, each containing a stream of task instances.
Figure [1](https://arxiv.org/html/2604.27003v1#S1.F1 "Figure 1 ‣ 1 Introduction ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents") illustrates the process: the agent starts from empty memory(experience pool), processes Task A instances, and then continues with Task B while carrying over the accumulated memory.
In our main experiments, each phase contains `n=200` training instances.
For each instance, the agent retrieves relevant experience from a shared external memory `\mathcal{M}`, attempts the task, and then stores the resulting experience back into `\mathcal{M}`.
When the phase switches from Task A to Task B, `\mathcal{M}` is reused and continues to grow.
Concretely, the agent follows a ReAct-style interaction loop ([Yao et al., 2022](https://arxiv.org/html/2604.27003v1#bib.bib10)) and uses the ReMe memory module ([Cao et al., 2025](https://arxiv.org/html/2604.27003v1#bib.bib22)); retrieved experiences are inserted into the model context before the first action step.

This setup is naturally a form of non-parametric continual learning.
The LLM backbone is frozen, so there is no parametric forgetting.
However, behavior still depends on what is recalled into the finite context window, so retrieval pollution, context competition, and memory dilution remain central sources of interference.

|  |  |  |
| --- | --- | --- |
|  | Parametric CL | Memory CL |
| Carrier | Model weights | External memory |
| Interference | Gradient overwrite | Retrieval pollution |
| Bottleneck | Parameter capacity | Context window |

Table 1: Parametric vs. memory-based CL. External memory avoids weight overwriting but introduces a retrieval bottleneck.

### 2.2 A `(k,v)` View of Experience Reuse

Given continual learning in memory-augmented agents hinges on retrieval, the central question is whether stored experience can be effectively *reused* across tasks and over time.
In practice, experience reuse varies widely across memory designs: some memories remain overly specific to transfer well, while others fail to be retrieved when needed.
This suggests that successful reuse depends on two factors: how experience is *represented*, and how it is *organized and accessed*.
To analyze these factors systematically, we model each memory unit as a key–value pair `(k,v)`. This abstraction separates the representation of experience from the mechanism used to retrieve it, allowing us to characterize reuse along two complementary dimensions.

Value `v` captures the *representation* of experience.
A memory may preserve raw, instance-specific procedural detail or store more abstract, transferable insights, which in turn shapes how brittle or reusable the retrieved content is (Study 1).

Key `k` captures how experience is organized and accessed.
We distinguish *storage granularity* (does one memory unit correspond to a whole task-level bundle or a insight-level unit?) from *retrieval granularity* (is memory retrieved once per task instance or updated more frequently during execution?). Together these determine whether the right unit can be matched and recalled at the right time (Study 2).

### 2.3 Continual Learning Metrics

For a two-phase sequence, we use transfer-oriented metrics from continual learning on held-out test sets.
Task A and Task B denote the two task families in the sequence.
Here `\text{Acc}_{T}(\cdot)` denotes success rate on the held-out test set of task `T`.

### Forward Transfer (FWT).

For the sequence `A\!\to\!B`, forward transfer measures whether prior learning on Task A helps or hurts Task B:

|  |  |  |
| --- | --- | --- |
|  | `\mathrm{FWT}(A\!\to\!B)=\text{Acc}_{B}(\varnothing\!\to\!A\!\to\!B)-\text{Acc}_{B}(\varnothing\!\to\!B).` |  |

`\mathrm{FWT}<0` indicates impaired plasticity, while `\mathrm{FWT}>0` indicates positive transfer.

### Backward Transfer (BWT).

For the same sequence `A\!\to\!B`, backward transfer measures whether the later phase degrades the earlier task:

|  |  |  |
| --- | --- | --- |
|  | `\mathrm{BWT}(A\!\to\!B)=\text{Acc}_{A}(\varnothing\!\to\!A\!\to\!B)-\text{Acc}_{A}(\varnothing\!\to\!A),` |  |

`\mathrm{BWT}<0` indicates forgetting, while `\mathrm{BWT}>0` indicates positive backward transfer.
Both FWT and BWT are indexed by the *training sequence* (`A\!\to\!B` or `B\!\to\!A`): FWT refers to the later task, BWT to the earlier one.

### RR/NL subset diagnostic.

Average success alone does not tell us *where* transfer occurs, so we partition each test set using the no-memory baseline into a baseline-success subset (easy cases) and a baseline-fail subset (hard cases).
We then measure Retention Rate (RR), the success rate on the baseline-success subset after memory is introduced, and New Learning rate (NL), the success rate on the baseline-fail subset after memory is introduced.
For a cross-task run `X\to T`, we define:

|  |  |  |  |
| --- | --- | --- | --- |
|  | `\displaystyle\Delta\mathrm{RR}` | `\displaystyle=\text{RR}(\varnothing\!\to\!X\!\to\!T)-\text{RR}(\varnothing\to T),` |  |
|  |  |  |  |
| --- | --- | --- | --- |
|  | `\displaystyle\Delta\mathrm{NL}` | `\displaystyle=\text{NL}(\varnothing\!\to\!X\!\to\!T)-\text{NL}(\varnothing\to T).` |  |

These deltas distinguish two failure modes:

- •

  `\Delta\mathrm{RR}<0`: harmful reuse. Cross-task memory breaks previously solved cases.
- •

  `\Delta\mathrm{NL}<0`: ineffective reuse. Cross-task memory fails to help, or further harms, previously difficult cases.

### 2.4 Environments, Task Pairs, and Protocol

| Env | Task | BL | `n_{\text{s}}` | `n_{\text{f}}` |
| --- | --- | --- | --- | --- |
| ALFWorld | A: pick_and_place | 95% | 95 | 5† |
| B: pick_clean_place | 54% | 54 | 46 |
| BabyAI | A: action_obj_door | 70% | 70 | 30 |
| B: find_obj | 49% | 49 | 51 |

Table 2: Task pairs. BL: no-memory baseline. `n_{\text{s}}`/`n_{\text{f}}`: baseline-success/fail subset sizes. †Small baseline-fail subset (`n<10`), NL-based estimates are noisy and omitted from the main results tables.

We analyze one task pair in ALFWorld ([Shridhar et al., 2020](https://arxiv.org/html/2604.27003v1#bib.bib5)) and one in BabyAI ([Chevalier-Boisvert et al., 2018](https://arxiv.org/html/2604.27003v1#bib.bib6)) (Table [2](https://arxiv.org/html/2604.27003v1#S2.T2 "Table 2 ‣ 2.4 Environments, Task Pairs, and Protocol ‣ 2 Framework & Experimental Setup ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents")).
In ALFWorld, Task A uses instructions of the form “put X in Y,” while Task B uses “put a clean X in Y.” The two tasks are therefore highly similar at the instruction level but differ procedurally, making them well-suited for studying retrieval pollution.
In BabyAI, Task A produces heterogeneous queries across three sub-task types, whereas Task B produces homogeneous “find [object]” queries. This contrast is especially useful in Study 2 for analyzing how storage granularity and retrieval frequency interact with query structure.
Further protocol details are given in Appendix [A](https://arxiv.org/html/2604.27003v1#A1 "Appendix A Experimental Details ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").

## 3 Study 1: Memory Representation

We investigate the value `v`: how does the representation of stored experience affect CL dynamics?
We compare two representations:
Raw, which stores the action–observation trajectory from each episode,
and Insight, which stores LLM-abstracted strategy insights distilled from the trajectory.

|  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
|  |  | Performance (%) | | | Diagnostic | |
| Env | Repr | `\varnothing\!\!\to\!\!T` | `X\!\!\to\!\!T` | FWT | `\Delta\mathrm{RR}` | `\Delta\mathrm{NL}` |
| A`\to`B | | | | | | |
| ALF | Raw | 80.5 | 71.0 | `-`9.5 | `+`4.6 | `-`26.1 |
| Insight | 65.5 | 72.0 | `+`6.5 | `+`9.3 | `+`3.3 |
| Baby | Raw | 53.5 | 46.0 | `-`7.5 | `-`2.0 | `-`12.7 |
| Insight | 46.0 | 55.0 | `+`9.0 | `+`8.2 | `+`9.8 |
| B`\to`A | | | | | | |
| ALF | Raw | 92.0 | 91.5 | `-`0.5 | `-`0.7 | — |
| Insight | 97.0 | 94.5 | `-`2.5 | `-`1.1 | — |
| Baby | Raw | 64.0 | 71.0 | `+`7.0 | `+`2.9 | `+`16.7 |
| Insight | 65.5 | 73.0 | `+`7.5 | `+`1.4 | `+`21.7 |

Table 3: Study 1 FWT results. ALFWorld B`\to`A: `\Delta\mathrm{NL}` omitted for small samples.

### 3.1 Abstraction Facilitates Safer Cross-Task Reuse

Table [3](https://arxiv.org/html/2604.27003v1#S3.T3 "Table 3 ‣ 3 Study 1: Memory Representation ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents") and Figure [2](https://arxiv.org/html/2604.27003v1#S3.F2 "Figure 2 ‣ 3.1 Abstraction Facilitates Safer Cross-Task Reuse ‣ 3 Study 1: Memory Representation ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents") present the full results.
The clearest pattern appears in the A`\to`B sequence: Raw produces negative FWT across both environments, while Insight shifts transfer to positive.
At the task-family level, Task A is relatively easier than Task B in both environments, as reflected in the baseline success rates in Table [2](https://arxiv.org/html/2604.27003v1#S2.T2 "Table 2 ‣ 2.4 Environments, Task Pairs, and Protocol ‣ 2 Framework & Experimental Setup ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").

This directional asymmetry helps explain why abstraction matters most here.
When experience from a relatively easier task is reused for a relatively harder one, raw trajectories can carry over procedures that look relevant but miss the additional structure the harder task requires.
In ALFWorld, for example, Task A trajectories prescribe “take`\to`go`\to`place” while Task B requires an additional cleaning step.
In this case, raw procedural detail can push the agent toward a behavior that is locally plausible but globally ill-suited to the new task (see Appendix [F](https://arxiv.org/html/2604.27003v1#A6 "Appendix F Case Analyses ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents") for qualitative examples).

Insight memory reduces this risk by abstracting away from task-specific action scripts and preserving higher-level guidance.
As a result, abstraction appears to facilitate safer reuse precisely in the direction where cross-task procedural mismatch is most damaging.
By contrast, in the B`\to`A sequence the gap between Raw and Insight becomes much smaller, suggesting that experience from the relatively harder task is less harmful when reused for the easier one.
Appendix [F.2](https://arxiv.org/html/2604.27003v1#A6.SS2 "F.2 Study 1: Why the B→A Gap Is Small ‣ Appendix F Case Analyses ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents") provides a fuller discussion of this directional asymmetry.

Figure 2: FWT by representation. In the A`\to`B direction, Raw produces negative transfer while Insight yields positive transfer across both environments.

### 3.2 Negative Transfer Is Concentrated on Hard Cases

Figure 3: `\Delta\mathrm{RR}`/`\Delta\mathrm{NL}` decomposition (A`\to`B). Under Raw, the hard subset (purple) suffers more than the easy subset (teal), especially on ALFWorld. Insight memory largely reduces this asymmetry.

The RR/NL diagnostic (Figure [3](https://arxiv.org/html/2604.27003v1#S3.F3 "Figure 3 ‣ 3.2 Negative Transfer Is Concentrated on Hard Cases ‣ 3 Study 1: Memory Representation ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents")) shows that negative transfer is not evenly distributed.
The most illustrative case is ALFWorld A`\to`B: under Raw, `\Delta\mathrm{RR}=+4.6` but `\Delta\mathrm{NL}=-26.1`, so the easy subset is largely preserved while the hard subset degrades sharply.
This pattern is intuitive: cases the agent can already solve tend to remain solvable regardless of what is retrieved, whereas cases it cannot yet solve depend much more on retrieved guidance.
When that guidance comes from a different task, more procedural details is more likely to mislead than to help.

Insight memory largely reduces this vulnerability, as abstract representations do not prescribe task-specific procedures.

In summary, representation choice is especially important for the hardest test instances as they are the most vulnerable to cross-task noise.

### 3.3 Within-Task Advantage Does Not Predict Cross-Task Benefit

Figure 4: Within-task vs. cross-task performance on Task B. Raw’s large within-task advantage disappears or reverses in the cross-task setting.

The Raw–Insight comparison highlights a practical pitfall: the representation that works best within a single task distribution may not retain that advantage once cross-task reuse is introduced (Figure [4](https://arxiv.org/html/2604.27003v1#S3.F4 "Figure 4 ‣ 3.3 Within-Task Advantage Does Not Predict Cross-Task Benefit ‣ 3 Study 1: Memory Representation ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents")).
On ALFWorld Task B, Raw has a large within-task advantage because detailed trajectories are highly informative when reused within the *same* task family.
Under cross-task reuse, however, that advantage disappears: both conditions converge to similar performance, with Insight slightly ahead.
On BabyAI, the shift is stronger still: Raw declines while Insight improves, producing a clear crossover.
The underlying mechanism is similar in both environments: procedural detail is an asset within-task but can become a liability once the retrieved procedure belongs to a different task (see Appendix [F](https://arxiv.org/html/2604.27003v1#A6 "Appendix F Case Analyses ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents")).
The implication is straightforward: a memory design that looks best within a single task distribution may not be the best choice for cross-task deployment.

### 3.4 Backward Transfer: Abstraction Reduces Forgetting

Figure 5: BWT by representation. On BabyAI, Insight achieves positive BWT under the B`\to`A sequence while Raw causes forgetting. On ALFWorld, both representations show moderate forgetting.

|  |  | BWT(A`\to`B) | | BWT(B`\to`A) | |
| --- | --- | --- | --- | --- | --- |
| Env | Repr | BWT | `\Delta\mathrm{RR}` | BWT | `\Delta\mathrm{RR}` |
| ALF | Raw | `+`0.5 | `+`0.5 | `-`5.5 | `+`2.9 |
| Insight | `-`1.0 | 0.0 | `-`3.5 | `+`4.6 |
| Baby | Raw | `+`3.0 | `+`2.9 | `-`4.0 | `+`2.1 |
| Insight | 0.0 | `+`2.2 | `+`3.5 | `+`8.2 |

Table 4: Study 1 backward transfer. BWT(`X{\to}Y`) re-evaluates Task `X` after the full `X{\to}Y` sequence. `\Delta\mathrm{RR}` shown for the baseline-success subset.

We now ask whether the same abstraction effect extends to *stability*, measured via backward transfer (Table [4](https://arxiv.org/html/2604.27003v1#S3.T4 "Table 4 ‣ 3.4 Backward Transfer: Abstraction Reduces Forgetting ‣ 3 Study 1: Memory Representation ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents"), Figure [5](https://arxiv.org/html/2604.27003v1#S3.F5 "Figure 5 ‣ 3.4 Backward Transfer: Abstraction Reduces Forgetting ‣ 3 Study 1: Memory Representation ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents")).

BWT(A`\to`B) is near-zero in all conditions, which is unsurprising given Task A’s high baseline and limited room for change.
The more informative sequence is B`\to`A, where BWT measures whether continuing with Task A degrades previously learned Task B performance.
On ALFWorld, both representations show moderate forgetting.
On BabyAI, however, the two diverge: Insight achieves *positive* backward transfer, while Raw causes forgetting.

This mirrors the forward-transfer story.
Raw trajectories from Task A are task-specific procedures that, once mixed into the pool, can mislead retrieval for Task B.
Insight memories from Task A, by contrast, encode task-agnostic principles that may also be useful for Task B, enriching rather than polluting the pool.
The benefit of abstraction therefore appears to extend beyond forward transfer: it can also reduce forgetting, and in some settings even support positive backward transfer.

### 3.5 Study 1 Summary

1. 1.

   Abstraction facilitates safer cross-task reuse. Raw trajectories tend to behave like misleading procedures across task boundaries, while abstract insights are more transferable.
2. 2.

   Negative transfer is concentrated where help is most needed. Cross-task noise disproportionately harms hard cases, which depend most on retrieved guidance.
3. 3.

   Within-task evaluation is not enough. A representation that looks strong within one task distribution can lose its advantage once cross-task reuse is introduced.
4. 4.

   Abstraction can also reduce forgetting. Beyond helping adaptation to new tasks, abstract insights make previously learned behavior less vulnerable to cross-task interference.

## 4 Study 2: Memory Organization

![Refer to caption](https://arxiv.org/html/2604.27003v1/fig/Cond_Comparison.png)

Figure 6: Visual comparison of Cond-Agg, Cond-Ind, and Cond-Step.

Study 1 fixed memory organization and varied representation.
We now fix representation to Insight (the better `v` from Study 1) and vary the `k` dimension: how memory units are organized and accessed.
We vary two aspects of granularity (Figure [6](https://arxiv.org/html/2604.27003v1#S4.F6 "Figure 6 ‣ 4 Study 2: Memory Organization ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents")):

Cond-Agg bundles all insights from an episode into a single memory entry keyed by the task instruction. The agent queries once at the start of each episode and retrieves the full bundle.
Cond-Ind stores each insight as a separate entry with its own retrieval key (a short applicability description). The agent still queries once per episode but can retrieve individual insights from different source episodes.
Cond-Step uses the same insight-level storage as Cond-Ind but re-queries periodically during execution, allowing retrieved guidance to update as the episode progresses.
Appendix [B](https://arxiv.org/html/2604.27003v1#A2 "Appendix B Memory Content Examples ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents") shows examples of stored entries for each condition.

Comparing Agg vs. Ind isolates *unit granularity* (bundled vs. individual storage), while Ind vs. Step isolates *retrieval frequency* (single vs. periodic querying). All conditions surface roughly the same number of insights per retrieval, keeping the information budget comparable.

|  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
|  |  | Performance (%) | | | Diagnostic | |
| Env | Cond | `\varnothing\!\!\to\!\!T` | `X\!\!\to\!\!T` | FWT | `\Delta\mathrm{RR}` | `\Delta\mathrm{NL}` |
| A`\to`B | | | | | | |
| ALF | Agg | 65.5 | 72.0 | `+`6.5 | `+`9.3 | `+`3.3 |
| Ind | 55.0 | 53.0 | `-`2.0 | `-`4.6 | `+`0.9 |
| Step | 79.5 | 78.0 | `-`1.5 | `-`3.7 | `+`1.1 |
| Baby | Agg | 46.0 | 55.0 | `+`9.0 | `+`8.2 | `+`9.8 |
| Ind | 32.0 | 47.0 | `+`15.0 | `+`19.4 | `+`10.8 |
| Step | 48.0 | 45.5 | `-`2.5 | `-`4.1 | `-`1.0 |
| B`\to`A | | | | | | |
| ALF | Agg | 97.0 | 94.5 | `-`2.5 | `-`1.1 | — |
| Ind | 96.5 | 97.0 | `+`0.5 | `+`0.5 | — |
| Step | 99.0 | 98.5 | `-`0.5 | `-`1.1 | — |
| Baby | Agg | 65.5 | 73.0 | `+`7.5 | `+`1.4 | `+`21.7 |
| Ind | 75.5 | 74.5 | `-`1.0 | `{\approx}`0 | `-`1.7 |
| Step | 70.0 | 77.5 | `+`7.5 | `+`4.3 | `+`15.0 |

Table 5: Study 2 Forward transfer results.

Figure 7: FWT by memory organization. No condition universally dominates; the best configuration depends on the task pair.

Figure 8: BabyAI: FWT by direction, contrasting unit granularity (left) and retrieval frequency (right). Fine-grained storage or retrieval helps in one direction but not the other.

### 4.1 Memory-Unit Granularity (Agg vs. Ind)

Tables [5](https://arxiv.org/html/2604.27003v1#S4.T5 "Table 5 ‣ 4 Study 2: Memory Organization ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents") and Figure [7](https://arxiv.org/html/2604.27003v1#S4.F7 "Figure 7 ‣ 4 Study 2: Memory Organization ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents") present the results.
The key pattern is that finer storage granularity helps only when splitting memory produces entries that are genuinely different in content and can be retrieved separately.

### BabyAI: Diverse And Homogeneous Source Memories Behave Differently.

The two directions produce opposite results (Figure [8](https://arxiv.org/html/2604.27003v1#S4.F8 "Figure 8 ‣ 4 Study 2: Memory Organization ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents"), left).

In A`\to`B, Cond-Ind achieves `+`15.0% (vs. Agg’s `+`9.0%), with both subsets improving (`\Delta\mathrm{RR}=+19.4`, `\Delta\mathrm{NL}=+10.8`; Figure [9](https://arxiv.org/html/2604.27003v1#S4.F9 "Figure 9 ‣ ALFWorld: Bundling Remains The Safer Choice. ‣ 4.1 Memory-Unit Granularity (Agg vs. Ind) ‣ 4 Study 2: Memory Organization ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents")).
Task A contains three distinct sub-task types (go-to, pick-up, open-door), so its insights reflect different strategies.
When stored individually, each entry has a distinct retrieval key, allowing the retriever to match Task B queries to the most relevant one.

In B`\to`A, Cond-Ind drops to `-`1.0% while Agg reaches `+`7.5%.
Task B episodes are essentially systematic grid search (“find [object]”), producing highly repetitive insights.
Splitting them creates a large pool of near-identical entries that the retriever cannot meaningfully distinguish.
Individually indexing identical memories therefore offers little advantage over bundling.
We call this *retrieval diversity collapse*: the pool appears large, but homogeneous queries repeatedly retrieve the same few entries (Appendix [D](https://arxiv.org/html/2604.27003v1#A4 "Appendix D Retrieval Diversity Collapse ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents")).
Appendix [F](https://arxiv.org/html/2604.27003v1#A6 "Appendix F Case Analyses ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents") provides retrieval-level examples of both regimes.

### ALFWorld: Bundling Remains The Safer Choice.

ALFWorld shows a milder contrast than BabyAI, but the pattern is compatible with the same conclusion.
In A`\to`B, Agg outperforms Ind (`+`6.5 vs. `-`2.0), and only Agg yields consistently positive diagnostics (`\Delta\mathrm{RR}=+9.3`, `\Delta\mathrm{NL}=+3.3`; Figure [9](https://arxiv.org/html/2604.27003v1#S4.F9 "Figure 9 ‣ ALFWorld: Bundling Remains The Safer Choice. ‣ 4.1 Memory-Unit Granularity (Agg vs. Ind) ‣ 4 Study 2: Memory Organization ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents")).
The results are consistent with the view that ALFWorld tasks rely on coherent multi-step strategies (e.g., find`\to`take`\to`clean`\to`place), so fragmenting those strategies into individually indexed insights may weaken the structure that is preserved when they are bundled.

Figure 9: `\Delta\mathrm{RR}`/`\Delta\mathrm{NL}` diagnostic for A`\to`B (Study 2). On BabyAI, Cond-Ind shows broad improvement across both subsets (`\Delta\mathrm{RR}=+19.4`, `\Delta\mathrm{NL}=+10.8`), while on ALFWorld Cond-Agg yields positive diagnostics.

### Overall.

The two environments point to the same practical lesson from different angles.
Fine-grained storage is most useful when task experience can be decomposed into self-contained insights that remain useful on their own.
When the stored experience is highly repetitive or is better understood as one coherent multi-step strategy, splitting it into many entries is less helpful, and coarser aggregation is the safer choice.

### 4.2 Retrieval Frequency (Ind vs. Step)

The previous section examined how memories should be stored; here we ask how often they should be retrieved.
The key question is whether step-level retrieval helps when an agent’s information needs change during an episode.
We use the Ind–Step comparison to study retrieval frequency.
Appendix [F](https://arxiv.org/html/2604.27003v1#A6 "Appendix F Case Analyses ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents") provides relevant case analyses.

### BabyAI: Step Helps When Tasks Have Distinct Phases.

In B`\to`A, Step achieves `+`7.5% FWT while Ind drops to `-`1.0%.
Task A contains distinct execution phases: the agent must navigate and then interact with objects or doors.
Periodic re-querying may help because the information needed later in the episode differs from what is needed initially.

In A`\to`B, the pattern reverses: Step yields `-`2.5% while Ind achieves `+`15.0%.
Task B follows a largely uniform execution pattern, essentially systematic grid search throughout the episode.
When information needs remain stable over time, re-querying is less likely to surface new guidance and more likely to return redundant content.

### ALFWorld: Within-Task Gains Do Not Transfer Cleanly.

On ALFWorld, cross-task FWT differences between Ind and Step are small (`\pm`1.5pp), making retrieval-frequency effects less distinct under task shift.
However, Step achieves substantially higher *within-task* performance (e.g., 79.5% vs. 55.0% scratch on Task B; Appendix [C](https://arxiv.org/html/2604.27003v1#A3 "Appendix C Retrieval Frequency: Additional Analysis ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents")).
This suggests step-level retrieval can be highly effective for multi-step tasks within the same distribution, but the advantage does not necessarily transfer across tasks.
As in Study 1, within-task performance alone may therefore give a misleading picture of which memory design is best under task shift.

### Overall.

More frequent retrieval is not universally beneficial.
It appears most useful when the target task’s information needs change over the course of execution; when they remain stable, a single initial retrieval may be enough.

Figure 10: BWT by memory organization. On BabyAI under the A`\to`B sequence, Cond-Ind yields `-`10% (forgetting), while Cond-Step achieves `+`3% (positive backward transfer).

|  |  | BWT(A`\to`B) | | BWT(B`\to`A) | |
| --- | --- | --- | --- | --- | --- |
| Env | Cond | BWT | `\Delta\mathrm{RR}` | BWT | `\Delta\mathrm{RR}` |
| ALF | Agg | `-`1.0 | 0.0 | `-`3.5 | `+`4.6 |
| Ind | `+`1.5 | `+`1.1 | `+`0.5 | `-`0.9 |
| Step | `-`0.5 | `-`0.5 | `-`5.0 | `-`4.6 |
| Baby | Agg | 0.0 | `+`2.2 | `+`3.0 | `+`8.2 |
| Ind | `-`10.0 | `-`6.4 | `+`4.0 | `+`7.1 |
| Step | `+`3.0 | `-`2.2 | `+`0.5 | `-`5.1 |

Table 6: Study 2 backward transfer result.

### 4.3 Stability-Plasticity Trade-off

While forward transfer suggests that fine-grained storage can be effective, backward transfer reveals an important caveat (Table [6](https://arxiv.org/html/2604.27003v1#S4.T6 "Table 6 ‣ Overall. ‣ 4.2 Retrieval Frequency (Ind vs. Step) ‣ 4 Study 2: Memory Organization ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents"), Figure [10](https://arxiv.org/html/2604.27003v1#S4.F10 "Figure 10 ‣ Overall. ‣ 4.2 Retrieval Frequency (Ind vs. Step) ‣ 4 Study 2: Memory Organization ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents")).

The clearest case appears in BabyAI under the A`\to`B sequence: Cond-Ind achieves the strongest forward transfer but also the most severe forgetting.
In the same run, the design that adapts best to the new task degrades most on the old one.
This pattern reflects a stability-plasticity trade-off, but the mechanism here is not parameter overwriting but memory dilution.

After Task B training, the memory pool becomes dominated by near-identical grid-search insights.
When re-evaluated on Task A, the agent’s queries often retrieve these homogeneous new entries instead of the original Task A memories.
Old memories are not erased but become harder to access as the pool grows (Appendix [F](https://arxiv.org/html/2604.27003v1#A6 "Appendix F Case Analyses ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents")).

Cond-Agg mitigates this issue by keeping the pool compact through aggregation.
Cond-Step may partially compensate via step-level retrieval, which can surface different items across execution steps even in a diluted pool.
On ALFWorld, BWT values are small across conditions, making this sequence less informative about stability differences.

Overall, these results suggest that external memory may not eliminate the stability-plasticity dilemma but shift its mechanism from parameter updates to retrieval dynamics.

### 4.4 Study 2 Summary

1. 1.

   Finer storage granularity is not always better.
   Indexing insights individually helps when source memories are diverse enough for the retriever to discriminate, but hurts when memories are homogeneous or tasks require coherent multi-step guidance.
2. 2.

   More frequent retrieval is not universally better either.
   Periodic re-querying helps when tasks contain distinct execution phases, but adds noise when execution is uniform throughout.
3. 3.

   Retrieval diversity collapse explains why finer granularity can fail.
   Fine-grained storage creates a seemingly rich pool, but homogeneous queries funnel most retrievals to the similar few items (Appendix [D](https://arxiv.org/html/2604.27003v1#A4 "Appendix D Retrieval Diversity Collapse ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents")).
4. 4.

   A stability-plasticity trade-off can emerge through memory dilution.
   The condition with the strong forward transfer also shows the significant forgetting, suggesting that the dilemma can emerge in non-parametric CL through retrieval dynamics rather than parameter overwriting.

## 5 Related Work

### 5.1 Agent Experience and Memory

A growing line of work equips LLM agents with external memory so they can improve through interaction without updating model weights. These systems mainly differ in what they treat as the reusable unit of *experience*: reflections or lessons ([Shinn et al., 2023](https://arxiv.org/html/2604.27003v1#bib.bib1); [Zhao et al., 2024](https://arxiv.org/html/2604.27003v1#bib.bib3)), executable skills or workflows ([Wang et al., 2023a](https://arxiv.org/html/2604.27003v1#bib.bib2); [Nottingham et al., 2024](https://arxiv.org/html/2604.27003v1#bib.bib27); [Wang et al., 2024b](https://arxiv.org/html/2604.27003v1#bib.bib28); [Zhang et al., 2026](https://arxiv.org/html/2604.27003v1#bib.bib35)), full trajectories or exemplars ([Zheng et al., 2023](https://arxiv.org/html/2604.27003v1#bib.bib26)), and persistent abstractions or memory structures ([Majumder et al., 2023](https://arxiv.org/html/2604.27003v1#bib.bib25); [Park et al., 2023](https://arxiv.org/html/2604.27003v1#bib.bib14); [Packer et al., 2023](https://arxiv.org/html/2604.27003v1#bib.bib13); [Zhong et al., 2024](https://arxiv.org/html/2604.27003v1#bib.bib4)). Recent work also studies cross-task reuse and memory-side failure modes ([Li et al., 2025](https://arxiv.org/html/2604.27003v1#bib.bib29); [Xiong et al., 2025](https://arxiv.org/html/2604.27003v1#bib.bib18)). We examine what these memory designs imply under task shift.

### 5.2 Continual Learning for LLMs and Agents

Classical continual learning studies how to balance stability and plasticity under non-stationary data through regularization, replay, and architectural isolation or expansion ([Kirkpatrick et al., 2017](https://arxiv.org/html/2604.27003v1#bib.bib7); [Li and Hoiem, 2017](https://arxiv.org/html/2604.27003v1#bib.bib30); [Lopez-Paz and Ranzato, 2017](https://arxiv.org/html/2604.27003v1#bib.bib8); [Mallya and Lazebnik, 2018](https://arxiv.org/html/2604.27003v1#bib.bib31)), with recent surveys extending this perspective to foundation models ([Wang et al., 2024a](https://arxiv.org/html/2604.27003v1#bib.bib9); [Wu et al., 2024](https://arxiv.org/html/2604.27003v1#bib.bib21)). For LLMs, continual or instruction tuning remains vulnerable to forgetting, motivating approaches such as non-parametric memory, parameter-efficient adaptation, expert composition, and architectural preservation ([Luo et al., 2025](https://arxiv.org/html/2604.27003v1#bib.bib16); [Gutiérrez et al., 2025](https://arxiv.org/html/2604.27003v1#bib.bib19); [Wang et al., 2025a](https://arxiv.org/html/2604.27003v1#bib.bib32); [Wang et al., 2025b](https://arxiv.org/html/2604.27003v1#bib.bib33); [Biswas et al., 2026](https://arxiv.org/html/2604.27003v1#bib.bib34)). Continual learning is also studied at the agent level, e.g., through disentangled parameter updates in Agent-Dice ([Wu et al., 2026](https://arxiv.org/html/2604.27003v1#bib.bib20)). We focus on the complementary frozen-backbone setting, where interference arises in retrieval rather than parameter updates.

## 6 Conclusion

External memory may appear to sidestep the stability-plasticity dilemma because old experience is preserved while new experience can always be appended.
Our results suggest a more cautious view: once behavior depends on retrieval through a finite context window, old and new memories compete for the same channel into the agent’s decisions, reintroducing transfer and interference through retrieval rather than through parameter updates.
Across both studies, abstraction shapes whether retrieved experience helps or misleads, memory granularity determines whether stored diversity becomes useful guidance or repetitive noise, and the resulting system remains subject to trade-offs that require careful design.

## Limitations

Our experiments prioritize controlled analysis over broad coverage. In practice, even a single task-pair study expands into many training and evaluation groups once baselines, single-task controls, both transfer directions, backward probes, repeated runs, and multiple memory conditions are included. For this reason, we focus on two environments with one representative task pair each, one sparse retrieval backbone, and two runs per condition. We do not claim this setup is exhaustive; rather, we view it as a resource-constrained but targeted testbed that isolates key design dimensions and makes the resulting transfer, forgetting, and retrieval effects easier to interpret. Broader task coverage, additional retrievers, and larger-scale repetition would strengthen the generality of the conclusions and are important directions for future improvements.

## References

- Biswas et al. (2026)
  S. D. Biswas, Y. Zhang, A. Pal, R. Bhargava, and K. Roy
  ELLA: efficient lifelong learning for adapters in large language models.
  arXiv preprint arXiv:2601.02232.
  Cited by: [§5.2](https://arxiv.org/html/2604.27003v1#S5.SS2.p1.1 "5.2 Continual Learning for LLMs and Agents ‣ 5 Related Work ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").
- Borgeaud et al. (2022)
  S. Borgeaud, A. Mensch, J. Hoffmann, T. Cai, E. Rutherford, K. Millican, G. B. Van Den Driessche, J. Lespiau, B. Damoc, A. Clark, et al.
  Improving language models by retrieving from trillions of tokens.
  In International conference on machine learning,
  pp. 2206–2240.
  Cited by: [§1](https://arxiv.org/html/2604.27003v1#S1.p1.1 "1 Introduction ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").
- Cao et al. (2025)
  Z. Cao, J. Deng, L. Yu, W. Zhou, Z. Liu, B. Ding, and H. Zhao
  Remember me, refine me: a dynamic procedural memory framework for experience-driven agent evolution.
  arXiv preprint arXiv:2512.10696.
  Cited by: [§A.1.3](https://arxiv.org/html/2604.27003v1#A1.SS1.SSS3.p1.1 "A.1.3 Memory System ‣ A.1 Terminology and Conditions ‣ Appendix A Experimental Details ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents"),
  [§2.1](https://arxiv.org/html/2604.27003v1#S2.SS1.p1.1 "2.1 Agent Memory as Continual Learning ‣ 2 Framework & Experimental Setup ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").
- Chevalier-Boisvert et al. (2018)
  M. Chevalier-Boisvert, D. Bahdanau, S. Lahlou, L. Willems, C. Saharia, T. H. Nguyen, and Y. Bengio
  Babyai: a platform to study the sample efficiency of grounded language learning.
  arXiv preprint arXiv:1810.08272.
  Cited by: [§1](https://arxiv.org/html/2604.27003v1#S1.p4.1 "1 Introduction ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents"),
  [§2.4](https://arxiv.org/html/2604.27003v1#S2.SS4.p1.1 "2.4 Environments, Task Pairs, and Protocol ‣ 2 Framework & Experimental Setup ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").
- Gutiérrez et al. (2025)
  B. J. Gutiérrez, Y. Shu, W. Qi, S. Zhou, and Y. Su
  From rag to memory: non-parametric continual learning for large language models.
  arXiv preprint arXiv:2502.14802.
  Cited by: [§1](https://arxiv.org/html/2604.27003v1#S1.p3.1 "1 Introduction ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents"),
  [§5.2](https://arxiv.org/html/2604.27003v1#S5.SS2.p1.1 "5.2 Continual Learning for LLMs and Agents ‣ 5 Related Work ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").
- Kirkpatrick et al. (2017)
  J. Kirkpatrick, R. Pascanu, N. Rabinowitz, J. Veness, G. Desjardins, A. A. Rusu, K. Milan, J. Quan, T. Ramalho, A. Grabska-Barwinska, et al.
  Overcoming catastrophic forgetting in neural networks.
  Proceedings of the national academy of sciences 114 (13), pp. 3521–3526.
  Cited by: [§1](https://arxiv.org/html/2604.27003v1#S1.p2.1 "1 Introduction ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents"),
  [§5.2](https://arxiv.org/html/2604.27003v1#S5.SS2.p1.1 "5.2 Continual Learning for LLMs and Agents ‣ 5 Related Work ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").
- Li et al. (2025)
  Y. Li, C. Qian, Y. Xia, R. Shi, Y. Dang, Z. Xie, Z. You, W. Chen, C. Yang, W. Liu, et al.
  Cross-task experiential learning on llm-based multi-agent collaboration.
  arXiv preprint arXiv:2505.23187.
  Cited by: [§5.1](https://arxiv.org/html/2604.27003v1#S5.SS1.p1.1 "5.1 Agent Experience and Memory ‣ 5 Related Work ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").
- Li and Hoiem (2017)
  Z. Li and D. Hoiem
  Learning without forgetting.
  IEEE transactions on pattern analysis and machine intelligence 40 (12), pp. 2935–2947.
  Cited by: [§5.2](https://arxiv.org/html/2604.27003v1#S5.SS2.p1.1 "5.2 Continual Learning for LLMs and Agents ‣ 5 Related Work ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").
- Lopez-Paz and Ranzato (2017)
  D. Lopez-Paz and M. Ranzato
  Gradient episodic memory for continual learning.
  Advances in neural information processing systems 30.
  Cited by: [§1](https://arxiv.org/html/2604.27003v1#S1.p2.1 "1 Introduction ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents"),
  [§5.2](https://arxiv.org/html/2604.27003v1#S5.SS2.p1.1 "5.2 Continual Learning for LLMs and Agents ‣ 5 Related Work ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").
- Luo et al. (2025)
  Y. Luo, Z. Yang, F. Meng, Y. Li, J. Zhou, and Y. Zhang
  An empirical study of catastrophic forgetting in large language models during continual fine-tuning.
  IEEE Transactions on Audio, Speech and Language Processing.
  Cited by: [§5.2](https://arxiv.org/html/2604.27003v1#S5.SS2.p1.1 "5.2 Continual Learning for LLMs and Agents ‣ 5 Related Work ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").
- Majumder et al. (2023)
  B. P. Majumder, B. Dalvi Mishra, P. Jansen, O. Tafjord, N. Tandon, L. Zhang, C. Callison-Burch, and P. Clark
  CLIN: a continually learning language agent for rapid task adaptation and generalization.
  arXiv preprint arXiv:2310.10134.
  Cited by: [§5.1](https://arxiv.org/html/2604.27003v1#S5.SS1.p1.1 "5.1 Agent Experience and Memory ‣ 5 Related Work ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").
- Mallya and Lazebnik (2018)
  A. Mallya and S. Lazebnik
  Packnet: adding multiple tasks to a single network by iterative pruning.
  In Proceedings of the IEEE conference on Computer Vision and Pattern Recognition,
  pp. 7765–7773.
  Cited by: [§5.2](https://arxiv.org/html/2604.27003v1#S5.SS2.p1.1 "5.2 Continual Learning for LLMs and Agents ‣ 5 Related Work ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").
- Nottingham et al. (2024)
  K. Nottingham, B. P. Majumder, B. D. Mishra, S. Singh, P. Clark, and R. Fox
  Skill set optimization: reinforcing language model behavior via transferable skills.
  arXiv preprint arXiv:2402.03244.
  Cited by: [§5.1](https://arxiv.org/html/2604.27003v1#S5.SS1.p1.1 "5.1 Agent Experience and Memory ‣ 5 Related Work ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").
- Packer et al. (2023)
  C. Packer, V. Fang, S. Patil, K. Lin, S. Wooders, and J. Gonzalez
  MemGPT: towards llms as operating systems..
  ArXiv.
  Cited by: [§1](https://arxiv.org/html/2604.27003v1#S1.p1.1 "1 Introduction ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents"),
  [§5.1](https://arxiv.org/html/2604.27003v1#S5.SS1.p1.1 "5.1 Agent Experience and Memory ‣ 5 Related Work ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").
- Park et al. (2023)
  J. S. Park, J. O’Brien, C. J. Cai, M. R. Morris, P. Liang, and M. S. Bernstein
  Generative agents: interactive simulacra of human behavior.
  In Proceedings of the 36th annual acm symposium on user interface software and technology,
  pp. 1–22.
  Cited by: [§5.1](https://arxiv.org/html/2604.27003v1#S5.SS1.p1.1 "5.1 Agent Experience and Memory ‣ 5 Related Work ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").
- Robertson and Zaragoza (2009)
  S. Robertson and H. Zaragoza
  The probabilistic relevance framework: bm25 and beyond.
  Vol. 4, Now Publishers Inc.
  Cited by: [§A.1.3](https://arxiv.org/html/2604.27003v1#A1.SS1.SSS3.p1.1 "A.1.3 Memory System ‣ A.1 Terminology and Conditions ‣ Appendix A Experimental Details ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").
- Shinn et al. (2023)
  N. Shinn, F. Cassano, A. Gopinath, K. Narasimhan, and S. Yao
  Reflexion: language agents with verbal reinforcement learning.
  Advances in neural information processing systems 36, pp. 8634–8652.
  Cited by: [§1](https://arxiv.org/html/2604.27003v1#S1.p1.1 "1 Introduction ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents"),
  [§5.1](https://arxiv.org/html/2604.27003v1#S5.SS1.p1.1 "5.1 Agent Experience and Memory ‣ 5 Related Work ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").
- Shridhar et al. (2020)
  M. Shridhar, X. Yuan, M. Côté, Y. Bisk, A. Trischler, and M. Hausknecht
  Alfworld: aligning text and embodied environments for interactive learning.
  arXiv preprint arXiv:2010.03768.
  Cited by: [§1](https://arxiv.org/html/2604.27003v1#S1.p4.1 "1 Introduction ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents"),
  [§2.4](https://arxiv.org/html/2604.27003v1#S2.SS4.p1.1 "2.4 Environments, Task Pairs, and Protocol ‣ 2 Framework & Experimental Setup ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").
- Wang et al. (2025a)
  C. Wang, Y. Lyu, Z. Sun, and L. Jing
  Continual gradient low-rank projection fine-tuning for llms.
  In Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers),
  pp. 14815–14829.
  Cited by: [§5.2](https://arxiv.org/html/2604.27003v1#S5.SS2.p1.1 "5.2 Continual Learning for LLMs and Agents ‣ 5 Related Work ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").
- Wang et al. (2023a)
  G. Wang, Y. Xie, Y. Jiang, A. Mandlekar, C. Xiao, Y. Zhu, L. Fan, and A. Anandkumar
  Voyager: an open-ended embodied agent with large language models.
  arXiv preprint arXiv:2305.16291.
  Cited by: [§1](https://arxiv.org/html/2604.27003v1#S1.p1.1 "1 Introduction ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents"),
  [§5.1](https://arxiv.org/html/2604.27003v1#S5.SS1.p1.1 "5.1 Agent Experience and Memory ‣ 5 Related Work ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").
- Wang et al. (2024a)
  L. Wang, X. Zhang, H. Su, and J. Zhu
  A comprehensive survey of continual learning: theory, method and application.
  IEEE transactions on pattern analysis and machine intelligence 46 (8), pp. 5362–5383.
  Cited by: [§1](https://arxiv.org/html/2604.27003v1#S1.p2.1 "1 Introduction ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents"),
  [§5.2](https://arxiv.org/html/2604.27003v1#S5.SS2.p1.1 "5.2 Continual Learning for LLMs and Agents ‣ 5 Related Work ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").
- Wang et al. (2023b)
  W. Wang, L. Dong, H. Cheng, X. Liu, X. Yan, J. Gao, and F. Wei
  Augmenting language models with long-term memory.
  Advances in Neural Information Processing Systems 36, pp. 74530–74543.
  Cited by: [§1](https://arxiv.org/html/2604.27003v1#S1.p1.1 "1 Introduction ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").
- Wang et al. (2025b)
  Z. Wang, Y. Li, X. Qu, and Y. Cheng
  SEE: continual fine-tuning with sequential ensemble of experts.
  In Findings of the Association for Computational Linguistics: ACL 2025,
  pp. 7418–7432.
  Cited by: [§5.2](https://arxiv.org/html/2604.27003v1#S5.SS2.p1.1 "5.2 Continual Learning for LLMs and Agents ‣ 5 Related Work ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").
- Wang et al. (2024b)
  Z. Z. Wang, J. Mao, D. Fried, and G. Neubig
  Agent workflow memory.
  arXiv preprint arXiv:2409.07429.
  Cited by: [§5.1](https://arxiv.org/html/2604.27003v1#S5.SS1.p1.1 "5.1 Agent Experience and Memory ‣ 5 Related Work ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").
- Wu et al. (2024)
  T. Wu, L. Luo, Y. Li, S. Pan, T. Vu, and G. Haffari
  Continual learning for large language models: a survey.
  arXiv preprint arXiv:2402.01364.
  Cited by: [§5.2](https://arxiv.org/html/2604.27003v1#S5.SS2.p1.1 "5.2 Continual Learning for LLMs and Agents ‣ 5 Related Work ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").
- Wu et al. (2026)
  Z. Wu, X. Lou, X. Ma, Y. Li, W. Liu, W. Zhang, J. Wang, and Z. Zhang
  Agent-dice: disentangling knowledge updates via geometric consensus for agent continual learning.
  arXiv preprint arXiv:2601.03641.
  Cited by: [§5.2](https://arxiv.org/html/2604.27003v1#S5.SS2.p1.1 "5.2 Continual Learning for LLMs and Agents ‣ 5 Related Work ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").
- Xi et al. (2024)
  Z. Xi, Y. Ding, W. Chen, B. Hong, H. Guo, J. Wang, D. Yang, C. Liao, X. Guo, W. He, S. Gao, L. Chen, R. Zheng, Y. Zou, T. Gui, Q. Zhang, X. Qiu, X. Huang, Z. Wu, and Y. Jiang
  AgentGym: evolving large language model-based agents across diverse environments.
  arXiv preprint arXiv:2406.04151.
  Cited by: [§A.1.3](https://arxiv.org/html/2604.27003v1#A1.SS1.SSS3.p1.1 "A.1.3 Memory System ‣ A.1 Terminology and Conditions ‣ Appendix A Experimental Details ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").
- Xiong et al. (2025)
  Z. Xiong, Y. Lin, W. Xie, P. He, Z. Liu, J. Tang, H. Lakkaraju, and Z. Xiang
  How memory management impacts llm agents: an empirical study of experience-following behavior.
  arXiv preprint arXiv:2505.16067.
  Cited by: [§5.1](https://arxiv.org/html/2604.27003v1#S5.SS1.p1.1 "5.1 Agent Experience and Memory ‣ 5 Related Work ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").
- Xu et al. (2025)
  W. Xu, Z. Liang, K. Mei, H. Gao, J. Tan, and Y. Zhang
  A-mem: agentic memory for llm agents.
  arXiv preprint arXiv:2502.12110.
  Cited by: [§1](https://arxiv.org/html/2604.27003v1#S1.p1.1 "1 Introduction ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").
- Yao et al. (2022)
  S. Yao, J. Zhao, D. Yu, N. Du, I. Shafran, K. R. Narasimhan, and Y. Cao
  React: synergizing reasoning and acting in language models.
  In The eleventh international conference on learning representations,
  Cited by: [§2.1](https://arxiv.org/html/2604.27003v1#S2.SS1.p1.1 "2.1 Agent Memory as Continual Learning ‣ 2 Framework & Experimental Setup ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").
- Zhang et al. (2026)
  H. Zhang, Q. Long, J. Bao, T. Feng, W. Zhang, H. Yue, and W. Wang
  MemSkill: learning and evolving memory skills for self-evolving agents.
  arXiv preprint arXiv:2602.02474.
  Cited by: [§5.1](https://arxiv.org/html/2604.27003v1#S5.SS1.p1.1 "5.1 Agent Experience and Memory ‣ 5 Related Work ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").
- Zhang et al. (2025)
  Z. Zhang, Q. Dai, X. Bo, C. Ma, R. Li, X. Chen, J. Zhu, Z. Dong, and J. Wen
  A survey on the memory mechanism of large language model-based agents.
  ACM Transactions on Information Systems 43 (6), pp. 1–47.
  Cited by: [§1](https://arxiv.org/html/2604.27003v1#S1.p3.1 "1 Introduction ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").
- Zhao et al. (2024)
  A. Zhao, D. Huang, Q. Xu, M. Lin, Y. Liu, and G. Huang
  Expel: llm agents are experiential learners.
  In Proceedings of the AAAI Conference on Artificial Intelligence,
  Vol. 38, pp. 19632–19642.
  Cited by: [§1](https://arxiv.org/html/2604.27003v1#S1.p1.1 "1 Introduction ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents"),
  [§5.1](https://arxiv.org/html/2604.27003v1#S5.SS1.p1.1 "5.1 Agent Experience and Memory ‣ 5 Related Work ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").
- Zheng et al. (2023)
  L. Zheng, R. Wang, X. Wang, and B. An
  Synapse: trajectory-as-exemplar prompting with memory for computer control.
  arXiv preprint arXiv:2306.07863.
  Cited by: [§5.1](https://arxiv.org/html/2604.27003v1#S5.SS1.p1.1 "5.1 Agent Experience and Memory ‣ 5 Related Work ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").
- Zhong et al. (2024)
  W. Zhong, L. Guo, Q. Gao, H. Ye, and Y. Wang
  Memorybank: enhancing large language models with long-term memory.
  In Proceedings of the AAAI conference on artificial intelligence,
  Vol. 38, pp. 19724–19731.
  Cited by: [§1](https://arxiv.org/html/2604.27003v1#S1.p1.1 "1 Introduction ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents"),
  [§5.1](https://arxiv.org/html/2604.27003v1#S5.SS1.p1.1 "5.1 Agent Experience and Memory ‣ 5 Related Work ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").

## Appendix A Experimental Details

### A.1 Terminology and Conditions

| Term | Meaning in this paper |
| --- | --- |
| Raw | Full action–observation trajectory from one episode. |
| Insight | LLM-distilled strategy insights derived from a trajectory. |
| Cond-Agg | Task-level aggregation of insights, retrieved once per episode. |
| Cond-Ind | Insight-level storage, with each insight indexed separately and retrieved once per episode. |
| Cond-Step | Same insight-level storage as Cond-Ind, but with step-level retrieval; in our implementation, the agent re-queries periodically during execution. |

Table 7: Representation and condition glossary.

### A.1.1 Run Types and Labels

No-memory baseline disables external memory entirely.
Scratch run means a memory-enabled agent trained on a single task family from empty memory.
Cross-task run means a memory-enabled agent trained on one task family and then continued on another while reusing the accumulated pool.
Eval-only probe denotes post-training evaluation on the earlier task for backward transfer.
Throughout the paper, FWT(`X\to Y`) refers to forward transfer on the later task `Y`, while BWT(`X\to Y`) refers to backward transfer measured by re-evaluating the earlier task `X` after the full `X\to Y` sequence.

### A.1.2 Metrics and Diagnostics

FWT(`X\to Y`) is defined as `\text{Acc}_{Y}(\varnothing\!\to\!X\!\to\!Y)-\text{Acc}_{Y}(\varnothing\!\to\!Y)` and measures whether prior experience from `X` helps or hurts learning on the later task `Y`.
BWT(`X\to Y`) is defined as `\text{Acc}_{X}(\varnothing\!\to\!X\!\to\!Y)-\text{Acc}_{X}(\varnothing\!\to\!X)` and measures whether the later phase changes performance on the earlier task `X`.
RR (Retention Rate) is the success rate on the baseline-success subset after memory is introduced, and NL (New Learning rate) is the success rate on the baseline-fail subset after memory is introduced.
For a cross-task run `X\to T`, we report `\Delta\mathrm{RR}=\text{RR}(\varnothing\!\to\!X\!\to\!T)-\text{RR}(\varnothing\!\to\!T)` and `\Delta\mathrm{NL}=\text{NL}(\varnothing\!\to\!X\!\to\!T)-\text{NL}(\varnothing\!\to\!T)`.

### A.1.3 Memory System

We build on AgentGym ([Xi et al., 2024](https://arxiv.org/html/2604.27003v1#bib.bib12)) with the ReMe memory module ([Cao et al., 2025](https://arxiv.org/html/2604.27003v1#bib.bib22)).
Retrieval uses BM25 ([Robertson and Zaragoza, 2009](https://arxiv.org/html/2604.27003v1#bib.bib11)) throughout.

### A.1.4 Study 1 Conditions

Both representations use instance-level storage with a single retrieved memory per query (top-1).
Raw stores the complete action–observation trajectory from each episode.
Insight prompts the LLM to distill the trajectory into abstract strategy insights (`{\sim}`3 per instance), which are aggregated into a single task-level memory unit keyed by the original task instruction.

### A.1.5 Study 2 Conditions

All three conditions use the Insight representation.
Cond-Agg stores one task-level bundle per instance (key = task instruction) and retrieves the top-1 match at the start of each episode (`{\sim}`3 insights per retrieval).
Cond-Ind stores each insight as a separate memory unit (key = a when_to_use descriptor generated alongside the insight) and retrieves the top-3 matches at the start of each episode.
Cond-Step uses the same insight-level storage as Cond-Ind but re-queries every 4 execution steps, allowing dynamically updated guidance.
All three conditions thus surface approximately 3 insights per retrieval event, holding the information budget roughly constant.

### A.1.6 Training and Evaluation

All conditions use Qwen-Plus as the backbone LLM.
Each task phase contains 200 training instances and 100 test instances.
Results are averaged over two independent runs.

### A.2 Hyperparameters

Table [8](https://arxiv.org/html/2604.27003v1#A1.T8 "Table 8 ‣ A.2 Hyperparameters ‣ Appendix A Experimental Details ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents") summarizes the main hyperparameters used in the experiments.

| Scope | Hyperparameter | Value | Notes |
| --- | --- | --- | --- |
| Shared | Backbone LLM | Qwen-Plus | Used for both training and evaluation across all reported conditions. |
| Shared | Training instances per task phase | 200 | Matches train_size in the experiment runner. |
| Shared | Test instances per task phase | 100 | Fixed task split used in both environments. |
| Shared | Number of runs | 2 | Final results are averaged over two independent runs. |
| Shared | Random seed | 42 | Set in the launch scripts. |
| Shared | Evaluation workers | 4 | EVAL_PROCESSES=4 in the chapter scripts. |
| Shared | Milestones | 1 | One end-of-phase evaluation checkpoint per task phase. |
| Shared | Max generation tokens | 4096 | Overrides the lower parser default in the launcher configuration. |
| Shared | Temperature | 0.5 | Shared sampling setting in the chapter scripts. |
| Study 1 | Memory representation | Raw / Insight | Corresponds to trajectory memory vs. distilled insight memory. |
| Study 1 | Retrieval top-`k` | 1 | Single retrieved memory per query. |
| Study 1 | Success-only filtering | false | Both successful and unsuccessful episodes may enter memory. |
| Study 2 | Conditions | Cond-Agg / Cond-Ind / Cond-Step | All three use the Insight representation but differ in organization and retrieval timing. |
| Study 2 | Retrieval top-`k` | 1 / 3 / 3 | Cond-Agg retrieves one aggregated bundle; Cond-Ind and Cond-Step retrieve top-3 insight entries. |
| Study 2 | Step retrieval interval | 4 steps | Cond-Step re-queries memory every 4 environment steps. |
| Study 2 | Success-only filtering | false | Same memory inclusion rule as in Study 1. |

Table 8: Main hyperparameters used in our experiments.

## Appendix B Memory Content Examples

We show representative entries for each memory type studied in this paper.
All examples are drawn from actual experimental runs and lightly abbreviated for space.

### B.1 Study 1: Raw vs. Insight

Raw entry (ALFWorld, “put some bowl on fridge”).
  
*Key*: the full task instruction plus initial environment observation.
  
*Content*: the complete action–observation trajectory from the episode, including all agent reasoning steps and environment responses.
For example:

> [User]: Your task is: put some bowl on fridge.
>   
> [Agent]: I need to find a bowl first. Let me check the countertop…
>   
> Action: go to countertop 1
>   
> [User]: On the countertop 1, you see a bowl 2…
>   
> …(*full episode, typically 20–50 turns*)

Insight entry (ALFWorld, same task).
  
*Key*: same task instruction as Raw.
  
*Content*: `\sim`3 abstract insights distilled by the LLM.
For example:

> Insight 1. Check countertops and tables first, as they are the most common locations for portable objects like bowls and cups.
>   
> Insight 2. If the target object is not visible, systematically visit receptacles in order of likelihood rather than searching randomly.
>   
> Insight 3. Once the object is picked up, navigate directly to the target receptacle to avoid unnecessary steps.

### B.2 Study 2: Cond-Agg vs. Cond-Ind

Cond-Agg entry (BabyAI, Task A “open the purple door”).
  
*Key*: task instruction plus initial observation.
  
*Content*: all `\sim`3 insights bundled together, covering different aspects of the episode (e.g., door traversal strategy, backtracking from dead ends, color-based heuristics).
The entire bundle is retrieved as a single unit.

Cond-Ind entries (BabyAI, Task A, same source episode).
  
Each insight is stored separately with its own retrieval key:

> Entry 1.
>   
> *Key*: “When the target object is absent from all observations after multiple reorientations, and multiple closed doors are present”
>   
> *Content*: “Prioritize attempting all available closed-door traversals from the initial room before committing to any one path…”
>
> Entry 2.
>   
> *Key*: “After entering an empty room with no objects or doors visible”
>   
> *Content*: “An empty room with zero object observations is a strong signal of a dead-end branch; backtracking should be initiated immediately…”

The retriever can now match an incoming query to the single most relevant entry rather than returning the entire bundle.

Figure 11: Retrieval diversity analysis (BabyAI, within-task setting). (a) Key diversity in storage (left marker of each pair) vs. effective context diversity at retrieval (right marker). For Task B under Cond-Ind, storage diversity is high (`>`0.91) but context diversity drops to 0.38. (b) Retrieval coverage: fraction of unique items among all retrievals. Cond-Ind `\times` Task B retrieves only 13 unique items out of 240 (5.4%). (c) Top-1 concentration: 88.5% of Task B queries under Cond-Ind retrieve the identical item. (d) Within-task performance impact.

## Appendix C Retrieval Frequency: Additional Analysis

Pool content differs between conditions. 
Although Cond-Ind and Cond-Step both use insight-level storage, their memory pools are not identical.
During training, the agent retrieves memory before (and, for Step, during) each episode.
Different retrieval affects the agent’s behavior, which affects task outcomes, which in turn affects what insights are generated and stored.
Thus the Ind–Step comparison conflates two effects: retrieval frequency at evaluation time and pool composition from training time.

Within-task performance. 
Cond-Step achieves the highest within-task (scratch) success rates on ALFWorld: 99.0% on Task A and 79.5% on Task B, compared to 96.5%/55.0% for Cond-Ind and 97.0%/65.5% for Cond-Agg.
The advantage is especially large on Task B (`+`24.5pp over Cond-Ind), indicating that step-level retrieval is highly effective for multi-step manipulation tasks when source and target share the same task distribution.
On BabyAI, Step is middle-ground (70.0% on A, 48.0% on B), falling between Ind and Agg.

Scratch baselines affect FWT interpretation. 
Because FWT is defined relative to each condition’s own scratch performance, different baselines can affect the comparison.
For example, on BabyAI B`\to`A: Cond-Ind’s scratch is 75.5% and cross-task is 74.5% (FWT `=-1.0`); Cond-Step’s scratch is 70.0% and cross-task is 77.5% (FWT `=+7.5`).
Step achieves higher *absolute* cross-task performance (77.5 vs. 74.5), and the FWT gap is amplified by Step’s lower scratch baseline.
This does not invalidate the comparison (FWT measures each design’s relative gain from cross-task memory), but readers should note that the absolute performance levels are closer than the FWT values suggest.

## Appendix D Retrieval Diversity Collapse

When Cond-Ind is applied to homogeneous source memories (e.g., BabyAI Task B), individually indexing each insight creates a large pool of near-identical entries.
We call the resulting phenomenon *retrieval diversity collapse*: the pool *appears* diverse from the storage side, but the actual retrieved content is highly repetitive because homogeneous queries cannot discriminate among similar keys.

To quantify this, we measure how diversity changes from storage to retrieval using TF-IDF similarity analysis (Figure [11](https://arxiv.org/html/2604.27003v1#A2.F11 "Figure 11 ‣ B.2 Study 2: Cond-Agg vs. Cond-Ind ‣ Appendix B Memory Content Examples ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents")).
We compare two levels: *key diversity* (how varied the retrieval keys are in the pool) and *context diversity* (how varied the items actually retrieved across all test queries are).

Under Cond-Agg, key diversity and context diversity are similar (the pool has one entry per task instance, and different queries tend to retrieve different entries).
Under Cond-Ind, the pool contains many individually indexed insights, producing high key diversity (`>`0.91 for both tasks).
However, whether this high key diversity translates into diverse *retrieved* content depends on the queries.

Task A (heterogeneous queries). 
Task A encompasses three sub-task types, so different test queries activate different subsets of the pool.
Context diversity under Cond-Ind (0.45) exceeds that under Cond-Agg (0.29): individual indexing is helpful here because the retriever can select the most relevant entry per query.

Task B (homogeneous queries). 
Task B uniformly instructs “find [object],” so all test queries are lexically similar.
Despite the pool containing many entries, these similar queries all produce nearly identical retrieval scores, funneling 88.5% of queries to the same top-1 item (panel c).
Context diversity under Cond-Ind (0.38) is actually *lower* than under Cond-Agg (0.41), and retrieval coverage drops to 5.4% (panel b).
The result is a `-`17pp within-task performance loss (panel d).

The collapse is invisible from the storage side (key diversity remains high) and manifests only at retrieval time.
This is why pool-side metrics alone (e.g., number of stored entries, key diversity) are insufficient to predict retrieval effectiveness.

## Appendix E Learning Dynamics

Figure [12](https://arxiv.org/html/2604.27003v1#A5.F12 "Figure 12 ‣ Appendix E Learning Dynamics ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents") visualizes cumulative success during ALFWorld training for the main Study 1 conditions.
The most important pattern is that the Raw A`\to`B curve drops below the scratch Task B curve soon after the phase switch and never recovers, indicating that the negative forward-transfer effect is not a brief adaptation cost but a persistent deficit throughout Task B learning.
By contrast, the Insight A`\to`B curve tracks much closer to, and in some regions above, the scratch baseline, consistent with the interpretation that abstraction makes cross-task reuse safer over the full learning trajectory rather than only at final evaluation.

Figure 12: ALFWorld cumulative success rate (training set). Raw A`\to`B (solid red) causes a persistent plasticity deficit that never recovers.

Figure 13: ALFWorld Task B: RR/NL dynamics over training. RR remains stable; the NL gap is the primary driver of negative FWT and persists throughout.

## Appendix F Case Analyses

### F.1 Study 1: Retrieval Pollution from Raw Trajectories

In Study 1, we find that raw trajectories can hurt cross-task reuse because they provide detailed but procedurally wrong guidance, whereas abstract insights are less likely to displace the agent’s own reasoning.
The two ALFWorld cases below make that mechanism concrete.

Case 1. Missing cleaning step (ALFWorld)

Task. “put a clean bowl in fridge.”
Scratch / Insight behavior.
Both the scratch agent and the insight-based cross-task agent clean the bowl first, then move it to the fridge, and succeed.
Raw cross-task retrieval.
The retrieved memory is a Task A bowl trajectory whose successful procedure does not require cleaning.
Observed reasoning.
After locating the bowl, the Raw agent states: *“Since bowl 1 was on the diningtable (a clean surface), it’s reasonable to assume it’s clean.”*
It then moves the bowl directly to the fridge without washing it and fails.
Why it matters.
The retrieved trajectory is locally plausible because it concerns the same object and a very similar placement task, but it omits the one step that distinguishes Task B from Task A.
This is exactly the failure mode described in Study 1: raw procedural detail displaces task-specific reasoning under task shift.

Case 2. Procedural mimicry (ALFWorld)

Task. “clean some cloth and put it in bathtubbasin.”
Raw cross-task behavior.
The Raw agent finds a handtowel, goes to a sinkbasin, searches for soap, places the towel in the sink, and picks it back up, but never issues the correct clean handtowel with sinkbasin command.
Insight cross-task retrieval.
The retrieved guidance is functional rather than procedural: *“only after arriving at the cleaning station did the ‘clean [object] with [station]’ action succeed.”*
Outcome.
The Insight agent issues clean cloth with sinkbasin directly and succeeds.
Why it matters.
This case shows a stronger version of the same phenomenon.
Raw memory does not merely omit a required step; it encourages a longer but functionally wrong action pattern.
Insight memory, by contrast, preserves the condition under which the right action becomes available.

Together, these cases support the main Study 1 interpretation: raw trajectories inject task-specific procedures that can *displace* the agent’s own reasoning, while abstract insights preserve functional guidance without prescribing a full action script.

### F.2 Study 1: Why the B`\to`A Gap Is Small

The main text emphasizes the A`\to`B direction because that is where Raw and Insight diverge most sharply.
In the reverse B`\to`A sequence, the gap becomes much smaller.
On BabyAI, both representations yield similar positive forward transfer; on ALFWorld, both are close to zero, in part because Task A already has a high baseline.

One plausible interpretation is that experience from the relatively harder task is less likely to be actively misleading when reused for the relatively easier one.
In ALFWorld, for example, a “clean-then-place” trajectory can still solve the simpler “place” task, even if one step is unnecessary.
In BabyAI, Task B’s search-heavy experience can still provide useful navigation guidance for Task A, even when it does not cover all of Task A’s interaction-specific steps.
Thus the reverse direction appears to involve less harmful procedural mismatch, leaving less for abstraction to correct.

### F.3 Study 2: Granularity and Retrieval-Side Failure Modes

We conclude three findings from Study 2: fine-grained storage helps when the stored units are genuinely distinguishable, step-level retrieval can sometimes help by aligning guidance with the agent’s current execution phase, and backward-transfer failures can arise through memory dilution.
The following cases are designed to illustrate each of these points.

Case 3. Fine-grained storage helps when source memories are genuinely diverse

Setting.
This case supports ‘4.1 Memory-Unit Granularity (Agg vs. Ind)‘ on BabyAI Task A, where Cond-Ind performs well.
Representative stored entries.
In ‘Task A / Cond-Ind‘, the individually indexed insights are qualitatively different.
For example, one key concerns door-adjacent navigation (*“When navigating to a door using ‘go to <door>’ …”*), another emphasizes preserving the initial spatial anchor (*“Always treat the initial observation as the authoritative spatial anchor …”*), and another concerns systematic search after repeated failure (*“Persistent absence of a required item … suggests it is in an unobserved direction …”*).
Representative queries.
Queries such as *“open the purple door”* and *“go to the red door”* retrieve different top-ranked keys, even though both come from the same task family.
Why it matters.
This is the qualitative pattern behind Cond-Ind’s benefit on BabyAI A`\to`B.
Splitting memory into individual entries is useful here because the resulting entries are not merely numerous; they differ in content, and the retriever can select among them.

Case 4. Fine-grained storage fails when many entries say roughly the same thing

Setting.
This case supports ‘4.1‘ and complements the retrieval-diversity analysis in Appendix [D](https://arxiv.org/html/2604.27003v1#A4 "Appendix D Retrieval Diversity Collapse ‣ When Continual Learning Moves to Memory:A Study of Experience Reuse in LLM Agents").
Representative stored entries.
In ‘Task B / Cond-Ind‘, many high-scoring keys are variants of the same broad strategy: door traversal, room scanning, and continued search when the target object is absent.
Examples include keys beginning with *“When the initial observation shows only a closed door directly in front …”* and *“When ‘go to <obj>’ … loops produce identical empty rooms …”*.
Representative queries.
Different queries such as *“pick up the ball”* and *“pick up the box”* repeatedly retrieve the same top-ranked key.
In the full retrieval log, the most common top-1 entry is returned for 82 of 200 queries.
Why it matters.
This is the intuitive core of retrieval diversity collapse.
The pool looks large because it contains many individual entries, but many of those entries encode only slight variants of the same search strategy.
In this situation, splitting memory creates redundancy rather than useful granularity.

Case 5. Step-level retrieval can align guidance with the current phase

Caveat.
This case should be read as an illustration of how step-level retrieval can help in practice, not as a perfectly controlled comparison, because Cond-Step and Cond-Ind do not accumulate identical memory pools during training.
Representative Step case.
In one ALFWorld Step run from our main setup, the task is *“clean some egg and put it in sidetable.”*
The retrieved guidance emphasizes the cleaning phase specifically: after acquiring a cleanable object, the agent should first navigate to a sinkbasin because cleaning actions are only available when the agent is co-located with the cleaning fixture.
Observed behavior.
The agent follows this phase-appropriate guidance: it goes to the sinkbasin, executes clean egg 1 with sinkbasin 1, then moves to the sidetable and places the cleaned egg there.
Why it matters.
This case illustrates the kind of guidance a step-style condition can exploit.
The value of more frequent retrieval is not that it is always better, but that it can align guidance with the agent’s current execution phase when the task’s information needs change over time.

Case 6. Memory dilution after homogeneous Task B training

Setting.
This case supports ‘4.3 Backward Transfer and the Stability-Plasticity Trade-off‘.
Representative pool composition.
After Task B training under ‘Cond-Ind‘, the pool is filled with entries that all encode closely related search behavior, for example:

•

*“When the goal object is absent from all initial observations across multiple rooms … pivot from blind door progression to systematic orientation-based scanning …”*
•

*“Persistent linear door traversal without environmental anchoring leads to unbounded exploration loops …”*
Why it matters.
These entries are not wrong for Task B.
The problem is that, after enough such entries accumulate, they dominate the pool.
Under backward evaluation on Task A, this makes it harder for more diverse Task A memories to be retrieved.
The resulting failure is therefore not deletion of old memories, but reduced access to them through a pool dominated by repetitive new guidance.
