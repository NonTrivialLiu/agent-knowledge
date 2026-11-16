---
title: "TRACE: Capability-Targeted Agentic Training"
url: https://hgkang02.github.io/trace-blog/
published: 2026-07
fetched: 2026-11-11
type: engineering-blog
topics: [training]
summary: "Stanford团队对比成功和失败轨迹，诊断缺失能力，合成针对性可验证环境，逐能力LoRA并用路由组合；博客可读性高。"
---

# TRACE: Capability-Targeted Agentic Training

Stanford University · \*Equal contribution · July 2026

Agentic LLMs fail in target environments because they often lack *reusable capabilities* the environment demands — retrieving the right customer record before acting, verifying preconditions before a state-changing tool call, or localizing the right function in a large repository. The two mainstream fixes both spend compute poorly:

Our observation is that failures are not random. When we analyze rollouts from a base agent, the same small set of deficits accounts for most failed trajectories. That makes failures *actionable*: instead of training on the whole environment, we can turn each recurring deficit into its own dense, verifiable training signal.

We collect rollouts of the base agent in the target environment and split them into successful (𝒟⁺) and failed (𝒟⁻) sets. An analysis agent reads tool calls, observations, and final responses to induce a canonical capability dictionary, then labels every trajectory–capability pair as `NA`, `PRESENT`, or `LACKING`. A capability *c* is retained only if its absence is concentrated in failures *and* it explains enough of them:

Δ̂(c) = ÊR⁻(c) − ÊR⁺(c) ≥ 0.20

Ĉov(c) = #{failed trajectories lacking c} ⁄ #{failed trajectories} ≥ 0.10

where ÊR<sup>±</sup>(c) is the rate at which *c* is lacking among failed / successful trajectories. On τ²-Bench this yields four deficits: **structured data reasoning**, **multi-step task completion**, **precondition verification**, and **tool-calling precision**.

For each retained capability, an LLM generation agent creates a **seeded, procedurally-generated synthetic environment** that isolates that capability while preserving the target environment's tool schemas and interaction format. Because each task instance is generated from a seed, rewards are **automatically verifiable** from tool arguments, state changes, final answers, or patches — no human labels, and no LLM judge in the reward loop. The result is a much denser learning signal than the original environment, where success depends on many capabilities at once.

Each capability gets its own frozen-base LoRA adapter (≈5% of backbone parameters) trained with GRPO on its synthetic environment. Keeping adapters separate matters: it avoids collapsing several capabilities into one entangled update, and it gives us interpretable experts we can compose — or inspect — later.

A real task interleaves capabilities — a customer-service agent reads structured data, then verifies a precondition, then issues a precise tool call, all in one trajectory. Token-level routing lets the model switch experts mid-trajectory. Top-1 routing works best on τ²-Bench: **48.2%** vs. 47.0% for top-2 and 45.1% for top-4.

We evaluate on **τ²-Bench** (50 airline + 114 retail customer-service workflows, pass rate) and **SWE-bench Verified** (500 real GitHub issues, Pass@1), with Qwen3-30B-A3B-Instruct-2507 and Qwen3.6-27B backbones. Baselines include GRPO directly on the target environment, AWM, ADP, GEPA prompt optimization, and SWE-RL. For SWE-bench, TRACE's capability environments are trained on a disjoint SWE-smith split.

The Qwen3.6-27B result is worth dwelling on. TRACE lifts a 27B open-weight backbone from 68.0% to **73.2% Pass@1** on SWE-bench Verified — which places it **above GPT-5.2-Codex (72.8%)**, GLM 5, and Claude 4.5 Sonnet on the [public leaderboard](https://www.swebench.com/). No frontier-scale pretraining, no proprietary scaffold: the gap is closed purely by diagnosing what the model can't do and training exactly those capabilities.

| Backbone | Method | τ²-Bench Overall | SWE-bench Verified Pass@1 | 
|---|---|---|---|
| Qwen3-30B-A3B | Base | 32.9 | 26.0 | 
|  | GEPA | 39.6 | 31.0 | 
|  | Strongest ext. baseline | 39.6 | 32.6 | 
|  | TRACE (Ours) | 48.2 | 41.0 | 
| Qwen3.6-27B | Base | 50.0 | 68.0 | 
|  | GEPA | 53.0 | 69.6 | 
|  | Strongest ext. baseline | 53.7 | 70.4 | 
|  | TRACE (Ours) | 59.1 | 73.2 | 

Two things stand out. First, **training beats telling**: GEPA can describe the missing capabilities in the prompt, and it helps (+6.7 points), but a single trained capability adapter already exceeds general-purpose AWM and ADP, and four trained capabilities beat the best prompt by +8.6 points. Second, **targeted environments are sample-efficient**: because each synthetic environment rewards exactly one capability, every rollout carries signal about the deficit it was built for, instead of diluting credit across the whole task.

| Consolidation method | τ²-Bench Overall | 
|---|---|
| SFT on synthetic data | 37.8 | 
| Single-capability GRPO | 40.3 | 
| Multi-capability GRPO (one adapter for all) | 40.9 | 
| TRACE MoE (Ours) | 48.2 | 

Given the same synthetic environments, *how* you consolidate the learning matters as much as the data itself. Distilling everything into one adapter — whether by SFT or by multi-capability GRPO — collapses distinct skills into a single entangled update and leaves more than 7 points on the table. Separate experts plus a learned token-level router preserves each capability and deploys the right one at the right step.

**T1 — Failure contrast is actionable.** Comparing success and failure trajectories identifies *trainable* deficits, not generic error categories. The diagnosis is stable across analysis runs, and a handful of deficits covers most failures.

**T2 — Targeted synthetic environments are efficient.** A verifiable environment built around one capability provides far denser supervision than the sparse end-task reward — TRACE outperforms target-environment GRPO and GEPA with less than a quarter of their rollouts.

**T3 — Compositional adaptation matters.** One LoRA expert per capability avoids collapsing multiple skills into one update, and token-level MoE routing selects the right expert at each step — worth +7.3 points over the best single-adapter alternative.

More broadly, TRACE is a recipe for **environment-specific agent self-improvement**: deploy an agent, watch where it recurrently fails, and convert those failures into exactly the training signal that fixes them — no human curation of skills, environments, or rewards in the loop.

```
@article{kang2026trace,
  title   = {TRACE: Capability-Targeted Agentic Training},
  author  = {Kang, Hangoo and Suresh, Tarun and Saad-Falcon, Jon and Mirhoseini, Azalia},
  journal = {arXiv preprint arXiv:2604.05336},
  year    = {2026}
}
```
