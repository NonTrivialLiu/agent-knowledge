---
title: "The Anatomy of Harness Engineering: How to Evaluate, Iterate, and Guard AI Coding Agents"
url: https://developers.googleblog.com/the-anatomy-of-harness-engineering-how-to-evaluate-iterate-and-guard-ai-coding-agents/
published: 2026-09-09
fetched: 2026-11-11
type: engineering-blog
topics: [harness, google, multi-agent, evaluation]
summary: "Google Antigravity 工程团队讨论行为级评估：观察中间工具调用、文件修改与回归，补足单一终局 benchmark 分数不能定位原因的问题。"
---

# The Anatomy of Harness Engineering: How to Evaluate, Iterate, and Guard AI Coding Agents

When developers first work on harness engineering for agentic coding systems, they often fall into the same trap: they run common end-to-end benchmarks like Terminal-Bench and DeepSWE, watch a composite score move by a few percentage points, and have no idea why it changed.

End-to-end benchmarks are the de facto for evaluating model performance and determining what needs deeper investigation, but the challenge is that those investigations come at a high cost.

**Behavioral evaluations are often a better measure of confidence** on whether the behaviors you expect actually do happen and whether you’re moving in the right direction instead of backsliding when it comes to regressions or new model changes. They can serve as your iteration partner and help give insight into why certain changes move the needle in one way or another.

Here’s our take on behavioral evaluation, including approaches that have helped us keep agent systems reliable as models evolve.

Most teams evaluate AI agents like they would evaluate a student taking an exam. They hand the agent a large codebase, give it a time limit, and measure its success based on how many tests pass or fail.

When that score drops, what went wrong?

End-to-end benchmarks don’t typically directly answer these questions.

**Behavioral evaluations** function like integration tests for improving agent harness operation. When you have a rich enough behavioral eval set, you have a baseline for the behavior you're targeting from your agent, and you're able to iteratively improve the prompt to get there.

Instead of measuring whether the agent solved an entire multi-file refactor, a behavioral eval measures discrete, observable actions:

Instead of setting up a complex evaluation harness on day one, use this time to follow your hunches and run experiments.

When bootstrapping an agent from scratch, **you start with developer instinct and dogfooding**. Until you have built an agent capable of dogfooding its own codebase, handling boilerplate, writing its own markdown renderer, and executing routine developer tasks, it doesn’t make sense to run evaluations.

Evals belong to the second phase of development: **ensuring forward progress** and **guarding against regressions**.

The primary purpose of an evaluation suite is not to celebrate when you make the agent 2% better; it is to give you unshakeable confidence that a new prompt tweak, tool schema change, or model upgrade **did not make the agent holistically worse**.

A robust harness evaluation framework separates behavioral assertions into fast, deterministic, unit-style checks that run locally.

Shifting your focus to these smaller, observable actions creates a reliable safety net. You can confidently iterate on your system prompts or switch to a different model, because you’ll know immediately if you've accidentally broken a core behavior.

Behavioral evals assert on intermediate execution steps, like specific tool calls or file modifications, instead of final string equality:

```
import pytest
from google.antigravity import Agent, LocalAgentConfig, types
@pytest.mark.asyncio
async def test_agent_uses_web_search_for_live_weather():
  """Assert that the agent consults ground truth rather than guessing."""
  config = LocalAgentConfig()
  async with Agent(config) as agent:
    response = await agent.chat("What's the weather like in Mountain View, California?")
    tools = [call.name async for call in response.tool_calls]
  # Assert behavior, not output prose
  assert types.BuiltinTools.SEARCH_WEB in tools, (
      "Agent answered from memory without consulting live search."
  )
```
With a rich suite of behavioral evals, you can automate your prompt engineering. For example, you can set up a loop where an LLM tweaks its own system prompt, iterating until a failing test finally passes, all while the rest of your test suite acts similar to how a CI/CD-style guardrail operates. This helps you ensure that the changes don’t break any existing features.

There are a few things you can do from the start to make this process repeatable. I suggest you start small with a three-step behavioral testing loop:

```
# Run local behavioral suite in under 5 seconds
pytest evals/behavioral/ -v
```
Your agent doesn't need a higher benchmark score to get started. It needs an evaluation harness that keeps it honest.

To build a stable, resilient harness, you have to stop treating your model like a black box passing a final exam, and start treating your harness like standard software that requires unit and integration testing.

While behavioral evaluations are a core pillar of harness engineering, they aren’t a replacement for larger, end-to-end evaluation suites. They’re actually complementary. Macro benchmarks verify the final destination and micro behavioral evals serve as a partner that enables safe, rapid iteration. When you adopt both, you'll have higher confidence levels when iterating, like when making prompt changes, building out new features, or even deploying brand-new models.
