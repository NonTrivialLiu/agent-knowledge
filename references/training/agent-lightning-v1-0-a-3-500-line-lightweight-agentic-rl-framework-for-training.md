---
title: "Agent Lightning v1.0: A 3,500-Line Lightweight Agentic RL Framework for Training Agents with Real Harnesses"
url: https://www.microsoft.com/en-us/research/blog/agent-lightning-v1-0-a-3500-line-lightweight-agentic-rl-framework-for-training-agents-with-real-harnesses/
published: 2026-10-07
fetched: 2026-11-11
priority: core
type: engineering-blog
topics: [training, microsoft, harness, multi-agent]
summary: "LLM 代理让部署时实际 Harness 控制训练轨迹，研究重分词、样本合并与训练调度；论文报告Qwen3.5-9B 在约6000样本训练下 SWE-bench Verified 41.8%→56.4%，属于团队实验。"
---

# Agent Lightning v1.0: A 3,500-Line Lightweight Agentic RL Framework for Training Agents with Real Harnesses

Published 
October 7, 2026

By 
[Zhiyuan He](https://www.microsoft.com/en-us/research/people/zhiyuhe/)
,

Research Software Development Engineer II 

[Yuqing Yang](https://www.microsoft.com/en-us/research/people/yuqyang/)
,

Principal Research SDE Manager

Share this page

- [Share on Facebook](https://www.facebook.com/sharer/sharer.php?u=https%3A%2F%2Fwww.microsoft.com%2Fen-us%2Fresearch%2Fblog%2Fagent-lightning-v1-0-a-3500-line-lightweight-agentic-rl-framework-for-training-agents-with-real-harnesses%2F "Share on Facebook")
- [Share on X](https://x.com/intent/tweet?text=Agent%20Lightning%20v1.0%3A%20A%203%2C500-Line%20Lightweight%20Agentic%20RL%20Framework%20for%20Training%20Agents%20with%20Real%20Harnesses&url=https%3A%2F%2Fwww.microsoft.com%2Fen-us%2Fresearch%2Fblog%2Fagent-lightning-v1-0-a-3500-line-lightweight-agentic-rl-framework-for-training-agents-with-real-harnesses%2F "Share on X")
- [Share on LinkedIn](https://www.linkedin.com/shareArticle?mini=true&url=https%3A%2F%2Fwww.microsoft.com%2Fen-us%2Fresearch%2Fblog%2Fagent-lightning-v1-0-a-3500-line-lightweight-agentic-rl-framework-for-training-agents-with-real-harnesses%2F&title=Agent%20Lightning%20v1.0%3A%20A%203%2C500-Line%20Lightweight%20Agentic%20RL%20Framework%20for%20Training%20Agents%20with%20Real%20Harnesses&summary=Agent%20Lightning%20v1.0%3A%20A%203%2C500-Line%20Lightweight%20Agentic%20RL%20Framework%20for%20Training%20Agents%20with%20Real%20Harnesses&source=Microsoft%20Research "Share on LinkedIn")
- [Share on Reddit](
  			http://www.reddit.com/submit?title=Agent%20Lightning%20v1.0%3A%20A%203%2C500-Line%20Lightweight%20Agentic%20RL%20Framework%20for%20Training%20Agents%20with%20Real%20Harnesses&url=https%3A%2F%2Fwww.microsoft.com%2Fen-us%2Fresearch%2Fblog%2Fagent-lightning-v1-0-a-3500-line-lightweight-agentic-rl-framework-for-training-agents-with-real-harnesses%2F			 "Share on Reddit")
- [Subscribe to our RSS feed](https://www.microsoft.com/en-us/research/feed/ "Subscribe to our RSS feed")

![System architecture diagram. On the left, agents with harnesses — mini-SWE-agent, OpenHands, and OpenClaw — run on a Kubernetes cluster. They connect to three components: an API Gateway containing a Rollout API and an LLM API Proxy, a Rollout Controller containing a local reconciler and a Kubernetes reconciler, and a Customized Trainer containing a sample adapter and monitoring. These connect in turn to an inference engine and a training engine holding the model.](https://www.microsoft.com/en-us/research/wp-content/uploads/2026/09/AgentLightning-BlogHeroFeature-1400x788-1.jpg)

## At a glance

- Harnessed Agentic RL: Microsoft Research Asia introduces a training paradigm in which the same agent harness used in deployment participates directly in reinforcement learning, removing the need to reimplement the agent inside the training framework.
- Lightweight by design: Agent Lightning v1.0 delivers a complete agent RL control plane in roughly 3,500 lines of code.
- Native Kubernetes support: agents run as standard Kubernetes jobs on self-managed clusters, cloud Kubernetes, or local infrastructure, with no dependency on paid commercial sandbox services.
- Data-efficient training recipe: an end-to-end coding agent pipeline raised Qwen3.5-9B from 41.8% to 56.4% Pass@1 on SWE-bench Verified, a 14.6 percentage point gain, using only about 6,000 training samples based on open sourced dataset.

AI agents have evolved from single models to complex full-stack systems built from models, tools, and execution environments. Their capabilities increasingly depend on the agent harness that coordinates them from outside the model. Reinforcement learning (RL) is an approach where AI systems learn through trial and error, guided by rewards and penalties for their actions. RL can make those agents better, but most agent RL systems require developers to reimplement the agent inside the training framework. That is costly, and it means the agent being trained is not quite the agent that gets deployed.

To address this, researchers at Microsoft Research Asia have introduced the Harnessed Agentic RL training paradigm and open-sourced a fully rebuilt [Agent Lightning v1.0 (opens in new tab)](https://github.com/microsoft/agent-lightning). Compared with the original, Agent Lightning, v1.0 puts more emphasis on staying lightweight, on integrating with real harnesses, and on a complete, reproducible agent RL training pipeline.

Agent Lightning v1.0 was rebuilt around Harnessed Agentic RL, with key improvements:

- **Lightweight**: the entire framework is about 3,500 lines of code. Agent Lightning v1.0 implements a complete Harnessed Agentic RL system in a codebase that is small and clear enough to understand, modify, and extend.
- **Training on a real agent harness**: agents reach the model through the large language model (LLM) proxy in Agent Lightning v1.0, leaving existing harness code unchanged.
- **Native Kubernetes support**: agents run directly as Kubernetes jobs, without external commercial sandbox services. Self-managed clusters and local infrastructure alike can support rollouts at scale.
- **A complete coding agent training example**: an end-to-end pipeline built on Qwen3.5-9B raised Pass@1 on SWE-bench Verified from 41.8% to 56.4%, an absolute gain of 14.6 percentage points, using only about 6,000 training samples.

## The limits of traditional agentic RL

Traditional agentic RL assumes the training framework owns the interaction loop with the environment. In a ReAct-style loop, the model generates an action, the environment returns an observation, the observation is appended to the context, and the model generates the next action, so the whole rollout maps onto one continuous token trajectory. Early RL systems such as verl, AReaL, and slime were built this way, which meant training an agent required rebuilding its loop inside the RL framework.

Real harnesses have outgrown that assumption. Coding agents such as mini-SWE-agent, OpenHands, OpenCode, Claude Code, and Codex each bring their own context management, tool protocols, execution logic, and dependencies, as do general-purpose agent systems. Rebuilding one for training is expensive, and the rebuilt agent may no longer behave in the same way as the deployed agent.

Agent Lightning takes a different route. It places an LLM proxy between the agent and the model. The agent continues to run as before: simply point the endpoint that previously called the model API at Agent Lightning, and the training framework can observe and record its model calls. In v1.0, the researchers go further and formally define this paradigm as Harnessed Agentic RL: whichever agent harness is used in deployment is the harness that takes part directly in reinforcement learning during training (Figure 1).

![Figure 1: Side-by-side comparison of two training loops. In Agentic RL, the environment exchanges actions and observations with a tokenizer, which passes action and observation tokens to the policy model. In Harnessed Agentic RL, an agent harness handling context and orchestration sits between the environment and an OpenAI-like API, which exchanges input and output tokens with the policy model.](https://www.microsoft.com/en-us/research/wp-content/uploads/2026/09/AgentLightning-blog_EXT_FA_figure.1.jpg)

Figure 1. Traditional agentic RL compared with Harnessed Agentic RL. In traditional agentic RL, the training framework manages the environment and the agent loop. In Harnessed Agentic RL, the harness manages both.

## Four challenges in training with real harnesses

A core difference between Harnessed Agentic RL and traditional agentic RL is that the environment interaction loop is handled by the agent harness rather than the training framework. The training system can only observe a series of LLM request and response pairs, so a single rollout may be split into a variable number of training samples. This brings four key challenges:

- **Retokenization and sample merging**: Harnesses keep context as text, but RL training needs the token IDs sampled during the rollout. Passing text through the chat template and tokenizer again can shift token boundaries, so adjacent calls cannot always be merged into one sample.
- **Advantage calculation**: Retokenization, subagents and context summarization can split one rollout into several samples. Computing baselines and advantages directly at the sample level causes rollouts that produce more samples to be counted repeatedly, which alters the original statistical relationships at the rollout level.
- **Loss normalization**: Averaging loss by sample count gives more weight to rollouts that produce more samples. Since sample count is often just a product of harness behavior, loss normalization must also avoid being distorted by it.
- **Training backend scheduling**: Sample count and length are known only after the harness finishes, while GPU counts and data/tensor parallel configurations are usually fixed. The backend has to map a variable workload into fixed resources.

Spotlight: Event Series

[![Research Forum | abstract background with colorful hexagons](https://www.microsoft.com/en-us/research/wp-content/uploads/2025/05/Research-Forum-hero_1400x788.jpg)](https://www.microsoft.com/en-us/research/event/microsoft-research-forum/past-episodes/?OCID=msr_researchforum_MCR_Blog_Promo)

## Microsoft Research Forum

Join us for a continuous exchange of ideas about research in the era of general AI. Watch the latest episodes on demand.

[Watch on-demand](https://www.microsoft.com/en-us/research/event/microsoft-research-forum/past-episodes/?OCID=msr_researchforum_MCR_Blog_Promo)

Opens in a new tab

## Building a complete agent RL control plane in 3,500 lines of code

In system design, Agent Lightning v1.0 treats simplicity as its first principle. The entire framework is about 3,500 lines of code, with three core components: the API Gateway, the Rollout Controller, and the Customized Trainer (Figure 2).

The API gateway stores rollouts, models, and events, and serves as an OpenAI-compatible LLM proxy. It links every model call from the harness to its rollout and records the prompts, responses, and log probabilities that training needs. The rollout controller starts and manages agent execution, either as local processes or as standard Kubernetes jobs, keeping agent execution separate from the trainer. The customized trainer, built on verl, creates rollouts, waits for them to finish, collects samples, and assembles the final training samples through a sample adapter. As a result, for an existing agent harness, simply pointing the model endpoint at the Agent Lightning proxy is usually enough to connect quickly to RL training.

![Figure 2: System architecture diagram. On the left, agents with harnesses — mini-SWE-agent, OpenHands, and OpenClaw — run on a Kubernetes cluster. They connect to three components: an API Gateway containing a Rollout API and an LLM API Proxy, a Rollout Controller containing a local reconciler and a Kubernetes reconciler, and a Customized Trainer containing a sample adapter and monitoring. These connect in turn to an inference engine and a training engine holding the model.](https://www.microsoft.com/en-us/research/wp-content/uploads/2026/09/AgentLightning-blog_EXT_FA_figure.2.png)

Figure 2. The Agent Lightning v1.0 system architecture showing the API gateway, rollout controller, and customized trainer.

## Collocated async RL

Rollout times vary widely across agents. Synchronous RL waits for the slowest agent in a batch and leaves GPUs idle, while fully asynchronous RL raises utilization but needs separate GPU pools for rollout and training. In response, Agent Lightning v1.0 introduces Collocated Async RL, which lets rollout and model updates share the same set of GPUs.

Once the system has collected enough rollouts, the update begins: the API Gateway pauses accepting new requests and waits for requests already in progress to finish, and rollout resumes after the update completes. The entire state transition is transparent to the external agent harness. In experiments, this approach achieved about a 2x end-to-end speedup over synchronous RL while using fewer GPUs than conventional asynchronous RL (Figure 3).

![Figure 3: Three GPU scheduling timelines. Synchronous RL uses four GPUs at low efficiency, with long idle gaps before a single update block. Collocated Async RL uses the same four GPUs at high efficiency, interleaving full and partial rollouts with update blocks. Asynchronous RL reaches high efficiency but requires eight GPUs. Bars are colored for full rollout, partial rollout, and update.](https://www.microsoft.com/en-us/research/wp-content/uploads/2026/09/AgentLightning-blog_EXT_FA_figure.3.jpg)

Figure 3. Synchronous RL, asynchronous RL, and Collocated Async RL compared. Collocated Async RL raises utilization while occupying fewer GPUs.

## Running agents on Kubernetes

Collecting enough rollouts means running many agents at once, which consumes substantial CPU, memory, and compute resources. Other Harnessed Agentic RL frameworks often host those agents on commercial sandbox services such as Modal Sandbox or E2B, where cost climbs quickly with scale. Instead, Agent Lightning v1.0 runs them as standard Kubernetes jobs, reusing existing self-managed clusters, cloud Kubernetes, or local infrastructure (Figure 4). Existing compute resources are used more efficiently, large rollouts cost less, and the whole pipeline stays open source and reproducible.

![Figure 4: Flow diagram. An API Gateway holds three rollouts, two queueing and one running. The Rollout Controller polls the gateway and uses a Kubernetes reconciler to create jobs on a Kubernetes cluster, and a local reconciler to watch and list local processes. Status updates flow back to the gateway.](https://www.microsoft.com/en-us/research/wp-content/uploads/2026/09/AgentLightning-blog_EXT_FA_figure.4.jpg)

Figure 4. The Rollout Controller in Agent Lightning v1.0 provides native Kubernetes support, running agents directly as standard Kubernetes jobs.

## 6,000 training samples, a 14.6-point performance gain

To test the approach, researchers built a full pipeline on SWE-smith, mini-SWE-agent, and Qwen3.5-9B, covering data cleaning, environment construction, reward-hacking safeguards, and RL training. The training set holds about 6,000 samples and needs no large-scale compute. RL training alone raised Qwen3.5-9B from 41.8% to 56.4% on SWE-bench Verified, a gain of 14.6 percentage points.

The coding agent experiments further confirm the earlier analysis of two challenges: advantage calculation and loss normalization. Compared with sample-level handling, rollout-level advantage combined with rollout-level normalization achieves a higher validation reward and keeps policy entropy more stable during training (Figure 5).

![Figure 5: Two line charts plotting 200 training steps. On the left, validation reward: rollout-level advantage combined with rollout-level normalization reaches the highest reward at about 0.37, above rollout-level advantage alone and sample-level advantage. On the right, policy entropy: rollout-level advantage alone climbs steeply to about 0.65, while the combined method stays lower and steadier.](https://www.microsoft.com/en-us/research/wp-content/uploads/2026/09/AgentLightning-blog_EXT_FA_figure.5.jpg)

Figure 5. Pass rate and policy entropy for Qwen3.5-9B on the SWE-smith validation set.

[Technical report](https://www.microsoft.com/en-us/research/publication/agent-lightning-v1-0-towards-harnessed-agentic-rl/)

[GitHub project](https://github.com/microsoft/agent-lightning)

Opens in a new tab

## Related publications

### [Agent Lightning v1.0: Towards Harnessed Agentic RL](https://www.microsoft.com/en-us/research/publication/agent-lightning-v1-0-towards-harnessed-agentic-rl/)

## Meet the authors

![Portrait of Zhiyuan He](https://www.microsoft.com/en-us/research/wp-content/uploads/2022/05/Screenshot-2022-05-31-155131.png)

### Zhiyuan He

Research Software Development Engineer II

[Learn more](https://www.microsoft.com/en-us/research/people/zhiyuhe/)

![Portrait of Yuqing Yang](https://www.microsoft.com/en-us/research/wp-content/uploads/2025/03/181A0688_11-180x180.jpg)

### Yuqing Yang

Principal Research SDE Manager

[Learn more](https://www.microsoft.com/en-us/research/people/yuqyang/)

## Research Areas

- [![](https://www.microsoft.com/en-us/research/wp-content/uploads/2020/07/msr-ai-2x.png) Artificial intelligence](https://www.microsoft.com/en-us/research/research-area/artificial-intelligence?lang=fr-ca/)
- [![](https://www.microsoft.com/en-us/research/wp-content/uploads/2020/07/msr-systems-2x.png) Systems and networking](https://www.microsoft.com/en-us/research/research-area/systems-and-networking/)

## Research Groups

- [Microsoft Research Asia - Shanghai](https://www.microsoft.com/en-us/research/group/msr-asia-shanghai/)
- [MSRA (Shanghai) System and Engineering Group](https://www.microsoft.com/en-us/research/group/sh-sys-eng-group/)

## Related labs

- [Microsoft Research Asia](https://www.microsoft.com/en-us/research/lab/microsoft-research-asia/)
