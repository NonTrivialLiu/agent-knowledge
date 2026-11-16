---
title: "SentinelBench, a Benchmark for Long-Running Monitoring Agents"
url: https://www.microsoft.com/en-us/research/articles/sentinelbench-a-benchmark-for-long-running-monitoring-agents/
published: 2026-06-08
fetched: 2026-11-11
type: engineering-blog
topics: [evaluation, microsoft, multi-agent, long-running]
summary: "关注等待外部世界变化的长期监测任务，区分主动长任务与事件驱动的安静监测，100个任务、10个模拟环境；由研究团队解释设计及基准结果。"
---

# SentinelBench, a Benchmark for Long-Running Monitoring Agents

![background pattern](https://www.microsoft.com/en-us/research/wp-content/uploads/2024/01/aif_social_banner.png)

## Microsoft Research AI Frontiers

Published 
June 8, 2026

Share this page

- [Share on Facebook](https://www.facebook.com/sharer/sharer.php?u=https%3A%2F%2Fwww.microsoft.com%2Fen-us%2Fresearch%2Farticles%2Fsentinelbench-a-benchmark-for-long-running-monitoring-agents%2F "Share on Facebook")
- [Share on X](https://x.com/intent/tweet?text=SentinelBench%2C%20a%20Benchmark%20for%20Long-Running%20Monitoring%20Agents&url=https%3A%2F%2Fwww.microsoft.com%2Fen-us%2Fresearch%2Farticles%2Fsentinelbench-a-benchmark-for-long-running-monitoring-agents%2F "Share on X")
- [Share on LinkedIn](https://www.linkedin.com/shareArticle?mini=true&url=https%3A%2F%2Fwww.microsoft.com%2Fen-us%2Fresearch%2Farticles%2Fsentinelbench-a-benchmark-for-long-running-monitoring-agents%2F&title=SentinelBench%2C%20a%20Benchmark%20for%20Long-Running%20Monitoring%20Agents&summary=SentinelBench%2C%20a%20Benchmark%20for%20Long-Running%20Monitoring%20Agents&source=Microsoft%20Research "Share on LinkedIn")
- [Share on Reddit](
  			http://www.reddit.com/submit?title=SentinelBench%2C%20a%20Benchmark%20for%20Long-Running%20Monitoring%20Agents&url=https%3A%2F%2Fwww.microsoft.com%2Fen-us%2Fresearch%2Farticles%2Fsentinelbench-a-benchmark-for-long-running-monitoring-agents%2F			 "Share on Reddit")
- [Subscribe to our RSS feed](https://www.microsoft.com/en-us/research/lab/ai-frontiers/feed "Subscribe to our RSS feed")

*By Matheus Kunzler Maldaner, Adam Fourney, Amanda Swearngin, Hussein Mozannar, Gagan Bansal, Maya Murad, Rafah Hosn, Saleema Amershi*

Modern AI agents are increasingly capable of long and complex work. [METR  (opens in new tab)](https://metr.org/time-horizons/)has been tracking how this scales, and the 50% task-completion time horizon for frontier models has roughly doubled every seven months, climbing from four seconds in 2019 to more than sixteen hours in 2026. In practice, that means [hours-long codebase migrations and deep research reports (opens in new tab)](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents), where an agent grinds away at a problem in a single sustained sitting, have become increasingly feasible.

But these workflows embed the implicit assumption that meaningful state changes in the environment come only from the agent’s own actions. In other words, the agent believes it must keep acting to trigger new events to progress with its objective.

That’s the wrong model for a large class of tasks. For example, no amount of reloading a webpage will make concert tickets go on sale faster, and no amount of search broadening helps when those tickets are exclusive to a single site. Here, the correct behavior is to watch, wait, and act only when the environment changes on its own. But current agents are not optimized for this. They either churn obsessively, burning context and tokens on every page refresh (and risking an error on every extra action), or they give up after a few attempts.

In a [previous post](https://www.microsoft.com/en-us/research/blog/tell-me-when-building-agents-that-can-wait-monitor-and-act/), we presented designs for agents that are better able to handle monitoring tasks. We referred to such tasks as Sentinel Tasks and previewed a benchmark for measuring agent performance on these workloads. In this post, we formally present that benchmark, [SentinelBench (opens in new tab)](https://github.com/microsoft/sentinel_environments), as open source on GitHub, and as a [detailed technical report (opens in new tab)](https://arxiv.org/abs/2606.05342).

## Overview

SentinelBench contains 100 tasks spread across 10 high-fidelity synthetic web environments. Each environment mimics a familiar consumer product:

|  |  |  |  |
| --- | --- | --- | --- |
| **MicroMail** | An email client | **MicroGram** | A photo sharing site |
| **MicroChat** | A team messaging client | **MicroTube** | A online video platform |
| **MicroDin** | A professional network | **MicroFy** | A music streaming platform |
| **MicroHub** | A code hosting website | **MicroLendar** | A calendar application |
| **MicroHood** | A stock trading website | **MicroScholar** | Academic Search |

*Table 1: The ten environments in SentinelBench. Each resembles a popular class of web application, and includes both a multi-screen interactive UI, and a catalog of synthetic data from which content and events are sampled.*

What makes these environments useful for benchmarking is that they can evolve over time, regardless of which actions an agent takes. Each task ships with a scripted timeline of events that the server plays back as the simulation runs. New emails arrive, stock prices drift, songs land on the trending feed, and so forth. The agent is then tasked to perform a task on a live page, whose state is changing underfoot. Here is one example from the MicroFy environment, a music streaming platform:

> “Watch the trending feed. When a song drops whose lyrics mention ‘subway’, like it for me.”

To make the simulations feel coherent, all 10 apps are populated from a shared catalog of 100 synthetic personas and 201 entities (e.g., companies, music bands, news organizations etc.) The principal user (the account the agent is acting on behalf of) is a 29-year-old product associate named Chris Taylor, who has the same identity, social network, and content history across all 10 environments.

![table](https://www.microsoft.com/en-us/research/wp-content/uploads/2026/06/persona-chris-preview-1-1-1024x486.png)

*Figure 2: SentinelBench includes 100 synthetic user personas. Each persona consists of core demographic and biographical attributes plus per-environment sub-profiles that ground the same identity coherently across all 10 simulated applications (MicroGram, MicroScholar, MicroFy, MicroHub, MicroDin shown). Chris Taylor, shown here, is the principal user. I.e., the user whose profile is accessed by the agent.*

## Task Design

SentinelBench tasks can be organized along two independent axes of task design, plus a third category of no-operation tasks. These penalize agents that game the benchmark by unconditionally declaring success moments before the simulation ends.

|  |  |  |
| --- | --- | --- |
|  | **Absolute** | **Relative** |
| **Passive** | 18 | 20 |
| **Active** | 23 | 19 |
| **No-operation** (No-op) | 20 | |

*Table 2: Task counts by action requirement and criterion type.*

**Active versus passive.** Some monitoring tasks are purely about detection. The agent notices that the condition has occurred and lets the user know. For example, “Let me know when my post about brunch gets 100 likes”, is passive, and can be solved by watching a social feed. Others require the agent to periodically do something to reveal hidden information. In a team messaging app, a task that says “let me know the moment Charles Davis sends design mockups in any channel” is active because it forces the agent to keep opening chat channels as new messages arrive, to check for Charles’ message.

**Absolute versus relative.** The phrasing of the success criterion changes the cognitive demand on the agent. “Tell me when CHIP exceeds $300 per share”, an absolute task, is solvable from a single screenshot. “Tell me when CHIP is up 10%”, a relative task, forces the agent to remember the starting condition across an arbitrary number of polls. The latter can be a challenge for agents with aggressive context management.

**No-operation tasks.** Finally, there is an obvious adversarial strategy that any benchmark of this type must address. If an agent “knows” when the simulation ends (in our case, 10 minutes by default), it can take increasingly urgent action as the clock nears its end. For example, an agent performing a passive task could unconditionally declare the task complete within seconds of termination, if the task has not already done by that time. To penalize such strategies, 20 of the 100 tasks are deliberately designed so the target condition never fires. The only way to pass a no-op task is to still be watching when the simulation ends.

Finally, by default each task is designed to be solvable inside a 10-minute window, but a single `speed_factor` knob can stretch them out to arbitrary lengths. That’s useful when we want to amplify the cost of bad waiting strategies, which we’ll do later.

## Task Life Cycle

We wanted SentinelBench to work with whatever web agent you already have. From the user’s perspective, the evaluation harness launches an agent from the command shell, with two parameters: the starting page, and the task prompt. The harness doesn’t require a particular browser framework like Playwright, and it doesn’t assume any particular observation modality, whether screenshots, accessibility trees, or the DOM. Instead, any web-capable agent that can be launched from a terminal can be evaluated (agents must also exit when their work is done, rather than interactively prompting the user for more work).

![The simulation life cycle for SentinelBench environments. The evaluation harness interacts with
the server to transition between life cycle states: Pre-init, Ready, Running and Completed](https://www.microsoft.com/en-us/research/wp-content/uploads/2026/06/lifecycle-1024x160.png)

*Figure 3: The simulation life cycle for SentinelBench environments. The evaluation harness interacts with the server to transition between life cycle states.*

Once a SentinelBench evaluation is initiated, an evaluation harness enumerates the tasks, and manages them through a short, four state, life cycle. **Pre-initialization** is the starting state. The harness calls `/init` with a scenario (the event timeline, and an SQL query that will be used to score the task), and the server moves to **Ready**. The agent is then invoked in the terminal. Here it is given the starting page `/redirect`, and the task prompt with an extra benchmark instruction appended to the end: to visit `/contact` “Once the necessary conditions are met and/or sufficient actions are taken”. As the name suggests, `/redirect` serves an HTTP 301 to the actual starting page, at which point the server moves to **Running**. From this moment, scheduled events fire at their wall-clock times, the database updates, and the UI reflects those updates as the agent navigates.

The agent signals task completion by accessing `/contact`, a simple “contact the user” web form. That transitions the server to **Completed** and cancels any remaining scheduled events. The harness detects the transition and hits `/evaluate`, which runs a task evaluation SQL query against the live database state to determine success. Notably, since success is measured against the database, not against the agent’s output, any web-capable agent can be evaluated

## What We Measured

To validate that the benchmark distinguishes meaningful differences, and to establish some baseline for comparisons, we ran each of the benchmark tasks under six conditions. Specifically, we chose three multimodal models (GPT-5.4 in low-reasoning mode, GPT-4o, and Qwen 3.5:9B), each paired with two versions of a simple browser agent adapted from [Magentic-UI (opens in new tab)](https://github.com/microsoft/magentic-ui).

The two versions differ in only one place, namely what the agent does when it decides to wait. The first variant has a familiar `sleep(time)` tool that unconditionally blocks the agent for a specified number of seconds. The second is a purpose-built `wait_for(condition, timeout)` tool. When invoked, `wait_for` takes a baseline textual snapshot of the page, then loops once per second, computing a textual diff against the baseline. For new changes, not previously evaluated, wait_for invokes the LLM to evaluate the change against the condition. This turns out to be both token efficient and responsive as seen below.

![Screenshots and event timelines for an example task in the micro MicroTube environment: ](https://www.microsoft.com/en-us/research/wp-content/uploads/2026/06/microtube-video-total-relative-passive-teaser-1024x556.png)

*Figure 4: Agent execution timelines in SentinelBench for a representative scenario. Each row visualizes one agent strategy over simulated time as events are played back in the simulation (screenshots show the state of the app after selected events). The `sleep` agent spends most of its time executing fixed interval polling  
while the `wait_for` agent waits for a condition for an extended period and resumes once the environment changes to meet the condition. SentinelBench enables systematic investigation of agent implementation choices for measuring progress on time-evolving monitoring tasks.*

## What We Found

From the baseline evaluation, two findings stood out:

**Models are cleanly distinguishable.** Overall pass rates ranged from 0.46 (GPT-4o + `sleep`) to 0.75 (GPT-5.4 + `wait_for`). Within each model, passive tasks were easier than active tasks, as expected. Likewise, GPT-4o and Qwen both struggled noticeably more on relative tasks than on absolute tasks, whereas GPT-5.4 proved to be robust on solving relative tasks (actually performing slightly better on relative tasks!)

![table](https://www.microsoft.com/en-us/research/wp-content/uploads/2026/06/success-rate-table-1.png)

*Table 3: Success rates for three models and two agent configurations (six conditions total). As expected, GPT-5.4 performs better overall than GPT-4o and Qwen 3.5:9B. Likewise, agents configured to use `wait_for`perform about as well as, or better than, agents configured to use `sleep`. We also observe that no-operation  
tasks are generally easier than passive tasks, and that active tasks are harder still. The one exception is GPT-5.4 with sleep, which performs unexpectedly poorly on no-operation tasks.*

While GPT-5.4 fared extremely well, it exhibited a surprising number of failures on the no-operation tasks, when using the sleep tool (0.70 task completion, vs 0.95 – 1.00 for all other conditions). Inspecting the logs, we found GPT-5.4 with `sleep` giving up on tasks too early, filing the contact form with messages like “*I checked the chats and did not find any conversation where Diana Miller @mentioned you.*” The model was effectively acknowledging that the condition had not been met but submitting anyway.

**Waiting strategy matters as much as model choice.** For GPT-5.4 at the default 10-minute setting, the median task cost was 5.1× higher with `sleep` than with wait_for ($1.17 vs. $0.23), with comparable or worse task completion. A similar pattern was observed for the other models, with sleep costing more than `wait_for`, while performing no better.

![Box-whisker plot of task API cost in USD for each model and tool configuration. The horizontal axis is logarithmic; Qwen 3.5:9B is roughly two orders of magnitude cheaper than the GPT models, and within every model sleep is consistently more expensive than wait_for. Means landing outside Q3 (GPT-5.4 wait_for, GPT-4o sleep) reflect right-skewed distributions with high-cost outliers visible at the upper whisker.](https://www.microsoft.com/en-us/research/wp-content/uploads/2026/06/sentinel_api_costs-1-1024x352.png)

*Figure 5: Per-task API cost in USD for each model and tool configuration. Box outlines show the interquartile range, the colored bar inside each box marks the median (blue for `wait_for`, orange for `sleep`), whiskers  
extend to the observed minimum and maximum, and the diamond marks the mean. Dashed horizontal lines separate model groups. The horizontal axis is logarithmic; Qwen 3.5:9B is roughly two orders of magnitude cheaper than the GPT models, and within every model `sleep` is consistently more expensive than `wait_for`.  
Means landing outside Q3 (GPT-5.4 `wait_for`, GPT-4o `sleep`) reflect right-skewed distributions with high-cost outliers visible at the upper whisker.*

## Evaluation “Stretch” Goal

Finally, we re-ran the best-performing model (GPT-5.4) with `speed_factor=0.25`, which stretches the maximum task length from 10 minutes to 40 minutes. At 40 minutes, the gap between the two waiting strategies becomes dramatic. The median task cost under sleep rises to $4.65, while wait_for remains low, and around $0.48. That’s a 9.7× difference.

![chart, scatter chart](https://www.microsoft.com/en-us/research/wp-content/uploads/2026/06/gpt54-cost-vs-target-time-1-1024x434.png)

*Figure 6: Per-task API cost as a function of target event time for GPT-5.4 under the `wait_for` and `sleep`tool configurations. Successful tasks appear as blue dots. Failed tasks appear as red ‘X’s. Here, tasks are scaled to take up to 40 minutes to complete (2400 seconds). When using `wait_for`, costs remain relatively  
stable and low, with some outliers as high as $10.59. When using `sleep`, costs trend upward with time, especially for successful tasks, with costs as high as $31.15.*

This trend is even more evident when plotting cost against the ideal task completion time (the time when the target event occurs). Looking at successful tasks (blue dots in the above figure), `wait_for` cost stays nearly flat, while sleep cost climbs steadily. At the high end, one sleep task cost $31.15 to complete. Pass rate doesn’t compensate either. `wait_for` finishes 69 of 100 tasks correctly, while `sleep` finishes only 56.

Even with the same model, choices made about how an agent waits can dominate everything else about its performance over long-running tasks. SentinelBench surfaces those choices cleanly.

## Availability and Looking Ahead

We’re releasing [SentinelBench  (opens in new tab)](https://github.com/microsoft/sentinel_environments)on GitHub. That includes the ten environments, all 100 scenarios with their event timelines. We also include the generation pipeline that produced them, and a [full technical report on arXiv. (opens in new tab)](https://arxiv.org/abs/2606.05342)

Like any benchmark, SentinelBench makes deliberate tradeoffs. Event timing is artificial rather than sampled from real distributions. The environments are convincing facades but not production systems, and prolonged exploration will find their edges. Most success criteria are still objective rather than judgment-based, and the current tasks watch for persistent conditions — we haven’t yet captured the harder category of ephemeral, must-act-now tasks like “*buy the stock if it dips below $500.*“

But the broader point holds. As agents take on longer-running work, more of their time will be spent waiting than acting. Building always-on assistants requires being able to measure them, and a benchmark whose primary task is to wait is a useful place to start.

Opens in a new tab

## Research Areas

- [![](https://www.microsoft.com/en-us/research/wp-content/uploads/2020/07/msr-ai-2x.png) Artificial intelligence](https://www.microsoft.com/en-us/research/research-area/artificial-intelligence/)

## Related labs

- [Microsoft Research AI Frontiers](https://www.microsoft.com/en-us/research/lab/ai-frontiers/)
