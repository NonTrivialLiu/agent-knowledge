---
title: "Measuring AGENTS.md: Five-Run Benchmark Results"
url: https://aaif.io/blog/measuring-agents-md-what-five-runs-show-that-one-doesn-t
type: engineering-blog
topics: [harness, agents-md, measurement]
summary: "五次重复运行展示 AGENTS.md 收益测量的方差与外推限制。"
---

# Measuring AGENTS.md: Five-Run Benchmark Results - Agentic AI Foundation (AAIF)

URL Source: https://aaif.io/blog/measuring-agents-md-what-five-runs-show-that-one-doesn-t

AGENTS.md didn't win by mandate. No vendor forced it, no spec committee voted it in. It started as OpenAI's answer for Codex. Cursor, Amp, opencode, Warp, Claude Code, GitHub Copilot's coding agent, and goose didn't have to follow. They did anyway, all adopting the same plain Markdown file at the root of a repo for agent-facing context.

That's a rare outcome in developer tooling, and it's exactly the kind of outcome AAIF exists to protect: an open, vendor-neutral standard that any tool can adopt without asking permission.

But adoption isn't evidence. A format can spread because it's convenient, gets recommended in enough onboarding docs, or simply because everyone else is doing it, not because anyone's shown it changes what an agent actually does on a real task. I wanted to know which one this was.

AGENTS.md is a Markdown file that gives coding agents the repo-specific context a README doesn't: build commands, test commands, file boundaries, conventions. No schema, no required fields, just Markdown. It's now stewarded by the Agentic AI Foundation under the Linux Foundation, alongside MCP, goose, and agentgateway, the other open infrastructure pieces most coding agents already touch.

Claude Code reads its own CLAUDE.md natively rather than AGENTS.md directly. Its own documentation recommends bridging the two with a one-line @AGENTS.md import or a symlink, so a team can still maintain a single source of truth even when a tool has its own native filename.

The pitch is straightforward: write your repo's operating instructions once, and every compliant agent reads the same file. Switch tools, and your instructions don't have to be rewritten. That's the interoperability case for the standard. What it doesn't tell you is whether the file changes agent behavior in a way you can actually measure, or whether it's a nice idea that mostly sits unread.

I ran a controlled test on a real repository: [teamxray](https://github.com/AndreaGriffiths11/teamxray), a VS Code extension with a normal amount of repo-specific texture, npm not pnpm, a specific pretest chain, a postinstall patch script, generated files that shouldn't be touched.

Two identical clones. One got a twelve-line AGENTS.md. One didn't. Same coding agent, GitHub Copilot CLI in non-interactive mode, chosen because it reports credits, tokens, and wall time per run and scripts cleanly for repeated trials. Same prompt, same starting commit, five runs per condition.

Two tasks. One ambiguous (add a utility function, let the agent figure out conventions), one multi-file and closer to real feature work (register a new command across two files, with a couple of realistic ways to make the change too broad).

My first attempt to measure this, one run per condition, told me the wrong thing. On the harder task, the AGENTS.md run looked 44% slower and 41% more expensive for identical output. Clean numbers. Wrong conclusion. Agent wall-clock time and token counts are noisy enough per run that a single comparison can point the wrong direction and still look convincing.

I ran every condition five times and took the median instead of trusting one sample. The result flipped back. AGENTS.md won on both tasks. On the ambiguous task, it cut wall time 27%, credits 24%, and produced diffs 26% smaller, because the file's single instruction to keep changes scoped removed defensive code nobody asked for. On the multi-file task, the median win was smaller, 9 to 10%, but the more useful finding was in the tail: two of five runs without AGENTS.md wasted time re-orienting in the repo or running an unrequested production build at the end. Every run with AGENTS.md skipped both. None of the runs, with or without the file, touched the protected postinstall script or webpack config, so the guardrails weren't the reason for the win. The context was.

A few patterns repeated across the runs, and they matched what I found reading Cursor's, Codex's, Amp's, Claude Code's, and Warp's own guidance on writing these files, independently of my results.

Concrete instructions beat aspirational ones. "Follow best practices" gives an agent nothing to act on. "Run npm run lint after any source change" and "do not edit files in dist/" give it commands, paths, and boundaries. A few extra characters of specificity, completely different runtime behavior.

Short files perform better than long ones. Cursor recommends staying under 500 lines; Claude Code targets under 200 for its equivalent file. OpenAI's own Codex documentation confirms this isn't just style preference: Codex caps the combined instruction chain at 32 KiB by default (configurable via project_doc_max_bytes) and truncates past that limit. A file is read and reasoned about on every turn whether the task needs it or not, so length is a cost you pay on every run, not just the ones where it matters.

Nested files are the right pattern for monorepos: a general file at the root, specific files in subprojects, closest file wins, and an explicit user instruction still overrides the file. That precedence keeps the standard useful without letting it override the actual task.

And AGENTS.md is guidance, not enforcement, a distinction Amp's and Claude Code's own documentation make explicit. It can tell an agent not to touch a file. It can't guarantee that. Real enforcement still belongs to CI, branch protection, and sandboxed execution. The value of the standard isn't that it replaces those controls. It's that a team running multiple agents no longer needs to maintain multiple, slowly diverging copies of the same repo guidance, one per tool.

That last point is the strongest case for AGENTS.md living under an open foundation rather than any single vendor. A team adopting three different coding agents without a shared format is maintaining three separate files of the same advice, each updated by whoever remembered last, each drifting at its own pace. A single, portable, git-tracked file means one place to fix a wrong instruction and one diff for every compliant agent to pick up the moment it merges.

That's the promise AAIF was set up to keep: a standard that works the same way regardless of which member company built the tool reading it. My results are one data point, gathered on one repo with one agent, but they're a data point in the right direction: the standard doesn't just spread because it's convenient. On the tasks I tested, it measurably changed what the agent did, and it did it without needing any single vendor's cooperation to work.

If you're deciding whether to add an AGENTS.md to a repo your team already runs agents against, here's where I'd start:

1.   Write the short version first: package manager, key commands, one generated-file boundary, one line about staying scoped to the task. Twelve lines is enough to start.
2.   Run one small task with an agent before and after. Watch where it guesses wrong. Turn each guess into a line in the file.
3.   Add nested files only where a subfolder's conventions actually diverge from the root, not because a deeper structure looks more thorough.
4.   Keep enforcement in CI and branch protection, not in the file. The file guides; the checks decide.
5.   Don't optimize for the average case. Optimize for the runs where an agent would otherwise wander, reorient, or touch something it shouldn't. That's where the measurable win showed up in my tests.

If you're running similar tests on your own repos, especially at a scale bigger than one contributor's side project, I'd be interested to know whether the pattern holds. A standard this widely adopted deserves more than one person's data.
