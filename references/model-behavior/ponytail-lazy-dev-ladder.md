---
title: "Ponytail: Lazy Senior Dev Ladder"
url: https://ponytail.dev
fetched: 2026-11-12
priority: core
type: engineering-blog
topics: [model-behavior, anti-overengineering, prompting, ladder]
summary: "懒资深工程师反过度工程阶梯：是否需要存在→复用→stdlib→平台→依赖→一行→最小实现；实测少 53% 代码行；验证与安全不简化。"
---

# Ponytail: Lazy Senior Dev Ladder

A ruleset that makes your AI coding agent write the least code that works: 53% less code, 41% faster, 26% cheaper, and just as correct.

Opus 5.5 on 39 tasks, five runs each: feature tickets in a real repo, tasks with hidden checks, open "build me" requests. No skill = 100%.

Geometric mean of per-task medians. Hidden correctness and safety checks: 96% / 96% / 97% passed.

Validation, error handling, security and accessibility are never simplified away. [Method and limits](https://github.com/DietrichGebert/ponytail/blob/main/benchmarks/results/2026-10-07-agentic.md).

and yet

"Add a date picker to the frontend." Same agent, same repo, lines added, median of five runs.

Without Ponytail: a hand-built calendar and date picker, 335 lines. With Ponytail 5: one 10-line file, built on the browser's own \<input type="date">.

The repo is React, so the answer stays React. The calendar comes from the browser.

It reads the code first and traces the real flow. Then it climbs. Pick a request:

The old review only looked for code to cut. The new /ponytail-review reads the code your change touches, not just the diff: bugs, security, real load, missing tests, speed, and what to cut. Each finding says what the code does, what goes wrong, how to fix it, and what happens if you don't. /ponytail-audit does the same for the whole repo.

New in 5.3: in Claude Code, ponytail shows a band above the prompt. What the current task costs, its tokens and agent time, how often it reused existing code instead of writing new code, and whether the tests passed after the last change. One click runs a review or an audit, copies the task as Markdown, or folds the band into one line.

Board opens a local page with every task across your projects: cost, agent time and tokens over time, every session with its tests, and the days you worked.

Everything stays on your machine.

The band is Claude Code only. The other agents get the same rules without it.

`rules = rules.filter(beats_baseline)`
Every line had to beat the version without it, one change at a time. What did not win, left.

`assert parse_price("1,50") == 150`
A branch, a loop, a parser, money or security leaves one small test. Trivial stays trivial.

`// skipped: retries, add when it flakes`
Every reply ends with what was left out or not checked, and any risk.

`claude · codex · copilot · gemini · pi`
Claude Code, Codex, Copilot, Gemini, Cursor, OpenCode, pi and a dozen more.

/plugin marketplace add DietrichGebert/ponytail
/plugin install ponytail@ponytail

$ codex plugin marketplace add DietrichGebert/ponytail
$ codex plugin add ponytail@ponytail

`$ copilot plugin install ponytail@ponytail``$ gemini extensions install github.com/DietrichGebert/ponytail``$ pi install git:github.com/DietrichGebert/ponytail`
Cursor, Windsurf, Cline, Kiro, OpenCode, Zed and the rest: [INSTALL.md](https://github.com/DietrichGebert/ponytail/blob/main/INSTALL.md).

Only install from DietrichGebert/ponytail or @dietrichgebert/ponytail on npm.
