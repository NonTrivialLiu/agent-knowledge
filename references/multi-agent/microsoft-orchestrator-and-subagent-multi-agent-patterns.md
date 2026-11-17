---
title: "Orchestrator and subagent multi-agent patterns"
url: https://learn.microsoft.com/en-us/agents/architecture/multi-agent-orchestrator-sub-agent
published: 2026-05-20
fetched: 2026-11-17
type: docs
topics: [multi-agent, microsoft, orchestration, context]
summary: "Microsoft层级委派设计：主agent负责高层决定、专长agent执行；明确大请求/响应与强依赖流程的适用限制。日期为页面最后更新日。"
---

# Orchestrator and subagent multi-agent patterns

[Read in English](https://learn.microsoft.com/en-us/agents/architecture/multi-agent-orchestrator-sub-agent)
[Edit](https://learn.microsoft.com/en-us/agents/architecture/multi-agent-orchestrator-sub-agent)

---

---

Note

Access to this page requires authorization. You can try [signing in](https://learn.microsoft.com/en-us/agents/architecture/multi-agent-orchestrator-sub-agent) or changing directories.

Access to this page requires authorization. You can try changing directories.

A primary orchestrator delegates tasks to a set of subordinate specialist agents. These specialist subagents can be "child agents" managed within the same solution, or external "connected agents" (standalone agents that different teams or business units own and maintain).

This hierarchical pattern is ideal for clear separation of concerns. For example, a Sales Copilot agent might orchestrate one agent for lead scoring and another for generating proposals. The orchestrator manages the overall user conversation and high-level decisions ("do we need to involve another agent?"), while subagents focus on execution.

Use this pattern (also referred to as "Russian doll" or [magentic](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns#magentic-orchestration) patterns) when the top-down solution can be naturally broken into domains or functional areas. It's especially useful when modularity, independent ownership, or reuse is important. This approach creates a simpler user experience with one entry point, while using multiple agents optimized for quality and reliability for their targeted domain or function.

Use this pattern when:

- The use case is open-ended with no predetermined process flow.
- Specialist agents are already available and optimized for reuse or explicitly needed to provide tuned or specialized quality for the use case.
- The use case tolerates or benefits from "spray and pray" approaches, where a single success justifies all prior failed attempts.

Example use cases include vibe coding, red teaming, and modeling potential new vaccines or chemical compounds. This pattern also works well when the user is educated to generate several responses and selects the best result for further evaluation or refinement.

Don't use this pattern when:

- The use case requires a consistent success rate (compliance or Q&A use cases).
- The process includes well-defined steps and strong hierarchical dependencies.
- The process is time-sensitive and can't tolerate waiting for failed plans or responses to retry.
- The component agents require long response windows or require large request and response sizes that exceed the limitations of the primary orchestrator.

Learn more about [magentic orchestration](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns#magentic-orchestration).

---

## Feedback

Was this page helpful?

No

Need help with this topic?

Want to try using Ask Learn to clarify or guide you through this topic?

---

## Additional resources

---

- Last updated on 
  2026-05-20
