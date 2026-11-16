---
title: "What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"
url: https://arxiv.org/abs/2611.06483
published: 2026-11-04
fetched: 2026-11-11
type: paper
topics: [training]
summary: "通过 Pass@(K,T) 区分采样宽度与交互深度；报告多轮 RL 的优势在回合预算收紧时下降，主要提升错误恢复与长轨迹韧性。"
---

# What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?

What Does Multi-Turn Reinforcement Learning
  
Really Improve in LLM Agents?
Kejian Zhu1,2,
Zhuoran Jin1,2,
Shangqing Tu3,
Tianyi Men1,2
Yupu Hao1,2,
Jiachun Li1,2,
Kang Liu1,2,
Jun Zhao1,2
1The Key Laboratory of Cognition and Decision Intelligence for Complex Systems,
Institute of Automation, Chinese Academy of Sciences, Beijing, China
2School of Artificial Intelligence, University of Chinese Academy of Sciences
3Tsinghua University
zhukejian2025@ia.ac.cn {zhuoran.jin, kliu, jzhao}@nlpr.ia.ac.cn 
Abstract
While multi-turn agentic reinforcement learning (RL) excels on long-horizon tasks, its performance gains remain highly sensitive to interaction constraints. Evaluating across sampling breadth `K` and interaction depth `T` via `\mathrm{Pass}@(K,T)`, we show that trajectory-level RL advantages depend on sufficient turn budgets, diminishing significantly when budgets tighten. Besides, agentic RL does not uniformly elevate single-step decision quality; rather, its strength concentrates in error recovery and long-horizon resilience. To mitigate the deployment risks caused by this budget dependence, we provide a preliminary discussion on the benefits and limitations of process supervision signals and introduce BudgetMix RL as an alternative that varies interaction budgets during training. Experiments demonstrate that BudgetMix RL achieves robust performance across diverse execution settings.

Project
<https://rethinking-agentic-rl.github.io/>

## 1 Introduction

Multi-turn agentic reinforcement learning (RL) has recently emerged as an important paradigm for improving the long-horizon capabilities of large language model (LLM) agents ([Li et al., 2026a](https://arxiv.org/html/2611.06483#bib.bib21); [Xi et al., 2025a](https://arxiv.org/html/2611.06483#bib.bib4)). By interacting with environments persistently, consuming feedback, and adapting subsequent actions, agents trained with RL have achieved substantial gains on multi-turn tasks (e.g., code or tool use). Despite these improvements, a fundamental question remains insufficiently understood: what capabilities does multi-turn agentic RL actually improve? Answering this question is important not only for understanding how agentic RL differs from its base model, but also for assessing whether agentic RL models remain reliable under realistic deployment scenarios.

Existing works primarily evaluate agents at the trajectory level, typically based on whether a task is completed within a given budget. Prior work on single-turn RL further uses `\mathrm{Pass}@K` to probe model capability boundary ([Yue et al., 2025](https://arxiv.org/html/2611.06483#bib.bib23)), which increases the number of independently sampled solutions. `\mathrm{Pass}@K` captures one dimension of test-time scaling: *sampling breadth*. Thus, we first apply `\mathrm{Pass}@K` to the evaluation of agents in §[3.1](https://arxiv.org/html/2611.06483#S3.SS1 "3.1 Trajectory-Level Gains across Sampling Breadth ‣ 3 When Does agentic RL Outperform the Base Model? ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"). The results show that agentic RL models consistently outperform base models as the number of sampled trajectories `k` increases. These results suggest that agentic RL effectively expands the empirical capability boundary of the base model.

However, for interactive agents, there is another test-time dimension: the number of interactions allowed per trajectory ([Shen et al., 2026](https://arxiv.org/html/2611.06483#bib.bib33)), which captures *interaction depth*. Accordingly, we evaluate performance using `\mathrm{Pass}@T` by varying the maximum allowed interaction turns (§[3.2](https://arxiv.org/html/2611.06483#S3.SS2 "3.2 RL Gains Shrink under Tight Interaction Budgets ‣ 3 When Does agentic RL Outperform the Base Model? ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?")). When we vary budget `T`, an interesting phenomenon emerges: given a large budget, agentic RL models demonstrate a substantial advantage over base models. However, under tighter budgets, this advantage shrinks considerably and can even disappear or reverse on certain tasks (right-hand panel of Figure [1](https://arxiv.org/html/2611.06483#S1.F1 "Figure 1 ‣ 1 Introduction ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?")). These results suggest that the gains of agentic RL depend on a sufficient interaction budget. To ensure that this phenomenon is not merely an artifact of restrictive budgets rendering some tasks structurally unsolvable, we compute structural performance upper bounds and discuss in Appendix [B.3](https://arxiv.org/html/2611.06483#A2.SS3 "B.3 Pass⁢@⁢𝑇 ‣ Appendix B Evaluation Details ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").

To further study this budget-dependent shift in capability, we analyze the step-level action quality of models before and after multi-turn RL (§[3.3](https://arxiv.org/html/2611.06483#S3.SS3 "3.3 Does Multi-Turn RL Improve Step-Level Action Quality? ‣ 3 When Does agentic RL Outperform the Base Model? ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?")). Results show that, given the same state and history, RL models do not consistently produce better next-step actions and can even perform worse in certain settings. Instead, their advantage becomes more pronounced at error states and later stages of a trajectory. As illustrated in Figure [1](https://arxiv.org/html/2611.06483#S1.F1 "Figure 1 ‣ 1 Introduction ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"), multi-turn RL does not uniformly improve action quality of every step; it primarily strengthens ability of error recovery and sustain long-horizon execution, which may partly explain why RL models need a larger budget `T` to demonstrate their advantages.

To understand this phenomenon more deeply, we perform a series of mechanistic analyses (§[4](https://arxiv.org/html/2611.06483#S4 "4 Mechanisms Behind the Observed Behaviors ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?")). Our log-likelihood analysis (§[4.1](https://arxiv.org/html/2611.06483#S4.SS1 "4.1 Likelihood Analysis: Local Surprisal and Trajectory-Level Policy Shift ‣ 4 Mechanisms Behind the Observed Behaviors ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?")) shows that RL-generated actions remain locally plausible under the base policy, yet complete RL trajectories receive substantially higher likelihood under the RL policy than under the base policy. This suggests that multi-turn RL may improve how reliably the model composes locally plausible actions into long-horizon trajectories. This phenomenon offers a possible explanation for how RL models can surpass the empirical `\mathrm{Pass}@K` capability boundary of base models, even without consistently superior single-step actions to the base models. The training dynamics in §[4.2](https://arxiv.org/html/2611.06483#S4.SS2 "4.2 Training Dynamics of Multi-Turn RL ‣ 4 Mechanisms Behind the Observed Behaviors ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?") further show how this pattern emerges progressively during training.

![Refer to caption](https://arxiv.org/html/2611.06483v1/agent-rl-intro-figure_v6.png)

Figure 1: Overview of our findings. Left: Multi-turn agentic RL does not uniformly enhance per-step action quality; rather, it mainly enhances ability of error recovery and long-horizon resilience. Right: The trajectory-level gains of agentic RL depend on a sufficient interaction budget (`T`).

These analyses reveal a hidden risk masked by conventional trajectory-level success rates: models trained with multi-turn RL may fail to perform consistently under varying interaction budgets. Furthermore, their single-step action quality can decline, which are critical in real-world deployments involving strict budget limits or irreversible errors ([Ma et al., 2026](https://arxiv.org/html/2611.06483#bib.bib35); [Doshi et al., 2026](https://arxiv.org/html/2611.06483#bib.bib36)). To address this, we provide a preliminary discussion on some candidate solutions (§[5](https://arxiv.org/html/2611.06483#S5 "5 Discussion: Towards More Stable Agentic RL ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?")). Specifically, we examine the benefits and limitations of process supervision signals and introduce BudgetMix RL, an alternative training strategy that varies interaction budgets. Experiments show that BudgetMix RL consistently improves performance across budgets while mitigating the decline in step-level action quality (§[5.2](https://arxiv.org/html/2611.06483#S5.SS2 "5.2 BudgetMix RL: Optimizing RL across Interaction Budgets ‣ 5 Discussion: Towards More Stable Agentic RL ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?")).

## 2 Preliminaries and Evaluation Framework

This section formalizes our research setting. We first describe multi-turn agentic reinforcement learning (§[2.1](https://arxiv.org/html/2611.06483#S2.SS1 "2.1 Multi-Turn Agentic Reinforcement Learning ‣ 2 Preliminaries and Evaluation Framework ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?")) and then present the two-dimensional `\mathrm{Pass}@(K,T)` evaluation metric (§[2.2](https://arxiv.org/html/2611.06483#S2.SS2 "2.2 Pass⁢@⁢(𝐾,𝑇): Sampling Breadth and Interaction Depth ‣ 2 Preliminaries and Evaluation Framework ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?")).

### 2.1 Multi-Turn Agentic Reinforcement Learning

We consider an agent interacting with an environment over multiple turns to solve a task `x\sim\mathcal{D}`. At step `t`, given the interaction history `h_{t}=(x,o_{1},a_{1},\ldots,o_{t-1},a_{t-1},o_{t})`, the agent samples an action `a_{t}\sim\pi(\cdot\mid h_{t})`, prompting the environment to return observation `o_{t+1}\sim P(\cdot\mid h_{t},a_{t})`:

|  |  |  |
| --- | --- | --- |
|  | `a_{t}\sim\pi(\cdot\mid h_{t}),\qquad o_{t+1}\sim P(\cdot\mid h_{t},a_{t}).` |  |

Actions can represent tool calls, terminal operations or code execution. Under an interaction budget of at most `T` turns, an episode yields a trajectory `\tau_{\leq T}=(x,o_{1},a_{1},\ldots,o_{T},a_{T})`, scored by a terminal verifier with reward `R(\tau_{\leq T})`. Our framework accommodates both outcome-only RL (e.g., GRPO ([Guo et al., 2025](https://arxiv.org/html/2611.06483#bib.bib11))) and process-level credit assignment methods (e.g., GiGPO ([Feng et al., 2025b](https://arxiv.org/html/2611.06483#bib.bib15))).

### 2.2 `\mathrm{Pass}@(K,T)`: Sampling Breadth and Interaction Depth

Conventional agent evaluations typically report trajectory success. To probe capability boundaries, prior work on single-turn RL uses the metric `\mathrm{Pass}@K`, the probability that at least one of `k` independent samples succeeds, which can be seen as *sampling breadth*. Interactive agents introduce an orthogonal axis: the maximum interaction budget `T` per trajectory, which governs *interaction depth*. To capture both dimensions, we use metric `\mathrm{Pass}@(K,T)` ([Zhai et al., 2026](https://arxiv.org/html/2611.06483#bib.bib31)) for a policy `\pi` on task `x`:

|  |  |  |  |
| --- | --- | --- | --- |
|  | `\mathrm{Pass}@(K,T)=\Pr_{\tau^{(1)},\dots,\tau^{(K)}\sim\pi(\cdot\mid x)}\Bigl[\exists i\in\{1,\ldots,K\}:R(\tau^{(i)}_{\leq T})=1\Bigr],` |  | (1) |

which underpins our analysis in §[3](https://arxiv.org/html/2611.06483#S3 "3 When Does agentic RL Outperform the Base Model? ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"). Fixing the sampling budget to a constant `C` while sweeping `T` yields `\mathrm{Pass}@T=\mathrm{Pass}@(K=C,T)`, isolating the depth axis evaluated in §[3.2](https://arxiv.org/html/2611.06483#S3.SS2 "3.2 RL Gains Shrink under Tight Interaction Budgets ‣ 3 When Does agentic RL Outperform the Base Model? ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").

## 3 When Does agentic RL Outperform the Base Model?

We now examine whether the gains from multi-turn agentic RL can be consistently achieved, as well as its potential risks. We evaluate models with two dimensional metrics `\mathrm{Pass}@(K,T)` introduced in §[2.2](https://arxiv.org/html/2611.06483#S2.SS2 "2.2 Pass⁢@⁢(𝐾,𝑇): Sampling Breadth and Interaction Depth ‣ 2 Preliminaries and Evaluation Framework ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?") (§[3.1](https://arxiv.org/html/2611.06483#S3.SS1 "3.1 Trajectory-Level Gains across Sampling Breadth ‣ 3 When Does agentic RL Outperform the Base Model? ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?") and §[3.2](https://arxiv.org/html/2611.06483#S3.SS2 "3.2 RL Gains Shrink under Tight Interaction Budgets ‣ 3 When Does agentic RL Outperform the Base Model? ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?")), analyze step-level action quality (§[3.3](https://arxiv.org/html/2611.06483#S3.SS3 "3.3 Does Multi-Turn RL Improve Step-Level Action Quality? ‣ 3 When Does agentic RL Outperform the Base Model? ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?")), and summarize the potential risks (§[3.4](https://arxiv.org/html/2611.06483#S3.SS4 "3.4 Risks: Real-World Deployment of Agents ‣ 3 When Does agentic RL Outperform the Base Model? ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?")). We adopt GRPO as our primary RL algorithm and evaluate on four interactive benchmarks: DeepCoder-MT, BFCL, InterCode-SQL, and FrozenLake, spanning diverse domains and modalities. Additional results are reported in Appendix [C](https://arxiv.org/html/2611.06483#A3 "Appendix C Additional Pass⁢@⁢𝐾 Experiments ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?") and [D](https://arxiv.org/html/2611.06483#A4 "Appendix D Additional Pass⁢@⁢𝑇 Experiments ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"), implementation details in Appendix [A](https://arxiv.org/html/2611.06483#A1 "Appendix A Training Details ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?") and [B](https://arxiv.org/html/2611.06483#A2 "Appendix B Evaluation Details ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").

### 3.1 Trajectory-Level Gains across Sampling Breadth

We begin by evaluating the trajectory-level performance using the `\mathrm{Pass}@K`. By increasing the number of independently sampled trajectories, `\mathrm{Pass}@K` probes the empirical capability boundary of a model, which we use to characterize how this boundary changes after multi-turn RL. As shown in Figure [2](https://arxiv.org/html/2611.06483#S3.F2 "Figure 2 ‣ 3.1 Trajectory-Level Gains across Sampling Breadth ‣ 3 When Does agentic RL Outperform the Base Model? ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"), the RL model consistently outperforms the base model as the sampling breadth `k` increases, suggesting that multi-turn RL can push trajectory-level success beyond the empirical capability boundary of base model. This contrasts with prior observations in single-turn tasks, where RL does not expand capability boundary beyond the base model. Further results are shown in Appendix [C](https://arxiv.org/html/2611.06483#A3 "Appendix C Additional Pass⁢@⁢𝐾 Experiments ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").

Takeaway 3.1

Pros of Agentic RL: unlike single-turn RL, multi-turn agentic RL can push trajectory-level performance beyond the empirical `\mathrm{Pass}@K` capability boundary of the base model.

Figure 2: `\mathrm{Pass}@K` across sampling breadth. Sweeping the number of sampled trajectories `K`.

### 3.2 RL Gains Shrink under Tight Interaction Budgets

Beyond sampling breadth, we evaluate how model performance evolves with interaction depth. As shown in Figure [3](https://arxiv.org/html/2611.06483#S3.F3 "Figure 3 ‣ 3.2 RL Gains Shrink under Tight Interaction Budgets ‣ 3 When Does agentic RL Outperform the Base Model? ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"), we fix the sampling breadth at `k=8` and vary the maximum interaction turns `T`. The results reveal an interesting pattern: the advantage of the RL model depends on a sufficient interaction budget. As the budget `T` increases, the performance advantage of RL model over base model becomes increasingly pronounced. Conversely, under tight budgets (small `T`), this advantage diminishes, and can even reverse on certain tasks. To rule out the possibility that the performance drop at small `T` is trivially caused by tasks becoming structurally unsolvable under restrictive budgets, we also compute the structural performance upper bound for each task and discuss in Appendix [B.3](https://arxiv.org/html/2611.06483#A2.SS3 "B.3 Pass⁢@⁢𝑇 ‣ Appendix B Evaluation Details ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"). Notably, at small `T`, even when substantial headroom remains below this upper bound, agentic RL fails to exhibit any clear advantage over the base model. More results are shown in Appendix [D](https://arxiv.org/html/2611.06483#A4 "Appendix D Additional Pass⁢@⁢𝑇 Experiments ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").

We conjecture that agent RL primarily strengthens long-horizon capabilities whose benefits emerge when sufficient interaction budget is available. Under restricted budgets, these benefits may disappear, suggesting that its gains do not necessarily stem from uniformly better step-level actions.

Figure 3: `\mathrm{Pass}@T` at fixed `k{=}8`. Sweeping the maximum number of interaction turns `T`.

Takeaway 3.2

Potential Cons of Agentic RL: the performance gains from multi-turn RL depend on sufficient interaction budgets, and can diminish or even reverse under tight budgets.

### 3.3 Does Multi-Turn RL Improve Step-Level Action Quality?

The phenomenon of last section motivates a question: does multi-turn RL improve action quality for each individual step? Thus we compare the step quality of the base and RL model under identical states. For each state `s`, we independently sampled `G=16` actions from both policies and averaged their quality scores to reduce sampling variance and obtain a more robust estimate of action quality:

|  |  |  |
| --- | --- | --- |
|  | `a_{i}^{\mathrm{Base}}\sim\pi_{\mathrm{Base}}(\cdot\mid s),\qquad a_{i}^{\mathrm{RL}}\sim\pi_{\mathrm{RL}}(\cdot\mid s),\qquad i=1,\ldots,G.` |  |

Strictly evaluating one-step quality is challenging because reliable process rewards remain difficult to obtain in agentic settings ([Li et al., 2026b](https://arxiv.org/html/2611.06483#bib.bib37)). We therefore focus on two tasks with reliable step-level evaluation: (1) For FrozenLake, we use finite-horizon dynamic programming (DP) with a discount factor `\gamma` of `0.95` to compute the exact `Q^{*}` value of each step-level action under optimal continuation within the remaining interaction budget. (2) For DeepCoder-MT, the code of each step can be scored by unit-test pass rates. To isolate action quality from state visitation bias, we construct a state evaluation pool by sampling intermediate states equally from base and RL trajectories. Following experiments use Qwen3-4B trained with GRPO, with additional results presented in Appendix [E.1](https://arxiv.org/html/2611.06483#A5.SS1 "E.1 Additional Results of Step-Level Action Quality ‣ Appendix E Additional Results for Analysis Experiments ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").

Agentic RL does not uniformly improve step-level action quality.
We first evaluate whether agentic RL uniformly improves action quality per-step. As shown in Figure [4](https://arxiv.org/html/2611.06483#S3.F4 "Figure 4 ‣ 3.3 Does Multi-Turn RL Improve Step-Level Action Quality? ‣ 3 When Does agentic RL Outperform the Base Model? ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"), each point represents a matched state, with the `x`- and `y`-coordinates indicating action quality of the base and RL models, respectively. Points below the diagonal indicate superior action quality from base model, whereas points above the diagonal favor RL model. We find that the distribution does not favor the RL model and even leans slightly toward the base model. Specifically, RL achieves better step-level decision quality on only 46.8% of DeepCoder-MT states and 42.8% of FrozenLake states, with average quality no better than, even slightly below, the base model. These results demonstrate that multi-turn agentic RL does not consistently enhance single-step action and may occasionally degrade it.

Figure 4: Step-level action quality. Each point is one matched state; its coordinates are action quality of the base and RL model. Teal points favor the base model, red points favor the RL model.

Agentic RL excels after errors.
Since the RL model does not consistently yield superior single-step decisions across every matched state, a natural question arises: why does multi-turn RL achieve marked trajectory-level performance gains? To answer this, we focus on states immediately following an error (e.g., error states), where effective recovery ability of models becomes critical. Specifically, we construct an error state pool by injecting an incorrect action at the preceding step. As shown in Figure [5](https://arxiv.org/html/2611.06483#S3.F5 "Figure 5 ‣ 3.3 Does Multi-Turn RL Improve Step-Level Action Quality? ‣ 3 When Does agentic RL Outperform the Base Model? ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"), the pattern reverses under these error states: data points shift predominantly above the diagonal, with the RL model selecting the superior action in 65.7% of cases on FrozenLake and 67.3% on DeepCoder-MT. We additionally compare the terminal success rates of RL and base models when continuing from identical error states. RL outperforms base on both FrozenLake (`51.3\%` vs. `38.6\%`) and DeepCoder-MT (`38.5\%` vs. `22.9\%`). Appendix [E.4](https://arxiv.org/html/2611.06483#A5.SS4 "E.4 Additional Case Study Results ‣ Appendix E Additional Results for Analysis Experiments ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?") also illustrates how the RL model corrects an erroneous tool call on BFCL. These results demonstrate that RL achieves higher action quality and continuation success on these error states. When errors occur in interaction trajectories, agentic RL demonstrates superior error recovery capabilities and resilience.

Figure 5: Step-level action quality on error states. Each point is one error state.

The RL advantage emerges later in trajectories.
Finally, we examine how decision quality evolves over the course of a trajectory. We group intermediate states by turn index and define the normalized depth at turn `t` as `d_{t}=t/T_{\max}\in[0,1]`, where `T_{\max}` is the maximum interaction budget. As shown in Figure [6](https://arxiv.org/html/2611.06483#S3.F6 "Figure 6 ‣ 3.3 Does Multi-Turn RL Improve Step-Level Action Quality? ‣ 3 When Does agentic RL Outperform the Base Model? ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"), the RL model shows little advantage early in execution and even underperforms the base model. As interaction proceeds, however, the gap gradually narrows and reverses. This indicates that the RL model does not make superior decisions at the beginning of a trajectory; its advantage emerges as interaction unfolds. This suggests that the step-level advantage of agentic RL is not uniform across a trajectory, but becomes more pronounced at later stages of long-horizon interaction.

Figure 6: Action quality versus normalized trajectory depth
`d_{t}=t/T_{\max}`. Shading denotes 95% CI.

Takeaway 3.3

Multi-turn agentic RL does not consistently improve single-step action quality. Its advantage is instead more pronounced in error states and later stages of long-horizon trajectories.

### 3.4 Risks: Real-World Deployment of Agents

These findings highlight a deployment risk: the gains from agentic RL depend on sufficient interaction budget and may diminish or reverse under tight budgets. This is particularly concerning for tasks involving irreversible actions, such as financial or database operations ([Doshi et al., 2026](https://arxiv.org/html/2611.06483#bib.bib36)), where agents must make high-quality and conservative actions at each step. Yet higher trajectory success does not ensure better individual actions. As LLM agents are increasingly deployed in real-world settings, understanding such limitations beyond final task success becomes increasingly important.

## 4 Mechanisms Behind the Observed Behaviors

The previous section characterized the behavior of RL models at trajectory and step level. This section digs into the mechanism: a likelihood analysis (§[4.1](https://arxiv.org/html/2611.06483#S4.SS1 "4.1 Likelihood Analysis: Local Surprisal and Trajectory-Level Policy Shift ‣ 4 Mechanisms Behind the Observed Behaviors ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?")), the training dynamics analysis (§[4.2](https://arxiv.org/html/2611.06483#S4.SS2 "4.2 Training Dynamics of Multi-Turn RL ‣ 4 Mechanisms Behind the Observed Behaviors ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?")).

### 4.1 Likelihood Analysis: Local Surprisal and Trajectory-Level Policy Shift

The results in §[3.3](https://arxiv.org/html/2611.06483#S3.SS3 "3.3 Does Multi-Turn RL Improve Step-Level Action Quality? ‣ 3 When Does agentic RL Outperform the Base Model? ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?") show that the per-step actions of the agent RL model do not consistently outperform those of the base model. In this section, we compare both the RL and base policies through their likelihoods. Specifically, we evaluate rollouts from both models under the base and RL policies, measuring the log-likelihood of individual actions and the relative likelihood of complete trajectories.
Concretely, let a trajectory be `\tau=(h_{1},a_{1},\ldots,h_{T},a_{T})`, where `h_{t}` denotes the history and `a_{t}` is the corresponding action. We keep the histories fixed and evaluate each action under base policy. As an action is a token sequence `a_{t}=(w_{t,1},\ldots,w_{t,m_{t}})`, its negative log-likelihood (NLL) is

|  |  |  |
| --- | --- | --- |
|  | `\mathrm{ActionNLL}_{\mathrm{B}}(a_{t}\mid h_{t})=-\sum_{j=1}^{m_{t}}\log p_{\mathrm{B}}\bigl(w_{t,j}\mid h_{t},w_{t,<j}\bigr).` |  |

To examine the complete trajectory, we further compute the cumulative log-likelihood ratio (LLR),

|  |  |  |
| --- | --- | --- |
|  | `\mathrm{LLR}_{1:t}(\tau)=\sum_{i=1}^{t}\left[\log\pi_{\mathrm{RL}}(r_{i}\mid h_{i})-\log\pi_{\mathrm{B}}(r_{i}\mid h_{i})\right],` |  |

where `r_{i}` denotes the complete model response in one turn, including reasoning and action tokens. Positive LLR indicates that the recorded trajectory is more likely under the RL policy than under the base policy. Together these two quantities characterize, respectively, how unusual each single action of the RL model is under the base policy and relative policy preference over complete trajectory.

Figure 7: Likelihood analysis. Boxplots show action NLL under base policy (left axis). Curves show cumulative LLR (right axis). Bands indicate 95% confidence.

Step-level actions of RL remain locally plausible under base policy. We evaluate per-token action NLL under the base policy on Terminal-Bench (Figure [7](https://arxiv.org/html/2611.06483#S4.F7 "Figure 7 ‣ 4.1 Likelihood Analysis: Local Surprisal and Trajectory-Level Policy Shift ‣ 4 Mechanisms Behind the Observed Behaviors ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?")). We find that the RL action distributions (pink boxplots) substantially overlap with those of the base model (blue boxplots), with mean NLLs of `12.20` and `10.25`, respectively. Thus, the single-step action of the RL model does not deviate far from the support of the base model, which partly explains why the step-level decisions of the RL model do not consistently beat the base model in §[3.3](https://arxiv.org/html/2611.06483#S3.SS3 "3.3 Does Multi-Turn RL Improve Step-Level Action Quality? ‣ 3 When Does agentic RL Outperform the Base Model? ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").

From actions to long-horizon execution.
Although individual actions are supported, this does not mean base model can reliably sample the entire long-horizon trajectory. As shown on the right y-axis of Figure [7](https://arxiv.org/html/2611.06483#S4.F7 "Figure 7 ‣ 4.1 Likelihood Analysis: Local Surprisal and Trajectory-Level Policy Shift ‣ 4 Mechanisms Behind the Observed Behaviors ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"), the cumulative LLR of successful RL trajectories increases with interaction progress, reaching approximately `228`, compared with `26` for successful base trajectories. The RL model assigns much higher probabilities to its trajectories than base model. This contrasts with the similar NLLs that base model assigns to RL and its own actions. Overall, this demonstrates that even if the conditional probability per-step is reasonably high, the overall probability of entire trajectory can be extremely low. This provides a possible explanation for observations in §[3.1](https://arxiv.org/html/2611.06483#S3.SS1 "3.1 Trajectory-Level Gains across Sampling Breadth ‣ 3 When Does agentic RL Outperform the Base Model? ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"): multi-turn RL enables trajectory-level success to surpass base model’s `\mathrm{Pass}@K` capability boundary even without improvement of every action.

### 4.2 Training Dynamics of Multi-Turn RL

Figure 8: Training dynamics of the trajectory-level reward `R_{\mathrm{multi}}` and step reward `R_{\mathrm{single}}` on DeepCoder-MT.

To more directly examine how multi-turn RL affects step-level action quality and trajectory-level performance, we further analyze the training dynamics. Standard agentic RL is optimized and validated using trajectory reward `R_{\mathrm{multi}}`. For tasks with step-level quality measures (§[3.3](https://arxiv.org/html/2611.06483#S3.SS3 "3.3 Does Multi-Turn RL Improve Step-Level Action Quality? ‣ 3 When Does agentic RL Outperform the Base Model? ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?")), we track the average step reward `R_{\mathrm{single}}` as a validation for step-level action, while training optimizes only on `R_{\mathrm{multi}}`. As shown in Figure [8](https://arxiv.org/html/2611.06483#S4.F8 "Figure 8 ‣ 4.2 Training Dynamics of Multi-Turn RL ‣ 4 Mechanisms Behind the Observed Behaviors ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?") (red and blue curves), we find a phenomenon: as training proceeds, the trajectory-level reward `R_{\mathrm{multi}}` keeps rising while the per-step reward does not improve and even gradually declines. On DeepCoder-MT, `R_{\mathrm{multi}}` rises by `0.331` while `R_{\mathrm{single}}` drops by `0.097`. This indicates that the phenomenon observed at the final checkpoint is not incidental, but rather emerge progressively during training (More results in Appendix [E.3](https://arxiv.org/html/2611.06483#A5.SS3 "E.3 Additional Training Dynamics ‣ Appendix E Additional Results for Analysis Experiments ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?")). This echoes our earlier findings: trajectory-level gains can develop alongside declining step-level action quality.

Figure 9: Effect of process supervision signals on `\mathrm{Pass}@T`.

## 5 Discussion: Towards More Stable Agentic RL

The preceding sections indicate that the gains of agent RL rely on sufficient interaction budgets, while local action quality does not consistently improve and can even decline. This raises reliability concerns for real-world deployment. Consequently, this section offers a preliminary discussion on potential mitigation strategies. Our objective is to preserve its long-horizon execution capabilities and and trajectory-level gains while reducing its reliance on extra interaction budget for downstream error recovery and encouraging greater prudence in single-step decision making.

### 5.1 High-quality Process Signals Can Partly Mitigate this Risk

A natural direction is to introduce finer-grained signals to improve per-step action quality through either process rewards or credit assignment. We therefore evaluate several methods to examine whether step-level signals can alleviate above limitations. As shown on the left of Figure [9](https://arxiv.org/html/2611.06483#S4.F9 "Figure 9 ‣ 4.2 Training Dynamics of Multi-Turn RL ‣ 4 Mechanisms Behind the Observed Behaviors ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"), on FrozenLake, accurate process supervision can substantially mitigate the limitations of outcome-only RL. In particular, oracle Q-value process rewards and GiGPO stabilize performance across various interaction budgets, especially under tight budgets. However, as discussed in §[3.3](https://arxiv.org/html/2611.06483#S3.SS3 "3.3 Does Multi-Turn RL Improve Step-Level Action Quality? ‣ 3 When Does agentic RL Outperform the Base Model? ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"), such precise process supervision is rarely accessible in realistic agent tasks. Results of BFCL on the right illustrate this bottleneck, where no exact step-level oracle is available. Dense signal methods such as GiGPO and PPO fail to enhance performance under constrained budgets and perform similarly to GRPO. These findings demonstrate that while high-quality process rewards can alleviate budget reliance, acquiring such supervision signals remains impractical for most real-world applications.

### 5.2 BudgetMix RL: Optimizing RL across Interaction Budgets

We therefore take a simpler route: BudgetMix RL. It keeps the same reward mechanism as traditional multi-turn RL, but varies the interaction budget across training trajectories. BudgetMix RL can be combined with existing agentic RL algorithms (e.g., GRPO, PPO, and GiGPO). Standard multi-turn agentic RL samples trajectories under a fixed maximum budget `T_{\max}` and optimizes either outcome or per-step rewards. However, this objective does not explicitly distinguish solutions that require different amounts of interaction, provided they finish within the budget. BudgetMix makes a single modification to this procedure. For a task instance `x` with full budget `T_{\max}(x)`, we construct candidate budgets at `10\%` intervals and uniformly sample one budget per task group:

|  |  |  |  |
| --- | --- | --- | --- |
|  | `\mathcal{T}(x)=\operatorname{Unique}\left(\left\{\left\lceil\frac{k}{10}T_{\max}(x)\right\rceil:k=1,\ldots,10\right\}\right),\qquad T(x)\sim\operatorname{Uniform}\bigl(\mathcal{T}(x)\bigr).` |  | (2) |

During training, the total and remaining budget are provided within the prompt; trajectories that exceed the budget without completion receive a reward of zero. The reward signal design is consistent with that of traditional RL. We provide pseudocode and implementation details in Appendix [A.4](https://arxiv.org/html/2611.06483#A1.SS4 "A.4 BudgetMix Implementation ‣ Appendix A Training Details ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"). BudgetMix turns the budget `T` from an evaluation dimension in `\mathrm{Pass}@(K,T)` into a training dimension. Its central idea is that the interaction budget changes the conditions under which the same reward can be obtained. A tighter budget limits opportunities for retries, placing greater demands on earlier decisions, whereas an ample budget preserves opportunities for long-range execution.

Table 1: 
`\mathrm{Pass}@T` evaluation results (`\mathrm{Pass}@8`, %).
We evaluate models at 25%, 50%, 75%, and 100% of the
maximum interaction budget. Bold and underlined values denote the best and second-best results, respectively, within each model size and budget. Avg. gain reports the average improvement of BudgetMix over full-budget RL across GRPO, GiGPO, and PPO, in percentage points.

|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | FrozenLake (`T_{\max}=70`) | | | | DeepCoder-MT (`T_{\max}=10`) | | | | BFCL-v3 (`T_{\max}=24`) | | | | InterCode-SQL (`T_{\max}=10`) | | | |  |
| Method | 25% | 50% | 75% | 100% | 25% | 50% | 75% | 100% | 25% | 50% | 75% | 100% | 25% | 50% | 75% | 100% | Avg. |
| Qwen3-4B | | | | | | | | | | | | | | | | | |
| Base | 30.3 | 49.1 | 58.7 | 61.6 | 34.0 | 43.5 | 47.3 | 48.3 | 3.0 | 15.6 | 21.2 | 26.4 | 23.1 | 28.8 | 31.8 | 33.5 | 34.8 |
| GRPO Full | 28.7 | 55.1 | 68.1 | 72.4 | 29.2 | 48.0 | 56.0 | 59.0 | 2.5 | 17.6 | 27.0 | 30.2 | 23.1 | 32.2 | 37.4 | 46.0 | 39.5 |
| GRPO BudgetMix | 37.6 | 61.1 | 72.0 | 73.5 | 38.1 | 54.3 | 60.5 | 61.2 | 8.5 | 23.0 | 30.5 | 30.8 | 28.9 | 37.7 | 42.9 | 47.5 | 44.3 |
| GiGPO Full | 38.4 | 58.4 | 70.4 | 76.5 | 28.8 | 48.3 | 55.6 | 58.8 | 3.4 | 18.4 | 28.8 | 31.3 | 23.4 | 31.5 | 37.5 | 45.0 | 40.9 |
| GiGPO BudgetMix | 46.3 | 63.5 | 74.0 | 78.5 | 36.5 | 52.0 | 59.3 | 59.5 | 8.5 | 23.2 | 31.7 | 33.0 | 27.9 | 37.0 | 41.7 | 44.8 | 44.8 |
| PPO Full | 38.5 | 58.6 | 71.2 | 80.0 | 29.5 | 45.6 | 51.6 | 55.0 | 4.2 | 19.4 | 29.0 | 33.4 | 22.4 | 30.6 | 34.8 | 41.0 | 40.3 |
| PPO BudgetMix | 45.5 | 63.1 | 75.1 | 80.3 | 36.4 | 51.6 | 55.5 | 56.9 | 10.2 | 24.8 | 32.8 | 34.5 | 27.0 | 35.2 | 38.3 | 42.7 | 44.4 |
| Avg. gain | `+7.9` | `+5.2` | `+3.8` | `+1.1` | `+7.8` | `+5.3` | `+4.0` | `+1.6` | `+5.7` | `+5.2` | `+3.4` | `+1.1` | `+5.0` | `+5.2` | `+4.4` | `+1.0` | `+4.2` |
| Qwen3-8B | | | | | | | | | | | | | | | | | |
| Base | 34.0 | 49.5 | 52.7 | 58.5 | 42.8 | 51.6 | 54.6 | 56.8 | 4.8 | 23.2 | 29.4 | 37.8 | 29.8 | 34.9 | 37.6 | 40.8 | 39.9 |
| GRPO Full | 31.9 | 58.8 | 68.5 | 78.0 | 31.5 | 54.5 | 60.8 | 66.5 | 3.8 | 27.5 | 39.0 | 45.0 | 27.0 | 40.5 | 45.7 | 49.4 | 45.5 |
| GRPO BudgetMix | 40.8 | 65.1 | 72.9 | 79.6 | 45.5 | 59.8 | 64.6 | 66.8 | 10.5 | 33.0 | 43.2 | 47.2 | 33.1 | 46.5 | 50.4 | 50.4 | 50.6 |
| GiGPO Full | 34.6 | 56.5 | 65.5 | 71.5 | 28.7 | 48.2 | 55.7 | 58.7 | 5.6 | 26.8 | 38.8 | 43.5 | 22.8 | 32.9 | 36.1 | 45.6 | 42.0 |
| GiGPO BudgetMix | 40.9 | 60.4 | 69.1 | 72.3 | 44.9 | 57.8 | 60.1 | 60.7 | 10.8 | 30.8 | 42.8 | 43.2 | 32.6 | 39.4 | 40.2 | 47.7 | 47.1 |
| PPO Full | 40.4 | 63.5 | 71.2 | 85.0 | 34.5 | 51.5 | 57.0 | 64.8 | 7.0 | 29.5 | 41.5 | 48.0 | 26.5 | 36.0 | 40.8 | 45.0 | 46.4 |
| PPO BudgetMix | 47.1 | 67.4 | 75.2 | 86.7 | 44.0 | 56.6 | 61.1 | 65.9 | 12.2 | 34.2 | 46.0 | 50.5 | 32.1 | 40.0 | 44.5 | 46.6 | 50.6 |
| Avg. gain | `+7.3` | `+4.7` | `+4.0` | `+1.4` | `+13.2` | `+6.7` | `+4.1` | `+1.1` | `+5.7` | `+4.7` | `+4.2` | `+1.5` | `+7.2` | `+5.5` | `+4.2` | `+1.6` | `+4.8` |

### 5.3 Experimental Setup

Tasks and models. Our main experiments cover four tasks: FrozenLake, DeepCoder-MT, BFCL and InterCode-SQL. We primarily use Qwen3-4B and Qwen3-8B as the base models.

Baselines.
From the same base checkpoint, we compare standard full-budget RL against BudgetMix RL under identical algorithm settings including GRPO, GiGPO, PPO.

Evaluation protocol.
We evaluate `\mathrm{Pass}@T` with the maximum interaction budget set to 25%, 50%, 75%, and 100% of `T_{\max}`. Consistent with the previous `\mathrm{Pass}@T` evaluation setup, we inform the model of the total budget limit and the remaining budget within the prompt, as shown in Appendix [B](https://arxiv.org/html/2611.06483#A2 "Appendix B Evaluation Details ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").

### 5.4 Results and Analysis

Table [1](https://arxiv.org/html/2611.06483#S5.T1 "Table 1 ‣ 5.2 BudgetMix RL: Optimizing RL across Interaction Budgets ‣ 5 Discussion: Towards More Stable Agentic RL ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?") reports the main results. First, under tight budget constraints (`25\%`, `50\%` and `75\%` `T_{\mathrm{max}}`), BudgetMix outperforms both the base model and standard full-budget RL across all four tasks, achieving average performance gains of 7.5, 5.3 and 4.0 percentage points over full-budget RL, respectively. Second, at full interaction capacity (`100\%` `T_{\mathrm{max}}`), BudgetMix maintains parity with full-budget RL, demonstrating that its low-budget enhancements do not compromise long-horizon execution capability. Overall, BudgetMix improves the stability of agent performance, delivering strong performance across diverse interaction budgets and retaining strong full-budget results.

We further examine the training dynamics of BudgetMix. As shown in Figure [8](https://arxiv.org/html/2611.06483#S4.F8 "Figure 8 ‣ 4.2 Training Dynamics of Multi-Turn RL ‣ 4 Mechanisms Behind the Observed Behaviors ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"), during BudgetMix training (yellow and gray curves), the trajectory-level reward `R_{\mathrm{multi}}` steadily increases, while the step-level reward `R_{\mathrm{single}}` remains stable or improves slightly. In contrast, standard full-budget agent RL (blue curve) degrades step-level quality. Thus, BudgetMix largely mitigates local decision-quality degradation while preserving long-horizon gains. Consistent results from direct step-level action-quality evaluation are provided in Appendix [E.1](https://arxiv.org/html/2611.06483#A5.SS1 "E.1 Additional Results of Step-Level Action Quality ‣ Appendix E Additional Results for Analysis Experiments ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").

## 6 Related Work

### 6.1 Multi-Turn Agentic Reinforcement Learning

LLM agents are widely used for interactive tasks like coding and tool use ([Zhou et al., 2024](https://arxiv.org/html/2611.06483#bib.bib1); [Qian et al., 2025](https://arxiv.org/html/2611.06483#bib.bib2); [Wang et al., 2026a](https://arxiv.org/html/2611.06483#bib.bib54); [Hao et al., 2026a](https://arxiv.org/html/2611.06483#bib.bib55); [Men et al., 2025](https://arxiv.org/html/2611.06483#bib.bib56)), with RL becoming a major training paradigm ([Jin et al., 2026a](https://arxiv.org/html/2611.06483#bib.bib58); [Zhu et al., 2026a](https://arxiv.org/html/2611.06483#bib.bib59)). Many methods extend single-turn outcome-based RL ([Yu et al., 2025](https://arxiv.org/html/2611.06483#bib.bib12)) to interactive tasks using trajectory-level rewards ([Xi et al., 2025a](https://arxiv.org/html/2611.06483#bib.bib4); [Wang et al., 2025d](https://arxiv.org/html/2611.06483#bib.bib5)), enabling applications such as deep research ([Jin et al., 2025](https://arxiv.org/html/2611.06483#bib.bib3); [Sun et al., 2026](https://arxiv.org/html/2611.06483#bib.bib7)), tool-augmented reasoning ([Feng et al., 2025a](https://arxiv.org/html/2611.06483#bib.bib27)), and web interaction ([Qi et al., 2025](https://arxiv.org/html/2611.06483#bib.bib13)). However, sparse terminal rewards make credit assignment increasingly difficult as interaction horizons grow ([Tao et al., 2026](https://arxiv.org/html/2611.06483#bib.bib9); [Tan et al., 2026](https://arxiv.org/html/2611.06483#bib.bib10)). To address this, methods derive process signals from outcomes ([Liu et al., 2025b](https://arxiv.org/html/2611.06483#bib.bib14); [Zheng et al., 2026](https://arxiv.org/html/2611.06483#bib.bib19)), including state-grouped advantages in GiGPO ([Feng et al., 2025b](https://arxiv.org/html/2611.06483#bib.bib15)), stepwise reward decomposition in SPA-RL ([Wang et al., 2025a](https://arxiv.org/html/2611.06483#bib.bib16)), and advantage attribution with entropy-guided exploration in ARPO ([Dong et al., 2025](https://arxiv.org/html/2611.06483#bib.bib17)). Other work explicitly models intermediate decision quality ([Xi et al., 2025b](https://arxiv.org/html/2611.06483#bib.bib18); [Lin et al., 2026](https://arxiv.org/html/2611.06483#bib.bib20)). Despite these advances, evaluation remains largely centered on trajectory-level success ([Li et al., 2026c](https://arxiv.org/html/2611.06483#bib.bib34); [Men et al., 2026](https://arxiv.org/html/2611.06483#bib.bib53); [Jin et al., 2026b](https://arxiv.org/html/2611.06483#bib.bib57)). We therefore analyze multi-turn RL beyond final task success to better understand its gains and limitations.

### 6.2 Understanding and Rethinking RL Post-Training

Recently, post-training has become a key stage to improving reasoning and planning capabilities of LLMs ([Guo et al., 2025](https://arxiv.org/html/2611.06483#bib.bib11)), prompting studies of its mechanisms and limitations ([Zhu et al., 2026b](https://arxiv.org/html/2611.06483#bib.bib22); [He et al., 2025](https://arxiv.org/html/2611.06483#bib.bib52); [Fu et al., 2026](https://arxiv.org/html/2611.06483#bib.bib51)). For single-turn reasoning, Pass@`K` analyses suggest that RLVR primarily reweights solutions already reachable by the base model ([Yue et al., 2025](https://arxiv.org/html/2611.06483#bib.bib23)). Later work reports boundary expansion with prolonged RL ([Liu et al., 2025a](https://arxiv.org/html/2611.06483#bib.bib24)), while others attribute apparent gains to recombining existing skills ([Yuan et al., 2025](https://arxiv.org/html/2611.06483#bib.bib25)) or amplifying latent base-model behaviors ([Wu et al., 2026](https://arxiv.org/html/2611.06483#bib.bib26)). These findings suggest that final success may obscure the source of RL gains. Other studies examine entropy dynamics ([Cui et al., 2025](https://arxiv.org/html/2611.06483#bib.bib28); [Xu et al., 2026a](https://arxiv.org/html/2611.06483#bib.bib29)), identify high-entropy tokens as key carriers of learning signals ([Wang et al., 2025b](https://arxiv.org/html/2611.06483#bib.bib32)). Related work further compares SFT and RL in generalization and capability acquisition ([Chu et al., 2025](https://arxiv.org/html/2611.06483#bib.bib30); [Zhu et al., 2026b](https://arxiv.org/html/2611.06483#bib.bib22)). Mechanistic analyses have recently extended to multi-turn agents ([Wang et al., 2026b](https://arxiv.org/html/2611.06483#bib.bib6); [Li et al., 2026a](https://arxiv.org/html/2611.06483#bib.bib21); [Hao et al., 2026b](https://arxiv.org/html/2611.06483#bib.bib8)). Most relevantly, prior work introduced Pass@`(K,T)` to characterize multi-turn capability boundaries and showed that agentic RL can surpass capability boundary of base model ([Zhai et al., 2026](https://arxiv.org/html/2611.06483#bib.bib31)). We go beyond this perspective by analyzing interaction-budget dependence, step quality and mechanisms to identify the sources of RL gains and potential limitations.

## 7 Conclusion

We revisit the benefits of multi-turn agentic RL beyond final task success. Through `\mathrm{Pass}@(K,T)` evaluation, we demonstrate that RL can extend the empirical capabilities of the base model, though this advantage may diminish or reverse as interaction budgets become more constrained. Our analysis suggests that these gains stem primarily from long-horizon execution and error recovery, rather than consistently superior single-step actions. As this may impact the reliability of agents deployed in real-world settings, we further discuss potential strategies to mitigate this risk and their limitations.

## AI Use Statement

During the writing of this paper, we used LLMs to assist with grammar checking, text polishing, and improving overall readability. All AI-assisted revisions were carefully reviewed by the authors to ensure that they did not alter the original meaning, technical content, or conclusions. We also used AI assistants to improve the presentation of selected tables and figures. In addition, we evaluated an LLM-based judge as a process reward model in one of our analysis experiments. We ensure that the AI does not alter the results. All experimental data and numerical results were verified by the authors.

## Ethics Statement

This work studies the capabilities and limitations of multi-turn reinforcement learning for LLM agents, with particular attention to their reliability under different interaction constraints. Our experiments are conducted on benchmark environments covering tool use, interactive coding, planning, and terminal operations. We do not conduct human-subject experiments in this study. Our analysis highlights a potential deployment risk: the gains of agentic RL can shrink under tight interaction budgets, while single-step action quality of RL models does not consistently improve. This limitation can be particularly relevant in applications involving strict interaction budgets or irreversible actions. We therefore believe that agentic systems should be evaluated not only by final task success, but also by their robustness across execution constraints and the reliability of individual decisions.

## Reproducibility Statement

We provide the experimental settings and implementation details required to reproduce our main results in both the main text and the appendix. The main text describes the evaluation metrics, experimental protocols, and the BudgetMix RL framework. More complete reproducibility details are provided in the appendix. Specifically, Appendix [A](https://arxiv.org/html/2611.06483#A1 "Appendix A Training Details ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?") describes the details of tasks and training implementation. Appendix [B](https://arxiv.org/html/2611.06483#A2 "Appendix B Evaluation Details ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?") provides the detailed evaluation protocols. Additional experiments across RL algorithms, model architectures, tasks, and analysis settings are reported in Appendices [C](https://arxiv.org/html/2611.06483#A3 "Appendix C Additional Pass⁢@⁢𝐾 Experiments ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"),[D](https://arxiv.org/html/2611.06483#A4 "Appendix D Additional Pass⁢@⁢𝑇 Experiments ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?") and [E](https://arxiv.org/html/2611.06483#A5 "Appendix E Additional Results for Analysis Experiments ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"). Together, these details are intended to facilitate reproducibility of our results.

## References

- Chen et al. (2021)
  M. Chen, J. Tworek, H. Jun, Q. Yuan, H. P. de Oliveira Pinto, J. Kaplan, H. Edwards, Y. Burda, N. Joseph, G. Brockman, A. Ray, R. Puri, G. Krueger, M. Petrov, H. Khlaaf, G. Sastry, P. Mishkin, B. Chan, S. Gray, N. Ryder, M. Pavlov, A. Power, L. Kaiser, M. Bavarian, C. Winter, P. Tillet, F. P. Such, D. Cummings, M. Plappert, F. Chantzis, E. Barnes, A. Herbert-Voss, W. H. Guss, A. Nichol, A. Paino, N. Tezak, J. Tang, I. Babuschkin, S. Balaji, S. Jain, W. Saunders, C. Hesse, A. N. Carr, J. Leike, J. Achiam, V. Misra, E. Morikawa, A. Radford, M. Knight, M. Brundage, M. Murati, K. Mayer, P. Welinder, B. McGrew, D. Amodei, S. McCandlish, I. Sutskever, and W. Zaremba
  Evaluating large language models trained on code.
  External Links: 2107.03374,
  [Link](https://arxiv.org/abs/2107.03374)
  Cited by: [§B.2](https://arxiv.org/html/2611.06483#A2.SS2.p1.2 "B.2 Pass⁢@⁢𝐾 ‣ Appendix B Evaluation Details ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Chu et al. (2025)
  T. Chu, Y. Zhai, J. Yang, S. Tong, S. Xie, D. Schuurmans, Q. V. Le, S. Levine, and Y. Ma
  SFT memorizes, rl generalizes: a comparative study of foundation model post-training.
  External Links: 2501.17161,
  [Link](https://arxiv.org/abs/2501.17161)
  Cited by: [§6.2](https://arxiv.org/html/2611.06483#S6.SS2.p1.1 "6.2 Understanding and Rethinking RL Post-Training ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Cui et al. (2025)
  G. Cui, Y. Zhang, J. Chen, L. Yuan, Z. Wang, Y. Zuo, H. Li, Y. Fan, H. Chen, W. Chen, Z. Liu, H. Peng, L. Bai, W. Ouyang, Y. Cheng, B. Zhou, and N. Ding
  The entropy mechanism of reinforcement learning for reasoning language models.
  External Links: 2505.22617,
  [Link](https://arxiv.org/abs/2505.22617)
  Cited by: [§6.2](https://arxiv.org/html/2611.06483#S6.SS2.p1.1 "6.2 Understanding and Rethinking RL Post-Training ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Dong et al. (2025)
  G. Dong, H. Mao, K. Ma, L. Bao, Y. Chen, Z. Wang, Z. Chen, J. Du, H. Wang, F. Zhang, G. Zhou, Y. Zhu, J. Wen, and Z. Dou
  Agentic reinforced policy optimization.
  External Links: 2507.19849,
  [Link](https://arxiv.org/abs/2507.19849)
  Cited by: [§6.1](https://arxiv.org/html/2611.06483#S6.SS1.p1.1 "6.1 Multi-Turn Agentic Reinforcement Learning ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Doshi et al. (2026)
  A. Doshi, Y. Hong, C. Xu, E. Kang, A. Kapravelos, and C. Kästner
  Towards verifiably safe tool use for llm agents.
  In Proceedings of the IEEE/ACM 48th International Conference on Software Engineering,
  pp. 201–205.
  Cited by: [§1](https://arxiv.org/html/2611.06483#S1.p6.1 "1 Introduction ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"),
  [§3.4](https://arxiv.org/html/2611.06483#S3.SS4.p1.1 "3.4 Risks: Real-World Deployment of Agents ‣ 3 When Does agentic RL Outperform the Base Model? ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Feng et al. (2025a)
  J. Feng, S. Huang, X. Qu, G. Zhang, Y. Qin, B. Zhong, C. Jiang, J. Chi, and W. Zhong
  ReTool: reinforcement learning for strategic tool use in llms.
  External Links: 2504.11536,
  [Link](https://arxiv.org/abs/2504.11536)
  Cited by: [§6.1](https://arxiv.org/html/2611.06483#S6.SS1.p1.1 "6.1 Multi-Turn Agentic Reinforcement Learning ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Feng et al. (2025b)
  L. Feng, Z. Xue, T. Liu, and B. An
  Group-in-group policy optimization for llm agent training.
  External Links: 2505.10978,
  [Link](https://arxiv.org/abs/2505.10978)
  Cited by: [§A.2](https://arxiv.org/html/2611.06483#A1.SS2.p1.1 "A.2 Models and Training Hyperparameters ‣ Appendix A Training Details ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"),
  [§A.2](https://arxiv.org/html/2611.06483#A1.SS2.p4.1 "A.2 Models and Training Hyperparameters ‣ Appendix A Training Details ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"),
  [§C.1](https://arxiv.org/html/2611.06483#A3.SS1.p1.1 "C.1 Additional Agentic RL Algorithms ‣ Appendix C Additional Pass⁢@⁢𝐾 Experiments ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"),
  [§2.1](https://arxiv.org/html/2611.06483#S2.SS1.p1.2 "2.1 Multi-Turn Agentic Reinforcement Learning ‣ 2 Preliminaries and Evaluation Framework ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"),
  [§6.1](https://arxiv.org/html/2611.06483#S6.SS1.p1.1 "6.1 Multi-Turn Agentic Reinforcement Learning ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Fu et al. (2026)
  Z. Fu, B. He, Y. Zuo, H. Huang, J. Zhang, R. Xiao, C. Qian, Q. Luo, H. Gao, Y. Wang, et al.
  Rethinking on-policy distillation of large language models ii: one training example.
  arXiv preprint arXiv:2609.04172.
  Cited by: [§6.2](https://arxiv.org/html/2611.06483#S6.SS2.p1.1 "6.2 Understanding and Rethinking RL Post-Training ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Guo et al. (2025)
  D. Guo, D. Yang, H. Zhang, J. Song, P. Wang, Q. Zhu, R. Xu, R. Zhang, S. Ma, X. Bi, et al.
  Deepseek-r1: incentivizing reasoning capability in llms via reinforcement learning.
  arXiv preprint arXiv:2501.12948.
  Cited by: [§A.2](https://arxiv.org/html/2611.06483#A1.SS2.p1.1 "A.2 Models and Training Hyperparameters ‣ Appendix A Training Details ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"),
  [§C.2](https://arxiv.org/html/2611.06483#A3.SS2.p1.1 "C.2 Additional Model Architectures ‣ Appendix C Additional Pass⁢@⁢𝐾 Experiments ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"),
  [§2.1](https://arxiv.org/html/2611.06483#S2.SS1.p1.2 "2.1 Multi-Turn Agentic Reinforcement Learning ‣ 2 Preliminaries and Evaluation Framework ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"),
  [§6.2](https://arxiv.org/html/2611.06483#S6.SS2.p1.1 "6.2 Understanding and Rethinking RL Post-Training ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Hao et al. (2026a)
  Y. Hao, Z. Jin, H. Liao, K. Liu, and J. Zhao
  Pushing the limits of llm tool calling via experiential knowledge integration and activation.
  In Findings of the Association for Computational Linguistics: ACL 2026,
  pp. 14470–14497.
  Cited by: [§6.1](https://arxiv.org/html/2611.06483#S6.SS1.p1.1 "6.1 Multi-Turn Agentic Reinforcement Learning ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Hao et al. (2026b)
  Y. Hao, Z. Jin, H. Liao, K. Liu, and J. Zhao
  Why multi-step tool-use reinforcement learning collapses and how supervisory signals fix it.
  External Links: 2606.26027,
  [Link](https://arxiv.org/abs/2606.26027)
  Cited by: [§6.2](https://arxiv.org/html/2611.06483#S6.SS2.p1.1 "6.2 Understanding and Rethinking RL Post-Training ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- He et al. (2025)
  B. He, Z. Qu, Z. Liu, Y. Chen, Y. Zuo, C. Qian, K. Zhang, W. Chen, C. Xiao, G. Cui, N. Ding, and Z. Liu
  JustRL: scaling a 1.5b llm with a simple rl recipe.
  External Links: 2512.16649,
  [Link](https://arxiv.org/abs/2512.16649)
  Cited by: [§6.2](https://arxiv.org/html/2611.06483#S6.SS2.p1.1 "6.2 Understanding and Rethinking RL Post-Training ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Ivison et al. (2026)
  H. Ivison, J. O. Yin, R. Shao, T. Xiao, N. Lambert, and H. Hajishirzi
  Tmax: a simple recipe for terminal agents.
  External Links: 2606.23321,
  [Link](https://arxiv.org/abs/2606.23321)
  Cited by: [§A.1](https://arxiv.org/html/2611.06483#A1.SS1.p1.1 "A.1 Tasks and Training Data ‣ Appendix A Training Details ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Jin et al. (2025)
  B. Jin, H. Zeng, Z. Yue, J. Yoon, S. Arik, D. Wang, H. Zamani, and J. Han
  Search-r1: training llms to reason and leverage search engines with reinforcement learning.
  External Links: 2503.09516,
  [Link](https://arxiv.org/abs/2503.09516)
  Cited by: [§6.1](https://arxiv.org/html/2611.06483#S6.SS1.p1.1 "6.1 Multi-Turn Agentic Reinforcement Learning ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Jin et al. (2026a)
  Z. Jin, H. Yuan, K. Zhu, J. Li, P. Cao, Y. Chen, K. Liu, and J. Zhao
  Omni-reward: towards generalist omni-modal reward modeling with free-form preferences.
  In International Conference on Learning Representations,
  Vol. 2026, pp. 108481–108530.
  Cited by: [§6.1](https://arxiv.org/html/2611.06483#S6.SS1.p1.1 "6.1 Multi-Turn Agentic Reinforcement Learning ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Jin et al. (2026b)
  Z. Jin, K. Zhu, H. Yuan, Y. Hao, P. Cao, Y. Chen, K. Liu, and J. Zhao
  Look light, think heavy: what multimodal chain-of-thought reasoning can and cannot do.
  In Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers),
  pp. 8567–8608.
  Cited by: [§6.1](https://arxiv.org/html/2611.06483#S6.SS1.p1.1 "6.1 Multi-Turn Agentic Reinforcement Learning ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Li et al. (2026a)
  J. Li, Z. Jin, T. Men, Y. Hao, K. Zhu, L. Wang, D. Huang, L. Wang, S. Hua, L. Wang, J. Gao, H. Yuan, R. Xu, K. Liu, and J. Zhao
  Agentic environment engineering for large language models: A survey of environment modeling, synthesis, evaluation, and application.
  CoRR abs/2606.12191.
  External Links: [Link](https://doi.org/10.48550/arXiv.2606.12191),
  [Document](https://dx.doi.org/10.48550/ARXIV.2606.12191),
  2606.12191
  Cited by: [§1](https://arxiv.org/html/2611.06483#S1.p1.1 "1 Introduction ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"),
  [§6.2](https://arxiv.org/html/2611.06483#S6.SS2.p1.1 "6.2 Understanding and Rethinking RL Post-Training ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Li et al. (2026b)
  M. Li, Q. Zeng, T. Fang, Z. Liang, L. Song, Q. Liu, H. Mi, and D. Yu
  Verified critical step optimization for llm agents.
  External Links: 2602.03412,
  [Link](https://arxiv.org/abs/2602.03412)
  Cited by: [§3.3](https://arxiv.org/html/2611.06483#S3.SS3.p1.2 "3.3 Does Multi-Turn RL Improve Step-Level Action Quality? ‣ 3 When Does agentic RL Outperform the Base Model? ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Li et al. (2026c)
  X. Li, R. Ming, P. Setlur, A. Paladugu, A. Tang, H. Kang, S. Shao, R. Jin, and C. Xiong
  Benchmark test-time scaling of general llm agents.
  arXiv preprint arXiv:2602.18998.
  Cited by: [§6.1](https://arxiv.org/html/2611.06483#S6.SS1.p1.1 "6.1 Multi-Turn Agentic Reinforcement Learning ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Lin et al. (2026)
  J. Lin, Y. Shi, X. Peng, R. Ding, H. Wang, Y. Peng, B. Bai, W. Song, F. Bai, H. Chai, W. Zhang, F. Huang, and Y. Wen
  ToolPRM: fine-grained inference scaling of structured outputs for function calling.
  External Links: 2510.14703,
  [Link](https://arxiv.org/abs/2510.14703)
  Cited by: [§6.1](https://arxiv.org/html/2611.06483#S6.SS1.p1.1 "6.1 Multi-Turn Agentic Reinforcement Learning ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Liu et al. (2025a)
  M. Liu, S. Diao, X. Lu, J. Hu, X. Dong, Y. Choi, J. Kautz, and Y. Dong
  ProRL: prolonged reinforcement learning expands reasoning boundaries in large language models.
  External Links: 2505.24864,
  [Link](https://arxiv.org/abs/2505.24864)
  Cited by: [§6.2](https://arxiv.org/html/2611.06483#S6.SS2.p1.1 "6.2 Understanding and Rethinking RL Post-Training ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Liu et al. (2025b)
  X. Liu, K. Wang, Y. Wu, F. Huang, Y. Li, J. Zhang, and J. Jiao
  Online process reward leanring for agentic reinforcement learning.
  arXiv e-prints, pp. arXiv–2509.
  Cited by: [§6.1](https://arxiv.org/html/2611.06483#S6.SS1.p1.1 "6.1 Multi-Turn Agentic Reinforcement Learning ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Luo et al. (2025)
  M. Luo, S. Tan, R. Huang, A. Patel, A. Ariyak, Q. Wu, X. Shi, R. Xin, C. Cai, M. Weber, C. Zhang, L. E. Li, R. A. Popa, and I. Stoica
  DeepCoder: a fully open-source 14b coder at o3-mini level.
  Note: <https://pretty-radio-b75.notion.site/DeepCoder-A-Fully-Open-Source-14B-Coder-at-O3-mini-Level-1cf81902c14680b3bee5eb349a512a51>Notion Blog
  Cited by: [§A.1](https://arxiv.org/html/2611.06483#A1.SS1.p1.1 "A.1 Tasks and Training Data ‣ Appendix A Training Details ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Ma et al. (2026)
  Y. Ma, L. Li, Y. Chen, P. Li, X. Li, Q. Guo, D. Lin, and K. Chen
  Timely machine: awareness of time makes test-time scaling agentic.
  In Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers),
  pp. 4619–4636.
  Cited by: [§1](https://arxiv.org/html/2611.06483#S1.p6.1 "1 Introduction ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Men et al. (2025)
  T. Men, Z. Jin, P. Cao, Y. Chen, K. Liu, and J. Zhao
  Agent-rewardbench: towards a unified benchmark for reward modeling across perception, planning, and safety in real-world multimodal agents.
  In Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers),
  pp. 17521–17541.
  Cited by: [§6.1](https://arxiv.org/html/2611.06483#S6.SS1.p1.1 "6.1 Multi-Turn Agentic Reinforcement Learning ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Men et al. (2026)
  T. Men, Z. Jin, K. Liu, and J. Zhao
  The physics of multi-turn long-horizon planning: from pre-training to post-training via single-and multi-teacher on-policy agentic distillation.
  arXiv preprint arXiv:2607.24720.
  Cited by: [§6.1](https://arxiv.org/html/2611.06483#S6.SS1.p1.1 "6.1 Multi-Turn Agentic Reinforcement Learning ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Merrill et al. (2026)
  M. A. Merrill, A. G. Shaw, N. Carlini, B. Li, H. Raj, I. Bercovich, L. Shi, J. Y. Shin, T. Walshe, E. K. Buchanan, J. Shen, G. Ye, H. Lin, J. Poulos, M. Wang, M. Nezhurina, J. Jitsev, D. Lu, O. M. Mastromichalakis, Z. Xu, Z. Chen, Y. Liu, R. Zhang, L. L. Chen, A. Kashyap, J. Uslu, J. Li, J. Wu, M. Yan, S. Bian, V. Sharma, K. Sun, S. Dillmann, A. Anand, A. Lanpouthakoun, B. Koopah, C. Hu, E. Guha, G. H. S. Dreiman, J. Zhu, K. Krauth, L. Zhong, N. Muennighoff, R. Amanfu, S. Tan, S. Pimpalgaonkar, T. Aggarwal, X. Lin, X. Lan, X. Zhao, Y. Liang, Y. Wang, Z. Wang, C. Zhou, D. Heineman, H. Liu, H. Trivedi, J. Yang, J. Lin, M. Shetty, M. Yang, N. Omi, N. Raoof, S. Li, T. Y. Zhuo, W. Lin, Y. Dai, Y. Wang, W. Chai, S. Zhou, D. Wahdany, Z. She, J. Hu, Z. Dong, Y. Zhu, S. Cui, A. Saiyed, A. Kolbeinsson, J. Hu, C. M. Rytting, R. Marten, Y. Wang, A. Dimakis, A. Konwinski, and L. Schmidt
  Terminal-bench: benchmarking agents on hard, realistic tasks in command line interfaces.
  External Links: 2601.11868,
  [Link](https://arxiv.org/abs/2601.11868)
  Cited by: [§A.1](https://arxiv.org/html/2611.06483#A1.SS1.p1.1 "A.1 Tasks and Training Data ‣ Appendix A Training Details ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"),
  [§C.3](https://arxiv.org/html/2611.06483#A3.SS3.p1.1 "C.3 Additional Tasks ‣ Appendix C Additional Pass⁢@⁢𝐾 Experiments ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Patil et al. (2025)
  S. G. Patil, H. Mao, F. Yan, C. C. Ji, V. Suresh, I. Stoica, and J. E. Gonzalez
  The berkeley function calling leaderboard (bfcl): from tool use to agentic evaluation of large language models.
  In Forty-second International Conference on Machine Learning,
  Cited by: [§A.1](https://arxiv.org/html/2611.06483#A1.SS1.p1.1 "A.1 Tasks and Training Data ‣ Appendix A Training Details ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Qi et al. (2025)
  Z. Qi, X. Liu, I. L. Iong, H. Lai, X. Sun, W. Zhao, Y. Yang, X. Yang, J. Sun, S. Yao, T. Zhang, W. Xu, J. Tang, and Y. Dong
  WebRL: training llm web agents via self-evolving online curriculum reinforcement learning.
  External Links: 2411.02337,
  [Link](https://arxiv.org/abs/2411.02337)
  Cited by: [§6.1](https://arxiv.org/html/2611.06483#S6.SS1.p1.1 "6.1 Multi-Turn Agentic Reinforcement Learning ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Qian et al. (2025)
  C. Qian, E. C. Acikgoz, Q. He, H. Wang, X. Chen, D. Hakkani-Tür, G. Tur, and H. Ji
  ToolRL: reward is all tool learning needs.
  External Links: 2504.13958,
  [Link](https://arxiv.org/abs/2504.13958)
  Cited by: [§6.1](https://arxiv.org/html/2611.06483#S6.SS1.p1.1 "6.1 Multi-Turn Agentic Reinforcement Learning ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Schulman et al. (2018)
  J. Schulman, P. Moritz, S. Levine, M. Jordan, and P. Abbeel
  High-dimensional continuous control using generalized advantage estimation.
  External Links: 1506.02438,
  [Link](https://arxiv.org/abs/1506.02438)
  Cited by: [§A.2](https://arxiv.org/html/2611.06483#A1.SS2.p5.1 "A.2 Models and Training Hyperparameters ‣ Appendix A Training Details ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Schulman et al. (2017)
  J. Schulman, F. Wolski, P. Dhariwal, A. Radford, and O. Klimov
  Proximal policy optimization algorithms.
  External Links: 1707.06347,
  [Link](https://arxiv.org/abs/1707.06347)
  Cited by: [§A.2](https://arxiv.org/html/2611.06483#A1.SS2.p1.1 "A.2 Models and Training Hyperparameters ‣ Appendix A Training Details ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"),
  [§C.1](https://arxiv.org/html/2611.06483#A3.SS1.p1.1 "C.1 Additional Agentic RL Algorithms ‣ Appendix C Additional Pass⁢@⁢𝐾 Experiments ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Shen et al. (2026)
  J. Shen, H. Bai, L. Zhang, Y. Zhou, A. Setlur, P. Tong, D. Caples, N. Jiang, T. Zhang, A. Talwalkar, et al.
  Thinking vs. doing: improving agent reasoning by scaling test-time interaction.
  Advances in Neural Information Processing Systems 38, pp. 169640–169681.
  Cited by: [§1](https://arxiv.org/html/2611.06483#S1.p3.1 "1 Introduction ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Sheng et al. (2024)
  G. Sheng, C. Zhang, Z. Ye, X. Wu, W. Zhang, R. Zhang, Y. Peng, H. Lin, and C. Wu
  HybridFlow: a flexible and efficient rlhf framework.
  arXiv preprint arXiv: 2409.19256.
  Cited by: [§A.2](https://arxiv.org/html/2611.06483#A1.SS2.p1.1 "A.2 Models and Training Hyperparameters ‣ Appendix A Training Details ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Sun et al. (2026)
  H. Sun, Z. Qiao, J. Guo, X. Fan, Y. Hou, Y. Jiang, P. Xie, Y. Zhang, F. Huang, and J. Zhou
  ZeroSearch: incentivize the search capability of llms without searching.
  External Links: 2505.04588,
  [Link](https://arxiv.org/abs/2505.04588)
  Cited by: [§6.1](https://arxiv.org/html/2611.06483#S6.SS1.p1.1 "6.1 Multi-Turn Agentic Reinforcement Learning ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Tan et al. (2026)
  H. Tan, X. Yang, H. Chen, J. Shao, Y. Wen, Y. Shen, W. Luo, X. Du, L. Guo, and Y. Li
  Hindsight credit assignment for long-horizon llm agents.
  External Links: 2603.08754,
  [Link](https://arxiv.org/abs/2603.08754)
  Cited by: [§6.1](https://arxiv.org/html/2611.06483#S6.SS1.p1.1 "6.1 Multi-Turn Agentic Reinforcement Learning ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Tao et al. (2026)
  L. Tao, B. Peng, W. Yao, T. Ge, H. Cheng, M. H. Wang, J. Gao, and S. Li
  TRACE: turn-level reward assignment via credit estimation for long-horizon agents.
  External Links: 2607.13988,
  [Link](https://arxiv.org/abs/2607.13988)
  Cited by: [§6.1](https://arxiv.org/html/2611.06483#S6.SS1.p1.1 "6.1 Multi-Turn Agentic Reinforcement Learning ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Wang et al. (2025a)
  H. Wang, C. T. Leong, J. Wang, J. Wang, and W. Li
  SPA-rl: reinforcing llm agents via stepwise progress attribution.
  External Links: 2505.20732,
  [Link](https://arxiv.org/abs/2505.20732)
  Cited by: [§6.1](https://arxiv.org/html/2611.06483#S6.SS1.p1.1 "6.1 Multi-Turn Agentic Reinforcement Learning ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Wang et al. (2026a)
  L. Wang, Z. Jin, Y. Hao, Y. Chen, K. Liu, Y. Ao, and J. Zhao
  Think while watching: online streaming segment-level memory for multi-turn video reasoning in multimodal large language models.
  In European Conference on Computer Vision,
  pp. 342–361.
  Cited by: [§6.1](https://arxiv.org/html/2611.06483#S6.SS1.p1.1 "6.1 Multi-Turn Agentic Reinforcement Learning ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Wang et al. (2025b)
  S. Wang, L. Yu, C. Gao, C. Zheng, S. Liu, R. Lu, K. Dang, X. Chen, J. Yang, Z. Zhang, Y. Liu, A. Yang, A. Zhao, Y. Yue, S. Song, B. Yu, G. Huang, and J. Lin
  Beyond the 80/20 rule: high-entropy minority tokens drive effective reinforcement learning for llm reasoning.
  External Links: 2506.01939,
  [Link](https://arxiv.org/abs/2506.01939)
  Cited by: [§6.2](https://arxiv.org/html/2611.06483#S6.SS2.p1.1 "6.2 Understanding and Rethinking RL Post-Training ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Wang et al. (2025c)
  W. Wang, Z. Gao, L. Gu, H. Pu, L. Cui, X. Wei, Z. Liu, L. Jing, S. Ye, J. Shao, Z. Wang, Z. Chen, H. Zhang, G. Yang, H. Wang, Q. Wei, J. Yin, W. Li, E. Cui, G. Chen, Z. Ding, C. Tian, Z. Wu, J. Xie, Z. Li, B. Yang, Y. Duan, X. Wang, Z. Hou, H. Hao, T. Zhang, S. Li, X. Zhao, H. Duan, N. Deng, B. Fu, Y. He, Y. Wang, C. He, B. Shi, J. He, Y. Xiong, H. Lv, L. Wu, W. Shao, K. Zhang, H. Deng, B. Qi, J. Ge, Q. Guo, W. Zhang, S. Zhang, M. Cao, J. Lin, K. Tang, J. Gao, H. Huang, Y. Gu, C. Lyu, H. Tang, R. Wang, H. Lv, W. Ouyang, L. Wang, M. Dou, X. Zhu, T. Lu, D. Lin, J. Dai, W. Su, B. Zhou, K. Chen, Y. Qiao, W. Wang, and G. Luo
  InternVL3.5: advancing open-source multimodal models in versatility, reasoning, and efficiency.
  External Links: 2508.18265,
  [Link](https://arxiv.org/abs/2508.18265)
  Cited by: [§C.2](https://arxiv.org/html/2611.06483#A3.SS2.p1.1 "C.2 Additional Model Architectures ‣ Appendix C Additional Pass⁢@⁢𝐾 Experiments ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Wang et al. (2026b)
  Z. Wang, C. Gui, X. Jin, Q. Wang, L. Liu, K. Wang, S. Chen, L. Li, Z. Yang, P. Zhang, Y. Lu, J. Wu, L. Fei-Fei, L. Wang, Y. Choi, and M. Li
  RAGEN-2: reasoning collapse in agentic rl.
  External Links: 2604.06268,
  [Link](https://arxiv.org/abs/2604.06268)
  Cited by: [§6.2](https://arxiv.org/html/2611.06483#S6.SS2.p1.1 "6.2 Understanding and Rethinking RL Post-Training ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Wang et al. (2025d)
  Z. Wang, K. Wang, Q. Wang, P. Zhang, L. Li, Z. Yang, X. Jin, K. Yu, M. N. Nguyen, L. Liu, E. Gottlieb, Y. Lu, K. Cho, J. Wu, L. Fei-Fei, L. Wang, Y. Choi, and M. Li
  RAGEN: understanding self-evolution in llm agents via multi-turn reinforcement learning.
  External Links: 2504.20073,
  [Link](https://arxiv.org/abs/2504.20073)
  Cited by: [§6.1](https://arxiv.org/html/2611.06483#S6.SS1.p1.1 "6.1 Multi-Turn Agentic Reinforcement Learning ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Wu et al. (2026)
  F. Wu, W. Xuan, X. Lu, M. Liu, Y. Dong, Z. Harchaoui, and Y. Choi
  The invisible leash: why rlvr may or may not escape its origin.
  External Links: 2507.14843,
  [Link](https://arxiv.org/abs/2507.14843)
  Cited by: [§6.2](https://arxiv.org/html/2611.06483#S6.SS2.p1.1 "6.2 Understanding and Rethinking RL Post-Training ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Xi et al. (2025a)
  Z. Xi, J. Huang, C. Liao, B. Huang, H. Guo, J. Liu, R. Zheng, J. Ye, J. Zhang, W. Chen, W. He, Y. Ding, G. Li, Z. Chen, Z. Du, X. Yao, Y. Xu, J. Chen, T. Gui, Z. Wu, Q. Zhang, X. Huang, and Y. Jiang
  AgentGym-rl: training llm agents for long-horizon decision making through multi-turn reinforcement learning.
  External Links: 2509.08755,
  [Link](https://arxiv.org/abs/2509.08755)
  Cited by: [§1](https://arxiv.org/html/2611.06483#S1.p1.1 "1 Introduction ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"),
  [§6.1](https://arxiv.org/html/2611.06483#S6.SS1.p1.1 "6.1 Multi-Turn Agentic Reinforcement Learning ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Xi et al. (2025b)
  Z. Xi, C. Liao, G. Li, Y. Yang, W. Chen, Z. Zhang, B. Wang, S. Jin, Y. Zhou, J. Guan, W. Wu, T. Ji, T. Gui, Q. Zhang, and X. Huang
  AgentPRM: process reward models for llm agents via step-wise promise and progress.
  External Links: 2511.08325,
  [Link](https://arxiv.org/abs/2511.08325)
  Cited by: [§6.1](https://arxiv.org/html/2611.06483#S6.SS1.p1.1 "6.1 Multi-Turn Agentic Reinforcement Learning ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Xu et al. (2026a)
  H. Xu, S. Zhao, X. Wu, and A. T. Luu
  Understanding and preventing entropy collapse in rlvr with on-policy entropy flow optimization.
  External Links: 2605.11491,
  [Link](https://arxiv.org/abs/2605.11491)
  Cited by: [§6.2](https://arxiv.org/html/2611.06483#S6.SS2.p1.1 "6.2 Understanding and Rethinking RL Post-Training ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Xu et al. (2026b)
  M. Xu, Z. Wang, M. DENG, Z. Li, Z. Yang, X. Zhu, Y. Liu, B. Zhu, B. Huang, C. Chen, H. Deng, F. Mi, L. Shang, X. Zeng, and Z. Guo
  EnvFactory: scaling tool-use agents via executable environments synthesis and robust rl.
  External Links: 2605.18703,
  [Link](https://arxiv.org/abs/2605.18703)
  Cited by: [§A.1](https://arxiv.org/html/2611.06483#A1.SS1.p1.1 "A.1 Tasks and Training Data ‣ Appendix A Training Details ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Yang et al. (2025)
  A. Yang, A. Li, B. Yang, B. Zhang, B. Hui, B. Zheng, B. Yu, C. Gao, C. Huang, C. Lv, C. Zheng, D. Liu, F. Zhou, F. Huang, F. Hu, H. Ge, H. Wei, H. Lin, J. Tang, J. Yang, J. Tu, J. Zhang, J. Yang, J. Yang, J. Zhou, J. Zhou, J. Lin, K. Dang, K. Bao, K. Yang, L. Yu, L. Deng, M. Li, M. Xue, M. Li, P. Zhang, P. Wang, Q. Zhu, R. Men, R. Gao, S. Liu, S. Luo, T. Li, T. Tang, W. Yin, X. Ren, X. Wang, X. Zhang, X. Ren, Y. Fan, Y. Su, Y. Zhang, Y. Zhang, Y. Wan, Y. Liu, Z. Wang, Z. Cui, Z. Zhang, Z. Zhou, and Z. Qiu
  Qwen3 technical report.
  External Links: 2505.09388,
  [Link](https://arxiv.org/abs/2505.09388)
  Cited by: [§A.2](https://arxiv.org/html/2611.06483#A1.SS2.p1.1 "A.2 Models and Training Hyperparameters ‣ Appendix A Training Details ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Yang et al. (2023)
  J. Yang, A. Prabhakar, K. Narasimhan, and S. Yao
  InterCode: standardizing and benchmarking interactive coding with execution feedback.
  External Links: 2306.14898,
  [Link](https://arxiv.org/abs/2306.14898)
  Cited by: [§A.1](https://arxiv.org/html/2611.06483#A1.SS1.p1.1 "A.1 Tasks and Training Data ‣ Appendix A Training Details ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Yu et al. (2025)
  Q. Yu, Z. Zhang, R. Zhu, Y. Yuan, X. Zuo, Y. Yue, W. Dai, T. Fan, G. Liu, L. Liu, X. Liu, H. Lin, Z. Lin, B. Ma, G. Sheng, Y. Tong, C. Zhang, M. Zhang, W. Zhang, H. Zhu, J. Zhu, J. Chen, J. Chen, C. Wang, H. Yu, Y. Song, X. Wei, H. Zhou, J. Liu, W. Ma, Y. Zhang, L. Yan, M. Qiao, Y. Wu, and M. Wang
  DAPO: an open-source llm reinforcement learning system at scale.
  External Links: 2503.14476,
  [Link](https://arxiv.org/abs/2503.14476)
  Cited by: [§6.1](https://arxiv.org/html/2611.06483#S6.SS1.p1.1 "6.1 Multi-Turn Agentic Reinforcement Learning ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Yu et al. (2019)
  T. Yu, R. Zhang, K. Yang, M. Yasunaga, D. Wang, Z. Li, J. Ma, I. Li, Q. Yao, S. Roman, Z. Zhang, and D. Radev
  Spider: a large-scale human-labeled dataset for complex and cross-domain semantic parsing and text-to-sql task.
  External Links: 1809.08887,
  [Link](https://arxiv.org/abs/1809.08887)
  Cited by: [§A.1](https://arxiv.org/html/2611.06483#A1.SS1.p1.1 "A.1 Tasks and Training Data ‣ Appendix A Training Details ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Yuan et al. (2025)
  L. Yuan, W. Chen, Y. Zhang, G. Cui, H. Wang, Z. You, N. Ding, Z. Liu, M. Sun, and H. Peng
  From `f(x)` and `g(x)` to `f(g(x))`: llms learn new skills in rl by composing old ones.
  External Links: 2509.25123,
  [Link](https://arxiv.org/abs/2509.25123)
  Cited by: [§6.2](https://arxiv.org/html/2611.06483#S6.SS2.p1.1 "6.2 Understanding and Rethinking RL Post-Training ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Yue et al. (2025)
  Y. Yue, Z. Chen, R. Lu, A. Zhao, Z. Wang, Y. Yue, S. Song, and G. Huang
  Does reinforcement learning really incentivize reasoning capacity in llms beyond the base model?.
  External Links: 2504.13837,
  [Link](https://arxiv.org/abs/2504.13837)
  Cited by: [§B.2](https://arxiv.org/html/2611.06483#A2.SS2.p1.2 "B.2 Pass⁢@⁢𝐾 ‣ Appendix B Evaluation Details ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"),
  [§1](https://arxiv.org/html/2611.06483#S1.p2.1 "1 Introduction ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"),
  [§6.2](https://arxiv.org/html/2611.06483#S6.SS2.p1.1 "6.2 Understanding and Rethinking RL Post-Training ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Zhai et al. (2026)
  Z. Zhai, W. Yan, X. Shao, and X. Wang
  Does rl expand the capability boundary of llm agents? a pass@(k,t) analysis.
  External Links: 2604.14877,
  [Link](https://arxiv.org/abs/2604.14877)
  Cited by: [§2.2](https://arxiv.org/html/2611.06483#S2.SS2.p1.1 "2.2 Pass⁢@⁢(𝐾,𝑇): Sampling Breadth and Interaction Depth ‣ 2 Preliminaries and Evaluation Framework ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"),
  [§6.2](https://arxiv.org/html/2611.06483#S6.SS2.p1.1 "6.2 Understanding and Rethinking RL Post-Training ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Zheng et al. (2026)
  Y. Zheng, H. Sun, J. Bao, L. Liu, H. Jiang, Y. Song, and D. Dou
  PGPO: potential-guided policy optimization for multi-turn agentic tasks.
  arXiv preprint arXiv:2609.02236.
  Cited by: [§6.1](https://arxiv.org/html/2611.06483#S6.SS1.p1.1 "6.1 Multi-Turn Agentic Reinforcement Learning ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Zhou et al. (2024)
  S. Zhou, F. F. Xu, H. Zhu, X. Zhou, R. Lo, A. Sridhar, X. Cheng, T. Ou, Y. Bisk, D. Fried, U. Alon, and G. Neubig
  WebArena: a realistic web environment for building autonomous agents.
  External Links: 2307.13854,
  [Link](https://arxiv.org/abs/2307.13854)
  Cited by: [§6.1](https://arxiv.org/html/2611.06483#S6.SS1.p1.1 "6.1 Multi-Turn Agentic Reinforcement Learning ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Zhu et al. (2026a)
  K. Zhu, Z. Jin, D. Huang, H. Yuan, Y. Hao, K. Liu, and J. Zhao
  Beyond simply environment scaling: designing effective environment distributions for multimodal agent learning.
  arXiv preprint arXiv:2608.03571.
  Cited by: [§6.1](https://arxiv.org/html/2611.06483#S6.SS1.p1.1 "6.1 Multi-Turn Agentic Reinforcement Learning ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
- Zhu et al. (2026b)
  K. Zhu, Z. Jin, S. Tu, H. Yuan, Y. Bai, K. Liu, J. Li, and J. Zhao
  SFT conflicts, RL coexists: A theoretical and empirical analysis of multi-task learning for llms.
  CoRR abs/2608.03573.
  External Links: [Link](https://doi.org/10.48550/arXiv.2608.03573),
  [Document](https://dx.doi.org/10.48550/ARXIV.2608.03573),
  2608.03573
  Cited by: [§6.2](https://arxiv.org/html/2611.06483#S6.SS2.p1.1 "6.2 Understanding and Rethinking RL Post-Training ‣ 6 Related Work ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").

## Appendix A Training Details

### A.1 Tasks and Training Data

We train and evaluate agents on five representative tasks, covering tool calling, interactive code generation, embodied planning, terminal operations.
For BFCL ([Patil et al., 2025](https://arxiv.org/html/2611.06483#bib.bib38)), we use executable tool environments and interaction trajectories from EnvFactory ([Xu et al., 2026b](https://arxiv.org/html/2611.06483#bib.bib39)) as training data, with downstream evaluation restricted to BFCL.
For DeepCoder-MT, we construct multi-turn code generation tasks from DeepCoder ([Luo et al., 2025](https://arxiv.org/html/2611.06483#bib.bib40)) programming problems: at each turn, the model can submit a candidate program, inspect unit-test feedback, and revise the program in subsequent turns.
For FrozenLake, we independently generate training and test maps, ensuring that the two splits are disjoint.
For Terminal-Bench 1.0 ([Merrill et al., 2026](https://arxiv.org/html/2611.06483#bib.bib41)), we use the training tasks provided by Tmax ([Ivison et al., 2026](https://arxiv.org/html/2611.06483#bib.bib42)).
For InterCode-SQL ([Yang et al., 2023](https://arxiv.org/html/2611.06483#bib.bib43)), we construct interactive SQL training environments from the Spider training set ([Yu et al., 2019](https://arxiv.org/html/2611.06483#bib.bib44)) and evaluate on a separate split.

### A.2 Models and Training Hyperparameters

We consider Qwen3-4B and Qwen3-8B ([Yang et al., 2025](https://arxiv.org/html/2611.06483#bib.bib45)) and three RL algorithms: GRPO ([Guo et al., 2025](https://arxiv.org/html/2611.06483#bib.bib11)), GiGPO ([Feng et al., 2025b](https://arxiv.org/html/2611.06483#bib.bib15)), and PPO ([Schulman et al., 2017](https://arxiv.org/html/2611.06483#bib.bib46)). GRPO and GiGPO do not use value networks, whereas PPO trains a separate critic to estimate state values. GiGPO derives step-level credit assignment from terminal rewards and recurring environment states. Neither GiGPO nor PPO requires an additional external process reward model. Our implementation builds on the VeRL framework ([Sheng et al., 2024](https://arxiv.org/html/2611.06483#bib.bib47)), and we thank its developers for their excellent work.

All algorithms are trained from the base model. The learning rate is `1\times 10^{-6}`, with weight decay of `0.01`. Training rollouts are sampled with temperature `1.0` and top-`p` of `1.0`. KL regularization against the reference policy uses the low_var_kl estimator with a coefficient of `0.001`. For GRPO and GiGPO, we sample `G=16` trajectories per task instance. PPO also generates `16` trajectories per task instance to match the sampling budget, but does not use group advantages. Full-Budget and BudgetMix RL use identical training settings; their only difference is the distribution of budgets.

GRPO.
We compute group-relative advantages over `G` trajectories sampled for the same task instance. Environment-observation tokens and padding tokens are excluded from the policy loss.

GiGPO.
Following the official GiGPO ([Feng et al., 2025b](https://arxiv.org/html/2611.06483#bib.bib15)) settings, we combine trajectory-level advantages with anchor-state step-level advantages:

|  |  |  |
| --- | --- | --- |
|  | `A_{i,t}=A_{i}^{E}+\omega A_{i,t}^{S}.` |  |

In the main experiments, we set the step-level weight to `\omega=1` and the environment-step discount factor to `\gamma=0.95`.
For environment step `t` of trajectory `i`, the discounted return is

|  |  |  |
| --- | --- | --- |
|  | `R_{i,t}=\sum_{u=t}^{T_{i}}\gamma^{u-t}r_{i,u},` |  |

where `T_{i}` is the number of environment steps in trajectory `i`.

PPO.
The critic is initialized from the same base model as the actor, while optimizers remain independent.
The critic learning rate is `1\times 10^{-5}`, with weight decay of `0.01`. The critic is updated from the start of training, without warmup. Both actor and critic are updated for one epoch per rollout batch. We use token-level generalized advantage estimation (GAE) ([Schulman et al., 2018](https://arxiv.org/html/2611.06483#bib.bib48)). The lower and upper policy-clipping parameters are both set to `0.2`. Value clipping is set to `0.5`.

### A.3 Interaction Budgets

For the `\mathrm{Pass}@T` evaluations, we set
`T_{\max}=70` for FrozenLake,
`T_{\max}=10` for DeepCoder-MT,
`T_{\max}=24` for BFCL-v3,
`T_{\max}=10` for InterCode-SQL,
and `T_{\max}=50` for Terminal-Bench. The maximum number of interaction turns per trajectory is explicitly communicated to the model through the system prompt shown in Table [2](https://arxiv.org/html/2611.06483#A1.T2 "Table 2 ‣ A.3 Interaction Budgets ‣ Appendix A Training Details ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"). Here, [ENVIRONMENT]
denotes the task environment (such as FrozenLake, Terminal-Bench);
[MAX_TURNS]
is the maximum number of permitted interactions;
[CURRENT_TURN]
is the number of completed interactions; and
[REMAINING_TURNS]
is the remaining interaction budget.
[TASK_SPECIFIC_PROMPT]
contains the task instruction, while
[TASK_SPECIFIC_ACTION_FORMAT]
specifies the required action syntax.

Table 2: 
Budget-aware prompt template used during training and evaluation.
The turn counters are instantiated before each model action.

|  |
| --- |
| SYSTEM PROMPT |
| You are an agent interacting with the [ENVIRONMENT] task under a finite interaction budget. One interaction turn consists of one action from you followed by one observation from the environment. Maximum number of interaction turns: [MAX_TURNS]. Number of turns already completed: [CURRENT_TURN]. Number of turns remaining: [REMAINING_TURNS]. Follow the task-specific instruction below. At each turn, output exactly one action in the required format. Do not output multiple actions in one turn, and do not assume that additional turns will be available after the budget is exhausted. |
| TASK-SPECIFIC INSTRUCTION |
| [TASK_SPECIFIC_PROMPT] |
| ACTION FORMAT |
| Output exactly one action in the following format: [TASK_SPECIFIC_ACTION_FORMAT] |

### A.4 BudgetMix Implementation

Algorithm 1  BudgetMix with GRPO

1:
Policy `\pi_{\theta}`, dataset `\mathcal{D}`, group size `G`,
candidate budgets `\mathcal{B}(x)`

2:
for each training iteration do

3:
  `\pi_{\mathrm{old}}\leftarrow\pi_{\theta}`

4:
  Sample a task batch `\mathcal{X}` from `\mathcal{D}`

5:
  for each task `x\in\mathcal{X}` do

6:
   Sample `B\sim\operatorname{Uniform}(\mathcal{B}(x))`

7:
   Insert `B` into the budget-aware prompt

8:
   Collect `G` trajectories using `\pi_{\mathrm{old}}`,
each with at most `B` interaction turns

9:
   Assign outcome rewards `R_{1},\ldots,R_{G}`

10:
   `A_{i}\leftarrow\dfrac{R_{i}-\operatorname{mean}(R)}{\operatorname{std}(R)+\epsilon}`
for `i=1,\ldots,G`

11:
  end for

12:
  Update `\pi_{\theta}` using the standard GRPO objective
with reference KL regularization

13:
end for

Budget sampling. BudgetMix follows the training settings of the corresponding Full-Budget RL baseline, changing only the interaction-budget distribution. For each task `x`, we construct candidate budgets at `10\%` intervals of its full budget `B_{\max}(x)`:

|  |  |  |  |
| --- | --- | --- | --- |
|  | `\mathcal{B}(x)=\operatorname{Unique}\left(\left\{\left\lceil\frac{k}{10}B_{\max}(x)\right\rceil:k=1,\ldots,10\right\}\right),\qquad B\sim\operatorname{Uniform}(\mathcal{B}(x)).` |  | (3) |

The distribution remains fixed throughout training. Algorithm [1](https://arxiv.org/html/2611.06483#alg1 "Algorithm 1 ‣ A.4 BudgetMix Implementation ‣ Appendix A Training Details ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?") presents the implementation of BudgetMix using GRPO as an example. For GRPO and GiGPO, all trajectories within a task group share one sampled budget. For PPO, the actor and critic receive the same budget conditioning. The prompt specifies the assigned budget and the number of completed interactions.

Rewards and termination. Trajectories that exhaust their budget without success receive a terminal success reward of zero. For PPO, task termination and budget exhaustion both use zero terminal bootstrap, with trajectories retained for policy and value updates. For GiGPO, we match anchors within the same task instance and rollout group using both the environment state and the remaining interaction budget. Specifically, the anchor is `(s_{t},B-t)`, where `t` counts completed interactions before the current action. Singleton or zero-variance anchor groups receive zero step-level advantage, while the trajectory-level advantage is retained.

## Appendix B Evaluation Details

In this section, we provide a detailed description of the evaluation settings and implementation details presented in our paper.

### B.1 Generation Settings and Paired Comparisons

For all tasks, we evaluate with temperature `0.6` and top-`p=0.9`.
Base and RL models are evaluated on identical task instances, with the same prompt templates, interaction budgets, and numbers of sampled trajectories.
The budget is specified in the system prompt before generation begins, as illustrated in Table [2](https://arxiv.org/html/2611.06483#A1.T2 "Table 2 ‣ A.3 Interaction Budgets ‣ Appendix A Training Details ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?").
Task success within the specified budget is determined by the official evaluator.

### B.2 `\mathrm{Pass}@K`

`\mathrm{Pass}@K`. For each task instance, we generate `n` independent trajectories and denote the number of successful trajectories by `c`.
For `n\geq k`, we use the unbiased estimator

|  |  |  |
| --- | --- | --- |
|  | `\widehat{\mathrm{Pass}@k}=1-\frac{\binom{n-c}{k}}{\binom{n}{k}}.` |  |

This estimator equals the probability of obtaining at least one success when uniformly selecting `k` trajectories without replacement from the `n` generated trajectories. It reduces variance relative to direct estimation using repeated groups of `k` samples. In the main text, we sweep `k` up to `128`. This estimation follows [Chen et al. (2021)](https://arxiv.org/html/2611.06483#bib.bib49) and [Yue et al. (2025)](https://arxiv.org/html/2611.06483#bib.bib23).

### B.3 `\mathrm{Pass}@T`

`\mathrm{Pass}@T`. For interactive tasks, we additionally report `\mathrm{Pass}@T`. Each trajectory allows at most `T` interactions, and performance is measured by the probability that at least one of `k` independent trajectories succeeds. In the main-text `\mathrm{Pass}@T` evaluations, we fix `k=8` and sweep `T`.

Figure 10: 
Model performance and structural performance upper bounds
across interaction budgets.
Gray lines indicate the structural upper bounds.

Some tasks may become structurally unsolvable under overly restrictive budgets. To clarify that our findings in the main text are not driven by this constraint, we also plot the structural performance upper bound for each task at each budget. For FrozenLake, we compute the shortest path for each task instance and use it to determine the structural performance upper bound under a given interaction budget. For BFCL, we estimate this upper bound using the officially annotated ground-truth tool-call trajectories. For DeepCoder and InterCode-SQL, each turn consists of a complete code submission, meaning that every instance is, in principle, solvable within a single turn; their structural upper bounds therefore remain at 100%. As shown in Figure [10](https://arxiv.org/html/2611.06483#A2.F10 "Figure 10 ‣ B.3 Pass⁢@⁢𝑇 ‣ Appendix B Evaluation Details ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"), at small `T`, these upper bounds, shown by the gray lines, decrease on some tasks, notably FrozenLake and BFCL. Nevertheless, substantial headroom remains for both models, yet RL still shows no advantage over base model. This supports our conclusion that the gains of agentic RL depend on sufficiently generous interaction budgets.

### B.4 Local Decision Quality at Matched States

As described in §[3.3](https://arxiv.org/html/2611.06483#S3.SS3 "3.3 Does Multi-Turn RL Improve Step-Level Action Quality? ‣ 3 When Does agentic RL Outperform the Base Model? ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"), we extract intermediate states from complete base and RL trajectories and construct a state pool with equal contributions from the two policies to mitigate bias.
Each state includes the current observation and the history.
For each state, we sample `G=16` next-step actions from each policy and estimate its single-step decision quality by the sample mean of the corresponding action values.
For FrozenLake, we use the known deterministic transition dynamics of the environment to compute the exact `Q^{*}` value of each candidate action via finite-horizon dynamic programming (DP) or breadth-first search (BFS).
For DeepCoder-MT, we execute each candidate program independently and use its pass rate on the official unit tests as the action-quality measure.

### B.5 Error-State Construction

We construct error states to evaluate single-step decision quality as follows.

For FrozenLake, we select a random intermediate state `s_{t}` along a trajectory and execute a randomly chosen action `a_{t}`. If the action increases the shortest-path distance to the goal, we regard the resulting state as worse than the preceding state and include it in the error-state pool.

For DeepCoder-MT, we use Qwen3-1.7B to modify the code at a randomly selected intermediate state. If the modified program passes fewer unit tests than the original program, we regard this as a degradation in code quality and use the resulting state for subsequent evaluation.

Both constructions serve as proxies rather than rigorous definitions of error states.

### B.6 Effect of Process Supervision Signals

In §[5.1](https://arxiv.org/html/2611.06483#S5.SS1 "5.1 High-quality Process Signals Can Partly Mitigate this Risk ‣ 5 Discussion: Towards More Stable Agentic RL ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?") of the main text, we preliminarily investigate whether high-quality process supervision can alleviate the dependence of agentic RL gains on interaction budgets. On FrozenLake, we use oracle `Q`-values as process rewards, following the same procedure as in § [3.3](https://arxiv.org/html/2611.06483#S3.SS3 "3.3 Does Multi-Turn RL Improve Step-Level Action Quality? ‣ 3 When Does agentic RL Outperform the Base Model? ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"): we compute the `Q`-value of each action via finite-horizon dynamic programming. For both tasks, we additionally explore using an LLM judge as a process reward model to provide step-level supervision. Specifically, we use GPT-5.6-Sol as the judge model with the prompt shown in Table [3](https://arxiv.org/html/2611.06483#A2.T3 "Table 3 ‣ B.6 Effect of Process Supervision Signals ‣ Appendix B Evaluation Details ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"). Our results show that even a strong judge model cannot consistently provide high-quality process supervision across all tasks, particularly in more realistic settings such as BFCL.

Table 3: 
LLM judge prompt for step-level process supervision.
The judge scores the current action before execution.
Scores are mapped to `[0,1]` by dividing by 10.

|  |
| --- |
| SYSTEM PROMPT |
| You are evaluating one action taken by an agent in an interactive task. Given the task, interaction history, current observation, and remaining interaction budget, rate the proposed action with an integer from 0 to 10. Evaluate its correctness, relevance, and expected contribution to completing the task efficiently. Necessary intermediate steps can receive full credit. Do not reward verbosity or redundant actions. |
| INPUT |
| Task: [TASK] Interaction history: [HISTORY] Current observation: [OBSERVATION] Remaining turns, including this action: [REMAINING_TURNS] Action to evaluate: [ACTION] |
| OUTPUT FORMAT |
| Output only one integer from 0 to 10, with no explanation. |

## Appendix C Additional `\mathrm{Pass}@K` Experiments

Due to space limitations, the main text presents only the `\mathrm{Pass}@K` results for Qwen3-4B and Qwen3-8B trained with GRPO.
Here, we provide additional results across agentic RL algorithms, base model architectures, and a more realistic task to further substantiate our findings.

### C.1 Additional Agentic RL Algorithms

We first evaluate additional agentic RL algorithms to examine whether our `\mathrm{Pass}@K` findings extend beyond outcome-only GRPO.
We consider two types of methods:
GiGPO ([Feng et al., 2025b](https://arxiv.org/html/2611.06483#bib.bib15)), which uses credit assignment to derive richer, denser learning signals from outcome rewards, and
PPO ([Schulman et al., 2017](https://arxiv.org/html/2611.06483#bib.bib46)), which uses a critic to provide denser process-level learning signals.

Figure 11: 
Additional `\mathrm{Pass}@K` results with GiGPO.

Figure 12: 
Additional `\mathrm{Pass}@K` results with PPO.

As shown in Figure [11](https://arxiv.org/html/2611.06483#A3.F11 "Figure 11 ‣ C.1 Additional Agentic RL Algorithms ‣ Appendix C Additional Pass⁢@⁢𝐾 Experiments ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?") and  [12](https://arxiv.org/html/2611.06483#A3.F12 "Figure 12 ‣ C.1 Additional Agentic RL Algorithms ‣ Appendix C Additional Pass⁢@⁢𝐾 Experiments ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"), our conclusion holds for both algorithms:
RL-trained models consistently outperform their base models as the number of sampled trajectories `K` increases.

### C.2 Additional Model Architectures

We evaluate InternVL3.5-8B ([Wang et al., 2025c](https://arxiv.org/html/2611.06483#bib.bib50)) on FrozenLake and DeepSeek-R1-Distill-Llama-8B ([Guo et al., 2025](https://arxiv.org/html/2611.06483#bib.bib11)) on DeepCoder-MT.
For each model, we conduct RL training with GRPO. Figure [13](https://arxiv.org/html/2611.06483#A3.F13 "Figure 13 ‣ C.2 Additional Model Architectures ‣ Appendix C Additional Pass⁢@⁢𝐾 Experiments ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?") shows that agentic RL consistently surpasses the empirical `\mathrm{Pass}@K` capability boundaries of base models across these architectures. This finding is therefore not specific to the Qwen3 family.

Figure 13: 
`\mathrm{Pass}@K` results for InternVL3.5-8B on FrozenLake
and DeepSeek-R1-Distill-Llama-8B on DeepCoder-MT with GRPO.

### C.3 Additional Tasks

Finally, we include Terminal-Bench ([Merrill et al., 2026](https://arxiv.org/html/2611.06483#bib.bib41)), a more realistic agent benchmark, to examine whether our findings remain robust in more realistic environments. Figure [14](https://arxiv.org/html/2611.06483#A3.F14 "Figure 14 ‣ C.3 Additional Tasks ‣ Appendix C Additional Pass⁢@⁢𝐾 Experiments ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?") shows a pattern consistent with the preceding experiments, supporting the relevance of our findings to realistic settings. For both scales, RL models consistently outperform their base models as `K` increases. These results further suggest that agentic RL can reliably expand the empirical capability boundary.

Figure 14: 
Additional `\mathrm{Pass}@K` results on Terminal-Bench.

## Appendix D Additional `\mathrm{Pass}@T` Experiments

As in Appendix [C](https://arxiv.org/html/2611.06483#A3 "Appendix C Additional Pass⁢@⁢𝐾 Experiments ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"), we vary the RL algorithm, model architecture, and task to examine the generality of our `\mathrm{Pass}@T` findings:
the gains of agentic RL depend on sufficient interaction budgets, and its advantage over the base model shrinks, disappears, or even reverses as the turn budget `T` tightens.
Does this pattern hold across all settings?

### D.1 Additional Agentic RL Algorithms

Whereas the main text primarily reports results with outcome-only GRPO, this section examines GiGPO and PPO.
Both provide process-level learning signals:
GiGPO derives finer-grained credit assignment from outcome rewards, while PPO trains a critic to provide denser learning signals.

Figure 15: 
`\mathrm{Pass}@T` results with GiGPO
on FrozenLake, DeepCoder-MT, BFCL and InterCode-SQL.

Figure 16: 
`\mathrm{Pass}@T` results with PPO
on FrozenLake, DeepCoder-MT, BFCL and InterCode-SQL.

Figure [15](https://arxiv.org/html/2611.06483#A4.F15 "Figure 15 ‣ D.1 Additional Agentic RL Algorithms ‣ Appendix D Additional Pass⁢@⁢𝑇 Experiments ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?") and  [16](https://arxiv.org/html/2611.06483#A4.F16 "Figure 16 ‣ D.1 Additional Agentic RL Algorithms ‣ Appendix D Additional Pass⁢@⁢𝑇 Experiments ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?") reveal an interesting contrast.
FrozenLake is a relatively simple, idealized environment in which single-step decision quality and process rewards can be evaluated reliably.
On this task, both GiGPO and PPO alleviate, to varying degrees, the `\mathrm{Pass}@T` limitation:
rather than losing their advantage as the budget tightens, models trained with these algorithms achieve relatively consistent gains across budgets.
However, on more realistic tasks such as DeepCoder-MT and InterCode-SQL, reliable process supervision is harder to obtain, and neither algorithm effectively alleviates this limitation. This is consistent with our analysis in §[5](https://arxiv.org/html/2611.06483#S5 "5 Discussion: Towards More Stable Agentic RL ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"):
high-quality process supervision can improve single-step decision quality and stabilize gains across interaction budgets.
However, such supervision is difficult to obtain in more realistic tasks, which limits its effectiveness.

### D.2 Additional Model Architectures

We again evaluate InternVL3.5-8B on FrozenLake and DeepSeek-R1-Distill-Llama-8B on DeepCoder-MT. As shown in Figure [17](https://arxiv.org/html/2611.06483#A4.F17 "Figure 17 ‣ D.2 Additional Model Architectures ‣ Appendix D Additional Pass⁢@⁢𝑇 Experiments ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"), the `\mathrm{Pass}@T` limitation persists across these architectures and is not specific to the Qwen3 family. As the interaction budget tightens, the advantage of RL-trained models diminishes and may disappear or reverse.

Figure 17: 
`\mathrm{Pass}@T` results for InternVL3.5-8B on FrozenLake
and DeepSeek-R1-Distill-Llama-8B on DeepCoder-MT.

### D.3 Additional Tasks

Figure 18: 
`\mathrm{Pass}@T` results for the Qwen3 models on Terminal-Bench.

As in Appendix [C](https://arxiv.org/html/2611.06483#A3 "Appendix C Additional Pass⁢@⁢𝐾 Experiments ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"), we also evaluate the Qwen3 models on Terminal-Bench. Figure [18](https://arxiv.org/html/2611.06483#A4.F18 "Figure 18 ‣ D.3 Additional Tasks ‣ Appendix D Additional Pass⁢@⁢𝑇 Experiments ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?") shows that this limitation also arises in more realistic terminal tasks.
As turn budgets tighten, the gains of RL-trained models become inconsistent.
This further highlights the need for a comprehensive understanding of agentic RL to ensure stable and reliable real-world deployment.

Overall, the limitations and risks we identify recur across model architectures and tasks:
the advantage of agentic RL depends on the interaction budget and is not consistently maintained across budgets.
High-quality process rewards can mitigate this limitation, but such ideal supervision is not always available in real-world tasks.
This motivates our preliminary exploration of BudgetMix RL.

## Appendix E Additional Results for Analysis Experiments

The preceding sections of the appendix focus on `\mathrm{Pass}@(K,T)` results.
Here, we present additional results of analysis experiment to complement §[3.3](https://arxiv.org/html/2611.06483#S3.SS3 "3.3 Does Multi-Turn RL Improve Step-Level Action Quality? ‣ 3 When Does agentic RL Outperform the Base Model? ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?") and  [4](https://arxiv.org/html/2611.06483#S4 "4 Mechanisms Behind the Observed Behaviors ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?") of the main text.

Figure 19: Step-level action quality. Each point is one matched state; its coordinates are action quality of the base and RL model. Teal points favor the base model, red points favor the RL model.

Figure 20: Step-level action quality on error states. Each point is one error state.

Figure 21: Step-level action quality of BudgetMix RL.

Figure 22: Step-level action quality on error states of BudgetMix RL.

### E.1 Additional Results of Step-Level Action Quality

In §[3.3](https://arxiv.org/html/2611.06483#S3.SS3 "3.3 Does Multi-Turn RL Improve Step-Level Action Quality? ‣ 3 When Does agentic RL Outperform the Base Model? ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?") of the main text, we analyze how agentic RL affects single-step action quality. While the main experiments use GRPO, here we provide additional results with GiGPO. As shown in Figures [19](https://arxiv.org/html/2611.06483#A5.F19 "Figure 19 ‣ Appendix E Additional Results for Analysis Experiments ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?") and [20](https://arxiv.org/html/2611.06483#A5.F20 "Figure 20 ‣ Appendix E Additional Results for Analysis Experiments ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"), on FrozenLake, where GiGPO can obtain informative step-level credit signals, the RL model achieves better single-step action quality than the base model at both all matched states and error states. In contrast, on DeepCoder-MT, recurring matched states are difficult to obtain, making reliable step-level credit assignment substantially harder. Consequently, the RL model again does not consistently outperform the base model in single-step action quality. These results suggest that high-quality process-level supervision can improve single-step action quality. However, such supervision may be difficult to obtain in more realistic agentic tasks.

Similarly, we evaluate the single-step action quality of models trained with BudgetMix GRPO. As shown in Figure [21](https://arxiv.org/html/2611.06483#A5.F21 "Figure 21 ‣ Appendix E Additional Results for Analysis Experiments ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"), on randomly sampled matched states, BudgetMix RL yields a clear improvement in single-step decision quality.
Unlike standard GRPO, which does not consistently improve action quality and can even degrade it, as shown in Figure [4](https://arxiv.org/html/2611.06483#S3.F4 "Figure 4 ‣ 3.3 Does Multi-Turn RL Improve Step-Level Action Quality? ‣ 3 When Does agentic RL Outperform the Base Model? ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?") of §[3.3](https://arxiv.org/html/2611.06483#S3.SS3 "3.3 Does Multi-Turn RL Improve Step-Level Action Quality? ‣ 3 When Does agentic RL Outperform the Base Model? ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"), BudgetMix does not exhibit such degradation and instead produces consistently higher-quality local decisions.

### E.2 Additional Log-Likelihood Analysis

Figure 23: 
More log-likehood analysis of base and RL models. (a) Additional log-likelihood analysis on BFCL. (b) Cumulative LLR after length matching. Error bars indicate 95% CI.

In §[4.1](https://arxiv.org/html/2611.06483#S4.SS1 "4.1 Likelihood Analysis: Local Surprisal and Trajectory-Level Policy Shift ‣ 4 Mechanisms Behind the Observed Behaviors ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"), we present a mechanistic analysis based on log-likelihoods, primarily on Terminal-Bench. Here, we extend this analysis to BFCL. As shown in Figure [23](https://arxiv.org/html/2611.06483#A5.F23 "Figure 23 ‣ E.2 Additional Log-Likelihood Analysis ‣ Appendix E Additional Results for Analysis Experiments ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?") (a), we observe a consistent pattern: base model assigns similar likelihoods to individual actions generated by base and RL models, yet at the trajectory level, base systematically assigns lower likelihoods to RL trajectories than to its own. These results show a substantial shift between the RL and base policies over complete long-horizon trajectories, despite similar per-token NLLs under the base policy for RL and base actions.

Controlling for output length. We match base and RL trajectories within each task, requiring scored output token counts to differ by at most 10% of the longer sequence. This yields 193 pairs across 89 tasks on Terminal and 283 pairs across 146 tasks on BFCL. Using the cumulative LLR from §[4.1](https://arxiv.org/html/2611.06483#S4.SS1 "4.1 Likelihood Analysis: Local Surprisal and Trajectory-Level Policy Shift ‣ 4 Mechanisms Behind the Observed Behaviors ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?") without token normalization, the matched difference between base and RL models is 185.9 nats on Terminal and 805.8 on BFCL, with both 95% confidence intervals above zero (Figure [23](https://arxiv.org/html/2611.06483#A5.F23 "Figure 23 ‣ E.2 Additional Log-Likelihood Analysis ‣ Appendix E Additional Results for Analysis Experiments ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?") (b)). The separation of cumulative LLRs thus helps us to partly rule out the influence of trajectory length.

### E.3 Additional Training Dynamics

Figure 24: Training dynamics of the trajectory-level reward `R_{\mathrm{multi}}` and step reward `R_{\mathrm{single}}`.

In §[4.2](https://arxiv.org/html/2611.06483#S4.SS2 "4.2 Training Dynamics of Multi-Turn RL ‣ 4 Mechanisms Behind the Observed Behaviors ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"), we track how agentic RL affects trajectory success and single-step action quality as training progresses. Here, we provide additional training dynamics on FrozenLake. As shown in Figure [24](https://arxiv.org/html/2611.06483#A5.F24 "Figure 24 ‣ E.3 Additional Training Dynamics ‣ Appendix E Additional Results for Analysis Experiments ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"), under standard RL, trajectory-level reward `R_{\mathrm{multi}}` (red curve) increases, indicating agent RL can improve trajectory success. However, single-step action quality reward `R_{\mathrm{single}}` (blue curve) does not improve and instead tends to decline. Thus, trajectory-level gains during training do not necessarily translate into better local actions. However, with BudgetMix RL, single-step decision quality `R_{\mathrm{single}}` (gray curve) remains stable or improves slightly, ending approximately `0.1` above the standard RL curve. These results suggest that BudgetMix RL can help mitigate the decline in single-step decision quality. For each of FrozenLake and DeepCoder-MT, we construct a fixed pool of 512 states from base model trajectories on held-out tasks, using multiple rollout seeds and sampling across tasks and trajectory depths to encourage diversity. Each state includes its history and remaining budget. At each validation checkpoint, we sample 8 next-step actions per state and average their quality scores over actions and states to obtain `R_{\mathrm{single}}`. All checkpoints share the same state pool and scoring protocol.

### E.4 Additional Case Study Results

In §[3.3](https://arxiv.org/html/2611.06483#S3.SS3 "3.3 Does Multi-Turn RL Improve Step-Level Action Quality? ‣ 3 When Does agentic RL Outperform the Base Model? ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?"), we find that RL models produce higher-quality actions in error states, suggesting agent RL may improve error recovery.
Here, we provide a more direct case study on BFCL, examining whether models correctly revise a failed tool call in their next action. We collect trajectory prefixes containing tool-call errors (191), drawing half from RL rollouts (91) and half from base (100). Both models then take one action from each identical prefix. The RL model achieves an error correction rate of `41.4\%`, substantially exceeding the `27.2\%` of base model. Figure [25](https://arxiv.org/html/2611.06483#A5.F25 "Figure 25 ‣ E.4 Additional Case Study Results ‣ Appendix E Additional Results for Analysis Experiments ‣ What Does Multi-Turn Reinforcement Learning Really Improve in LLM Agents?") illustrates a case in which the RL model removes an unsupported argument rather than repeating the same error. Together, these results provide further support for our conclusion that agentic RL strengthens error recovery and resilience.

Figure 25: 
A BFCL example in which the RL model corrects an erroneous tool call.
