---
title: "Emerging trends in AI agent evaluation"
url: https://www.normaltech.ai/p/new-paper-emerging-trends-in-ai-agent
published: 2026-10-19
fetched: 2026-11-11
type: engineering-blog
topics: [evaluation, normaltech]
summary: "轨迹、人与Agent交互、制度影响是不同评价层次。"
---

# Emerging trends in AI agent evaluation

*By Felix Chen, Stephan Rabanser, Sayash Kapoor, and Arvind Narayanan. See the full author list and affiliations [here](https://sage.cs.princeton.edu/trends/).*

There are [growing calls](https://aievaluatorforum.org/initiatives/embedded-evaluation-letter) for independent and embedded AI evaluation, especially of AI agents. But much remains unclear: what constitutes a “good” evaluation, what needs to be evaluated in the first place, and how best to coordinate and support the influx of people entering the burgeoning evaluation ecosystem.

Our group at Princeton has been working to improve the state of AI agent evaluation for about [three years](https://arxiv.org/abs/2407.01502). We teamed up with people who’ve done foundational work on evaluation at Stanford, the UK AI Security Institute, and Brookings. **Our [paper](https://rabanser.dev/assets/papers/emerging-trends-paper.pdf) is titled Emerging Trends in AI Agent Evaluation.** We synthesized the trends we see across three dimensions—the science and methods, the research agenda, and the evaluation ecosystem—with the goal to help those who are upskilling for this new paradigm. We also aim to equip evaluators, funders, and the public with a set of questions to ask, and provide actionable recommendations.

[![](https://substackcdn.com/image/fetch/$s_!B9sr!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fdf3d3b4a-b29e-4214-9e4b-b1c17d8acbd9_3188x1830.png)](https://substackcdn.com/image/fetch/$s_!B9sr!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fdf3d3b4a-b29e-4214-9e4b-b1c17d8acbd9_3188x1830.png)

Thirty-three emerging trends in AI agent evaluation. (Figure from the [paper](https://rabanser.dev/assets/papers/emerging-trends-paper.pdf).)

## Challenges for agents, new and old

AI developers have long made claims about the real-world performance of their systems based on benchmark scores. It is harder now to assess whether the evidence gathered supports claims made about agents. The evaluator must scrutinize the entire trajectory, not just the final outcome. It is important, for example, to know if agents took shortcuts, particularly since they have access to tools and environments. And when agents perform better or worse, it is harder to attribute these changes to different components of the agent. Addressing these concerns requires significant engineering effort, and the work is getting increasingly expensive—for example, several agents on the ExploitBench benchmark [cost](https://exploitbench.ai/) tens of thousands of dollars in credits to evaluate. These numbers also don’t factor in the significant engineering effort needed to set up and maintain the evaluation infrastructure itself.

[![](https://substackcdn.com/image/fetch/$s_!_h3_!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F770ee50d-b62a-41be-8d69-07843214513d_3681x1515.png)](https://substackcdn.com/image/fetch/$s_!_h3_!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F770ee50d-b62a-41be-8d69-07843214513d_3681x1515.png)

Agent evaluation is much more complex than model evaluation. (Figure from the [paper](https://rabanser.dev/assets/papers/emerging-trends-paper.pdf).)

Faced with the massive volume of traces that agents generate, evaluators are also struggling to inspect and monitor these agents at scale. The tools evaluators rely on today to do this work are not foolproof—and themselves require evaluation. To investigate the recent OpenAI-HuggingFace incident after the fact, evaluators [relied upon](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/) other agents to look for and identify instances of harmful action, an approach they acknowledged carried its own limitations and biases.

Because agents are deployed in dynamic settings (and increasingly together with other agents), it is harder to design good metrics to capture the underlying concepts of interest, and create valid conditions to implement them. Addressing these challenges will require better tools, more rigorous benchmarks, and experimentation with different approaches and formats, such as through [open-world evaluations](https://www.normaltech.ai/p/open-world-evaluations-for-measuring) and growing observational data on real-world usage.

## The scope of evaluation needs is growing

[![](https://substackcdn.com/image/fetch/$s_!BJOH!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F9e0027ce-11bc-4ab9-9812-dfb26c5f4543_2204x1476.png)](https://substackcdn.com/image/fetch/$s_!BJOH!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F9e0027ce-11bc-4ab9-9812-dfb26c5f4543_2204x1476.png)

Evidence about agents is needed to understand their effects at different layers, but does not always translate across layers. (Figure from the [paper](https://rabanser.dev/assets/papers/emerging-trends-paper.pdf).)

Crucially, the results of evaluation at one level of scope are not guaranteed to translate to another. An agent might demonstrate capability in the lab, but face limits when placed in a specific use case. Consider METR’s randomized controlled trial which found that, despite expectations, usage of agent tools toward software development actually *[increased](https://arxiv.org/abs/2507.09089)* overall completion time on the tasks at hand. Agents may be able to perform certain tasks, but how that capability translates for humans in the real world requires evaluation in context. An expanded research agenda is therefore needed to understand agents at each level: their capabilities, their interactions with humans, and their impact on institutions and incentive structures. This work requires both technical and sociotechnical evaluation to study not just the agent itself but the agent(s) in context.

Across these different layers, evaluators have a choice in framing the questions they ask and the findings they generate. Can an agent *automate* a task or process? Or, can an agent *augment* the work of a human? These are two complementary lenses. If evaluation largely focuses on how agents automate certain tasks, we will better understand where and how human work can be replaced. But it won’t tell us how humans can better collaborate using agents, or how agents can improve human work.

## Who gets to evaluate and how?

This expanded research agenda will require an expanded set of evaluators from a mix of disciplines. It will also require that evaluators have the freedom to choose which questions to pursue and how. When evaluators with different approaches agree, we might gain greater confidence in those results. And when they conflict, evaluators can identify vague definitions and limitations to their findings.

Who gets to participate, and with what independence, will shape the questions evaluators ask and the methods they use. Meaningful independence is influenced by several factors. As the costs of frontier evaluation keep increasing, the ability of independent evaluators to participate will be increasingly determined by their access to increased funding. Whether independent evaluators have [sufficient access](https://www.anthropic.com/claude-fable-and-mythos-5-1) to models also impacts their ability to measure and assess the true frontier. Questions of access now also extend to Chain of Thought traces for agents, since frontier labs now release summarized versions instead of raw traces. Alongside these challenges, evaluators also need to navigate whether they can conduct work without fear of retaliation, and how they can transparently share their findings.

## Where do we go from here?

There is a clear window now to bring in new participants, methods, and ideas for agent evaluations, and to meet the pressing need for rigorous evidence in a fast-moving space. We hope this paper gives readers an emerging sense of the field’s direction. There are many steps that stakeholders in the AI evaluation community can take to advance the science and practice of AI evaluation.

*For prospective evaluators*, there is a need to determine what roles or questions within this ecosystem best fit their expertise, and examine which dimensions of independence are required for that work. In particular, we encourage participation from disciplines not yet engaged in AI evaluation; there are many open challenges that can benefit from their perspectives.

*For current evaluators*, there is an opportunity to examine their own methodological assumptions and embrace perspectives from other disciplines; this field of agent evaluation is inherently interdisciplinary, and will necessarily involve some rediscovery and reinvention of existing ideas and insights.

*For field-builders*—funders, coalitions, and conference organizers—agent evaluation demands its own field of practice, one with higher standards for validity and rigor. Raising this bar can happen by coalescing best practices and fostering conversation and engagement between different disciplinary perspectives.

*For leaderboard aggregators,* who are central to this emerging ecosystem by shaping which dimensions of evaluation receive attention and in what manner, there is a prime opportunity to incorporate best practices around reporting for downstream adoption, and to help the public understand the rising costs of evaluation.

*For deployers and industry evaluators,* there is a critical gap for real-world settings to inform evaluation work. By contributing on-the-ground insights and engaging with work in the lab, they can strengthen the discourse in this fast-moving space.

*For labs*, there is an opportunity to build bridges with independent evaluators and examine the community’s best practices. Successful embedded evaluators will require public legitimacy through independence, transparency, and methodological rigor.

*For policymakers,* there is a need to develop a clear sense of the current ecosystem and what good evaluations should look like. And for public sector deployments, evaluation needs to be an integrated and continuous part of the process from day one. AISIs can play a key role by pioneering new models for collaboration and inviting new stakeholders into their public input mechanisms within the current ecosystem.

*Read the paper [here](https://rabanser.dev/assets/papers/emerging-trends-paper.pdf).*