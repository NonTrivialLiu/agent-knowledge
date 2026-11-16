---
title: "QwenGyre: An Elastic Reinforcement Learning Framework for Training xLong-Horizon Agents"
url: https://arxiv.org/abs/2609.33848
published: 2026-09-27
fetched: 2026-11-11
type: paper
topics: [training, multi-agent, long-running]
summary: "超长轨迹强化学习的弹性调度和资源利用；v2 2026-10-20。文章是研究论文，适合重点阅读系统设计和实验。"
---

# QwenGyre : An Elastic Reinforcement Learning Framework for Training x Long-Horizon Agents

[Weiqi Wang](mailto:wangweiqi0329@mail.ustc.edu.cn)*
[Yuxin Zhou](mailto:suishi.zyx@alibaba-inc.com)*
[Mouxiang Chen](mailto:chenmx@zju.edu.cn)*
[Siyuan Zhang](mailto:18301188748@163.com)

[Yi Zhang](mailto:1109276519@qq.com)
[Yuyan Luo](mailto:luoyuyan.lyy@alibaba-inc.com)
[Zhiyu Yin](mailto:yinzhiyu.yzy@alibaba-inc.com)
[Chencan Wu](mailto:wuchencan.wcc@alibaba-inc.com)

[Jiemin Jiang](mailto:jiangjiemin.jjm@alibaba-inc.com)
[Wentao Yao](mailto:wenyao.ywt@alibaba-inc.com)
[Chujie Zheng](mailto:zhengchujie.zcj@alibaba-inc.com)
[JianWei Zhang](mailto:zhangjianwei.zjw@alibaba-inc.com)†
Alibaba Token Hub, Alibaba Group

## Abstract

Large language model (LLM) agents increasingly undertake extreme-long (xLong) horizon tasks, where a single execution can span hours, hundreds of model–environment interactions, and nearly 1M tokens per rollout.
Applying online reinforcement learning (RL) to such executions poses two fundamental challenges:
(1) severe execution variance and prolonged rollout delays cause massive GPU idling;
and (2) complex non-linear branching generates massive trajectory redundancy, crippling training efficiency.

To address these, we presents QwenGyre, an end-to-end framework for xLong-horizon online RL.
QwenGyre elastically reallocates GPUs between rollout and training without interrupting live executions, while its trajectory processor reconstructs branching histories, scores partial progress, and deduplicates redundant paths to bound training costs.
Scaled to our flagship model, Qwen 3.8 2.4T, with 700K tokens per rollout, QwenGyre yields a 6.0% absolute gain on NL2RepoBench (52.5% `\to` 58.5%) in 48 steps. Across our evaluations on diverse domains of training datasets, QwenGyre
delivers up to `1.85\times` and `1.78\times` speedups over Colocate
and Async, respectively.

Figure 1: QwenGyre addresses two challenges of xLong-horizon agentic RL.
(a) The Elastic Scheduler reallocates idle rollout capacity to training
while continuing to serve ongoing executions.
(b) The Trajectory Processor converts branching executions into bounded
training samples while masking repeated targets in shared prefixes.

11footnotetext: Equal contribution.22footnotetext: Corresponding author.

## 1 Introduction

Large language model (LLM) agents increasingly solve software
engineering tasks that are *long-horizon*: completing one task
requires an extended sequence of interdependent decisions and
environment interactions over a persistent workspace.
A representative class of such tasks is issue resolution (e.g., SWE-bench ([Jimenez et al., 2024](https://arxiv.org/html/2609.33848#bib.bib12); [Deng et al., 2026](https://arxiv.org/html/2609.33848#bib.bib13))),
which localizes a single fix within an existing repository and spans tens of
interactions.
On these workloads, online reinforcement learning (RL) has demonstrated
promising gains by iteratively refining policies through environment interactions ([Luo et al., 2025a](https://arxiv.org/html/2609.33848#bib.bib60); [Golubev et al., 2025](https://arxiv.org/html/2609.33848#bib.bib61); [Song et al., 2026b](https://arxiv.org/html/2609.33848#bib.bib16); [Du et al., 2026b](https://arxiv.org/html/2609.33848#bib.bib17)).

As foundation models rapidly advance in reasoning and context capabilities,
the paradigm is shifting toward fully autonomous, end-to-end software
development, such as repository generation ([Ding et al., 2026](https://arxiv.org/html/2609.33848#bib.bib18)), system reimplementation ([Yang et al., 2026](https://arxiv.org/html/2609.33848#bib.bib19)), and codebase-wide refactoring ([Hong et al., 2026](https://arxiv.org/html/2609.33848#bib.bib20)).
These workloads extend long-horizon execution to multi-hour, project-scale runs.
A single stateful rollout spans hundreds of dependent model–environment interactions and processes around 1M tokens across its context.
We refer to this regime as *xLong-horizon*.
Scaling RL to xLong-horizons introduces fundamental
challenges on both system scheduling and trajectory modeling.

Challenge 1: Extreme rollout variance and severe GPU underutilization at xLong-horizons.
Online RL conventionally adopts a *colocate* design that alternates
the GPU pool between rollout and training ([Sheng et al., 2025](https://arxiv.org/html/2609.33848#bib.bib26); [Mei et al., 2025](https://arxiv.org/html/2609.33848#bib.bib28)).
At xLong-horizons, however, rollouts exhibit severe long-tail variance;
without general support for checkpointing workspace state, training remains
blocked until all live executions end, leaving GPUs idle on a few trailing tasks.
Alternative *async* deployments statically partition GPUs into
dedicated pools ([Fu et al., 2025](https://arxiv.org/html/2609.33848#bib.bib33)).
Nevertheless, at xLong-horizons, the wait for a ready batch can far exceed the duration of a training
step, leaving training GPUs idle while rigid partitions prevent either
stage from utilizing the other’s spare capacity.
The challenge is therefore to reallocate GPUs dynamically as demand changes,
using idle capacity for training while maintaining inference service for
ongoing rollouts.

Challenge 2: Complex trajectory branching and prohibitive training overhead at xLong-horizons.
The linear agent loop used in simple agent designs ([Yao et al., 2023](https://arxiv.org/html/2609.33848#bib.bib11); [Yang et al., 2024](https://arxiv.org/html/2609.33848#bib.bib10))
does not survive at xLong-horizons: sustaining hours of execution
typically relies on black-box harnesses that routinely compact
saturated histories, delegate sub-tasks to sub-agents with isolated contexts,
and retry failed execution paths ([He et al., 2026b](https://arxiv.org/html/2609.33848#bib.bib47); [Song et al., 2026a](https://arxiv.org/html/2609.33848#bib.bib49)).
As a result, a single task execution no longer yields a sequential trajectory,
but an intricate, non-linear graph of divergent context paths.
This non-linearity leads to an explosion in sample and token volume:
expanding all these paths into individual training samples introduces severe
redundancy across shared prefixes and incurs prohibitive training overhead.
The challenge is thus to reconstruct valid training representations from
such complex, branching executions while preventing the sheer volume of paths
and tokens from overwhelming the training pipeline.

In this paper, we present QwenGyre, an end-to-end
framework for online RL
through black-box agent harnesses at
xLong-horizons.
Its design separates the lifetimes of
harness executions,
GPU roles, and training samples. Harness
state persists
across GPU role changes, while recorded
model calls are
materialized into training samples on
demand.

To address Challenge 1, QwenGyre introduces an *elastic scheduler*, which
adjusts GPU allocation between rollout and training according to
the amount of unfinished rollout work while ensuring that model
calls from ongoing harness executions continue to be served.
Centralized data-parallel training allows newly available
nodes to join an ongoing batch as the training pool grows.
Streaming training distributes work according to each participating
data-parallel group’s progress, helping the groups finish the same
batch at similar times to minimize idle gaps.

To address Challenge 2, QwenGyre introduces a *trajectory processor*, which
organizes each execution’s recorded model calls into a trajectory
tree with shared prefixes, preserving each output’s original
conditioning context.
Task-specific evaluation scores preserved work after termination,
including assessable partial progress after timeout.
Once valid rewards are available, QwenGyre selects a bounded set of trajectories per execution by role priority to control training cost.
Training uses only policy-generated targets ([Gallouédec and Rasul, 2026](https://arxiv.org/html/2609.33848#bib.bib3)), counts shared targets once, and averages token losses within each execution to avoid overweighting executions with more paths.

We evaluate QwenGyre on NL2RepoBench ([Ding et al., 2026](https://arxiv.org/html/2609.33848#bib.bib18)),
DeepSWE ([Huang et al., 2026](https://arxiv.org/html/2609.33848#bib.bib14)), and TerminalBench ([Merrill et al., 2026](https://arxiv.org/html/2609.33848#bib.bib15))
using Qwen 3.6 122B. We also apply QwenGyre to
xLong RL training of our flagship model, Qwen 3.8 2.4T,
on NL2RepoBench.
We compare against Colocate and Async
baselines using equal GPU budgets
under the same staleness constraints.
Across the reported configurations, QwenGyre achieves end-to-end
speedups of 1.38 to 1.78 times over Async and 1.21 to 1.85 times
over Colocate while matching baseline training scores.
On NL2RepoBench, QwenGyre improves Qwen 3.8 2.4T’s score from
approximately 52.5 % to 58.5 % over 48 training steps.

In summary, this paper makes the
following contributions:

- •

  We identify the scheduling and
  trajectory-processing
  challenges of online RL for xLong
  agent executions.
- •

  We design an elastic scheduler that reallocates GPUs between
  rollout and training as demand changes, lets newly available GPUs
  join an ongoing training batch, and balances training work across
  them to reduce idle time.
- •

  We develop a trajectory processor that preserves each model
  output’s original context and evaluates partial work after timeouts.
  It selects a limited number of trajectories per execution, counts
  shared outputs once, and averages token losses within each execution.
- •

  We demonstrate QwenGyre on Qwen 3.8 2.4T,
  improving NL2RepoBench passrate from 52.5% to 58.5% in
  48 training steps. Across evaluated workloads, QwenGyre achieves
  up to `1.85\times` and `1.78\times` end-to-end speedups over
  Colocate and Async, respectively.

## 2 Background and Motivation

### 2.1 xLong Agentic RL Workloads

We first describe the group-relative RL pipeline and the
execution characteristics of xLong agentic workloads. We then
examine their implications for rollout–training scheduling and
training data construction.

Figure 2: Hierarchy of training bursts, rollout groups, and trajectories.
(a) Each burst performs `\mu` consecutive training steps, then publishes the policy; each step consumes `B` query groups.
(b) Each query produces `N` independent rollouts, and rollout `i`
yields `J_{i}` training trajectories.
(c) A rollout includes main-agent and sub-agent trajectories,
with compaction producing summary branches. Dashed links reinsert summaries into post-compaction contexts.

### Group-relative RL pipeline.

For each *query*, `N` independent rollouts sampled from the policy
form a *rollout group* (Figure [2](https://arxiv.org/html/2609.33848#S2.F2 "Figure 2 ‣ 2.1 xLong Agentic RL Workloads ‣ 2 Background and Motivation ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents")(b)). Advantages are computed
from the group’s scalar rewards, avoiding a learned value function
([Shao et al., 2024](https://arxiv.org/html/2609.33848#bib.bib2)). In our pipeline, each *training step*
consumes a *batch* of `B` distinct rollout groups and advances the policy version by one. To amortize the cost of weight publication, the RL framework may
perform `\mu` consecutive training steps between publications;
we call this interval a *burst*. Each burst consumes `\mu B`
rollout groups and publishes the weights at its final step,
as shown in Figure [2](https://arxiv.org/html/2609.33848#S2.F2 "Figure 2 ‣ 2.1 xLong Agentic RL Workloads ‣ 2 Background and Motivation ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents")(a).

### Harness-driven agentic RL

An agentic rollout is an end-to-end task execution in which a model
interacts with an environment through a harness. The harness
maintains task state, invokes tools according to model outputs,
and constructs context for subsequent model calls.
We call each model call–response interaction a *model calls*,
each tool invocation a *tool call*, and the full task lifecycle,
including retries, a *rollout execution*.
Figure [2](https://arxiv.org/html/2609.33848#S2.F2 "Figure 2 ‣ 2.1 xLong Agentic RL Workloads ‣ 2 Background and Motivation ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents")(c) shows an execution that branches at tool calls
and the trajectories selected from it for training.

In our black-box setting, the harness accesses the model through
a proxy provided by the RL framework. The framework records model calls
and receives task-level evaluation results without changing the
harness’s execution logic ([He et al., 2026b](https://arxiv.org/html/2609.33848#bib.bib47); [Song et al., 2026a](https://arxiv.org/html/2609.33848#bib.bib49)).
This interface provides no general mechanism to checkpoint and
resume a live execution. If a model call cannot be served, the
harness may stall or time out, changing the task outcome for
reasons unrelated to the policy’s decisions. Scheduling must
therefore preserve inference access throughout the execution.
Requests can be routed to different rollout instances while the harness
continues running.

### The xLong execution profile.

Recent software engineering benchmarks evaluate agents on repository
construction, program reimplementation, and migration across entire
codebases ([Ding et al., 2026](https://arxiv.org/html/2609.33848#bib.bib18); [Yang et al., 2026](https://arxiv.org/html/2609.33848#bib.bib19); [Desai et al., 2026](https://arxiv.org/html/2609.33848#bib.bib1); [Hong et al., 2026](https://arxiv.org/html/2609.33848#bib.bib20)).
We focus on xLong executions that last hours, span hundreds of
dependent model–environment interactions, and process around 1M
input and output tokens across model calls. This lifecycle volume
counts repeated contexts at each request and can exceed the context
limit of an individual request.

These workloads exhibit both long execution tails and clustered
terminations.
Execution durations vary across queries and within each rollout group:
generation length and tool latency affect the time per interaction
([Zhang et al., 2026b](https://arxiv.org/html/2609.33848#bib.bib25)).
Over hundreds of dependent interactions, these differences can leave
some executions running long after their peers finish.
Since group-relative advantages require all `N` rewards, a straggler
can delay training on its entire group.
Executions with similar start times and a common timeout budget may expire within a narrow interval, producing clusters of execution terminations that can sharply reduce inference demand.

### 2.2 Rollout–Training Scheduling

RL frameworks organize rollout and training through two scheduling
policies. A data *dispatch policy* controls when and how much
rollout work enters the pipeline. A GPU *placement policy*
allocates GPUs between rollout and training in space and time.
These policies can be combined to form different framework designs:
Async, for example, can use either continuous or
boundary dispatch.

### Data dispatch policy and staleness.

Under *boundary dispatch*, each rollout group enters the dispatch
queue when admitted and retains its slot until training consumes it.
Let `\varphi\geq 0` denote the extra dispatch in units of `B` rollout
groups. With `\mu` training steps per burst, the target queue depth is
`(\varphi+\mu)B` groups. The queue is filled to this depth at startup
and replenished with `\mu B` new groups after each burst’s weight
publication.

We measure a group’s *scheduling staleness* as `d=v_{t}-v_{d}`,
with policy versions indexed by training steps. Here, `v_{d}` is the
version of the latest published policy when the group is admitted,
and `v_{t}` is the policy version immediately before the step that
consumes it.

The target queue depth `Q_{\mathrm{b}}` and steady-state mean scheduling
staleness satisfy

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
|  | `\displaystyle Q_{\mathrm{b}}` | `\displaystyle=(\varphi+\mu)B,` |  | (1) |
|  |  |  |  |  |
| --- | --- | --- | --- | --- |
|  | `\displaystyle\mathbb{E}[d]` | `\displaystyle=\varphi+\frac{\mu-1}{2}.` |  | (2) |

The `\varphi` term accounts for extra dispatched groups, while
`\tfrac{\mu-1}{2}` averages the training-step positions within a burst,
indexed from zero.

### GPU placement policy and utilization.

*Async* assigns fixed GPU pools to rollout and training,
allowing the two stages to overlap ([Fu et al., 2025](https://arxiv.org/html/2609.33848#bib.bib33); [Zhong et al., 2025](https://arxiv.org/html/2609.33848#bib.bib35)).
Long rollout latency requires high concurrency to sustain throughput,
but increasing dispatch depth also raises scheduling staleness
(Equation [2](https://arxiv.org/html/2609.33848#S2.E2 "In Data dispatch policy and staleness. ‣ 2.2 Rollout–Training Scheduling ‣ 2 Background and Motivation ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents")).
Limiting dispatch depth can therefore leave training GPUs waiting for
data, while the fixed split prevents training from using spare rollout
capacity as executions finish (Figure [1](https://arxiv.org/html/2609.33848#S0.F1 "Figure 1 ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"),
Async).

*Colocate* alternates a shared GPU pool between rollout and
training, as supported by HybridFlow and ReaL
([Sheng et al., 2025](https://arxiv.org/html/2609.33848#bib.bib26); [Mei et al., 2025](https://arxiv.org/html/2609.33848#bib.bib28)).
Because the pool switches as a unit, training must wait for the rollout
tail even when groups are ready and GPUs are idle
(Figure [1](https://arxiv.org/html/2609.33848#S0.F1 "Figure 1 ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"), Colocate).
More steps per burst amortize switching and weight-publication costs,
but increase scheduling staleness for later steps.

### 2.3 From Harness Executions to Training Data

At xLong-horizons, context management and sub-agent delegation routinely
break the append-only history of a simple agent loop ([Yao et al., 2023](https://arxiv.org/html/2609.33848#bib.bib11); [Yang et al., 2024](https://arxiv.org/html/2609.33848#bib.bib10)).
Harnesses compact histories as context windows fill and maintain
separate contexts for sub-agents.

The harnesses used for these executions are also used in deployment, and
the most capable, such as Claude Code and Codex, are closed and evolve
rapidly; reimplementing their control flow inside an RL framework is
impractical and would train the policy under a harness different from
the one it is deployed with. This motivates the black-box interface of
Section [2.1](https://arxiv.org/html/2609.33848#S2.SS1 "2.1 xLong Agentic RL Workloads ‣ 2 Background and Motivation ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"), which exposes only model calls
and task-level evaluation results. Using these records for group-relative RL requires valid
outcome rewards and explicit choices of training targets and loss weights.

### Execution structure.

An execution can contain multiple *trajectories*. A trajectory
is a linear path of model calls in which each successive call
extends the preceding call’s recorded context and response.
Compaction and other context edits can rewrite an existing history
([He et al., 2026b](https://arxiv.org/html/2609.33848#bib.bib47)).
Calls may remain causally related across these changes without
forming one append-only history. A single agent or role can therefore
contribute multiple trajectories.
Concatenating requests across these boundaries as one history can give
responses contexts they did not have during generation.
Across hundreds of interactions, repeated context changes produce varying numbers of trajectories with different lengths.

### Reward validity.

An execution’s reward can fail to support training in two
distinct ways. First, an execution may reach its deadline before
completing the task ([Desai et al., 2026](https://arxiv.org/html/2609.33848#bib.bib1)): its captured trajectories
describe a partial attempt, and assigning all partial attempts the
same failure reward obscures differences in task progress. Second,
infrastructure or evaluator failures may leave no valid assessment at
all; a missing assessment is distinct from a valid zero reward and
cannot be filled in as one. Even after every execution in a group has
terminated, the group may therefore lack the `N` valid sample rewards
needed for advantage estimation.

### Training semantics.

A task-level outcome reward evaluates an execution of the original task.
Figure [2](https://arxiv.org/html/2609.33848#S2.F2 "Figure 2 ‣ 2.1 xLong Agentic RL Workloads ‣ 2 Background and Motivation ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents") illustrates the varying trajectory
counts: each query has `N` executions, while execution `i` contributes
`J_{i}` selected trajectories. A flat average of trajectory losses gives
executions with more selected paths greater aggregate weight
([He et al., 2026b](https://arxiv.org/html/2609.33848#bib.bib47)).
Within an execution, the same averaging can give many short auxiliary
paths more aggregate weight than a long main-agent path. A shared
response can likewise receive extra weight if each copy contributes
to the loss. The RL objective must therefore specify which roles, trajectories, and tokens contribute to the loss, together with the normalization and weighting rules.

## 3 QwenGyre Overview

Figure 3: Elastic scheduling and data flow in QwenGyre.
The sandbox hosts the harness and repository, linked by tool calls;
Solid and dashed control
links denote burst-boundary actions and waterlevel feedback,
respectively. Double lines show data flow; the buffer combines trajectory
storage and stream packing.

QwenGyre supports online RL through unmodified black-box agent
harnesses at xLong-horizons. Its architecture consists of two
cooperating parts (Figure [3](https://arxiv.org/html/2609.33848#S3.F3 "Figure 3 ‣ 3 QwenGyre Overview ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents")).
The elastic scheduler (Section [4](https://arxiv.org/html/2609.33848#S4 "4 Elastic Scheduler ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents")) reallocates
GPUs between rollout and training while allowing live harness
executions to continue.
The trajectory processor (Section [5](https://arxiv.org/html/2609.33848#S5 "5 Trajectory Processor ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"))
constructs training samples from recorded model calls,
retaining execution records independently of the samples admitted
for optimization.

### Elastic scheduler.

GPU resources comprise elastic cells
and an optional standalone rollout pool. Cells share a training parallel
layout; each can serve rollouts or host a complete training actor replica.
The black-box proxy, as part of the trajectory processor forwards model calls to rollout engines and
reroutes them during role changes, while harnesses and workspaces remain
outside GPU workers. The elastic scheduler dispatches rollout work at
startup and burst boundaries and tracks queued and running executions as the
rollout waterlevel.
As this level falls,
cells move to training when the
remaining rollout capacity covers outstanding work.
The core cell holds the authoritative weights and
alone maintains optimizer state. Satellite cells pull its
parameter snapshot and can join the ongoing batch before the rollout tail
completes.

### Trajectory processor.

The proxy records exact
model-request tokens and behavior log-probabilities in trajectory
trees that share common prefixes and preserve each output’s original
conditioning context. The evaluator scores each execution’s preserved
workspace, including assessable partial progress after timeout, and sends
the reward and its validity status to the buffer. At training admission,
QwenGyre computes group-relative advantages from the original execution
rewards and selects at most `J_{\max}` trajectories per execution by role
priority. Selected trajectories inherit their execution’s advantage. Only
policy-generated tokens are eligible targets, and shared targets contribute
once. Averaging losses over selected trainable tokens within each
execution, then over executions in the batch, prevents additional
trajectories from increasing an execution’s aggregate weight.

The two parts connect through a shared stream of training
micro-steps, allowing the core to begin a batch before all samples are
materialized. Execution termination lowers the scheduling waterlevel;
a group becomes ready for training only after all its executions have closed
and their designated outcomes are valid. The buffer in
Figure [3](https://arxiv.org/html/2609.33848#S3.F3 "Figure 3 ‣ 3 QwenGyre Overview ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents") stores execution records and associated rewards
and packs selected paths from ready groups on demand into micro-steps
carrying loss masks and weights. Training cells consume
this stream, and the core performs one optimizer update per batch.

Sections [4](https://arxiv.org/html/2609.33848#S4 "4 Elastic Scheduler ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents") and [5](https://arxiv.org/html/2609.33848#S5 "5 Trajectory Processor ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents") detail the
elastic scheduling and trajectory processing planes, respectively.

## 4 Elastic Scheduler

Figure 4: Illustrative timeline of a two-step burst.
The core (n0–n1) performs both optimizer updates.
Satellite cells join ongoing steps after pulling its current
parameters; n6–n7 stay in rollout during this burst.
Gradient reduction precedes each update; a parameter broadcast
follows the nonfinal update, and rollout policy publication follows
the final update. The core’s final role transition and local
publication (Pub.) occur only when it returns to rollout.

The elastic scheduling plane coordinates role
transitions and streaming training to use available GPUs while
serving ongoing rollouts.

### 4.1 Topology-Aware Resource Organization

### Cell layout and roles.

QwenGyre uses Megatron ([Shoeybi et al., 2019](https://arxiv.org/html/2609.33848#bib.bib6)) for training and
SGLang ([Zheng et al., 2024](https://arxiv.org/html/2609.33848#bib.bib7)) for rollout. Its `K` *elastic cells*
share a training parallel layout; an optional *standalone pool*
remains in rollout.
We favor small cells for fine-grained resource reallocation, subject to
parallelism and topology constraints. Tensor, pipeline, expert, and context
parallel groups remain within each cell, with placement favoring
high-bandwidth interconnects.

Cells follow a fixed order, with the *core cell* first and
*satellite cells* thereafter.
The core holds the authoritative weights and is the sole
optimizer owner.

### Rollout capacity.

Rollout capacity is measured as the number of concurrent rollout executions
allowed by QwenGyre. Let `C_{e}` and `C_{s}\geq 0` denote the
capacities of each elastic cell in rollout mode and the standalone pool, respectively, with `C_{s}=0`
when the standalone pool is absent. With `k(t)` cells assigned to training,
the available rollout capacity is

|  |  |  |  |
| --- | --- | --- | --- |
|  | `C_{R}(t)=C_{s}+\bigl(K-k(t)\bigr)C_{e}.` |  | (3) |

### 4.2 Boundary Dispatch and Waterlevel Control

### Boundary dispatch.

To implement boundary dispatch (Section [2.2](https://arxiv.org/html/2609.33848#S2.SS2 "2.2 Rollout–Training Scheduling ‣ 2 Background and Motivation ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents")),
the scheduler tracks three cumulative execution counts: `d(t)`
increases when executions are dispatched into the rollout queue,
`p(t)` increases when they launch, and `f(t)` increases when they
terminate. Thus
`d(t)-p(t)` counts queued executions, `p(t)-f(t)` counts running
executions, and `0\leq f(t)\leq p(t)\leq d(t)`.
Each launched execution increments `f(t)` exactly once on completion,
failure, timeout, or cancellation, including surplus executions under
oversampling. Model-request retries remain within the same execution and
leave all counters unchanged. Queued entries record the published
policy version at dispatch; harnesses and sandboxes are created at launch.

In execution units, the initial dispatch is `d(0)=(\varphi+\mu)NB`,
with `\mu NB` new executions dispatched after each burst’s weight
publication.
Whenever there is spare rollout capacity (Equation [3](https://arxiv.org/html/2609.33848#S4.E3 "In Rollout capacity. ‣ 4.1 Topology-Aware Resource Organization ‣ 4 Elastic Scheduler ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"))
and engines are ready to serve, the scheduler immediately fills available
slots by launching

|  |  |  |  |
| --- | --- | --- | --- |
|  | `\min\bigl\{d(t)-p(t),\ C_{R}(t)-\bigl(p(t)-f(t)\bigr)\bigr\}` |  | (4) |

queued executions and leaving any excess queued. The launches in
Equation [4](https://arxiv.org/html/2609.33848#S4.E4 "In Boundary dispatch. ‣ 4.2 Boundary Dispatch and Waterlevel Control ‣ 4 Elastic Scheduler ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents") use the existing quota, so `d(t)` remains
fixed within the burst.

### Waterlevel control and training supply.

The waterlevel `w(t)=d(t)-f(t)` is nonincreasing within a
burst. The next cell can join training only if the remaining
rollout capacity covers these outstanding executions:

|  |  |  |  |
| --- | --- | --- | --- |
|  | `w(t)\leq C_{R}(t)-C_{e}.` |  | (5) |

Equation [5](https://arxiv.org/html/2609.33848#S4.E5 "In Waterlevel control and training supply. ‣ 4.2 Boundary Dispatch and Waterlevel Control ‣ 4 Elastic Scheduler ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents") is paired with a supply check that
counts ready, unassigned groups, capped by the number of groups the
current batch still needs. This count must cover at least
a fraction `\rho_{\min}\in(0,1]` of the batch’s `B` groups continuously
for `\tau` before a transition begins. The timer resets after each
transition and at each batch start. Cells transition serially, core
first and then satellites by index, and remain in training throughout
the burst, forming a growing prefix.

### Burst-End Weight Sync and Core Retention.

After the burst’s final optimizer update, all training satellites
return to rollout and restore their SGLang engines. The core then
publishes the updated weights to all satellite and standalone rollout
engines, preparing them for the next burst.

After synchronization, the core remains in training only if at least
`\rho_{\min}B` ready, unassigned groups are available for the next batch
and the remaining rollout capacity covers outstanding work plus the
pending `\mu NB` executions:

|  |  |  |  |
| --- | --- | --- | --- |
|  | `w(t)+\mu NB\leq C_{s}+(K-1)C_{e}.` |  | (6) |

If either the supply check or Equation [6](https://arxiv.org/html/2609.33848#S4.E6 "In Burst-End Weight Sync and Core Retention. ‣ 4.2 Boundary Dispatch and Waterlevel Control ‣ 4 Elastic Scheduler ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents") fails,
the core returns to rollout and reshards its parameters into the local
SGLang (Figure [4](https://arxiv.org/html/2609.33848#S4.F4 "Figure 4 ‣ 4 Elastic Scheduler ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents")).

### 4.3 Harness-Preserving Role Transitions

### Request rerouting.

During a role transition, the proxy reroutes model calls
while the harness, workspace, and tool execution state remain in place.
The source cell first stops accepting new requests. The scheduler
reserves destination capacity for affected executions and updates their
routes, then cancels outstanding requests on the source engines.
The proxy transparently retries these requests at the destination
engines. The scheduler prioritizes available standalone engines,
followed by engines in rollout cells in descending cell order.
This ordering favors destinations expected to remain available longer,
reducing repeated rerouting of the same execution within a burst.

### KV-cache migration.

KV-cache migration can reduce prefix recomputation during
request rerouting. Before a request is canceled on the source engine, the
source pins the corresponding cache blocks. Once the request is canceled
and cache writes have stopped, the destination can read these blocks
through RDMA. The source releases the cache only after the destination
acknowledges receipt and takeover.

### Role-state management.

After request rerouting and cache handoff are complete, the cell
offloads rollout parameters and releases KV caches and temporary buffers
to reclaim GPU memory, then restores training parameters and buffers.
Backend processes and communication groups remain alive across role
changes.

### 4.4 Streaming Training with Dynamic Membership

### Centralized dynamic data parallelism.

To let satellites join an ongoing batch, the core exposes
buffers holding its authoritative weights through Mooncake’s
Transfer Engine during its transition from rollout to training for the
burst’s first step, and before each subsequent step.
While training on the current batch is still in progress, satellites
can join in the predefined cell order. Each satellite registers with
the scheduler, pulls the core’s weights via RDMA, and begins
training without interrupting the core (Figure [4](https://arxiv.org/html/2609.33848#S4.F4 "Figure 4 ‣ 4 Elastic Scheduler ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents")).
The weights remain fixed during gradient accumulation, so joining
satellites read a consistent snapshot. The controller closes the
joining window before the optimizer update.

After the entire batch has been processed, the core aggregates and
normalizes gradients from all training cells. It then applies gradient clipping and
performs a single optimizer update. After each nonfinal update, it
broadcasts the new parameters to the current satellites, which remain
in training for the next step.

For `K` ordered cells, we prebuild `K-1` sets of communication groups,
one for each prefix of `2,\ldots,K` cells. Within each set, groups
connect ranks holding corresponding model shards across cells.
Each collective uses the set matching its participating prefix.

### Streaming training.

Streaming training uses two buffers, shown as the Buffer in
Figure [3](https://arxiv.org/html/2609.33848#S3.F3 "Figure 3 ‣ 3 QwenGyre Overview ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"). The *trajectory buffer* stores execution
records and associated rewards by rollout group. The *stream
packing buffer* prepares training inputs on demand. When its buffered
trajectories run low, it pulls a ready group from the trajectory
buffer, prioritizing the oldest policy version. It materializes the
group’s selected trajectories into token rows and reorders the rows
for efficient packing.

The packing buffer emits training inputs in small *micro-steps*,
each providing data for a cell’s data-parallel ranks. Cells atomically
claim micro-steps from the packing buffer’s shared queue as compute
capacity becomes available, receiving disjoint work. Earlier or faster cells
consume more micro-steps, helping participating cells finish the batch
at similar times. The packing buffer selects the batch’s `B` groups
incrementally and closes the stream only after enqueuing all their
micro-steps.

Each cell processes incoming micro-steps with a continuous
one-forward-one-backward (1F1B) pipeline. All stages within a cell use
the same signal for input availability. When data are temporarily
unavailable, the stages complete outstanding communication and pause
at consistent scheduling points, preserving pipeline state. After the
stream closes and the queue is exhausted, the pipeline drains its
remaining work. Each cell that processes micro-steps therefore incurs
one startup and one final drain per batch.

## 5 Trajectory Processor

The trajectory processing plane constructs training samples
from harness execution records and task outcomes. During rollout,
QwenGyre preserves the exact model-request tokens and each
output’s original conditioning context using token-in, token-out (TITO) ([Gallouédec and Rasul, 2026](https://arxiv.org/html/2609.33848#bib.bib3))
(Section [5.1](https://arxiv.org/html/2609.33848#S5.SS1 "5.1 TITO and Trajectory Trees ‣ 5 Trajectory Processor ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents")). After an execution terminates,
QwenGyre evaluates its preserved work, including assessable partial
progress after timeout, under the task’s scoring rule to obtain
an execution-level reward
(Section [5.2](https://arxiv.org/html/2609.33848#S5.SS2 "5.2 Partial Scoring ‣ 5 Trajectory Processor ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents")).
At training admission, QwenGyre selects a bounded set of paths
per execution from ready groups by role priority and fixes target
masks so shared targets contribute once
(Section [5.3](https://arxiv.org/html/2609.33848#S5.SS3 "5.3 Trajectory Sampling ‣ 5 Trajectory Processor ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents")).

### 5.1 TITO and Trajectory Trees

### Request records with TITO

QwenGyre implements TITO in the
black-box proxy (Section [4.3](https://arxiv.org/html/2609.33848#S4.SS3 "4.3 Harness-Preserving Role Transitions ‣ 4 Elastic Scheduler ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents")) to maintain
a record of each model call.
Each record preserves the exact input and output token IDs, the output tokens’ behavior log-probabilities, and associated metadata.

To maintain these records across harness message processing,
the proxy also caches original tool-call payloads by call ID.
Before matching a subsequent request’s history, it restores these
payloads while preserving the incoming IDs for tool-response
association. This avoids spurious history mismatches caused by
tool-call reformatting.
The harness keeps its existing message interface, while training
consumes the recorded tokens and associated metadata.
Each output retains its original conditioning context even if
later compaction removes it from the harness’s history.

### Prefix sharing through trajectory trees

QwenGyre organizes the input/output tokens and associated metadata
in the TITO request records described above into a trajectory tree
for each execution, following the prefix representation used in
black-box agent training ([Song et al., 2026a](https://arxiv.org/html/2609.33848#bib.bib49)).
Each node is built from a request record and stores its incremental
input, recorded output, and associated metadata.
After the tool-call restoration described above, the framework
matches an incoming request’s serialized context against existing
paths and reuses the tokens stored in the matched nodes.
Only new input content is encoded, and the new request record is
appended as a node.
Diverging contexts create branches; requests with no matching
prefix attach to the root.
This organization captures the different context paths introduced
by compaction and sub-agent calls
(Figure [2](https://arxiv.org/html/2609.33848#S2.F2 "Figure 2 ‣ 2.1 xLong Agentic RL Workloads ‣ 2 Background and Motivation ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents")(c)), while retaining independently
generated outputs as separate nodes.

Candidate trajectories remain in this shared representation until
selection, avoiding full-history expansion for every path.
Selected paths are materialized from the stored token segments
and their aligned metadata.

### 5.2 Partial Scoring

### Scoring preserved work

At execution closure, QwenGyre fixes the committed
policy-generation request record and identifies any available
artifact state to assess.
QwenGyre evaluates the preserved work under the task’s scoring rule
after an execution terminates, including after timeout.
An unfinished execution can receive a valid score when
its completed work is assessable.
For these assessed outcomes, the data plane does not derive rewards
from elapsed time, trajectory length, or termination status.
Using executable checks or task-specific agentic
evaluation ([Zhuge et al., 2024](https://arxiv.org/html/2609.33848#bib.bib4)), the evaluator returns a score,
its validity status, and a reference to the assessed state.

### Preserving the scope of an assessment

An xLong execution may evaluate intermediate artifacts, revise
them, and abandon branches.
Each assessment remains associated with its execution,
artifact version, and available branch reference; later assessments
do not overwrite these associations.
A critique used by a subsequent policy request remains
part of its input, but its evaluator provenance excludes it from
policy training targets.
The designated task assessment supplies one reward for
each scored execution; intermediate assessments remain associated
with the states they evaluate.

### Handling failures

An evaluator failure leaves the assessment unresolved;
evaluation may be retried against the same preserved state within
the execution’s overall time budget.
If this budget expires without a valid reward, the recorded
trajectories are excluded from training.
An unresolved assessment is distinct from a valid zero score,
which remains usable for training.

For rare complete failures that leave no assessable work,
such as image-pull failures, QwenGyre inserts a dummy trajectory with
zero reward as a failure placeholder.

### 5.3 Trajectory Sampling

The trajectory tree records all context in the execution, which QwenGyre
turns into training data in two steps: it first masks every token that
should not be trained, and then converts the tree into individual
training trajectories.

### Trainable tokens are defined by provenance.

A node’s tokens are eligible training targets only if the policy produced
them during rollout. TITO (Section [5.1](https://arxiv.org/html/2609.33848#S5.SS1 "5.1 TITO and Trajectory Trees ‣ 5 Trajectory Processor ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents")) records
whether each token was emitted by our SGLang engines or supplied from
outside. System prompts, user prompts, tool results, and
assistant-role content the harness injects rather than samples from the
policy will be masked and carry no training signal: they are retained as
conditioning context only.

### Sampling trajectories from the tree.

Candidate trajectories correspond to the leaves of the trajectory tree:
a leaf together with the prefix path from the root defines one
trajectory. At xLong-horizons a single execution can produce many
candidate trajectories, and their number may vary widely across
executions. Simply retaining all trajectories may lead to a decrease in training efficiency, so QwenGyre retains at most `J_{\max}` training trajectories
per execution and fills this budget in order of expected importance. To
rank the candidates, QwenGyre classifies each leaf by the role of the request
sequence it terminates. For a Claude Code harness these classes are, for
the main agent and for each sub-agent, its task-driving trajectory and
its summary trajectory, ordered by the priority

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
|  | `\displaystyle\text{main}` | `\displaystyle>\text{main-summary}` |  | (7) |
|  |  | `\displaystyle>\text{sub-agent}>\text{sub-agent-summary}.` |  |

The ordering in Equation [7](https://arxiv.org/html/2609.33848#S5.E7 "In Sampling trajectories from the tree. ‣ 5.3 Trajectory Sampling ‣ 5 Trajectory Processor ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents") follows two
principles. The main agent’s turns are what the
task-level reward most directly credits, whereas sub-agent trajectories
contribute only through delegated subtasks; and within each agent, turns
that advance the task rank above the summary trajectory, which manages
context rather than acting on the task.

Admission starts from the provenance mask above and draws trajectories one at a time. Each step takes the
highest-priority class that still has a leaf with unmasked trainable
tokens, and draws one leaf from it with probability proportional to its
unmasked count. The drawn trajectory’s targets are fixed to the tokens
still unmasked at this draw; QwenGyre then masks its entire root-to-leaf
path in the tree. This keeps a shared prefix from being trained more than once and leaves
already-fixed targets untouched, while the lowered counts reweight the
remaining leaves for the next draw. Admission repeats until no unmasked
trainable token remains or `J_{\max}` trajectories are admitted, yielding
`J_{i}\leq J_{\max}` trajectories from execution `i`
(Figure [2](https://arxiv.org/html/2609.33848#S2.F2 "Figure 2 ‣ 2.1 xLong Agentic RL Workloads ‣ 2 Background and Motivation ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents")), each inheriting the execution’s
group-relative advantage.

The admitted trajectories retain their execution identities,
recorded contexts and behavior log-probabilities, and fixed target
masks. Materialization and packing preserve these annotations for the
execution-level objective.

## 6 Experimental Results

Figure 5: NL2RepoBench execution distributions with Qwen 3.6 122B
at `\mathbb{E}[d]=1.5` over steps 1–48.
(a) Query durations, measured as the longest of each query’s
16 rollout execution durations.
(b) Rollout execution durations.
(c) Total (solid) counts input and output tokens per rollout
tree; Decode (dashed) counts generated output tokens. Both count
shared prefixes once. The smoothed curves show shares per 50k tokens.
(d) Tool calls per rollout execution.
(e) Leaves per rollout tree.
In (b), pink and purple mark harness and overall timeouts, respectively;
executions with both flags appear only in purple.
Final bins labeled `\geq` collect values at or above the indicated thresholds.

Figure 6: Execution profile of QwenGyre on NL2RepoBench with Qwen 3.6 122B
at `\mathbb{E}[d]=1.5`.
(a) Cell roles during the first three bursts (steps 1–9).
(b) Each cell’s recorded training time as a fraction of the full
observation window. Cell 7 remains in rollout throughout this
interval.

Figure 7: NL2RepoBench results with Qwen 3.6 122B at `\mathbb{E}[d]=1` (left) and
`\mathbb{E}[d]=1.5` (right). Speedup is cumulative baseline time divided by
cumulative QwenGyre time. In (c,d), in-plot tables give speedups at
selected checkpoints: Async in the upper row and Colocate
in the lower row, with matching curve colors.
Max. `|\Delta\log p|` is the maximum absolute difference between
current-policy and recorded rollout-policy log-probabilities
over unmasked response tokens.

Figure 8: NL2RepoBench with Qwen 3.8 2.4T. (a) Measured query durations,
using the longest rollout execution wall time per query.
(b) Measured rollout execution durations.
The final bin collects durations `\geq 4.45` h.
In (b), pink and purple mark harness and overall timeouts,
respectively.
(c,d) Step times and cumulative speedups over 48 steps.
Arrows in (d) label speedups at selected checkpoints in matching colors.
(e,f) Training and evaluation scores.

### 6.1 Experimental Setup

### Tasks.

We evaluate QwenGyre on three agentic workloads: NL2RepoBench ([Ding et al., 2026](https://arxiv.org/html/2609.33848#bib.bib18)), DeepSWE ([Huang et al., 2026](https://arxiv.org/html/2609.33848#bib.bib14)), and TerminalBench ([Merrill et al., 2026](https://arxiv.org/html/2609.33848#bib.bib15)).
We construct training data internally for all three workloads.
For benchmark evaluation, we follow each benchmark’s prescribed evaluation protocol.
NL2RepoBench covers the xLong setting of building software repositories
from natural-language specifications;
during training, we use a separate Qwen 3.7-Max evaluator to score the
generated code using independently written tests.
DeepSWE covers software engineering in existing repositories;
during training, we use repository tests for evaluation.
TerminalBench comprises multi-turn terminal tasks;
during training, we use task-specific verifiers for evaluation.
All workloads use Claude Code 2.1.220 ([Anthropic, 2026](https://arxiv.org/html/2609.33848#bib.bib9)) to execute shell commands and
manipulate files in containerized environments.

### Models.

We use Qwen 3.6 122B and Qwen 3.8 2.4T.
For Qwen 3.6 122B, the NL2RepoBench experiments use 32 nodes, organized into
eight cells of four nodes each by default, with an inference concurrency limit of
144 per cell. The cell-granularity ablation also evaluates four
8-node cells under the same 32-node budget.
DeepSWE and TerminalBench follow the same protocol, using 24 nodes
organized into six cells with an inference concurrency limit of 192 per cell.
For Qwen 3.8 2.4T, the NL2RepoBench traces use four cells of 48 nodes each,
with a total inference concurrency limit of 384.
Unless otherwise stated, we use no dedicated standalone rollout nodes.

### RL algorithm.

All methods use our adaptation of Group Sequence Policy
Optimization (GSPO) ([Zheng et al., 2025](https://arxiv.org/html/2609.33848#bib.bib5)), combining token-level importance
weighting with execution-level clipping. Token importance weights
are capped at 5, and the sequence-level clipping bounds are
`[0.995,1.005]`. Each group contains 16 independent rollout executions;
each update consumes 32 groups for NL2RepoBench or 48 for DeepSWE
and TerminalBench. The default trajectory cap is `J_{\max}=5` per rollout
execution. All methods use Adam ([Kingma and Ba, 2015](https://arxiv.org/html/2609.33848#bib.bib8)) with a constant
learning rate of `10^{-6}`.

### Baselines.

We compare QwenGyre with two scheduling baselines.
*Async* assigns separate, fixed GPU pools to rollout
and training, allowing training steps to consume ready rollout groups
while other executions continue. It uses boundary dispatch with a
target queue depth, refilling consumed groups’ slots after weight
publication.
*Colocate* alternates a shared GPU pool between rollout and
training. Once the admitted rollout executions finish, the entire pool
switches to training and processes the completed rollout groups in a
burst of consecutive training steps.

We compare methods at common target values of mean scheduling
staleness `\mathbb{E}[d]`, defined in
Section [2.2](https://arxiv.org/html/2609.33848#S2.SS2 "2.2 Rollout–Training Scheduling ‣ 2 Background and Motivation ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"). All three methods use boundary
dispatch; we choose the extra-dispatch parameter `\varphi` and the
number of training steps per burst `\mu` using
Equation [2](https://arxiv.org/html/2609.33848#S2.E2 "In Data dispatch policy and staleness. ‣ 2.2 Rollout–Training Scheduling ‣ 2 Background and Motivation ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"). The original Colocate cannot
dispatch extra groups without interrupting the harness, so it uses
`\varphi=0`. For example, at `\mathbb{E}[d]=1.5`, Async can use
`\mu=1` with `\varphi=1.5`, Colocate uses `\mu=4` with `\varphi=0`,
and QwenGyre can use `\mu=3` with `\varphi=0.5`.

### 6.2 End-to-End Performance

### NL2RepoBench on Qwen 3.6 122B

Figure [5](https://arxiv.org/html/2609.33848#S6.F5 "Figure 5 ‣ 6 Experimental Results ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents") shows mean durations of 1.93 hours
per rollout execution and 2.96 hours per query; 9.51% of queries
take at least four hours.
Figure [5](https://arxiv.org/html/2609.33848#S6.F5 "Figure 5 ‣ 6 Experimental Results ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents")(b) shows harness and overall
timeout rates of 6.25% and 0.87%, respectively.
Harness timeouts indicate that task execution has timed out; the results
are still scored and used for training.
Failed evaluations can be retried within the overall execution
time budget. An overall timeout exhausts this budget before a valid
reward is obtained, so the execution is discarded from training.

Figure [7](https://arxiv.org/html/2609.33848#S6.F7 "Figure 7 ‣ 6 Experimental Results ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents")(a–d) shows that QwenGyre achieves
`1.42`–`1.53\times` speedups over Async and `1.36`–`1.47\times`
over Colocate after 48 training steps at both mean scheduling staleness targets.
Figure [7](https://arxiv.org/html/2609.33848#S6.F7 "Figure 7 ‣ 6 Experimental Results ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents")(e,f) shows
comparable training-score curves across methods, indicating that faster
training is achieved while maintaining task performance.

The role timeline in Figure [6](https://arxiv.org/html/2609.33848#S6.F6 "Figure 6 ‣ 6 Experimental Results ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents")(a) shows how QwenGyre
dynamically allocates resources between training and inference.
Cells enter training at different points while other cells remain in rollout.
Figure [6](https://arxiv.org/html/2609.33848#S6.F6 "Figure 6 ‣ 6 Experimental Results ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents")(b) shows how training time shares vary
across cells over the full observation window.
This staggered allocation allows training to begin with a subset of
cells and subsequently expand. It uses resources that a fixed
Async partition leaves assigned to rollout and avoids requiring
Colocate’s pool-wide phase transition before training can proceed.
The average switching times are 8.52 s for rollout to training
and 3.46 s for training to rollout.
Both are negligible compared with rollout executions lasting hours.

### NL2RepoBench on Qwen 3.8 2.4T

On NL2RepoBench, Qwen 3.8 2.4T has a higher timeout rate than
Qwen 3.6 122B, even though we extend the timeout limit.
Figure [8](https://arxiv.org/html/2609.33848#S6.F8 "Figure 8 ‣ 6 Experimental Results ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents")(a,b) shows the query and rollout execution duration
distributions. Among queries with complete duration records,
61.1% take at least four hours, compared with 9.51% for
Qwen 3.6 122B.
In 38.2% of these queries, the longest rollout execution terminates with
an overall timeout.

As shown in Figure [8](https://arxiv.org/html/2609.33848#S6.F8 "Figure 8 ‣ 6 Experimental Results ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents")(c,d), QwenGyre completes
48 training steps in 75.42 hours, compared with 134.55 hours for Async
and 91.47 hours for Colocate, yielding end-to-end speedups of
`1.78\times` and `1.21\times`, respectively. The concentration of query durations
near the timeout limit helps
explain the difference in gains over the two baselines. It suggests
fewer opportunities for QwenGyre to reclaim cells early and expand
training gradually, consistent with the smaller gain over Colocate,
which also shares its resource pool between training and rollout.
Async’s fixed partition leaves resources reserved for training
unavailable to rollout, even when training is idle. By dynamically
allocating these resources to rollout, QwenGyre can increase inference
capacity during long executions, yielding a larger gain over Async.

Figure [8](https://arxiv.org/html/2609.33848#S6.F8 "Figure 8 ‣ 6 Experimental Results ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents")(e) shows that QwenGyre’s training
scores match those of Async and Colocate. Its evaluation passrate
improves from 52.48% to 58.54% over 48 training steps
(Figure [8](https://arxiv.org/html/2609.33848#S6.F8 "Figure 8 ‣ 6 Experimental Results ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents")(f)).

### DeepSWE and TerminalBench on Qwen 3.6 122B

DeepSWE and TerminalBench share the same end-to-end evaluation protocol: Qwen 3.6
122B, 24 training steps, and all three methods (QwenGyre, Async, and
Colocate) at target mean scheduling staleness values `\mathbb{E}[d]=1` and `1.5`.
Table [2](https://arxiv.org/html/2609.33848#S6.T2 "Table 2 ‣ DeepSWE and TerminalBench on Qwen 3.6 122B ‣ 6.2 End-to-End Performance ‣ 6 Experimental Results ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents") reports the resulting cumulative speedups.

Table 1: Scheduling ablations over the first 12 NL2RepoBench training
steps with Qwen 3.6 122B at `\mathbb{E}[d]=1.5`.
A0, C0, and E0 reuse the Async, Colocate,
and QwenGyre base configurations from Section [6.2](https://arxiv.org/html/2609.33848#S6.SS2 "6.2 End-to-End Performance ‣ 6 Experimental Results ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
Arrows show the evolution paths; E1 and E2 branch independently
from E0.
Switch is – for fixed partitions, Global for switching all nodes
together, Coarse for switching the Colocate pool together,
and Fine for switching cells independently. Standalone nodes remain
in rollout. Allocation lists training/rollout (T/R) or
Colocate/standalone (C/S) node counts; cell entries give
cells `\times` nodes per cell. Total is the time for all 12 steps
in hours; Time / E0 normalizes it to E0. Lower is better.

|  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ID |  | Evolution | Stream | Switch | `({\varphi},\mu)` | Allocation | Total (h) | Time / E0 |
| A0 |  | Original Async | Disabled | – | `(1.5,1)` | 16 T / 16 R | 25.08 | 1.556 |
| A1 |  | A0 with adjusted partition | Disabled | – | `(1.5,1)` | 8 T / 24 R | 27.01 | 1.676 |
| A2 |  | A0 + multi-step burst | Disabled | – | `(0.5,3)` | 16 T / 16 R | 32.58 | 2.021 |
| A3 |  | A0 + streaming | Enabled | – | `(1.5,1)` | 16 T / 16 R | 22.18 | 1.376 |
| C0 |  | Original Colocate | Disabled | Global | `(0,4)` | 32 C / 0 S | 23.23 | 1.442 |
| C1 |  | C0 + standalone rollout nodes | Disabled | Coarse | `(0.5,3)` | 28 C / 4 S | 22.56 | 1.400 |
| C2 |  | A3 + role switching; C1 + streaming | Enabled | Coarse | `(0.5,3)` | 28 C / 4 S | 19.23 | 1.193 |
| C3 |  | C2 with adjusted allocation | Enabled | Coarse | `(0.5,3)` | 16 C / 16 S | 20.69 | 1.284 |
| E0 |  | C2 + fine-grained elastic allocation | Enabled | Fine | `(0.5,3)` | 8 cells `\times` 4 | 16.12 | 1.000 |
| E1 |  | E0 with one step per burst | Enabled | Fine | `(1.5,1)` | 8 cells `\times` 4 | 17.87 | 1.109 |
| E2 |  | E0 with four 8-node cells | Enabled | Fine | `(0.5,3)` | 4 cells `\times` 8 | 16.47 | 1.022 |

Table 2: 24-step speedup of QwenGyre over each baseline with
Qwen 3.6 122B. The `(\varphi,\mu)` column gives QwenGyre’s
extra dispatch in batch units and training steps per burst.
Async uses `(\varphi,\mu)=(\mathbb{E}[d],1)`; Colocate uses
`(\varphi,\mu)=(0,2\mathbb{E}[d]+1)`, following
Equation [2](https://arxiv.org/html/2609.33848#S2.E2 "In Data dispatch policy and staleness. ‣ 2.2 Rollout–Training Scheduling ‣ 2 Background and Motivation ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").

| Dataset | `\mathbb{E}[d]` | `({\varphi},\mu)` | vs. Async | vs. Colocate |
| --- | --- | --- | --- | --- |
| DeepSWE | 1 | `(0.5,2)` | 1.569 | 1.610 |
| DeepSWE | 1.5 | `(0.5,3)` | 1.572 | 1.824 |
| TerminalBench | 1 | `(0.5,2)` | 1.383 | 1.809 |
| TerminalBench | 1.5 | `(0.5,3)` | 1.430 | 1.849 |

Across the reported DeepSWE and TerminalBench configurations, QwenGyre provides
consistent end-to-end speedups over both Async and Colocate.

### 6.3 Ablation Study

Table [1](https://arxiv.org/html/2609.33848#S6.T1 "Table 1 ‣ DeepSWE and TerminalBench on Qwen 3.6 122B ‣ 6.2 End-to-End Performance ‣ 6 Experimental Results ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents") traces two paths toward QwenGyre:
adding streaming training to Async and adding standalone rollout
capacity to Colocate.

### Adding streaming to Async.

Reallocating nodes from training to rollout (A0 to A1) increases
end-to-end time by 7.7%. Although training nodes wait for rollout data,
executions finish in bursts; the smaller training pool consumes these
bursts more slowly, delaying weight publication and replacement
rollouts under boundary dispatch. Longer training bursts (A2) increase
time by 29.9% relative to A0 because the fixed rollout pool cannot
supply them efficiently. Streaming (A3) instead reduces time by 11.6%
by starting training on completed queries before a full batch is ready.
However, streaming captures only part of the potential gain.
The fundamental limitation remains Async’s fixed resource
partition:
it cannot reallocate idle GPUs between training and rollout as
their demands change.

### Adding standalone rollout nodes to Colocate.

while the colocated pool switches to training, preserving
harness
state. Although extra dispatch mitigates the impact of rollout
stragglers, fewer training steps are completed per burst,
limiting
the end-to-end improvement over C0 to just 2.9%.

Adding streaming to C1 (C2) reduces time by 14.8%. However,
all 28
colocated nodes must still switch together, so streaming
training
can begin only late in the burst. Increasing standalone
capacity
(C3) shrinks the pool that must switch together, but also
leaves
fewer nodes for training. The resulting longer training phase
delays burst completion and the next dispatch, increasing
end-to-end time by 7.6% relative to C2.
The fundamental limitation is the coarse switching granularity,
which prevents training from fully using the idle capacity that
emerges as colocated rollouts finish at different times.

### Combining streaming and fine-grained allocation.

E0 builds on C2 by replacing its fixed split of 28 colocated
nodes
and four standalone rollout nodes with eight independently
switching
4-node cells, while retaining streaming and three training
steps per
burst. Training can thus start on a subset of cells and expand
as
data arrives while other cells continue rollout, yielding a
`1.19\times` speedup over C2.

E1 retains E0’s streaming and cell allocation but uses one
training
step per burst, with extra dispatch increased from `0.5` to
`1.5`
to preserve scheduling staleness. Although E1 takes 10.9%
longer
than E0, it still achieves a `1.24\times` speedup over A3,
which
also uses streaming and one training step per burst, and a
`1.08\times` speedup over C2. These results show that fine-
grained
allocation provides substantial gains even without multi-step
bursts; longer bursts offer an additional benefit.

Streaming makes rollout data available for training earlier,
while fine-grained allocation supplies training resources
as that data arrives.

### Cell granularity.

E2 builds on E0 by regrouping the same 32 nodes from eight
4-node cells into four 8-node cells, retaining streaming and
`(\varphi,\mu)=(0.5,3)`. It completes the 12 training steps in
16 hours 28 minutes (16.47 hours), only 2.2% longer than E0’s
16.12 hours. In E0, rollout fully hides training, with 20.85%
slack remaining. E2’s coarser cell granularity exposes a small
amount of training on the critical path, while most training
remains overlapped with rollout. This explains the modest impact
of reducing the number of cells from eight to four in this setting.

### Trajectory sampling budget.

Sampling only the main trajectory per execution is insufficient:
it yields lower training scores and larger gradient norms over
the first 42 training steps
(Figure [9](https://arxiv.org/html/2609.33848#S6.F9 "Figure 9 ‣ Trajectory sampling budget. ‣ 6.3 Ablation Study ‣ 6 Experimental Results ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents")). Increasing the budget
(Section [5.3](https://arxiv.org/html/2609.33848#S5.SS3 "5.3 Trajectory Sampling ‣ 5 Trajectory Processor ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents")) to five trajectories matches the
scores obtained by sampling all available trajectories, with similarly
small gradient norms. Over the same window, mean forward–backward
time per step with caps of one and five is 41.4% and 74.8% of the
uncapped baseline, respectively. A cap of five therefore preserves
comparable training scores while reducing forward–backward time by
25.2%.

Figure 9: Trajectory-budget ablation for QwenGyre on NL2RepoBench
with Qwen 3.6 122B over training steps 1–42.
(a) Gradient norm on a logarithmic scale.
(b) Mean training score. Max traj 1 samples only the main
trajectory per execution; Max traj 5 admits up to five trajectories;
“Uncapped” uses all available leaf trajectories.

## 7 Related Work

### Agentic RL execution.

General-purpose LLM RL frameworks such as HybridFlow/veRL, OpenRLHF,
ReaL, and ROLL compose rollout, reference, reward, and policy-update
workers under different placement strategies
 ([Sheng et al., 2025](https://arxiv.org/html/2609.33848#bib.bib26); [Hu et al., 2025](https://arxiv.org/html/2609.33848#bib.bib27); [Mei et al., 2025](https://arxiv.org/html/2609.33848#bib.bib28); [Wang et al., 2025b](https://arxiv.org/html/2609.33848#bib.bib29)). Agent-oriented runtimes extend
these abstractions with multi-turn tools, containerized environments,
asynchronous dispatch, and trajectory-level scheduling
 ([Jiang et al., 2026](https://arxiv.org/html/2609.33848#bib.bib50); [Wang et al., 2025c](https://arxiv.org/html/2609.33848#bib.bib51); [Zhang et al., 2025](https://arxiv.org/html/2609.33848#bib.bib22); [Cao et al., 2025](https://arxiv.org/html/2609.33848#bib.bib23); [Zhang et al., 2026a](https://arxiv.org/html/2609.33848#bib.bib24); [Zhang et al., 2026b](https://arxiv.org/html/2609.33848#bib.bib25)).

Synchronous RL frameworks preserve explicit policy-update boundaries but expose
rollout-length skew. Recent work mitigates this tail through scheduling,
length-aware packing, partial-rollout continuation, and tail isolation
 ([Qin et al., 2026](https://arxiv.org/html/2609.33848#bib.bib30); [Gao et al., 2026a](https://arxiv.org/html/2609.33848#bib.bib31); [Zhou et al., 2025](https://arxiv.org/html/2609.33848#bib.bib32); [Xu et al., 2026b](https://arxiv.org/html/2609.33848#bib.bib52)). Asynchronous RL frameworks instead
stream trajectories between disaggregated rollout and trainer pools,
using bounded staleness, multiple policy versions, or fixed-weight
trajectory groups to control training semantics
 ([Fu et al., 2025](https://arxiv.org/html/2609.33848#bib.bib33); [Han et al., 2025](https://arxiv.org/html/2609.33848#bib.bib34); [Li et al., 2026](https://arxiv.org/html/2609.33848#bib.bib36); [Hu et al., 2026](https://arxiv.org/html/2609.33848#bib.bib37); [Chen et al., 2026b](https://arxiv.org/html/2609.33848#bib.bib38)). SAO and SPO++ further
adapt policy optimization to asynchronously arriving agent trajectories
 ([Hou et al., 2026](https://arxiv.org/html/2609.33848#bib.bib39); [Ruan et al., 2026](https://arxiv.org/html/2609.33848#bib.bib53)).

### Elastic rollout–training scheduling.

Recent RL frameworks dynamically adjust the resource boundary between rollout
and training. TideRL adapts rollout and reference execution using
readiness signals ([Ren et al., 2026b](https://arxiv.org/html/2609.33848#bib.bib40)); BiDiRL allows either side of an
asynchronous pipeline to borrow idle resources from the other
 ([Tan et al., 2026](https://arxiv.org/html/2609.33848#bib.bib41)); and DynaResize reallocates GPUs between rollout and
training pools using communicator reuse and state staging
 ([Du et al., 2026a](https://arxiv.org/html/2609.33848#bib.bib42)). Libra combines a global resource planner with an
elastic hybrid pool whose workers can join training as additional
data-parallel replicas ([Chen et al., 2026a](https://arxiv.org/html/2609.33848#bib.bib54)). Other RL frameworks obtain elasticity
from complementary phases across RL jobs, online-serving clusters, or
preemptible rollout resources ([Wu et al., 2026a](https://arxiv.org/html/2609.33848#bib.bib43); [Gao et al., 2026b](https://arxiv.org/html/2609.33848#bib.bib44); [Wu et al., 2026b](https://arxiv.org/html/2609.33848#bib.bib45)), while
AReaL-DTE reduces cross-role policy synchronization through sparse weight
transfer ([Peng et al., 2026](https://arxiv.org/html/2609.33848#bib.bib55)).

### Black-box harnesses and structured trajectories.

Harness-native RL frameworks connect opaque agent runtimes to policy
optimization by instrumenting or proxying model calls. Agent Lightning
decouples agent execution from training, while Polar and LEGO-RL preserve
rollout-time token identity under harness-controlled context processing
 ([Luo et al., 2025b](https://arxiv.org/html/2609.33848#bib.bib46); [He et al., 2026b](https://arxiv.org/html/2609.33848#bib.bib47); [Xu et al., 2026a](https://arxiv.org/html/2609.33848#bib.bib48); [Du et al., 2026b](https://arxiv.org/html/2609.33848#bib.bib17)). ClawGym II
reconstructs captured requests as shared-prefix trees and adapts PPO and
GRPO so that each shared node contributes training signal only once
 ([Song et al., 2026a](https://arxiv.org/html/2609.33848#bib.bib49)); its retained paths share a reward derived from the
final workspace evaluation.

Related work exploits execution structure at other
layers. BPO, IAPO,
and MileGPO use branches, dependency graphs, or
intermediate milestones
for finer-grained credit
assignment ([He et al., 2026a](https://arxiv.org/html/2609.33848#bib.bib56); [Ren et al., 2026a](https://arxiv.org/html/2609.33848#bib.bib57); [Qian et al., 2026](https://arxiv.org/html/2609.33848#bib.bib58)), whereas
psRL and related frameworks reuse shared
prefixes
after sample construction
 ([Yu et al., 2026](https://arxiv.org/html/2609.33848#bib.bib59); [Wang et al., 2025a](https://arxiv.org/html/2609.33848#bib.bib21)).
These techniques address trajectory capture, credit
assignment, or
prefix computation individually. QwenGyre instead
couples
readiness-driven actor reconfiguration with a
trajectory processor
preserving role, branch, environment-state,
and evaluator
provenance throughout xLong rollout collection,
admission, and
training materialization.

## 8 Limitations

### GPU budget and cell granularity.

Elastic scheduling needs multiple independently switchable cells
while maintaining enough rollout capacity to serve unfinished
executions. Each cell must accommodate the model’s memory and
training parallelism requirements, so a very small GPU budget may
not support this organization. Such deployments are generally
impractical for the resource-intensive xLong workloads targeted
here. Within our evaluated regime, a modest number of cells is
sufficient: under the same 32-node budget, regrouping eight 4-node
cells (E0) into four 8-node cells (E2) increases execution time by
only 2.2% (Table [1](https://arxiv.org/html/2609.33848#S6.T1 "Table 1 ‣ DeepSWE and TerminalBench on Qwen 3.6 122B ‣ 6.2 End-to-End Performance ‣ 6 Experimental Results ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents")). E0 fully hides
training behind rollout, while E2 exposes a small amount of training
on the critical path. Most of the overlap benefit is therefore
retained with four cells in this setting. This result concerns cell
granularity at a fixed budget; efficiency under substantially smaller
total GPU budgets remains unevaluated.

### Shuffling with streaming training.

With multiple training steps per burst (`\mu>1`), streaming training
assigns ready rollout groups incrementally to successive updates.
The current design therefore cannot globally shuffle data across all
minibatches before the burst starts. Supporting such a shuffle would
require waiting for the complete burst’s data before its first update,
delaying training and sacrificing some overlap with rollout. This
constrains training procedures that depend on globally randomized
minibatch assignment. Single-step bursts (`\mu=1`) avoid the
cross-minibatch split while retaining elastic allocation and streaming.
At matched scheduling staleness, E1 takes 10.9% longer than E0,
but still achieves a `1.24\times` speedup over streaming Async (A3)
and a `1.08\times` speedup over Colocate with streaming (C2)
(Table [1](https://arxiv.org/html/2609.33848#S6.T1 "Table 1 ‣ DeepSWE and TerminalBench on Qwen 3.6 122B ‣ 6.2 End-to-End Performance ‣ 6 Experimental Results ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents")). Thus, multi-step bursts provide
an additional efficiency gain, while single-step bursts remain a
practical option. These ablations quantify execution time; the effect
of sample ordering on learning quality has not been isolated.

## 9 Conclusion

We presented QwenGyre, which combines elastic scheduling and trajectory
processing for online RL through unmodified harnesses at xLong-horizons. It reallocates GPUs while preserving live executions and
constructs bounded training samples with original contexts and balanced
execution-level contributions. We demonstrate these capabilities through
xLong RL training of our flagship model, Qwen 3.8 2.4T.
Across three workloads, QwenGyre achieves up to `1.78\times` speedup over
Async and `1.85\times` over Colocate under equal GPU budgets and
matched scheduling staleness, with comparable training scores.

## References

- Anthropic (2026)
  Anthropic
  Claude Code.
  Note: Official software repository
  External Links: [Link](https://github.com/anthropics/claude-code)
  Cited by: [§6.1](https://arxiv.org/html/2609.33848#S6.SS1.SSS0.Px1.p1.1 "Tasks. ‣ 6.1 Experimental Setup ‣ 6 Experimental Results ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Cao et al. (2025)
  S. Cao, D. Li, F. Zhao, S. Yuan, S. R. Hegde, C. Chen, C. Ruan, T. Griggs, S. Liu, E. Tang, R. Liaw, P. Moritz, M. Zaharia, J. E. Gonzalez, and I. Stoica
  SkyRL-Agent: efficient RL training for multi-turn LLM agent.
  External Links: 2511.16108,
  [Link](https://arxiv.org/abs/2511.16108)
  Cited by: [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px1.p1.1 "Agentic RL execution. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Chen et al. (2026a)
  K. Chen, X. Tan, J. Li, and H. Xu
  Libra: efficient resource management for agentic RL post-training.
  External Links: 2606.03077,
  [Link](https://arxiv.org/abs/2606.03077)
  Cited by: [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px2.p1.1 "Elastic rollout–training scheduling. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Chen et al. (2026b)
  R. Chen, J. Hu, K. Ye, and M. Xu
  RolloutPipe: overlapping pipelined rollout and training in disaggregated on-policy LLM reinforcement learning.
  In Proceedings of the 2026 International Conference on Cognitive Computing (ICCC 2026),
  External Links: 2606.26997,
  [Link](https://arxiv.org/abs/2606.26997)
  Cited by: [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px1.p2.1 "Agentic RL execution. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Deng et al. (2026)
  X. Deng, J. Da, E. Pan, Y. Y. He, C. Ide, K. Garg, N. Lauffer, A. Park, C. Rane, K. Sampath, M. Krishnan, S. Kundurthy, S. Hendryx, Z. Wang, C. B. C. Zhang, N. Jacobson, B. Liu, and B. Kenstler
  SWE-Bench Pro: can AI agents solve long-horizon software engineering tasks?.
  In Proceedings of the 43rd International Conference on Machine Learning,
  Proceedings of Machine Learning Research, Vol. 306.
  External Links: [Link](https://icml.cc/virtual/2026/poster/61047)
  Cited by: [§1](https://arxiv.org/html/2609.33848#S1.p1.1 "1 Introduction ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Desai et al. (2026)
  R. Desai, J. Hu, J. Cabezas, N. Harsola, P. Shukla, R. B. Chaim, A. E. Assadi, O. M. Kamath, F. Faldu, P. Hebbar, J. Sun, Y. Li, P. Srinivasan, I. Gupta, C. Settles, D. Wang, D. Chen, P. Raja, A. Liu, M. Šuppa, N. Sasikumar, L. Kong, E. Quintanilla, X. Li, I. Bercovich, and S. Dillmann
  SWE-Marathon: can agents autonomously complete ultra-long-horizon software work?.
  External Links: 2606.07682,
  [Link](https://arxiv.org/abs/2606.07682)
  Cited by: [§2.1](https://arxiv.org/html/2609.33848#S2.SS1.SSS0.Px3.p1.1 "The xLong execution profile. ‣ 2.1 xLong Agentic RL Workloads ‣ 2 Background and Motivation ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"),
  [§2.3](https://arxiv.org/html/2609.33848#S2.SS3.SSS0.Px2.p1.1 "Reward validity. ‣ 2.3 From Harness Executions to Training Data ‣ 2 Background and Motivation ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Ding et al. (2026)
  J. Ding, S. Long, C. Pu, G. Zhang, H. Zhou, H. Gao, X. Gao, C. He, Y. Hou, F. Hu, Z. Li, W. Shi, Z. Wang, D. Zan, C. Zhang, X. Zhang, Q. Chen, X. Cheng, B. Deng, Q. Gu, K. Hua, J. Lin, P. Liu, M. Li, M. Li, X. Pan, Z. Peng, Y. Qin, Y. Shan, Z. Tan, H. Wang, T. Tang, W. Xie, Y. Yuan, J. Zhang, Y. Zhao, H. Zhu, L. Zhu, C. Zou, M. Ding, J. Jiao, J. Liu, L. Liu, Q. Liu, C. Tao, J. Yang, T. Yang, Z. Zhang, X. Chen, and W. Huang
  NL2Repo-Bench: towards long-horizon repository generation evaluation of coding agents.
  In Proceedings of the 43rd International Conference on Machine Learning,
  Proceedings of Machine Learning Research, Vol. 306.
  External Links: [Link](https://icml.cc/virtual/2026/poster/60772)
  Cited by: [§1](https://arxiv.org/html/2609.33848#S1.p2.1 "1 Introduction ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"),
  [§1](https://arxiv.org/html/2609.33848#S1.p8.1 "1 Introduction ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"),
  [§2.1](https://arxiv.org/html/2609.33848#S2.SS1.SSS0.Px3.p1.1 "The xLong execution profile. ‣ 2.1 xLong Agentic RL Workloads ‣ 2 Background and Motivation ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"),
  [§6.1](https://arxiv.org/html/2609.33848#S6.SS1.SSS0.Px1.p1.1 "Tasks. ‣ 6.1 Experimental Setup ‣ 6 Experimental Results ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Du et al. (2026a)
  H. Du, Z. Yan, Y. Bao, and S. Wang
  DynaResize: runtime GPU reallocation for disaggregated LLM post-training.
  External Links: 2607.22614,
  [Link](https://arxiv.org/abs/2607.22614)
  Cited by: [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px2.p1.1 "Elastic rollout–training scheduling. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Du et al. (2026b)
  Y. Du, Y. Jiang, T. Yuan, J. Dai, S. Wang, J. Chen, C. Tao, X. Yu, L. Shang, K. Wong, X. Li, and H. Bai
  LEGO-RL: harness-native reinforcement learning for coding agents.
  External Links: 2608.17393,
  [Link](https://arxiv.org/abs/2608.17393)
  Cited by: [§1](https://arxiv.org/html/2609.33848#S1.p1.1 "1 Introduction ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"),
  [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px3.p1.1 "Black-box harnesses and structured trajectories. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Fu et al. (2025)
  W. Fu, J. Gao, X. Shen, C. Zhu, Z. Mei, C. He, S. Xu, G. Wei, J. Mei, J. Wang, T. Yang, B. Yuan, and Y. Wu
  AReaL: a large-scale asynchronous reinforcement learning system for language reasoning.
  In Advances in Neural Information Processing Systems,
  Vol. 38, pp. 36256–36282.
  External Links: [Document](https://dx.doi.org/10.52202/085713-1218),
  [Link](https://proceedings.neurips.cc/paper_files/paper/2025/hash/33c00862bfa29ac72ecf630a41e19352-Abstract-Conference.html)
  Cited by: [§1](https://arxiv.org/html/2609.33848#S1.p3.1 "1 Introduction ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"),
  [§2.2](https://arxiv.org/html/2609.33848#S2.SS2.SSS0.Px2.p1.1 "GPU placement policy and utilization. ‣ 2.2 Rollout–Training Scheduling ‣ 2 Background and Motivation ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"),
  [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px1.p2.1 "Agentic RL execution. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Gallouédec and Rasul (2026)
  Q. Gallouédec and K. Rasul
  Agentic RL: token-in, token-out done right.
  Note: Hugging Face Blog
  External Links: [Link](https://huggingface.co/blog/huggingface/tito)
  Cited by: [§1](https://arxiv.org/html/2609.33848#S1.p7.1 "1 Introduction ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"),
  [§5](https://arxiv.org/html/2609.33848#S5.p1.1 "5 Trajectory Processor ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Gao et al. (2026a)
  W. Gao, Y. Zhao, D. An, T. Wu, L. Cao, S. Xiong, J. Huang, W. Wang, S. Yang, W. Su, J. Wang, L. Qu, B. Zheng, and W. Wang
  RollPacker: taming long-tail rollouts for RL post-training with tail batching.
  In 23rd USENIX Symposium on Networked Systems Design and Implementation (NSDI 26),
  Renton, WA, pp. 849–866.
  External Links: ISBN 978-1-939133-54-0,
  [Link](https://www.usenix.org/conference/nsdi26/presentation/gao-wei)
  Cited by: [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px1.p2.1 "Agentic RL execution. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Gao et al. (2026b)
  W. Gao, Y. Zhao, D. Muhtar, D. An, X. Shang, T. Wu, L. Cao, S. Xiong, W. Wang, J. Huang, T. Ma, S. Yang, J. Wang, L. Qu, B. Zheng, and W. Wang
  ROSE: rollout on serving GPUs via cooperative elasticity for agentic RL.
  External Links: 2605.06534,
  [Link](https://arxiv.org/abs/2605.06534)
  Cited by: [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px2.p1.1 "Elastic rollout–training scheduling. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Golubev et al. (2025)
  A. Golubev, M. Trofimova, S. Polezhaev, I. Badertdinov, M. Nekrashevich, A. Shevtsov, S. Karasik, S. Abramov, A. Andriushchenko, F. Fisin, S. Skvortsov, and B. Yangel
  Training long-context, multi-turn software engineering agents with reinforcement learning.
  External Links: 2508.03501,
  [Link](https://arxiv.org/abs/2508.03501)
  Cited by: [§1](https://arxiv.org/html/2609.33848#S1.p1.1 "1 Introduction ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Han et al. (2025)
  Z. Han, A. You, H. Wang, K. Luo, G. Yang, W. Shi, M. Chen, S. Zhang, Z. Lan, C. Deng, H. Ji, W. Liu, Y. Huang, Y. Zhang, C. Pan, J. Wang, X. Huang, C. Li, and J. Wu
  AsyncFlow: an asynchronous streaming RL framework for efficient LLM post-training.
  External Links: 2507.01663,
  [Link](https://arxiv.org/abs/2507.01663)
  Cited by: [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px1.p2.1 "Agentic RL execution. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- He et al. (2026a)
  B. He, Y. Chen, X. Zhang, and X. Liu
  Branching policy optimization: sandbox-native language agent reinforcement learning.
  In World Artificial Intelligence Conference Academic (WAICA),
  Note: Main Conference
  External Links: 2607.14171,
  [Link](https://arxiv.org/abs/2607.14171)
  Cited by: [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px3.p2.1 "Black-box harnesses and structured trajectories. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- He et al. (2026b)
  Z. He, S. Zhang, Z. Zhou, Y. Yang, Y. Kang, Y. Zhang, L. K. Qiu, T. Y. Tsui, J. Xu, and C. Luo
  Agent Lightning v1.0: towards harnessed agentic RL.
  External Links: 2608.17528,
  [Link](https://arxiv.org/abs/2608.17528)
  Cited by: [§1](https://arxiv.org/html/2609.33848#S1.p4.1 "1 Introduction ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"),
  [§2.1](https://arxiv.org/html/2609.33848#S2.SS1.SSS0.Px2.p2.1 "Harness-driven agentic RL ‣ 2.1 xLong Agentic RL Workloads ‣ 2 Background and Motivation ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"),
  [§2.3](https://arxiv.org/html/2609.33848#S2.SS3.SSS0.Px1.p1.1 "Execution structure. ‣ 2.3 From Harness Executions to Training Data ‣ 2 Background and Motivation ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"),
  [§2.3](https://arxiv.org/html/2609.33848#S2.SS3.SSS0.Px3.p1.1 "Training semantics. ‣ 2.3 From Harness Executions to Training Data ‣ 2 Background and Motivation ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"),
  [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px3.p1.1 "Black-box harnesses and structured trajectories. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Hong et al. (2026)
  D. Hong, Y. Chi, W. Li, X. Wang, M. Gao, K. Yang, B. He, Y. Zheng, C. Xiao, and Q. Na
  SWE Refactor Bench: can coding agents complete a long-horizon, whole-repository stack migration?.
  External Links: 2608.23564,
  [Link](https://arxiv.org/abs/2608.23564)
  Cited by: [§1](https://arxiv.org/html/2609.33848#S1.p2.1 "1 Introduction ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"),
  [§2.1](https://arxiv.org/html/2609.33848#S2.SS1.SSS0.Px3.p1.1 "The xLong execution profile. ‣ 2.1 xLong Agentic RL Workloads ‣ 2 Background and Motivation ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Hou et al. (2026)
  Z. Hou, Y. Li, J. Tang, and Y. Dong
  Single-rollout asynchronous optimization for agentic reinforcement learning.
  External Links: 2607.07508,
  [Link](https://arxiv.org/abs/2607.07508)
  Cited by: [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px1.p2.1 "Agentic RL execution. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Hu et al. (2025)
  J. Hu, X. Wu, W. Shen, J. K. Liu, W. Wang, S. Jiang, H. Wang, H. Chen, B. Chen, W. Fang, Xianyu, Y. Cao, H. Xu, and Y. Liu
  OpenRLHF: a ray-based easy-to-use, scalable and high-performance RLHF framework.
  In Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing: System Demonstrations,
  Suzhou, China, pp. 656–666.
  External Links: [Document](https://dx.doi.org/10.18653/v1/2025.emnlp-demos.48),
  [Link](https://aclanthology.org/2025.emnlp-demos.48/)
  Cited by: [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px1.p1.1 "Agentic RL execution. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Hu et al. (2026)
  T. Hu, X. Liu, Y. Miao, Y. Xiao, H. Zang, Y. Zheng, X. Huang, J. Ding, Y. Zhang, Y. Yang, Y. Zhang, Y. Sun, C. Han, X. Ma, W. Wang, Q. Gu, Y. Sun, Y. Xie, and X. Cai
  DORA: a scalable asynchronous reinforcement learning system for language model training.
  External Links: 2604.26256,
  [Link](https://arxiv.org/abs/2604.26256)
  Cited by: [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px1.p2.1 "Agentic RL execution. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Huang et al. (2026)
  W. Huang, C. Lee, L. Tng, and S. Ge
  DeepSWE: measuring frontier coding agents on original, long-horizon engineering tasks.
  External Links: 2607.07946,
  [Link](https://arxiv.org/abs/2607.07946)
  Cited by: [§1](https://arxiv.org/html/2609.33848#S1.p8.1 "1 Introduction ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"),
  [§6.1](https://arxiv.org/html/2609.33848#S6.SS1.SSS0.Px1.p1.1 "Tasks. ‣ 6.1 Experimental Setup ‣ 6 Experimental Results ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Jiang et al. (2026)
  D. Jiang, Y. Lu, Z. Li, Z. Lyu, P. Nie, H. Wang, A. Su, H. Chen, K. Zou, C. Du, T. Pang, and W. Chen
  VerlTool: towards holistic agentic reinforcement learning with tool use.
  Transactions on Machine Learning Research.
  External Links: 2509.01055,
  [Link](https://arxiv.org/abs/2509.01055)
  Cited by: [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px1.p1.1 "Agentic RL execution. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Jimenez et al. (2024)
  C. E. Jimenez, J. Yang, A. Wettig, S. Yao, K. Pei, O. Press, and K. Narasimhan
  SWE-bench: can language models resolve real-world GitHub issues?.
  In International Conference on Learning Representations,
  pp. 54107–54157.
  External Links: [Link](https://proceedings.iclr.cc/paper_files/paper/2024/file/edac78c3e300629acfe6cbe9ca88fb84-Paper-Conference.pdf)
  Cited by: [§1](https://arxiv.org/html/2609.33848#S1.p1.1 "1 Introduction ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Kingma and Ba (2015)
  D. P. Kingma and J. Ba
  Adam: a method for stochastic optimization.
  In The Third International Conference on Learning Representations,
  External Links: [Link](https://arxiv.org/abs/1412.6980)
  Cited by: [Appendix B](https://arxiv.org/html/2609.33848#A2.SS0.SSS0.Px1.p2.1 "Training configuration. ‣ Appendix B RL Algorithm Details ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"),
  [§6.1](https://arxiv.org/html/2609.33848#S6.SS1.SSS0.Px3.p1.1 "RL algorithm. ‣ 6.1 Experimental Setup ‣ 6 Experimental Results ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Li et al. (2026)
  H. Li, S. Lin, F. Fu, Y. Zhou, X. Ji, Y. Zhao, L. Wang, J. Jiang, and B. Cui
  StaleFlow: staleness-aware data management for mitigating data skewness in fully disaggregated RL post-training.
  Note: To appear at ACM SIGMOD 2027
  External Links: 2601.12784,
  [Link](https://arxiv.org/abs/2601.12784)
  Cited by: [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px1.p2.1 "Agentic RL execution. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Luo et al. (2025a)
  M. Luo, N. Jain, J. Singh, S. Tan, A. Patel, Q. Wu, A. Ariyak, C. Cai, T. Venkat, S. Zhu, B. Athiwaratkun, M. Roongta, C. Zhang, L. E. Li, R. A. Popa, K. Sen, and I. Stoica
  DeepSWE: training a fully open-sourced, state-of-the-art coding agent by scaling RL.
  Note: Together AI research blog
  External Links: [Link](https://www.together.ai/blog/deepswe)
  Cited by: [§1](https://arxiv.org/html/2609.33848#S1.p1.1 "1 Introduction ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Luo et al. (2025b)
  X. Luo, Y. Zhang, Z. He, Z. Wang, S. Zhao, D. Li, L. K. Qiu, and Y. Yang
  Agent Lightning: train ANY AI agents with reinforcement learning.
  External Links: 2508.03680,
  [Link](https://arxiv.org/abs/2508.03680)
  Cited by: [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px3.p1.1 "Black-box harnesses and structured trajectories. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Mei et al. (2025)
  Z. Mei, W. Fu, K. Li, G. Wang, H. Zhang, and Y. Wu
  ReaL: efficient RLHF training of large language models with parameter reallocation.
  In Proceedings of Machine Learning and Systems,
  Vol. 7.
  External Links: [Link](https://proceedings.mlsys.org/paper_files/paper/2025/hash/3b3889d313ba9476c12c2d77ea66b24f-Abstract-Conference.html)
  Cited by: [§1](https://arxiv.org/html/2609.33848#S1.p3.1 "1 Introduction ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"),
  [§2.2](https://arxiv.org/html/2609.33848#S2.SS2.SSS0.Px2.p2.1 "GPU placement policy and utilization. ‣ 2.2 Rollout–Training Scheduling ‣ 2 Background and Motivation ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"),
  [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px1.p1.1 "Agentic RL execution. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Merrill et al. (2026)
  M. Merrill, A. Shaw, N. Carlini, B. Li, H. Raj, I. Bercovich, L. Shi, J. Shin, T. Walshe, E. K. Buchanan, J. Shen, G. Ye, H. Lin, J. Poulos, M. Wang, M. Nezhurina, D. Lu, O. M. Mastromichalakis, Z. Xu, Z. Chen, Y. Liu, R. Zhang, L. L. Chen, A. Kashyap, J. Uslu, J. Li, J. Wu, M. Yan, S. Bian, V. Sharma, K. Sun, S. Dillmann, A. Anand, A. Lanpouthakoun, B. Koopah, C. Hu, E. Guha, G. Dreiman, J. Zhu, K. Krauth, L. Zhong, N. Muennighoff, R. Amanfu, S. Tan, S. Pimpalgaonkar, T. Aggarwal, X. Lin, X. Lan, X. Zhao, Y. Liang, Y. Wang, Z. (. Wang, C. Zhou, D. Heineman, H. Liu, H. Trivedi, J. Yang, J. Lin, M. Shetty, M. Yang, N. Omi, N. Raoof, S. Li, T. Y. Zhuo, W. Lin, Y. Dai, Y. Wang, W. Chai, S. Zhou, D. Wahdany, Z. She, J. Hu, Z. Dong, Y. Zhu, S. Cui, A. Saiyed, A. Kolbeinsson, C. Rytting, R. Marten, Y. Wang, J. Jitsev, A. Dimakis, A. Konwinski, and L. Schmidt
  Terminal-Bench: benchmarking agents on hard, realistic tasks in command line interfaces.
  In International Conference on Learning Representations,
  Vol. 2026, pp. 40903–40986.
  External Links: [Link](https://proceedings.iclr.cc/paper_files/paper/2026/file/444a3737adaee10d86ad2ef5f74468e6-Paper-Conference.pdf)
  Cited by: [§1](https://arxiv.org/html/2609.33848#S1.p8.1 "1 Introduction ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"),
  [§6.1](https://arxiv.org/html/2609.33848#S6.SS1.SSS0.Px1.p1.1 "Tasks. ‣ 6.1 Experimental Setup ‣ 6 Experimental Results ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Peng et al. (2026)
  Y. Peng, J. Zhang, W. Zhou, R. Xu, R. Yan, W. Dong, Y. Gao, Z. Ding, T. Yang, and B. Yuan
  AReaL-DTE: sparse policy-weight transfer for online agentic reinforcement learning.
  External Links: 2608.00455,
  [Link](https://arxiv.org/abs/2608.00455)
  Cited by: [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px2.p1.1 "Elastic rollout–training scheduling. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Qian et al. (2026)
  B. Qian, Y. Wu, S. Zeng, H. Wan, D. Zhang, and J. Liu
  MileGPO: milestone inference with local evidence for graph-based policy optimization of long-horizon LLM agents.
  External Links: 2608.19803,
  [Link](https://arxiv.org/abs/2608.19803)
  Cited by: [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px3.p2.1 "Black-box harnesses and structured trajectories. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Qin et al. (2026)
  R. Qin, W. He, W. Huang, Y. Zhang, Y. Zhao, B. Pang, X. Xu, Y. Shan, Y. Wu, and M. Zhang
  Seer: online context learning for fast synchronous LLM reinforcement learning.
  In 20th USENIX Symposium on Operating Systems Design and Implementation (OSDI 26),
  Seattle, WA, pp. 883–901.
  External Links: ISBN 978-1-939133-55-7,
  [Link](https://www.usenix.org/conference/osdi26/presentation/qin)
  Cited by: [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px1.p2.1 "Agentic RL execution. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Ren et al. (2026a)
  B. Ren, Y. Mao, Y. Yang, and W. Que
  IAPO: influence-aware policy optimization for credit assignment in multi-turn service agents.
  External Links: 2608.24588,
  [Link](https://arxiv.org/abs/2608.24588)
  Cited by: [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px3.p2.1 "Black-box harnesses and structured trajectories. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Ren et al. (2026b)
  Y. Ren, X. Wang, X. Liu, B. Lv, H. Zhang, S. Zhang, H. Lai, S. Wang, L. Chen, D. Li, and J. Tang
  TideRL: boosting agentic RL goodput with readiness-aware scheduling.
  External Links: 2608.10402,
  [Link](https://arxiv.org/abs/2608.10402)
  Cited by: [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px2.p1.1 "Elastic rollout–training scheduling. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Ruan et al. (2026)
  K. Ruan, J. Lin, Q. Wei, Z. Zhou, and Z. Huang
  SPO++: stream-aligned policy optimization for asynchronous agentic RL.
  External Links: 2608.24870,
  [Link](https://arxiv.org/abs/2608.24870)
  Cited by: [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px1.p2.1 "Agentic RL execution. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Shao et al. (2024)
  Z. Shao, P. Wang, Q. Zhu, R. Xu, J. Song, X. Bi, H. Zhang, M. Zhang, Y. K. Li, Y. Wu, and D. Guo
  DeepSeekMath: pushing the limits of mathematical reasoning in open language models.
  External Links: 2402.03300,
  [Link](https://arxiv.org/abs/2402.03300)
  Cited by: [§2.1](https://arxiv.org/html/2609.33848#S2.SS1.SSS0.Px1.p1.1 "Group-relative RL pipeline. ‣ 2.1 xLong Agentic RL Workloads ‣ 2 Background and Motivation ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Sheng et al. (2025)
  G. Sheng, C. Zhang, Z. Ye, X. Wu, W. Zhang, R. Zhang, Y. Peng, H. Lin, and C. Wu
  HybridFlow: a flexible and efficient RLHF framework.
  In Proceedings of the Twentieth European Conference on Computer Systems,
  pp. 1279–1297.
  External Links: [Document](https://dx.doi.org/10.1145/3689031.3696075),
  [Link](https://doi.org/10.1145/3689031.3696075)
  Cited by: [§1](https://arxiv.org/html/2609.33848#S1.p3.1 "1 Introduction ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"),
  [§2.2](https://arxiv.org/html/2609.33848#S2.SS2.SSS0.Px2.p2.1 "GPU placement policy and utilization. ‣ 2.2 Rollout–Training Scheduling ‣ 2 Background and Motivation ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"),
  [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px1.p1.1 "Agentic RL execution. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Shoeybi et al. (2019)
  M. Shoeybi, M. Patwary, R. Puri, P. LeGresley, J. Casper, and B. Catanzaro
  Megatron-LM: training multi-billion parameter language models using model parallelism.
  External Links: 1909.08053,
  [Link](https://arxiv.org/abs/1909.08053)
  Cited by: [§4.1](https://arxiv.org/html/2609.33848#S4.SS1.SSS0.Px1.p1.1 "Cell layout and roles. ‣ 4.1 Topology-Aware Resource Organization ‣ 4 Elastic Scheduler ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Song et al. (2026a)
  H. Song, F. Bai, M. Yang, R. Li, J. Deng, J. He, Z. Zhang, D. Cheng, Y. Xing, Q. Yun, X. Chen, D. Li, F. Chang, C. Hao, R. Tao, J. Yang, B. Dai, W. X. Zhao, M. Tang, and J. Wen
  ClawGym II: exploring black-box RL on agent harness.
  External Links: 2608.16798,
  [Link](https://arxiv.org/abs/2608.16798)
  Cited by: [§1](https://arxiv.org/html/2609.33848#S1.p4.1 "1 Introduction ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"),
  [§2.1](https://arxiv.org/html/2609.33848#S2.SS1.SSS0.Px2.p2.1 "Harness-driven agentic RL ‣ 2.1 xLong Agentic RL Workloads ‣ 2 Background and Motivation ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"),
  [§5.1](https://arxiv.org/html/2609.33848#S5.SS1.SSS0.Px2.p1.1 "Prefix sharing through trajectory trees ‣ 5.1 TITO and Trajectory Trees ‣ 5 Trajectory Processor ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"),
  [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px3.p1.1 "Black-box harnesses and structured trajectories. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Song et al. (2026b)
  H. Song, L. Huang, S. Sun, J. Jiang, R. Le, D. Cheng, G. Chen, Y. Hu, Z. Chen, Y. Jia, W. X. Zhao, Y. Song, T. Zhang, and J. Wen
  SWE-Master: unleashing the potential of software engineering agents via post-training.
  External Links: 2602.03411,
  [Link](https://arxiv.org/abs/2602.03411)
  Cited by: [§1](https://arxiv.org/html/2609.33848#S1.p1.1 "1 Introduction ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Tan et al. (2026)
  Z. Tan, M. Wang, S. Wang, Y. Yin, Q. Wang, X. Chu, and S. Shi
  Bidirectional resource scheduling for disaggregated and asynchronous RL post-training.
  External Links: 2607.09207,
  [Link](https://arxiv.org/abs/2607.09207)
  Cited by: [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px2.p1.1 "Elastic rollout–training scheduling. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Wang et al. (2025a)
  J. Wang, S. Wang, Y. Cui, X. Chen, C. Wang, L. Huang, C. Tang, X. Zhang, J. Peng, L. Wan, H. Zhang, and B. Chen
  Tree training: accelerating agentic LLMs training via shared prefix reuse.
  External Links: 2511.00413,
  [Link](https://arxiv.org/abs/2511.00413)
  Cited by: [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px3.p2.1 "Black-box harnesses and structured trajectories. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Wang et al. (2025b)
  W. Wang, S. Xiong, G. Chen, W. Gao, S. Guo, Y. He, J. Huang, J. Liu, Z. Li, X. Li, Z. Liu, H. Zhao, D. An, L. Cao, Q. Cao, W. Deng, F. Du, Y. Gu, J. Li, X. Li, M. Liu, Y. Luo, Z. Liu, Y. Wang, P. Wang, T. Wu, Y. Wu, Y. Zhao, S. Zhao, J. Yang, S. Yang, Y. Tan, H. Yi, Y. Xu, Y. Yuan, X. Zhang, L. Qu, W. Su, W. Wang, J. Wang, and B. Zheng
  Reinforcement learning optimization for large-scale learning: an efficient and user-friendly scaling library.
  External Links: 2506.06122,
  [Link](https://arxiv.org/abs/2506.06122)
  Cited by: [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px1.p1.1 "Agentic RL execution. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Wang et al. (2025c)
  Z. Wang, K. Wang, Q. Wang, P. Zhang, L. Li, Z. Yang, X. Jin, K. Yu, M. N. Nguyen, L. Liu, E. Gottlieb, Y. Lu, K. Cho, J. Wu, F. Li, L. Wang, Y. Choi, and M. Li
  RAGEN: understanding self-evolution in LLM agents via multi-turn reinforcement learning.
  External Links: 2504.20073,
  [Link](https://arxiv.org/abs/2504.20073)
  Cited by: [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px1.p1.1 "Agentic RL execution. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Wu et al. (2026a)
  T. Wu, L. Cao, Y. Wei, W. Gao, Y. Zhao, D. An, S. Xiong, Z. Lv, J. Huang, S. Yang, Y. Yu, J. Wang, L. Qu, and W. Wang
  Weave: efficient Co-Scheduling for disaggregated RL Post-Training.
  In 20th USENIX Symposium on Operating Systems Design and Implementation (OSDI 26),
  Seattle, WA, pp. 809–827.
  External Links: ISBN 978-1-939133-55-7,
  [Link](https://www.usenix.org/conference/osdi26/presentation/wu-tianyuan)
  Cited by: [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px2.p1.1 "Elastic rollout–training scheduling. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Wu et al. (2026b)
  Y. Wu, X. Liu, H. Zheng, J. Gu, B. Chen, Z. M. Mao, A. Krishnamurthy, and I. Stoica
  RLBoost: harvesting preemptible cloud resources for cost-efficient reinforcement learning on LLMs.
  In 23rd USENIX Symposium on Networked Systems Design and Implementation (NSDI 26),
  Renton, WA, pp. 1323–1339.
  External Links: ISBN 978-1-939133-54-0,
  [Link](https://www.usenix.org/conference/nsdi26/presentation/wu-yongji)
  Cited by: [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px2.p1.1 "Elastic rollout–training scheduling. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Xu et al. (2026a)
  B. Xu, H. Zhang, S. Zhang, S. Han, M. Liu, J. Hu, S. Diao, Z. Jin, Y. Zou, M. Demoret, J. Kautz, and Y. Dong
  Polar: agentic RL on any harness at scale.
  External Links: 2605.24220,
  [Link](https://arxiv.org/abs/2605.24220)
  Cited by: [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px3.p1.1 "Black-box harnesses and structured trajectories. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Xu et al. (2026b)
  T. Xu, L. Lv, H. Huang, W. Huang, Z. Shen, Y. Shen, B. Zhang, X. Hu, S. Ge, J. Dai, T. Liu, S. Yang, Z. Li, Y. Bai, J. Zhang, L. Chen, Y. Li, and M. Wan
  TailSieve: partial-rollout-guided tail routing for LLM rollouts.
  External Links: 2608.22788,
  [Link](https://arxiv.org/abs/2608.22788)
  Cited by: [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px1.p2.1 "Agentic RL execution. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Yang et al. (2024)
  J. Yang, C. E. Jimenez, A. Wettig, K. Lieret, S. Yao, K. Narasimhan, and O. Press
  SWE-agent: agent-computer interfaces enable automated software engineering.
  In Advances in Neural Information Processing Systems,
  Vol. 37, pp. 50528–50652.
  External Links: [Document](https://dx.doi.org/10.52202/079017-1601),
  [Link](https://proceedings.neurips.cc/paper_files/paper/2024/hash/5a7c947568c1b1328ccc5230172e1e7c-Abstract-Conference.html)
  Cited by: [§1](https://arxiv.org/html/2609.33848#S1.p4.1 "1 Introduction ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"),
  [§2.3](https://arxiv.org/html/2609.33848#S2.SS3.p1.1 "2.3 From Harness Executions to Training Data ‣ 2 Background and Motivation ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Yang et al. (2026)
  J. Yang, K. Lieret, J. Ma, P. Thakkar, D. Pedchenko, S. Sootla, E. McMilin, P. Yin, R. Hou, G. Synnaeve, D. Yang, and O. Press
  ProgramBench: can language models rebuild programs from scratch?.
  External Links: 2605.03546,
  [Link](https://arxiv.org/abs/2605.03546)
  Cited by: [§1](https://arxiv.org/html/2609.33848#S1.p2.1 "1 Introduction ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"),
  [§2.1](https://arxiv.org/html/2609.33848#S2.SS1.SSS0.Px3.p1.1 "The xLong execution profile. ‣ 2.1 xLong Agentic RL Workloads ‣ 2 Background and Motivation ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Yao et al. (2023)
  S. Yao, J. Zhao, D. Yu, N. Du, I. Shafran, K. Narasimhan, and Y. Cao
  ReAct: synergizing reasoning and acting in language models.
  In The Eleventh International Conference on Learning Representations,
  External Links: [Link](https://openreview.net/forum?id=WE_vluYUL-X)
  Cited by: [§1](https://arxiv.org/html/2609.33848#S1.p4.1 "1 Introduction ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"),
  [§2.3](https://arxiv.org/html/2609.33848#S2.SS3.p1.1 "2.3 From Harness Executions to Training Data ‣ 2 Background and Motivation ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Yu et al. (2026)
  M. Yu, Z. Mo, H. Qu, Z. Qian, H. Xu, C. Li, Z. Zhao, Z. Zhou, J. Zhou, J. Xie, and C. Xu
  psRL: efficient training for agentic AI via training-time prefix sharing.
  External Links: 2608.25683,
  [Link](https://arxiv.org/abs/2608.25683)
  Cited by: [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px3.p2.1 "Black-box harnesses and structured trajectories. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Zhang et al. (2025)
  H. Zhang, X. Liu, B. Lv, X. Sun, B. Jing, I. L. Iong, Z. Hou, Z. Qi, H. Lai, Y. Xu, R. Lu, H. Wang, J. Tang, and Y. Dong
  AgentRL: scaling agentic reinforcement learning with a multi-turn, multi-task framework.
  External Links: 2510.04206,
  [Link](https://arxiv.org/abs/2510.04206)
  Cited by: [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px1.p1.1 "Agentic RL execution. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Zhang et al. (2026a)
  L. Zhang, M. Chen, R. Cao, J. Chen, F. Zhou, Y. Xu, J. Yang, Z. Ma, L. Chen, C. Luo, K. Zhang, F. Yan, K. Shum, J. Zhang, Z. Cui, F. Hu, J. Lin, B. Hui, and M. Yang
  MegaFlow: large-scale distributed orchestration system for the agentic era.
  External Links: 2601.07526,
  [Link](https://arxiv.org/abs/2601.07526)
  Cited by: [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px1.p1.1 "Agentic RL execution. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Zhang et al. (2026b)
  Z. Zhang, Y. Zhong, C. Yang, C. Jin, B. Wu, X. Wei, Y. Liu, and X. Jin
  Heddle: a distributed orchestration system for agentic RL rollout.
  External Links: 2603.28101,
  [Link](https://arxiv.org/abs/2603.28101)
  Cited by: [§2.1](https://arxiv.org/html/2609.33848#S2.SS1.SSS0.Px3.p2.1 "The xLong execution profile. ‣ 2.1 xLong Agentic RL Workloads ‣ 2 Background and Motivation ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"),
  [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px1.p1.1 "Agentic RL execution. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Zheng et al. (2025)
  C. Zheng, S. Liu, M. Li, X. Chen, B. Yu, C. Gao, K. Dang, Y. Liu, R. Men, A. Yang, J. Zhou, and J. Lin
  Group sequence policy optimization.
  External Links: 2507.18071,
  [Link](https://arxiv.org/abs/2507.18071)
  Cited by: [Appendix B](https://arxiv.org/html/2609.33848#A2.SS0.SSS0.Px1.p1.1 "Training configuration. ‣ Appendix B RL Algorithm Details ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"),
  [§6.1](https://arxiv.org/html/2609.33848#S6.SS1.SSS0.Px3.p1.1 "RL algorithm. ‣ 6.1 Experimental Setup ‣ 6 Experimental Results ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Zheng et al. (2024)
  L. Zheng, L. Yin, Z. Xie, C. Sun, J. Huang, C. H. Yu, S. Cao, C. Kozyrakis, I. Stoica, J. E. Gonzalez, C. Barrett, and Y. Sheng
  SGLang: efficient execution of structured language model programs.
  In Advances in Neural Information Processing Systems,
  Vol. 37, pp. 62557–62583.
  External Links: [Document](https://dx.doi.org/10.52202/079017-2000),
  [Link](https://doi.org/10.52202/079017-2000)
  Cited by: [§4.1](https://arxiv.org/html/2609.33848#S4.SS1.SSS0.Px1.p1.1 "Cell layout and roles. ‣ 4.1 Topology-Aware Resource Organization ‣ 4 Elastic Scheduler ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Zhong et al. (2025)
  Y. Zhong, Z. Zhang, X. Song, H. Hu, C. Jin, B. Wu, N. Chen, Y. Chen, Y. Zhou, C. Wan, H. Zhou, Y. Jiang, Y. Zhu, and D. Jiang
  StreamRL: scalable, heterogeneous, and elastic RL for LLMs with disaggregated stream generation.
  External Links: 2504.15930,
  [Link](https://arxiv.org/abs/2504.15930)
  Cited by: [§2.2](https://arxiv.org/html/2609.33848#S2.SS2.SSS0.Px2.p1.1 "GPU placement policy and utilization. ‣ 2.2 Rollout–Training Scheduling ‣ 2 Background and Motivation ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Zhou et al. (2025)
  Y. Zhou, J. Li, Y. Su, G. Ramesh, Z. Zhu, X. Long, C. Zhao, J. Pan, X. Yu, Z. Wang, K. Du, J. Wu, X. Sun, J. Liu, Q. Yu, H. Chen, Z. Liu, and E. Barsoum
  APRIL: active partial rollouts in reinforcement learning to tame long-tail generation.
  External Links: 2509.18521,
  [Link](https://arxiv.org/abs/2509.18521)
  Cited by: [§7](https://arxiv.org/html/2609.33848#S7.SS0.SSS0.Px1.p2.1 "Agentic RL execution. ‣ 7 Related Work ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
- Zhuge et al. (2024)
  M. Zhuge, C. Zhao, D. Ashley, W. Wang, D. Khizbullin, Y. Xiong, Z. Liu, E. Chang, R. Krishnamoorthi, Y. Tian, Y. Shi, V. Chandra, and J. Schmidhuber
  Agent-as-a-judge: evaluate agents with agents.
  External Links: 2410.10934,
  [Link](https://arxiv.org/abs/2410.10934)
  Cited by: [§5.2](https://arxiv.org/html/2609.33848#S5.SS2.SSS0.Px1.p1.1 "Scoring preserved work ‣ 5.2 Partial Scoring ‣ 5 Trajectory Processor ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").

## Appendix A Mean Staleness under Boundary Dispatch

All three methods in Section [6](https://arxiv.org/html/2609.33848#S6 "6 Experimental Results ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents") use boundary
dispatch. We derive the mean staleness used to match their
configurations and explain why the identity also holds under elastic
GPU placement.

### A.1 Model and Accounting Assumptions

Each training step consumes `B` distinct rollout groups. Policy versions
are indexed by training steps and increase by one after each optimizer
update. A burst contains `\mu` steps and publishes the weights from its
final step with that step’s version number.
Following Section [2.2](https://arxiv.org/html/2609.33848#S2.SS2 "2.2 Rollout–Training Scheduling ‣ 2 Background and Motivation ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"),
define a consumed group’s staleness as

|  |  |  |  |
| --- | --- | --- | --- |
|  | `d=v_{t}-v_{d},` |  | (8) |

where `v_{d}` is the latest published version at admission and `v_{t}`
is the trainer version immediately before the consuming update.
Admission may precede execution launch
(Section [4.2](https://arxiv.org/html/2609.33848#S4.SS2 "4.2 Boundary Dispatch and Waterlevel Control ‣ 4 Elastic Scheduler ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents")). This metric includes queueing
and readiness waiting, but does not track the behavior policy of
each model call. Means weight each consumed group equally.

Under boundary dispatch, every admitted group retains its slot until
consumption. The queue is filled at startup and replenished with
`\mu B` new groups after each burst’s publication. Its target depth is

|  |  |  |  |
| --- | --- | --- | --- |
|  | `Q_{\mathrm{b}}=(\varphi+\mu)B,` |  | (9) |

where `\varphi\geq 0` is extra dispatch in units of `B` groups.
`Q_{\mathrm{b}}` counts all unconsumed groups after refill, including
queued, running, and ready groups. No new groups are admitted within
a burst.

### Assumption A.1 (Stationary group accounting).

`B`, `\mu`, and `Q_{\mathrm{b}}` are fixed. Every admitted group is
eventually consumed exactly once. At corresponding burst boundaries,
the unconsumed population and its relative version ages are stationary,
with finite expected total outstanding age.

### A.2 Boundary Staleness Identity

### Theorem A.1 (Mean staleness).

Under Assumption [A.1](https://arxiv.org/html/2609.33848#A1.Thmdispatchassumption1 "Assumption A.1 (Stationary group accounting). ‣ A.1 Model and Accounting Assumptions ‣ Appendix A Mean Staleness under Boundary Dispatch ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"),

|  |  |  |  |
| --- | --- | --- | --- |
|  | `\mathbb{E}_{\mathrm{b}}[d]=\frac{Q_{\mathrm{b}}}{B}-\frac{\mu+1}{2}=\varphi+\frac{\mu-1}{2}.` |  | (10) |

### Proof.

After update `j` in a burst, `Q_{\mathrm{b}}-jB` groups remain,
and each gains one unit of age. Replacements enter only after
publication, at age zero. Stationarity equates expected age removed
by consumption with expected age added by updates, so

|  |  |  |
| --- | --- | --- |
|  | `\mu B\,\mathbb{E}_{\mathrm{b}}[d]=\sum_{j=1}^{\mu}(Q_{\mathrm{b}}-jB)=\mu Q_{\mathrm{b}}-\frac{B\mu(\mu+1)}{2}.` |  |

Dividing by `\mu B` and substituting
`Q_{\mathrm{b}}=(\varphi+\mu)B` proves the result.
∎

The proof counts admission and consumption events, so neither FIFO
consumption nor a particular rollout latency distribution is needed.
Moving GPUs between rollout and training changes event timing, but
preserves this identity as long as the boundary-dispatch accounting
is unchanged. It therefore applies to Async, Colocate, and QwenGyre.

### A.3 Configurations at a Common Mean

For a target mean `s`, the identity gives

|  |  |  |  |
| --- | --- | --- | --- |
|  | `\displaystyle\varphi` | `\displaystyle=s-\frac{\mu-1}{2}\geq 0,` |  |
|  |  |  |  |
| --- | --- | --- | --- |
|  | `\displaystyle Q_{\mathrm{b}}` | `\displaystyle=B\left(s+\frac{\mu+1}{2}\right).` |  |

The burst size must satisfy `\mu\leq 2s+1`, and group counts must be
integral. Larger feasible bursts permit a greater dispatch depth
at the same mean; their performance still depends on placement and
workload latency.

With one step per burst, Async has `s=\varphi`. Without extra
dispatch, Colocate has `s=(\mu-1)/2`. Thus, at `s=1.5`, the
`(\varphi,\mu)` settings `(1.5,1)` for Async, `(0,4)` for Colocate,
and `(0.5,3)` for QwenGyre share the same mean staleness.
The same calculation preserves the mean when the scheduling ablation
changes QwenGyre from `(0.5,3)` to `(1.5,1)`.

## Appendix B RL Algorithm Details

This appendix specifies the GSPO adaptation summarized in Section [6.1](https://arxiv.org/html/2609.33848#S6.SS1.SSS0.Px3 "RL algorithm. ‣ 6.1 Experimental Setup ‣ 6 Experimental Results ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"), including its execution-level clipping, token-level importance correction, loss normalization, and training hyperparameters.

### Training configuration.

We use Group Sequence Policy Optimization (GSPO) ([Zheng et al., 2025](https://arxiv.org/html/2609.33848#bib.bib5))
with token-level importance correction. Each rollout group contains
`N=16` independent rollout executions. Each training step
consumes a batch of `B=32` distinct rollout groups for NL2RepoBench or `B=48`
for DeepSWE and TerminalBench. The remaining RL
hyperparameters are shared across all experiments.

All configurations use Adam ([Kingma and Ba, 2015](https://arxiv.org/html/2609.33848#bib.bib8)) with a constant learning rate of `10^{-6}`,
`\beta_{1}=0.9`, `\beta_{2}=0.95`, `\epsilon=10^{-15}`, weight decay 0.01,
and gradient clipping at norm 1.0. KL and entropy regularization are
disabled.

### Execution-level targets.

For execution `i`, let `\mathcal{R}_{i}` be its admitted trajectories.
For each `r\in\mathcal{R}_{i}`, the target set `\mathcal{T}_{r}` is fixed to
the trainable tokens still unmasked when `r` is drawn
(Section [5.3](https://arxiv.org/html/2609.33848#S5.SS3 "5.3 Trajectory Sampling ‣ 5 Trajectory Processor ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents")). On-tree masking makes these
sets disjoint. Let `\mathcal{T}_{i}=\bigcup_{r\in\mathcal{R}_{i}}\mathcal{T}_{r}`,
`L_{r}=|\mathcal{T}_{r}|`, and `L_{i}=|\mathcal{T}_{i}|=\sum_{r\in\mathcal{R}_{i}}L_{r}`.
The sequence used for importance-ratio computation and clipping is this
entire execution’s set of admitted, deduplicated trainable tokens.
Each token retains its original generation context. Tokens excluded by
provenance, role, or the `J_{\max}` cutoff contribute neither to the
sequence ratio nor to the loss.

### Importance correction and clipping.

Let `y_{u}` be target token `u`, `c_{u}` its recorded conditioning
context, and `p_{u}^{\mathrm{roll}}` its recorded behavior probability,
reused without recomputation. Let `\operatorname{sg}` denote
stop-gradient. For `L_{i}>0`, the token importance ratio and detached
execution-level sequence ratio are

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
|  | `\displaystyle\rho_{u}(\theta)` | `\displaystyle=\frac{\pi_{\theta}(y_{u}\mid c_{u})}{p_{u}^{\mathrm{roll}}},` |  | (11) |
|  | `\displaystyle s_{i}(\theta)` | `\displaystyle=\operatorname{sg}\!\left[\exp\!\left(\frac{1}{L_{i}}\sum_{u\in\mathcal{T}_{i}}\log\rho_{u}(\theta)\right)\right].` |  |

The detached sequence ratio in Equation [11](https://arxiv.org/html/2609.33848#A2.E11 "In Importance correction and clipping. ‣ Appendix B RL Algorithm Details ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents") is
used for monitoring and determines a shared clipping mask according
to execution `i`’s group-relative advantage `\hat{A}_{i}`:

|  |  |  |  |
| --- | --- | --- | --- |
|  | `m_{i}(\theta)=\begin{cases}0,&\hat{A}_{i}>0\ \text{and}\ s_{i}(\theta)>1.005,\\ 0,&\hat{A}_{i}<0\ \text{and}\ s_{i}(\theta)<0.995,\\ 1,&\text{otherwise}.\end{cases}` |  | (12) |

The token-specific importance weight is
`\bar{\rho}_{u}(\theta)=\operatorname{sg}(\min\{\rho_{u}(\theta),5\})`.
These weights may differ within an execution; `s_{i}` affects the loss
only through the common mask in Equation [12](https://arxiv.org/html/2609.33848#A2.E12 "In Importance correction and clipping. ‣ Appendix B RL Algorithm Details ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").
The token loss, upper-bounded by 100, is

|  |  |  |  |
| --- | --- | --- | --- |
|  | `\ell_{u}(\theta)=\min\!\left\{100,\,-m_{i}(\theta)\bar{\rho}_{u}(\theta)\hat{A}_{i}\log\pi_{\theta}(y_{u}\mid c_{u})\right\}.` |  | (13) |

### Loss normalization.

Using the token losses in Equation [13](https://arxiv.org/html/2609.33848#A2.E13 "In Importance correction and clipping. ‣ Appendix B RL Algorithm Details ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents"), weighting
each trajectory by its target share `L_{r}/L_{i}` and averaging over its
targets gives

|  |  |  |  |
| --- | --- | --- | --- |
|  | `\mathcal{L}_{i}(\theta)=\sum_{r\in\mathcal{R}_{i}}\frac{L_{r}}{L_{i}}\cdot\frac{1}{L_{r}}\sum_{u\in\mathcal{T}_{r}}\ell_{u}(\theta)=\frac{1}{L_{i}}\sum_{u\in\mathcal{T}_{i}}\ell_{u}(\theta),` |  | (14) |

Equation [14](https://arxiv.org/html/2609.33848#A2.E14 "In Loss normalization. ‣ Appendix B RL Algorithm Details ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents") gives every admitted target the same
normalization coefficient `1/L_{i}`; importance weighting and clipping
do not change this denominator. Executions with `L_{i}=0` contribute zero
loss. A batch averages over all `B` queries and their `N` original
rollout executions:

|  |  |  |  |
| --- | --- | --- | --- |
|  | `\mathcal{L}(\theta)=\frac{1}{B\,N}\sum_{q=1}^{B}\sum_{k=1}^{N}\mathcal{L}_{i(q,k)}(\theta),` |  | (15) |

where `i(q,k)` is query `q`’s `k`-th execution. Equation [15](https://arxiv.org/html/2609.33848#A2.E15 "In Loss normalization. ‣ Appendix B RL Algorithm Details ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents")
preserves each execution’s aggregate normalization weight regardless
of how many trajectories it contributes. For a fixed admitted target
set `\mathcal{T}_{i}`, changing which selected path carries a shared
target leaves the execution’s sequence ratio, clipping decision, and
loss unchanged. Sampling can change `\mathcal{T}_{i}` itself; the
invariance concerns the assignment and ordering of a fixed set of
targets. Packing preserves these per-execution weights.

## Appendix C Case Study: One Execution, Multiple Training Trajectories

We examine execution f3ad38e5, in which an agent uses Claude
Code to build a Python analytics SDK from a natural-language
specification. The task requires nine packages, including catalog
services, data frames, Flight connectivity, and pipeline utilities,
implemented from scratch in a shared workspace.
Figure [10](https://arxiv.org/html/2609.33848#A3.F10 "Figure 10 ‣ Appendix C Case Study: One Execution, Multiple Training Trajectories ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents") combines its prefix structure with
recorded messages to illustrate the trajectory-processing problem
of Section [5](https://arxiv.org/html/2609.33848#S5 "5 Trajectory Processor ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").

Figure 10: Prefix graph of execution f3ad38e5 with real message
excerpts. Rectangles represent collapsed context segments;
right-angle edges encode prefix sharing. Each parent is top-aligned
with its first child, and other children are stacked below.
Node counts refer to each segment; *path* counts the complete
root-to-leaf context. Dashed rectangles identify summary leaves.
Excerpts carry their original roles and node IDs; ellipses mark
omissions. The interruption at TOOL[1036] remains in the
main context where it was received.

### C.1 Execution and Context Structure

The trace reports 636 proxy requests and 1,347 unique message nodes
across ten candidate trajectories. The main agent produces two
task-driving trajectories and one summary. Five sub-agent invocations
produce six task-driving trajectories and one summary: the catalog
sub-agent compacts its history, while the FDW work item has two
attempts. These visualization nodes count messages, distinct from
the data plane’s request increments and trainable tokens.

Main and sub-agent contexts have separate roots because their system
prompts differ. Delegation can be identified separately by matching
an Agent call’s prompt to a sub-agent’s initial user message
after removing harness reminders; the export also identifies a
sub-agent billing flag. Causal parentage therefore differs from
context-prefix sharing. Concatenating the two agents’ conversations
would give outputs conditioning messages absent during generation.

### C.2 Compaction and Shared Prefixes

Both the main agent and the catalog sub-agent compact their contexts.
After their system prompts, they have shared prefixes of 168 and 193
messages, respectively. Each prefix forks into a task-driving
assistant response and a summarization request–response pair.
Continuation after compaction starts a separate path under the
system prompt, with a new user message containing the summary.

The ten complete paths contain 53–293 message nodes each.
Expanding them independently produces 1,716 node occurrences,
compared with 1,347 shared nodes. The 369 extra occurrences repeat
shared prefixes and system prompts; their token volume depends on
message lengths.

If a task-driving leaf and its summary leaf are both selected,
their shared policy outputs must contribute loss once.
Section [5.3](https://arxiv.org/html/2609.33848#S5.SS3 "5.3 Trajectory Sampling ‣ 5 Trajectory Processor ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents")’s on-tree masking retains the
prefix as context while suppressing repeated targets. Provenance
also matters: the original summary can be a target if the rollout
policy generated it, whereas its reinsertion into the continuation’s
user prompt is conditioning input. TITO preserves the original token
contexts and distinguishes these two occurrences.

### C.3 Delegation, Interruption, and Outcome Validity

One response attempts four Agent calls, but the harness
admits only two concurrent sub-agents. Two tool results report the
concurrency limit. Subsequent calls start the remaining work, but
the first FDW attempt is interrupted after a 53-node path. Later,
a local test run reports OK for 259 tests, with one skipped,
yet an import check cannot find the FDW, dbt, pipeline, and
test-support packages. The main agent launches another attempt,
which contributes a separate 202-node path. Rejection, partial
execution, and retry thus affect the record differently within
one rollout.

The leaf tagged is_final_main ends with renewed delegation:
it identifies the last recorded main trajectory, not successful
completion. An interrupted sub-agent likewise does not determine
the execution’s reward. Section [5.2](https://arxiv.org/html/2609.33848#S5.SS2 "5.2 Partial Scoring ‣ 5 Trajectory Processor ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents")
requires the designated evaluator to assess the preserved workspace;
a group becomes trainable only after its executions close with valid
outcomes. The visualization supplies no designated task reward.
The recovery sequence also motivates preserving harness and workspace
state during the request rerouting of
Section [4.3](https://arxiv.org/html/2609.33848#S4.SS3 "4.3 Harness-Preserving Role Transitions ‣ 4 Elastic Scheduler ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents").

### C.4 Applying the Training Admission Rule

The priority classes are two *main*, one *main-summary*,
six *sub-agent*, and one *sub-agent-summary*.
For illustration, suppose `J_{\max}=4` and each path has eligible
policy-generated targets. The rule in
Section [5.3](https://arxiv.org/html/2609.33848#S5.SS3 "5.3 Trajectory Sampling ‣ 5 Trajectory Processor ‣ QwenGyre: An Elastic Reinforcement Learning Framework forTraining xLong-Horizon Agents") admits both main trajectories,
the main-summary trajectory, and one sub-agent trajectory.
Selection within each class is proportional to remaining trainable
tokens, with shared targets masked after every draw. The figure’s
message counts cannot determine these token probabilities.

A flat mean over all ten leaf losses would allocate eight equal
coefficients to delegated or summary paths and repeat shared
targets. In QwenGyre, selected paths inherit the original execution’s
group-relative advantage. Token losses are averaged over disjoint
targets within each execution, then over the original rollout executions.
Additional compaction or delegation changes the admitted targets
without creating independent rewards or increasing the execution’s
aggregate normalization weight.
