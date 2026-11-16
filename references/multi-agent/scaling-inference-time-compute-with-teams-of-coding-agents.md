---
title: "Scaling Inference-Time Compute with Teams of Coding Agents"
url: https://arxiv.org/abs/2610.17471
published: 2026-10-12
fetched: 2026-11-11
type: paper
topics: [multi-agent]
summary: "将多 agent 规划、实现、验证与模型分配视为奖励-成本帕累托优化；在 ProgramBench 研究配置中，规划阶段委派更划算。"
---

# Scaling Inference-Time Compute with Teams of Coding Agents

name=Keenan Samway\fa
  
affiliation=Cohere Labs
  
name=Daniel D’souza\fa
  
affiliation=Cohere Labs
  
name=Omar Darwiche Domingues
  
affiliation=Cohere
  
name=Marzieh Fadaee
  
affiliation=Cohere Labs
  
name=Tan Yi-Chern`\boldsymbol{\dagger}`
  
affiliation=Cohere
  
name=Nouha Dziri
  
affiliation=Cohere Labs

## Abstract

Multi-agent systems promise a new axis for scaling inference: rather than having one agent think longer or sample more attempts, a task is split across many agents that work in parallel and coordinate. However, in practice, more agents can easily produce duplicate work, coordination failures, and higher costs. We therefore formulate team design as a compute allocation problem: starting from a solo agent, where should additional inference compute go to reach the reward-cost Pareto frontier? We build a minimal multi-agent harness from the ground up and trace this frontier by varying, one at a time, the workflow stage at which a lead delegates to its workers (planning, implementation, or verification), the models that form the team, and the number of workers. On long-horizon challenging software-engineering tasks (e.g., ProgramBench), teams outperform solo agents but cost three to seven times as much. With the right compute allocation, however, a heterogeneous 17-agent team comes within 1.4 points of a strong homogeneous 5-agent team at 70% lower cost. This efficiency stems from three findings. First, planning is the most valuable use of workers: in a homogeneous team whose lead decides how many workers to spawn, a lead that delegates only planning to its workers, and then implements and verifies the code itself, matches the reward of a lead that delegates to workers throughout planning, implementation, and verification, at half the cost. Second, cheap models pay off as planners but not as implementers: a strong lead with cheap planners recovers 47.5% of the reward gain of an all-strong team for only 13.9% of its additional cost, whereas cheap implementers lower reward. Third, planners keep improving reward as the team grows, whereas implementers and verifiers plateau beyond four workers: additional implementers fragment the code into more files for the lead to integrate, and additional verifiers add little new information about the program. Together, our results offer a guide to spending an agent budget where it counts, given the task, cost, and latency constraints a user has.

\corresponding

[*]{danieldsouza, nouha.dziri}@cohere.com
††footnotetext: `\boldsymbol{\dagger}`Work done while at Cohere.

## 1 Introduction

Coding agents can now solve long-horizon software-engineering tasks that require navigating large repositories, editing code, invoking tools, and iteratively debugging their own solutions ([Jimenez et al., 2024](https://arxiv.org/html/2610.17471#bib.bib11); [Yang et al., 2024](https://arxiv.org/html/2610.17471#bib.bib12); [DeepSeek-AI et al., 2026](https://arxiv.org/html/2610.17471#bib.bib1); [Z.ai, 2026](https://arxiv.org/html/2610.17471#bib.bib2); [Team et al., 2026](https://arxiv.org/html/2610.17471#bib.bib3); [OpenAI, 2026](https://arxiv.org/html/2610.17471#bib.bib4); [Anthropic, 2026](https://arxiv.org/html/2610.17471#bib.bib5)). The dominant way to make such an agent stronger at inference time is to scale its compute sequentially, by letting it reason or revise for longer ([OpenAI et al., 2026](https://arxiv.org/html/2610.17471#bib.bib8); [Guo et al., 2025](https://arxiv.org/html/2610.17471#bib.bib9); [Muennighoff et al., 2025](https://arxiv.org/html/2610.17471#bib.bib10)), or in parallel, by sampling independent attempts and aggregating them ([Wang et al., 2023](https://arxiv.org/html/2610.17471#bib.bib31); [Brown et al., 2024](https://arxiv.org/html/2610.17471#bib.bib32); [Snell et al., 2024](https://arxiv.org/html/2610.17471#bib.bib7)). Both are bounded by a single agent’s trajectory. Longer traces increase latency and eventually exhaust the context window, and independent attempts repeat the work rather than dividing it. A team of agents offers a third axis: it divides a single attempt among agents that work on different parts of the task, whose work must then be consolidated into one solution. Team members can explore competing hypotheses, inspect different parts of a repository, implement separable changes, and independently verify a candidate solution. This provides a new test-time scaling strategy for when a single agent’s context window or time budget becomes limiting.

Adding agents, however, does not automatically add useful work. More agents bring more compute, which can raise solution correctness, but in practice these gains can be lost to duplicated work, conflicting edits, and the cost of consolidating what each agent produces ([Geng and Neubig, 2026](https://arxiv.org/html/2610.17471#bib.bib14); [Yang et al., 2026b](https://arxiv.org/html/2610.17471#bib.bib15)). Whether a team helps therefore depends less on how many agents it has than on how it spends its compute.
We make this question precise by treating team design as a compute allocation problem (Section [2](https://arxiv.org/html/2610.17471#S2 "2 Team Design as Budget-Constrained Optimization ‣ Scaling Inference-Time Compute with Teams of Coding Agents")). Starting from a solo agent, the next dollar of inference can go to a stronger lead, to stronger or cheaper workers, to more workers, or to a particular stage of the software-engineering workflow ([Royce, 1987](https://arxiv.org/html/2610.17471#bib.bib35)): planning (P), implementation (I), or verification (V). Each choice moves the team to a different point in reward and cost. We ask which choices reach the reward-cost Pareto frontier, and which buy the most reward per added dollar.

To answer this, we build a minimal, configurable harness with a hierarchical lead-worker topology (Figure [1](https://arxiv.org/html/2610.17471#S2.F1 "Figure 1 ‣ 2 Team Design as Budget-Constrained Optimization ‣ Scaling Inference-Time Compute with Teams of Coding Agents")): a lead agent decomposes the task, delegates subtasks to workers, and consolidates their results. Because every part of the harness is exposed, we can vary one design choice at a time: the stage at which the lead delegates (P, I, V, or all three, PIV), the lead and worker models, the number of workers, whether the lead waits for its workers or keeps working while they run, and whether workers can message each other. We focus on ProgramBench ([Yang et al., 2026a](https://arxiv.org/html/2610.17471#bib.bib13)), a long-horizon repository-reconstruction benchmark in which agents receive only a black-box executable and its documentation, and must discover its behavior, plan, implement, and verify a complete program that reproduces it. We complement it with Commit0 ([Zhao et al., 2024](https://arxiv.org/html/2610.17471#bib.bib33)), which also asks agents to build a repository from scratch but provides its skeleton, including the file layout and function stubs, together with its unit tests. We evaluate frontier models from the GPT and Claude Opus families.

Our results show that teams outperform solo agents, but at a steep price: a team composed of all strong agents raises reward over a single agent working alone, yet costs 3 to 7 times as much in inference dollars and, in most configurations, takes longer to finish (Section [4](https://arxiv.org/html/2610.17471#S4 "4 Does a team of agents outperform a solo agent? ‣ Scaling Inference-Time Compute with Teams of Coding Agents")). We find, however, that with the right allocation of compute, a heterogeneous 17-agent team can come within 1.4 points of a strong homogeneous 5-agent team at 70% lower cost
(Section [7](https://arxiv.org/html/2610.17471#S7 "7 How Many Workers Should a Team Have? ‣ Scaling Inference-Time Compute with Teams of Coding Agents")). This configuration rests on where the compute goes. On ProgramBench, planning emerges as the most valuable use of workers: when the lead delegates planning to a team of workers and then writes and verifies the code itself, the team matches the reward of a lead that delegates all three stages (planning, implementation, and verification) to its workers, at half its cost, and each dollar spent on planning buys up to twice the reward of a dollar spent on any other stage (Section [5](https://arxiv.org/html/2610.17471#S5 "5 Where should workers be utilized? ‣ Scaling Inference-Time Compute with Teams of Coding Agents")). Adding more workers to implementation or verification, in contrast, quickly plateaus. Planning wins here because it is the bottleneck of this task; on Commit0, where the repository already dictates the plan, implementation benefits most instead (Appendix [C.13](https://arxiv.org/html/2610.17471#A3.SS13 "C.13 Commit0 ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents")). Because planning workers only gather information for the lead to act on, they can be cheap: a strong lead with cheap planners recovers 47.5% of the reward gain of an all-strong team for only 13.9% of its additional cost (Section [6](https://arxiv.org/html/2610.17471#S6 "6 Can Heterogeneous Teams Scale More Efficiently? ‣ Scaling Inference-Time Compute with Teams of Coding Agents")).

## 2 Team Design as Budget-Constrained Optimization

A single agent spends its inference budget along one trajectory. A team, by contrast, distributes it across several design dimensions: the capability of the lead, the capability and number of workers, and the workflow stage at which workers are deployed. These dimensions are not independent, since the value of cheaper workers depends on the lead that directs them, and the value of additional workers depends on the stage to which they are assigned. We therefore formulate team design as a budget allocation problem.

![Refer to caption](https://arxiv.org/html/2610.17471v1/harness_overview.png)

Figure 1: Overview of our multi-agent harness. A lead agent delegates subtasks to workers operating in a shared sandbox. We vary team composition (a), whether the lead blocks or keeps working while workers run (b), and which stages of the task the lead is prompted to delegate (c).

### Formulation

We consider hierarchical teams in which a lead agent decomposes the task, delegates subtasks to workers, and consolidates their results (Section [3](https://arxiv.org/html/2610.17471#S3 "3 Experimental Setup ‣ Scaling Inference-Time Compute with Teams of Coding Agents")). A team configuration `c=(s,w,n,\ell)` is specified by the stage `s\in\{\text{P},\text{I},\text{V},\text{PIV}\}` toward which the lead is instructed to direct its workers, the worker model `w`, the number of workers `n`, and the lead model `\ell`. On a task distribution `\mathcal{T}`, each configuration attains a mean reward `R(c;\mathcal{T})` at a total inference cost `C(c;\mathcal{T})`.11
1
We treat wall-clock latency as a secondary objective rather than a constraint in Eq. [1](https://arxiv.org/html/2610.17471#S2.E1 "Equation 1 ‣ Formulation ‣ 2 Team Design as Budget-Constrained Optimization ‣ Scaling Inference-Time Compute with Teams of Coding Agents"). It is governed mainly by the scheduling policy (blocking or asynchronous), and we report it alongside reward and cost in Section [4](https://arxiv.org/html/2610.17471#S4 "4 Does a team of agents outperform a solo agent? ‣ Scaling Inference-Time Compute with Teams of Coding Agents"). Ideally, designing a team under a budget `B` would amount to solving

|  |  |  |  |
| --- | --- | --- | --- |
|  | `R^{*}(B;\mathcal{T})\;=\;\max_{c}\;R(c;\mathcal{T})\quad\text{subject to}\quad C(c;\mathcal{T})\leq B,` |  | (1) |

whose solution, traced across budgets, defines the Pareto frontier of performance and cost. The optimal configuration is task-dependent: extra workers pay off most at the stage that bottlenecks the task (Section [5](https://arxiv.org/html/2610.17471#S5 "5 Where should workers be utilized? ‣ Scaling Inference-Time Compute with Teams of Coding Agents"), Appendix [C.13](https://arxiv.org/html/2610.17471#A3.SS13 "C.13 Commit0 ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents")).

### Efficiency

Solving Eq. [1](https://arxiv.org/html/2610.17471#S2.E1 "Equation 1 ‣ Formulation ‣ 2 Team Design as Budget-Constrained Optimization ‣ Scaling Inference-Time Compute with Teams of Coding Agents") exactly is infeasible, as each configuration requires a full benchmark evaluation, and the stage instruction `s` steers where the lead delegates rather than fixing how much it spends. We therefore do not match budgets across configurations. Instead, we ask a marginal question: *starting from a solo agent, where does the next dollar of inference buy the most reward?* We define the *efficiency* of a configuration `c` as the reward it gains per dollar of added inference cost relative to the solo agent:

|  |  |  |  |
| --- | --- | --- | --- |
|  | `\eta_{c}=\frac{R_{c}-R_{\text{solo}}}{C_{c}-C_{\text{solo}}},` |  | (2) |

where `R_{c}` and `C_{c}` denote the mean reward and total inference cost of configuration `c`, and `R_{\text{solo}}` and `C_{\text{solo}}` those of the solo agent under the same guidance. We report `\eta_{c}` in reward points per $100; a higher `\eta_{c}` means the configuration spends its added compute more productively, and a negative `\eta_{c}` means added compute lowers reward. A configuration *dominates* another if it achieves at least the same reward at no greater cost, with one of the two strictly better. We compute `\eta_{c}` only when `C_{c}>C_{\text{solo}}`; a configuration that costs no more than the solo agent while achieving higher reward dominates it, and we mark it as such.

### Tracing the frontier

We approximate the frontier by varying one design choice at a time and fixing each subsequent study at the most efficient choice found so far. We vary, in turn, the workflow stage `s` at which the lead delegates to workers, whether planning, implementation, verification, or all three (Section [5](https://arxiv.org/html/2610.17471#S5 "5 Where should workers be utilized? ‣ Scaling Inference-Time Compute with Teams of Coding Agents")); the lead and worker models `\ell` and `w` (Section [6](https://arxiv.org/html/2610.17471#S6 "6 Can Heterogeneous Teams Scale More Efficiently? ‣ Scaling Inference-Time Compute with Teams of Coding Agents")); and the number of workers `n` (Section [7](https://arxiv.org/html/2610.17471#S7 "7 How Many Workers Should a Team Have? ‣ Scaling Inference-Time Compute with Teams of Coding Agents")). Since this coordinate-wise search does not solve Eq. [1](https://arxiv.org/html/2610.17471#S2.E1 "Equation 1 ‣ Formulation ‣ 2 Team Design as Budget-Constrained Optimization ‣ Scaling Inference-Time Compute with Teams of Coding Agents"), the resulting configurations are empirical operating points rather than guaranteed optima.

## 3 Experimental Setup

### Harness Architecture

To study multi-agent orchestration under controlled conditions, we design a configurable harness that isolates key orchestration primitives such as scheduling, message delivery, agent prompts, and model choice.
Following the minimalist design of mini-SWE-agent ([Yang et al., 2024](https://arxiv.org/html/2610.17471#bib.bib12)), agents use a standard bash tool to interact with the environment and follow a ReAct-style loop ([Yao et al., 2023](https://arxiv.org/html/2610.17471#bib.bib19)).
We adopt a top-down hierarchy where a lead agent receives the task instruction and coordinates workers through a delegate_agent(task, agent_id=None) tool.
Omitting agent_id instantiates a fresh worker with its own context window and role prompt.
Providing an existing ID resumes that worker, preserving its conversation history (e.g., to revise tests or continue debugging an authored module).
In some configurations, list_agents and wait_for_updates tools are also provided to the lead, allowing it to check the status of all agents or block until the next worker update is surfaced.

### Agent Team Configurations

Given a task, the lead dynamically determines the team size and delegates well-scoped subtasks to worker agents. Each worker observes only its assigned subtask: it does not receive the full task description or observe other workers’ conversations. We evaluate two scheduling strategies. Under *blocking* scheduling, the lead waits for a worker to finish before continuing; under *asynchronous* scheduling, the lead continues working while workers execute concurrently and receives their outputs upon completion. Unless otherwise noted, Sections [4](https://arxiv.org/html/2610.17471#S4 "4 Does a team of agents outperform a solo agent? ‣ Scaling Inference-Time Compute with Teams of Coding Agents")–[7](https://arxiv.org/html/2610.17471#S7 "7 How Many Workers Should a Team Have? ‣ Scaling Inference-Time Compute with Teams of Coding Agents") use only communication at delegation boundaries: the lead provides a subtask when it spawns or resumes a worker, and the worker’s terminal output is delivered to the lead upon completion. Agents cannot exchange direct messages while a worker is running, either between the lead and workers or among workers. Section [8](https://arxiv.org/html/2610.17471#S8 "8 Does inter-agent communication help? ‣ Scaling Inference-Time Compute with Teams of Coding Agents") adds and evaluates this capability. We also compare two prompting regimes. Under *minimal* prompting, the lead is only told to assign workers non-conflicting tasks and how its delegation tools behave; when and how to delegate is left to the lead. For guided prompting, we adopt a three-stage abstraction inspired by waterfall-style software development ([Royce, 1987](https://arxiv.org/html/2610.17471#bib.bib35)): planning and exploration (P), implementation (I), and verification (V). Each stage-specific guidance instructs the lead to complete the full workflow while using workers only in the designated phase. This design isolates the value of delegation at each phase. We then compose all three interventions into PIV, our *heavy-guidance* variant, to evaluate their joint effect when workers are used throughout the workflow (full prompts in Appendix [D](https://arxiv.org/html/2610.17471#A4 "Appendix D Prompts and Tool Definitions ‣ Scaling Inference-Time Compute with Teams of Coding Agents")).

### Datasets

We primarily use ProgramBench ([Yang et al., 2026a](https://arxiv.org/html/2610.17471#bib.bib13)), a from-scratch repository reconstruction benchmark comprised of 200 unique tasks ranging from simpler command-line utilities like CMatrix and Ripgrep to complex programs like FFmpeg and The PHP Interpreter.
In each task, an agent is provided access to a fresh workspace, a black-box reference executable, and relevant behavioral documentation from the original repository.

Rather than repairing existing codebases or satisfying pre-written unit tests ([Jimenez et al., 2024](https://arxiv.org/html/2610.17471#bib.bib11)), the agent must actively probe the reference executable to discover its interface, edge cases, and runtime behavior, and then reconstruct a compatible implementation that is evaluated against held-out behavioral test suites.
Additionally, we also explore Commit0-Lite ([Zhao et al., 2024](https://arxiv.org/html/2610.17471#bib.bib33))22
2
Commit0-Lite is only reported in the Appendix [C.13](https://arxiv.org/html/2610.17471#A3.SS13 "C.13 Commit0 ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents"): its 16 tasks limit statistical power, and it is near saturation, likely because frontier models are trained on its public libraries. a benchmark comprised of 16 Python libraries that an agent is asked to reimplement given a repository skeleton and a set of unit tests.

### Models

We conduct our main experiments with three tiers of the GPT-5.6 model family ([OpenAI, 2026](https://arxiv.org/html/2610.17471#bib.bib4)): Sol, Terra, and Luna, with all models set to use medium reasoning effort.
Homogeneous teams use the same model for the lead and all workers. Heterogeneous teams pair a Sol or Terra lead with Luna workers.
We also run additional experiments with Claude and Gemini model families (Appendix [C](https://arxiv.org/html/2610.17471#A3 "Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents")).

## 4 Does a team of agents outperform a solo agent?

Figure 2: Teams outperform solo agents, but incur higher inference and wall-clock costs. Mean ProgramBench reward versus total inference
cost (left) and total recorded wall-clock time (right) for Sol solo agents and homogeneous blocking and asynchronous teams under minimal and heavy (PIV) guidance. Points are means over three runs; error bars are 95% intervals over tasks of each team’s paired difference from the solo agent with the same guidance.

### Results

Teams outperform solo agents under both minimal and heavy PIV guidance, and heavy guidance pushes them further ahead, yielding the best reward (Figure [2](https://arxiv.org/html/2610.17471#S4.F2 "Figure 2 ‣ 4 Does a team of agents outperform a solo agent? ‣ Scaling Inference-Time Compute with Teams of Coding Agents")). Teams spawn between 4.2 and 5 workers depending on whether minimal or heavy guidance is provided. Compared to a solo agent that issues between 19 and 22 tool calls, (Appendix [C.6](https://arxiv.org/html/2610.17471#A3.SS6 "C.6 Activity Statistics ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents")), teams issue between 44 and 140 tool calls per task based on the guidance respectively. Across configurations, gains are largest on easy tasks and are less pronounced on harder ones (Appendix [C.7](https://arxiv.org/html/2610.17471#A3.SS7 "C.7 Where teams add reward: task difficulty ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents")). A team is thus an effective way to scale inference-time compute, but it incurs substantially higher inference cost. On Sol, blocking teams take 3.5`\times` longer under minimal guidance and 3.8`\times` longer under heavy guidance. Whereas asynchronous teams take 1.4`\times` and 3.1`\times` longer respectively, a setting where the lead can also progress simultaneously with the workers as opposed to blocking where the lead idles while the workers run.
Under minimal guidance, however, this speed costs about 6 reward points relative to blocking. An asynchronous lead must decide for itself when to wait for workers, and in the trajectories we inspected it often acted on partial results or ended the task before its workers had finished. Heavy guidance, which instructs the lead to collect every report first, closes this gap.

This raises the central question of our study:
how should a team allocate its compute to reach the Pareto frontier of performance and cost?

## 5 Where should workers be utilized?

We first vary the stage `s` to which workers are directed. We ask whether directing workers to specific stages of the software-engineering workflow (planning a design, implementing it, and verifying its behavior) changes this tradeoff. We consider 3 variants besides heavy guidance prompting (PIV)
that differ in where the lead delegates work. Under *heavy guidance (PIV)*, the team follows a plan-implement-verify workflow, and the lead decides which stages to delegate to workers (Appendix [D](https://arxiv.org/html/2610.17471#A4 "Appendix D Prompts and Tool Definitions ‣ Scaling Inference-Time Compute with Teams of Coding Agents")). To isolate the value of each stage, in the other three variants we restrict all delegation to a single stage and let the lead handle the rest: under *planning* (P), workers explore and plan while the lead implements and verifies; under *implementation* (I), workers write code while the lead plans, integrates, and verifies; and under *verification* (V), workers test the lead’s work after it plans and implements.
33
3
We use Sol as the default model in subsequent analyses, since its higher capability better isolates how coordination choices shape team performance. Additional results for Terra and Luna are included in Appendix [C](https://arxiv.org/html/2610.17471#A3 "Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents")

Figure 3: Planning provides the strongest reward–cost tradeoff under both schedules on ProgramBench (Sol teams; means over three runs).
Error bars are paired 95% intervals relative to Solo PIV.

Figure 4: Efficiency `\eta` of Sol teams relative to the Sol Solo PIV agent. Error bars are 95% bootstrap intervals over tasks.

### Results

Planning is by far the most efficient place to spend compute (Figure [4](https://arxiv.org/html/2610.17471#S5.F4 "Figure 4 ‣ 5 Where should workers be utilized? ‣ Scaling Inference-Time Compute with Teams of Coding Agents"), Figure [4](https://arxiv.org/html/2610.17471#S5.F4 "Figure 4 ‣ 5 Where should workers be utilized? ‣ Scaling Inference-Time Compute with Teams of Coding Agents")). With `\eta_{\text{P}}=3.8` versus at most `2.4` for any other stage (Eq. [2](https://arxiv.org/html/2610.17471#S2.E2 "Equation 2 ‣ Efficiency ‣ 2 Team Design as Budget-Constrained Optimization ‣ Scaling Inference-Time Compute with Teams of Coding Agents")), each dollar spent on planning buys roughly `1.6\times` more reward than the same dollar spent on implementation, verification, or the full workflow. Planning alone matches the reward of heavy PIV guidance at half the cost, and thus dominates it on the frontier. Because ProgramBench provides the target program only as a black-box executable, its behavior must be uncovered through probing, and planning workers parallelize this discovery across its interface, edge cases, and outputs. Additional compute therefore pays off most before any code is written, and delegating beyond planning adds cost without improving reward.

### Why is planning efficient?

To understand how guidance shapes the team’s use of compute, we locate every successful lead delegation call relative to the team’s first and last source edits, which divide each rollout into planning (pre-edit), implementation (edit), and verification (post-edit) phases (Figure [5](https://arxiv.org/html/2610.17471#S5.F5 "Figure 5 ‣ Why is planning efficient? ‣ 5 Where should workers be utilized? ‣ Scaling Inference-Time Compute with Teams of Coding Agents")).

Figure 5: Stage guidance shifts delegation timing, but nominal labels
do not partition edit-defined phases. The figure covers 600 ProgramBench rollouts per guidance setting (200 tasks `\times` three runs) from homogeneous Sol blocking teams, with the lead’s successful delegate_agent calls marked. The four left rasters show PIV, P, I, and V guidance from top to bottom. Each row represents one rollout. Within each panel, rows are ordered by implementation start (the first detected source write; defined in Appendix [B](https://arxiv.org/html/2610.17471#A2 "Appendix B Guidance delegation ‣ Scaling Inference-Time Compute with Teams of Coding Agents")), with the earliest at the bottom; rows are not aligned across panels. The bars on the right give the mean share of a rollout’s delegation calls in the planning (P), implementation (I), and verification (V) phases (one P-guidance rollout without delegation calls is excluded); error bars are 95% bootstrap intervals from resampling tasks. Per-guidance call counts vary by at most 3% across runs.

On average, Planning guidance issues all of its 674 calls in a single burst before any code is written. Heavy PIV guidance issues a comparable 794 calls before the first edit, then keeps delegating through implementation and verification, adding an additional 830 calls that yield no additional reward. With the same gain over the solo agent, planning therefore obtains `2.4\times` more reward per call, mirroring its efficiency advantage (`\eta_{\text{P}}=3.8` vs. `\eta_{\text{PIV}}=1.4`): one early burst of discovery rather than continuous delegation. This advantage is task-dependent. On Commit0-Lite, where the repository skeleton largely supplies the decomposition, implementation guidance instead becomes the most effective stage for delegation (Appendix [C.13](https://arxiv.org/html/2610.17471#A3.SS13 "C.13 Commit0 ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents")).

Figure 6: Planning remains the strongest reward–cost tradeoff with cheaper workers. Mean reward versus total inference cost for a Sol lead with Luna workers under P, I, V, or PIV guidance. Solid lines lead to blocking teams (open squares) and dotted lines to asynchronous teams (filled squares); error bars are paired 95% intervals relative to Solo PIV.

Figure 7: Strong leads paired with cheaper planning workers open a lower-cost scaling axis. Mean reward versus total inference cost (log scale) for Solo PIV agents and asynchronous planning teams led by Luna, Terra, or Sol. Stars mark heterogeneous teams with Luna workers: Sol+Luna recovers `47.5\%` of the all-Sol team’s reward gain at `13.9\%` of its added cost.

## 6 Can Heterogeneous Teams Scale More Efficiently?

In all configurations considered thus far, workers share the model of their lead. Replicating an expensive model across every role, however, multiplies the cost of the team, and it remains unclear whether strong workers are necessary to realize the benefits of delegation. To investigate this question, we retain a Sol lead and replace all of its workers with the substantially cheaper Luna. Because weaker workers may alter which stages of the workflow benefit from delegation, we again direct them toward planning (P), implementation (I), verification (V), or all three stages (PIV).

### Results

Cheap workers pay off only when directed toward planning (Figure [7](https://arxiv.org/html/2610.17471#S5.F7 "Figure 7 ‣ Why is planning efficient? ‣ 5 Where should workers be utilized? ‣ Scaling Inference-Time Compute with Teams of Coding Agents")). Relative to PIV, planning raises reward by 5.6% while lowering cost by 22.2% under blocking, and by 4.0% while lowering cost by 30.9% under asynchronous push. Directed toward implementation, by contrast, Luna workers reduce the team’s reward below that of the Sol solo agent while increasing its cost, and directed toward verification, they leave reward essentially unchanged. The reward–cost trajectories in Figure [7](https://arxiv.org/html/2610.17471#S5.F7 "Figure 7 ‣ Why is planning efficient? ‣ 5 Where should workers be utilized? ‣ Scaling Inference-Time Compute with Teams of Coding Agents") make this contrast explicit: planning climbs most sharply, whereas implementation falls below the solo level, where `\eta` is negative. Cheap workers are thus effective when they gather information for a strong lead to act upon, but not when they produce code that the lead must integrate. The payoff of this substitution is striking: every dollar spent on Luna planners buys roughly `13\times` more reward than the same dollar spent on Sol planners (`\eta=51.0` versus `3.8` under blocking), whereas for implementation the same substitution is ruinous, with each additional dollar lowering reward (`\eta=-12.0`).

### Can a stronger lead make better use of the same workers?

To disentangle lead capability from worker capability, we fix all workers at Luna and vary the lead across Luna, Terra, and Sol (Figure [7](https://arxiv.org/html/2610.17471#S5.F7 "Figure 7 ‣ Why is planning efficient? ‣ 5 Where should workers be utilized? ‣ Scaling Inference-Time Compute with Teams of Coding Agents")). Team reward closely tracks the capability of the lead: with identical Luna workers, upgrading the lead from Luna to Terra raises reward by 20.9%, and from Terra to Sol by a further 15.4%, and at every tier the team outperforms the solo agent built on the same model. Cheap workers, however, cannot compensate for a weak lead, as a Terra lead with Luna workers still trails a Sol agent working alone by 10.3%. The lead therefore determines the ceiling that a team can reach, while the workers determine how cheaply it is approached, suggesting that model capability is best invested in the lead rather than replicated across the team. Across all lead tiers and schedules, planning remains the most efficient way to direct the workers, attaining the highest efficiency `\eta` and reducing inference cost by 22–46% relative to PIV (Appendix [C.4](https://arxiv.org/html/2610.17471#A3.SS4 "C.4 Heterogeneous teams and lead capability ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents")).

## 7 How Many Workers Should a Team Have?

Figure 8: Where additional agents are deployed determines the reward–cost scaling curve. Fixed teams pair a GPT-5.6 Sol lead with 2–16 Luna workers (numbers give team size); dynamic teams are all-Sol teams sized by the lead, shown at their mean number of workers. Scaling the heterogeneous team to 16 workers with planning guidance comes within 1.4 points of the homogeneous team at 70% lower cost. All teams use asynchronous push. Fixed teams are a single run; error bars (left) are paired 95% intervals relative to Solo PIV.

### Scaling the number of workers

In the preceding sections, the lead determined the team size itself, spawning 4.2–5 workers on average. We now control the team size `n` directly, pairing a Sol lead with 2, 4, 8, or 16 Luna workers directed toward planning, implementation, or verification, which lets us ask whether additional workers continue to pay off and at which stage of the workflow.
Directed toward planning, sixteen Luna workers come within 1.4 points of an all-Sol team at 70% lower cost
(Figure [8](https://arxiv.org/html/2610.17471#S7.F8 "Figure 8 ‣ 7 How Many Workers Should a Team Have? ‣ Scaling Inference-Time Compute with Teams of Coding Agents")), making them roughly `4\times` more efficient. This gain, however, depends on where the workers are directed, as Figure [8](https://arxiv.org/html/2610.17471#S7.F8 "Figure 8 ‣ 7 How Many Workers Should a Team Have? ‣ Scaling Inference-Time Compute with Teams of Coding Agents") reveals a pronounced asymmetry across stages. Planning workers improve reward at every team size: two workers already improve on the solo agent by 3.2%, and sixteen raise the gain to 7.1%.
Implementation and verification workers, in contrast, improve from two to four workers but then plateau, with their reward changing by `-0.015` and `-0.011`, respectively, when scaling to 16 workers.
The plateau is not explained by explicit coordination failures.
We find that implementers rarely write to the same file (PIV guidance instructs the lead to delegate independent tasks; Appendix [D](https://arxiv.org/html/2610.17471#A4 "Appendix D Prompts and Tool Definitions ‣ Scaling Inference-Time Compute with Teams of Coding Agents")) and verifier reports become less useful as the team grows (Appendix [C.8](https://arxiv.org/html/2610.17471#A3.SS8 "C.8 Why implementation and verification plateau ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents")). Instead, planners return progressively more information about the black-box target, whereas additional implementers and verifiers subdivide work the lead can already coordinate without adding new information about the program.

## 8 Does inter-agent communication help?

To study communication, we give every agent a send_message tool that can reach any other running agent.44
4
Agents were only able to send messages to other agents that were actively working, so we also provided all agents with the list_agents tool. Messages flow largely from workers to the lead (84% for Sol teams under PIV guidance), carrying interim findings, proposed interfaces, verification failures, and questions. Workers rarely message each other (less than one message per task), even when told to collaborate (Appendix [C.10](https://arxiv.org/html/2610.17471#A3.SS10 "C.10 Peer-to-peer messaging ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents")).

Communication grows with model capability (Figure [9](https://arxiv.org/html/2610.17471#S8.F9 "Figure 9 ‣ 8 Does inter-agent communication help? ‣ Scaling Inference-Time Compute with Teams of Coding Agents")). Under minimal guidance, all three tiers send 7–9 messages per task, but Sol writes `3.4\times` as much text as Luna (13.7k versus 4.0k characters). Under PIV guidance, stronger teams also send more messages (10.9 to 16.9 per task), and their leads steer workers more (0.15 to 2.0 lead-to-worker messages per task). Greater communication, however, does not yield higher reward. Sol and Terra teams are unchanged within noise, and Luna teams lose 4.4–7.1 points (Figure [9](https://arxiv.org/html/2610.17471#S8.F9 "Figure 9 ‣ 8 Does inter-agent communication help? ‣ Scaling Inference-Time Compute with Teams of Coding Agents")). The channel mostly carries status reports to a lead that already receives each worker’s outcome.

Figure 9: Stronger models communicate more, but messaging does not raise reward. Homogeneous asynchronous teams under minimal and PIV guidance. Hatched segments are rejected worker calls. Right: reward change relative to the same team without the tool, with paired 95% intervals.

## 9 Related Work

### Multi-agent Coding Systems

There is a growing body of work on teams of coding agents. Early systems encode a fixed team workflow into their orchestration, assigning specialized roles ([Qian et al., 2024](https://arxiv.org/html/2610.17471#bib.bib20); [Hong et al., 2024](https://arxiv.org/html/2610.17471#bib.bib21); [Tao et al., 2024](https://arxiv.org/html/2610.17471#bib.bib22); [Liu et al., 2025](https://arxiv.org/html/2610.17471#bib.bib23)). More recent work asks how teams behave as they grow and run concurrently. CAID ([Geng and Neubig, 2026](https://arxiv.org/html/2610.17471#bib.bib14)) combines dependency-aware delegation with isolated workspaces and asynchronous execution, and [Yang et al. (2026b)](https://arxiv.org/html/2610.17471#bib.bib15) study when partitioning coding tasks across parallel agents pays off. Agensh ([Zhan et al., 2026](https://arxiv.org/html/2610.17471#bib.bib25)) lets teams self-organize from 1 to 128 agents on the five hardest ProgramBench tasks and scales one task to 1,024 agents. We instead hold one lead–worker architecture fixed and run a controlled study on all 200 ProgramBench tasks, measuring how each design choice moves the team along the reward-cost frontier.

### Team configuration under a budget

Closest to our work are studies of how to configure a team given limited compute. ZEBRA ([Hamri and Talgam-Cohen, 2026](https://arxiv.org/html/2610.17471#bib.bib26)) allocates a fixed monetary budget across coding phases, ManagerWorker ([Liu, 2026](https://arxiv.org/html/2610.17471#bib.bib27)) pairs strong managers with weaker workers, and AgentCARD ([Jiang et al., 2026](https://arxiv.org/html/2610.17471#bib.bib28)) shows that the value of role and model placement depends on the task domain. LoopArena ([Wang et al., 2026](https://arxiv.org/html/2610.17471#bib.bib24)) isolates controller capability by holding a coding worker fixed, and [Pan et al. (2026)](https://arxiv.org/html/2610.17471#bib.bib29) and [Fan et al. (2026)](https://arxiv.org/html/2610.17471#bib.bib30) show that harness components such as planning, action interfaces, and context management change task outcomes and costs. We bring these questions together in a single white-box harness, comparing stage-directed delegation, scheduling, lead and worker capability, and team size on a common benchmark.

## 10 Discussion and Conclusion

### From Solo Agents to Agent Societies

Inference-time scaling is moving from single agents toward teams of agents, and we expect this shift to accelerate as tasks grow from fixing a bug or implementing a feature to scientific discovery and open-ended research. Our results show that teams deliver gains over solo agents, but at a substantial increase in inference cost. We show, however, that with the right allocation of compute, a team can nearly match the reward of an all-strong team at 70% lower cost. The next question is how to manage teams of hundreds, thousands, or even millions of agents. For this study, we considered teams of up to sixteen workers, although we expect team sizes to grow substantially in practice. At that scale, how such teams should be organized? How should their agents communicate, and where is their compute best spent? And can agents optimize the network themselves, so that depending on the task, the budget, and the deadline, they make these choices naturally?

### Imposed Hierarchy versus Self-Organization

Our harness imposes a lead–worker hierarchy, but a society of thousands of agents working over weeks must decide who assigns roles, how information flows, when to reorganize, and how agents communicate. In our runs, workers rarely talk to each other: 84% of messages go to the lead and only 4% between workers (Section [8](https://arxiv.org/html/2610.17471#S8 "8 Does inter-agent communication help? ‣ Scaling Inference-Time Compute with Teams of Coding Agents")). This may partly reflect our harness, which exposes a messaging tool but does not incentivize its use, and partly the task, since on ProgramBench the lead can still hold the full picture. As projects outgrow what any single agent can track, agents will need to share what they learn directly, and may even invent their own protocols to do so. Pretraining on human text already gives agents primitives such as reporting, asking, and delegating. Whether coordination emerges from these with model parameters scale or must be trained remains open, and we see it as central to scaling inference.

### Call for Multi-Agent Safety and Security

Our work studies how teams of coding agents scale and how to approach the reward-cost frontier, but does not evaluate their safety. The mechanisms that improve team performance may also introduce new risks: aligning individual agents does not guarantee that the team behaves as intended, errors can propagate through delegation, and agents may develop communication protocols that are difficult for humans to audit. We invite the broader research community, particularly those advancing multi-agent capabilities, to develop methods for monitoring, auditing, and aligning agent societies alongside methods for scaling them.

## Acknowledgements

We thank Beyza Ermiş, Julia Kreutzer and Jon Ander Campos for their thoughtful feedback on the paper; Gautier Dagan and Minjie Xu for early discussions; and Aryan Mann and Saurabh Dash for their technical assistance. We are also grateful to Thomas Euyang for the beautiful figures.

## References

- Anthropic (2026)
  Anthropic
  Claude fable 5 and claude mythos 5.
  Note: Technical report and model release
  External Links: [Link](https://www.anthropic.com/news/claude-fable-5-mythos-5)
  Cited by: [§1](https://arxiv.org/html/2610.17471#S1.p1.1 "1 Introduction ‣ Scaling Inference-Time Compute with Teams of Coding Agents").
- Brown et al. (2024)
  B. Brown, J. Juravsky, R. Ehrlich, R. Clark, Q. V. Le, C. Ré, and A. Mirhoseini
  Large language monkeys: scaling inference compute with repeated sampling.
  External Links: 2407.21787,
  [Link](https://arxiv.org/abs/2407.21787)
  Cited by: [§1](https://arxiv.org/html/2610.17471#S1.p1.1 "1 Introduction ‣ Scaling Inference-Time Compute with Teams of Coding Agents").
- DeepSeek-AI et al. (2026)
  DeepSeek-AI, :, A. Xu, B. Li, B. Lin, B. Xue, B. Xian, B. Xu, B. Wu, B. Zhang, B. Deng, C. C. Yu, C. Jin, C. Lin, C. Dong, C. Wang, C. Feng, C. Lu, C. Zhao, C. Deng, C. Zhang, C. Xu, C. Zhao, C. Shao, C. Wang, C. Zhang, D. Dai, D. Yang, D. Chen, D. Huang, D. Wu, D. Li, E. Li, E. Fu, F. Zhou, F. Zhou, F. Lin, F. Yuan, F. Xia, F. Dai, G. Hao, G. Li, G. Chen, G. Cao, G. Fan, G. Meng, G. Li, H. Zhang, H. Ma, H. Shen, H. Li, H. Yu, H. Zhang, H. Deng, H. Xu, H. Xu, H. Zhong, H. Guo, H. Jiang, H. Li, H. Qin, H. Wen, H. Liang, H. Huang, H. Liu, H. Zhang, H. Luo, H. Yang, H. Xu, H. Yuan, H. Huang, H. Luo, H. Cai, H. Chen, H. Ji, H. Zhang, H. Wang, H. Wu, H. Ding, H. Tang, H. Wang, H. Cao, H. Gao, H. Qu, H. Zeng, J. Yang, J. H. Jin, J. H. Zhang, J. X. Zou, J. Yu, J. Zhou, J. Chen, J. Huang, J. Zhao, J. Tang, J. Zhou, J. Tong, J. Li, J. Zhu, J. Wang, J. Ye, J. Li, J. Xu, J. Ding, J. Lu, J. Hu, J. Yan, J. Zhai, J. Chen, J. Hu, J. Zhou, J. Xu, J. Xiang, J. Yun, J. Yuan, J. Cheng, J. Zhu, J. Wang, J. Chen, J. Hu, J. Yu, J. Guo, J. Pei, J. Sun, J. Jiang, J. Qiu, J. Zhou, J. Liu, J. Li, J. Li, J. Song, J. Guo, K. Dong, K. Chen, K. Gao, K. Guan, K. Yuan, K. Hong, K. Xu, K. Zhao, K. Ji, K. Zhang, K. Zhou, K. Yu, L. Zhang, L. Wang, L. Zhang, L. Wang, L. Gao, L. Zhao, L. Xu, L. Guo, L. Luo, L. Fu, L. Deng, L. Wang, L. Zhang, L. Chen, L. Chen, L. Huang, L. Ma, L. Wang, M. S. Di, M. Mei, M. Ye, M. Cui, M. Zhang, M. Zhang, M. Tang, M. Zhang, M. Wei, M. Chen, M. Liu, M. Zhou, M. Xu, M. Yang, M. Wang, M. Chen, N. Shentu, N. Wang, N. Ning, P. Huang, P. Cong, P. Wang, P. Xin, P. Ren, P. Yan, P. Zhang, Q. Kang, Q. Tang, Q. Wang, Q. Li, Q. Zhu, Q. Li, Q. Chen, Q. Du, Q. Guo, R. Xu, R. Ding, R. Hu, R. Tian, R. Yu, R. Zhu, R. Xu, R. Yang, R. Xia, R. Lu, R. Geng, R. Hong, R. Ge, R. Zhang, R. Sun, R. Pan, R. Wang, R. Chen, R. Xu, R. Tian, R. Shen, R. Zhang, R. X., S. H. Liu, S. Lu, S. Zhou, S. Chen, S. Cai, S. Nie, S. Chen, S. Hu, S. Lin, S. Ran, S. Liu, S. Jia, S. Bai, S. Feng, S. Xu, S. Liu, S. Hu, S. Ma, S. Wang, S. Feng, S. Gong, S. Lin, S. Yu, S. Zhou, S. Yang, S. Wang, S. Guo, S. Pan, S. Yu, S. Cao, S. Lin, S. Chen, S. Chen, S. Zhou, T. Ni, T. Yun, T. Jin, T. Pei, T. Ye, T. Lin, T. Ji, T. Cui, T. Yue, T. Yu, T. Xiong, W. Zeng, W. Liu, W. Zhang, W. Xu, W. Zeng, W. Zhao, W. Liu, W. Liang, W. Pang, W. Luo, W. Yao, W. Gao, W. Shao, W. Yang, W. Zhang, W. Wang, W. Huang, W. Yan, W. Zhang, X. Gao, X. He, X. Li, X. Li, X. Wang, X. Zhang, X. Wei, X. Bi, X. Liu, X. Wang, X. Qu, X. Chen, X. Zhang, X. Nie, X. Zou, X. Li, X. Guo, X. Chu, X. Cheng, X. Liu, X. Xie, X. Xu, X. Liu, X. Liu, X. Yu, X. Li, X. Yao, X. Chen, X. Jiang, X. Yang, X. Yang, X. Chen, X. Wang, X. Zhong, X. Su, X. Liu, X. Lin, X. Fan, X. Zhao, X. Fu, Y. C. Yan, Y. H. Jiang, Y. T. Wu, Y. W. M., Y. Z. Wang, Y. Gao, Y. Yang, Y. Zhang, Y. Ma, Y. Huang, Y. Li, Y. Li, Y. Meng, Y. Zhao, Y. Sun, Y. Wang, Y. Ye, Y. Yin, Y. Wu, Y. Qian, Y. Tao, Y. Yu, Y. Zhang, Y. Jiang, Y. Wang, Y. Ding, Y. Shi, Y. Peng, Y. Zhai, Y. Wu, Y. Xiong, Y. Wang, Y. He, Y. Zhou, Y. Luo, Y. Zhong, Y. Wang, Y. Wang, Y. Zhang, Y. Chen, Y. Tan, Y. Wei, Y. Ma, Y. Yang, Y. Liu, Y. Cai, Y. Wei, Y. Wang, Y. Yang, Y. Zhuo, Y. Guo, Y. Wu, Y. Wu, Y. Zhang, Y. Bian, Y. Cheng, Y. Ou, Y. Sun, Y. Xu, Y. Sun, Y. Li, Y. Liu, Y. Yao, Y. Han, Y. Wang, Y. Wu, Y. Meng, Y. Zou, Y. Li, Y. Wang, Y. Xiao, Y. Xiong, Y. Chen, Y. Cao, Y. Wang, Y. Chen, Y. Zhang, Y. Lin, Y. Xiao, Y. Gu, Y. Chen, Y. Huang, Y. Luo, Y. You, Y. Chen, Y. Xiang, Y. Liu, Y. Zhou, Y. Zhou, Y. Guo, Y. Huang, Y. Bai, Z. Y. Z., Z. Ni, Z. Wang, Z. Zhao, Z. Ren, Z. Zhao, Z. Sha, Z. Wang, Z. Zhang, Z. Du, Z. Fu, Z. Xu, Z. Xie, Z. Liu, Z. Zhang, Z. Dong, Z. Hao, Z. Wang, Z. Gou, Z. Ma, Z. Li, Z. Shao, Z. Huang, Z. Li, Z. Lu, Z. Huang, Z. Chen, Z. Chen, Z. Pan, Z. Wu, Z. Ren, Z. He, Z. Li, Z. Zhang, Z. Xu, Z. Wang, Z. Gu, Z. Zhu, Z. Zhang, Z. Li, Z. Hou, Z. Lyu, Z. Wang, Z. Xie, Z. Zhang, Z. Gao, Z. Pan, Z. Li, Z. Yao, Z. Chen, Z. Wu, C. Ling, C. Hou, C. Chen, D. Li, D. Qi, D. Ji, F. Wei, F. Xia, F. Xie, F. Tan, H. Guo, H. Zhai, H. Zhou, H. Tan, H. Li, J. Luo, J. Song, J. Cai, J. Liang, J. Zhou, J. Gao, J. Shao, J. Chen, J. Yang, J. Chen, J. Zhang, J. Zhou, J. Wang, J. Liu, J. Sun, J. Ling, J. Zheng, K. Yang, K. Xu, L. Su, L. Xia, L. Ding, L. Zhuo, L. Ma, L. Zhu, L. Cai, L. Yao, M. K. Zhang, M. Li, M. Lin, M. Wang, M. Zhang, M. Li, M. Wang, M. Yin, M. Han, N. Cao, N. Wang, N. Ma, P. Wang, P. Lin, P. Sun, P. Zhang, Q. Ying, Q. Xiang, Q. Wang, Q. Mao, Q. Jiang, R. Jin, R. Chen, S. Tao, S. Sun, S. Wu, S. Zou, S. Lei, T. Zhang, T. Sun, T. Yin, W. L. Xiao, W. An, W. Li, W. Wang, W. Lin, W. Hou, X. Lin, X. Meng, X. Huang, X. Peng, X. Li, X. Zhang, X. Sun, X. Wang, X. Ye, X. Zhang, X. Zhang, X. Cao, X. Chen, Y. Zhou, Y. Xu, Y. Xia, Y. Xu, Y. Shao, Y. Zhang, Y. Ma, Y. Tang, Y. Lou, Y. Chen, Y. Piao, Y. Chen, Y. Xiong, Y. Xuan, Y. Yang, Y. Xu, Y. Zha, Y. Ma, Y. Lin, Y. Yan, Y. Xie, Y. Sheng, Y. Zhu, Z. Zhang, Z. Ju, Z. Lin, Z. Gao, Z. Sun, Z. Yan, Z. Wu, Z. Wang, Z. Qu, Z. Yan, and Z. Wan
  DeepSeek-v4.1-flash: pushing the limits of kv cache compression.
  External Links: 2609.19969,
  [Link](https://arxiv.org/abs/2609.19969)
  Cited by: [§1](https://arxiv.org/html/2610.17471#S1.p1.1 "1 Introduction ‣ Scaling Inference-Time Compute with Teams of Coding Agents").
- Fan et al. (2026)
  R. Fan, Z. Zhang, S. Ma, Y. Hu, S. Wang, K. Song, F. Liu, H. Zamani, and X. Wang
  An empirical study of harness design for coding agents.
  External Links: 2609.20804,
  [Link](https://arxiv.org/abs/2609.20804)
  Cited by: [§9](https://arxiv.org/html/2610.17471#S9.SS0.SSS0.Px2.p1.1 "Team configuration under a budget ‣ 9 Related Work ‣ Scaling Inference-Time Compute with Teams of Coding Agents").
- Geng and Neubig (2026)
  J. Geng and G. Neubig
  Effective strategies for asynchronous software engineering agents.
  External Links: 2603.21489,
  [Link](https://arxiv.org/abs/2603.21489)
  Cited by: [§1](https://arxiv.org/html/2610.17471#S1.p2.1 "1 Introduction ‣ Scaling Inference-Time Compute with Teams of Coding Agents"),
  [§9](https://arxiv.org/html/2610.17471#S9.SS0.SSS0.Px1.p1.1 "Multi-agent Coding Systems ‣ 9 Related Work ‣ Scaling Inference-Time Compute with Teams of Coding Agents").
- Goodfellow et al. (2016)
  I. Goodfellow, Y. Bengio, A. Courville, and Y. Bengio
  Deep learning.
  Vol. 1, MIT Press.
- Guo et al. (2025)
  D. Guo, D. Yang, H. Zhang, J. Song, P. Wang, Q. Zhu, R. Xu, R. Zhang, S. Ma, X. Bi, X. Zhang, X. Yu, Y. Wu, Z. F. Wu, Z. Gou, Z. Shao, Z. Li, Z. Gao, A. Liu, B. Xue, B. Wang, B. Wu, B. Feng, C. Lu, C. Zhao, C. Deng, C. Ruan, D. Dai, D. Chen, D. Ji, E. Li, F. Lin, F. Dai, F. Luo, G. Hao, G. Chen, G. Li, H. Zhang, H. Xu, H. Ding, H. Gao, H. Qu, H. Li, J. Guo, J. Li, J. Chen, J. Yuan, J. Tu, J. Qiu, J. Li, J. L. Cai, J. Ni, J. Liang, J. Chen, K. Dong, K. Hu, K. You, K. Gao, K. Guan, K. Huang, K. Yu, L. Wang, L. Zhang, L. Zhao, L. Wang, L. Zhang, L. Xu, L. Xia, M. Zhang, M. Zhang, M. Tang, M. Zhou, M. Li, M. Wang, M. Li, N. Tian, P. Huang, P. Zhang, Q. Wang, Q. Chen, Q. Du, R. Ge, R. Zhang, R. Pan, R. Wang, R. J. Chen, R. L. Jin, R. Chen, S. Lu, S. Zhou, S. Chen, S. Ye, S. Wang, S. Yu, S. Zhou, S. Pan, S. S. Li, S. Zhou, S. Wu, T. Yun, T. Pei, T. Sun, T. Wang, W. Zeng, W. Liu, W. Liang, W. Gao, W. Yu, W. Zhang, W. L. Xiao, W. An, X. Liu, X. Wang, X. Chen, X. Nie, X. Cheng, X. Liu, X. Xie, X. Liu, X. Yang, X. Li, X. Su, X. Lin, X. Q. Li, X. Jin, X. Shen, X. Chen, X. Sun, X. Wang, X. Song, X. Zhou, X. Wang, X. Shan, Y. K. Li, Y. Q. Wang, Y. X. Wei, Y. Zhang, Y. Xu, Y. Li, Y. Zhao, Y. Sun, Y. Wang, Y. Yu, Y. Zhang, Y. Shi, Y. Xiong, Y. He, Y. Piao, Y. Wang, Y. Tan, Y. Ma, Y. Liu, Y. Guo, Y. Ou, Y. Wang, Y. Gong, Y. Zou, Y. He, Y. Xiong, Y. Luo, Y. You, Y. Liu, Y. Zhou, Y. X. Zhu, Y. Huang, Y. Li, Y. Zheng, Y. Zhu, Y. Ma, Y. Tang, Y. Zha, Y. Yan, Z. Z. Ren, Z. Ren, Z. Sha, Z. Fu, Z. Xu, Z. Xie, Z. Zhang, Z. Hao, Z. Ma, Z. Yan, Z. Wu, Z. Gu, Z. Zhu, Z. Liu, Z. Li, Z. Xie, Z. Song, Z. Pan, Z. Huang, Z. Xu, Z. Zhang, and Z. Zhang
  DeepSeek-r1 incentivizes reasoning in llms through reinforcement learning.
  Nature 645 (8081), pp. 633–638.
  External Links: ISSN 1476-4687,
  [Link](http://dx.doi.org/10.1038/s41586-025-09422-z),
  [Document](https://dx.doi.org/10.1038/s41586-025-09422-z)
  Cited by: [§1](https://arxiv.org/html/2610.17471#S1.p1.1 "1 Introduction ‣ Scaling Inference-Time Compute with Teams of Coding Agents").
- Hamri and Talgam-Cohen (2026)
  M. Hamri and I. Talgam-Cohen
  ZEBRA: zero-shot budgeted resource allocation for llm orchestration.
  External Links: 2605.20485,
  [Link](https://arxiv.org/abs/2605.20485)
  Cited by: [§9](https://arxiv.org/html/2610.17471#S9.SS0.SSS0.Px2.p1.1 "Team configuration under a budget ‣ 9 Related Work ‣ Scaling Inference-Time Compute with Teams of Coding Agents").
- Hong et al. (2024)
  S. Hong, M. Zhuge, J. Chen, X. Zheng, Y. Cheng, C. Zhang, J. Wang, Z. Wang, S. K. S. Yau, Z. Lin, L. Zhou, C. Ran, L. Xiao, C. Wu, and J. Schmidhuber
  MetaGPT: meta programming for a multi-agent collaborative framework.
  External Links: 2308.00352,
  [Link](https://arxiv.org/abs/2308.00352)
  Cited by: [§9](https://arxiv.org/html/2610.17471#S9.SS0.SSS0.Px1.p1.1 "Multi-agent Coding Systems ‣ 9 Related Work ‣ Scaling Inference-Time Compute with Teams of Coding Agents").
- Jiang et al. (2026)
  Y. Jiang, L. Cheng, Y. Huang, Y. Zhao, Z. Lu, L. Dong, W. Li, E. Ponti, and L. Mai
  Specialize roles, mix deployments: pushing the cost-accuracy frontier of llm agent teams.
  External Links: 2606.20629,
  [Link](https://arxiv.org/abs/2606.20629)
  Cited by: [§9](https://arxiv.org/html/2610.17471#S9.SS0.SSS0.Px2.p1.1 "Team configuration under a budget ‣ 9 Related Work ‣ Scaling Inference-Time Compute with Teams of Coding Agents").
- Jimenez et al. (2024)
  C. E. Jimenez, J. Yang, A. Wettig, S. Yao, K. Pei, O. Press, and K. Narasimhan
  SWE-bench: can language models resolve real-world github issues?.
  External Links: 2310.06770,
  [Link](https://arxiv.org/abs/2310.06770)
  Cited by: [§1](https://arxiv.org/html/2610.17471#S1.p1.1 "1 Introduction ‣ Scaling Inference-Time Compute with Teams of Coding Agents"),
  [§3](https://arxiv.org/html/2610.17471#S3.SS0.SSS0.Px3.p2.1 "Datasets ‣ 3 Experimental Setup ‣ Scaling Inference-Time Compute with Teams of Coding Agents").
- Khatua et al. (2026)
  A. Khatua, H. Zhu, P. Tran, A. Prabhudesai, F. Sadrieh, J. K. Lieberwirth, X. Yu, Y. Fu, M. J. Ryan, J. Pei, and D. Yang
  CooperBench: why coding agents cannot be your teammates yet.
  External Links: 2601.13295,
  [Link](https://arxiv.org/abs/2601.13295)
- Kim et al. (2026)
  Y. Kim, K. Gu, C. Park, C. Park, S. Schmidgall, A. A. Heydari, Y. Yan, Z. Zhang, Y. Zhuang, Y. Liu, et al.
  Capable language models can outgrow the benefits of collaboration.
  Nature Machine Intelligence 8 (7), pp. 1157–1172.
- Liu et al. (2025)
  J. Liu, G. Wang, R. Yang, J. Zeng, M. Zhao, and Y. Cai
  RTADev: intention aligned multi-agent framework for software development.
  In Findings of the Association for Computational Linguistics: ACL 2025, W. Che, J. Nabende, E. Shutova, and M. T. Pilehvar (Eds.),
  Vienna, Austria, pp. 1548–1581.
  External Links: [Link](https://aclanthology.org/2025.findings-acl.80/),
  [Document](https://dx.doi.org/10.18653/v1/2025.findings-acl.80),
  ISBN 979-8-89176-256-5
  Cited by: [§9](https://arxiv.org/html/2610.17471#S9.SS0.SSS0.Px1.p1.1 "Multi-agent Coding Systems ‣ 9 Related Work ‣ Scaling Inference-Time Compute with Teams of Coding Agents").
- Liu et al. (2026)
  M. Liu, T. Chen, Z. Xu, X. Jiang, and Y. Dong
  Multi-agent collaboration with state management.
  External Links: 2605.20563,
  [Link](https://arxiv.org/abs/2605.20563)
- Liu (2026)
  R. Liu
  Can ai models direct each other? organizational structure as a probe into training limitations.
  External Links: 2603.26458,
  [Link](https://arxiv.org/abs/2603.26458)
  Cited by: [§9](https://arxiv.org/html/2610.17471#S9.SS0.SSS0.Px2.p1.1 "Team configuration under a budget ‣ 9 Related Work ‣ Scaling Inference-Time Compute with Teams of Coding Agents").
- Miller (2024)
  E. Miller
  Adding error bars to evals: a statistical approach to language model evaluations.
  External Links: 2411.00640,
  [Link](https://arxiv.org/abs/2411.00640)
- Muennighoff et al. (2025)
  N. Muennighoff, Z. Yang, W. Shi, X. L. Li, L. Fei-Fei, H. Hajishirzi, L. Zettlemoyer, P. Liang, E. Candès, and T. Hashimoto
  S1: simple test-time scaling.
  External Links: 2501.19393,
  [Link](https://arxiv.org/abs/2501.19393)
  Cited by: [§1](https://arxiv.org/html/2610.17471#S1.p1.1 "1 Introduction ‣ Scaling Inference-Time Compute with Teams of Coding Agents").
- OpenAI et al. (2026)
  OpenAI, :, A. Jaech, A. Kalai, A. Lerer, A. Richardson, A. El-Kishky, A. Low, A. Helyar, A. Madry, A. Beutel, A. Carney, A. Iftimie, A. Karpenko, A. T. Passos, A. Neitz, A. Prokofiev, A. Wei, A. Tam, A. Bennett, A. Kumar, A. Saraiva, A. Vallone, A. Duberstein, A. Kondrich, A. Mishchenko, A. Applebaum, A. Jiang, A. Nair, B. Zoph, B. Ghorbani, B. Zhang, B. Rossen, B. Sokolowsky, B. Barak, B. McGrew, B. Minaiev, B. Hao, B. Baker, B. Houghton, B. McKinzie, B. Eastman, C. Lugaresi, C. Bassin, C. Hudson, C. M. Li, C. de Bourcy, C. Voss, C. Shen, C. Zhang, C. Koch, C. Orsinger, C. Hesse, C. Fischer, C. Chan, D. Roberts, D. Kappler, D. Levy, D. Selsam, D. Dohan, D. Farhi, D. Mely, D. Robinson, D. Tsipras, D. Li, D. Oprica, E. Freeman, E. Zhang, E. Wong, E. Proehl, E. Cheung, E. Mitchell, E. Wallace, E. Ritter, E. Mays, F. Wang, F. P. Such, F. Raso, F. Leoni, F. Tsimpourlas, F. Song, F. von Lohmann, F. Sulit, G. Salmon, G. Parascandolo, G. Chabot, G. Zhao, G. Brockman, G. Leclerc, H. Salman, H. Bao, H. Sheng, H. Andrin, H. Bagherinezhad, H. Ren, H. Lightman, H. W. Chung, I. Kivlichan, I. O’Connell, I. Osband, I. C. Gilaberte, I. Akkaya, I. Kostrikov, I. Sutskever, I. Kofman, J. Pachocki, J. Lennon, J. Wei, J. Harb, J. Twore, J. Feng, J. Yu, J. Weng, J. Tang, J. Yu, J. Q. Candela, J. Palermo, J. Parish, J. Heidecke, J. Hallman, J. Rizzo, J. Gordon, J. Uesato, J. Ward, J. Huizinga, J. Wang, K. Chen, K. Xiao, K. Singhal, K. Nguyen, K. Cobbe, K. Shi, K. Wood, K. Rimbach, K. Gu-Lemberg, K. Liu, K. Lu, K. Stone, K. Yu, L. Ahmad, L. Yang, L. Liu, L. Maksin, L. Ho, L. Fedus, L. Weng, L. Li, L. McCallum, L. Held, L. Kuhn, L. Kondraciuk, L. Kaiser, L. Metz, M. Boyd, M. Trebacz, M. Joglekar, M. Chen, M. Tintor, M. Meyer, M. Jones, M. Kaufer, M. Schwarzer, M. Shah, M. Yatbaz, M. Y. Guan, M. Xu, M. Yan, M. Glaese, M. Chen, M. Lampe, M. Malek, M. Wang, M. Fradin, M. McClay, M. Pavlov, M. Wang, M. Wang, M. Murati, M. Bavarian, M. Rohaninejad, N. McAleese, N. Chowdhury, N. Chowdhury, N. Ryder, N. Tezak, N. Brown, O. Nachum, O. Boiko, O. Murk, O. Watkins, P. Chao, P. Ashbourne, P. Izmailov, P. Zhokhov, R. Dias, R. Arora, R. Lin, R. G. Lopes, R. Gaon, R. Miyara, R. Leike, R. Hwang, R. Garg, R. Brown, R. James, R. Shu, R. Cheu, R. Greene, S. Jain, S. Altman, S. Toizer, S. Toyer, S. Miserendino, S. Agarwal, S. Hernandez, S. Baker, S. McKinney, S. Yan, S. Zhao, S. Hu, S. Santurkar, S. R. Chaudhuri, S. Zhang, S. Fu, S. Papay, S. Lin, S. Balaji, S. Sanjeev, S. Sidor, T. Broda, A. Clark, T. Wang, T. Gordon, T. Sanders, T. Patwardhan, T. Sottiaux, T. Degry, T. Dimson, T. Zheng, T. Garipov, T. Stasi, T. Bansal, T. Creech, T. Peterson, T. Eloundou, V. Qi, V. Kosaraju, V. Monaco, V. Pong, V. Fomenko, W. Zheng, W. Zhou, W. Zhan, W. McCabe, W. Zaremba, Y. Dubois, Y. Lu, Y. Chen, Y. Cha, Y. Bai, Y. He, Y. Zhang, Y. Wang, Z. Shao, and Z. Li
  OpenAI o1 system card.
  External Links: 2412.16720,
  [Link](https://arxiv.org/abs/2412.16720)
  Cited by: [§1](https://arxiv.org/html/2610.17471#S1.p1.1 "1 Introduction ‣ Scaling Inference-Time Compute with Teams of Coding Agents").
- OpenAI (2026)
  OpenAI
  GPT-5.6 Sol.
  Note: OpenAI API documentation
  External Links: [Link](https://developers.openai.com/api/docs/models/gpt-5.6-sol)
  Cited by: [§1](https://arxiv.org/html/2610.17471#S1.p1.1 "1 Introduction ‣ Scaling Inference-Time Compute with Teams of Coding Agents"),
  [§3](https://arxiv.org/html/2610.17471#S3.SS0.SSS0.Px4.p1.1 "Models ‣ 3 Experimental Setup ‣ Scaling Inference-Time Compute with Teams of Coding Agents").
- Pan et al. (2026)
  L. Pan, L. Zou, S. Guo, J. Ni, and H. Zheng
  Natural-language agent harnesses.
  External Links: 2603.25723,
  [Link](https://arxiv.org/abs/2603.25723)
  Cited by: [§9](https://arxiv.org/html/2610.17471#S9.SS0.SSS0.Px2.p1.1 "Team configuration under a budget ‣ 9 Related Work ‣ Scaling Inference-Time Compute with Teams of Coding Agents").
- Qian et al. (2024)
  C. Qian, W. Liu, H. Liu, N. Chen, Y. Dang, J. Li, C. Yang, W. Chen, Y. Su, X. Cong, J. Xu, D. Li, Z. Liu, and M. Sun
  ChatDev: communicative agents for software development.
  External Links: 2307.07924,
  [Link](https://arxiv.org/abs/2307.07924)
  Cited by: [§9](https://arxiv.org/html/2610.17471#S9.SS0.SSS0.Px1.p1.1 "Multi-agent Coding Systems ‣ 9 Related Work ‣ Scaling Inference-Time Compute with Teams of Coding Agents").
- Royce (1987)
  W. W. Royce
  Managing the development of large software systems: concepts and techniques.
  In Proceedings of the 9th international conference on Software Engineering,
  pp. 328–338.
  Cited by: [§1](https://arxiv.org/html/2610.17471#S1.p2.1 "1 Introduction ‣ Scaling Inference-Time Compute with Teams of Coding Agents"),
  [§3](https://arxiv.org/html/2610.17471#S3.SS0.SSS0.Px2.p1.1 "Agent Team Configurations ‣ 3 Experimental Setup ‣ Scaling Inference-Time Compute with Teams of Coding Agents").
- Snell et al. (2024)
  C. Snell, J. Lee, K. Xu, and A. Kumar
  Scaling llm test-time compute optimally can be more effective than scaling model parameters.
  External Links: 2408.03314,
  [Link](https://arxiv.org/abs/2408.03314)
  Cited by: [§1](https://arxiv.org/html/2610.17471#S1.p1.1 "1 Introduction ‣ Scaling Inference-Time Compute with Teams of Coding Agents").
- Tao et al. (2024)
  W. Tao, Y. Zhou, Y. Wang, W. Zhang, H. Zhang, and Y. Cheng
  MAGIS: llm-based multi-agent framework for github issue resolution.
  External Links: 2403.17927,
  [Link](https://arxiv.org/abs/2403.17927)
  Cited by: [§9](https://arxiv.org/html/2610.17471#S9.SS0.SSS0.Px1.p1.1 "Multi-agent Coding Systems ‣ 9 Related Work ‣ Scaling Inference-Time Compute with Teams of Coding Agents").
- Team et al. (2026)
  K. Team, T. Bai, Y. Bai, Y. Bao, M. C., J. Cai, X. Cai, P. Cao, Y. Cao, Z. Chai, Y. Charles, H. S. Che, G. Chen, G. Chen, G. Chen, H. Chen, J. Chen, J. Chen, J. Chen, K. Chen, P. Chen, R. Chen, W. Chen, X. Chen, Y. Chen, Y. Chen, Y. Chen, Y. Chen, Y. Chen, Y. Chen, Y. Chen, Z. Chen, D. Cheng, Y. Cheng, J. Cui, J. Cui, A. Dai, J. Deng, H. Ding, R. Ding, S. Ding, M. Dong, M. Dong, Y. Dong, Y. Dong, A. Du, C. Du, D. Du, J. Du, Y. Du, Y. Fan, J. Feng, Q. Feng, Y. Feng, K. Fu, Q. Fu, F. Gao, H. Gao, J. Gao, T. Gao, W. Gao, S. Geng, J. Gong, L. Gong, S. Gong, X. Gong, Q. Gu, Y. Gu, S. Guan, H. Guo, S. Guo, X. Guo, Z. Guo, B. Hao, W. Hao, X. Hao, D. He, H. He, L. He, Q. He, W. He, X. He, X. He, Y. He, Y. He, C. Hong, T. Hong, H. Hu, J. Hu, R. Hu, W. Hu, Y. Hu, Z. Hu, L. Hua, J. Huang, K. Huang, R. Huang, S. Huang, W. Huang, Y. Huang, Z. Huang, Z. Huang, Y. Hui, C. Jia, Y. Jiang, Z. Jiang, Z. Jiang, W. Jin, X. Jin, Y. Jing, H. Kong, G. Lai, A. Li, C. Li, C. Li, C. Li, F. Li, G. Li, H. Li, J. Li, J. Li, L. Li, L. Li, L. Li, W. Li, W. Li, X. Li, Y. Li, Y. Li, Y. Li, Y. Li, Z. Li, Z. Li, Z. Li, Z. Li, Z. Li, J. Lin, X. Lin, Y. Lin, Z. Lin, Z. Lin, B. Liu, B. Liu, C. Liu, L. Liu, S. Liu, S. Liu, S. Liu, T. Liu, W. Liu, Y. Liu, Y. Liu, Y. Liu, Y. Liu, Z. Liu, Z. Liu, E. Lu, H. Lu, L. Lu, T. Lu, Z. Lu, A. Luo, G. Luo, J. Luo, Y. Luo, B. Lyu, W. Lyu, S. Mao, Y. Mei, X. Men, M. Ni, Y. Niu, S. Pan, S. Peng, Z. Qi, R. Qin, Z. Qin, Z. Qin, H. Qiu, J. Qiu, J. Qiu, B. Qu, Y. Qu, Z. Shang, Y. Shao, H. Shen, J. Shi, J. Shi, L. Shi, S. Shi, W. Siu, P. Song, X. Song, J. Su, Y. Su, Z. Su, L. Sui, J. Sun, J. Sun, S. Sun, S. Sun, T. Sun, Y. Sun, Y. Tai, C. Tang, H. Tang, S. Tang, Z. Tang, C. Tian, R. Tian, Y. Tian, W. Tu, C. Wang, C. Wang, C. Wang, D. Wang, F. Wang, H. Wang, H. Wang, H. Wang, H. Wang, H. Wang, H. Wang, J. Wang, J. Wang, J. Wang, J. Wang, L. Wang, S. Wang, S. Wang, S. Wang, S. Wang, S. Wang, T. Wang, W. Wang, X. Wang, X. Wang, X. Wang, X. Wang, Y. Wang, Y. Wang, Y. Wang, Y. Wang, Y. Wang, Y. Wang, Y. Wang, Y. Wang, Z. Wang, Z. Wang, Z. Wang, Z. Wang, Z. Wang, Z. Wang, C. Wei, M. Wei, S. Wei, Z. Wen, F. Wu, H. Wu, R. Wu, W. Wu, X. Wu, Y. Wu, Y. Wu, Y. Wu, Z. Wu, X. Xian, C. Xiang, Y. Xiang, B. Xiao, C. Xiao, X. Xiao, J. Xie, X. Xie, Y. Xie, Z. Xie, B. Xing, Y. Xiong, B. Xu, B. Xu, J. Xu, J. Xu, J. Xu, J. Xu, L. H. Xu, Q. Xu, S. Xu, S. Xu, T. Xu, T. Xu, W. Xu, X. Xu, Y. Xu, Y. Xu, Y. Xu, Z. Xu, H. Xue, J. Yan, Y. Yan, F. Yang, G. Yang, H. Yang, J. Yang, R. Yang, W. Yang, X. Yang, X. Yang, Y. Yang, Y. Yang, Y. Yang, Y. Yang, Z. Yang, Z. Yang, Z. Yang, Z. Yang, H. Yao, D. Ye, H. Ye, W. Ye, Z. Ye, B. Yin, H. Yin, X. Yin, C. Yu, H. Yu, L. Yu, S. Yu, S. Yu, T. Yu, E. Yuan, M. Yuan, T. Yue, W. Yue, Y. Yue, D. Zha, H. Zhan, B. H. Zhang, D. Zhang, F. Zhang, H. Zhang, H. Zhang, H. Zhang, J. Zhang, J. Zhang, J. Zhang, K. Zhang, M. Zhang, P. Zhang, Q. Zhang, R. Zhang, R. Zhang, S. Zhang, S. Zhang, X. Zhang, X. Zhang, Y. Zhang, Y. Zhang, Y. Zhang, Y. Zhang, Y. Zhang, Y. Zhang, Y. Zhang, Y. Zhang, Y. Zhang, Y. Zhang, Z. Zhang, Z. Zhang, B. Zhao, C. Zhao, F. Zhao, J. Zhao, J. Zhao, S. Zhao, W. Zhao, X. Zhao, X. Zhao, Y. Zhao, Z. Zhao, H. Zheng, H. Zheng, R. Zheng, S. Zheng, T. Zheng, H. Zhong, L. Zhong, L. Zhong, M. Zhou, Q. Zhou, R. Zhou, R. Zhou, X. Zhou, Y. Zhou, Z. Zhou, J. Zhu, L. Zhu, X. Zhu, Y. Zhu, Y. Zhu, Z. Zhu, C. Zhuang, W. Zhuang, and X. Zu
  Kimi k3: open frontier intelligence.
  External Links: 2607.24653,
  [Link](https://arxiv.org/abs/2607.24653)
  Cited by: [§1](https://arxiv.org/html/2610.17471#S1.p1.1 "1 Introduction ‣ Scaling Inference-Time Compute with Teams of Coding Agents").
- Wang et al. (2023)
  X. Wang, J. Wei, D. Schuurmans, Q. Le, E. Chi, S. Narang, A. Chowdhery, and D. Zhou
  Self-consistency improves chain of thought reasoning in language models.
  External Links: 2203.11171,
  [Link](https://arxiv.org/abs/2203.11171)
  Cited by: [§1](https://arxiv.org/html/2610.17471#S1.p1.1 "1 Introduction ‣ Scaling Inference-Time Compute with Teams of Coding Agents").
- Wang et al. (2026)
  Y. Wang, H. Zhang, C. Huang, R. Dai, K. Liu, P. Koniusz, and X. Chu
  LoopArena: benchmarking models as runtime controllers for loop engineering.
  External Links: 2608.28281,
  [Link](https://arxiv.org/abs/2608.28281)
  Cited by: [§9](https://arxiv.org/html/2610.17471#S9.SS0.SSS0.Px2.p1.1 "Team configuration under a budget ‣ 9 Related Work ‣ Scaling Inference-Time Compute with Teams of Coding Agents").
- Yang et al. (2024)
  J. Yang, C. E. Jimenez, A. Wettig, K. Lieret, S. Yao, K. Narasimhan, and O. Press
  SWE-agent: agent-computer interfaces enable automated software engineering.
  External Links: 2405.15793,
  [Link](https://arxiv.org/abs/2405.15793)
  Cited by: [§1](https://arxiv.org/html/2610.17471#S1.p1.1 "1 Introduction ‣ Scaling Inference-Time Compute with Teams of Coding Agents"),
  [§3](https://arxiv.org/html/2610.17471#S3.SS0.SSS0.Px1.p1.1 "Harness Architecture ‣ 3 Experimental Setup ‣ Scaling Inference-Time Compute with Teams of Coding Agents").
- Yang et al. (2026a)
  J. Yang, K. Lieret, J. Ma, P. Thakkar, D. Pedchenko, S. Sootla, E. McMilin, P. Yin, R. Hou, G. Synnaeve, D. Yang, and O. Press
  ProgramBench: can language models rebuild programs from scratch?.
  External Links: 2605.03546,
  [Link](https://arxiv.org/abs/2605.03546)
  Cited by: [§1](https://arxiv.org/html/2610.17471#S1.p3.1 "1 Introduction ‣ Scaling Inference-Time Compute with Teams of Coding Agents"),
  [§3](https://arxiv.org/html/2610.17471#S3.SS0.SSS0.Px3.p1.1 "Datasets ‣ 3 Experimental Setup ‣ Scaling Inference-Time Compute with Teams of Coding Agents").
- Yang et al. (2026b)
  X. Yang, L. Nie, E. Chandra, S. Gannutin, F. Lin, and S. Chaudhuri
  When parallelism pays off: cohesion-aware task partitioning for multi-agent coding.
  External Links: 2606.00953,
  [Link](https://arxiv.org/abs/2606.00953)
  Cited by: [§1](https://arxiv.org/html/2610.17471#S1.p2.1 "1 Introduction ‣ Scaling Inference-Time Compute with Teams of Coding Agents"),
  [§9](https://arxiv.org/html/2610.17471#S9.SS0.SSS0.Px1.p1.1 "Multi-agent Coding Systems ‣ 9 Related Work ‣ Scaling Inference-Time Compute with Teams of Coding Agents").
- Yao et al. (2023)
  S. Yao, J. Zhao, D. Yu, N. Du, I. Shafran, K. Narasimhan, and Y. Cao
  ReAct: synergizing reasoning and acting in language models.
  External Links: 2210.03629,
  [Link](https://arxiv.org/abs/2210.03629)
  Cited by: [§3](https://arxiv.org/html/2610.17471#S3.SS0.SSS0.Px1.p1.1 "Harness Architecture ‣ 3 Experimental Setup ‣ Scaling Inference-Time Compute with Teams of Coding Agents").
- Z.ai (2026)
  Z.ai
  GLM-5.3: frontier coding with emergent cyber capabilities.
  Note: Technical report
  External Links: [Link](https://z.ai/blog/glm-5.3)
  Cited by: [§1](https://arxiv.org/html/2610.17471#S1.p1.1 "1 Introduction ‣ Scaling Inference-Time Compute with Teams of Coding Agents").
- Zhan et al. (2026)
  Z. Zhan, T. Song, L. Dong, S. Huang, J. Lian, Y. Xia, and F. Wei
  Agensh: scaling organizational intelligence to 1,024 agents.
  External Links: 2609.26781,
  [Link](https://arxiv.org/abs/2609.26781)
  Cited by: [§9](https://arxiv.org/html/2610.17471#S9.SS0.SSS0.Px1.p1.1 "Multi-agent Coding Systems ‣ 9 Related Work ‣ Scaling Inference-Time Compute with Teams of Coding Agents").
- Zhao et al. (2024)
  W. Zhao, N. Jiang, C. Lee, J. T. Chiu, C. Cardie, M. Gallé, and A. M. Rush
  Commit0: library generation from scratch.
  External Links: 2412.01769,
  [Link](https://arxiv.org/abs/2412.01769)
  Cited by: [§1](https://arxiv.org/html/2610.17471#S1.p3.1 "1 Introduction ‣ Scaling Inference-Time Compute with Teams of Coding Agents"),
  [§3](https://arxiv.org/html/2610.17471#S3.SS0.SSS0.Px3.p2.1 "Datasets ‣ 3 Experimental Setup ‣ Scaling Inference-Time Compute with Teams of Coding Agents").

Appendices

## Appendix A Harness Architecture and Implementation Details

### A.1 Agent Turn Lifecycle

A rollout begins by providing the benchmark task instruction as the initial user message to a lead agent.
The lead may invoke a delegate_agent tool with a natural-language assignment to spawn and delegate a task to a subagent worker.
The new subagent initially begins with a fresh conversation state where the initial user message contains only this assignment from the lead.

When a subagent terminates, its final assistant message becomes the result returned to the lead.
Each worker is assigned a unique agent ID (e.g. agent_1), and the lead can later delegate another task to a previously spawned agent, resuming the worker with its previous context and the new assignment as an appended user turn.
This persistence allows the lead to return to a worker that has already developed task-specific context, rather than starting a new trajectory for every delegation.

### A.2 Scheduling and Delivery Policy Comparison

Table 1: Comparison of scheduling and message-delivery policies.

| Policy | How it works | Pros | Cons |
| --- | --- | --- | --- |
| Blocking delegation | The lead delegates to a worker and remains blocked until the worker returns its result. | Simple coordination; provides a natural synchronization point; allows the lead to reason from a completed result; lowers the risk of acting on incomplete information. | The lead is idle while the worker runs; prevents lead–worker parallelism; can substantially increase wall-clock time. |
| Async push: full message | The worker runs concurrently. Once finished, its full result is appended to the lead’s next tool result. | Requires no explicit retrieval call; makes completed work difficult to overlook; preserves concurrency; allows results to be incorporated quickly. | May interrupt the lead at an awkward point; unexpectedly consumes context; multiple messages may overload the next tool output; may destabilize the lead’s current plan. |

We study two scheduling policies. Under blocking delegation, a call to delegate_agent returns only when that worker has finished.
The lead therefore cannot begin its next step until the delegated work is completed.
However, multiple delegations issued in the same turn may execute in parallel, so blocking serializes the lead with respect to its workers, rather than serializing all activity.

Under asynchronous push, a call to delegate_agent immediately returns with the agent ID and the subagent continues to work in the background.
The lead can continue reasoning, using tools, or spawning additional workers while any subagents execute concurrently.
When a worker finishes, its outcome is appended to the subsequent tool result observed by the lead.
Optionally, the lead may call wait_for_updates, which blocks until a worker update becomes available.

## Appendix B Guidance delegation

We anchor each delegation call to the team’s source
edits. The first and last detected source writes divide a rollout into three
observable intervals: time before editing, active editing, and time after
editing. Write boundaries use the
completion time of any lead or worker bash call matched by a
limited regex for patch commands, selected redirected shell writes,
terminal editors, or direct Python file writes. Writes under /tmp,
/var/tmp, /dev, and /opt, as well as writes to
the generated executable, are excluded.

We refer to these edit-defined intervals as planning,
implementation, and verification. They provide a common clock for comparing
trajectories across guidance ablations and studying delegation patterns.

Figure [5](https://arxiv.org/html/2610.17471#S5.F5 "Figure 5 ‣ Why is planning efficient? ‣ 5 Where should workers be utilized? ‣ Scaling Inference-Time Compute with Teams of Coding Agents") applies this clock to every
successful lead delegation call from homogeneous Sol blocking teams on ProgramBench,
for PIV/P/I/V guidance setups. Calls rejected by the harness (e.g. exceeding the five-worker cap) are excluded from this analysis as they failed to successfully delegate a task to a worker.
We assign each call to an interval from its completion time relative to the edit boundaries, then
normalize that time by the rollout’s team-wide wall-clock duration.

Planning guidance aligns most tightly with its nominal stage: all 674 P calls
occur before the first detected edit. V shifts calls later, although a slight
majority of its 599 calls remains within the active-edit window (55.0%), with
45.0% after the final edit. With I, 74.7% of its 429 calls precede the first edit, 25.1% occur
during active editing, and 0.2% follow the last edit. PIV instead spans all
three phases, distributing its 1,625 calls across planning (48.9%),
implementation (32.5%), and verification (18.6%).

## Appendix C Additional Experimental Details

All figures in this section use the full 200-task ProgramBench benchmark and the same conventions as the corresponding main-text figures. GPT-5.6 results are means over three runs; Claude results are single runs.

### C.1 Model configurations

Table [2](https://arxiv.org/html/2610.17471#A3.T2 "Table 2 ‣ C.1 Model configurations ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents") lists every model we evaluate, the provider we accessed it through, its reasoning setting, and the per-token prices from which all reported inference costs are computed. The same configuration is used whenever a model acts as a solo agent, a lead, or a worker.

Table 2: Model configurations and prices. Reasoning settings are OpenAI’s reasoning effort, Anthropic’s extended thinking (adaptive with an effort level, or a fixed token budget), and Gemini’s thinking level. Prompt caching is enabled explicitly for Claude on Bedrock, which charges for cache writes; OpenAI and Gemini cache prompts automatically and charge only the discounted cache-read price. Evaluation gives the ProgramBench runs in which each model appears.

|  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  | Price ($ per million tokens) | | | |  |
| Model | Provider | Reasoning setting | Input | Output | Cache read | Cache write | Evaluation |
| GPT-5.6 Sol | OpenAI | effort: medium | 4.00 | 20.00 | 0.40 | – | Full 200, 3 runs |
| GPT-5.6 Terra | OpenAI | effort: medium | 2.00 | 12.00 | 0.20 | – | Full 200, 3 runs |
| GPT-5.6 Luna | OpenAI | effort: medium | 0.20 | 1.20 | 0.02 | – | Full 200, 3 runs |
| Claude Opus 4.8 | Bedrock | adaptive, effort: medium | 5.00 | 25.00 | 0.50 | 6.25 | Balanced-30 |
| Claude Opus 4.7 | Bedrock | adaptive, effort: medium | 5.00 | 25.00 | 0.50 | 6.25 | Full 200, 1 run |
| Claude Haiku 4.5 | Bedrock | budget: 4,000 tokens | 1.00 | 5.00 | 0.10 | 1.25 | Full 200, 1 run |
| Gemini 3.8 Flash | Gemini API | level: medium | 0.75 | 3.75 | 0.075 | – | Balanced-30 |
| Gemini 3.7 Flash | Gemini API | level: medium | 0.75 | 3.75 | 0.075 | – | Balanced-30 |

### C.2 Team versus solo across models

Here we repeat the solo-versus-team comparison for homogeneous GPT-5.6 Terra and Luna teams (Figures [10](https://arxiv.org/html/2610.17471#A3.F10 "Figure 10 ‣ C.2 Team versus solo across models ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents") and [11](https://arxiv.org/html/2610.17471#A3.F11 "Figure 11 ‣ C.2 Team versus solo across models ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents")) and for Claude Opus 4.7 and Haiku 4.5 (Figures [12](https://arxiv.org/html/2610.17471#A3.F12 "Figure 12 ‣ C.2 Team versus solo across models ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents") and [13](https://arxiv.org/html/2610.17471#A3.F13 "Figure 13 ‣ C.2 Team versus solo across models ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents")). The Claude models illustrate two distinct ways in which added capacity fails to help. Opus 4.7 teams under minimal guidance are indistinguishable from the solo agent (`+0.001\pm 0.022`), because the lead almost never delegates (Table [5](https://arxiv.org/html/2610.17471#A3.T5 "Table 5 ‣ C.6 Activity Statistics ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents")). Under PIV guidance they gain `0.043`–`0.063` at 1.7–2.0`\times` the solo cost. Haiku 4.5 delegates readily, but every team configuration scores at or below the solo agent (`-0.041` to `-0.004`) at roughly twice the cost.

Figure 10: Solo agents versus homogeneous Terra teams. Each configuration is run for three trials, and error bars are 95% intervals over tasks of each team’s paired difference from the solo agent with the same guidance.

Figure 11: Solo agents versus homogeneous Luna (bottom) teams. Each configuration is run for three trials, and error bars are 95% intervals over tasks of each team’s paired difference from the solo agent with the same guidance.

Figure 12: Solo agents versus homogeneous teams for Claude Opus 4.7. Each is a single run, and error bars are 95% intervals over tasks of each team’s paired difference from the solo agent with the same guidance.

Figure 13: Solo agents versus homogeneous teams for Claude Haiku 4.5. Each is a single run, and error bars are 95% intervals over tasks of each team’s paired difference from the solo agent with the same guidance.

### C.3 Stage guidance across model tiers

Figures [14](https://arxiv.org/html/2610.17471#A3.F14 "Figure 14 ‣ C.3 Stage guidance across model tiers ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents") and [15](https://arxiv.org/html/2610.17471#A3.F15 "Figure 15 ‣ C.3 Stage guidance across model tiers ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents") repeat the stage-guidance (Figure [4](https://arxiv.org/html/2610.17471#S5.F4 "Figure 4 ‣ 5 Where should workers be utilized? ‣ Scaling Inference-Time Compute with Teams of Coding Agents")) and efficiency (Figure [4](https://arxiv.org/html/2610.17471#S5.F4 "Figure 4 ‣ 5 Where should workers be utilized? ‣ Scaling Inference-Time Compute with Teams of Coding Agents")) comparisons for homogeneous Terra and Luna teams. Figures [16](https://arxiv.org/html/2610.17471#A3.F16 "Figure 16 ‣ C.3 Stage guidance across model tiers ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents") and [17](https://arxiv.org/html/2610.17471#A3.F17 "Figure 17 ‣ C.3 Stage guidance across model tiers ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents") do the same for teams with Luna workers, complementing Figure [7](https://arxiv.org/html/2610.17471#S5.F7 "Figure 7 ‣ Why is planning efficient? ‣ 5 Where should workers be utilized? ‣ Scaling Inference-Time Compute with Teams of Coding Agents").

Figure 14: Stage guidance for homogeneous Terra (left) and Luna (right) teams, as in Figure [4](https://arxiv.org/html/2610.17471#S5.F4 "Figure 4 ‣ 5 Where should workers be utilized? ‣ Scaling Inference-Time Compute with Teams of Coding Agents").

Figure 15: Efficiency `\eta` of homogeneous Terra (left) and Luna (right) teams relative to each tier’s Solo PIV agent, as in Figure [4](https://arxiv.org/html/2610.17471#S5.F4 "Figure 4 ‣ 5 Where should workers be utilized? ‣ Scaling Inference-Time Compute with Teams of Coding Agents").

Figure 16: Stage guidance for heterogeneous teams with Terra lead with Luna workers.

Figure 17: Efficiency `\eta` for a Terra lead (left) and a Sol lead (right) with Luna workers, relative to the lead’s Solo PIV agent. A missing bar marks a team that is both cheaper and higher-reward than the solo agent (it dominates it). Error bars are 95% bootstrap intervals over tasks.

### C.4 Heterogeneous teams and lead capability

Figure [18](https://arxiv.org/html/2610.17471#A3.F18 "Figure 18 ‣ C.4 Heterogeneous teams and lead capability ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents") repeats Figure [7](https://arxiv.org/html/2610.17471#S5.F7 "Figure 7 ‣ Why is planning efficient? ‣ 5 Where should workers be utilized? ‣ Scaling Inference-Time Compute with Teams of Coding Agents") with PIV-guided instead of planning-guided teams.
Figure [19](https://arxiv.org/html/2610.17471#A3.F19 "Figure 19 ‣ C.4 Heterogeneous teams and lead capability ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents") fixes workers at Luna and varies the lead. With workers fixed at Luna, planning guidance attains the highest reward with Luna and Sol leads under both schedules; with a Terra lead, PIV is 0.003–0.009 higher. Planning costs 22–46% less than PIV across all six lead–schedule combinations (Figure [19](https://arxiv.org/html/2610.17471#A3.F19 "Figure 19 ‣ C.4 Heterogeneous teams and lead capability ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents")).

Figure 18: Solo PIV agents versus homogeneous and heterogeneous (Luna-worker) teams under PIV guidance, the PIV counterpart of Figure [7](https://arxiv.org/html/2610.17471#S5.F7 "Figure 7 ‣ Why is planning efficient? ‣ 5 Where should workers be utilized? ‣ Scaling Inference-Time Compute with Teams of Coding Agents"). Teams use asynchronous push.

Figure 19: Mean reward (top) and total inference cost (bottom) with workers fixed at Luna and the lead varied across Luna, Terra, and Sol, under blocking (left) and asynchronous push (right). Faint lines show implementation and verification guidance; the gray dotted line is each lead’s Solo PIV agent. Reward error bars are paired 95% intervals relative to each lead’s Solo PIV agent.

### C.5 Run-to-run Variance

Our main results with the GPT 5.6 series (Sol, Terra, Luna) are run and averaged across three independent trials on the full set of 200 ProgramBench tasks.
Figure [20](https://arxiv.org/html/2610.17471#A3.F20 "Figure 20 ‣ C.5 Run-to-run Variance ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents") compares task-level rewards between pairs of runs for six Sol configurations.
Individual task outcomes are noisy; across all five model setups, the same configuration’s reward on a task differs between two runs by 0.057–0.113 on average.
However, rewards remain strongly correlated across runs and benchmark-level means are much more stable (Table [3](https://arxiv.org/html/2610.17471#A3.T3 "Table 3 ‣ C.5 Run-to-run Variance ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents")).
Across the five model setups, the standard deviation of the 200-task mean across runs is at most 0.014.

Figure 20: Task-level reward comparisons between two GPT-5.6 Sol solo agent and teams runs (top: minimal guidance; bottom: PIV guidance). Each panel pools three of runs (600 points total); the dashed diagonal line marks equal reward. Annotations give the mean pairwise correlation, the mean absolute difference, and each run’s 200-task mean.

Table 3: Run-to-run variance for every GPT-5.6 configuration across three runs. All summary statistics are computed over 200-tasks across three runs. Task `|\Delta|` is the mean absolute difference in a single task’s reward between combinations of any two runs; task correlation is the mean pairwise correlation of task rewards between runs.

|  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  |  | Reward | | | | |  |
| Configuration | Schedule | Mean | 95% CI | SD | Range | Task `|\Delta|` | Task correlation |
| Sol lead | | | | | | | |
| Solo minimal | – | 0.521 | `\pm`0.030 | 0.008 | 0.015 | 0.072 | 0.86 |
| Solo PIV | – | 0.577 | `\pm`0.031 | 0.006 | 0.011 | 0.066 | 0.90 |
| with Sol workers | | | | | | | |
| Team minimal | Async | 0.559 | `\pm`0.032 | 0.001 | 0.001 | 0.069 | 0.88 |
|  | Blocking | 0.618 | `\pm`0.033 | 0.005 | 0.010 | 0.072 | 0.89 |
| Team P | Async | 0.636 | `\pm`0.033 | 0.003 | 0.006 | 0.057 | 0.92 |
|  | Blocking | 0.634 | `\pm`0.033 | 0.006 | 0.011 | 0.065 | 0.88 |
| Team I | Async | 0.593 | `\pm`0.031 | 0.002 | 0.005 | 0.064 | 0.90 |
|  | Blocking | 0.596 | `\pm`0.032 | 0.009 | 0.018 | 0.065 | 0.90 |
| Team V | Async | 0.591 | `\pm`0.033 | 0.004 | 0.007 | 0.060 | 0.92 |
|  | Blocking | 0.600 | `\pm`0.033 | 0.003 | 0.005 | 0.059 | 0.92 |
| Team PIV | Async | 0.632 | `\pm`0.033 | 0.005 | 0.010 | 0.057 | 0.92 |
|  | Blocking | 0.631 | `\pm`0.033 | 0.006 | 0.011 | 0.060 | 0.92 |
| with Luna workers | | | | | | | |
| Team minimal | Async | 0.564 | `\pm`0.032 | 0.003 | 0.006 | 0.067 | 0.89 |
|  | Blocking | 0.575 | `\pm`0.032 | 0.002 | 0.005 | 0.066 | 0.90 |
| Team P | Async | 0.605 | `\pm`0.033 | 0.004 | 0.008 | 0.055 | 0.93 |
|  | Blocking | 0.601 | `\pm`0.033 | 0.006 | 0.011 | 0.057 | 0.93 |
| Team I | Async | 0.563 | `\pm`0.031 | 0.001 | 0.001 | 0.067 | 0.90 |
|  | Blocking | 0.564 | `\pm`0.031 | 0.006 | 0.011 | 0.069 | 0.88 |
| Team V | Async | 0.581 | `\pm`0.032 | 0.002 | 0.004 | 0.057 | 0.93 |
|  | Blocking | 0.587 | `\pm`0.032 | 0.007 | 0.013 | 0.058 | 0.92 |
| Team PIV | Async | 0.581 | `\pm`0.032 | 0.004 | 0.008 | 0.067 | 0.87 |
|  | Blocking | 0.569 | `\pm`0.032 | 0.006 | 0.013 | 0.073 | 0.88 |
| Terra lead | | | | | | | |
| Solo minimal | – | 0.452 | `\pm`0.029 | 0.003 | 0.005 | 0.080 | 0.82 |
| Solo PIV | – | 0.471 | `\pm`0.030 | 0.006 | 0.012 | 0.078 | 0.87 |
| with Terra workers | | | | | | | |
| Team minimal | Async | 0.484 | `\pm`0.030 | 0.003 | 0.005 | 0.075 | 0.87 |
|  | Blocking | 0.486 | `\pm`0.030 | 0.004 | 0.008 | 0.089 | 0.82 |
| Team P | Async | 0.515 | `\pm`0.031 | 0.003 | 0.006 | 0.076 | 0.86 |
|  | Blocking | 0.509 | `\pm`0.032 | 0.008 | 0.015 | 0.081 | 0.86 |
| Team I | Async | 0.498 | `\pm`0.030 | 0.003 | 0.007 | 0.089 | 0.82 |
|  | Blocking | 0.491 | `\pm`0.029 | 0.007 | 0.014 | 0.086 | 0.83 |
| Team V | Async | 0.507 | `\pm`0.032 | 0.006 | 0.011 | 0.074 | 0.87 |
|  | Blocking | 0.499 | `\pm`0.031 | 0.009 | 0.016 | 0.076 | 0.85 |
| Team PIV | Async | 0.545 | `\pm`0.033 | 0.002 | 0.004 | 0.066 | 0.91 |
|  | Blocking | 0.536 | `\pm`0.032 | 0.013 | 0.025 | 0.076 | 0.87 |
| with Luna workers | | | | | | | |
| Team minimal | Async | 0.473 | `\pm`0.030 | 0.008 | 0.015 | 0.077 | 0.85 |
|  | Blocking | 0.479 | `\pm`0.031 | 0.006 | 0.012 | 0.083 | 0.86 |
| Team P | Async | 0.516 | `\pm`0.031 | 0.009 | 0.019 | 0.073 | 0.86 |
|  | Blocking | 0.496 | `\pm`0.031 | 0.005 | 0.009 | 0.074 | 0.87 |
| Team I | Async | 0.482 | `\pm`0.030 | 0.004 | 0.008 | 0.078 | 0.85 |
|  | Blocking | 0.482 | `\pm`0.030 | 0.006 | 0.011 | 0.074 | 0.87 |
| Team V | Async | 0.505 | `\pm`0.031 | 0.003 | 0.005 | 0.068 | 0.88 |
|  | Blocking | 0.497 | `\pm`0.031 | 0.006 | 0.012 | 0.071 | 0.87 |
| Team PIV | Async | 0.519 | `\pm`0.031 | 0.005 | 0.010 | 0.078 | 0.86 |
|  | Blocking | 0.505 | `\pm`0.031 | 0.011 | 0.022 | 0.076 | 0.87 |
| Luna lead | | | | | | | |
| Solo minimal | – | 0.347 | `\pm`0.027 | 0.004 | 0.008 | 0.082 | 0.82 |
| Solo PIV | – | 0.374 | `\pm`0.027 | 0.005 | 0.010 | 0.084 | 0.80 |
| with Luna workers | | | | | | | |
| Team minimal | Async | 0.390 | `\pm`0.028 | 0.001 | 0.002 | 0.080 | 0.83 |
|  | Blocking | 0.391 | `\pm`0.028 | 0.002 | 0.005 | 0.091 | 0.80 |
| Team P | Async | 0.425 | `\pm`0.030 | 0.011 | 0.020 | 0.083 | 0.84 |
|  | Blocking | 0.428 | `\pm`0.029 | 0.001 | 0.003 | 0.073 | 0.87 |
| Team I | Async | 0.344 | `\pm`0.028 | 0.006 | 0.011 | 0.101 | 0.77 |
|  | Blocking | 0.355 | `\pm`0.026 | 0.009 | 0.017 | 0.109 | 0.66 |
| Team V | Async | 0.380 | `\pm`0.027 | 0.003 | 0.006 | 0.077 | 0.82 |
|  | Blocking | 0.383 | `\pm`0.027 | 0.011 | 0.019 | 0.078 | 0.83 |
| Team PIV | Async | 0.402 | `\pm`0.028 | 0.014 | 0.024 | 0.113 | 0.68 |
|  | Blocking | 0.404 | `\pm`0.029 | 0.006 | 0.012 | 0.097 | 0.77 |

### C.6 Activity Statistics

Tables [4](https://arxiv.org/html/2610.17471#A3.T4 "Table 4 ‣ C.6 Activity Statistics ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents") and [5](https://arxiv.org/html/2610.17471#A3.T5 "Table 5 ‣ C.6 Activity Statistics ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents") and Figure [21](https://arxiv.org/html/2610.17471#A3.F21 "Figure 21 ‣ C.6 Activity Statistics ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents") summarize how each configuration uses its team.
A solo Sol agent issues 19–22 tool calls per task, whereas teams issue between 44 and 140.
Stage guidance largely determines team size: the lead spawns 2.2 workers on average under implementation guidance, 3.0 under verification, 3.4–3.6 under planning, and 4.2–5.0 under minimal and PIV guidance, where the cap of five unique workers binds.
Persistent workers are reused almost exclusively under PIV, where 38–48% of delegations resume a worker that already holds task context.
Implementation guidance leaves the lead with most of the work, as workers account for only 21% of tokens compared with 46–66% under minimal and PIV guidance.

Figure 21: Per-task team activity for GPT-5.6 Sol teams pooled over three runs. Filled bars denote asynchronous and outlined bars blocking teams. In the delegation panel, the solid part of each bar counts delegations that spawn a new worker (and therefore equals the number of workers spawned), hatching marks delegations that resume an already spawned worker, and the dashed line marks the standard cap of five unique worker agents. In the tool-call panel, dashed lines mark Solo minimal and Solo PIV.

Table 4: Per-task team activity for GPT-5.6 models, grouped by lead model and worker model. All columns are per-task means pooled over three runs. Cost is inference cost per task; the resumed share is the fraction of delegations that resume a previously spawned worker, and the worker token share is the fraction of all tokens generated by workers.

|  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  | Cost | Wall-clock | Tool | Workers |  | Resumed | Worker |
| Configuration | Schedule | Reward | ($) | (min) | calls | spawned | Delegations | share | token share |
| Sol lead | | | | | | | | | |
| Solo minimal | – | 0.52 | 0.24 | 1.9 | 19.2 | 0.0 | 0.0 | – | 0.00 |
| Solo PIV | – | 0.58 | 0.38 | 2.5 | 22.4 | 0.0 | 0.0 | – | 0.00 |
| with Sol workers | | | | | | | | | |
| Team minimal | Async | 0.56 | 0.91 | 2.6 | 84.0 | 4.2 | 4.4 | 0.03 | 0.46 |
|  | Blocking | 0.62 | 1.28 | 6.5 | 96.4 | 4.9 | 6.1 | 0.15 | 0.66 |
| Team P | Async | 0.64 | 1.24 | 5.1 | 85.3 | 3.6 | 3.6 | 0.00 | 0.39 |
|  | Blocking | 0.63 | 1.12 | 4.7 | 70.6 | 3.4 | 3.4 | 0.00 | 0.51 |
| Team I | Async | 0.59 | 0.84 | 4.2 | 50.5 | 2.2 | 2.2 | 0.00 | 0.20 |
|  | Blocking | 0.60 | 0.78 | 4.3 | 44.2 | 2.1 | 2.1 | 0.00 | 0.22 |
| Team V | Async | 0.59 | 1.15 | 5.4 | 70.6 | 3.0 | 3.1 | 0.00 | 0.41 |
|  | Blocking | 0.60 | 1.07 | 5.0 | 60.2 | 3.0 | 3.0 | 0.00 | 0.49 |
| Team PIV | Async | 0.63 | 2.55 | 7.6 | 139.6 | 4.5 | 8.8 | 0.48 | 0.51 |
|  | Blocking | 0.63 | 2.29 | 9.5 | 117.5 | 5.0 | 8.1 | 0.38 | 0.66 |
| with Luna workers | | | | | | | | | |
| Team minimal | Async | 0.56 | 0.36 | 2.3 | 77.7 | 4.3 | 4.7 | 0.07 | 0.45 |
|  | Blocking | 0.58 | 0.31 | 4.2 | 83.2 | 4.9 | 6.1 | 0.16 | 0.62 |
| Team P | Async | 0.60 | 0.50 | 3.3 | 72.6 | 3.6 | 3.6 | 0.00 | 0.35 |
|  | Blocking | 0.60 | 0.40 | 3.7 | 60.6 | 3.4 | 3.4 | 0.00 | 0.45 |
| Team I | Async | 0.56 | 0.45 | 3.5 | 44.9 | 2.2 | 2.2 | 0.00 | 0.17 |
|  | Blocking | 0.56 | 0.43 | 3.5 | 40.8 | 2.1 | 2.1 | 0.01 | 0.18 |
| Team V | Async | 0.58 | 0.48 | 4.4 | 62.8 | 3.1 | 3.1 | 0.00 | 0.36 |
|  | Blocking | 0.59 | 0.44 | 4.2 | 54.3 | 3.0 | 3.0 | 0.00 | 0.44 |
| Team PIV | Async | 0.58 | 0.72 | 4.5 | 118.5 | 4.4 | 8.7 | 0.49 | 0.46 |
|  | Blocking | 0.57 | 0.52 | 6.1 | 98.5 | 5.0 | 8.1 | 0.38 | 0.61 |
| Terra lead | | | | | | | | | |
| Solo minimal | – | 0.45 | 0.13 | 3.1 | 17.7 | 0.0 | 0.0 | – | 0.00 |
| Solo PIV | – | 0.47 | 0.16 | 3.4 | 18.5 | 0.0 | 0.0 | – | 0.00 |
| with Terra workers | | | | | | | | | |
| Team minimal | Async | 0.48 | 0.33 | 2.9 | 48.2 | 3.5 | 3.6 | 0.01 | 0.38 |
|  | Blocking | 0.49 | 0.39 | 5.3 | 59.6 | 4.6 | 4.7 | 0.02 | 0.61 |
| Team P | Async | 0.51 | 0.42 | 5.0 | 62.8 | 3.1 | 3.1 | 0.00 | 0.34 |
|  | Blocking | 0.51 | 0.39 | 4.7 | 51.9 | 3.0 | 3.0 | 0.00 | 0.48 |
| Team I | Async | 0.50 | 0.38 | 4.7 | 41.7 | 2.1 | 2.2 | 0.02 | 0.23 |
|  | Blocking | 0.49 | 0.34 | 5.3 | 33.0 | 2.0 | 2.0 | 0.02 | 0.25 |
| Team V | Async | 0.51 | 0.52 | 6.9 | 54.9 | 3.0 | 3.0 | 0.00 | 0.37 |
|  | Blocking | 0.50 | 0.46 | 6.6 | 45.3 | 3.0 | 3.0 | 0.00 | 0.46 |
| Team PIV | Async | 0.55 | 1.08 | 7.3 | 116.0 | 4.3 | 8.4 | 0.48 | 0.45 |
|  | Blocking | 0.54 | 0.94 | 10.3 | 95.1 | 5.0 | 7.9 | 0.35 | 0.62 |
| with Luna workers | | | | | | | | | |
| Team minimal | Async | 0.47 | 0.16 | 2.5 | 55.8 | 3.6 | 3.7 | 0.02 | 0.42 |
|  | Blocking | 0.48 | 0.13 | 3.3 | 66.7 | 4.7 | 4.8 | 0.02 | 0.64 |
| Team P | Async | 0.52 | 0.20 | 3.3 | 56.6 | 3.1 | 3.1 | 0.00 | 0.37 |
|  | Blocking | 0.50 | 0.16 | 3.0 | 52.8 | 3.0 | 3.0 | 0.00 | 0.51 |
| Team I | Async | 0.48 | 0.20 | 4.2 | 38.6 | 2.1 | 2.1 | 0.02 | 0.19 |
|  | Blocking | 0.48 | 0.19 | 4.2 | 32.5 | 2.0 | 2.1 | 0.03 | 0.21 |
| Team V | Async | 0.51 | 0.25 | 4.9 | 57.3 | 3.0 | 3.0 | 0.00 | 0.36 |
|  | Blocking | 0.50 | 0.20 | 5.1 | 48.4 | 3.0 | 3.0 | 0.00 | 0.46 |
| Team PIV | Async | 0.52 | 0.37 | 5.0 | 114.7 | 4.3 | 8.4 | 0.48 | 0.46 |
|  | Blocking | 0.50 | 0.26 | 5.9 | 94.8 | 5.0 | 7.9 | 0.35 | 0.62 |
| Luna lead | | | | | | | | | |
| Solo minimal | – | 0.35 | 0.01 | 1.2 | 16.0 | 0.0 | 0.0 | – | 0.00 |
| Solo PIV | – | 0.37 | 0.01 | 1.3 | 17.7 | 0.0 | 0.0 | – | 0.00 |
| with Luna workers | | | | | | | | | |
| Team minimal | Async | 0.39 | 0.03 | 1.6 | 63.6 | 3.1 | 3.1 | 0.00 | 0.46 |
|  | Blocking | 0.39 | 0.03 | 2.5 | 65.9 | 3.7 | 3.8 | 0.03 | 0.60 |
| Team P | Async | 0.43 | 0.04 | 2.1 | 72.7 | 3.5 | 3.5 | 0.00 | 0.45 |
|  | Blocking | 0.43 | 0.04 | 2.3 | 68.0 | 3.4 | 3.4 | 0.00 | 0.53 |
| Team I | Async | 0.34 | 0.03 | 2.4 | 47.6 | 2.4 | 2.4 | 0.01 | 0.35 |
|  | Blocking | 0.36 | 0.02 | 2.8 | 34.2 | 1.8 | 1.8 | 0.01 | 0.33 |
| Team V | Async | 0.38 | 0.03 | 2.7 | 56.6 | 3.0 | 3.0 | 0.00 | 0.45 |
|  | Blocking | 0.38 | 0.03 | 2.6 | 51.2 | 3.0 | 3.0 | 0.00 | 0.50 |
| Team PIV | Async | 0.40 | 0.07 | 3.8 | 111.9 | 4.9 | 7.1 | 0.30 | 0.51 |
|  | Blocking | 0.40 | 0.06 | 4.1 | 100.2 | 5.0 | 7.2 | 0.27 | 0.66 |

Table 5: Per-task team activity for Claude models on the full 200-task ProgramBench run (single run; same columns as Table [4](https://arxiv.org/html/2610.17471#A3.T4 "Table 4 ‣ C.6 Activity Statistics ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents")).

|  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  | Cost | Wall-clock | Tool | Workers |  | Resumed | Worker |
| Configuration | Schedule | Reward | ($) | (min) | calls | spawned | Delegations | share | token share |
| Claude Opus 4.7 lead | | | | | | | | | |
| Solo minimal | – | 0.51 | 2.81 | 9.6 | 59.0 | 0.0 | 0.0 | – | 0.00 |
| Solo PIV | – | 0.49 | 2.47 | 8.9 | 56.1 | 0.0 | 0.0 | – | 0.00 |
| with Opus 4.7 workers | | | | | | | | | |
| Team minimal | Async | 0.51 | 3.23 | 11.3 | 69.1 | 0.4 | 0.4 | 0.05 | 0.24 |
|  | Blocking | 0.51 | 2.70 | 9.8 | 61.7 | 0.3 | 0.4 | 0.08 | 0.22 |
| Team P | Async | 0.52 | 3.72 | 13.6 | 72.5 | 0.4 | 0.4 | 0.00 | 0.02 |
|  | Blocking | 0.52 | 3.67 | 13.2 | 73.4 | 0.6 | 0.6 | 0.00 | 0.05 |
| Team I | Async | 0.50 | 2.58 | 10.2 | 55.6 | 0.0 | 0.0 | – | 0.01 |
|  | Blocking | 0.51 | 2.93 | 11.8 | 60.4 | 0.1 | 0.1 | – | 0.03 |
| Team V | Async | 0.54 | 5.16 | 17.0 | 104.2 | 1.7 | 1.8 | 0.06 | 0.07 |
|  | Blocking | 0.53 | 4.64 | 17.5 | 97.2 | 1.6 | 1.6 | 0.03 | 0.07 |
| Team PIV | Async | 0.54 | 4.09 | 12.9 | 80.3 | 0.8 | 0.8 | 0.03 | 0.08 |
|  | Blocking | 0.56 | 4.93 | 16.6 | 94.8 | 1.3 | 1.4 | 0.04 | 0.21 |
| Claude Haiku 4.5 lead | | | | | | | | | |
| Solo minimal | – | 0.36 | 1.40 | 16.9 | 169.0 | 0.0 | 0.0 | – | 0.00 |
| Solo PIV | – | 0.37 | 1.47 | 17.1 | 170.6 | 0.0 | 0.0 | – | 0.00 |
| with Haiku 4.5 workers | | | | | | | | | |
| Team minimal | Async | 0.36 | 2.79 | 29.2 | 321.0 | 3.1 | 3.8 | 0.14 | 0.37 |
|  | Blocking | 0.32 | 3.25 | 39.6 | 363.7 | 3.6 | 4.5 | 0.14 | 0.52 |
| Team P | Async | 0.36 | 2.38 | 22.6 | 301.9 | 3.7 | 3.7 | 0.00 | 0.29 |
|  | Blocking | 0.34 | 2.34 | 31.2 | 281.8 | 3.7 | 3.7 | 0.00 | 0.32 |
| Team I | Async | 0.35 | 2.99 | 24.2 | 355.6 | 2.7 | 3.1 | 0.06 | 0.35 |
|  | Blocking | 0.34 | 2.82 | 34.1 | 314.4 | 2.5 | 3.4 | 0.17 | 0.37 |
| Team V | Async | 0.37 | 2.26 | 23.8 | 272.8 | 2.5 | 2.7 | 0.02 | 0.15 |
|  | Blocking | 0.37 | 2.21 | 29.6 | 254.7 | 2.5 | 2.6 | 0.03 | 0.17 |
| Team PIV | Async | 0.34 | 2.91 | 27.4 | 358.9 | 4.8 | 5.0 | 0.02 | 0.35 |
|  | Blocking | 0.34 | 2.97 | 41.3 | 355.0 | 4.9 | 5.0 | 0.01 | 0.39 |

### C.7 Where teams add reward: task difficulty

We compare each team with the solo agent that receives matching guidance: minimal teams with the minimally prompted solo agent, and stage-guided teams (P, I, V, and PIV) with the solo agent given the full plan–implement–verify prompt.
Across configurations, the lift generally decreases from easy to hard tasks.
The one exception is for Implementation guidance, where the trend reverses, and we observe the team generally performing worst on the easy tasks.

Figure 22: Lift by difficulty tier for asynchronous Team minimal (relative to Solo minimal) and Team PIV (relative to Solo PIV), for all model setups. Lighter shades (leftwards in each group) denote easier tiers; error bars are 95% intervals over tasks.

Figure 23: Lift by difficulty tier for asynchronous Team P, I, V, and PIV relative to Solo PIV, for all model setups.

### C.8 Why implementation and verification plateau

In the fixed-size runs (Figure [8](https://arxiv.org/html/2610.17471#S7.F8 "Figure 8 ‣ 7 How Many Workers Should a Team Have? ‣ Scaling Inference-Time Compute with Teams of Coding Agents")), planning is the only stage whose reward monotonically grows with team size (`+2.2` points, 95% CI `[+1.0,+3.5]` from two to sixteen workers). Implementation and verification improve from two to four workers and then plateau. From four to sixteen workers they change by `-1.5` points, 95% CI `[-3.4,+0.4]` and `-1.1` points, 95% CI `[-2.6,+0.3]`, respectively.

Figure [24](https://arxiv.org/html/2610.17471#A3.F24 "Figure 24 ‣ C.8 Why implementation and verification plateau ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents") shows how work is divided as teams grow. Explicit coordination failures are rare: implementers almost never write the same file (0.1% of their files), and worker reports become less similar as the team grows. What differs is what an additional worker contributes. Each planner runs the reference executable about seven times regardless of team size, so the information returned to the lead grows with the team (15 to 109 reference runs and 17k to 75k characters of reports from two to sixteen workers), while the Sol lead still writes essentially all of the code. Adding implementers instead subdivides a fixed plan: the lead explores for the same number of turns before delegating, each worker’s assignment shrinks from 1.4k to 0.4k characters, implementers barely consult the reference (about one run each), and the share of source edits made by the Luna workers rises from 54% to 85%. The lead’s final check does not grow to match: it runs the reference five to six times after the last report whether it integrates two modules or sixteen. Verifiers show a similar dilution: total checks grow, but each verifier receives a shorter assignment and runs the reference less (8.1 to 4.7 times), and the lead’s edits in response to verifier reports peak at four workers, as does reward. Beyond four workers, additional implementers and verifiers therefore appear to shift work toward the weaker model without increasing the information or checking that reaches the combined program.

Figure 24: How work is divided as fixed-size teams grow (asynchronous Team P, I, V, and PIV; Sol lead with 2–16 Luna workers). Panels show the length of each worker’s assignment, files written by workers, total runs of the reference executable by workers, total report text returned to the lead, pairwise report similarity (word-set Jaccard; higher means more alike), and the lead’s runs of the reference executable after the last worker report. Files and reference runs are detected from shell commands, so file counts are lower bounds.

### C.9 Raising the worker cap

Raising the cap on unique workers from five to twenty changes how the lead delegates but not how well the team performs (Figure [25](https://arxiv.org/html/2610.17471#A3.F25 "Figure 25 ‣ C.9 Raising the worker cap ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents")).
Under minimal guidance the lead rarely approaches the original cap and spawns at most 0.7 additional workers per task.
Under PIV guidance it spawns 2.2–3.0 additional workers, but mostly in place of resuming existing ones.
Delegations to previously spawned workers fall by 2.0–2.9 per task, so the total number of delegations changes by at most 0.9.
Relative to the mean of three runs at the default worker cap, reward changes by `-1.6` to `+1.6` points. 8 of the 10 differences lie within their 95% interval of zero.
Cost, however, tends to rise.
Relative to the default cap, cost per task increases by 5–17% in 7 of the 10 settings (95% intervals exclude zero), well beyond the run-to-run variation in cost at the default cap.
Raising the cap therefore appears to add cost without improving reward, and the default of five does not constrain the dynamically sized teams.

Figure 25: Change from a cap of five unique workers (mean of three runs) to twenty (one run) for asynchronous teams. Cost is shown as the percentage change in mean cost per task. Error bars on reward and cost are 95% intervals over tasks, paired by task.

### C.10 Peer-to-peer messaging

In runs where every agent had access to a send_message tool, workers mainly use it to report to the lead (6.8–14.2 messages per task) rather than to coordinate with one another (at most 0.7 messages per task; Figure [26](https://arxiv.org/html/2610.17471#A3.F26 "Figure 26 ‣ C.10 Peer-to-peer messaging ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents") and Table [6](https://arxiv.org/html/2610.17471#A3.T6 "Table 6 ‣ C.10 Peer-to-peer messaging ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents")).
Under minimal guidance these reports arrive near the end of a worker’s trajectory (median 82% of the way through for Sol), shortly before the harness returns the worker’s outcome anyway; under PIV guidance they arrive mid-task (median 61%) and carry interim findings, verification failures, and questions.

We count a message as a question if it contains a sentence ending in “?” outside code, and say the lead replied if it messages that worker before the worker sends anything else.

Under PIV guidance, Sol’s lead replies to 74% of worker questions, typically within seconds.
The most common question is where to find the reference executable once a worker’s build has overwritten ./executable, which the lead answers by pointing to /opt/reference-executable.
Leads of teams with Luna workers reply to 9–20% of questions.
An additional worker instruction encouraging collaboration (Peer Plus: “Treat other active agents as collaborators within a shared workspace…”) raises worker-to-worker messages only modestly, from 0.7 to 1.0 per task for Sol and from 0.3 to 0.5 for Terra, and not at all for teams with Luna workers.

Messaging leaves Sol teams unchanged but lowers reward for teams with Luna workers, most clearly Luna (`-7.1` points) and Terra + Luna (`-3.5`).

Luna workers frequently misuse the tool: about half of their send_message calls are rejected by the harness, typically because the recipient is passed under the wrong argument name or addressed to an agent that does not exist (e.g., agent_lead), whereas at most 1% of Sol and Terra worker calls fail.
Claude Opus 4.7 and Haiku 4.5 teams send far fewer messages on average, at most 4.6 messages per task with the tool enabled.

Figure 26: Left: messages per task by direction when a send_message tool is available, for asynchronous Team minimal and Team PIV. Right: change in reward relative to the same team without the tool, with 95% intervals paired by task. Row configurations are aligned across panels.

Table 6: Peer messaging for asynchronous teams under PIV guidance (cap of five workers). Messages per task count delivered messages from workers to the lead (W`\to`L), from the lead to workers (L`\to`W), and between workers (W`\to`W); Plus adds a worker instruction encouraging collaboration. Questions replied is the share of worker questions to which the lead messages that worker before the worker sends anything else. Failed calls is the share of worker send_message calls rejected by the harness. `\Delta` reward is the change relative to the same team without the tool, in points, with paired 95% intervals.

|  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  | Messages per task | | | | Questions | Failed |  |
| Setup | W`\to`L | L`\to`W | W`\to`W | W`\to`W (Plus) | replied | calls | `\Delta` reward |
| Sol | 14.2 | 2.0 | 0.7 | 1.0 | 74% | 1% | `+0.4\pm 1.2` |
| Sol + Luna | 12.4 | 1.2 | 0.2 | 0.3 | 16% | 55% | `-1.3\pm 1.2` |
| Terra | 11.7 | 1.3 | 0.3 | 0.5 | 28% | 0% | `-1.4\pm 1.5` |
| Terra + Luna | 12.8 | 1.2 | 0.3 | 0.3 | 20% | 50% | `-3.5\pm 1.5` |
| Luna | 10.4 | 0.2 | 0.3 | 0.2 | 9% | 50% | `-7.1\pm 2.3` |

### C.11 Comparison between additional model families

To test whether these patterns depend on the GPT-5.6 family, we compare four additional models on a 30-task subset of ProgramBench built by randomly sampling 10 easy, 10 medium, and 10 hard tasks.
With identical tools and prompts, different models delegate very differently (Figure [27](https://arxiv.org/html/2610.17471#A3.F27 "Figure 27 ‣ C.11 Comparison between additional model families ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents")).
GPT-5.6 teams spawn 3.1–5.0 workers per task and gain 2.6–8.9 points over the matching solo agent.
Claude Opus 4.7 rarely delegates, spawning 0.3 workers per task under minimal guidance and at most 1.3 under PIV.
Claude Haiku 4.5 and Gemini 3.7 Flash delegate as readily as the GPT-5.6 series (4.8 workers each under asynchronous PIV) but gain nothing from doing so (`-4.0` and `-0.6` points).
Claude Opus 4.8 delegates and benefits, gaining 5.9 points under asynchronous PIV, at 2.3 times the solo cost.
Gemini 3.8 Flash likewise delegates mainly under PIV guidance (1.3 workers under minimal guidance, 4.6–4.7 under PIV), but unlike Gemini 3.7 Flash it gains modestly from blocking teams (+2.1 and +3.1 under minimal and PIV guidance).
Additional capacity therefore helps only when the lead both chooses to delegate and can use what its workers return.

Figure 27: Balanced-30 comparison across model families. Left: solo and best-team mean reward. Middle: team lift over the solo agent with matching guidance (Solo minimal for Team minimal, Solo PIV for Team PIV). Right: workers spawned and delegations issued per task; the cap of five unique workers bounds the former but not the latter. Filled bars denote asynchronous and outlined bars blocking teams.

### C.12 How models structure their code

Model families also differ in the types of implementations they write (Figure [28](https://arxiv.org/html/2610.17471#A3.F28 "Figure 28 ‣ C.12 How models structure their code ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents")).
Across all 200 tasks, GPT-5.6 solo agents submit a median of one source file, written in Python for 86–92% of tasks, regardless of the language of the original program.
Claude Opus 4.7 and Haiku 4.5 instead attempt to reimplement the program in its original language in 69–82% of tasks.
On the 30-task subset (introduced in [C.11](https://arxiv.org/html/2610.17471#A3.SS11 "C.11 Comparison between additional model families ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents")), Claude Opus 4.8 and Gemini 3.7 and 3.8 Flash produce a median of 5–7 source files even without a team.
Teams change file structure much more than language.
GPT-5.6 series teams keep writing Python, but teams with heavy PIV guidance split the program into a median of 3 files.

Figure 28: Submission structure on the 30 task subset for Solo minimal, Team minimal, Solo PIV, and Team PIV (teams asynchronous). Top: share of submissions whose dominant source language (by bytes) is the original program’s language, Python, or another language. Bottom: median number of source files (i.e. excluding benchmark-requested files such as compile.sh).

### C.13 Commit0

We also evaluate on Commit0-Lite, a benchmark comprised of 16 Python libraries that an agent is asked to reimplement given a repository skeleton and a set of unit tests (Figures [29](https://arxiv.org/html/2610.17471#A3.F29 "Figure 29 ‣ C.13 Commit0 ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents")–[30](https://arxiv.org/html/2610.17471#A3.F30 "Figure 30 ‣ C.13 Commit0 ‣ Appendix C Additional Experimental Details ‣ Scaling Inference-Time Compute with Teams of Coding Agents")).
Implementation guidance is the most effective single-stage prompt in eight of ten settings, while planning, the most efficient stage on ProgramBench, is never clearly best.
We attribute this to what each benchmark gives the agent.
A Commit0 task ships the repository’s file layout and function stubs, which act as an already decomposed plan.
The repository’s unit tests are also provided in full to the agent, so there is effectively little left to discover and verification is cheap.
What remains is filling in many independent functions, which parallelizes naturally across implementers.
ProgramBench provides only a black-box executable, so the specification itself must be discovered first.
Because Commit0-lite has only 16 tasks and one run per configuration, confidence intervals are wide and these differences are directional.
Additionally, frontier models (e.g. GPT 5.6 Sol) have already begun to saturate the benchmark (achieving a perfect reward of `1` on 12 of 16 tasks), resulting in little insight to be gained from comparing Solo and Team configurations.

Figure 29: Commit0-Lite lift of Team minimal over Solo minimal and of Team PIV over Solo PIV. Filled bars denote asynchronous and outlined bars blocking teams. Error bars are 95% normal intervals of the paired per-task differences over the 16 tasks.

Figure 30: Commit0-Lite lift of Team P, I, V, and PIV over Solo PIV, for asynchronous (left) and blocking (right) teams. Error bars are 95% normal intervals of the paired per-task differences over the 16 tasks.

## Appendix D Prompts and Tool Definitions

### D.1 Minimal System Prompts

The minimal solo condition receives no additional orchestration preamble.
Blocking and asynchronous teams use the following lead prompts.
Both use the same worker prompt.

[⬇](data:text/plain;base64,V29yayBhcyB0aGUgbGVhZCBvZiBhIHRlYW0gb2YgZW5naW5lZXJzLiBVc2UgdGhlIGBkZWxlZ2F0ZV9hZ2VudGAgdG9vbCB0byBhc3NpZ24gc3ViLWFnZW50cyBkaXN0aW5jdCwgaW5kZXBlbmRlbnQgdGFza3MgdGhhdCB3aWxsIG5vdCBjb25mbGljdCB3aXRoIG9uZSBhbm90aGVyLiBTdWItYWdlbnRzIHJ1biBzeW5jaHJvbm91c2x5OiBlYWNoIGBkZWxlZ2F0ZV9hZ2VudGAgY2FsbCBibG9ja3MgdW50aWwgdGhlIHN1Yi1hZ2VudCBjb21wbGV0ZXMgYW5kIHJldHVybnMgaXRzIGZpbmFsIHJlc3BvbnNlIGRpcmVjdGx5IHRvIHlvdS4gVG8gcnVuIHN1Yi1hZ2VudHMgaW4gcGFyYWxsZWwsIGlzc3VlIHRoZSBgZGVsZWdhdGVfYWdlbnRgIGNhbGxzIGluIHRoZSBzYW1lIHR1cm4uCgpFYWNoIGBkZWxlZ2F0ZV9hZ2VudGAgY2FsbCByZXR1cm5zIHRoZSBzdWItYWdlbnQncyBmaW5hbCByZXNwb25zZSBhbG9uZyB3aXRoIGFuIGBhZ2VudF9pZGAuIE9uY2UgdGhhdCBhZ2VudCByZXBvcnRzIGJhY2ssIHlvdSBtYXkgZGVsZWdhdGUgbW9yZSB3b3JrIHRvIGl0IGJ5IGluY2x1ZGluZyBpdHMgSUQgaW4gYSBuZXcgYGRlbGVnYXRlX2FnZW50YCBjYWxsLiBSZXVzaW5nIGFuIGFnZW50IHByZXNlcnZlcyBpdHMgY29udGV4dDsgY3JlYXRpbmcgYSBuZXcgYWdlbnQgcHJvdmlkZXMgZnJlc2ggY29udGV4dC4gQ2hvb3NlIHdoaWNoZXZlciBpcyBtb3JlIHVzZWZ1bCBmb3IgdGhlIHRhc2sgYXQgYW55IGdpdmVuIHRpbWUu)

Work as the lead of a team of engineers. Use the ‘delegate_agent‘ tool to assign sub-agents distinct, independent tasks that will not conflict with one another. Sub-agents run synchronously: each ‘delegate_agent‘ call blocks until the sub-agent completes and returns its final response directly to you. To run sub-agents in parallel, issue the ‘delegate_agent‘ calls in the same turn.

Each ‘delegate_agent‘ call returns the sub-agent’s final response along with an ‘agent_id‘. Once that agent reports back, you may delegate more work to it by including its ID in a new ‘delegate_agent‘ call. Reusing an agent preserves its context; creating a new agent provides fresh context. Choose whichever is more useful for the task at any given time.

[⬇](data:text/plain;base64,V29yayBhcyB0aGUgbGVhZCBvZiBhIHRlYW0gb2YgZW5naW5lZXJzLiBVc2UgdGhlIGBkZWxlZ2F0ZV9hZ2VudGAgdG9vbCB0byBhc3NpZ24gc3ViLWFnZW50cyBkaXN0aW5jdCwgaW5kZXBlbmRlbnQgdGFza3MgdGhhdCB3aWxsIG5vdCBjb25mbGljdCB3aXRoIG9uZSBhbm90aGVyLiBTdWItYWdlbnRzIHJ1biBhc3luY2hyb25vdXNseSwgc28gY29udGludWUgcGxhbm5pbmcsIHVzaW5nIHRvb2xzLCBhbmQgbWFraW5nIHByb2dyZXNzIHdoaWxlIHRoZXkgd29yay4KCldoZW4geW91IGhhdmUgbm8gb3RoZXIgdXNlZnVsIHdvcmsgdG8gZG8sIHVzZSB0aGUgYHdhaXRfZm9yX3VwZGF0ZXNgIHRvb2wgdG8gYmxvY2sgdW50aWwgYSBzdWItYWdlbnQgZmluaXNoZXMgYW5kIHJlcG9ydHMgaXRzIGZpbmRpbmdzLiBVc2UgdGhlIGBsaXN0X2FnZW50c2AgdG9vbCB0byBjaGVjayB0aGVpciBzdGF0dXMgYXQgYW55IHRpbWUgd2l0aG91dCBibG9ja2luZy4KCkVhY2ggYGRlbGVnYXRlX2FnZW50YCBjYWxsIHJldHVybnMgYW4gYGFnZW50X2lkYC4gT25jZSB0aGF0IGFnZW50IHJlcG9ydHMgYmFjaywgeW91IG1heSBkZWxlZ2F0ZSBtb3JlIHdvcmsgdG8gaXQgYnkgaW5jbHVkaW5nIGl0cyBJRCBpbiBhIG5ldyBgZGVsZWdhdGVfYWdlbnRgIGNhbGwuIFJldXNpbmcgYW4gYWdlbnQgcHJlc2VydmVzIGl0cyBjb250ZXh0OyBjcmVhdGluZyBhIG5ldyBhZ2VudCBwcm92aWRlcyBmcmVzaCBjb250ZXh0LiBDaG9vc2Ugd2hpY2hldmVyIGlzIG1vcmUgdXNlZnVsIGZvciB0aGUgdGFzayBhdCBhbnkgZ2l2ZW4gdGltZS4=)

Work as the lead of a team of engineers. Use the ‘delegate_agent‘ tool to assign sub-agents distinct, independent tasks that will not conflict with one another. Sub-agents run asynchronously, so continue planning, using tools, and making progress while they work.

When you have no other useful work to do, use the ‘wait_for_updates‘ tool to block until a sub-agent finishes and reports its findings. Use the ‘list_agents‘ tool to check their status at any time without blocking.

Each ‘delegate_agent‘ call returns an ‘agent_id‘. Once that agent reports back, you may delegate more work to it by including its ID in a new ‘delegate_agent‘ call. Reusing an agent preserves its context; creating a new agent provides fresh context. Choose whichever is more useful for the task at any given time.

[⬇](data:text/plain;base64,WW91IGFyZSBhIGhlbHBlciBhZ2VudC4gQ29tcGxldGUgdGhlIHRhc2sgZGVsZWdhdGVkIGJ5IHRoZSBsZWFkLiBTdGF5IHdpdGhpbiBpdHMgc2NvcGUsIGF2b2lkIGNvbmZsaWN0aW5nIHdpdGggb3RoZXIgYWdlbnRzLCBhbmQgcmVwb3J0IGNvbmNyZXRlIGZpbmRpbmdzLCBjaGFuZ2VzLCBhbmQgY2hlY2tzIHdoZW4gZmluaXNoZWQuIERvIG5vdCBhc3N1bWUgdGhhdCB0aGUgbGVhZCBzaGFyZXMgeW91ciBjb250ZXh0Lg==)

You are a helper agent. Complete the task delegated by the lead. Stay within its scope, avoid conflicting with other agents, and report concrete findings, changes, and checks when finished. Do not assume that the lead shares your context.

### D.2 Heavy System Prompts

[⬇](data:text/plain;base64,Q29tcGxldGUgdGhlIHRhc2sgaW4gdGhyZWUgcGhhc2VzOiBwbGFuIGFuZCBleHBsb3JlLCBpbXBsZW1lbnQsIHRoZW4gdmVyaWZ5LgoKIyMgMS4gUGxhbiBhbmQgZXhwbG9yZQoKQmVmb3JlIGJlZ2lubmluZyBzdWJzdGFudGlhbCBpbXBsZW1lbnRhdGlvbiwgaW5zcGVjdCB0aGUgdGFzayByZXF1aXJlbWVudHMsIHJlbGV2YW50IGRvY3VtZW50YXRpb24sIGFuZCBhdmFpbGFibGUgZXZpZGVuY2UuIEludmVzdGlnYXRlOgoKLSByZXF1aXJlbWVudHMsIGFyY2hpdGVjdHVyZSwgaW50ZXJmYWNlcywgYW5kIGV4aXN0aW5nIGJlaGF2aW9yOwotIG1ham9yIGZlYXR1cmVzIGFuZCByZXByZXNlbnRhdGl2ZSB3b3JrZmxvd3M7Ci0gZWRnZSBjYXNlcywgZmFpbHVyZSBtb2RlcywgY29tcGF0aWJpbGl0eSBjb25zdHJhaW50cywgYW5kIHNpZGUgZWZmZWN0czsKLSBpbXBsZW1lbnRhdGlvbiByaXNrcyBhbmQgbGlrZWx5IHByaW9yaXRpZXMgZ3JvdW5kZWQgaW4gZXZpZGVuY2UuCgpUcmVhdCBvYnNlcnZhdGlvbnMgYXMgZXZpZGVuY2UgcmF0aGVyIHRoYW4gYXNzdW1pbmcgY29udmVudGlvbmFsIGJlaGF2aW9yLiBSZWNvbmNpbGUgaW5jb25zaXN0ZW5jaWVzIGFuZCBzeW50aGVzaXplIGEgcHJpb3JpdGl6ZWQgaW1wbGVtZW50YXRpb24gcGxhbiBjb3ZlcmluZyB0aGUgcmVxdWlyZW1lbnRzIHRvIHNhdGlzZnksIHByb3Bvc2VkIHN0cnVjdHVyZSwgdW5jZXJ0YWluIGFyZWFzLCBhbmQgdmVyaWZpY2F0aW9uIHRhcmdldHMuCgojIyAyLiBJbXBsZW1lbnRhdGlvbgoKQWZ0ZXIgZm9ybWluZyB0aGUgcGxhbiwgaW1wbGVtZW50IGl0IGluIGNvaGVyZW50IHVuaXRzIHdpdGggY2xlYXIgaW50ZXJmYWNlcyBhbmQgaW52YXJpYW50cy4gUHJpb3JpdGl6ZSBicm9hZCwgY29ycmVjdCBiZWhhdmlvcmFsIGNvdmVyYWdlIGJlZm9yZSBsb3ctdmFsdWUgZGV0YWlscy4gUnVuIGZvY3VzZWQgdGVzdHMgb3IgYWNjZXB0YW5jZSBjaGVja3MgYXMgeW91IGJ1aWxkLCByZXZpc2UgdGhlIHBsYW4gd2hlbiBpbXBsZW1lbnRhdGlvbiByZXZlYWxzIG5ldyBldmlkZW5jZSwgYW5kIGF2b2lkIGRyaWZ0aW5nIGludG8gdW5yZWxhdGVkIHdvcmsuCgojIyAzLiBWZXJpZmljYXRpb24KCk9ubHkgYWZ0ZXIgdGhlIGltcGxlbWVudGF0aW9uIGlzIGNvaGVyZW50IGFuZCBwYXNzZXMgYmFzaWMgY2hlY2tzLCBwZXJmb3JtIGEgZGlzdGluY3QgYWR2ZXJzYXJpYWwgdmVyaWZpY2F0aW9uIHBhc3MuIENvdmVyOgoKLSByZXF1aXJlbWVudHMgYW5kIHJlcHJlc2VudGF0aXZlIGVuZC10by1lbmQgd29ya2Zsb3dzOwotIGJvdW5kYXJ5IGNvbmRpdGlvbnMsIGZhaWx1cmUgbW9kZXMsIGVycm9yIGhhbmRsaW5nLCBjb21wYXRpYmlsaXR5LCBhbmQgc2lkZSBlZmZlY3RzOwotIGNvbXBvbmVudCBpbnRlcmFjdGlvbnMsIHN0YXRlZnVsIGJlaGF2aW9yLCBjb25jdXJyZW5jeSwgYW5kIG5vbmRldGVybWluaXNtOwotIHNvdXJjZSByZXZpZXcgdGFyZ2V0ZWQgYXQgYmVoYXZpb3IgdGhhdCBtYXkgYmUgc3R1YmJlZCwgb3ZlcnNpbXBsaWZpZWQsIG9yIG1pc3NpbmcuCgpWYWxpZGF0ZSB0aGUgaW1wbGVtZW50YXRpb24gYWdhaW5zdCB0aGUgcmVxdWlyZW1lbnRzIGFuZCBhdmFpbGFibGUgZXZpZGVuY2UsIGNhcHR1cmluZyBleGFjdCByZXByb2R1Y3Rpb24gc3RlcHMgYW5kIG9ic2VydmFibGUgZGlmZmVyZW5jZXMgd2hlbiByZWxldmFudC4gVHJlYXQgc3VzcGVjdGVkIGRlZmVjdHMgYXMgaHlwb3RoZXNlcyB1bnRpbCByZXByb2R1Y2VkLiBGaXggY29uY3JldGUgZGlzY3JlcGFuY2llcywgcmVydW4gdGhlIGFmZmVjdGVkIGNoZWNrcywgYW5kIGZpbmlzaCBieSBydW5uaW5nIHRoZSByZWxldmFudCB2YWxpZGF0aW9uIHN1aXRlIGZyb20gYSBjbGVhbiBzdGF0ZS4=)

Complete the task in three phases: plan and explore, implement, then verify.

## 1. Plan and explore

Before beginning substantial implementation, inspect the task requirements, relevant documentation, and available evidence. Investigate:

- requirements, architecture, interfaces, and existing behavior;

- major features and representative workflows;

- edge cases, failure modes, compatibility constraints, and side effects;

- implementation risks and likely priorities grounded in evidence.

Treat observations as evidence rather than assuming conventional behavior. Reconcile inconsistencies and synthesize a prioritized implementation plan covering the requirements to satisfy, proposed structure, uncertain areas, and verification targets.

## 2. Implementation

After forming the plan, implement it in coherent units with clear interfaces and invariants. Prioritize broad, correct behavioral coverage before low-value details. Run focused tests or acceptance checks as you build, revise the plan when implementation reveals new evidence, and avoid drifting into unrelated work.

## 3. Verification

Only after the implementation is coherent and passes basic checks, perform a distinct adversarial verification pass. Cover:

- requirements and representative end-to-end workflows;

- boundary conditions, failure modes, error handling, compatibility, and side effects;

- component interactions, stateful behavior, concurrency, and nondeterminism;

- source review targeted at behavior that may be stubbed, oversimplified, or missing.

Validate the implementation against the requirements and available evidence, capturing exact reproduction steps and observable differences when relevant. Treat suspected defects as hypotheses until reproduced. Fix concrete discrepancies, rerun the affected checks, and finish by running the relevant validation suite from a clean state.

[⬇](data:text/plain;base64,V29yayBhcyB0aGUgbGVhZCBvZiBhIHRlYW0gb2YgZW5naW5lZXJzLiBDb21wbGV0ZSB0aGUgdGFzayBpbiB0aHJlZSBwaGFzZXM6IHBsYW4gYW5kIGV4cGxvcmUsIGltcGxlbWVudCwgdGhlbiB2ZXJpZnkuIFVzZSBzdWItYWdlbnRzIGR1cmluZyBhbGwgdGhyZWUgcGhhc2VzLgoKU3ViLWFnZW50cyBydW4gYXN5bmNocm9ub3VzbHkuIENhbGwgYGRlbGVnYXRlX2FnZW50YCBmb3IgY29uY3VycmVudCBhc3NpZ25tZW50cyBiZWZvcmUgd2FpdGluZyBmb3IgYW55IG9uZSByZXN1bHQsIGFuZCBjb250aW51ZSB1c2VmdWwgbm9uLWNvbmZsaWN0aW5nIHdvcmsgd2hpbGUgdGhleSBydW4uIEl0IHJldHVybnMgYW4gYGFnZW50X2lkYDsgcmV0YWluIHRoYXQgSUQgd2hlbiB0aGUgc2FtZSB3b3JrZXIncyBjb250ZXh0IG1heSBiZSB1c2VmdWwgaW4gYSBsYXRlciBwaGFzZSBvciBmb2xsb3ctdXAuIFVzZSBgbGlzdF9hZ2VudHNgIHRvIGluc3BlY3Qgc3RhdHVzIGFuZCB1bnJlYWQgb3V0Y29tZXMuIFVzZSBgd2FpdF9mb3JfdXBkYXRlc2Agb25seSB3aGVuIG5vIHByb2R1Y3RpdmUgaW5kZXBlbmRlbnQgd29yayByZW1haW5zIG9yIGEgcmVzdWx0IGlzIHJlcXVpcmVkIHRvIHByb2NlZWQuCgojIyAxLiBQbGFuIGFuZCBleHBsb3JlCgpPcmllbnQgeW91cnNlbGYgYnJpZWZseSwgdGhlbiBkZWxlZ2F0ZSBjb21wbGVtZW50YXJ5IHBsYW5uaW5nIGFuZCBleHBsb3JhdGlvbiB0YXNrcyBiZWZvcmUgYmVnaW5uaW5nIHN1YnN0YW50aWFsIGltcGxlbWVudGF0aW9uLiBVc2VmdWwgZGl2aXNpb25zIG1heSBpbmNsdWRlOgoKLSByZXF1aXJlbWVudHMsIGNvZGViYXNlLCBhcmNoaXRlY3R1cmUsIGFuZCBpbnRlcmZhY2UgbWFwcGluZzsKLSBzeXN0ZW1hdGljIGludmVzdGlnYXRpb24gb2YgbWFqb3IgZmVhdHVyZXMgYW5kIHdvcmtmbG93czsKLSBlZGdlIGNhc2VzLCBmYWlsdXJlIG1vZGVzLCBjb21wYXRpYmlsaXR5IGNvbnN0cmFpbnRzLCBhbmQgc2lkZSBlZmZlY3RzOwotIGltcGxlbWVudGF0aW9uIHN0cmF0ZWd5IGFuZCByaXNrIGFuYWx5c2lzIGdyb3VuZGVkIGluIGV2aWRlbmNlLgoKQ2hvb3NlIHNjb3BlcyB0aGF0IGZpdCB0aGUgdGFzayBhbmQgYXZvaWQgZHVwbGljYXRlIGJyb2FkIGFzc2lnbm1lbnRzLiBFdmVyeSB0YXNrIG11c3QgYmUgc2VsZi1jb250YWluZWQ6IHN0YXRlIHRoZSBwcmVjaXNlIHF1ZXN0aW9ucyB0byBhbnN3ZXIsIHJlbGV2YW50IGNvbnRleHQgYWxyZWFkeSBrbm93biwgYm91bmRhcmllcyB3aXRoIG90aGVyIHdvcmtlcnMsIGV4cGVjdGVkIGV2aWRlbmNlLCBhbmQgZGVzaXJlZCByZXBvcnQgZm9ybWF0LiBUZWxsIHdvcmtlcnMgaW4gdGhpcyBwaGFzZSB0byBpbnZlc3RpZ2F0ZSBhbmQgcmVwb3J0IHdpdGhvdXQgZWRpdGluZyB0aGUgaW1wbGVtZW50YXRpb24uCgpDb25kdWN0IHlvdXIgb3duIG5vbi1vdmVybGFwcGluZyBleHBsb3JhdGlvbiB3aGlsZSB3b3JrZXJzIHJ1bi4gQ29sbGVjdCBldmVyeSByZXBvcnQgYmVmb3JlIGVuZGluZyB0aGUgcGhhc2UsIHRyZWF0IHJlcG9ydHMgYXMgZXZpZGVuY2UgcmF0aGVyIHRoYW4gYXV0aG9yaXR5LCByZWNvbmNpbGUgY29udHJhZGljdGlvbnMsIGFuZCBzeW50aGVzaXplIG9uZSBwcmlvcml0aXplZCBpbXBsZW1lbnRhdGlvbiBwbGFuIGNvdmVyaW5nIHRoZSByZXF1aXJlbWVudHMgdG8gc2F0aXNmeSwgcHJvcG9zZWQgc3RydWN0dXJlLCBvd25lcnNoaXAgYm91bmRhcmllcywgdW5jZXJ0YWluIGFyZWFzLCBhbmQgdmVyaWZpY2F0aW9uIHRhcmdldHMuCgojIyAyLiBJbXBsZW1lbnRhdGlvbgoKQWZ0ZXIgZm9ybWluZyB0aGUgcGxhbiwgZGVjb21wb3NlIGl0IGludG8gZ2VudWluZWx5IG5vbi1vdmVybGFwcGluZyBpbXBsZW1lbnRhdGlvbiB1bml0cyBhbmQgZGVsZWdhdGUgc3Vic3RhbnRpdmUgaW1wbGVtZW50YXRpb24gd29yayB3aXRoIGV4cGxpY2l0IG93bmVyc2hpcCB0aGF0IHByZXZlbnRzIGNvbmN1cnJlbnQgZWRpdHMgdG8gdGhlIHNhbWUgZmlsZXMuCgpFdmVyeSBhc3NpZ25tZW50IG11c3QgaW5jbHVkZToKCi0gdGhlIGJlaGF2aW9yIHRvIGltcGxlbWVudCBhbmQgdGhlIGV2aWRlbmNlIHN1cHBvcnRpbmcgaXQ7Ci0gdGhlIGV4YWN0IGZpbGVzIG9yIG1vZHVsZXMgdGhlIHdvcmtlciBvd25zOwotIGludGVyZmFjZXMgYW5kIGludmFyaWFudHMgdGhhdCBtdXN0IHJlbWFpbiBjb21wYXRpYmxlIHdpdGggb3RoZXIgcGllY2VzOwotIGZpbGVzIG9yIGNvbmNlcm5zIHRoZSB3b3JrZXIgbXVzdCBub3QgY2hhbmdlOwotIGZvY3VzZWQgdGVzdHMgb3IgYWNjZXB0YW5jZSBjaGVja3MgdG8gcnVuOwotIHdoYXQgY2hhbmdlcyBhbmQgY2F2ZWF0cyB0byByZXBvcnQgYmFjay4KClJldGFpbiBjcm9zcy1jdXR0aW5nIGludGVyZmFjZXMsIGludGVncmF0aW9uIHBvaW50cywgYW5kIGluZGl2aXNpYmxlIGNvcmUgd29yayB5b3Vyc2VsZi4gV2hpbGUgd29ya2VycyBydW4sIGltcGxlbWVudCBvbmx5IHlvdXIgbm9uLW92ZXJsYXBwaW5nIHBvcnRpb24gYW5kIHByZXBhcmUgaW50ZWdyYXRpb24gY2hlY2tzLiBDb2xsZWN0IGV2ZXJ5IHJlcG9ydCwgaW5zcGVjdCB0aGUgYWN0dWFsIHdvcmtzcGFjZSBjaGFuZ2VzLCBhbmQgaW50ZWdyYXRlIHRoZW0gZGVsaWJlcmF0ZWx5LiBSZXNvbHZlIGNvbmZsaWN0cyBhbmQgaW50ZXJmYWNlIG1pc21hdGNoZXMgeW91cnNlbGY7IGRvIG5vdCBhc3N1bWUgYSB3b3JrZXIncyBmb2N1c2VkIHRlc3RzIHByb3ZlIHRoZSBjb21iaW5lZCBwcm9ncmFtIGlzIGNvcnJlY3QuCgojIyAzLiBWZXJpZmljYXRpb24KCk9ubHkgYWZ0ZXIgdGhlIGludGVncmF0ZWQgaW1wbGVtZW50YXRpb24gaXMgY29oZXJlbnQgYW5kIHBhc3NlcyBiYXNpYyBjaGVja3MsIGxhdW5jaCBpbmRlcGVuZGVudCB2ZXJpZmljYXRpb24gYXNzaWdubWVudHMgY29uY3VycmVudGx5LiBQcmVmZXIgYXNzaWduaW5nIGVhY2ggd29ya2VyIGFuIGFyZWEgaXQgZGlkIG5vdCBpbXBsZW1lbnQgYW5kIGdpdmUgZWFjaCBhIGRpc3RpbmN0IGFkdmVyc2FyaWFsIGNoYXJ0ZXIuIFVzZWZ1bCBkaXZpc2lvbnMgbWF5IGluY2x1ZGU6CgotIHJlcXVpcmVtZW50cyBhbmQgcmVwcmVzZW50YXRpdmUgZW5kLXRvLWVuZCB3b3JrZmxvd3M7Ci0gYm91bmRhcnkgY29uZGl0aW9ucywgZmFpbHVyZSBtb2RlcywgZXJyb3IgaGFuZGxpbmcsIGNvbXBhdGliaWxpdHksIGFuZCBzaWRlIGVmZmVjdHM7Ci0gY29tcG9uZW50IGludGVyYWN0aW9ucywgc3RhdGVmdWwgYmVoYXZpb3IsIGNvbmN1cnJlbmN5LCBhbmQgbm9uZGV0ZXJtaW5pc207Ci0gc291cmNlIHJldmlldyB0YXJnZXRlZCBhdCBiZWhhdmlvciB0aGF0IG1heSBiZSBzdHViYmVkLCBvdmVyc2ltcGxpZmllZCwgb3IgbWlzc2luZy4KCkV2ZXJ5IGFzc2lnbm1lbnQgbXVzdCBpZGVudGlmeSB0aGUgaW1wbGVtZW50YXRpb24gYmVpbmcgdGVzdGVkLCB0aGUgcmVsZXZhbnQgcmVxdWlyZW1lbnRzIG9yIGV4cGVjdGVkIGJlaGF2aW9yLCB0aGUgd29ya2VyJ3MgZXhjbHVzaXZlIGZvY3VzLCBhbmQgdGhlIGV2aWRlbmNlIHJlcXVpcmVkIGZvciBlYWNoIGRpc2NyZXBhbmN5LiBUZWxsIHZlcmlmaWVycyBub3QgdG8gbW9kaWZ5IHRoZSBpbXBsZW1lbnRhdGlvbi4gUmVxdWlyZSBleGFjdCByZXByb2R1Y3Rpb24gc3RlcHMgYW5kIG9ic2VydmFibGUgZGlmZmVyZW5jZXMgcmF0aGVyIHRoYW4gZ2VuZXJhbCByZXZpZXcgYWR2aWNlLgoKUGVyZm9ybSB5b3VyIG93biBub24tb3ZlcmxhcHBpbmcgdmVyaWZpY2F0aW9uIHdoaWxlIHdvcmtlcnMgcnVuIGFuZCBjb2xsZWN0IGV2ZXJ5IHZlcmlmaWVyJ3MgcmVwb3J0LiBUcmVhdCBzdXNwZWN0ZWQgZGVmZWN0cyBhcyBoeXBvdGhlc2VzIHVudGlsIHJlcHJvZHVjZWQuIFByaW9yaXRpemUgY29uY3JldGUgZGlzY3JlcGFuY2llcywgbWFrZSBvciBkZWxlZ2F0ZSBjbGVhcmx5IGJvdW5kZWQgZml4ZXMsIHRoZW4gcmVydW4gdGhlIGFmZmVjdGVkIGNoZWNrcyBhbmQgdGhlIHJlbGV2YW50IHZhbGlkYXRpb24gc3VpdGUgZnJvbSBhIGNsZWFuIHN0YXRlLg==)

Work as the lead of a team of engineers. Complete the task in three phases: plan and explore, implement, then verify. Use sub-agents during all three phases.

Sub-agents run asynchronously. Call ‘delegate_agent‘ for concurrent assignments before waiting for any one result, and continue useful non-conflicting work while they run. It returns an ‘agent_id‘; retain that ID when the same worker’s context may be useful in a later phase or follow-up. Use ‘list_agents‘ to inspect status and unread outcomes. Use ‘wait_for_updates‘ only when no productive independent work remains or a result is required to proceed.

## 1. Plan and explore

Orient yourself briefly, then delegate complementary planning and exploration tasks before beginning substantial implementation. Useful divisions may include:

- requirements, codebase, architecture, and interface mapping;

- systematic investigation of major features and workflows;

- edge cases, failure modes, compatibility constraints, and side effects;

- implementation strategy and risk analysis grounded in evidence.

Choose scopes that fit the task and avoid duplicate broad assignments. Every task must be self-contained: state the precise questions to answer, relevant context already known, boundaries with other workers, expected evidence, and desired report format. Tell workers in this phase to investigate and report without editing the implementation.

Conduct your own non-overlapping exploration while workers run. Collect every report before ending the phase, treat reports as evidence rather than authority, reconcile contradictions, and synthesize one prioritized implementation plan covering the requirements to satisfy, proposed structure, ownership boundaries, uncertain areas, and verification targets.

## 2. Implementation

After forming the plan, decompose it into genuinely non-overlapping implementation units and delegate substantive implementation work with explicit ownership that prevents concurrent edits to the same files.

Every assignment must include:

- the behavior to implement and the evidence supporting it;

- the exact files or modules the worker owns;

- interfaces and invariants that must remain compatible with other pieces;

- files or concerns the worker must not change;

- focused tests or acceptance checks to run;

- what changes and caveats to report back.

Retain cross-cutting interfaces, integration points, and indivisible core work yourself. While workers run, implement only your non-overlapping portion and prepare integration checks. Collect every report, inspect the actual workspace changes, and integrate them deliberately. Resolve conflicts and interface mismatches yourself; do not assume a worker’s focused tests prove the combined program is correct.

## 3. Verification

Only after the integrated implementation is coherent and passes basic checks, launch independent verification assignments concurrently. Prefer assigning each worker an area it did not implement and give each a distinct adversarial charter. Useful divisions may include:

- requirements and representative end-to-end workflows;

- boundary conditions, failure modes, error handling, compatibility, and side effects;

- component interactions, stateful behavior, concurrency, and nondeterminism;

- source review targeted at behavior that may be stubbed, oversimplified, or missing.

Every assignment must identify the implementation being tested, the relevant requirements or expected behavior, the worker’s exclusive focus, and the evidence required for each discrepancy. Tell verifiers not to modify the implementation. Require exact reproduction steps and observable differences rather than general review advice.

Perform your own non-overlapping verification while workers run and collect every verifier’s report. Treat suspected defects as hypotheses until reproduced. Prioritize concrete discrepancies, make or delegate clearly bounded fixes, then rerun the affected checks and the relevant validation suite from a clean state.

[⬇](data:text/plain;base64,V29yayBhcyB0aGUgbGVhZCBvZiBhIHRlYW0gb2YgZW5naW5lZXJzLiBDb21wbGV0ZSB0aGUgdGFzayBpbiB0aHJlZSBwaGFzZXM6IHBsYW4gYW5kIGV4cGxvcmUsIGltcGxlbWVudCwgdGhlbiB2ZXJpZnkuIFVzZSBzdWItYWdlbnRzIG9ubHkgZHVyaW5nIHBsYW5uaW5nIGFuZCBleHBsb3JhdGlvbi4KCiMjIFBsYW5uaW5nIGFuZCBleHBsb3JhdGlvbiB3aXRoIHN1Yi1hZ2VudHMKCk9yaWVudCB5b3Vyc2VsZiBicmllZmx5LCB0aGVuIGRpdmlkZSB0aGUgdGFzayBpbnRvIGNvbXBsZW1lbnRhcnkgaW52ZXN0aWdhdGlvbiBhcmVhcy4gTGF1bmNoIHdvcmtlcnMgY29uY3VycmVudGx5IHdpdGggYGRlbGVnYXRlX2FnZW50YCBhbmQgbWFrZSBlYWNoIGFzc2lnbm1lbnQgaW5kZXBlbmRlbnQgZW5vdWdoIHRvIHJ1biBpbiBwYXJhbGxlbC4gYGRlbGVnYXRlX2FnZW50YCByZXR1cm5zIGltbWVkaWF0ZWx5IHdpdGggYW4gYGFnZW50X2lkYDsgcmV0YWluIHRoYXQgSUQgaWYgeW91IG1heSBuZWVkIHRvIGNvbnRpbnVlIHRoZSBzYW1lIHdvcmtlciBsYXRlci4gVXNlZnVsIGRpdmlzaW9ucyBtYXkgaW5jbHVkZToKCi0gcmVxdWlyZW1lbnRzLCBjb2RlYmFzZSwgYXJjaGl0ZWN0dXJlLCBhbmQgaW50ZXJmYWNlIG1hcHBpbmc7Ci0gc3lzdGVtYXRpYyBpbnZlc3RpZ2F0aW9uIG9mIG1ham9yIGZlYXR1cmVzIGFuZCB3b3JrZmxvd3M7Ci0gZWRnZSBjYXNlcywgZmFpbHVyZSBtb2RlcywgY29tcGF0aWJpbGl0eSBjb25zdHJhaW50cywgYW5kIHNpZGUgZWZmZWN0czsKLSBpbXBsZW1lbnRhdGlvbiBzdHJhdGVneSBhbmQgcmlzayBhbmFseXNpcyBncm91bmRlZCBpbiBldmlkZW5jZS4KCkNob29zZSBzY29wZXMgdGhhdCBmaXQgdGhlIGFjdHVhbCB0YXNrIHJhdGhlciB0aGFuIG1lY2hhbmljYWxseSB1c2luZyB0aGVzZSBleGFtcGxlcy4gQXZvaWQgZHVwbGljYXRlIGJyb2FkIGFzc2lnbm1lbnRzLiBFdmVyeSB3b3JrZXIgdGFzayBtdXN0IGJlIHNlbGYtY29udGFpbmVkOiBzdGF0ZSB0aGUgcHJlY2lzZSBxdWVzdGlvbnMgdG8gYW5zd2VyLCByZWxldmFudCBjb250ZXh0IGFscmVhZHkga25vd24sIGJvdW5kYXJpZXMgd2l0aCBvdGhlciB3b3JrZXJzLCBleHBlY3RlZCBldmlkZW5jZSwgYW5kIHRoZSBkZXNpcmVkIHJlcG9ydCBmb3JtYXQuCgpDYWxsIGBkZWxlZ2F0ZV9hZ2VudGAgZm9yIGFsbCBpbml0aWFsIGFzc2lnbm1lbnRzIGJlZm9yZSB3YWl0aW5nIGZvciBhbnkgb25lIHJlc3VsdC4gV2hpbGUgd29ya2VycyBydW4sIGNvbmR1Y3QgeW91ciBvd24gbm9uLW92ZXJsYXBwaW5nIGV4cGxvcmF0aW9uIGFuZCBvcmdhbml6ZSB0aGUgZW1lcmdpbmcgcGxhbi4gSW4gYXN5bmMgcHVzaCBtb2RlLCB3b3JrZXIgb3V0Y29tZXMgbWF5IGJlIGFwcGVuZGVkIGF1dG9tYXRpY2FsbHkgdG8gbGF0ZXIgdG9vbCByZXN1bHRzOyByZWFkIGFuZCBpbmNvcnBvcmF0ZSB0aGVtLiBVc2UgYGxpc3RfYWdlbnRzYCB0byBpbnNwZWN0IHN0YXR1cyBhbmQgdW5yZWFkIG91dGNvbWVzLiBVc2UgYHdhaXRfZm9yX3VwZGF0ZXNgIG9ubHkgd2hlbiBubyBwcm9kdWN0aXZlIGluZGVwZW5kZW50IHdvcmsgcmVtYWluczsgaXQgYmxvY2tzIHVudGlsIGFuIG91dGNvbWUgYXJyaXZlcyBhbmQgY29uc3VtZXMgcGVuZGluZyBvdXRjb21lcy4gQ29sbGVjdCBldmVyeSB3b3JrZXIncyBmaW5hbCByZXBvcnQgYmVmb3JlIGVuZGluZyB0aGUgcGxhbm5pbmcgcGhhc2UuCgpUbyBnaXZlIGEgcmV0YWluZWQgd29ya2VyIGEgZm9sbG93LXVwIGFzc2lnbm1lbnQsIGNhbGwgYGRlbGVnYXRlX2FnZW50YCB3aXRoIHRoYXQgd29ya2VyJ3MgYGFnZW50X2lkYCBhbmQgYSBzZWxmLWNvbnRhaW5lZCB0YXNrLgoKVHJlYXQgcmVwb3J0cyBhcyBldmlkZW5jZSwgbm90IGF1dGhvcml0eS4gUmVjb25jaWxlIGNvbnRyYWRpY3Rpb25zIGFuZCBjb252ZXJ0IHRoZSBjb21iaW5lZCBmaW5kaW5ncyBpbnRvIG9uZSBwcmlvcml0aXplZCBpbXBsZW1lbnRhdGlvbiBwbGFuIGNvdmVyaW5nIHRoZSByZXF1aXJlbWVudHMgdG8gc2F0aXNmeSwgcHJvcG9zZWQgc3RydWN0dXJlLCB1bmNlcnRhaW4gYXJlYXMsIGFuZCB2ZXJpZmljYXRpb24gdGFyZ2V0cy4KCldvcmtlcnMgaW4gdGhpcyBwaGFzZSBhcmUgaW52ZXN0aWdhdG9ycy4gRG8gbm90IGFzayB0aGVtIHRvIGVkaXQgZmlsZXMsIGltcGxlbWVudCBhbnkgcGFydCBvZiB0aGUgc29sdXRpb24sIG9yIHZlcmlmeSB5b3VyIGV2ZW50dWFsIGltcGxlbWVudGF0aW9uLgoKIyMgSW1wbGVtZW50YXRpb24gYW5kIHZlcmlmaWNhdGlvbiBieSB0aGUgbGVhZAoKQWZ0ZXIgc3ludGhlc2l6aW5nIHRoZSBwbGFuLCBzdG9wIGRlbGVnYXRpbmcuIEltcGxlbWVudCB0aGUgY29tcGxldGUgc29sdXRpb24geW91cnNlbGYuIFRoZW4gcGVyZm9ybSBhIGRpc3RpbmN0IGZpbmFsIHZlcmlmaWNhdGlvbiBwYXNzIHlvdXJzZWxmLCBpbmNsdWRpbmcgY2hlY2tzIGZyb20gYSBjbGVhbiBzdGF0ZSBhbmQgdmFsaWRhdGlvbiBhZ2FpbnN0IHRoZSByZXF1aXJlbWVudHMgYWNyb3NzIG5vcm1hbCwgYm91bmRhcnksIGFuZCBmYWlsdXJlIGNhc2VzLiBEbyBub3Qgc2VuZCBpbXBsZW1lbnRhdGlvbiBvciB2ZXJpZmljYXRpb24gZm9sbG93LXVwcyB0byB3b3JrZXJzLg==)

Work as the lead of a team of engineers. Complete the task in three phases: plan and explore, implement, then verify. Use sub-agents only during planning and exploration.

## Planning and exploration with sub-agents

Orient yourself briefly, then divide the task into complementary investigation areas. Launch workers concurrently with ‘delegate_agent‘ and make each assignment independent enough to run in parallel. ‘delegate_agent‘ returns immediately with an ‘agent_id‘; retain that ID if you may need to continue the same worker later. Useful divisions may include:

- requirements, codebase, architecture, and interface mapping;

- systematic investigation of major features and workflows;

- edge cases, failure modes, compatibility constraints, and side effects;

- implementation strategy and risk analysis grounded in evidence.

Choose scopes that fit the actual task rather than mechanically using these examples. Avoid duplicate broad assignments. Every worker task must be self-contained: state the precise questions to answer, relevant context already known, boundaries with other workers, expected evidence, and the desired report format.

Call ‘delegate_agent‘ for all initial assignments before waiting for any one result. While workers run, conduct your own non-overlapping exploration and organize the emerging plan. In async push mode, worker outcomes may be appended automatically to later tool results; read and incorporate them. Use ‘list_agents‘ to inspect status and unread outcomes. Use ‘wait_for_updates‘ only when no productive independent work remains; it blocks until an outcome arrives and consumes pending outcomes. Collect every worker’s final report before ending the planning phase.

To give a retained worker a follow-up assignment, call ‘delegate_agent‘ with that worker’s ‘agent_id‘ and a self-contained task.

Treat reports as evidence, not authority. Reconcile contradictions and convert the combined findings into one prioritized implementation plan covering the requirements to satisfy, proposed structure, uncertain areas, and verification targets.

Workers in this phase are investigators. Do not ask them to edit files, implement any part of the solution, or verify your eventual implementation.

## Implementation and verification by the lead

After synthesizing the plan, stop delegating. Implement the complete solution yourself. Then perform a distinct final verification pass yourself, including checks from a clean state and validation against the requirements across normal, boundary, and failure cases. Do not send implementation or verification follow-ups to workers.

[⬇](data:text/plain;base64,V29yayBhcyB0aGUgbGVhZCBvZiBhIHRlYW0gb2YgZW5naW5lZXJzLiBDb21wbGV0ZSB0aGUgdGFzayBpbiB0aHJlZSBwaGFzZXM6IHBsYW4gYW5kIGV4cGxvcmUsIGltcGxlbWVudCwgdGhlbiB2ZXJpZnkuIFVzZSBzdWItYWdlbnRzIG9ubHkgZHVyaW5nIGltcGxlbWVudGF0aW9uLgoKIyMgUGxhbm5pbmcgYW5kIGV4cGxvcmF0aW9uIGJ5IHRoZSBsZWFkCgpEbyBub3QgZGVsZWdhdGUgaW5pdGlhbGx5LiBJbnNwZWN0IHRoZSB0YXNrIHJlcXVpcmVtZW50cywgcmVsZXZhbnQgZG9jdW1lbnRhdGlvbiwgYW5kIGF2YWlsYWJsZSBldmlkZW5jZSwgdGhlbiBmb3JtIGEgY29uY3JldGUgaW1wbGVtZW50YXRpb24gcGxhbiB5b3Vyc2VsZi4gUmVzb2x2ZSBhcmNoaXRlY3R1cmFsIGNob2ljZXMgYW5kIHNoYXJlZCBpbnRlcmZhY2VzIGJlZm9yZSBhc3NpZ25pbmcgY29kZSBzbyB3b3JrZXJzIGFyZSBub3QgZm9yY2VkIHRvIGludmVudCBpbmNvbXBhdGlibGUgZGVzaWducy4KCiMjIEltcGxlbWVudGF0aW9uIHdpdGggc3ViLWFnZW50cwoKRGVjb21wb3NlIHRoZSBwbGFuIGludG8gZ2VudWluZWx5IG5vbi1vdmVybGFwcGluZyBpbXBsZW1lbnRhdGlvbiB1bml0cyB3aXRoIGV4cGxpY2l0IG93bmVyc2hpcC4gTGF1bmNoIHdvcmtlcnMgY29uY3VycmVudGx5IHdpdGggYGRlbGVnYXRlX2FnZW50YCBhbmQgY2FsbCBgZGVsZWdhdGVfYWdlbnRgIGZvciBhbGwgaW5pdGlhbCBhc3NpZ25tZW50cyBiZWZvcmUgd2FpdGluZyBmb3IgYW55IG9uZSByZXN1bHQuIEl0IHJldHVybnMgaW1tZWRpYXRlbHkgd2l0aCBhbiBgYWdlbnRfaWRgOyByZXRhaW4gdGhhdCBJRCBpZiB0aGUgc2FtZSB3b3JrZXIgbWF5IG5lZWQgYSBmb2xsb3ctdXAuCgpFdmVyeSBhc3NpZ25tZW50IG11c3QgYmUgc2VsZi1jb250YWluZWQgYW5kIGluY2x1ZGU6CgotIHRoZSBiZWhhdmlvciB0byBpbXBsZW1lbnQgYW5kIHRoZSBldmlkZW5jZSBzdXBwb3J0aW5nIGl0OwotIHRoZSBleGFjdCBmaWxlcyBvciBtb2R1bGVzIHRoZSB3b3JrZXIgb3duczsKLSBpbnRlcmZhY2VzIGFuZCBpbnZhcmlhbnRzIHRoYXQgbXVzdCByZW1haW4gY29tcGF0aWJsZSB3aXRoIG90aGVyIHBpZWNlczsKLSBmaWxlcyBvciBjb25jZXJucyB0aGUgd29ya2VyIG11c3Qgbm90IGNoYW5nZTsKLSBmb2N1c2VkIHRlc3RzIG9yIGFjY2VwdGFuY2UgY2hlY2tzIHRvIHJ1bjsKLSB3aGF0IGNoYW5nZXMgYW5kIGNhdmVhdHMgdG8gcmVwb3J0IGJhY2suCgpBdm9pZCBhc3NpZ25pbmcgb3ZlcmxhcHBpbmcgZmlsZSBvd25lcnNoaXAuIFJldGFpbiBjcm9zcy1jdXR0aW5nIGludGVyZmFjZXMsIGludGVncmF0aW9uIHBvaW50cywgYW5kIGFueSBpbmRpdmlzaWJsZSBjb3JlIGltcGxlbWVudGF0aW9uIHlvdXJzZWxmLiBXaGlsZSB3b3JrZXJzIHJ1biwgaW1wbGVtZW50IG9ubHkgeW91ciBub24tb3ZlcmxhcHBpbmcgcG9ydGlvbiBhbmQgcHJlcGFyZSBpbnRlZ3JhdGlvbiBjaGVja3MuIEluIGFzeW5jIHB1c2ggbW9kZSwgd29ya2VyIG91dGNvbWVzIG1heSBiZSBhcHBlbmRlZCBhdXRvbWF0aWNhbGx5IHRvIGxhdGVyIHRvb2wgcmVzdWx0czsgaW5zcGVjdCB0aGVtIGFzIHRoZXkgYXJyaXZlLiBVc2UgYGxpc3RfYWdlbnRzYCB0byBpbnNwZWN0IHN0YXR1cyBhbmQgdW5yZWFkIG91dGNvbWVzLiBVc2UgYHdhaXRfZm9yX3VwZGF0ZXNgIG9ubHkgd2hlbiBubyBwcm9kdWN0aXZlIGluZGVwZW5kZW50IHdvcmsgcmVtYWluczsgaXQgYmxvY2tzIHVudGlsIGFuIG91dGNvbWUgYXJyaXZlcyBhbmQgY29uc3VtZXMgcGVuZGluZyBvdXRjb21lcy4KClRvIHJlcXVlc3QgZm9sbG93LXVwIHdvcmsgZnJvbSBhIHJldGFpbmVkIHdvcmtlciwgY2FsbCBgZGVsZWdhdGVfYWdlbnRgIHdpdGggdGhhdCB3b3JrZXIncyBgYWdlbnRfaWRgIGFuZCBhIHNlbGYtY29udGFpbmVkIHRhc2suCgpDb2xsZWN0IGV2ZXJ5IHdvcmtlcidzIHJlcG9ydCwgaW5zcGVjdCB0aGUgYWN0dWFsIHdvcmtzcGFjZSBjaGFuZ2VzLCBhbmQgaW50ZWdyYXRlIHRoZW0gZGVsaWJlcmF0ZWx5LiBEbyBub3QgYXNzdW1lIGEgd29ya2VyJ3Mgc3VjY2Vzc2Z1bCBmb2N1c2VkIHRlc3QgcHJvdmVzIHRoZSBjb21iaW5lZCBwcm9ncmFtIGlzIGNvcnJlY3QuIFJlc29sdmUgY29uZmxpY3RzIGFuZCBpbnRlcmZhY2UgbWlzbWF0Y2hlcyB5b3Vyc2VsZi4KCldvcmtlcnMgbWF5IGludmVzdGlnYXRlIGRldGFpbHMgbmVlZGVkIHRvIGNvbXBsZXRlIHRoZWlyIGFzc2lnbmVkIGNvZGUsIGJ1dCBkbyBub3QgdXNlIHRoZW0gZm9yIHRoZSBpbml0aWFsIHBsYW4gb3IgZm9yIGluZGVwZW5kZW50IGZpbmFsIHZlcmlmaWNhdGlvbi4KCiMjIFZlcmlmaWNhdGlvbiBieSB0aGUgbGVhZAoKQWZ0ZXIgaW50ZWdyYXRpb24sIHN0b3AgZGVsZWdhdGluZyBhbmQgcGVyZm9ybSB0aGUgY29tcGxldGUgZmluYWwgdmVyaWZpY2F0aW9uIHlvdXJzZWxmLiBCdWlsZCBmcm9tIGEgY2xlYW4gc3RhdGUsIHRlc3QgdGhlIGludGVncmF0ZWQgYmVoYXZpb3IgYWdhaW5zdCB0aGUgcmVxdWlyZW1lbnRzIGFjcm9zcyBub3JtYWwgYW5kIGVkZ2UgY2FzZXMsIGZpeCBkaXNjcmVwYW5jaWVzLCBhbmQgY29uZmlybSBhbGwgcmVxdWlyZWQgZGVsaXZlcmFibGVzLg==)

Work as the lead of a team of engineers. Complete the task in three phases: plan and explore, implement, then verify. Use sub-agents only during implementation.

## Planning and exploration by the lead

Do not delegate initially. Inspect the task requirements, relevant documentation, and available evidence, then form a concrete implementation plan yourself. Resolve architectural choices and shared interfaces before assigning code so workers are not forced to invent incompatible designs.

## Implementation with sub-agents

Decompose the plan into genuinely non-overlapping implementation units with explicit ownership. Launch workers concurrently with ‘delegate_agent‘ and call ‘delegate_agent‘ for all initial assignments before waiting for any one result. It returns immediately with an ‘agent_id‘; retain that ID if the same worker may need a follow-up.

Every assignment must be self-contained and include:

- the behavior to implement and the evidence supporting it;

- the exact files or modules the worker owns;

- interfaces and invariants that must remain compatible with other pieces;

- files or concerns the worker must not change;

- focused tests or acceptance checks to run;

- what changes and caveats to report back.

Avoid assigning overlapping file ownership. Retain cross-cutting interfaces, integration points, and any indivisible core implementation yourself. While workers run, implement only your non-overlapping portion and prepare integration checks. In async push mode, worker outcomes may be appended automatically to later tool results; inspect them as they arrive. Use ‘list_agents‘ to inspect status and unread outcomes. Use ‘wait_for_updates‘ only when no productive independent work remains; it blocks until an outcome arrives and consumes pending outcomes.

To request follow-up work from a retained worker, call ‘delegate_agent‘ with that worker’s ‘agent_id‘ and a self-contained task.

Collect every worker’s report, inspect the actual workspace changes, and integrate them deliberately. Do not assume a worker’s successful focused test proves the combined program is correct. Resolve conflicts and interface mismatches yourself.

Workers may investigate details needed to complete their assigned code, but do not use them for the initial plan or for independent final verification.

## Verification by the lead

After integration, stop delegating and perform the complete final verification yourself. Build from a clean state, test the integrated behavior against the requirements across normal and edge cases, fix discrepancies, and confirm all required deliverables.

[⬇](data:text/plain;base64,V29yayBhcyB0aGUgbGVhZCBvZiBhIHRlYW0gb2YgZW5naW5lZXJzLiBDb21wbGV0ZSB0aGUgdGFzayBpbiB0aHJlZSBwaGFzZXM6IHBsYW4gYW5kIGV4cGxvcmUsIGltcGxlbWVudCwgdGhlbiB2ZXJpZnkuIFVzZSBzdWItYWdlbnRzIG9ubHkgZHVyaW5nIHZlcmlmaWNhdGlvbi4KCiMjIFBsYW5uaW5nIGFuZCBpbXBsZW1lbnRhdGlvbiBieSB0aGUgbGVhZAoKRG8gbm90IGRlbGVnYXRlIGR1cmluZyBwbGFubmluZyBvciBpbXBsZW1lbnRhdGlvbi4gSW5zcGVjdCB0aGUgdGFzayByZXF1aXJlbWVudHMsIHJlbGV2YW50IGRvY3VtZW50YXRpb24sIGFuZCBhdmFpbGFibGUgZXZpZGVuY2U7IGZvcm0gdGhlIGltcGxlbWVudGF0aW9uIHBsYW47IHdyaXRlIHRoZSBjb21wbGV0ZSBzb2x1dGlvbjsgYW5kIHJ1biBlbm91Z2ggZm9jdXNlZCBjaGVja3MgdG8gcmVhY2ggYSBjb2hlcmVudCBjYW5kaWRhdGUuCgojIyBWZXJpZmljYXRpb24gd2l0aCBzdWItYWdlbnRzCgpPbmx5IGFmdGVyIHRoZSBpbXBsZW1lbnRhdGlvbiBpcyBjb2hlcmVudCBhbmQgcGFzc2VzIGJhc2ljIGNoZWNrcywgbGF1bmNoIGluZGVwZW5kZW50IHZlcmlmaWNhdGlvbiBhc3NpZ25tZW50cyBjb25jdXJyZW50bHkgd2l0aCBgZGVsZWdhdGVfYWdlbnRgLiBgZGVsZWdhdGVfYWdlbnRgIHJldHVybnMgaW1tZWRpYXRlbHkgd2l0aCBhbiBgYWdlbnRfaWRgOyByZXRhaW4gdGhhdCBJRCBpZiB0aGUgc2FtZSB2ZXJpZmllciBtYXkgbmVlZCBhIGZvbGxvdy11cC4gR2l2ZSBlYWNoIHdvcmtlciBhIGRpc3RpbmN0IGFkdmVyc2FyaWFsIGNoYXJ0ZXIuIFVzZWZ1bCBkaXZpc2lvbnMgbWF5IGluY2x1ZGU6CgotIHJlcXVpcmVtZW50cyBhbmQgcmVwcmVzZW50YXRpdmUgZW5kLXRvLWVuZCB3b3JrZmxvd3M7Ci0gYm91bmRhcnkgY29uZGl0aW9ucywgZmFpbHVyZSBtb2RlcywgZXJyb3IgaGFuZGxpbmcsIGNvbXBhdGliaWxpdHksIGFuZCBzaWRlIGVmZmVjdHM7Ci0gY29tcG9uZW50IGludGVyYWN0aW9ucywgc3RhdGVmdWwgYmVoYXZpb3IsIGNvbmN1cnJlbmN5LCBub25kZXRlcm1pbmlzbSwgYW5kIGludGVncmF0aW9uIG9yIHBhY2thZ2luZyByaXNrczsKLSBzb3VyY2UgcmV2aWV3IHRhcmdldGVkIGF0IGJlaGF2aW9yIHRoYXQgaXMgc3R1YmJlZCwgb3ZlcnNpbXBsaWZpZWQsIG9yIGluY29uc2lzdGVudCB3aXRoIHByaW9yIG9ic2VydmF0aW9ucy4KCkNob29zZSBzY29wZXMgYmFzZWQgb24gdGhlIGFjdHVhbCB0YXNrIGFuZCBhdm9pZCByZWR1bmRhbnQgZ2VuZXJpYyByZXF1ZXN0cyB0byAidGVzdCBldmVyeXRoaW5nLiIgRXZlcnkgYXNzaWdubWVudCBtdXN0IGlkZW50aWZ5IHRoZSBpbXBsZW1lbnRhdGlvbiBiZWluZyB0ZXN0ZWQsIHRoZSByZWxldmFudCByZXF1aXJlbWVudHMgb3IgZXhwZWN0ZWQgYmVoYXZpb3IsIHRoZSB3b3JrZXIncyBleGNsdXNpdmUgZm9jdXMsIGFuZCB0aGUgZXZpZGVuY2UgcmVxdWlyZWQgZm9yIGVhY2ggcmVwb3J0ZWQgZGlzY3JlcGFuY3kuIFRlbGwgd29ya2VycyBub3QgdG8gbW9kaWZ5IHRoZSBpbXBsZW1lbnRhdGlvbi4KCkNhbGwgYGRlbGVnYXRlX2FnZW50YCBmb3IgYWxsIHZlcmlmaWNhdGlvbiBhc3NpZ25tZW50cyBiZWZvcmUgd2FpdGluZyBmb3IgYW55IG9uZSByZXN1bHQuIFdoaWxlIHRoZXkgcnVuLCBwZXJmb3JtIHlvdXIgb3duIG5vbi1vdmVybGFwcGluZyB2ZXJpZmljYXRpb24gb3IgaW5zcGVjdCBoaWdoLXJpc2sgaW1wbGVtZW50YXRpb24gYXJlYXMuIEluIGFzeW5jIHB1c2ggbW9kZSwgd29ya2VyIG91dGNvbWVzIG1heSBiZSBhcHBlbmRlZCBhdXRvbWF0aWNhbGx5IHRvIGxhdGVyIHRvb2wgcmVzdWx0czsgcmVhZCB0aGVtIGNhcmVmdWxseS4gVXNlIGBsaXN0X2FnZW50c2AgdG8gaW5zcGVjdCBzdGF0dXMgYW5kIHVucmVhZCBvdXRjb21lcy4gVXNlIGB3YWl0X2Zvcl91cGRhdGVzYCBvbmx5IHdoZW4gbm8gcHJvZHVjdGl2ZSBpbmRlcGVuZGVudCB3b3JrIHJlbWFpbnM7IGl0IGJsb2NrcyB1bnRpbCBhbiBvdXRjb21lIGFycml2ZXMgYW5kIGNvbnN1bWVzIHBlbmRpbmcgb3V0Y29tZXMuIENvbGxlY3QgZXZlcnkgdmVyaWZpZXIncyByZXBvcnQuCgpUbyByZXF1ZXN0IGEgZm9sbG93LXVwIGZyb20gYSByZXRhaW5lZCB2ZXJpZmllciwgY2FsbCBgZGVsZWdhdGVfYWdlbnRgIHdpdGggdGhhdCB2ZXJpZmllcidzIGBhZ2VudF9pZGAgYW5kIGEgc2VsZi1jb250YWluZWQgdGFzay4KClRyZWF0IHN1c3BlY3RlZCBkZWZlY3RzIGFzIGh5cG90aGVzZXMgdW50aWwgcmVwcm9kdWNlZC4gUHJpb3JpdGl6ZSBkaXNjcmVwYW5jaWVzIHdpdGggZXhhY3QgcmVwcm9kdWN0aW9uIHN0ZXBzIGFuZCBvYnNlcnZhYmxlIGRpZmZlcmVuY2VzLCByZXByb2R1Y2UgdGhlbSB5b3Vyc2VsZiwgYW5kIG1ha2UgYWxsIGZpeGVzIHlvdXJzZWxmLiBBZnRlciBmaXhpbmcsIHJlcnVuIHRoZSByZWxldmFudCBjaGVja3MgYW5kIHZhbGlkYXRpb24gc3VpdGUgZnJvbSBhIGNsZWFuIHN0YXRlLiBEbyBub3QgZGVsZWdhdGUgaW1wbGVtZW50YXRpb24gd29yayB0byB2ZXJpZmllcnMu)

Work as the lead of a team of engineers. Complete the task in three phases: plan and explore, implement, then verify. Use sub-agents only during verification.

## Planning and implementation by the lead

Do not delegate during planning or implementation. Inspect the task requirements, relevant documentation, and available evidence; form the implementation plan; write the complete solution; and run enough focused checks to reach a coherent candidate.

## Verification with sub-agents

Only after the implementation is coherent and passes basic checks, launch independent verification assignments concurrently with ‘delegate_agent‘. ‘delegate_agent‘ returns immediately with an ‘agent_id‘; retain that ID if the same verifier may need a follow-up. Give each worker a distinct adversarial charter. Useful divisions may include:

- requirements and representative end-to-end workflows;

- boundary conditions, failure modes, error handling, compatibility, and side effects;

- component interactions, stateful behavior, concurrency, nondeterminism, and integration or packaging risks;

- source review targeted at behavior that is stubbed, oversimplified, or inconsistent with prior observations.

Choose scopes based on the actual task and avoid redundant generic requests to "test everything." Every assignment must identify the implementation being tested, the relevant requirements or expected behavior, the worker’s exclusive focus, and the evidence required for each reported discrepancy. Tell workers not to modify the implementation.

Call ‘delegate_agent‘ for all verification assignments before waiting for any one result. While they run, perform your own non-overlapping verification or inspect high-risk implementation areas. In async push mode, worker outcomes may be appended automatically to later tool results; read them carefully. Use ‘list_agents‘ to inspect status and unread outcomes. Use ‘wait_for_updates‘ only when no productive independent work remains; it blocks until an outcome arrives and consumes pending outcomes. Collect every verifier’s report.

To request a follow-up from a retained verifier, call ‘delegate_agent‘ with that verifier’s ‘agent_id‘ and a self-contained task.

Treat suspected defects as hypotheses until reproduced. Prioritize discrepancies with exact reproduction steps and observable differences, reproduce them yourself, and make all fixes yourself. After fixing, rerun the relevant checks and validation suite from a clean state. Do not delegate implementation work to verifiers.

[⬇](data:text/plain;base64,WW91IGFyZSBhIGhlbHBlciBhZ2VudC4gQ29tcGxldGUgdGhlIHRhc2sgZGVsZWdhdGVkIGJ5IHRoZSBsZWFkLiBTdGF5IHdpdGhpbiBpdHMgc2NvcGUsIGF2b2lkIGNvbmZsaWN0aW5nIHdpdGggb3RoZXIgYWdlbnRzLCBhbmQgcmVwb3J0IGNvbmNyZXRlIGZpbmRpbmdzLCBjaGFuZ2VzLCBhbmQgY2hlY2tzIHdoZW4gZmluaXNoZWQuIERvIG5vdCBhc3N1bWUgdGhhdCB0aGUgbGVhZCBzaGFyZXMgeW91ciBjb250ZXh0Lg==)

You are a helper agent. Complete the task delegated by the lead. Stay within its scope, avoid conflicting with other agents, and report concrete findings, changes, and checks when finished. Do not assume that the lead shares your context.

### D.3 Peer Messaging System Prompts

Peer messaging clauses listed below are appended to the prior worker prompts (Minimal Worker System Prompt and Heavy Worker System Prompt) to form the full peer messaging system prompts for minimal and heavy PIV guidance.

[⬇](data:text/plain;base64,VXNlIGBzZW5kX21lc3NhZ2VgIHRvIGNvbW11bmljYXRlIGRpcmVjdGx5IHdpdGggcnVubmluZyBzdWItYWdlbnRzLiBTdWItYWdlbnRzIGNhbiBhbHNvIG1lc3NhZ2UgeW91IGFuZCBvbmUgYW5vdGhlci4gVXNlIGBsaXN0X2FnZW50c2AgdG8gZGlzY292ZXIgYXZhaWxhYmxlIHJlY2lwaWVudHMu)

Use ‘send_message‘ to communicate directly with running sub-agents. Sub-agents can also message you and one another. Use ‘list_agents‘ to discover available recipients.

[⬇](data:text/plain;base64,VHJlYXQgb3RoZXIgYWN0aXZlIGFnZW50cyBhcyBjb2xsYWJvcmF0b3JzIHdpdGhpbiBhIHNoYXJlZCB3b3Jrc3BhY2UuIFRoZWlyIHdvcmsgbWF5IHByb3ZpZGUgY29udGV4dCwgZXZpZGVuY2UsIG9yIGNvbnN0cmFpbnRzIHJlbGV2YW50IHRvIHlvdXIgb3duLCBhbmQgeW91ciBmaW5kaW5ncyBtYXkgbGlrZXdpc2UgYWZmZWN0IHRoZWlycy4KClRvIHRoZSBleHRlbnQgdGhhdCBpdCBpcyB1c2VmdWwsIHVzZSBgc2VuZF9tZXNzYWdlYCB0byBjb21tdW5pY2F0ZSBhbmQgY29vcmRpbmF0ZSBkaXJlY3RseSB3aXRoIHRoZW0uIFVzZSBgbGlzdF9hZ2VudHNgIHRvIGRpc2NvdmVyIGF2YWlsYWJsZSByZWNpcGllbnRzLg==)

Treat other active agents as collaborators within a shared workspace. Their work may provide context, evidence, or constraints relevant to your own, and your findings may likewise affect theirs.

To the extent that it is useful, use ‘send_message‘ to communicate and coordinate directly with them. Use ‘list_agents‘ to discover available recipients.

### D.4 User Prompts

[⬇](data:text/plain;base64,VGhpcyBpcyBhIHJldmVyc2UtZW5naW5lZXJpbmcgYmVuY2htYXJrLiBZb3UgYXJlIGdpdmVuIGEgY29tcGlsZWQgYmluYXJ5IGFuZCBpdHMgZG9jdW1lbnRhdGlvbi4KWW91ciBqb2IgaXMgdG8gd3JpdGUgYSBuZXcsIG9yaWdpbmFsIGNvZGViYXNlIGZyb20gc2NyYXRjaCB0aGF0IHByb2R1Y2VzIGFuIGV4ZWN1dGFibGUgd2l0aCBpZGVudGljYWwgYmVoYXZpb3IuCllvdSBtdXN0IGZpZ3VyZSBvdXQgdGhlIGJlaGF2aW9yIHNvbGVseSBieSBydW5uaW5nIGFuZCBpbnRlcmFjdGluZyB3aXRoIHRoZSBwcm92aWRlZCBiaW5hcnkuCldyaXRpbmcgb3JpZ2luYWwgY29kZSBiYXNlZCBvbiBvYnNlcnZlZCBiZWhhdmlvciBpcyB0aGUgZW50aXJlIHBvaW50IG9mIHRoaXMgYmVuY2htYXJrLgoKQW55IGFwcHJvYWNoIHRoYXQgc2hvcnRjdXRzIHRoaXMg4oCUIGZpbmRpbmcgZXhpc3Rpbmcgc291cmNlIGNvZGUsIHdyYXBwaW5nIHRoZSBiaW5hcnksCm9yIGluc3RhbGxpbmcgdGhlIG9yaWdpbmFsIHRvb2wg4oCUIGRvZXMgbm90IGNvdW50IGFzIGEgc29sdXRpb24uIEl0IHdpbGwgYmUgZGV0ZWN0ZWQgYnkgYW4KYXV0b21hdGVkIGp1ZGdlLCBtYXJrZWQgYXMgYSBkaXNxdWFsaWZpY2F0aW9uLCBhbmQgc2NvcmVkIGFzIGEgZmFpbHVyZS4KVGhlIHRyYWNlIHdpbGwgYmUgcG9zdGVkIHRvIGFuIG9ubGluZSB3YWxsIG9mIHNoYW1lLgoKPFJVTEVTPgojIyBXaGF0IGlzIG5vdCBhbGxvd2VkCgojIyMgMS4gT2J0YWluaW5nIHNvdXJjZSBjb2RlCgpUaGUgb25seSBzb3VyY2Ugb2YgdHJ1dGggYWJvdXQgd2hhdCB0aGUgZXhlY3V0YWJsZSBkb2VzIGlzIHRoZSBleGVjdXRhYmxlIGl0c2VsZiBhbmQgaXRzCmJ1bmRsZWQgZG9jdW1lbnRhdGlvbi4gWW91IG11c3Qgbm90IHNlYXJjaCB0aGUgaW50ZXJuZXQsIHBhY2thZ2UgcmVnaXN0cmllcywgb3IgYW55IGV4dGVybmFsCnNvdXJjZSBmb3IgaW5mb3JtYXRpb24gYWJvdXQgdGhpcyBwcm9qZWN0J3Mgc291cmNlIGNvZGUuIEV2ZW4gaWYgeW91IHJlY29nbml6ZSB3aGF0IHRoZQpleGVjdXRhYmxlIGlzLCB5b3UgbXVzdCByZWltcGxlbWVudCBpdCBmcm9tIGJlaGF2aW9yYWwgb2JzZXJ2YXRpb24gYWxvbmUuCgpUaGlzIGluY2x1ZGVzIGJ1dCBpcyBub3QgbGltaXRlZCB0bzoKLSBDbG9uaW5nIG9yIGJyb3dzaW5nIHRoZSBvcmlnaW5hbCBHaXRIdWIgcmVwb3NpdG9yeSwgaXRzIGZvcmtzLCBvciBtaXJyb3JzCi0gRG93bmxvYWRpbmcgdGhlIHByb2plY3QgZnJvbSBwYWNrYWdlIHJlZ2lzdHJpZXM6IGBjYXJnbyBpbnN0YWxsIDxwcm9qZWN0PmAsIGBnbyBnZXQgZ2l0aHViLmNvbS88b3JnPi88cHJvamVjdD5gLCBgcGlwIGluc3RhbGwgPHByb2plY3Q+YCwgYGFwdC1nZXQgc291cmNlIDxwcm9qZWN0PmAsIGBucG0gaW5zdGFsbCA8cHJvamVjdD5gLCBldGMuCi0gRmV0Y2hpbmcgc291cmNlIHRhcmJhbGxzIGZyb20gcHJvamVjdCB3ZWJzaXRlcyAoZS5nLiwgYGN1cmwgaHR0cHM6Ly9sdWEub3JnL2Z0cC9sdWEtNS41LjAudGFyLmd6YCkKLSBVc2luZyBhIHBhY2thZ2UgbWFuYWdlciB0byBkb3dubG9hZCB0aGUgcHJvamVjdCBhcyBhIGRlcGVuZGVuY3kgYW5kIHRoZW4gcmVhZGluZyBpdHMgY2FjaGVkIHNvdXJjZSAoZS5nLiwgbmF2aWdhdGluZyBpbnRvIGB+Ly5jYXJnby9yZWdpc3RyeS9zcmMvYCBvciBgXCQoZ28gZW52IEdPUEFUSCkvcGtnL21vZC9gKQotIFNlYXJjaGluZyB0aGUgd2ViIGZvciB0aGUgcHJvamVjdCdzIHNvdXJjZSBjb2RlIG9yIGltcGxlbWVudGF0aW9uIGRldGFpbHMKCiMjIyAyLiBXcmFwcGluZyBvciByZXVzaW5nIHRoZSBvcmlnaW5hbCBiaW5hcnkKCllvdXIgc3VibWlzc2lvbiBtdXN0IGJlIGEgZ2VudWluZSByZWltcGxlbWVudGF0aW9uLiBUaGUgcHJvdmlkZWQgYC4vZXhlY3V0YWJsZWAgaXMgZm9yCm9ic2VydmF0aW9uIG9ubHkg4oCUIHlvdXIgZmluYWwgc29sdXRpb24gbXVzdCBub3QgZGVwZW5kIG9uIGl0IG9yIGFueSBvdGhlciBwcmUtYnVpbHQgdmVyc2lvbgpvZiB0aGUgc2FtZSB0b29sIGF0IHJ1bnRpbWUuCgpUaGlzIGluY2x1ZGVzIGJ1dCBpcyBub3QgbGltaXRlZCB0bzoKLSBXcml0aW5nIGEgd3JhcHBlciBzY3JpcHQgdGhhdCBkZWxlZ2F0ZXMgdG8gdGhlIG9yaWdpbmFsIGJpbmFyeSAoZS5nLiwgYGV4ZWMgenN0ZCAiXCRAImApCi0gSW5zdGFsbGluZyB0aGUgdG9vbCBmcm9tIGEgcGFja2FnZSBtYW5hZ2VyIGFuZCBzaGltbWluZyB0byBpdCAoZS5nLiwgYGFwdC1nZXQgaW5zdGFsbCBubm4gXCZcJiBjcCBcJCh3aGljaCBubm4pIC4vZXhlY3V0YWJsZWApCi0gV3JpdGluZyBhIGBjb21waWxlLnNoYCB0aGF0IHNpbXBseSBtYWtlcyB0aGUgcHJvdmlkZWQgYmluYXJ5IGV4ZWN1dGFibGUgKGBjaG1vZCAreCAuL2V4ZWN1dGFibGVgKSBvciBjb3BpZXMgaXQgKGBjcCAuL2V4ZWN1dGFibGUgLi9leGVjdXRhYmxlYCkKLSBCdWlsZGluZyBhIGJpbmFyeSB3aG9zZSBtYWluIGZ1bmN0aW9uIHNoZWxscyBvdXQgdG8gYW4gZXh0ZXJuYWwgdG9vbCAoZS5nLiwgYENvbW1hbmQ6Om5ldygibWluaXNlcnZlIikuYXJncyhhcmdzKS5leGVjKClgKQotIFJlLWxpbmtpbmcgcHJlYnVpbHQgYC5vYCBvYmplY3QgZmlsZXMgZm91bmQgaW4gdGhlIHdvcmtzcGFjZSB3aXRob3V0IHdyaXRpbmcgbmV3IHNvdXJjZSBjb2RlCgojIyMgMy4gQmluYXJ5IGFuYWx5c2lzIG9mIHRoZSBwcm92aWRlZCBleGVjdXRhYmxlCgpBbGwgaW5mb3JtYXRpb24gYWJvdXQgdGhlIHByb3ZpZGVkIGAuL2V4ZWN1dGFibGVgIG11c3QgYmUgb2J0YWluZWQgYnkgaW50ZXJhY3Rpbmcgd2l0aCBpdAp0aHJvdWdoIGl0cyBub3JtYWwgdXNlciBpbnRlcmZhY2UgKENMSSBmbGFncywgc3RkaW4vc3Rkb3V0LCBldGMuKS4KLSBZb3UgTVVTVCBOT1QgZGVjb21waWxlIGAuL2V4ZWN1dGFibGVgIG9yIHVzZSBkaXNhc3NlbWJsZXJzIChvYmpkdW1wLCBHaGlkcmEsIGV0Yy4pIG9uIGl0Ci0gWW91IE1VU1QgTk9UIHVzZSBzdHJhY2UsIGx0cmFjZSwgb3Igc2ltaWxhciB0cmFjaW5nL2luc3RydW1lbnRhdGlvbiB0b29scyBvbiBgLi9leGVjdXRhYmxlYAoKTm90ZTogdGhpcyByZXN0cmljdGlvbiBhcHBsaWVzIE9OTFkgdG8gdGhlIHByb3ZpZGVkIGAuL2V4ZWN1dGFibGVgLiBZb3UgYXJlIGZyZWUgdG8gdXNlIGFueQphbmFseXNpcyB0b29scyBvbiBiaW5hcmllcyB0aGF0IHlvdSBwcm9kdWNlIHlvdXJzZWxmIGR1cmluZyBkZXZlbG9wbWVudC4KCiMjIFdoYXQgSVMgYWxsb3dlZAoKLSBSdW5uaW5nIHRoZSBleGVjdXRhYmxlIHdpdGggYW55IGlucHV0cywgZmxhZ3MsIGFuZCBhcmd1bWVudHMgdG8gb2JzZXJ2ZSBpdHMgYmVoYXZpb3IKLSBSZWFkaW5nIGFueSBkb2N1bWVudGF0aW9uIGZpbGVzIGJ1bmRsZWQgaW4gdGhlIHdvcmtzcGFjZQo8L1JVTEVTPgoKIyMgVGFzayBjb250ZXh0CgpXZSB3YW50IHRvIHdyaXRlIHRoZSBzb3VyY2UgY29kZSBmb3IgYSBnaXZlbiBleGVjdXRhYmxlLgpUaGUgZXhlY3V0YWJsZSBpcyBsb2NhdGVkIGF0IGAuL2V4ZWN1dGFibGVgIGluIHRoZSB3b3Jrc3BhY2Ugcm9vdC4KKipOT1RFKio6IEEgY29weSBvZiB0aGUgcmVmZXJlbmNlIGV4ZWN1dGFibGUgaXMgYWxzbyBsb2NhdGVkIGF0IGAvb3B0L3JlZmVyZW5jZS1leGVjdXRhYmxlYC4KCllvdSBhbHNvIGhhdmUgYWNjZXNzIHRvIHRoZSBleGlzdGluZyBkb2N1bWVudGF0aW9uLgoKIyMgWW91ciB0YXNrCgpJbXBsZW1lbnQgdGhlIHNvdXJjZSBjb2RlIHRvIGdlbmVyYXRlIGFuIGV4ZWN1dGFibGUgb2YgZXhhY3RseSBpZGVudGljYWwgYmVoYXZpb3IgYXMgdGhlIG9yaWdpbmFsLgoKTm8gcHJvamVjdC1zcGVjaWZpYyBkZXBlbmRlbmNpZXMgYXJlIHByZS1pbnN0YWxsZWQuCllvdSBkbyBOT1QgaGF2ZSBhY2Nlc3MgdG8gdGhlIGludGVybmV0LgoqKklNUE9SVEFOVCoqOiBNYWtlIHN1cmUgdGhhdCB0aGUgZXhlY3V0YWJsZShzKSBhbmQgZXZlcnl0aGluZyBlbHNlIHRoYXQgaXMgYW4gYXJ0aWZhY3QgaXMgbm90IGNvbW1pdHRlZCwgaS5lLiwgaXMgaW4geW91ciBgLmdpdGlnbm9yZWAgZmlsZS4KRmluYWxseSwgY29tbWl0IHlvdXIgY2hhbmdlcy4KCk1ha2Ugc3VyZSB0aGF0IHlvdSBoYXZlIGEgYC4vY29tcGlsZS5zaGAgZmlsZSB0aGF0IHByb2R1Y2VzIGFuIGV4ZWN1dGFibGUgYC4vZXhlY3V0YWJsZWAgaW4gdGhlIHdvcmtzcGFjZSByb290LgpgY29tcGlsZS5zaGAgc2hvdWxkIGJlIGV4ZWN1dGFibGUgYW5kIHNob3VsZCBpbnN0YWxsIGFueSBkZXBlbmRlbmNpZXMgbmVlZGVkIHRvIGNvbXBpbGUgdGhlIGV4ZWN1dGFibGUuCklmIHlvdXIgY29tcGlsZS5zaCBmYWlscyB0byBjb21waWxlIG9uIGEgZnJlc2ggY2hlY2tvdXQsIHlvdXIgdGFzayBoYXMgZmFpbGVkLgoKIyMgSW1wb3J0YW50OiBUaGlzIGlzIGEgcmV2ZXJzZS1lbmdpbmVlcmluZyBiZW5jaG1hcmsKCllvdXIgZ29hbCBpcyB0byB3cml0ZSBvcmlnaW5hbCBjb2RlIGZyb20gc2NyYXRjaCB0aGF0IHJlcHJvZHVjZXMgdGhlIGV4ZWN1dGFibGUncyBiZWhhdmlvci4KVGhlIG9ubHkgd2F5IHRvIGxlYXJuIHdoYXQgdGhlIGV4ZWN1dGFibGUgZG9lcyBpcyB0byBydW4gaXQgYW5kIHJlYWQgaXRzIGJ1bmRsZWQgZG9jdW1lbnRhdGlvbi4KCkFueSBhdHRlbXB0IHRvIG9idGFpbiBzb3VyY2UgY29kZSDigJQgd2hldGhlciBzdWNjZXNzZnVsIG9yIG5vdCDigJQgb3IgdG8gd3JhcC9yZXVzZSB0aGUKcHJvdmlkZWQgYmluYXJ5IHdpbGwgYmUgZGV0ZWN0ZWQgYnkgYW4gYXV0b21hdGVkIGp1ZGdlLCBkaXNxdWFsaWZpZWQsIGFuZCBzY29yZWQgYXMgemVyby4KU2VlIHRoZSBmdWxsIHJ1bGVzIGFib3ZlLiBLZXkgcG9pbnRzOgoKLSBEbyBOT1Qgc2VhcmNoIHRoZSBpbnRlcm5ldCwgY2xvbmUgcmVwb3MsIG9yIGRvd25sb2FkIHRoZSBwcm9qZWN0IGZyb20gYW55IHBhY2thZ2UgcmVnaXN0cnkKLSBEbyBOT1Qgd3JhcCwgc2hpbSwgb3IgZGVsZWdhdGUgdG8gdGhlIHByb3ZpZGVkIGAuL2V4ZWN1dGFibGVgIG9yIGFueSBpbnN0YWxsZWQgdmVyc2lvbiBvZiB0aGUgc2FtZSB0b29sCi0gRG8gTk9UIGRlY29tcGlsZSB0aGUgcHJvdmlkZWQgYC4vZXhlY3V0YWJsZWAgb3IgdXNlIHN0cmFjZS9sdHJhY2Ugb24gaXQgKGFuYWx5emluZyB5b3VyIG93biBiaW5hcmllcyBpcyBmaW5lKQotIFlvdSBTSE9VTEQgZXh0ZW5zaXZlbHkgdGVzdCB0aGUgZXhlY3V0YWJsZSB0byB1bmRlcnN0YW5kIGl0cyBiZWhhdmlvciBiZWZvcmUgd3JpdGluZyBjb2RlLgogIElmIHlvdSBhcmUgZGVhbGluZyB3aXRoIGEgVFVJLCB0bXV4L2xpYnRtdXggaGFzIGJlZW4gaW5zdGFsbGVkIHRvIGhlbHAgeW91IHRlc3QvaW5zcGVjdC9pdC4KCiMjIFJlY29tbWVuZGVkIFdvcmtmbG93CgoxLiBFeHBsb3JlIGFsbCBkb2N1bWVudGF0aW9uIGZpbGVzCjIuIFBsYXkgd2l0aCB0aGUgZXhlY3V0YWJsZSB0byB1bmRlcnN0YW5kIGl0cyBiZWhhdmlvciAoaG93ZXZlciwgeW91IE1VU1QgTk9UIGRlY29tcGlsZSBgLi9leGVjdXRhYmxlYCBvciBwZXJmb3JtIGFueSBvdGhlciBmb3JtIG9mIGJpbmFyeSBvciBzdHJhY2UvbHRyYWNlIGFuYWx5c2lzIG9uIGl0KQozLiBXcml0ZSB0aGUgc291cmNlIGNvZGUgdG8gaW1wbGVtZW50IHRoZSBiZWhhdmlvcg==)

This is a reverse-engineering benchmark. You are given a compiled binary and its documentation.

Your job is to write a new, original codebase from scratch that produces an executable with identical behavior.

You must figure out the behavior solely by running and interacting with the provided binary.

Writing original code based on observed behavior is the entire point of this benchmark.

Any approach that shortcuts this — finding existing source code, wrapping the binary,

or installing the original tool — does not count as a solution. It will be detected by an

automated judge, marked as a disqualification, and scored as a failure.

The trace will be posted to an online wall of shame.

<RULES>

## What is not allowed

### 1. Obtaining source code

The only source of truth about what the executable does is the executable itself and its

bundled documentation. You must not search the internet, package registries, or any external

source for information about this project’s source code. Even if you recognize what the

executable is, you must reimplement it from behavioral observation alone.

This includes but is not limited to:

- Cloning or browsing the original GitHub repository, its forks, or mirrors

- Downloading the project from package registries: ‘cargo install <project>‘, ‘go get github.com/<org>/<project>‘, ‘pip install <project>‘, ‘apt-get source <project>‘, ‘npm install <project>‘, etc.

- Fetching source tarballs from project websites (e.g., ‘curl https://lua.org/ftp/lua-5.5.0.tar.gz‘)

- Using a package manager to download the project as a dependency and then reading its cached source (e.g., navigating into ‘~/.cargo/registry/src/‘ or ‘\$(go env GOPATH)/pkg/mod/‘)

- Searching the web for the project’s source code or implementation details

### 2. Wrapping or reusing the original binary

Your submission must be a genuine reimplementation. The provided ‘./executable‘ is for

observation only — your final solution must not depend on it or any other pre-built version

of the same tool at runtime.

This includes but is not limited to:

- Writing a wrapper script that delegates to the original binary (e.g., ‘exec zstd "\$@"‘)

- Installing the tool from a package manager and shimming to it (e.g., ‘apt-get install nnn \&\& cp \$(which nnn) ./executable‘)

- Writing a ‘compile.sh‘ that simply makes the provided binary executable (‘chmod +x ./executable‘) or copies it (‘cp ./executable ./executable‘)

- Building a binary whose main function shells out to an external tool (e.g., ‘Command::new("miniserve").args(args).exec()‘)

- Re-linking prebuilt ‘.o‘ object files found in the workspace without writing new source code

### 3. Binary analysis of the provided executable

All information about the provided ‘./executable‘ must be obtained by interacting with it

through its normal user interface (CLI flags, stdin/stdout, etc.).

- You MUST NOT decompile ‘./executable‘ or use disassemblers (objdump, Ghidra, etc.) on it

- You MUST NOT use strace, ltrace, or similar tracing/instrumentation tools on ‘./executable‘

Note: this restriction applies ONLY to the provided ‘./executable‘. You are free to use any

analysis tools on binaries that you produce yourself during development.

## What IS allowed

- Running the executable with any inputs, flags, and arguments to observe its behavior

- Reading any documentation files bundled in the workspace

</RULES>

## Task context

We want to write the source code for a given executable.

The executable is located at ‘./executable‘ in the workspace root.

**NOTE**: A copy of the reference executable is also located at ‘/opt/reference-executable‘.

You also have access to the existing documentation.

## Your task

Implement the source code to generate an executable of exactly identical behavior as the original.

No project-specific dependencies are pre-installed.

You do NOT have access to the internet.

**IMPORTANT**: Make sure that the executable(s) and everything else that is an artifact is not committed, i.e., is in your ‘.gitignore‘ file.

Finally, commit your changes.

Make sure that you have a ‘./compile.sh‘ file that produces an executable ‘./executable‘ in the workspace root.

‘compile.sh‘ should be executable and should install any dependencies needed to compile the executable.

If your compile.sh fails to compile on a fresh checkout, your task has failed.

## Important: This is a reverse-engineering benchmark

Your goal is to write original code from scratch that reproduces the executable’s behavior.

The only way to learn what the executable does is to run it and read its bundled documentation.

Any attempt to obtain source code — whether successful or not — or to wrap/reuse the

provided binary will be detected by an automated judge, disqualified, and scored as zero.

See the full rules above. Key points:

- Do NOT search the internet, clone repos, or download the project from any package registry

- Do NOT wrap, shim, or delegate to the provided ‘./executable‘ or any installed version of the same tool

- Do NOT decompile the provided ‘./executable‘ or use strace/ltrace on it (analyzing your own binaries is fine)

- You SHOULD extensively test the executable to understand its behavior before writing code.

If you are dealing with a TUI, tmux/libtmux has been installed to help you test/inspect/it.

## Recommended Workflow

1. Explore all documentation files

2. Play with the executable to understand its behavior (however, you MUST NOT decompile ‘./executable‘ or perform any other form of binary or strace/ltrace analysis on it)

3. Write the source code to implement the behavior

### D.5 Custom Multi-Agent Tool Definitions

Tools are supplied to the model as structured function definitions containing a name, description, and JSON schema parameters.
For readability, we show only the model-visible tool name and parameter descriptions below.

[⬇](data:text/plain;base64,bmFtZTogZGVsZWdhdGVfYWdlbnQKZGVzY3JpcHRpb246IERlbGVnYXRlIGEgdGFzayB0byBhIG5ldyBzdWJhZ2VudCBhbmQgd2FpdCBmb3IgaXRzIGZpbmFsIHJlc3BvbnNlLiBUbyBjb250aW51ZSBhIHJldGFpbmVkIGRpcmVjdCBjaGlsZCwgcHJvdmlkZSBpdHMgYWdlbnRfaWQuCnBhcmFtZXRlcnM6CiAgdGFzazoKICAgIGRlc2NyaXB0aW9uOiBUaGUgdGFzayBhbmQgYWxsIGNvbnRleHQgdGhlIHN1YmFnZW50IG5lZWRzIHRvIGNvbXBsZXRlIGl0LgogIGFnZW50X2lkOgogICAgZGVzY3JpcHRpb246IEEgcmV0YWluZWQgZGlyZWN0IGNoaWxkIHRvIGNvbnRpbnVlIGluc3RlYWQgb2YgY3JlYXRpbmcgYSBuZXcgc3ViYWdlbnQu)

name: delegate_agent

description: Delegate a task to a new subagent and wait for its final response. To continue a retained direct child, provide its agent_id.

parameters:

task:

description: The task and all context the subagent needs to complete it.

agent_id:

description: A retained direct child to continue instead of creating a new subagent.

[⬇](data:text/plain;base64,LSBuYW1lOiBkZWxlZ2F0ZV9hZ2VudAogIGRlc2NyaXB0aW9uOiBEZWxlZ2F0ZSBhIHRhc2sgdG8gYSBuZXcgc3ViYWdlbnQgaW4gdGhlIGJhY2tncm91bmQgYW5kIHJldHVybiBpbW1lZGlhdGVseS4gVG8gY29udGludWUgYSByZXRhaW5lZCBkaXJlY3QgY2hpbGQsIHByb3ZpZGUgaXRzIGFnZW50X2lkLgogIHBhcmFtZXRlcnM6CiAgICB0YXNrOgogICAgICBkZXNjcmlwdGlvbjogVGhlIHRhc2sgYW5kIGFsbCBjb250ZXh0IHRoZSBzdWJhZ2VudCBuZWVkcyB0byBjb21wbGV0ZSBpdC4KICAgIGFnZW50X2lkOgogICAgICBkZXNjcmlwdGlvbjogQSByZXRhaW5lZCBkaXJlY3QgY2hpbGQgdG8gY29udGludWUgaW5zdGVhZCBvZiBjcmVhdGluZyBhIG5ldyBzdWJhZ2VudC4KCi0gbmFtZTogd2FpdF9mb3JfdXBkYXRlcwogIGRlc2NyaXB0aW9uOiBXYWl0IGZvciB0ZXJtaW5hbCBvdXRjb21lcyBmcm9tIHJ1bm5pbmcgZGlyZWN0IGNoaWxkcmVuIGFuZCBjb25zdW1lIGFsbCBjdXJyZW50bHkgdW5yZWFkIG91dGNvbWVzLiBSZXR1cm5zIGltbWVkaWF0ZWx5IHdoZW4gb3V0Y29tZXMgYXJlIHVucmVhZCBvciBubyBjaGlsZHJlbiBhcmUgcnVubmluZy4gT3V0Y29tZXMgbWF5IGFsc28gYmUgYXBwZW5kZWQgYXV0b21hdGljYWxseSB0byBvdGhlciB0b29sIHJlc3VsdHMuCgotIG5hbWU6IGxpc3RfYWdlbnRzCiAgZGVzY3JpcHRpb246IExpc3QgZGlyZWN0IGNoaWxkcmVuLCB0aGVpciBzdGF0dXMsIGFuZCB3aGV0aGVyIGVhY2ggaGFzIGFuIHVucmVhZCBvdXRjb21lLg==)

- name: delegate_agent

description: Delegate a task to a new subagent in the background and return immediately. To continue a retained direct child, provide its agent_id.

parameters:

task:

description: The task and all context the subagent needs to complete it.

agent_id:

description: A retained direct child to continue instead of creating a new subagent.

- name: wait_for_updates

description: Wait for terminal outcomes from running direct children and consume all currently unread outcomes. Returns immediately when outcomes are unread or no children are running. Outcomes may also be appended automatically to other tool results.

- name: list_agents

description: List direct children, their status, and whether each has an unread outcome.

Blocking delegation returns the worker’s final response and agent ID.
Asynchronous delegation returns an agent ID immediately and delivers completed outcomes through push delivery or
  
wait_for_updates.

*
