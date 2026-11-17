---
title: "Claude Code Subagents in 2026: Six Patterns That Work, Three That Do Not"
url: https://klymentiev.com/tools/claude-code-subagents
published: 2026-10-24
fetched: 2026-11-17
type: engineering-blog
topics: [multi-agent, subagent, context-budget, practice]
summary: "社区实证：subagent 描述合计超 15k token 触发警告——描述只写路由行、细节放运行时；委派三信号、默认嵌套 3 层、回传须点名要哪些事实而非只要结论。"
---

# Claude Code Subagents in 2026: Six Patterns That Work, Three That Do Not

By Dmytro Klymentiev
· October 24, 2026

A Claude Code subagent is a separate Claude instance with its own context window, its own system prompt, and its own tool permissions. You hand it a task, it works in isolation, and it returns a summary to your main session. The search results, log dumps, and half-explored files it reads never enter your conversation.

That isolation is the point. It is also the cost, and most subagent mistakes come from forgetting the second half of the sentence.

*Written October 8, 2026. Facts below come from the Claude Code subagents documentation (code.claude.com, accessed October 2026) and Anthropic's guide How and when to use subagents in Claude Code (April 7, 2026). The positions are mine.*

## What a subagent actually is

A subagent is a Claude instance that starts fresh. It does not see your conversation history, the files you have already read, or the skills you invoked earlier in the session. It gets a system prompt from its own definition file plus a task message that Claude writes when it delegates. It works, then returns only its result.

Claude Code ships several built-in subagents and uses them on its own when a task fits:

- Explore, a fast read-only agent for file discovery and code search.
- Plan, a research agent used during plan mode before Claude proposes an implementation.
- General-purpose, for multi-step work that needs both exploration and edits.

A custom subagent is a Markdown file with YAML frontmatter. Only two fields are required: name and description. Everything else, tools, model, hooks, memory, is optional.

## When to use one

The honest rule is narrower than most write-ups suggest. Use a subagent when the work is self-contained, produces a lot of output you will not reference again, and can be summarised on the way back.

Three signals point to delegation:

- Gathering context means reading dozens of files before you can change anything.
- The subtasks do not depend on each other and can run at the same time.
- You want a second opinion from something that has not seen how the code got here.

If none of those is true, a subagent adds a layer of indirection and a cold context to refill for no gain.

## Six patterns that work

1. Isolate high-volume operations. Run the test suite, fetch documentation, or process log files through a subagent and ask for only the failures. The verbose output stays in the subagent's context; your session gets the three failing tests and their error messages.

1. Run parallel research. When authentication, the database layer, and the API routes are independent questions, spawn a subagent per area. Each explores on its own, and Claude synthesises the findings. This is the pattern that saves the most wall-clock time.

1. Chain subagents for staged work. Design, then implement, then test. Each stage gets a focused context window and a clean handoff, so the implementation agent is not distracted by design debate and the test agent does not inherit the implementer's assumptions.

1. Get an independent review. A subagent that did not watch you write the code evaluates it without your tradeoffs, your rejected approaches, and your assumptions. It catches what familiarity hides, especially before a commit. This is the same as asking a colleague who was not in the meeting.

1. Restrict tools per subagent. A research subagent can be read-only: give it Read, Grep, and Glob and it physically cannot edit. An implementation subagent gets Edit and Write. If you want a reviewer that stays read-only, deny it the Agent tool so it cannot spawn further subagents of its own. Tool lists are the cheapest guardrail in the system.

1. Route cheap work to a cheaper model. A subagent can run on a different model than your main session. The model field accepts sonnet, opus, haiku, fable, or a full model id, or you can set CLAUDE_CODE_SUBAGENT_MODEL for a default, and CLAUDE_CODE_SUBAGENT_MODEL_FORCE to apply one model to every subagent. Exploration on a small model is a reasonable trade; hard reasoning is not.

## Three patterns that do not work

1. Parallel edits to the same file. Two subagents editing one file is a recipe for conflict. Tightly coupled changes belong in one context window, not in a relay. This is the mistake that ends with a merge you have to untangle by hand.

1. Sequential work where each step needs the last step in full. When step two needs everything step one produced, and step three needs both, a chain of subagents passing state through files is worse than one session doing the whole thing. The context you save does not cover the context you lose.

1. Small, one-off tasks. For a quick fix or a focused question, delegation costs more than it saves. The subagent starts cold, re-derives background you already have, and spends tokens of its own. Just ask in the main conversation.

A fourth, softer failure mode is worth naming: a large roster of narrowly scoped specialists. Flooding the session with options makes automatic delegation less reliable, and it costs context, which is the next section.

## The gotcha nobody mentions

Every custom subagent's description is loaded into your main session at startup. Not only when the subagent runs: always, because Claude uses the description to decide when to delegate.

The practical consequence is easy to miss. Build a dozen specialists with careful descriptions and you have quietly spent part of the context window you were trying to protect. Claude Code shows a warning at startup when the combined descriptions of your custom subagents pass 15,000 tokens, with the running total.

The fix is straightforward once you know the rule: keep each description short and specific about when to use it, and move the detail into the subagent's system prompt, which only loads when that subagent actually runs. A description is a routing line, not documentation.

The same cold-start logic explains a related trap: a subagent returns a summary, so the raw material it worked from is gone. If you need to audit its work, ask for the specific facts you want back, not just the conclusion. Ask only for a verdict and you have a verdict you cannot check.

## Defining your own subagent

Subagent files live in one of five places, and the scope decides who sees them. When two subagents share a name, the higher-priority scope wins:

- Managed settings, deployed by an organization administrator. These outrank project and user subagents with the same name.
- Session-only JSON passed at launch, useful for a throwaway test. It is scoped to the current session and outranks project and user definitions.
- A project's .claude/agents/ directory, checked into version control and shared with the team.
- The user-level ~/.claude/agents/ directory, available in every project on the machine.
- A plugin's agents/ directory, for definitions distributed with a plugin.

The fields that matter most in day-to-day use:

- description: when Claude should delegate here. This is the routing rule, and it counts against the context budget above.
- tools and disallowedTools: an allowlist and a denylist for what the subagent can touch.
- permissionMode: the permission mode the subagent runs in, which can differ from the main session's. Values include default, acceptEdits, plan, and bypassPermissions.
- model: sonnet, opus, haiku, fable, or inherit.
- maxTurns: stops a subagent that will not converge; the run comes back marked partial and can be resumed.
- skills: skills preloaded into the subagent's context at startup.
- memory: user, project, or local, for cross-session learning.
- hooks: lifecycle hooks scoped to this subagent.
- mcpServers: MCP servers available only to this subagent, including inline definitions.
- omitClaudeMd: true launches the subagent without the user, project, and local CLAUDE.md files, for agents that take everything they need from the delegation prompt.
- isolation: worktree, to run the subagent against a temporary copy of the repository.

Two scale limits are worth knowing before you build a large system. Subagents can spawn their own subagents, nesting up to three layers below your main conversation by default; the limit is configurable and setting it to one turns nesting off. And a session stops spawning at 20 concurrent subagents by default. Both are adjustable, but the defaults are a reasonable ceiling for a single session.

You invoke a subagent three ways: by naming it in plain language so Claude delegates, by @-mentioning it so that specific agent runs for one task, or session-wide by starting Claude Code with an agent name or setting a default agent in project settings.

## Where subagents fit next to the rest of Claude Code

Subagents are one of several isolation tools now, and it helps to keep them straight. Skills are reusable prompts that run in your main context rather than an isolated one. Hooks are shell commands, HTTP endpoints, or prompts that fire on lifecycle events. Cross-session messaging and agent teams connect separate sessions that need to talk to each other, which subagents cannot do. If your subagents need to communicate with one another, subagents are the wrong tool.

For the surfaces around them, the [Claude Code CLI](https://klymentiev.com/tools/claude-code-cli) is where most sessions start, [hooks](https://klymentiev.com/tools/claude-code-hooks) automate the lifecycle, and [skills](https://klymentiev.com/tools/claude-code-skills) package repeatable workflows.

## Bottom line

Subagents buy you context isolation, parallelism, and a fresh perspective. They cost you a cold start, tokens of their own, and a summary that is the only thing you can audit. Reach for them when the work is self-contained and verbose, keep the roster small, keep the descriptions short, and restrict the tools. Do those four things and they earn their overhead. Skip them and you have built a slower way to do what one session already did.

---

When the AI editor stops being enough and you need a senior engineer for a week to finish the ship, you can [hire a senior Claude Code engineer for a week](https://klim.expert). Dmytro Klymentiev does AI-augmented development consulting: architecture review, stuck implementations, and code that needs a human's judgment to finish.

enjoyed this? follow me!

[X / Twitter](https://x.com/dklymentiev)
[LinkedIn](https://linkedin.com/in/dklymentiev)
[GitHub](https://github.com/dklymentiev)

share this!

[← Back to blog](https://klymentiev.com/blog)
