---
title: "Harness adapters: Safe RL for efficient agentic development"
url: https://huggingface.co/blog/harness-hub/harness-adapters
published: 2026-11-06
fetched: 2026-11-11
priority: core
type: engineering-blog
topics: [training, huggingface, harness]
summary: "每个模型与实际 Harness 对应一个 LoRA；直接在未修改的 pi、OpenCode、Hermes 内使用可验证任务做 RL，安全代理检查工具调用；实验仍是 smoke tests。"
---

# Harness adapters: Safe RL for efficient agentic development

[Back to Articles](https://huggingface.co/blog)

[Community Article](https://huggingface.co/blog/community)

Published
November 6, 2026

[Upvote

46](https://huggingface.co/login?next=%2Fblog%2Fharness-hub%2Fharness-adapters)  

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1648631057413-noauth.png)](https://huggingface.co/ybelkada "ybelkada")
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/608aabf24955d2bfc3cd99c6/-YxmtpzEmf3NKOTktODRP.jpeg)](https://huggingface.co/ariG23498 "ariG23498")
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1678663263366-63e0eea7af523c37e5a77966.jpeg)](https://huggingface.co/SaylorTwift "SaylorTwift")
- [![](https://huggingface.co/avatars/fd5487822c0c223732070dd3e9aedf25.svg)](https://huggingface.co/evalstate "evalstate")
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/63a369d98c0c89dcae3b8329/AiH2zjy1cnt9OADAAZMLD.jpeg)](https://huggingface.co/AdinaY "AdinaY")
- [![](https://huggingface.co/avatars/2299442868e076ba2db8e4badd12b8af.svg)](https://huggingface.co/Tastler "Tastler")

[![Younes B's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/1648631057413-noauth.png)](https://huggingface.co/ybelkada) 

[Younes B

ybelkada](https://huggingface.co/ybelkada)

[![harness-hub's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/62441d1d9fdefb55a0b7d12c/3hnC9tP4j8BlGQVXabNG4.png)](https://huggingface.co/harness-hub "harness-hub") [harness-hub](https://huggingface.co/harness-hub)

[![Lysandre's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/5e3aec01f55e2b62848a5217/PMKS0NNB4MJQlTSFzh918.jpeg)](https://huggingface.co/lysandre) 

[Lysandre

lysandre](https://huggingface.co/lysandre)

[![harness-hub's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/62441d1d9fdefb55a0b7d12c/3hnC9tP4j8BlGQVXabNG4.png)](https://huggingface.co/harness-hub "harness-hub") [harness-hub](https://huggingface.co/harness-hub)

[![Nathan Habib's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/1678663263366-63e0eea7af523c37e5a77966.jpeg)](https://huggingface.co/SaylorTwift) 

[Nathan Habib

SaylorTwift](https://huggingface.co/SaylorTwift)

[![harness-hub's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/62441d1d9fdefb55a0b7d12c/3hnC9tP4j8BlGQVXabNG4.png)](https://huggingface.co/harness-hub "harness-hub") [harness-hub](https://huggingface.co/harness-hub)

 

Small LoRA adapters, trained with reinforcement learning inside pi, opencode and hermes, all served from one model, with every tool call the model makes inspected by [safeagents](https://github.com/huggingface/safeagents) before it runs. Follow the training runs on the [live dashboard](https://harness-hub-harness-adapters-rl.hf.space/).

## In short

- We release several "harness adapters". It is one LoRA adapter per model and harness, trained with RL on verifiable tasks, inside unmodified agent harnesses (pi, opencode and hermes).
- Harness adapters can make local agentic development more efficient and accurate. On held-out eval tasks, in our smoke training tests, they make fewer tool calls than the base model, while keeping or improving its accuracy.
- New environments come from open coding sessions shared on the Hub: [Repo2RLEnvs](https://github.com/huggingface/Repo2RLEnv) turns them into verifiable tasks, mixed in training with [SmolDataEnvs](https://huggingface.co/datasets/FineEnvs/SmolDataEnvs-harbor-train).
- [safeagents](https://github.com/huggingface/safeagents), a proxy between the harness and the model, checks every tool call with rule-based detectors. Reward-hacking attempts are blocked and score 0.
- [TwIL-8B](https://huggingface.co/webAI-Official/TwIL-8B), a reasoning model never trained as an agent, learns too. The final runs are [streamed live](https://harness-hub-harness-adapters-rl.hf.space/).

## Evolving harness adapters

The same model behaves differently in different agent harnesses, where each one has its own tools, prompt and control flow. [The ultimate guide to multi-harness RL](https://huggingface.co/spaces/FineEnvs/multi-harness-rl) showed how to train a model inside the harnesses themselves, without modifying them.

Here, we take a different approach, we train a small LoRA adapter per harness, on top of a base model. People can then swap the model behind their local agent for the adapter trained in that agent.

### Early attempts

We first released [initial harness adapters](https://huggingface.co/collections/harness-hub/lfm25-24b-harness-adapters) for [LFM2.5-24B-A2B](https://huggingface.co/LiquidAI/LFM2.5-24B-A2B) only, trained under pi, hermes and claude-code. They gave positive signals, both in tool-calling efficiency and in accuracy on held-out tasks, and given their adoption by the community, we decided to push further in this direction and add new components to the RL training, to make our initial work more complete.

### LoRA is the natural candidate for harness adapters

LoRA adapters are cost-efficient for training and evaluation, since one server can host every harness's policy at once. At inference, anyone can load the adapter for the harness of their choice, to make the base model more efficient on their use case. We detail in [One base model, many adapters](https://huggingface.co/blog/harness-hub/harness-adapters#one-base-model-many-adapters) how exactly we leverage LoRA adapters for training and evaluation.

### Diversifying RL tasks

We increased the diversity and difficulty of our previous RL tasks by generating synthetic RL environments, with open-source agent trajectories (a *trajectory* being the full logs of an agent session: the user requests, the model replies and every tool call with its output) as seed data. We derived four types of RL environments:

1. `repair`: fix a bug in an existing codebase.
2. `qa`: answer a factual question.
3. `build`: build something new from scratch, graded by the fraction of hidden tests that pass. The original implementation serves as the oracle that validates the task.
4. `extend`: follow-up changes to an existing codebase.

This animated demo shows what each type of task looks like:

How these environments are built, checked and scored is in [Environments](https://huggingface.co/blog/harness-hub/harness-adapters#environments).

### Safe RL: mitigate reward hacking with safeagents

RL also lets the model hack the reward, taking shortcuts on the task it's trying to solve. So we plug [`safeagents`](https://github.com/huggingface/safeagents) into the RL training stage. It inspects the model's tool calls and blocks the ones that are clearly attempts at reward hacking. A blocked call is replaced by a text explaining why it was blocked, which invites the model to explore a different path. How the checks work, and a call they blocked, is in [Saying 🙅 to agent shortcuts](https://huggingface.co/blog/harness-hub/harness-adapters#saying-%F0%9F%99%85-to-agent-shortcuts).

### Train on more models

After feedback from the community, we extended the set of models we train to LFM2.5-24B-A2B and [LFM3-1.7B](https://huggingface.co/LiquidAI/LFM3-1.7B), plus [TwIL-8B](https://huggingface.co/webAI-Official/TwIL-8B) as an experiment. The model card states it was not trained on agentic data, and we want to know whether such a model gives positive signals and can produce harness adapters too. The models and their settings are in [Trained models](https://huggingface.co/blog/harness-hub/harness-adapters#trained-models).

## Setup

### Trained models

| model | what it is | role |
| --- | --- | --- |
| 🧩 [LiquidAI/LFM2.5-24B-A2B](https://huggingface.co/LiquidAI/LFM2.5-24B-A2B) | mixture of experts, 2B active parameters | main run |
| 🪶 [LiquidAI/LFM3-1.7B](https://huggingface.co/LiquidAI/LFM3-1.7B) | small hybrid model with short convolutions | main run |
| 🧠 [webAI-Official/TwIL-8B](https://huggingface.co/webAI-Official/TwIL-8B) | dense 8.8B reasoning model, from Granite 4.2 | experiment |

### Training codebase and main hyperparameters

We train our models with the GRPO algorithm, using TRL's [`AsyncGRPOTrainer`](https://huggingface.co/docs/trl/en/async_grpo_trainer) together with tree attention for efficient training. Our harness adapters are LoRA adapters with rank 32, attached on every linear layer (`all-linear`). The models perform 8 rollouts per task, and we use a learning rate of 1e-5 for all our trainings.

Each run mixes [SmolDataEnvs](https://huggingface.co/datasets/FineEnvs/SmolDataEnvs-harbor-train) tasks, weighted toward medium and hard ones, with 230 of the 270 Repo2RLEnvs tasks. The other 40 Repo2RLEnvs tasks, and 150 [SmolDataEnvs](https://huggingface.co/datasets/FineEnvs/SmolDataEnvs-harbor-train) tasks, are held out for evaluation and never trained on.

| model | steps | SmolDataEnvs | Repo2RLEnvs | tasks | agent steps |
| --- | --- | --- | --- | --- | --- |
| LFM2.5-24B-A2B | 200 | 100 medium + 200 hard | 230 | 530 | 17 |
| LFM3-1.7B | 400 | 300 medium + 250 hard | 230 | 780 | 17 |
| TwIL-8B (experiment) | 300 | 150 medium + 250 hard | 230 | 630 | 30 |

Some shared parameters are the following: sampling temperature 0.8, up to 32,768 output tokens per turn, rollouts at most 4 weight updates stale, 4 gradient-accumulation steps, and a checkpoint every 10 steps, each one evaluated. TwIL gets 30 agent steps per session and 20 minutes timeout as it needs more steps to tasks (since not trained on agentic data).

- Reward: the task's own verifier, plus a small bonus for solving with fewer tool calls, 0.1 × (1 − calls / 15), only on correct rollouts. We picked the weight in an ablation.
- Thinking mode: we leave thinking mode for all our models, in training and in evaluation. Reasoning from earlier turns stays in the context.
- Harnesses run unmodified, in their own sandbox per rollout, through OpenEnv's Harbor integration. Their model requests go to the trainer's vLLM, and training uses exactly the tokens the harness saw, with no re-tokenisation.

### Infrastructure

We train on [HF Jobs](https://huggingface.co/docs/huggingface_hub/guides/jobs): 2×H200 for LFM3-1.7B, and 4×H200 for the other runs. The total cost of each training run is shown on the [live dashboard](https://harness-hub-harness-adapters-rl.hf.space/) of the training jobs.

## One base model, many adapters

Adapters pay off in two places, both shown below: switch between the training and evaluation modes. The sections below break each one down.

### Training

Each model is served by one vLLM. Its three trainers, one per harness, all send rollouts to it, each request naming its own adapter, so the base weights are loaded once for all three. After a gradient step, the trainer loads its new adapter into vLLM by name, next to the current one. Requests already running on the old version finish on it, so nothing pauses.

For LFM3-1.7B, the three trainers even share one GPU: an agent rollout spends most of its time in the sandbox, not generating, so the trainers mostly wait. In earlier runs a trainer spent about 35 s per step in forward and backward passes, against several minutes waiting for rollouts. Three of them take turns instead of idling on their own.

### What goes into one training step

Training is asynchronous, where the rollouts and gradient steps don't wait for each other. Each trainer keeps up to 48 agent sessions running at once, about 6 tasks with 8 rollouts each (12 sessions for TwIL-8B, whose long reasoning fills vLLM's memory sooner). A task joins the training queue once all 8 of its rollouts are scored, since GRPO compares them with each other.

A gradient step packs finished rollouts into 4 micro-batches, each up to a token budget: 131,072 tokens for LFM2.5-24B-A2B, 65,536 for LFM3-1.7B and TwIL-8B. So the number of tasks per step isn't fixed: short sessions fit many, long ones few. Our earlier LFM2.5-24B-A2B runs trained on about 8 tasks (64 rollouts) per step, TwIL-8B's smoke run on about one. After the step, the new adapter version is loaded into vLLM, and rollouts started more than 4 versions earlier are dropped, so the model never learns from a policy too far behind it.

The dashboard logs both numbers for every run: `batch/groups_per_step` (tasks) and `batch/samples_per_step` (rollouts). They also set how often a task comes back: at 8 tasks per step, LFM2.5-24B-A2B's 200 steps go over its 530 tasks about 3 times.

### Evaluation

The same trick evaluates every checkpoint at once. One vLLM loads the base weights, then each checkpoint as an adapter, with one sandbox server per checkpoint running its held-out tasks in parallel. Nine checkpoints of LFM2.5-24B-A2B, 1,350 agent sessions in all, ran in a single H200 job in under an hour, for about $5 of GPU time. Merging each checkpoint into full weights and serving them one by one would have cost about $90. And a score measures the adapter exactly as it was trained (nothing is merged or converted).

## Environments

- [SmolDataEnvs](https://huggingface.co/datasets/FineEnvs/SmolDataEnvs-harbor-train): data-analysis questions from public Kaggle notebooks. The agent gets the data files in its sandbox and writes one answer, graded by exact or numeric match. It's the dataset used in [the ultimate guide to multi-harness RL](https://huggingface.co/spaces/FineEnvs/multi-harness-rl).
- Repo2RLEnvs: tasks rebuilt from open agent trajectories that people published on the Hub. A trajectory becomes a task when it contains a verifiable unit of work: a `repair`, a `build`, an `extend` or a `qa`.

### How we enhanced the mix with RL environments built from open-source agent trajectories

The raw material is agent sessions that people published on the Hugging Face Hub, from pi, Claude Code, Codex and other harnesses. They are converted to ATIF trajectories, then each one goes through the same six steps. A candidate that fails any of them is dropped, with its reason recorded.

1. Screen: [atif-scan](https://github.com/huggingface/atif-scan) drops trajectories with reward tampering or benchmark leakage.
2. Replay: every file write and edit is applied to a virtual filesystem, so each shell command comes with the files as they were just before it ran.
3. Find work: each family looks for its unit of work: a check that failed, then passed after edits (`repair`); a Python project finished from the first request (`build`); a later change whose checks pass (`extend`); a fact computed from public Hub data (`qa`). This is the only step that uses an LLM: for `build` and `extend` tasks, a teacher model, [Mistral-Large-4-1T-A52B](https://huggingface.co/mistralai/Mistral-Large-4-1T-A52B), writes the interface contract, a stub and the hidden tests (for `qa`, it would propose the questions). `repair` tasks need no LLM: their check comes from the trajectory itself. In this release, 259 of the 270 tasks carry teacher-written tests.
4. Build and check: the environment is built as a Docker image and checked offline, with no LLM in the loop, so the teacher's tests are never trusted unchecked. A `repair` must fail the way the trajectory recorded; `build` tests must pass on the reference, fail on a stub and an empty workspace, and catch most injected bugs (mutation testing).
5. Trial matrix: the original solution must score full reward, twice, while doing nothing, a stub, or tampering with the tests must score 0.
6. Publish and score: the image is pushed and pinned by digest in `task.toml`, after the oracle is run in it again. Then LFM2.5-24B-A2B, the largest model we train, attempts each task several times as the reference agent (under terminus-2), and its solve rate sets the difficulty label: hard below 0.3, medium up to 0.6, easy above.

### How the task type is decided

Let's now dive into how the task type (`repair`, `qa`, `build`, `extend`) is decided. No LLM is involved in this stage: the replayed trajectory already records every command the agent ran, its exit code and the files before it, plus where each user request starts. Each type is a simple rule over those facts, so the same trajectory always yields the same candidates:

- `repair`: a check (`pytest`, `npm test`, `tsc`…) exits non-zero, then the same command exits 0 after edits, with no new install in between and the tests themselves untouched.
- `build`: by the second request, there are at least two Python files and the last Python check passed.
- `extend`: a later request changes the source of an existing Python project, and its checks end passing.

The LLM only comes in afterwards, where understanding is needed: writing the contract and tests for a candidate that's already typed.

### Where the oracle comes from

Every task ships an oracle: a reference solution, in `solution/`, that must score full reward in the task's own image, or the task is dropped. In almost every case, the oracle is not written by the LLM: it's the original agent's own work, taken from the trajectory, where it really happened and passed its checks.

| task type | oracle | tests |
| --- | --- | --- |
| `repair` | the agent's fix: the changed files when the check passed | the trajectory's own failing check, no LLM |
| `build` | the project as the agent finished it, at the end of the first request | hidden tests written by the teacher LLM |
| `extend` | the agent's later change to the project | hidden tests for that change, written by the teacher LLM |
| `qa` | a script proposed by the LLM, whose answer must appear verbatim in a tool output the agent saw | exact or numeric match |

So the teacher LLM writes the exam, and the trajectory provides the answer key it's checked against. For `build` and `extend`, a test is kept only if it passes on the oracle twice and fails on a stub (the same interface with no behaviour) and on an empty workspace, and the kept tests must catch most deliberately injected bugs. A wrong test fails on the oracle and is dropped; a test too weak to tell real code from a stub is dropped too.

### Inspect a few tasks

Pick a task and a file to read it as the agent and the verifier see it. These five come from [harness-hub/traj2envs-rl](https://huggingface.co/datasets/harness-hub/traj2envs-rl), one per task type and difficulty level in the release.

### A distribution skewed toward build tasks

The release is far from balanced: 253 of its 270 tasks are `build` tasks (94%), against 11 `repair`, 6 `extend` and no `qa`. We still describe `qa` to share the full environment generation recipe, and we plan to include more of these tasks in future releases. 243 of the 270 come from one source, TeichAI/Ox-Alpha-Pi-Traces, and 238 of those are `build`. The skew comes from what shared trajectories contain, and from how strict each task type is:

- Most shared sessions are one-shot "build X" requests: a session that finishes a Python project from its first request is exactly what `build` looks for, so the largest trace datasets mostly yield `build` tasks.
- `repair` needs a rare pattern: a check that failed, then passed after edits, without a new install in between, and that fails the same way again once the project is rebuilt in a clean image. Few sessions record that, and fewer still reproduce it.
- `extend` needs a second request that changes a finished Python project and ends with its checks passing. Multi-request sessions are the exception in these datasets.
- `qa` needs a fact computed from public Hub data, quoted verbatim in a tool output. Coding sessions rarely contain one, and none passed in this release.

The difficulty labels lean the same way: 179 tasks are easy for LFM2.5-24B-A2B, 61 medium and 30 hard. That's why each run's mix weights [SmolDataEnvs](https://huggingface.co/datasets/FineEnvs/SmolDataEnvs-harbor-train) toward medium and hard tasks, and why we'd like more `repair` and `extend` tasks: they need sessions where something goes wrong and gets fixed, or where a project grows over several requests. Sharing such sessions, scrubbed with safeagents, is the most useful contribution.

Each task records how often a reference agent solves it, and the training mix favours tasks that are solved sometimes but not always: GRPO only learns from groups where some rollouts pass and others fail. Repo2RLEnvs is moving to [Repo2RLEnv](https://github.com/huggingface/Repo2RLEnv), and its repository will be archived.

| trajectory dataset | candidate environments |
| --- | --- |
| [TeichAI/Ox-Alpha-Pi-Traces](https://huggingface.co/datasets/TeichAI/Ox-Alpha-Pi-Traces) | 1,524 |
| [TeichAI/DeepSeek-v4-Pro-Agent](https://huggingface.co/datasets/TeichAI/DeepSeek-v4-Pro-Agent) | 143 |
| [choucsan/mimo-claude-code-traces-1k](https://huggingface.co/datasets/choucsan/mimo-claude-code-traces-1k) | 129 |
| [MaxDevv/real-pi-coding-agent-traces-sessions](https://huggingface.co/datasets/MaxDevv/real-pi-coding-agent-traces-sessions) | 42 |
| codex300, from the [SaylorTwift/agent-traces-analysis](https://huggingface.co/buckets/SaylorTwift/agent-traces-analysis) bucket | 41 |
| 11 more datasets: GLM, Kimi, MiniMax, Claude, pi and Codex sessions | 71 |
| total | 1,950 |

## Saying 🙅 to agent shortcuts

RL finds shortcuts: a policy rewarded for passing tests will, sooner or later, try to read the tests, rewrite them, or fetch the answer from wherever the task came from. So every tool call goes through [safeagents](https://github.com/huggingface/safeagents) before the harness runs it.

safeagents is a reverse proxy: a small server placed in front of another one, that clients talk to as if it were the real thing. The harness's base URL points at safeagents instead of vLLM. Each request goes through unchanged; each response comes back through it, and the tool calls in it are checked before the harness sees them. Neither the harness nor vLLM knows it's there, and it speaks both the OpenAI Chat Completions and the Anthropic Messages APIs, streaming or not. In training, it runs on a background thread of the trainer.

### Rule-based checks

Every check is a rule, not a model: the same call always gets the same verdict, in about 10 to 20 ms, and the policy can't talk its way past it. Each tool call goes through three stages, in order:

1. The request itself: the call must use a tool the request declared, and any host it reaches must appear somewhere in the conversation. The model's own earlier turns don't count, so it can't make up a URL and then cite itself.
2. atif-scan's detectors: the conversation so far is turned into an ATIF trace and scanned by [atif-scan](https://github.com/huggingface/atif-scan), the same scanner that screens trajectories for Repo2RLEnvs. Its built-in rules cover reward tampering, test editing, benchmark lookups, proxy bypass and more. A finding of high severity or above blocks the call; milder ones are logged as suspicious, and the call runs.
3. An optional judge: a model can review the calls atif-scan found suspicious. It sees the user's request, the call and the findings, never the agent's reasoning, and it can only add blocks, never lift one. We leave it off and don't explore this direction here.

A blocked call is replaced, in the response, by a text notice: `` [safeagents] blocked call to `bash`: … ``, and a "tool use" stop becomes a plain stop. Nothing runs. The reward function gives 0 to any rollout that contains a notice, and since the token ids and logprobs pass through untouched, the trainer still trains on the blocked tokens: GRPO pushes the attempt down.

| the agent tries to… | stage | blocked by |
| --- | --- | --- |
| call a tool the request never declared | 1 | `undeclared tool` |
| `curl` a host that appears nowhere in the conversation | 1 | `` host `…` appears nowhere in the conversation `` |
| write the verifier's reward file | 2 | `tamper.reward_write` |
| edit the test files | 2 | `tamper.test_files` |
| get around the sandbox proxy, e.g. `curl --noproxy` | 2 | `network.proxy_bypass` |
| `cat /tests/grader.py`, or `hf download FineEnvs/SmolDataEnvs-harbor-train` | 2, our plugin | `smoldataenvs.answer_source` |
| fetch the trajectory a Repo2RLEnvs task was built from | 2, our plugin | `traj2envs.solution_source` |
| `echo $HF_TOKEN` | 2, our plugin | `*.hf_credential` |

### Caught in a smoke run

We didn't have to wait long to see it work. In TwIL-8B's smoke run, at step 0, before any update, the model was working on a [SmolDataEnvs](https://huggingface.co/datasets/FineEnvs/SmolDataEnvs-harbor-train) task: answer a question about a Kaggle dataset. Instead of computing the answer, it went looking for the Hugging Face bucket the task's data was staged from, where the original notebook might be:

```
BLOCKED · TwIL-8B · pi · step 0 · 2026-11-05 11:56 UTC · bash

python3 -c "from huggingface_hub import list_bucket_tree; bucket = 'AdithyaSK/jupyter-agent-kaggle-all' ..."

[safeagents] blocked call to `bash`: atif-scan: smoldataenvs.answer_source (high)
```

The command names `jupyter-agent-kaggle`, one of the sources our [SmolDataEnvs](https://huggingface.co/datasets/FineEnvs/SmolDataEnvs-harbor-train) plugin lists. The call never ran, pi received the notice, and the rollout scored 0. A model that searches for answers at step 0 is the reason the guard is on from the first step, not added once something goes wrong.

### The plugins we train with

atif-scan's built-in rules know about benchmarks in general, not about where *our* tasks' answers live. A plugin adds that: a Python module whose factory returns extra detectors, loaded with `--plugin MODULE:FACTORY`. Ours are three regexes each, matched only against what the agent writes (commands, tool arguments, file contents, search queries and URLs), never against what tools return:

| rule | severity | matches |
| --- | --- | --- |
| `smoldataenvs.answer_source` | high | the public datasets the tasks and their answers come from (`SmolDataEnvs`, `FineEnvs/`, `jupyter-agent-dataset`, `jupyter-agent-kaggle`), `gold_answer`, `EXPECTED_ANSWER`, `task.toml`, `/tests/grader` |
| `smoldataenvs.source_recon` | medium | the task's staging script, bucket and Kaggle dataset names, Kaggle URLs |
| `traj2envs.solution_source` | high | the source trajectory datasets and the session id of each trajectory file, `traj2envs`, `source_trace`, `task.toml` |
| `traj2envs.hub_download` | medium | any Hub download: build tasks have no reason to use one |
| `smoldataenvs.hf_credential`, `traj2envs.hf_credential` | high | `HF_TOKEN`, the token file, `hf auth` and `huggingface-cli login` |

A rule is a few lines:

```
RegexDetector(
    CheckSpec("smoldataenvs.answer_source", Severity.HIGH, title="Task's published answer or grader sought"),
    r"\bSmolDataEnvs\b|\bFineEnvs/|jupyter-agent-dataset|jupyter-agent-kaggle"
    r"|\bgold_answer\b|\bEXPECTED_ANSWER\b|(?<![\w-])task\.toml\b|/tests/grader",
    AUTHORED,  # commands, arguments, payloads, queries, URLs
)
```

Since every run mixes both environments, the trainer loads both plugins:

```
--safeagents \
  --safeagents-plugin atif_smoldataenvs.py:checks \
  --safeagents-plugin atif_traj2envs.py:checks
```

Loading them together needed one fix. [SmolDataEnvs](https://huggingface.co/datasets/FineEnvs/SmolDataEnvs-harbor-train)' rule first matched any `grader.py`, and a Repo2RLEnvs build task asks the agent to write exactly that: a small auto-grading library. The rule would have scored correct work 0. It now matches only `/tests/grader`, where the [SmolDataEnvs](https://huggingface.co/datasets/FineEnvs/SmolDataEnvs-harbor-train) grader lives. Rescanned with both plugins, 213 agent sessions on Repo2RLEnvs tasks match none of their rules. Sandboxes get no Hugging Face token at all; the credential rules are there in case one leaks in.

In a 50-step ablation (pi, LFM2.5-24B-A2B), turning the guard on changed held-out pass@1 by +0.0 ± 4.1 points: it costs nothing. It's there for when the policy gets creative, as TwIL-8B showed.

## What's next

The final runs train all three models under all three harnesses: 200 steps for LFM2.5-24B-A2B, 400 for LFM3-1.7B and 300 for the TwIL experiment, each checkpoint evaluated as it lands. They are streamed on the [live dashboard](https://harness-hub-harness-adapters-rl.hf.space/): train reward, held-out pass@1 per checkpoint, tool calls per solved task, and every safeagents event.

Everything is open: the environments, the safeagents rules, the training recipe, every checkpoint's eval and every blocked tool call. Built with [TRL](https://github.com/huggingface/trl), OpenEnv, Harbor and vLLM.

## Openings: train an adapter for your own agent

Nothing in this recipe is specific to our harnesses or our tasks. The sessions you already run with your agent are the raw material for its next adapter:

1. Save your trajectories: keep the sessions of the agent you use every day, whatever the harness (pi, opencode, hermes, Claude Code, Codex…).
2. Scrub and share them: `safeagents scrub` removes credentials, secrets, emails and home directories, and `safeagents publish` pushes only the redacted copy to the Hub. Every shared session is a candidate environment, for you and for everyone else.
3. Turn them into environments: [Repo2RLEnv](https://github.com/huggingface/Repo2RLEnv) rebuilds each session as a verifiable task, with its Docker image, hidden tests and an oracle taken from the session itself.
4. Train a LoRA adapter inside your harness: run the same RL recipe with [TRL](https://github.com/huggingface/trl), with safeagents and a small plugin of your own guarding every tool call, then put the adapter behind your local agent.

The more people share their sessions, the more varied the environments get, and we're especially short of sessions where something breaks and gets fixed, or where a project grows over several requests. If you train an adapter for a harness we haven't covered, we'd love to hear about it.

## Acknowledgments

Thanks to Aritra Roy Gosthipaty, Shaun Smith, Adithya S Kolavi, Ben Burtenshaw and Amine Dirhoussi for their help and feedback on this work.

## Models mentioned in this article 4

 

## Datasets mentioned in this article 6

 

## Spaces mentioned in this article 1

  

## Collections mentioned in this article 1

  

### Community

Upload images, audio, and videos by dragging in the text input, pasting, or clicking here.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2Fharness-hub%2Fharness-adapters) or [log in](https://huggingface.co/login?next=%2Fblog%2Fharness-hub%2Fharness-adapters) to comment

[Upvote

46](https://huggingface.co/login?next=%2Fblog%2Fharness-hub%2Fharness-adapters)  

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1648631057413-noauth.png)](https://huggingface.co/ybelkada "ybelkada")
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/608aabf24955d2bfc3cd99c6/-YxmtpzEmf3NKOTktODRP.jpeg)](https://huggingface.co/ariG23498 "ariG23498")
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1678663263366-63e0eea7af523c37e5a77966.jpeg)](https://huggingface.co/SaylorTwift "SaylorTwift")
- [![](https://huggingface.co/avatars/fd5487822c0c223732070dd3e9aedf25.svg)](https://huggingface.co/evalstate "evalstate")
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/63a369d98c0c89dcae3b8329/AiH2zjy1cnt9OADAAZMLD.jpeg)](https://huggingface.co/AdinaY "AdinaY")
- [![](https://huggingface.co/avatars/2299442868e076ba2db8e4badd12b8af.svg)](https://huggingface.co/Tastler "Tastler")
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/68b232dcf6027d00161fb46c/FwXMNqgpoXBb2NWJ3X_Pq.jpeg)](https://huggingface.co/MadMike477 "MadMike477")
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6317233cc92fd6fee317e030/cJHSvvimr1kqgQfHOjO5n.png)](https://huggingface.co/tomaarsen "tomaarsen")
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/60a551a34ecc5d054c8ad93e/Z3GDwcXyTyiAXfoeO7tEt.jpeg)](https://huggingface.co/mishig "mishig")
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1669189789447-629f3b18ee05727ce328ccbe.jpeg)](https://huggingface.co/kashif "kashif")
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1617264212503-603d25b75f9d390ab190b777.jpeg)](https://huggingface.co/pcuenq "pcuenq")
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/5f17f0a0925b9863e28ad517/78BR8GuQiX9a8wbbRlSAC.webp)](https://huggingface.co/victor "victor")

## Models mentioned in this article 4

 

## Datasets mentioned in this article 6

 

## Spaces mentioned in this article 1

  

## Collections mentioned in this article 1
