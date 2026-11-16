---
title: "Open and Emergent Problems in Agentic Privacy and Security: A Contextual Angle"
url: https://research.google/blog/open-and-emergent-problems-in-agentic-privacy-and-security-a-contextual-angle/
published: 2026-10-05
fetched: 2026-11-11
type: engineering-blog
topics: [reliability-security, google, context, security]
summary: "Google研究者将Contextual Integrity应用于agent：信息发出者、接收者、数据类别和传播条件共同确定具体行为是否适当。"
---

# Open and Emergent Problems in Agentic Privacy and Security: A Contextual Angle

![A system diagram of an AI agent architecture detailing its internal components, behavioral expectations, and its interactions with users and different external contexts.](https://storage.googleapis.com/gweb-research2023-media/original_images/PrivacySecurity_ContextualAngle2-ModelOverview.png)

October 5, 2026

Eugene Bagdasarian, Research Scientist, and Marco Gruteser, Principal Scientist, Google Research

To be useful, AI agents must understand and be constrained by contextual behavioral norms to ensure they act appropriately. Inspired by the theory of Contextual Integrity, our new workshop report outlines key open research directions across system, model, and user levels to build AI agents users can trust.

## Quick links

- [Technical report](https://research.google/pubs/open-and-emergent-problems-in-agentic-privacy-and-security-a-contextual-angle/)

We're rapidly transitioning to a computing landscape defined by highly general, increasingly [autonomous agents](https://cloud.google.com/discover/what-are-ai-agents). Driven by large language models (LLMs) that can dynamically generate plans and invoke external tools, these systems offer the potential for AI to seamlessly handle complex, multi-step tasks on our behalf. However, realizing this potential requires solving a key challenge: enabling agent capability while ensuring that agents act appropriately.

Today, we share a comprehensive new workshop report, "[Open and Emergent Problems in Agentic Privacy and Security: A Contextual Angle](https://research.google/pubs/open-and-emergent-problems-in-agentic-privacy-and-security-a-contextual-angle/)," the result of a collaborative effort bringing together more than 50 academic and industry leaders from numerous institutions. We met at the Google Contextual Agent Privacy and Security (CAPS) Workshop, held in late 2025 in New York City. In this report, you’ll find a breakdown of foundational privacy and security challenges that autonomous agents face today, needing coordinated defenses at the system, model, user, and ecosystem levels.

## Agentic trade-offs

The core challenge of agentic AI is that, for an agent to be useful, it may need to have access to personal data *and* the ability to take consequential actions across a broad range of contexts. However, this access together with agents’ behavioral flexibility requires meaningfully different approaches from those used in traditional software. Unlike traditional deterministic software, agents differ in three critical dimensions that lead to challenges the research community must address together:

- **Unstructured interfaces and input ambiguity**: Agents process instructions in formats like natural language and images, which makes it difficult to define "expected behavior" or protect against adversarial manipulations like [prompt injection](https://en.wikipedia.org/wiki/Prompt_injection).
- **Probabilistic control flows**: Generative planning leads to probabilistic execution paths that traditional testing methodologies can’t easily secure.
- **Autonomy and delegation**: As agents handle longer tasks and delegate sub-tasks to other agents, traditional user oversight becomes less effective and likely insufficient, risking "confirmation fatigue".

![A diagram illustrating three AI security challenges: input ambiguity via prompt injection, non-deterministic control flows, and autonomy and delegation.](https://storage.googleapis.com/gweb-research2023-media/images/PrivacySecurity_ContextualAngle1-Challenges.width-1250.png)

*Agentic AI privacy and security challenges.*

## The contextual lens

Given that useful agents may need to share data and complete tasks, we believe that the future of trustworthy agents depends on their ability to reason about, understand, and be constrained by the social norms and appropriateness of their actions— for the *specific context* in which they operate.

But how do we teach an agent to understand "context" and appropriateness? Our report is grounded in the theory of [Contextual Integrity](https://nissenbaum.tech.cornell.edu/papers/Contextual%20Integrity%20Up%20and%20Down.pdf) (CI), which defines privacy not just as secrecy or control, but as "appropriate information flow" according to established and justifiable social norms. A context-specific informational norm is defined by its *actors* (who is sending and receiving information about whom), the *types of information* (specific categories of information, like medical or financial records), and *transmission principles* (the rules governing the flow, like confidentiality or reciprocity). For example, you might be willing to share your gift shopping list with a virtual shopping assistant, but not your family and friends. Our report extends and generalizes contextual integrity for information sharing to contextual security, that is the *appropriateness* of agent actions. By anchoring agent privacy and security in CI, we explore how we can design systems that evaluate whether an action is socially and contextually appropriate before executing it.

![A system diagram of an AI agent architecture detailing its internal components, behavioral expectations, and its interactions with users and different external contexts.](https://storage.googleapis.com/gweb-research2023-media/images/PrivacySecurity_ContextualAngle2-ModelOvervie.width-1250.png)

*Model of a general AI agent interacting with other users, tools, and agents across contexts.*

## Operationalizing Contextual Integrity

For the first time since the development of the theory of Contextual Integrity, LLMs provide an opportunity to create machine readable policy that is truly context dependent. There has historically been a semantic gap between high-level contextual norms and low-level system permissions. For example, “protect my data while organizing my travel for a conference” requires specific instructions on what user information is appropriate to share when booking flights, applying for visas, and communicating with organizers.

Traditional methods like manual permissions or expert-written policies cannot scale to a future with AI agents autonomously performing multiple complex, long-running tasks. As language models begin to [understand CI](https://openreview.net/pdf?id=l9rATNBB8Y), we argue that this gap can be bridged. Our report advocates for complementing model and user interaction advances with a contextual policy engine that forms part of a supervisor layer to monitor and enforce the appropriateness of actions. This policy engine includes a dynamic policy generation loop that can operate in real time (illustrated below) to tailor policies to the user request and open-ended, dynamic contexts, including new tools and capabilities that might be discovered at runtime. This allows the system to evaluate whether a requested data flow is appropriate before any information leaves the user's workspace.

![A flowchart demonstrating a contextual policy architecture where an AI agent's proposed actions are evaluated by a policy engine before being executed by external tools.](https://storage.googleapis.com/gweb-research2023-media/images/PrivacySecurity_ContextualAngle3-ContextualPo.width-1250.png)

*An illustrative example of how a contextual policy engine architecture could be instantiated within an agentic system.*

## Multi-layered approach to agentic privacy and security

Working towards contextual policy engines together with necessary advances at the model- and user-level results in a multi-layered approach. Our report outlines opportunities for innovation across the entire stack:

- **System-level sandboxing**: The execution environment can impose additional guardrails to limit the impact of agent or model failures and facilitate detection and response. Traditional operating systems sandbox applications by statically limiting access, say to files or networks. For agents, we explore dynamically limiting agentic capabilities, establishing agent identity, and authorizing or revoking access to data based on changes in context.
- **Model-level reasoning**: An agent performing complex tasks has to judge the appropriateness of its actions, such as sharing user data. Future research should enable models to disambiguate under-specified user prompts and reason about appropriateness under changing contextual norms.
- **User-centric controls**: The traditional “Notice and Choice” framework assumes that individuals can make fine-grained decisions about actions affecting personal data and relies on an assumption of foreseeability. However, autonomous agents’ behavior is inherently probabilistic, high volume, and generative. We explore shifting interfaces towards dynamic, contextual, and personalized control mechanisms consistent with user mental models.
- **Multi-agent interactions**: So that AI agents can safely collaborate with each other on complex tasks we need to develop effective guardrails to prevent the agents from colluding and violating contextual norms.
- **Ecosystem governance**: We explore challenges in governance mechanisms to arrive at a set of contextual norms that are collected and shared across agents. Furthermore, as norms can differ across domains and entities we need mechanisms that allow us to resolve conflicts, negotiate norm changes, and verify compliance.

## Measuring privacy and security dynamically

Finally, we propose the development of new approaches to safety evaluations that more directly apply to highly autonomous, multi-agent systems. Our report highlights the need for standardized, multi-agent benchmarks — dynamic "Agent Gym" environments where researchers can safely simulate complex, cascading interactions during extended periods. With these open-source sandboxes, we can establish a robust, shared privacy, security, and safety baseline across academia and industry.

## A call to action

This is an ambitious project, but a safe, secure, and trustworthy agentic ecosystem is too large a task for any single discipline, organization or sector. Calling for new ideas and unprecedented collaborations, the report lays out foundational opportunities; it is a call to action for the broader research community across academia, government, civil society, and industry to develop the contextual foundations necessary for a safe, secure, and privacy-respecting ecosystem. We invite you to read the [technical report](https://research.google/pubs/open-and-emergent-problems-in-agentic-privacy-and-security-a-contextual-angle/).

## Acknowledgements

*We would like to thank Lillian Tsai for serving as co-primary author and Sarah de Haas for coordinating the workshop, report writing, and blogpost. Kassem Fawaz, Stefan Mellem, Helen Nissenbaum, and Nina Taft contributed to conceptualization, writing across multiple sections, and guided the writing process. Sebastian Benthall, Madiha Zahrah Choksi, Seliem El-Sayed, Ferdinando Fioretto, Adrià Gascón, Ashish Hooda, Ivan Petrov, Francesco Pinto, Octavian Suciu, Trishita Tiwari, Harold Triedman, Ren Yi, and Wen Zhang served as section leads. We are grateful for the contribution by the over 50 researchers, academic partners, and industry leaders who co-authored the report or participated in workshop discussions. This work was supported by Daniel Ramage, Corinna Cortes, Yossi Matias, Pushmeet Kohli, Hank Levy, Raluca Ada Popa, Amanda Walker, Brendan McMahan, and James Manyika. Eugene Bagdasarian is also* an Assistant Professor at University of Massachusetts Amherst.

- Labels:
- [Generative AI](https://research.google/blog/label/generative-ai)
- [Natural Language Processing](https://research.google/blog/label/natural-language-processing)
- [Security, Privacy and Abuse Prevention](https://research.google/blog/label/security-privacy-and-abuse-prevention)

## Quick links

- [Technical report](https://research.google/pubs/open-and-emergent-problems-in-agentic-privacy-and-security-a-contextual-angle/)

×
❮
❯

![Privacy&Security_ContextualAngle2-ModelOverview](https://storage.googleapis.com/gweb-research2023-media/original_images/PrivacySecurity_ContextualAngle2-ModelOverview.png)

A system diagram of an AI agent architecture detailing its internal components, behavioral expectations, and its interactions with users and different external contexts.

![Privacy&Security_ContextualAngle1-Challenges](https://storage.googleapis.com/gweb-research2023-media/original_images/PrivacySecurity_ContextualAngle1-Challenges.png)

A diagram illustrating three AI security challenges: input ambiguity via prompt injection, non-deterministic control flows, and autonomy and delegation.

![Privacy&Security_ContextualAngle3-ContextualPolicy](https://storage.googleapis.com/gweb-research2023-media/original_images/PrivacySecurity_ContextualAngle3-ContextualPolicy.png)

A flowchart demonstrating a contextual policy architecture where an AI agent's proposed actions are evaluated by a policy engine before being executed by external tools.
