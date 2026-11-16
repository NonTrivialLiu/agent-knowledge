---
title: "A Practitioner's Guide to Multi-turn Agentic Reinforcement Learning"
url: https://arxiv.org/abs/2510.01132
published: 2025-10-01
fetched: 2026-11-11
type: paper
topics: [training]
summary: "以环境、奖励和策略三要素整理多轮RL，通过TextWorld、ALFWorld、SWE-Gym对照分析稀疏奖励和算法的交互。"
---

# A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning

Ruiyi Wang
Affiliation: University of California, San Diego
Email: {ruiyiwang}@ucsd.edu
  
Prithviraj Ammanabrolu
Affiliation: University of California, San Diego, NVIDIA
Email: {prithvi}@ucsd.edu

## Abstract

We study what actually works and what doesn’t for training large language models as agents via multi-turn reinforcement learning.
Despite rapid progress, existing frameworks and definitions are fragmented, and there is no systematic formulation or analysis of which design choices matter across tasks.
We address this gap by first breaking down the design space into three inter-related pillars—environment, reward, and policy—and empirically derive a recipe for training LLM agents in situated textual domains. In particular, we test TextWorld and ALFWorld, popular domains for testing situated embodied reasoning, as well as SWE-Gym for more software engineering style tasks.
(i) For the environment, we analyze the impacts of task complexity in terms of sizes of the state and action spaces as well as optimal solution length, finding that even simple environments within a domain can provide signal on how well an agent can generalize to more complex tasks.
(ii) For the reward, we ablate relative reward sparsity, observing that while dense turn-level rewards accelerate training, performance and stability is highly dependent on the choice of RL algorithm.
(iii) And for the agent’s policy, we explore the interplay between reward sparsity and biased (PPO, GRPO) and unbiased (RLOO) policy gradient methods in addition to showing how to find the optimal Supervised Fine-tuning (SFT) to RL training ratio given a fixed budget.

![Refer to caption](https://arxiv.org/html/2510.01132v2/fig1.png)

Figure 1: Illustration of multi-turn agentic RL and the key research questions.

## 1 Introduction

Training LLMs as autonomous agents to navigate open-ended environments presents unique challenges: planning across extended horizons, making multi-turn sequential decisions, and optimizing for multi-turn rewards.
The transition from static single-turn problem-solving to dynamic multistep reasoning is essential for agentic benchmarks such as interactive text and embodied simulations (TextWorld ([Côté et al., 2018](https://arxiv.org/html/2510.01132#bib.bib1)), ALFWorld ([Shridhar et al., 2021](https://arxiv.org/html/2510.01132#bib.bib2)), etc.), real-world software programming (OSWorld ([Xie et al., 2024](https://arxiv.org/html/2510.01132#bib.bib4)), SWE-gym ([Pan et al., 2025](https://arxiv.org/html/2510.01132#bib.bib3)), etc.), and abstract reasoning in novel situations (ARC-AGI ([Chollet et al., 2025](https://arxiv.org/html/2510.01132#bib.bib5))).
However, existing multi-turn RL implementations vary widely: some refer to tool-augmented single queries as multi-turn ([Zeng et al., 2025](https://arxiv.org/html/2510.01132#bib.bib10)), while many rely on model-based assumptions ([Wang et al., 2025](https://arxiv.org/html/2510.01132#bib.bib13)).
This fragmentation has led to incomparable results across papers and confusion about what constitutes true multi-turn learning versus pseudo-multi-turn adaptations of single-turn methods.

This paper aims to facilitate research efforts on the open research question: What factors are practically important in making multi-turn RL for LLM agent learning work.
Motivated by the lack of standardization of multi-turn RL approaches, we systematically decompose the design space into three interdependent pillars—environment, reward, and policy—and empirically derive a recipe for training LLM agents in situated textual domains (Figure [1](https://arxiv.org/html/2510.01132#S0.F1 "Figure 1 ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning")).
We evaluate our approach on TextWorld and ALFWorld for embodied reasoning, and SWE-gym for real-world programming, revealing critical insights for each pillar.
For the environment, we investigate how performance scales with environment complexity and task diversity, and how agents generalize across different environments and tasks.
For the policy, we investigate how model priors affect continual multi-turn RL training and analyze the interplay between multi-turn imitation learning (SFT) and multi-turn RL.
We further compare biased (PPO, GRPO) and unbiased (RLOO) policy gradient RL algorithms to isolate benefits from algorithmic heuristics.
For the reward, we experiment with varying densities of per-turn rewards to understand their impact on training.

The experiments show that our recipe works across textual reasoning, situated embodied reasoning, as well as software engineering tasks.
The key findings from our analysis are:
(1) Multi-turn RL performance scales with environment complexity across spatial, object, and solution dimensions;
(2) Agents trained on simpler environments show promising generalization to complex ones;
(3) Multi-task training enhances multi-turn RL performance;
(4) Model priors from minimal demonstrations accelerate convergence, but RL remains essential for generalization;
(5) An optimal SFT:RL ratio exists that balances task accuracy and generalization under fixed budgets;
(6) Both biased and unbiased algorithms achieve stable learning, validating that gains stem from our multi-turn formulation rather than algorithmic heuristics;
(7) Dense turn-level rewards accelerate multi-turn RL training compared to sparse rewards, but require algorithm-specific tuning.

These insights yield a concrete multi-turn RL recipe that guides co-design across all three pillars.
We demonstrate that multi-turn RL with LLMs is not simply an extension of single-turn optimization but requires fundamental rethinking across environment, policy, and reward.
To facilitate future research, we will release our multi-turn agentic RL framework built on veRL ([Sheng et al., 2025](https://arxiv.org/html/2510.01132#bib.bib15)), including the training scripts and model weights of the experiments in this paper.
This work provides both theoretical insights and practical guidelines for developing agentic AI systems capable of operating effectively in real-world interactive environments.

## 2 Related Work

While single-turn RL methods for LLMs including PPO ([Schulman et al., 2017](https://arxiv.org/html/2510.01132#bib.bib6)), RLOO ([Ahmadian et al., 2024](https://arxiv.org/html/2510.01132#bib.bib9)), GRPO ([Shao et al., 2024](https://arxiv.org/html/2510.01132#bib.bib8)), and DAPO ([Yu et al., 2025](https://arxiv.org/html/2510.01132#bib.bib7)) have been extensively optimized for immediate response quality, adapting them to multi-turn agentic scenarios remains non-trivial.
These methods assume rewards directly follow individual actions, but multi-turn environments only reveal outcomes after extended interaction sequences, breaking the action-reward coupling that single-turn methods rely upon.
Existing efforts on multi-turn RL have made limited progress on these challenges.
Some approaches construct multi-turn scenarios by interleaving tool-use or reasoning steps for single-turn QA pairs ([Zeng et al., 2025](https://arxiv.org/html/2510.01132#bib.bib10); [Dong et al., 2025](https://arxiv.org/html/2510.01132#bib.bib12)).
Others who work on true interactive environments either rely on sparse terminal rewards without turn-level learning signals ([Wang et al., 2025](https://arxiv.org/html/2510.01132#bib.bib13)), or assign turn-level advantages uniformly across sequence tokens without fine-grained credit assignment ([Zhou et al., 2025](https://arxiv.org/html/2510.01132#bib.bib11)).
More importantly, there lacks a comprehensive understanding of how the three fundamental pillars of RL – environment, policy, and reward – jointly determine performance in multi-turn interactive environments. This paper provides a systematic analysis on how the fundamental pillars of RL impact multi-turn RL training, respectively, and concludes insights on how to practically train multi-turn RL in different interactive agentic environments. Throughout the paper, we dedicate related works in individual sections.

## 3 Multi-turn Agentic Reinforcement Learning

We formulate multi-turn agentic tasks as a Partially Observable Markov Decision Process (POMDP) problem, defined as a tuple `(\mathcal{S},\mathcal{A},\mathcal{T},\mathcal{R},\Omega,\mathcal{O},\gamma)`.
Taking the Textworld task ([Côté et al., 2018](https://arxiv.org/html/2510.01132#bib.bib1)) as an example, an agent takes the action `a_{t}` (go south) sampled from the action space `\mathcal{A}` and receives a text observation `o_{t}` (You are in front of a garden) from the observation space `\Omega`.
`o_{t}` is a partial description of the true state `s_{t}` in the hidden state space `\mathcal{S}` which contains the complete state world model.
We assume that the state transition function `\mathcal{T}:\mathcal{S}\times\mathcal{A}\rightarrow\mathcal{S}` is deterministic.
Upon taking an action, the agent also receives a scalar reward `r_{t}=\mathcal{R}(s_{t},a_{t})`.
The agent’s objective is to learn a policy that maximizes the expected discounted sum of rewards `\mathbb{E}[\sum_{t}\gamma^{t}\cdot r_{t}]`.

We denote the trajectory history consisting of a task prompt `u`, action and state sequences by `h_{t}=(u,s_{0},a_{0},s_{1},a_{1},\cdots,s_{t})`11
1
We substitute observation `o` for state `s` for simplicity. The agent has no access to the true state of the game..
An LLM agent with policy `\pi_{\theta}` samples an action sequence `a_{t}\sim\pi_{\theta}(\cdot|h_{t})` based on the trajectory history.
`a_{t}` is a token sequence in natural language: `(a_{t}^{1},a_{t}^{2},...,a_{t}^{n_{t}},a_{t}^{eos})`, with each token `a_{t}^{i}` generated as `\pi_{\theta}(\cdot|h_{t},a_{t}^{<i})`.
Agentic environments execute language commands only upon completion, naturally defining the reward structure at the command boundaries, marked by <eos> tokens.
Therefore, we assign scalar reward `r_{t}` at `a_{t}^{eos}`, and the reward for each action token is formulated as:
`r_{t}^{i}=\begin{cases}r_{t}&\text{if }a_{t}^{i}=\texttt{<eos>}\\
0&\text{otherwise}\end{cases}`.
We make sure only action tokens contribute to the loss by masking out all state tokens.

Here is a concrete example: the input to the LLM during the rollout stage using a chat template is:

```
<|im_start|>user
Your task is: {task prompt}. state: {state 0} your action:<|im_end|>
<|im_start|>assistant
{action 0}<|im_end|>
...
<|im_start|>user
state: {state t} your action:<|im_end|>
<|im_start|>assistant
```

The LLM of policy `\pi_{\theta}` generates the output {action t}<|im_end|>.
The environment handles state transition and reward computation: next_state, reward, done = env.step(state, action).
The reward for each turn is assigned to the <|im_end|> token. The action and next state are then appended to the chat history under the template.

## 4 Background and Experimental Setup

Our experiments systematically investigate how three fundamental pillars of RL impact multi-turn agentic RL performance.
For Environment (§[5](https://arxiv.org/html/2510.01132#S5 "5 Environment ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning")), we examine how scaling environment complexity affects learning across spatial, object, and solution dimensions (§[5.1](https://arxiv.org/html/2510.01132#S5.SS1 "5.1 How does multi-turn RL performance scale with environment complexity? ‣ 5 Environment ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning")), evaluate whether agents trained on simpler environments generalize to complex ones (§[5.2](https://arxiv.org/html/2510.01132#S5.SS2 "5.2 How does multi-turn RL generalize to environments with different complexities? ‣ 5 Environment ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning")), and analyze how task diversity impacts training and generalization (§[5.3](https://arxiv.org/html/2510.01132#S5.SS3 "5.3 How does multi-turn RL generalize to different types of tasks within domain? ‣ 5 Environment ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning")).
For Policy (§[6](https://arxiv.org/html/2510.01132#S6 "6 Policy ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning")), we analyze how the model priors from demonstration data influence RL convergence and identify optimal ratios of SFT-to-RL data ratios under budget constraints (§[6.1](https://arxiv.org/html/2510.01132#S6.SS1 "6.1 How does prior model policy influence multi-turn RL training? ‣ 6 Policy ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning")).
We compare biased algorithms (PPO, GRPO) against unbiased algorithms (RLOO) to isolate benefits of algorithmic design versus our multi-turn formulation (§[6.2](https://arxiv.org/html/2510.01132#S6.SS2 "6.2 How do RL algorithms impact multi-turn RL training? ‣ 6 Policy ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning")).
For Reward (§[7](https://arxiv.org/html/2510.01132#S7 "7 Reward ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning")), we investigate how reward density, the frequency of feedback signals during trajectories, affects training and final performance (§[7.1](https://arxiv.org/html/2510.01132#S7.SS1 "7.1 What reward signals are needed for multi-turn RL training? ‣ 7 Reward ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning")).
These experiments demonstrate that multi-turn RL requires careful co-design across all components rather than naive extensions of single-turn methods.

### Tasks and Environments.

We evaluate on three situated textual benchmarks: TextWorld ([Côté et al., 2018](https://arxiv.org/html/2510.01132#bib.bib1)) and ALFWorld ([Shridhar et al., 2021](https://arxiv.org/html/2510.01132#bib.bib2)) for language grounding in situated embodied reasoning, and SWE-Gym ([Pan et al., 2025](https://arxiv.org/html/2510.01132#bib.bib3)) for real-world software engineering.
We extend veRL ([Sheng et al., 2025](https://arxiv.org/html/2510.01132#bib.bib15))’s efficient RL training infrastructure, integrating these benchmark environments through standard step and reset interfaces.
Critically, unlike traditional RL settings that provide both observations and admissible action lists (reducing the problem to action selection), our agents must generate executable natural language commands from environment observations alone, without action hints—testing their ability to discover valid actions through exploration.
The details of tasks and environments are provided in Appendix [B](https://arxiv.org/html/2510.01132#A2 "Appendix B Details of tasks and environments ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning").

- •

  TextWorld: A text adventure game environment where agents navigate rooms, manipulate objects, and solve quests via natural language.
  We procedurally generate tasks with controlled complexity across three dimensions: world size (w), number of objects (o), and quest length (q).
  For example, “w2-o3-q4” denotes 2 rooms, 3 objects, and a 4-step quest.
  Each task is uses unique seeds for diversity.
- •

  ALFWorld: An embodied household environment requiring multi-step task completion through text interaction.
  We use the text-only variant spanning six task categories, training on the “train” split and evaluating on the “valid_unseen” split.
- •

  SWE-Gym: Real-world programming tasks including bug fixes and feature implementation.
  We focus on 5 representative task types: getmoto, pydantic, mypy, pandas, and iterative_dvc, randomly sampling 90 training and 25 evaluation instances.

### Training and Evaluation.

We use Qwen2.5-1.5B-Instruct, Qwen2.5-7B-Instruct, and Qwen3-8B as base models (abbreviated as Qwen-1.5B, Qwen-7B, and Qwen-8B), training with PPO ([Schulman et al., 2017](https://arxiv.org/html/2510.01132#bib.bib6)), GRPO ([Shao et al., 2024](https://arxiv.org/html/2510.01132#bib.bib8)), and RLOO ([Ahmadian et al., 2024](https://arxiv.org/html/2510.01132#bib.bib9)) algorithms.
Maximum iteration steps and token limits scale with task complexity.
During rollout generation, we use temperature 0.7 to balance exploration-exploitation.
We evaluate agents on held-out test sets, reporting task success rate as our primary metric—the percentage of episodes where agents achieve objectives within exploration budgets. For SWE-Gym, we report test suite passing ratios.
Full training details and hyperparameter tuning analysis appear in Appendices [C](https://arxiv.org/html/2510.01132#A3 "Appendix C Details of training and evaluation ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning") and [A](https://arxiv.org/html/2510.01132#A1 "Appendix A Hyperparameter tuning for multi-turn RL ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning").

## 5 Environment

The environment fundamentally determines the challenges agents must overcome.
While single-turn tasks primarily measure reasoning difficulty, multi-turn environments introduce dimensions such as spatial navigation, object manipulation, and extended planning horizons.
We investigate three core research questions for practical multi-turn deployment:
(1) How does environment complexity affect multi-turn RL training efficiency?
This determines exploration budgets and model size requirements for tasks with varied environment complexities.
(2) Can agents trained on simpler environments generalize to complex ones?
This addresses the key consideration to scaling up agentic systems.
(3) How does task diversity impact training and generalization? We not only show our multi-turn RL recipe that works for TextWorld generalizes to ALFWorld and SWE-Gym, but also reveal whether agents learn generalizable skills or memorize task-specific behaviors.
Our experiments demonstrate that multi-turn RL enables effective knowledge transfer across environments and diverse tasks.

### Setup.

We design two experimental conditions to vary environment complexity and task diversity.
For environment complexity, starting from the base configuration w2-o3-q4, we create controlled variations: w8-o3-q4 (increased spatial complexity), w2-o12-q4 (increased object complexity), w8-o12-q4 (increased both dimensions), and w4-o6-q8 (proportional scaling across all dimensions).
In SWE-Gym, we focus on the getmoto task subset to isolate complexity factors, categorizing tasks into Easy, Medium, and Hard based on two distinct metrics: (1) Solution Complexity (lines of code in the gold patch) and (2) Verification Complexity (size of the test suite).
For task diversity, we construct mixtures of increasing heterogeneity for training.
In ALFWorld, we test single type (pick & place only), 4 types (heat, cool, cook, examine) and all 6 types (adding pick two & place).
In SWE-Gym, we compare single type (getmoto only) against all 5 types (getmoto, pydantic, mypy, pandas, and iterative_dvc).
All mixtures have the same data size to ensure fair comparison, with evaluation on both single-type and mixed-types held-out test sets.
We train Qwen-1.5B, Qwen-7B, and Qwen-8B models using PPO and GRPO with consistent hyperparameters. Full task specifications and training details appear in Appendices [B.1](https://arxiv.org/html/2510.01132#A2.SS1 "B.1 Additional task details for § ‣ Appendix B Details of tasks and environments ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning") and [C.1](https://arxiv.org/html/2510.01132#A3.SS1 "C.1 Additional training details for § ‣ Appendix C Details of training and evaluation ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning").

### 5.1 How does multi-turn RL performance scale with environment complexity?

Table [1](https://arxiv.org/html/2510.01132#S5.T1 "Table 1 ‣ 5.1 How does multi-turn RL performance scale with environment complexity? ‣ 5 Environment ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning") reveals that base models struggle dramatically as environment complexity increases, with performance dropping from 17% to just 3% when both spatial and object dimensions are scaled.
Critically, multi-turn RL improvements diminish with increasing complexity—while PPO achieves a 88% improvement on the base environment, this drops to 51% on the most complex setting.
Notably, object complexity proves more challenging than spatial complexity, suggesting that manipulating and tracking multiple objects across turns presents fundamentally harder challenges than spatial exploration in situated textual domains.
We observe parallel trends in the coding domain (Table [2](https://arxiv.org/html/2510.01132#S5.T2 "Table 2 ‣ 5.1 How does multi-turn RL performance scale with environment complexity? ‣ 5 Environment ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning")). Base model performance degrades as tasks require longer code solutions or pass more rigorous test suites. However, Multi-turn GRPO consistently recovers performance across all difficulty tiers, validating that our metrics capture genuine complexity.

Performance also scales with model size. As shown in Table [3](https://arxiv.org/html/2510.01132#S5.T3 "Table 3 ‣ 5.1 How does multi-turn RL performance scale with environment complexity? ‣ 5 Environment ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning"), the 7B model reaches 72% success on w4-o6-q8, demonstrating that larger models better handle the increased state spaces of complex environments.
Notably, even the 1.5B model shows strong learning potential with 65% and 58% gains on w2-o3-q4 and w4-o6-q8 respectively.

Table 1: Multi-turn PPO performance on TextWorld tasks with varying complexity dimensions. Base environment: w2-o3-q4. Maximum steps: 12.

| Tasks w/ varying env complexity | Qwen-1.5B | Qwen-1.5B (PPO) |
| --- | --- | --- |
| w2-o3-q4 (base env) | `0.17` | `0.88_{\uparrow 0.71}` |
| w8-o3-q4 (4x rooms) | `0.07` | `0.68_{\uparrow 0.61}` |
| w2-o12-q4 (4x objects) | `0.08` | `0.54_{\uparrow 0.46}` |
| w8-o12-q4 (4x objects & rooms) | `0.03` | `0.51_{\uparrow 0.48}` |

Table 2: Multi-turn GRPO performance on SWE-Gym tasks across varying complexity dimensions. We compare the Qwen3-8B base model against the policy trained with Multi-turn GRPO, categorizing tasks by solution size (lines of patch) and verification effort (test suite size).

|  |  |  |
| --- | --- | --- |
| Task Complexity Metrics | Qwen3-8B (Base) | Qwen3-8B (GRPO) |
| Metric A: Solution Complexity (Lines of Code) | | |
| Easy (`\leq` 8 lines) | `0.048` | `0.072_{\uparrow 0.024}` |
| Medium (9–31 lines) | `0.048` | `0.109_{\uparrow 0.061}` |
| Hard (`>` 31 lines) | `0.018` | `0.096_{\uparrow 0.078}` |
| Metric B: Verification Complexity (Test Suite Size) | | |
| Easy (`\leq` 17 tests) | `0.040` | `0.133_{\uparrow 0.093}` |
| Medium (18–53 tests) | `0.028` | `0.075_{\uparrow 0.047}` |
| Hard (`>` 53 tests) | `0.017` | `0.105_{\uparrow 0.088}` |

Table 3: Multi-turn PPO performance comparison across model sizes on proportionally scaled TextWorld environments. Maximum steps: 12 (w2-o3-q4) and 24 (w4-o6-q8).

| Tasks | Qwen-1.5B | Qwen-1.5B (PPO) | Qwen-7B | Qwen-7B (PPO) |
| --- | --- | --- | --- | --- |
| w2-o3-q4 | `0.15` | `0.8_{\uparrow 0.65}` | `0.65` | `0.98_{\uparrow 0.33}` |
| w4-o6-q8 | `0.01` | `0.59_{\uparrow 0.58}` | `0.28` | `0.72_{\uparrow 0.44}` |

Table 4: Impact of exploration horizon on multi-turn performance. We compare the effect of increasing allowed exploration steps on TextWorld w2-o3-q4 tasks(Left) and allowed tool calls/response length on SWE-Gym tasks (Right).

TextWorld (PPO)

Model: Qwen-2.5-1.5B

| Exploration Steps | Base | PPO |
| --- | --- | --- |
| `6` | `0.05` | `0.55_{\uparrow 0.50}` |
| `8` | `0.09` | `0.73_{\uparrow 0.64}` |
| `12` | `0.15` | `0.80_{\uparrow 0.65}` |
| `16` | `0.17` | `0.88_{\uparrow 0.71}` |

SWE-Gym (GRPO)

Model: Qwen3-8B

| Tool Calls (Context) | Base | GRPO |
| --- | --- | --- |
| `10` (3k tokens) | `0.03` | `0.03_{\uparrow 0.00}` |
| `25` (4k tokens) | `0.04` | `0.18_{\uparrow 0.14}` |
| `40` (6k tokens) | `0.04` | `0.22_{\uparrow 0.18}` |

Lastly, we investigate how the exploration budget (the maximum steps agents can take during rollout) affects learning.
For w2-o3-q4 tasks with 4-step optimal solutions, we vary maximum steps from 6 to 16.
Table [4](https://arxiv.org/html/2510.01132#S5.T4 "Table 4 ‣ 5.1 How does multi-turn RL performance scale with environment complexity? ‣ 5 Environment ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning") shows that performance saturates beyond 8 exploration steps.
Constraining agents to 6 steps (`1.5\times` optimal) limits PPO to 55% success, while 8 steps (`2\times` optimal) yields 73% success.
Further increases to 12 and 16 steps produces only marginal gains.
These results indicate that while insufficient exploration severely limits learning, budgets beyond 2× optimal provide negligible benefits for TextWorld tasks.
In contrast, complex coding tasks benefit significantly from extended horizons. In SWE-Gym, increasing the context window and allowed tool calls from 10 to 40 boosts success rates from 3% to 22%. Unlike simple text games, reasoning in software repositories does not saturate quickly; rather, sustained exploration allows agents to iteratively debug and refine solutions.

### 5.2 How does multi-turn RL generalize to environments with different complexities?

To investigate whether multi-turn RL learns transferable skills, we evaluate cross-environment generalization.
We train single-task models on w2-o3-q4, w8-o3-q4, and w2-o12-q4, plus a mixed-complexity model on equal proportions of w2-o12-q4 and w8-o3-q4, maintaining constant total RL data across conditions.
Table [5](https://arxiv.org/html/2510.01132#S5.T5 "Table 5 ‣ 5.2 How does multi-turn RL generalize to environments with different complexities? ‣ 5 Environment ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning") reveals that agents trained on simpler environments achieve substantial generalization to more complex ones, evidenced by the model trained on w2-o3-q4 that improves performance across all higher-complexity environments.
Transfer is particularly strong from w8-o3-q4 (increased spatial complexity), which achieves the largest average improvements across targets—notably improving w8-o12-q4 by 48%, matching the 48% gain from training solely on w8-o12-q4.
These results demonstrate that multi-turn RL acquires reusable skills like spatial exploration and object manipulation that transfer across complexity levels.

This generalization capability extends to non-embodied domains. As shown in Table [6](https://arxiv.org/html/2510.01132#S5.T6 "Table 6 ‣ 5.2 How does multi-turn RL generalize to environments with different complexities? ‣ 5 Environment ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning"), code agents trained on ”Easy” tasks (based on test suite complexity) transfer effectively to harder problems, achieving gains of 4.8% on Medium and 3.6% on Hard tasks. This mirrors our findings in TextWorld, confirming that multi-turn RL acquires robust, reusable behaviors—such as error correction and state tracking—that remain effective even as the environment’s complexity scales.

Table 5: Cross-environment generalization with multi-turn PPO on TextWorld tasks. All models trained with 5000 episodes/epoch (mixed-task: 2500 episodes each).

| Tasks | w2-o12-q4 | w8-o3-q4 | w8-o12-q4 | w4-o6-q8 |
| --- | --- | --- | --- | --- |
| w2-o3-q4 | `0.4_{\uparrow 0.32}` | `0.51_{\uparrow 0.44}` | `0.27_{\uparrow 0.24}` | `0.12_{\uparrow 0.11}` |
| w8-o3-q4 | `0.5_{\uparrow 0.42}` | `0.68_{\uparrow 0.61}` | `0.51_{\uparrow 0.48}` | `0.21_{\uparrow 0.2}` |
| w2-o12-q4 | `0.54_{\uparrow 0.46}` | `0.27_{\uparrow 0.2}` | `0.27_{\uparrow 0.24}` | `0.13_{\uparrow 0.12}` |
| w2-o12-q4 + w8-o3-q4 | `0.41_{\uparrow 0.33}` | `0.52_{\uparrow 0.45}` | `0.34_{\uparrow 0.31}` | `0.17_{\uparrow 0.16}` |

Table 6: Cross-environment generalization with Multi-turn GRPO on SWE-Gym tasks. We evaluate transfer performance across task complexity (Metric A: lines of patch) and verification complexity (Metric B: test suite size). Diagonal elements (gray) indicate in-distribution performance.

Metric A: Solution Complexity

| Tasks | easy | medium | hard |
| --- | --- | --- | --- |
| easy | `0.072_{\uparrow 0.024}` | `0.048_{\uparrow 0.0}` | `0.028_{\uparrow 0.01}` |
| medium | `0.161_{\uparrow 0.113}` | `0.109_{\uparrow 0.061}` | `0.055_{\uparrow 0.037}` |
| hard | `0.082_{\uparrow 0.034}` | `0.091_{\uparrow 0.043}` | `0.096_{\uparrow 0.078}` |

Metric B: Verification Complexity

| Tasks | easy | medium | hard |
| --- | --- | --- | --- |
| easy | `0.133_{\uparrow 0.093}` | `0.076_{\uparrow 0.048}` | `0.053_{\uparrow 0.036}` |
| medium | `0.082_{\uparrow 0.042}` | `0.075_{\uparrow 0.047}` | `0.042_{\uparrow 0.025}` |
| hard | `0.10_{\uparrow 0.06}` | `0.062_{\uparrow 0.034}` | `0.105_{\uparrow 0.088}` |

### 5.3 How does multi-turn RL generalize to different types of tasks within domain?

In §[5.1](https://arxiv.org/html/2510.01132#S5.SS1 "5.1 How does multi-turn RL performance scale with environment complexity? ‣ 5 Environment ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning") and §[5.2](https://arxiv.org/html/2510.01132#S5.SS2 "5.2 How does multi-turn RL generalize to environments with different complexities? ‣ 5 Environment ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning"), we examined how agents handle varying environment complexities within single task types.
Here we address a broader question: does our multi-turn RL recipe works for complex situated environments like ALFWorld and real-world scenarios like SWE-Gym?
Moreover, can agents trained on task subsets generalize to full task distributions?
We investigate how training on diverse task types affects generalization across two domains.
In ALFWorld, different tasks require distinct physical skills—cleaning involves finding and placing objects, while heating requires operating appliances in specific sequences. In SWE-gym, tasks span diverse software engineering challenges from fixing pydantic issues to resolving pandas problems.

Table [7](https://arxiv.org/html/2510.01132#S5.T7 "Table 7 ‣ 5.3 How does multi-turn RL generalize to different types of tasks within domain? ‣ 5 Environment ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning") and [8](https://arxiv.org/html/2510.01132#S5.T8 "Table 8 ‣ 5.3 How does multi-turn RL generalize to different types of tasks within domain? ‣ 5 Environment ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning") show that multi-turn RL successfully applies to challenging ALFworld and SWE-Gym environments.
Remarkably, agents trained on single task types achieve decent generalization to unseen task types, with 12% (ALFWorld) and 7% (SWE-Gym) improvements across all task types from single-type training alone.
This indicates that multi-turn RL learns transferable skills even from limited task exposure.
Surprisingly, multi-task training benefits seemingly unrelated tasks—agents trained on clean, heat, cool, and cook mixtures outperform single pick & place specialists by 19% on the single task itself and 21% on all-type evaluation.
The results demonstrate that multi-turn RL develops generalizable skills that transfer across diverse objectives.

Table 7: Multi-turn PPO performance on ALFWorld unseen tasks, trained on various task mixtures.

| Task mixture for training | Tested on single type (PPO) | Tested on all types (PPO) |
| --- | --- | --- |
| Single type of tasks | `0.63_{\uparrow 0.19}` | `0.59_{\uparrow 0.12}` |
| Mixture of 4 types of tasks | `0.82_{\uparrow 0.38}` | `0.8_{\uparrow 0.33}` |
| Mixture of 6 types of tasks (all) | `0.76_{\uparrow 0.32}` | `0.74_{\uparrow 0.27}` |

Table 8: Multi-turn GRPO performance on SWE-gym tasks, trained on various task mixtures. More comments on the use of GRPO algorithm are presented in §[6.2](https://arxiv.org/html/2510.01132#S6.SS2 "6.2 How do RL algorithms impact multi-turn RL training? ‣ 6 Policy ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning")

| Task mixture for training | Tested on single type (GRPO) | Tested on all types (GRPO) |
| --- | --- | --- |
| Single type of tasks (getmoto) | `0.28_{\uparrow 0.19}` | `0.11_{\uparrow 0.07}` |
| Mixture of 5 types of tasks (all) | `0.37_{\uparrow 0.28}` | `0.22_{\uparrow 0.18}` |

## 6 Policy

The choice of RL optimization algorithm and model initialization critically determines multi-turn RL performance.
First, we examine the role of demonstration data. In practice, access to human demonstration data for supervised fine-tuning (SFT) may be limited.
We ask: (1) What prior model policy enables effective multi-turn RL?
This addresses whether expensive human demonstrations are necessary if agents can learn effectively from scratch.
(2) Given a fixed data budget, what is the optimal ratio of SFT to RL data?
This determines how to best allocate limited resources between demonstration collection and online learning.
Second, we investigate whether RL optimization choices significantly impact multi-turn RL training.
We compare heuristic policy gradient methods (PPO ([Schulman et al., 2017](https://arxiv.org/html/2510.01132#bib.bib6)), GRPO ([Shao et al., 2024](https://arxiv.org/html/2510.01132#bib.bib8)), Reinforce++ ([Hu et al., 2025](https://arxiv.org/html/2510.01132#bib.bib16))) against unbiased methods (RLOO ([Ahmadian et al., 2024](https://arxiv.org/html/2510.01132#bib.bib9))) to isolate the contributions of our multi-turn formulation from specific optimization heuristics—essential for making rigorous claims about algorithmic improvements, as demonstrated in recent work on the pitfalls of heuristic-dependent results ([Oertell et al., 2025](https://arxiv.org/html/2510.01132#bib.bib14)).

### Setup.

TextWorld provides gold solutions for each procedurally generated game, which we use as demonstration data for SFT, representing human multi-turn trajectories.
The SFT data follows a turn-based chat format, the default template used in most instruction-following scenarios.
We generate SFT data with different random seeds than RL data to prevent leakage.
We train Qwen-1.5B, Qwen-7B, and Qwen-8B models using PPO, GRPO, Reinforce++, and RLOO with consistent hyperparameters across experiments.
Full task specifications and training details appear in Appendices [B.2](https://arxiv.org/html/2510.01132#A2.SS2 "B.2 Additional task details for § ‣ Appendix B Details of tasks and environments ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning") and [C.2](https://arxiv.org/html/2510.01132#A3.SS2 "C.2 Additional training details for § ‣ Appendix C Details of training and evaluation ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning").

### Multi-turn PPO Formulation.

For optimization algorithms with advantage estimation, such as Proximal Policy Optimization (PPO) ([Schulman et al., 2017](https://arxiv.org/html/2510.01132#bib.bib6)), we adopt token-level credit assignment.
We compute token-level values and apply to TD error as `\delta_{t}^{i}=r_{t}^{i}+\gamma V(h_{t}^{i+1})-V(h_{t}^{i})` where `h_{t}^{i}` is the history up to and including token `a_{t}^{i}`.
Then we estimate the advantage for each token using GAE: `\hat{A}_{t}^{i}=\sum_{l=0}^{L-i}(\gamma\lambda)^{l}\delta_{t}^{i+l}`, where `L` is the horizon (number of tokens until episode ends).
Even though only <eos> tokens receive rewards, all preceding tokens get non-zero advantages through value bootstrapping.
Therefore, the Clipped Surrogate Objective for all tokens in the trajectory can be written as:

|  |  |  |
| --- | --- | --- |
|  | `L^{CLIP}(\theta)=\mathbb{E}_{\tau\sim\pi_{\theta}}\left[\sum_{t=0}^{T}\sum_{i=1}^{n_{t}+1}\min\left(r_{t}^{i}(\theta)\hat{A}_{t}^{i},\text{clip}(r_{t}^{i}(\theta),1-\epsilon,1+\epsilon)\hat{A}_{t}^{i}\right)\right]` |  |

where the probability ratio for each token is: `r_{t}^{i}(\theta)=\dfrac{\pi_{\theta}(a_{t}^{i}|h_{t},a_{t}^{<i})}{\pi_{\theta_{old}}(a_{t}^{i}|h_{t},a_{t}^{<i})}`.

### 6.1 How does prior model policy influence multi-turn RL training?

We distinguish between establishing a prior (via SFT) and refining it through continual learning (via multi-turn online RL).
This two-stage approach mirrors real-world deployment where agents learn from demonstrations before online learning.
We find that a strong SFT prior dramatically accelerates RL efficiency.
Training on golden solutions from TextWorld tasks w2-o3-q4 reveals that we can match the performance of extensive RL training with a fraction of the data.
As shown in Table [9](https://arxiv.org/html/2510.01132#S6.T9 "Table 9 ‣ 6.1 How does prior model policy influence multi-turn RL training? ‣ 6 Policy ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning"), a model initialized with just 60 demonstrations and refined over 400 RL episodes achieves 85% success, nearly matching the 88% achieved by pure RL training that requires 5000 episodes.

To determine the optimal allocation of resources, we analyze performance under a fixed budget of 1000 cost units, assuming that SFT data costs 10`\times` more than RL episodes to reflect higher human annotation effort.
We find that while pure SFT excels at known tasks, RL is essential for robustness.
Using the full budget for SFT (100 demonstrations) shows excellent in-domain performance (95% on w2-o3-q4 tasks) but poor generalization to harder tasks (55% on w4-o6-q8 tasks).
The sweet spot appears to be a hybrid configuration: 60 demonstrations followed by 400 RL episodes.
This balances the behavioral grounding of SFT with the adaptability of RL, maintaining 85% in-domain success while improving generalization on the complex w4-o6-q8 task to 59%.

Table 9: Performance across SFT/RL data allocations under fixed budget. Models trained on w2-o3-q4, evaluated on w2-o3-q4 and w4-o6-q8. SFT followed by multi-turn PPO. ∗Results from previous experiments included for comparison.

| #SFT data | #RL data | SFT | SFT (test on w4-o6-q8) | SFT+PPO | SFT+PPO (test on w4-o6-q8) |
| --- | --- | --- | --- | --- | --- |
| / | 5000 | 0.17 (base) | 0.01 (base) | 0.88∗ | 0.12∗ |
| 0 | 1000 | / | / | 0.54 | 0.11 |
| 20 | 800 | 0.59 | 0.15 | 0.62 | 0.15 |
| 40 | 600 | 0.75 | 0.51 | 0.72 | 0.44 |
| 60 | 400 | 0.71 | 0.53 | 0.85 | 0.59 |
| 80 | 200 | 0.94 | 0.29 | 0.95 | 0.35 |
| 100 | 0 | 0.95 | 0.55 | / | / |

Finally, we explore whether priors transfer across distinct environments by training SFT models on ALFWorld (3553 samples) to initialize TextWorld agents, and vice versa.
We find that cross-domain priors actively harm multi-turn RL training. Initializing with a different domain causes rapid policy collapse, likely because the specific behavioral biases and action distributions learned from the source environment conflict with the dynamics of the target environment, effectively destabilizing the policy optimization.

### 6.2 How do RL algorithms impact multi-turn RL training?

Understanding whether performance gains stem from our multi-turn formulation or specific algorithmic choices is crucial for establishing the generalizability of our approach.
We compare PPO (heuristic policy gradient method with value function bootstrapping) against RLOO (unbiased policy gradient estimator), as well as recent variants like Reinforce++ and GRPO, to isolate the contributions of our token-level credit assignment from algorithmic design decisions ([Oertell et al., 2025](https://arxiv.org/html/2510.01132#bib.bib14)).

Both PPO and RLOO achieve improvements over base models, showing that the performance gains stem from multi-turn formulation rather than PPO-specific heuristics.
Table [10](https://arxiv.org/html/2510.01132#S6.T10 "Table 10 ‣ 6.2 How do RL algorithms impact multi-turn RL training? ‣ 6 Policy ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning") shows that PPO achieves 88% success on w2-o3-q4 versus RLOO’s 51%.
In contrast, Reinforce++ and GRPO induce negligible gains over the base model.
This gap widens on harder tasks w4-o6-q8: PPO maintains 59% success while RLOO, Reinforce++, and GRPO all suffer collapse for the 1.5B model.

Model scaling helps close the gap on simpler tasks, and PPO maintains the best algorithm in complex reasoning. At 7B parameters, both PPO and RLOO converge on simple w2-o3-q4 tasks (`\approx` 98%), but Reinforce++ and GRPO still lag behind (72% and 79% respectively.
On the harder w4-o6-q8 tasks, PPO dominates with 72% success compared to RLOO’s 47% and GRPO’s 36%.
These results confirm that the performance gains are not due to PPO heuristics, evidenced by RLOO’s consistent improvements across tasks, but they do highlight that PPO is significantly more sample-efficient and robust than Reinforce++ and GRPO in this domain.

Table 10: Comparison of different RL algorithms, including PPO, RLOO, Reinforce++, and GRPO on multi-turn TextWorld tasks across model sizes.

| Task / Model | Base model | RLOO | PPO | Reinforce++ | GRPO |
| --- | --- | --- | --- | --- | --- |
| w2-o3-q4 / Qwen-1.5B | `0.15` | `0.51_{\uparrow 0.36}` | `0.88_{\uparrow 0.73}` | `0.18_{\uparrow 0.03}` | `0.18_{\uparrow 0.03}` |
| w4-o6-q8 / Qwen-1.5B | `0.01` | `0.0` | `0.59_{\uparrow 0.58}` | `0.0` | `0.02_{\uparrow 0.01}` |
| w2-o3-q4 / Qwen-7B | `0.65` | `0.97_{\uparrow 0.32}` | `0.98_{\uparrow 0.33}` | `0.72_{\uparrow 0.07}` | `0.79_{\uparrow 0.14}` |
| w4-o6-q8 / Qwen-7B | `0.28` | `0.47_{\uparrow 0.21}` | `0.72_{\uparrow 0.44}` | `0.33_{\uparrow 0.05}` | `0.36_{\uparrow 0.08}` |

We also examine GRPO in §[5.3](https://arxiv.org/html/2510.01132#S5.SS3 "5.3 How does multi-turn RL generalize to different types of tasks within domain? ‣ 5 Environment ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning") for SWE-Gym tasks.
While GRPO underperforms on the TextWorld tasks in Table [10](https://arxiv.org/html/2510.01132#S6.T10 "Table 10 ‣ 6.2 How do RL algorithms impact multi-turn RL training? ‣ 6 Policy ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning"), SWE-Gym’s environment makes GRPO computationally advantageous. Therefore, we draw parallels between PPO and GRPO as biased algorithms only under sparse reward settings (only final rewards per trajectory).
The improvements from GRPO in Table [8](https://arxiv.org/html/2510.01132#S5.T8 "Table 8 ‣ 5.3 How does multi-turn RL generalize to different types of tasks within domain? ‣ 5 Environment ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning"), together with PPO’s results in Table [10](https://arxiv.org/html/2510.01132#S6.T10 "Table 10 ‣ 6.2 How do RL algorithms impact multi-turn RL training? ‣ 6 Policy ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning"), show the effectiveness of biased methods in multi-turn RL.

## 7 Reward

Multi-turn environments typically provide sparse feedback upon task completion, creating challenges across extended sequences that can lead to slow convergence or training instability.
However, some environments offer dense reward signals with partial rewards at solution milestones.
We investigate how reward density, the frequency of feedback signals in trajectories, affects multi-turn RL performance and learning efficiency.

### Setup.

We investigate the impact of reward design across two distinct domains: the text-based game TextWorld and the software engineering environment SWE-Gym.
For TextWorld, we manipulate reward density using built-in functions, comparing sparse rewards (task completion only) against dense rewards (intermediate steps).
We evaluate these on the tw-simple tasks22
2
<https://textworld.readthedocs.io/en/stable/textworld.challenges.simple.html> using PPO and RLOO over 3,000 episodes.
For SWE-Gym, we introduce a more complex evaluation of reward source and granularity. We compare verified rewards derived from ground-truth execution (both binary task completion and granular unit test ratios) against model-based rewards synthesized by judges (CodeRM-8B ([Ma et al., 2025](https://arxiv.org/html/2510.01132#bib.bib17)) and GPT-4.1). Given the long horizons of coding tasks, we employ GRPO for stability. 
Full specifications for both environments and reward configurations are detailed in Appendices [B.3](https://arxiv.org/html/2510.01132#A2.SS3 "B.3 Additional task details for § ‣ Appendix B Details of tasks and environments ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning") and [C.3](https://arxiv.org/html/2510.01132#A3.SS3 "C.3 Additional training details for § ‣ Appendix C Details of training and evaluation ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning").

Table 11: Performance across reward density schemes on tw-simple tasks (Qwen-7B). Parentheses show reward density as steps per reward.

| Reward density | Qwen-7B (PPO) | Qwen-7B (RLOO) |
| --- | --- | --- |
| Sparse (10.22) | `0.41_{\uparrow 0.12}` | `0.35_{\uparrow 0.06}` |
| Dense 1 (2.89) | `0.29_{\uparrow 0.0}` | `0.55_{\uparrow 0.26}` |
| Dense 2 (1.17) | `0.58_{\uparrow 0.29}` | `0.55_{\uparrow 0.26}` |

### 7.1 What reward signals are needed for multi-turn RL training?

Dense rewards significantly improve multi-turn RL performance, with optimal density varying by algorithm.
As shown in Table [11](https://arxiv.org/html/2510.01132#S7.T11 "Table 11 ‣ Setup. ‣ 7 Reward ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning"), PPO benefits from more frequent feedback, with success rates jumping from 41% under sparse rewards to 58% with the densest signal (Dense 2).
In contrast, RLOO maintains steady performance (55%) across both dense configurations, suggesting its unbiased gradient estimates are less sensitive to reward density.

The key insight here is that reward density should be calibrated to the optimization strategy. While dense signals can accelerate convergence, their utility depends on the quality of that signal. If intermediate rewards are poorly designed, they risk introducing noise that misguides the agent.

### 7.2 Verified vs. Model-Based Rewards in Complex Tasks

While TextWorld provides a controlled setting for analyzing reward density, real-world applications such as software engineering often involve complex and long-horizon reasoning where defining reward density is more challenging.
To address this, we extend our analysis to the coding domain using SWE-Gym.
We investigate two critical questions: (1) Does the granularity of verified feedback matter? and (2) Can model-based judges substitute for verifiers?

### The Necessity of Fine-Grained Verifier Rewards.

We first compare two implementations of execution-based feedback: a sparse binary verified reward (where the agent receives +1 only upon passing the full test suite) and a dense ratio-based verified reward (proportional to the percentage of unit tests passed).
As is shown in Table [12](https://arxiv.org/html/2510.01132#S7.T12 "Table 12 ‣ Verifiers vs. Model-Based Judges. ‣ 7.2 Verified vs. Model-Based Rewards in Complex Tasks ‣ 7 Reward ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning"), fine-grained verifier rewards are essential for more complex tasks.
With sparse binary rewards, the agent achieves only a 4.2% success rate, which is a negligible improvement over the base model’s 4%.
However, providing dense, ratio-based feedback boosts performance to 22%.
This confirms that in complex domains like software engineering, the “all-or-nothing” signal of a final test suite is too sparse to guide the policy, whereas fine-grained rew for passing individual unit tests provides the necessary gradient for learning.

### Verifiers vs. Model-Based Judges.

We also explore whether model-based rewards can serve as an effective alternative to verifiers. We employ two model-based judges capable of code generation: CodeRM-8B ([Ma et al., 2025](https://arxiv.org/html/2510.01132#bib.bib17)) and GPT-4.1, to generate synthetic test suites and evaluate agent’s code generation progress.
While model-based rewards show some improvement over the base model, they significantly underperform verified rewards.
As shown in Table [12](https://arxiv.org/html/2510.01132#S7.T12 "Table 12 ‣ Verifiers vs. Model-Based Judges. ‣ 7.2 Verified vs. Model-Based Rewards in Complex Tasks ‣ 7 Reward ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning"), rewards shaped by CodeRM-8B and GPT-4.1 achieve success rates of 7.2% and 9.3% respectively.
Although these model-based judges provide some useful signal, they lag behind verified ratio rewards (22%) by a wide margin.
Consequently, for practitioners, the most robust recipe remains relying on execution-based unit tests rather than model-based proxies.

Table 12: Performance of GRPO on SWE-Gym tasks with different reward signals. We compare the base model against verified rewards (binary vs. ratio) and model-based rewards (CodeRM-8B vs. GPT-4.1).

|  |  |  |  |
| --- | --- | --- | --- |
| Metric | Base Model | Verified (Binary) | Verified (Ratio) |
| Success Rate | `0.04` | `0.042_{\uparrow 0.002}` | `0.22_{\uparrow 0.18}` |
| Model-Based Rewards | | Judge (CodeRM-8B) | Judge (GPT-4.1) |
| Success Rate | `0.04` | `0.072_{\uparrow 0.032}` | `0.093_{\uparrow 0.053}` |

## 8 The Recipe and Conclusion

Our systematic investigation across environment, policy, and reward pillars yields a practical recipe for multi-turn agentic RL, validated across TextWorld, ALFWorld, and SWE-Gym.

Environment: Curriculum matters. Start training on simpler environments or tasks with lower verification complexity. We find that agents develop reusable skills (e.g., state tracking) in easier settings that generalize effectively to complex, object-heavy, or long-horizon tasks.

Policy: Prioritize stability and priors. Biased, stabilized algorithms (PPO, GRPO) significantly outperform unbiased estimators (RLOO) and naive gradients (Reinforce++) in multi-turn settings. Furthermore, initializing with a strong SFT prior dramatically reduces RL sample complexity, offering a more efficient path to convergence than pure RL.

Reward: Granularity beats approximation. Dense rewards are essential for complex reasoning. However, our results show that verified execution feedback (e.g., unit test pass rates) is far superior to model-based surrogates. Practitioners should prioritize engineering granular, execution-based signals over training reward models.

By systematically identifying this recipe: Curriculum + Stabilized Policy + Verified Dense Reward, we provide the empirical foundation and practical guidelines for developing truly autonomous agents capable of extended real-world interaction.

## Reproducibility statement

We are committed to ensuring the reproducibility of our experimental results.
To this end, we provide comprehensive details about our experimental setup and will release all necessary resources for replication:

Code and Framework:
We will open-source our complete multi-turn RL framework built on veRL, including environment integrations for TextWorld, ALFWorld, and SWE-Gym.
All training scripts, evaluation pipelines, and data generation procedures will be included in the repository upon publication.

Experimental Details:
Full hyperparameters for all experiments are provided in Appendices, including learning rates, KL penalties, batch sizes, exploration budgets, and temperature settings for each environment and model configuration. We specify exact model versions (Qwen2.5-1.5B-Instruct, Qwen2.5-7B-Instruct, Qwen3-8B), training epochs, and convergence criteria. Task selection procedures, including random seeds for procedural generation in TextWorld and specific task splits for ALFWorld and SWE-Gym, are also documented.

Data and Models:
We detail our data generation process, including the creation of SFT demonstrations from TextWorld gold solutions and the sampling strategy for SWE-Gym tasks. Model weights for key experimental configurations will be released. For environments requiring specific versions, we provide exact package versions and installation instructions.

Computational Requirements:
All experiments were conducted on NVIDIA H100 GPUs.
We report approximate training times and computational resources required for each experimental configuration, enabling researchers to estimate reproduction costs.
The framework supports distributed training for efficient replication at scale.

## References

- Ahmadian et al. (2024)
  A. Ahmadian, C. Cremer, M. Gallé, M. Fadaee, J. Kreutzer, O. Pietquin, A. Üstün, and S. Hooker
  Back to basics: revisiting reinforce style optimization for learning from human feedback in llms.
  External Links: 2402.14740,
  [Link](https://arxiv.org/abs/2402.14740)
  Cited by: [§2](https://arxiv.org/html/2510.01132#S2.p1.1 "2 Related Work ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning"),
  [§4](https://arxiv.org/html/2510.01132#S4.SS0.SSS0.Px2.p1.1 "Training and Evaluation. ‣ 4 Background and Experimental Setup ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning"),
  [§6](https://arxiv.org/html/2510.01132#S6.p1.1 "6 Policy ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning").
- Chollet et al. (2025)
  F. Chollet, M. Knoop, G. Kamradt, and B. Landers
  ARC prize 2024: technical report.
  External Links: 2412.04604,
  [Link](https://arxiv.org/abs/2412.04604)
  Cited by: [§1](https://arxiv.org/html/2510.01132#S1.p1.1 "1 Introduction ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning").
- Côté et al. (2018)
  M. Côté, A. Kádár, X. Yuan, B. Kybartas, T. Barnes, E. Fine, J. Moore, M. Hausknecht, L. El Asri, M. Adada, et al.
  Textworld: a learning environment for text-based games.
  In Workshop on Computer Games,
  pp. 41–75.
  Cited by: [§1](https://arxiv.org/html/2510.01132#S1.p1.1 "1 Introduction ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning"),
  [§3](https://arxiv.org/html/2510.01132#S3.p1.1 "3 Multi-turn Agentic Reinforcement Learning ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning"),
  [§4](https://arxiv.org/html/2510.01132#S4.SS0.SSS0.Px1.p1.1 "Tasks and Environments. ‣ 4 Background and Experimental Setup ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning").
- Dong et al. (2025)
  G. Dong, H. Mao, K. Ma, L. Bao, Y. Chen, Z. Wang, Z. Chen, J. Du, H. Wang, F. Zhang, G. Zhou, Y. Zhu, J. Wen, and Z. Dou
  Agentic reinforced policy optimization.
  External Links: 2507.19849,
  [Link](https://arxiv.org/abs/2507.19849)
  Cited by: [§2](https://arxiv.org/html/2510.01132#S2.p1.1 "2 Related Work ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning").
- Hu et al. (2025)
  J. Hu, J. K. Liu, H. Xu, and W. Shen
  REINFORCE++: stabilizing critic-free policy optimization with global advantage normalization.
  External Links: 2501.03262,
  [Link](https://arxiv.org/abs/2501.03262)
  Cited by: [§6](https://arxiv.org/html/2510.01132#S6.p1.1.4 "6 Policy ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning").
- Ma et al. (2025)
  Z. Ma, X. Zhang, J. Zhang, J. Yu, S. Luo, and J. Tang
  Dynamic scaling of unit tests for code reward modeling.
  External Links: 2501.01054,
  [Link](https://arxiv.org/abs/2501.01054)
  Cited by: [§7](https://arxiv.org/html/2510.01132#S7.SS0.SSS0.Px1.p1.1.4 "Setup. ‣ 7 Reward ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning"),
  [§7.2](https://arxiv.org/html/2510.01132#S7.SS2.SSS0.Px2.p1.1 "Verifiers vs. Model-Based Judges. ‣ 7.2 Verified vs. Model-Based Rewards in Complex Tasks ‣ 7 Reward ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning").
- Oertell et al. (2025)
  O. Oertell, W. Zhan, G. Swamy, Z. S. Wu, K. Brantley, J. Lee, and W. Sun
  Heuristics considered harmful: rl with random rewards should not make llms reason.
  External Links: [Link](https://fuchsia-arch-d8e.notion.site/Heuristics-Considered-Harmful-RL-With-Random-Rewards-Should-Not-Make-LLMs-Reason-21ba29497c4180ca86ffce303f01923d)
  Cited by: [§6.2](https://arxiv.org/html/2510.01132#S6.SS2.p1.1 "6.2 How do RL algorithms impact multi-turn RL training? ‣ 6 Policy ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning"),
  [§6](https://arxiv.org/html/2510.01132#S6.p1.1 "6 Policy ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning").
- Pan et al. (2025)
  J. Pan, X. Wang, G. Neubig, N. Jaitly, H. Ji, A. Suhr, and Y. Zhang
  Training software engineering agents and verifiers with swe‑gym.
  In Proceedings of the 42nd International Conference on Machine Learning (ICML 2025),
  Note: arXiv:2412.21139, accepted at ICML 2025
  External Links: [Link](https://arxiv.org/abs/2412.21139)
  Cited by: [§1](https://arxiv.org/html/2510.01132#S1.p1.1 "1 Introduction ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning"),
  [§4](https://arxiv.org/html/2510.01132#S4.SS0.SSS0.Px1.p1.1 "Tasks and Environments. ‣ 4 Background and Experimental Setup ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning").
- Schulman et al. (2017)
  J. Schulman, F. Wolski, P. Dhariwal, A. Radford, and O. Klimov
  Proximal policy optimization algorithms.
  External Links: 1707.06347,
  [Link](https://arxiv.org/abs/1707.06347)
  Cited by: [§2](https://arxiv.org/html/2510.01132#S2.p1.1 "2 Related Work ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning"),
  [§4](https://arxiv.org/html/2510.01132#S4.SS0.SSS0.Px2.p1.1 "Training and Evaluation. ‣ 4 Background and Experimental Setup ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning"),
  [§6](https://arxiv.org/html/2510.01132#S6.SS0.SSS0.Px2.p1.1 "Multi-turn PPO Formulation. ‣ 6 Policy ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning"),
  [§6](https://arxiv.org/html/2510.01132#S6.p1.1 "6 Policy ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning").
- Shao et al. (2024)
  Z. Shao, P. Wang, Q. Zhu, R. Xu, J. Song, X. Bi, H. Zhang, M. Zhang, Y. K. Li, Y. Wu, and D. Guo
  DeepSeekMath: pushing the limits of mathematical reasoning in open language models.
  External Links: 2402.03300,
  [Link](https://arxiv.org/abs/2402.03300)
  Cited by: [§2](https://arxiv.org/html/2510.01132#S2.p1.1 "2 Related Work ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning"),
  [§4](https://arxiv.org/html/2510.01132#S4.SS0.SSS0.Px2.p1.1 "Training and Evaluation. ‣ 4 Background and Experimental Setup ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning"),
  [§6](https://arxiv.org/html/2510.01132#S6.p1.1 "6 Policy ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning").
- Sheng et al. (2025)
  G. Sheng, C. Zhang, Z. Ye, X. Wu, W. Zhang, R. Zhang, Y. Peng, H. Lin, and C. Wu
  HybridFlow: a flexible and efficient rlhf framework.
  In Proceedings of the Twentieth European Conference on Computer Systems,
  EuroSys ’25, pp. 1279–1297.
  External Links: [Link](http://dx.doi.org/10.1145/3689031.3696075),
  [Document](https://dx.doi.org/10.1145/3689031.3696075)
  Cited by: [§1](https://arxiv.org/html/2510.01132#S1.p4.1 "1 Introduction ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning"),
  [§4](https://arxiv.org/html/2510.01132#S4.SS0.SSS0.Px1.p1.1 "Tasks and Environments. ‣ 4 Background and Experimental Setup ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning").
- Shridhar et al. (2021)
  M. Shridhar, X. Yuan, M. Côté, Y. Bisk, A. Trischler, and M. Hausknecht
  ALFWorld: aligning text and embodied environments for interactive learning.
  External Links: 2010.03768,
  [Link](https://arxiv.org/abs/2010.03768)
  Cited by: [§1](https://arxiv.org/html/2510.01132#S1.p1.1 "1 Introduction ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning"),
  [§4](https://arxiv.org/html/2510.01132#S4.SS0.SSS0.Px1.p1.1 "Tasks and Environments. ‣ 4 Background and Experimental Setup ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning").
- Wang et al. (2025)
  Z. Wang, K. Wang, Q. Wang, P. Zhang, L. Li, Z. Yang, X. Jin, K. Yu, M. N. Nguyen, L. Liu, E. Gottlieb, Y. Lu, K. Cho, J. Wu, L. Fei-Fei, L. Wang, Y. Choi, and M. Li
  RAGEN: understanding self-evolution in llm agents via multi-turn reinforcement learning.
  External Links: 2504.20073,
  [Link](https://arxiv.org/abs/2504.20073)
  Cited by: [§1](https://arxiv.org/html/2510.01132#S1.p1.1 "1 Introduction ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning"),
  [§2](https://arxiv.org/html/2510.01132#S2.p1.1 "2 Related Work ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning").
- Xie et al. (2024)
  T. Xie, D. Zhang, J. Chen, X. Li, S. Zhao, R. Cao, T. J. Hua, Z. Cheng, D. Shin, F. Lei, Y. Liu, Y. Xu, S. Zhou, S. Savarese, C. Xiong, V. Zhong, and T. Yu
  OSWorld: benchmarking multimodal agents for open-ended tasks in real computer environments.
  External Links: 2404.07972,
  [Link](https://arxiv.org/abs/2404.07972)
  Cited by: [§1](https://arxiv.org/html/2510.01132#S1.p1.1 "1 Introduction ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning").
- Yu et al. (2025)
  Q. Yu, Z. Zhang, R. Zhu, Y. Yuan, X. Zuo, Y. Yue, W. Dai, T. Fan, G. Liu, L. Liu, X. Liu, H. Lin, Z. Lin, B. Ma, G. Sheng, Y. Tong, C. Zhang, M. Zhang, W. Zhang, H. Zhu, J. Zhu, J. Chen, J. Chen, C. Wang, H. Yu, Y. Song, X. Wei, H. Zhou, J. Liu, W. Ma, Y. Zhang, L. Yan, M. Qiao, Y. Wu, and M. Wang
  DAPO: an open-source llm reinforcement learning system at scale.
  External Links: 2503.14476,
  [Link](https://arxiv.org/abs/2503.14476)
  Cited by: [§2](https://arxiv.org/html/2510.01132#S2.p1.1 "2 Related Work ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning").
- Zeng et al. (2025)
  S. Zeng, Q. Wei, W. Brown, O. Frunza, Y. Nevmyvaka, and M. Hong
  Reinforcing multi-turn reasoning in llm agents via turn-level credit assignment.
  External Links: 2505.11821,
  [Link](https://arxiv.org/abs/2505.11821)
  Cited by: [§1](https://arxiv.org/html/2510.01132#S1.p1.1 "1 Introduction ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning"),
  [§2](https://arxiv.org/html/2510.01132#S2.p1.1 "2 Related Work ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning").
- Zhou et al. (2025)
  Y. Zhou, S. Jiang, Y. Tian, J. Weston, S. Levine, S. Sukhbaatar, and X. Li
  SWEET-rl: training multi-turn llm agents on collaborative reasoning tasks.
  External Links: 2503.15478,
  [Link](https://arxiv.org/abs/2503.15478)
  Cited by: [§2](https://arxiv.org/html/2510.01132#S2.p1.1 "2 Related Work ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning").

## Appendix A Hyperparameter tuning for multi-turn RL

To establish a robust training recipe for multi-turn RL, we conducted systematic hyperparameter sweeps training Qwen-1.5B on TextWorld w2-o3-q4 tasks using PPO.
Following the setup in §[4](https://arxiv.org/html/2510.01132#S4 "4 Background and Experimental Setup ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning"), we train on 5,000 episodes and evaluate on 100 held-out episodes.
Each experiment runs for 30 epochs (approximately 575 steps) to assess early training stability, measuring task success rate throughout training.

Figure [2](https://arxiv.org/html/2510.01132#A1.F2 "Figure 2 ‣ Appendix A Hyperparameter tuning for multi-turn RL ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning") reveals substantial performance variation across hyperparameter configurations. Higher KL coefficients (`>0.001`) yield more stable training curves. Comparing configurations shows that gamma values below 1.0 impair performance (blue vs. pink curves), while rollout temperature critically affects outcomes—optimal performance occurs between 0.7 and 1.0 (comparing light green, pink, and dark green curves). Higher learning rates for both actor and critic networks improve training efficiency and final performance (brown vs. light green curves).

Table [13](https://arxiv.org/html/2510.01132#A1.T13 "Table 13 ‣ Appendix A Hyperparameter tuning for multi-turn RL ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning") confirms the optimal configuration: KL coefficient of 0.01, temperature of 0.7, actor learning rate of 1e-6, critic learning rate of 1e-5, and gamma of 1.0. These settings provide both training stability and strong final performance, forming the basis for our experiments across all benchmarks.

![Refer to caption](https://arxiv.org/html/2510.01132v2/hp_sweeping.png)

Figure 2: Training curves for Qwen-1.5B on TextWorld w2-o3-q4 with varying hyperparameters. Parameters shown: KL coefficient (kl_coef), rollout temperature (t), actor/critic learning rates, and discount factor (gam).

Table 13: Success rates at epoch 30 on TextWorld w2-o3-q4 test set, sorted by performance. Only top-performing configurations shown; excluded configurations performed substantially worse.

| Ranking | kl_coef | temperature | actor_lr | critic_lr | gamma | win rate |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 0.01 | 0.7 | 1e-6 | 1e-5 | 1.0 | 0.9 |
| 2 | 0.01 | 0.8 | 5e-7 | 5e-6 | 1.0 | 0.86 |
| 3 | 0.01 | 0.7 | 5e-7 | 5e-6 | 1.0 | 0.78 |
| 4 | 0.01 | 1.0 | 5e-7 | 5e-6 | 1.0 | 0.71 |
| 5 | 0.005 | 0.7 | 5e-7 | 5e-6 | 1.0 | 0.66 |
| 6 | 0.01 | 0.7 | 5e-7 | 5e-6 | 0.99 | 0.66 |
| 7 | 0.001 | 1.0 | 5e-7 | 5e-6 | 1.0 | 0.57 |
| 8 | 0.001 | 0.7 | 5e-7 | 5e-6 | 1.0 | 0.43 |

## Appendix B Details of tasks and environments

We show an example of the TextWorld w2-o3-q4 task in Figure [3](https://arxiv.org/html/2510.01132#A2.F3 "Figure 3 ‣ Appendix B Details of tasks and environments ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning"). The ALFWorld tasks are built on TextWorld and they are similar in format, but the tasks in ALFWorld rely more on agents’ embodied understanding. An example from ALFWorld heat & place task is presented in Figure [4](https://arxiv.org/html/2510.01132#A2.F4 "Figure 4 ‣ Appendix B Details of tasks and environments ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning").

We extract SWE-Gym tasks from their huggingface repository (<https://huggingface.co/datasets/SWE-Gym/SWE-Gym>. An example from SWE-Gym getmoto task is presented in Figure [5](https://arxiv.org/html/2510.01132#A2.F5 "Figure 5 ‣ Appendix B Details of tasks and environments ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning").

![Refer to caption](https://arxiv.org/html/2510.01132v2/textworld_example.png)

Figure 3: Textworld w2-o3-q4 task example. The text in gray are the prompts. The bold text is the objective. The text in blue are the observations and the text in orange are the actions.

![Refer to caption](https://arxiv.org/html/2510.01132v2/alfworld_example.png)

Figure 4: ALFWorld heat & place task example. The text in gray are the prompts. The bold text is the objective. The text in blue are the observations and the text in orange are the actions. We only provide part of the task trajectory because it is very long and is similar to the TextWorld example.

![Refer to caption](https://arxiv.org/html/2510.01132v2/swegym_example.png)

Figure 5: SWE-Gym getmoto task example. The text in gray are the prompts. The bold text is the objective. The text in blue are the observations and the text in orange are the actions.

### B.1 Additional task details for §[5](https://arxiv.org/html/2510.01132#S5 "5 Environment ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning")

For environment complexity, we procedurally generated 5000 RL episodes for w2-o3-q4, w8-o3-q4, w2-o12-q4, and w4-o6-q8 respectively using TextWorld’s tw-make, using random seeds ranging from 30001 to 35000.

For task complexity using ALFWorld, we make sure the number of data for each training mixture is the same, which is 1000.
Here is a brief data statistics: (1) single-type tasks contain 1000 pick & place tasks, randomly sampled from 3553 train data; (2) mixed-type (4 types) contain 250 heat, cool, cook, and examine tasks respectively; (3) mixed-type (all types), randomly sampled 1000 any type of tasks from 3553 train data.

For task complexity using SWE-Gym, we make sure the number of data for each training mixture is the same, which is 90.
Here is a brief data statistics: (1) single-type tasks contain 90 getmoto tasks, randomly sampled from the SWE-Gym huggingface repo; (2) mixed-type (5 types) contain 18 getmoto, pydantic, mypy, pandas, and interactive_dvc tasks respectively.

### B.2 Additional task details for §[6](https://arxiv.org/html/2510.01132#S6 "6 Policy ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning")

We collect 0/20/40/60/80/100 SFT data from the gold trajectories from TextWorld games. The seeds range from 40001 to 40101, different from the RL data.

### B.3 Additional task details for §[7](https://arxiv.org/html/2510.01132#S7 "7 Reward ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning")

The tasks are procedurally generated using TextWorld’s built-in tw-simple function, which has a dense reward calculator for each step.
We utilize TextWorld’s built-in reward function to assign rewards per step.
We collect 3000 episodes with sparse, dense 1, and dense 2 density levels, respectively.

## Appendix C Details of training and evaluation

We train Qwen-1.5B, Qwen-7B, and Qwen-8B on 8 NVIDIA H100 GPUs.

For PPO, by default, we use an actor learning rate of 5e-7, a critic learning rate of 5e-6, a clip ratio of 0.2, a discount factor `\gamma` of 1.0, a KL penalty coefficient of 0.001, batch size of 256, and a zero entropy regularization for both Qwen-1.5B and Qwen-7B models.

For GRPO, by default, we use an actor learning rate of 1e-6, KL loss coefficient of 0.001, GRPO sampling number of 4, and batch size of 16 for Qwen3-8B model.

For RLOO, by default, we use an actor learning rate of 1e-6, a KL penalty coefficient of 0.001, and batch size of 256 for both Qwen-1.5B and Qwen-7B models.

For SFT, by default, we use learning rate of 1e-6.

### C.1 Additional training details for §[5](https://arxiv.org/html/2510.01132#S5 "5 Environment ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning")

For TextWorld experiments, we train 150 epochs and evaluate on 100 held-out test sets (with seeds 1 to 100) at epoch 150.

For ALFWorld experiments, given that the base model has zero accuracy on the tasks, we do one epoch of SFT on 300 data, with different seeds from RL data. After the SFT initialization, we train 90 epochs and evaluate on 100 held-out test sets at epoch 90.

For SWE-Gym experiments, we train 15 epochs and evaluate on 25 held-out test sets at epoch 15.

### C.2 Additional training details for §[6](https://arxiv.org/html/2510.01132#S6 "6 Policy ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning")

For SFT, we do exactly one epoch, ensuring there is only one pass on the demonstration data to avoid overfitting.
We train RL on top of the SFT for another 100 epochs.

For RLOO and PPO comparison, we train 150 epochs for each, similar to Appendix [C.1](https://arxiv.org/html/2510.01132#A3.SS1 "C.1 Additional training details for § ‣ Appendix C Details of training and evaluation ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning").

### C.3 Additional training details for §[7](https://arxiv.org/html/2510.01132#S7 "7 Reward ‣ A Practitioner’s Guide to Multi-turn Agentic Reinforcement Learning")

For PPO and RLOO training for dense rewards, we train 150 epochs for each and test on 100 held-out data at epoch 150.

## Appendix D Training curves for PPO versus RLOO policies on TextWorld tasks

![Refer to caption](https://arxiv.org/html/2510.01132v2/iclr2026/images/ppo_vs_rloo_w2.png)

Figure 6: The training reward curve for Qwen-2.5-1.5B model trained using PPO and RLOO on TextWorld w2-o3-q4 tasks.

![Refer to caption](https://arxiv.org/html/2510.01132v2/iclr2026/images/ppo_vs_rloo_w4.png)

Figure 7: The training reward curve for Qwen-2.5-7B model trained using PPO and RLOO on TextWorld w4-o6-q8 tasks.

## Appendix E Use of LLMs

We used large language models (specifically Claude) exclusively for text polishing and grammar checking during the preparation of this manuscript. The LLM was used to improve clarity, fix grammatical errors, and enhance the conciseness of our writing. All experimental design, analysis, interpretations, and scientific conclusions are entirely our own original work. No LLMs were used for generating experimental results, creating figures or tables, or producing any technical content. The core research ideas, methodology, and findings presented in this paper are the product of human authorship.
