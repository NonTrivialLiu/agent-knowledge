---
title: "Tuning Deep Agents to Work Well with Different Models"
url: https://www.langchain.com/blog/tuning-deep-agents-different-models
published: 2026-04-29
fetched: 2026-11-11
type: engineering-blog
topics: [harness, langchain, multi-agent]
summary: "模型和 harness 联合调参；同一个模型在不同提示、工具和中间件配置下表现不同。基于 tau2-bench 困难子集，不应当泛化为全部工作负载。"
---

# Tuning Deep Agents to Work Well with Different Models

## Key Takeaways

‍💡**TL;DR:** [Deep Agents](https://github.com/langchain-ai/deepagents) was previously designed in a generic way to work well across model families. Today we’re adding model-specific profiles to adjust prompts, tools, and middleware. This allows us to better conform to prompting guides specific to model families. We ship profiles for OpenAI, Anthropic, and Google models out of the box, which we see leads to a 10–20 point jump on a subset of tau2-bench over the default harness.

Until today, `deepagents` shipped with a single set of prompts, tools, and middleware aimed to work well across *all* Large Language Models. Builders could swap in different models or extend the harness with additional tools extensions to the system prompt. But the base prompts, tools, and middleware were fixed and not optimized per model.

As of today, we’re excited to launch **harness profiles** as a way to control these parameters on a per-model basis. This matters because:

- **Prompting guides differ per model.** OpenAI's [Codex Prompting Guide](https://developers.openai.com/codex/prompting) prescribes specific tool implementations and names (`apply_patch`, `shell_command`) that move the needle on Codex models. Anthropic's [Claude prompting guidance](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) emphasizes a different set of conventions. Even within a family, the Opus 4.6 → 4.7 migration guide flags prompt-level changes worth making.
- **Eval leaderboards show that the same model in a different harness can yield much different performance.** [Terminal-Bench 2.0](https://www.tbench.ai/leaderboard/terminal-bench/2.0) is the cleanest public example. The [Claude Code harness ranks last](https://www.tbench.ai/leaderboard/terminal-bench/2.0?models=Claude+Opus+4.6) among Opus 4.6 submissions.  We saw similar effects of careful harness engineering in previous work: [Improving Deep Agents with harness engineering](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering). Here we took `gpt-5.2-codex` from 52.8% to 66.5% on Terminal-Bench 2.0 (Top 30 → Top 5 at the time of publishing) *just by applying harness layer changes* like prompts and middleware hooks.

A single harness can't be optimal for every model. So we make it easy to support varying the harness per model.

How much does this matter?

## Results on measuring the effect of profiles

In order to judge how much this matters, we measured performance on a subset of [tau2-bench](https://github.com/sierra-research/tau2-bench) (multi-turn tool use + instruction following). We use a curated subset of more difficult tasks that frontier models haven’t yet saturated so we can better measure the impacts of harness level changes on agents.

| Model | Base Deep Agents Harness | With Custom Profile |
| --- | --- | --- |
| GPT 5.3 Codex | 33% | 53% |
| Claude Opus 4.7 | 43% | 53% |

### What changed per model

We use the [Codex](https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide) and [Claude](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) prompting guides as the source for what changes we applied per profile.

For Codex the main changes included:

- **Tool changes:** overriding the default `edit_file` implementation in `deepagents` with the recommended `apply_patch` tool, and aliasing the `execute` tool name in `deepagents` as `shell_command`
- **Prompt changes:** largely around tool calling and planning using details from the prompting guide

> Before any tool call, decide ALL files and resources you will need. Batch reads, searches, and other independent operations into parallel tool calls instead of issuing them one at a time.

For Opus the main changes were all prompting focused on tool usage and planning. For example, below are two snippets that were added to the prompt.

> <tool_result_reflection>  
> After receiving tool results, carefully reflect on their quality and determine optimal next steps before proceeding. Use your thinking to plan and iterate based on this new information, and then take the best next action.  
> </tool_result_reflection>

> <tool_usage>  
> When a task depends on the state of files, tests, or system output, use tools to observe that state directly rather than reasoning from memory about what it probably contains. Read files before describing them. Run tests before claiming they pass. Search the codebase before asserting a symbol does or does not exist. Active investigation with tools is the default mode of working, not a fallback.  
> </tool_usage>

Our takeaway is that exposing an interface for customizing the harness per model is a helpful primitive for builders to manage profiles per agent, version them, and easily test differences in configurations.

## Try it today

To use this today, simply start using:

```
deepagents: uv add deepagents
```

```
agent = create_deep_agent(
    model="google_genai:gemini-3.1-pro-preview",
    tools=[internet_search],
    system_prompt=research_instructions,
)
```

The profiles will be automatically applied for supported models. If you want to look into the details of what each default profile looks like today, you can inspect the code in the [repo](https://github.com/langchain-ai/deepagents). To learn how to register your own profile, keep reading.

### How profiles work under the hood

A harness profile is a declarative override layer for the parts of the harness that vary per model: system prompt prefix/suffix, tool inclusion and naming, middleware selection, subagent configuration, and skills. You register a profile for a model or provider (or load a preexisting one from YAML), and `create_deep_agent` adapts when you swap the model. Importantly, your call site doesn't change.

We ship defaults for OpenAI, Anthropic, and Google models. You can override them, layer your own on top, or distribute profiles as plugins.

```
from deepagents import (
    HarnessProfile,
    register_harness_profile,
)

register_harness_profile(
    "openai:gpt-5.4",
    HarnessProfile(
        system_prompt_suffix="Respond in under 100 words.",
        excluded_tools={"execute"},
        excluded_middleware={"SummarizationMiddleware"},
    ),
)
```

Or declare a profile in YAML:

```
# openai.yaml
base_system_prompt: You are helpful.
system_prompt_suffix: Respond briefly.
excluded_tools:
  - execute
  - grep
excluded_middleware:
  - SummarizationMiddleware
  - my_pkg.middleware:TelemetryMiddleware
general_purpose_subagent:
  enabled: false
```

For more custom details read the [Profiles docs](https://docs.langchain.com/oss/python/deepagents/profiles) for the full field surface, merge semantics, and plugin packaging. Register a profile at startup for the models you use, or rely on the built-in profiles we ship.

If you're building on Deep Agents and want to share a profile, [open a PR](https://github.com/langchain-ai/deepagents) or [distribute it as a plugin](https://docs.langchain.com/oss/python/deepagents/profiles#ship-a-profile-as-a-plugin) via entry points. We'll keep extending the profile surface across models. The goal is that whichever model you reach choose, Deep Agents gives you the tools and defaults to create the best harness for your task. We’ll be releasing more information and walkthroughs showing how builders can customize their agent harness for their tasks.
