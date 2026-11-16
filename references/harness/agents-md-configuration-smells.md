---
title: "Configuration Smells in AGENTS.md Files"
url: https://arxiv.org/abs/2606.15828
fetched: 2026-09-28
type: paper
topics: [harness, agents-md, checklist]
summary: "从文件样本归纳的 AGENTS.md 配置问题，可转成审查清单。"
---

# Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents

Hélio Victor F. dos Santos
Affiliation: Department of Computer Science
  
Federal University of Minas Gerais
  
Belo Horizonte, Minas Gerais, Brazil
  
helio.santos@dcc.ufmg.br
  
Vitor Costa
Affiliation: Department of Computer Science
  
Federal University of Minas Gerais
  
Belo Horizonte, Minas Gerais, Brazil
  
vitorcosta@dcc.ufmg.br
  
João Eduardo Montandon
Affiliation: Department of Computer Science
  
Federal University of Minas Gerais
  
Belo Horizonte, Minas Gerais, Brazil
  
joao@dcc.ufmg.br
Affiliation: 

  
Luciana Lourdes Silva
Affiliation: Department of Computing
  
Federal Institute of Minas Gerais
  
Ouro Branco, Minas Gerais, Brazil
  
luciana.lourdes.silva@ifmg.edu.br
  
Marco Tulio Valente
Affiliation: Department of Computer Science
  
Federal University of Minas Gerais
  
Belo Horizonte, Minas Gerais, Brazil
  
mtov@dcc.ufmg.br

## Abstract

Coding agents are increasingly used to automate software engineering tasks. To guide their behavior, these agents commonly rely on configuration files, typically named AGENTS.md or CLAUDE.md, which provide instructions about architecture, workflows, coding conventions, and testing practices. Despite their growing importance, little is known about common problems affecting the definition and maintenance of these files. In this paper, we present the first catalog of smells for coding-agent configuration files. To identify such smells, we first conducted a grey literature review and a repository mining analysis. As a result, we identified six configuration smells and proposed automated heuristics to detect them.
To evaluate the prevalence of the proposed smells, we analyzed 100 popular open-source repositories containing either an AGENTS.md or a CLAUDE.md file. Our results show that configuration smells are widespread. Lint Leakage was the most common smell, affecting 62% of the files, followed by Context Bloat (42%) and Skill Leakage (35%). We further show that several smells frequently co-occur, particularly Context Bloat, Skill Leakage, and Conflicting Instructions.

## I Introduction

Large Language Models (LLMs) are transforming the way software is developed by automating a wide range of software engineering tasks. For example, LLMs can assist developers with code generation [[5](https://arxiv.org/html/2606.15828#bib.bib13), [27](https://arxiv.org/html/2606.15828#bib.bib9)], bug fixing [[15](https://arxiv.org/html/2606.15828#bib.bib12)], test creation [[28](https://arxiv.org/html/2606.15828#bib.bib11), [3](https://arxiv.org/html/2606.15828#bib.bib10)], code review [[14](https://arxiv.org/html/2606.15828#bib.bib35)], documentation writing [[9](https://arxiv.org/html/2606.15828#bib.bib31), [11](https://arxiv.org/html/2606.15828#bib.bib1)], software migration [[2](https://arxiv.org/html/2606.15828#bib.bib32), [36](https://arxiv.org/html/2606.15828#bib.bib34)], and code smell detection [[29](https://arxiv.org/html/2606.15828#bib.bib8)]. Initially, these capabilities were delivered through coding assistants that interactively support developers while they write code. For example, this was the case with the first version of GitHub Copilot, launched in 2021. More recently, however, automation has advanced with the emergence of coding agents, such as Claude Code11
1
https://claude.com/product/claude-code, Codex22
2
https://openai.com/codex/, Cursor Agent33
3
https://cursor.com/agents, and Gemini CLI44
4
https://ai.google.dev/gemini-api/docs, which can execute complex tasks with limited intervention.

Coding agents are designed to operate autonomously. Given a high-level goal, they can plan and execute multiple actions until the requested task is completed. Architecturally, a coding agent can be viewed as a combination of a language model and a harness. The language model provides reasoning and inference capabilities, while the harness implements an agentic loop that repeatedly interacts with the model, executes actions, and feeds the results back to the model. During this loop, agents can invoke a variety of external tools, including code search utilities, shell commands, test runners, version-control systems, web search engines, and issue-tracking platforms.

To guide their behavior, coding agents commonly rely on project-specific configuration files, typically named AGENTS.md or CLAUDE.md. These files contain instructions that complement the agent’s built-in capabilities, such as coding conventions, architectural guidelines, testing requirements, project workflows, and domain-specific knowledge. Their main purpose is to provide persistent contextual information that helps agents behave consistently across different tasks and sessions. In most agent harnesses, the configuration files are loaded when a session starts, incorporated into the agent’s prompt, and maintained as part of the context available throughout the execution of the agentic loop.

Given their importance for the performance of coding agents, in this paper we present a catalog of smells commonly found in agent configuration files. To identify these smells, we conducted a review of the grey literature, covering 14 recent articles on the topic. As a result, we identified six smells that may occur in these files and, consequently, impair the overall performance of coding agents. We then used a set of heuristics to detect these smells in a dataset of 100 popular open-source projects containing either an AGENTS.md or a CLAUDE.md file. In total, we identified 207 instances of the proposed smells. The most common smell was Lint Leakage, with 62 identified instances. This smell refers to instructions in configuration files that essentially restate rules already enforced by automated tools such as linters and formatters, thus unnecessarily consuming context space and tokens.
We also analyzed the co-occurrence of smells in our dataset and discovered several strong relationships. For example, two smells (Skill Leakage and Conflicting Instructions) increase the likelihood of Context Bloat by 83%.
These results are important because they allow us to understand which smells can trigger the appearance of others in configuration files.

The remainder of this paper is organized as follows. Section [II](https://arxiv.org/html/2606.15828#S2 "II Coding Agents Configuration Files ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents") provides background on the role and importance of configuration files in agentic development. Section [III](https://arxiv.org/html/2606.15828#S3 "III Methods ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents") details our study design and methods, which included a grey literature review, the creation of a dataset of real-world agent configuration files, and a manual analysis of pull requests involving changes to such files. Section [IV](https://arxiv.org/html/2606.15828#S4 "IV Configuration Smells ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents") describes the configuration smells that can occur in agent configuration files, i.e., the proposed catalog. Next, Section [V](https://arxiv.org/html/2606.15828#S5 "V Detection Heuristics ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents") defines the heuristics used to detect these smells, and Section [VI](https://arxiv.org/html/2606.15828#S6 "VI Configuration Smells in the Wild ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents") reports their occurrence in our dataset. Section [VII](https://arxiv.org/html/2606.15828#S7 "VII Co-Occurrence Analysis ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents") then investigates co-occurrence relationships among the identified smells. Finally, Section [VIII](https://arxiv.org/html/2606.15828#S8 "VIII Threats to Validity ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents") discusses threats to validity, Section [IX](https://arxiv.org/html/2606.15828#S9 "IX Related Work ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents") reviews related work, and Section [X](https://arxiv.org/html/2606.15828#S10 "X Conclusion ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents") concludes the paper.

## II Coding Agents Configuration Files

While the effectiveness of coding agents is heavily dependent on the capacity of the underlying model, it is equally restricted by the harness used for task execution. In this scenario, agent configuration files—such as AGENTS.md and CLAUDE.md—emerge as a standard for context injection and for providing a persistent memory for coding agents. According to [Xi et al. [35]](https://arxiv.org/html/2606.15828#bib.bib2), the effectiveness of an agent lies not only in the power of the base model but in the precision with which guidelines are defined, stored, and retrieved.

In essence, AGENTS.md is a markdown file with rules about the project.
In this file, one can add information regarding system architecture, tool documentation, testing practices, and other constraints whose absence might lead to agent errors.
In a recent study, [Santos et al. [25]](https://arxiv.org/html/2606.15828#bib.bib5) indicate that the most common sections in these files cover architecture, development rules, project overviews, and testing workflows.

Upon starting a session, the agent detects the presence of AGENTS.md files in the project directory and incorporates their content into the agent’s prompt, persisting this context throughout the entire agentic loop [[16](https://arxiv.org/html/2606.15828#bib.bib3)].
An example of a configuration file can be seen in Figure [1](https://arxiv.org/html/2606.15828#S2.F1 "Fig. 1 ‣ II Coding Agents Configuration Files ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").55
5
This example was extracted and adapted from https://agents.md This file includes a commands section for project setup, project-specific code style rules, and workflow definitions for the model.

[⬇](data:text/plain;base64,IyBBR0VOVFMubWQKCiMjIFNldHVwIGNvbW1hbmRzCi0gSW5zdGFsbCBkZXBzOiBgcG5wbSBpbnN0YWxsYAotIFN0YXJ0IGRldiBzZXJ2ZXI6IGBwbnBtIGRldmAKLSBSdW4gdGVzdHM6IGBwbnBtIHRlc3RgCgojIyBDb2RlIHN0eWxlCi0gVHlwZVNjcmlwdCBzdHJpY3QgbW9kZQotIFVzZSBmdW5jdGlvbmFsIHBhdHRlcm5zIHdoZXJlIHBvc3NpYmxlCi0gVXNlIEVTIG1vZHVsZXMgKGltcG9ydC9leHBvcnQpIHN5bnRheCwgbm90IENvbW1vbkpTIChyZXF1aXJlKQoKIyMgV29ya2Zsb3cKLSBCZSBzdXJlIHRvIHR5cGVjaGVjayB3aGVuIHlvdSdyZSBkb25lIG1ha2luZyBhIHNlcmllcyBvZiBjb2RlIGNoYW5nZXMKLSBQcmVmZXIgcnVubmluZyBzaW5nbGUgdGVzdHMsIGFuZCBub3QgdGhlIHdob2xlIHRlc3Qgc3VpdGUsIGZvciBwZXJmb3JtYW5jZQo=)

## AGENTS.md

## Setup commands

- Install deps: ‘pnpm install‘

- Start dev server: ‘pnpm dev‘

- Run tests: ‘pnpm test‘

## Code style

- TypeScript strict mode

- Use functional patterns where possible

- Use ES modules (import/export) syntax, not CommonJS (require)

## Workflow

- Be sure to typecheck when you’re done making a series of code changes

- Prefer running single tests, and not the whole test suite, for performance

Fig. 1: Example of AGENTS.md file

The first version of the AGENTS.md file can be created automatically by the agent itself.
In this case, a specific command—generally /init---relies on an internal prompt instructing the agent to inspect the repository and leverage an initial set of guidelines.
For example, the prompt used by the OpenAI Codex---which is publicly available66
6
https://github.com/openai/codex/blob/main/codex-rs/tui/prompt_for_init_command.md—asks the agent to summarize the project structure and module organization, build and testing commands, coding and naming conventions, testing guidelines, and pull request requirements, while keeping the resulting document concise, instructional, and tailored to the analyzed repository.

It is also possible to use both files in the same repository. In this case, one file should simply point to the other one. For example, the CLAUDE.md file may exist but contain only the following line: read AGENTS.MD.

Note: Most agent-based systems use the name AGENTS.md for their configuration files. The notable exception is Claude Code, which uses the name CLAUDE.md. Therefore, in this paper, we analyze both AGENTS.md and CLAUDE.md files, since the only difference between them, in terms of purpose and role within an agent-based system, is their name.

## III Methods

To research the smells that affect agent configuration files, we employed three methods: a grey literature review (Section [III-A](https://arxiv.org/html/2606.15828#S3.SS1 "III-A Literature Review ‣ III Methods ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents")), the creation of a dataset of real-world agent configuration files (Section [III-B](https://arxiv.org/html/2606.15828#S3.SS2 "III-B Dataset of Agent Configuration Files ‣ III Methods ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents")), and an analysis of discussions conducted in pull requests (Section [III-C](https://arxiv.org/html/2606.15828#S3.SS3 "III-C Pull Requests Analysis ‣ III Methods ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents")).

### III-A Literature Review

Grey literature review is commonly used in software engineering research to gather information for emerging topics, since it emphasizes the inclusion of non-academic sources, such as blog posts, technical reports, and documentation [[8](https://arxiv.org/html/2606.15828#bib.bib4)].
Our procedure is depicted in Figure [2](https://arxiv.org/html/2606.15828#S3.F2 "Fig. 2 ‣ III-A Literature Review ‣ III Methods ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents") and consists of three main steps: (a) Google search, (b) Document selection, and (c) Data extraction and validation.

![Refer to caption](https://arxiv.org/html/2606.15828v5/methodology_crawler.png)

Fig. 2: Overview of the grey literature steps

Document Search:
We started by performing a Google search to identify documents that describe bad practices or smells in AGENTS.md files.
Similar to other grey literature reviews, we restricted our search to Google due to its wide coverage and relevance for retrieving non-academic sources [[34](https://arxiv.org/html/2606.15828#bib.bib6), [24](https://arxiv.org/html/2606.15828#bib.bib33)].
Specifically, the search query, as presented in Figure [3](https://arxiv.org/html/2606.15828#S3.F3 "Fig. 3 ‣ III-A Literature Review ‣ III Methods ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents"), looked for documents containing the terms agents.md or claude.md together with terms related to bad smells, anti-patterns, and best practices.

[⬇](data:text/plain;base64,ICAoImFnZW50cy5tZCIgT1IgIkFHRU5UUy5tZCIgT1IgImNsYXVkZS5tZCIgT1IgIkNMQVVERS5tZCIpCiAgQU5ECiAgKCJiYWQgc21lbGwiIE9SICJiYWQgc21lbGxzIiBPUiAiYW50aS1wYXR0ZXJuIiBPUiAiYW50aS1wYXR0ZXJucyIgT1IgImFudGlwYXR0ZXJuIiBPUiAiYW50aXBhdHRlcm5zIiBPUiAiYmFkLXByYWN0aWNlIiBPUiAiYmFkLXByYWN0aWNlcyIgT1IgImJhZCBwcmFjdGljZSIgT1IgImJhZCBwcmFjdGljZXMiIE9SICJiZXN0LXByYWN0aWNlcyIgT1IgImJlc3QgcHJhY3RpY2UiIE9SICJiZXN0IHByYWN0aWNlcyIp)

("agents.md" OR "AGENTS.md" OR "claude.md" OR "CLAUDE.md")

AND

("bad smell" OR "bad smells" OR "anti-pattern" OR "anti-patterns" OR "antipattern" OR "antipatterns" OR "bad-practice" OR "bad-practices" OR "bad practice" OR "bad practices" OR "best-practices" OR "best practice" OR "best practices")

Fig. 3: Search string used in the literature review

Document Selection:
Our search returned 532,000 documents.
From these results, we manually analyzed the first 30 documents returned by the search; i.e., the ones returned in the first three pages.
The first author discarded 16 documents according to the following criteria:
(a) five documents were accessible only through subscription or paywall;
(b) four documents were out of scope, i.e., focused on specific tools or other topics;
(c) three represented discussion threads on forums;
(d) three documents did not explain any bad smell or best practice on AGENTS.md files, they only listed these issues pointing to the official documentation of the tools; and
(e) one document was written in a non-English language.
As a sanity check, the third author analyzed each discarded document to confirm the reason for exclusion; no disagreements were found in this process.
The remaining 14 documents were selected for the next step. We also assessed the quality and reputation of the authors of all selected documents. Six documents were published by well-known companies, such as Anthropic and GitHub. The remaining eight documents were written by authors with relevant expertise in the field (seven authors have at least six years of experience, and one author has two years). Furthermore, three of the articles were extensively discussed on Hacker News (a well-known forum for technology and startup discussions), receiving at least 140 upvotes each. Throughout this paper, we refer to these documents using the identifier $D_{n}$, where $n$ is a numeric identifier. The list of selected documents is available in our replication package.

Smells Extraction and Validation:
For each selected document, the first author thoroughly read its content and marked any sentence that described practice to avoid when creating AGENTS.md files.
Following this initial extraction, the second author reviewed the annotations as a sanity check to confirm whether they actually describe a bad smell. This process revealed four disagreements, which both authors discussed to reach a consensus. After this annotation process, the first and last authors manually grouped sentences describing similar smells and proposed a name and a short description for each group. They also decided to discard one smell that is not specific to coding agents: exposing secret keys in configuration files. At the end, we obtained a list of six smells.

### III-B Dataset of Agent Configuration Files

To investigate whether the smells actually occur in real projects, we created a dataset with 100 agent configuration files, including 39 AGENTS.md and 61 CLAUDE.md files. We selected these files using the following steps.
In January 2026, we used the GitHub Search API to find repositories containing either AGENTS.md or CLAUDE.md in their root folder.
Next, we manually removed from this list repositories that are not applications, e.g., awesome lists and tutorials. From the remaining ones, we selected the top-100 repositories with the highest number of stars.
For example, our dataset of selected GitHub projects includes n8n-io/n8n (a workflow automation platform)77
7
https://github.com/n8n-io/n8n, langchain-ai/langchain (an agent engineering platform)88
8
https://github.com/langchain-ai/langchain, and vercel/ai (an AI Toolkit for TypeScript).99
9
https://github.com/vercel/ai

### III-C Pull Requests Analysis

After creating the dataset of files described in the previous section, we decided to inspect the Pull Requests (PRs) of the corresponding projects to determine whether they contained discussions about potential issues in agent configuration files. Such issues could help expand the list of six smells identified through our grey literature review. Next, we explain how the pull requests were selected and analyzed.

Pull Requests Selection:
We collected all commits associated with each of the 100 configuration files in our dataset, including modifications, additions, and deletions.
This process yielded an initial dataset composed of 760 commits.
From this initial dataset, we selected only the ones linked to pull requests, resulting in a total of 383 pull requests.

A manual inspection was then performed on the conversation history of each filtered pull request to check whether the ongoing discussions about the target files, CLAUDE.md and AGENTS.md, were in fact of substantive relevance. We discarded all PRs that met any of the following exclusion criteria:
(a) conversations consisting entirely of bot-generated messages;
(b) threads where human participants interacted exclusively with bots;
(c) discussions that failed to actively engage with or reference the AGENTS.md or CLAUDE.md files;
(d) PRs containing only the initial opening description without any subsequent discussion or peer review.
The application of these sequential filters yielded a final corpus of 17 relevant pull requests.

Pull Requests Analysis: After analyzing the 17 pull requests, we found discussions about configuration-related problems in only two of them. These pull requests were labeled $PR_{1}$ and $PR_{2}$ and are also included in our replication package. However, the discussions concerned smells that had already been identified in the grey literature review. Therefore, our list remained unchanged, containing six smells. Although no new smells were discovered, the analysis of PRs was still valuable because it provided concrete examples of discussions about smells in agent configuration files, which we use to illustrate the content of Section [IV](https://arxiv.org/html/2606.15828#S4 "IV Configuration Smells ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").1010
10
As an additional note to this analysis, in six PRs, the goal was to consolidate agent-related documentation into a single file. For example, one PR was described as a pure rename of CLAUDE.md to AGENTS.md.

## IV Configuration Smells

Table [I](https://arxiv.org/html/2606.15828#S4.T1 "TABLE I ‣ IV Configuration Smells ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents") presents a list of the smells identified in our study.
The table also shows the identifiers of the articles in which these
smells were found. In the remainder of this section, we provide a description of the smells listed in this table.

TABLE I: Configuration Smells

| Smells | Articles and PRs |
| --- | --- |
| Context Bloat | $D_{1}$, $D_{3}$, $D_{4}$, $D_{5}$, $D_{6}$, $D_{9}$, $D_{11}$, $D_{12}$, $D_{13}$, $D_{14}$, $PR_{1}$ |
| Skill Leakage | $D_{2}$, $D_{3}$, $D_{4}$, $D_{5}$, $D_{6}$, $D_{11}$, $D_{12}$, $D_{13}$, $PR_{2}$ |
| Lint Leakage | $D_{1}$, $D_{4}$, $D_{5}$, $D_{6}$, $D_{9}$, $D_{13}$ |
| Blind Reference | $D_{6}$, $D_{7}$ |
| Init Fossilization | $D_{4}$, $D_{6}$, $D_{9}$, $D_{10}$, $D_{13}$ |
| Conflicting Instructions | $D_{1}$, $D_{3}$, $D_{6}$ |

### IV-A Context Bloat

This was the most frequently cited smell in our documents, being mentioned in 10 out of the 14 reviewed articles and in one PR. It occurs when an AGENTS.md file becomes excessively large and overloaded with rules, examples, or low-priority details. Bloated configuration files increase token consumption, raise costs, and reduce the visibility of important instructions. Therefore, AGENTS.md files should remain concise and focused on essential project-specific guidance. For example, Anthropic’s documentation explicitly recommends the following: target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence.1111
11
https://code.claude.com/docs/en/memory

To provide another example, in one of the pull requests we analyzed ($PR_{1}$), the authors proposed restructuring the AGENTS.md file to reduce its size. The PR explicitly states that the project’s configuration file was reduced from 598 to 149 lines, because modern LLMs tend to perform better with configuration files containing approximately 150 to 200 lines.

### IV-B Skill Leakage

This smell occurs when specific, rarely used, or highly
context-dependent instructions are placed in the AGENTS.md file instead of being specified in dedicated skill files (e.g., skills.md) and loaded on demand. In practice, this means that specialized knowledge “leaks” into every agent session, even when it is not needed. As a result, the agent’s context becomes larger, more expensive, and harder to maintain. Furthermore, such rules may compete for attention with the rules that are actually critical for the project. For example, one of the articles explicitly recommends the following: Instead of including all your different instructions about building your
project, running tests, code conventions, or other important context in your
CLAUDE.md file, we recommend keeping task-specific instructions in separate
markdown files with self-descriptive names somewhere in your project. ($D_{13}$)

### IV-C Lint Leakage

This smell occurs when an AGENTS.md file includes rules that are already checked by linters, formatters, or other static analysis tools. Typical examples include naming conventions (such as camelCase or PascalCase), formatting rules, import ordering, maximum line length, or generic style-guide recommendations. Because these constraints are automatically checked by local tools, repeating them in AGENTS.md adds limited value while unnecessarily increasing the agent’s context size [[12](https://arxiv.org/html/2606.15828#bib.bib36)]. Moreover, emphasizing such coding rules can divert the model from focusing on more important project-specific concerns, such as architectural constraints, domain rules, or safety policies. For example, one of the articles explicitly recommends the following: Code style enforcement is the biggest trap. Formatting, indentation, import ordering: these are deterministic problems with deterministic solutions. Linters and formatters like Biome, ESLint, or Ruff handle them faster, cheaper, and with 100% consistency. Spending instruction budget on style rules is dead weight: the same work a pre-commit hook does for free. ($D_{6}$)

### IV-D Blind References

This smell occurs when an AGENTS.md file contains references to external documents, files, or directories without explaining their purpose or scope. As a consequence, the agent may unnecessarily load large documents into context, ignore important references, or fail to prioritize the correct source of information for a given task. Thus, a better practice is to complement references with concise descriptions explaining the role of the document, the type of information it contains, and the context in which it should be used. For example, one document explicitly recommends the following: If you just mention the path [of an external document], Claude will often ignore it. You have to pitch the agent on why and when to read the file. ($D_{7}$)

### IV-E Init Fossilization

This smell occurs when the configuration file is generated by an initialization command such as /init but not reviewed or updated afterwards.
Thus, the file generated by the coding agent becomes the permanent configuration, often carrying instructions that are not relevant anymore to the project. As a result, the configuration tends to accumulate noise, increase context consumption, and reduce the overall effectiveness of the agent over time. For example,
Anthropic’s documentation explicitly recommends that the configuration file should be continuously updated, such as when: Claude makes the same mistake a second time;
a code review reveals something Claude should already have known about the codebase;
you find yourself typing the same correction or clarification in chat that you already provided in a previous session; and a new team member would need the same context in order to be productive.1212
12
https://code.claude.com/docs/en/memory

### IV-F Conflicting Instructions

This smell occurs when an AGENTS.md file contains instructions
that contradict each other, creating ambiguity about the expected behavior of the agent. Such inconsistencies can confuse the model and lead to unstable results. For example, small variations in the prompt can result in different agent behavior, because they are enough to make the agent follow a different inference path than the one followed previously. Anthropic’s documentation explicitly recommends the following: if two rules contradict each other, Claude may pick one arbitrarily. Review your CLAUDE.md files periodically to remove outdated or conflicting instructions.1313
13
https://code.claude.com/docs/en/memory

## V Detection Heuristics

We also propose a set of heuristics to detect the smells described in the previous section.

### V-A Heuristic based on Lines of Code

This heuristic is used exclusively to detect the Context Bloat smell. Specifically, we decided to use a threshold of 200 lines of code to identify this smell, as also suggested in the Anthropic document mentioned in Section [IV-A](https://arxiv.org/html/2606.15828#S4.SS1 "IV-A Context Bloat ‣ IV Configuration Smells ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents"). In other words, AGENTS.md files with 200 or more lines of code are classified as presenting the Context Bloat smell.

### V-B Heuristic based on Language Models

To detect the Skill Leakage, Lint Leakage, Blind References, and Conflicting Instructions smells, we decided to use a large language model. We designed a dedicated prompt for each smell, thereby requesting a more specific and objective task from the model. Figure [4](https://arxiv.org/html/2606.15828#S5.F4 "Fig. 4 ‣ V-B Heuristic based on Language Models ‣ V Detection Heuristics ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents") illustrates the baseline template of these prompts.

[⬇](data:text/plain;base64,IyBDb250ZXh0CgpZb3UgYXJlIGEgc2VuaW9yIHNvZnR3YXJlIGVuZ2luZWVyLiBJIHdpbGwgcHJvdmlkZQphbiBhZ2VudCBjb25maWd1cmF0aW9uIGZpbGUgKEFHRU5UUy5tZCkuIFlvdXIgdGFzawppcyB0byBkZXRlY3Qgd2hldGhlciB0aGUgZmlsZSBjb250YWlucyB0aGUKZm9sbG93aW5nIGNvbmZpZ3VyYXRpb24gc21lbGwuCgojIFNtZWxsOiBbbmFtZV0KCkRlc2NyaXB0aW9uOiBbYXMgaW4gU2VjdGlvbiBJVjsgZXNzZW50aWFsbHkgdGhlIGZpcnN0CnBhcmFncmFwaCBvZiB0aGUgc21lbGwgZGVzY3JpcHRpb25dCgpbT3B0aW9uYWw6IE9wZXJhdGlvbmFsIEd1aWRlbGluZXMgLyBUcnVlICYgRmFsc2UgUG9zaXRpdmVzIEV4YW1wbGVzXQotIEV4YW1wbGVzIGFuZCBlZGdlIGNhc2VzIHNwZWNpZmljIHRvIHRoZSBzbWVsbCB0byBtaW5pbWl6ZSBmYWxzZSBwb3NpdGl2ZXMuCgojIE91dHB1dAoKLSBJZiBkZXRlY3RlZDogW1JldHVybiBleGFjdCBsaW5lcyAvIEpTT04gb2JqZWN0IHdpdGggY29udHJhZGljdGlvbiBjb250ZXh0XQotIElmIG5vdCBkZXRlY3RlZCwgcmV0dXJuIG9ubHk6IE5PIFNNRUxMCgojIEFnZW50cy5tZCBmaWxlCgpbZmlsZSBjb250ZW50XQ==)

## Context

You are a senior software engineer. I will provide

an agent configuration file (AGENTS.md). Your task

is to detect whether the file contains the

following configuration smell.

## Smell: [name]

Description: [as in Section IV; essentially the first

paragraph of the smell description]

[Optional: Operational Guidelines / True & False Positives Examples]

- Examples and edge cases specific to the smell to minimize false positives.

## Output

- If detected: [Return exact lines / JSON object with contradiction context]

- If not detected, return only: NO SMELL

## Agents.md file

[file content]

Fig. 4: Prompt to detect Skill Leakage, Lint Leakage, Blind References and Conflicting Instructions

In the case of Blind References and Conflicting Instructions, we also enriched the basic prompt with examples of true/false positives. For example, in Figure [5](https://arxiv.org/html/2606.15828#S5.F5 "Fig. 5 ‣ V-B Heuristic based on Language Models ‣ V Detection Heuristics ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents") we show the example (true positive) added to the
prompt to detect Blind References.

[⬇](data:text/plain;base64,Li4uCiMjIFJlbGVhc2VzICYgRW52aXJvbm1lbnQKCkZvciByZWxlYXNlcyBvciBlbnZpcm9ubWVudCBpc3N1ZXMsIHNlZQpgd2ViL2Jvb2svc3JjL3Byb2plY3QvY29udHJpYnV0aW5nL2RldmVsb3BtZW50Lm1kYC4=)

...

## Releases & Environment

For releases or environment issues, see

‘web/book/src/project/contributing/development.md‘.

Fig. 5: Example added to the prompt to detect Blind References

### V-C Heuristic based on Number of Commits

This heuristic is used exclusively to detect the Init Fossilization smell. Conservatively, we consider that an AGENTS.md file with only a single commit exhibits this smell; that is, the file has never been modified since its creation.

## VI Configuration Smells in the Wild

To detect the smells in our dataset of 100 agent configuration files, we applied the heuristics proposed in Section [V](https://arxiv.org/html/2606.15828#S5 "V Detection Heuristics ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents"). For the heuristics based on LLMs, we used gemini-3.1-flash-lite, with a temperature of 0. Additionally, each smell instance identified by these heuristics was carefully reviewed by the first author to verify whether it is a true occurrence of the smell. The results are summarized in Table [II](https://arxiv.org/html/2606.15828#S6.T2 "TABLE II ‣ VI Configuration Smells in the Wild ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents") and are discussed in the following subsections.

TABLE II: Smells detected in real projects
  
(FP: False Positives; Prec: Precision)

|  |  |  |  |
| --- | --- | --- | --- |
|  | Instances | FP | Prec. (%) |
| Context Bloat | 42 | - | - |
| Skill Leakage | 35 | 6 | 82 |
| Lint Leakage | 62 | 4 | 93 |
| Blind Reference | 16 | 2 | 87 |
| Init Fossilization | 24 | - | - |
| Conflicting Instructions | 28 | 12 | 57 |

In Table [II](https://arxiv.org/html/2606.15828#S6.T2 "TABLE II ‣ VI Configuration Smells in the Wild ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents"), we also show the number of false positives and the precision, for the smells whose identification relies on LLM-based heuristics. In other words, we did not compute precision for Context Bloat and Init Fossilization because, in these cases, detection is based on pre-established thresholds.

Summary: We detected at least one smell in 91 agent configuration files. Thus, only nine files were found to be smell-free. These results suggest that developers could benefit from catalogs and tools designed to spot configuration issues in agent configuration files.

### VI-A Context Bloat

The proposed heuristic detected 42 cases of Context Bloat. The smallest file contains 216 lines of code, whereas the largest file contains 1,477 lines of code. Due to space constraints, we will not present a complete example of Context Bloat here. However, just to provide a high-level illustration, the CLAUDE.md file of the javascript-obfuscator project---a very popular and powerful obfuscator of JavaScript and Node.js source code---has 1,477 lines.1414
14
https://github.com/javascript-obfuscator/javascript-obfuscator This file is organized into 27 sections, including Project Overview, Architecture Overview, Core Workflow, CLI/API Usage, etc. As a result, the file is very large for repeated context loading, which can lead language models to discard important instructions. Much of these instructions would be better maintained in separate documentation or loaded on demand through skills.

When analyzing the file, we noticed, for example, that the second section is called Key Features, and has 22 lines. This section describes the obfuscation techniques used by the project, such as variable and function renaming, string extraction and encryption, dead code injection, and control-flow flattening. This information is mostly product documentation and provides limited value as persistent context for agents. Therefore, it could be removed from the agent configuration and described in the project’s README, for example.

It is also important to note that Context Bloat is a more visible smell, which makes it easier to detect. The root cause of this smell is the presence of other smells in the configuration file, such as Skill Leakage, which we will discuss next.

### VI-B Skill Leakage

The proposed heuristic detected 35 cases of Skill Leakage. After a manual analysis conducted by the first author, 29 cases were confirmed (86%). An example of Skill Leakage was found in the AGENTS.md file of quickemu-project/quickemu, which is a tool to simplify the creation and execution of virtual machines.1515
15
https://github.com/quickemu-project/quickemu The detected smell instance is shown in Figure [6](https://arxiv.org/html/2606.15828#S6.F6 "Fig. 6 ‣ VI-B Skill Leakage ‣ VI Configuration Smells in the Wild ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents"). As we can see, the section Adding a new OS to quickget contains instructions that are only useful for a small subset of tasks. Since most interactions with the coding agent do not involve adding new operating systems, these instructions unnecessarily increase the size of the configuration file. Thus, they would be better placed in a dedicated skill or documentation file.

[⬇](data:text/plain;base64,IyMgQWRkaW5nIGEgbmV3IE9TIHRvIHF1aWNrZ2V0CgpGb2xsb3cgdGhlIFtndWlkZSBpbiB0aGUgd2lraV0oLi4uKS4gRWFjaCBPUyByZXF1aXJlczoKCjEuIEVudHJ5IGluIGBvc19pbmZvKClgIGNhc2Ugc3RhdGVtZW50CjIuIGByZWxlYXNlc188b3M+KClgIGZ1bmN0aW9uIHJldHVybmluZyBhdmFpbGFibGUgdmVyc2lvbnMKMy4gYGVkaXRpb25zXzxvcz4oKWAgZnVuY3Rpb24gaWYgbXVsdGlwbGUgZWRpdGlvbnMgZXhpc3QKNC4gYGFyY2hfPG9zPigpYCBmdW5jdGlvbiBpZiBBUk02NCBpcyBzdXBwb3J0ZWQgKGRlZmF1bHRzIHRvIGFtZDY0IG9ubHkgaWYgb21pdHRlZCkKNS4gRG93bmxvYWQgVVJMIGNvbnN0cnVjdGlvbiBsb2dpYw==)

## Adding a new OS to quickget

Follow the [guide in the wiki](...). Each OS requires:

1. Entry in ‘os_info()‘ case statement

2. ‘releases_<os>()‘ function returning available versions

3. ‘editions_<os>()‘ function if multiple editions exist

4. ‘arch_<os>()‘ function if ARM64 is supported (defaults to amd64 only if omitted)

5. Download URL construction logic

Fig. 6: Example of Skill Leakage (quickemu-project/quickemu)

Most common leaked skills: We also manually classified the skills responsible for the identified Skill Leakage instances. The results of this classification are presented in Table [III](https://arxiv.org/html/2606.15828#S6.T3 "TABLE III ‣ VI-B Skill Leakage ‣ VI Configuration Smells in the Wild ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents"). As can be seen, the most common skills incorrectly defined in AGENTS.md files are related to testing concerns, followed by workflow guidelines (e.g., procedures for code reviews, pull requests, and issue management). Particularly, the Skill Leakage instance presented in Figure [6](https://arxiv.org/html/2606.15828#S6.F6 "Fig. 6 ‣ VI-B Skill Leakage ‣ VI Configuration Smells in the Wild ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents") was classified as scaffolding, as it defines functions that must be implemented to support a new operating system image within a module.

TABLE III: Most common leaked skills

| Skill Type | Frequency |
| --- | --- |
| Testing | 10 |
| Workflow | 8 |
| Scaffolding | 4 |
| Infrastructure | 4 |
| Architecture | 3 |

### VI-C Lint Leakage

The proposed heuristic detected 62 cases of Lint Leakage. After a manual analysis conducted by the first author, 58 cases were confirmed (93%). An interesting case of this smell was identified in the google/adk-python project, which is an open-source SDK for building agent-based applications in Python.1616
16
https://github.com/google/adk-python
As shown in Figure [7](https://arxiv.org/html/2606.15828#S6.F7 "Fig. 7 ‣ VI-C Lint Leakage ‣ VI Configuration Smells in the Wild ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents"), the AGENTS.md file of this project includes a section called Python Style Guide containing instructions for writing Python code, including recommendations for indentation and line length, naming conventions, usage of docstrings, etc. Normally, these recommendations are enforced by linters, formatters, or widely adopted community conventions, making their inclusion in the file unnecessary.

[⬇](data:text/plain;base64,IyMjIFB5dGhvbiBTdHlsZSBHdWlkZQoKKiBJbmRlbnRhdGlvbjogMiBzcGFjZXMuCiogTGluZSBMZW5ndGg6IE1heGltdW0gODAgY2hhcmFjdGVycy4KKiBOYW1pbmcgQ29udmVudGlvbnMqKjoKICAqIGBmdW5jdGlvbl9hbmRfdmFyaWFibGVfbmFtZXNgOiBgc25ha2VfY2FzZWAKICAqIGBDbGFzc05hbWVzYDogYENhbWVsQ2FzZWAKICAqIGBDT05TVEFOVFNgOiBgVVBQRVJDQVNFX1NOQUtFX0NBU0VgCiogRG9jc3RyaW5nczogUmVxdWlyZWQgZm9yIGFsbCBwdWJsaWMgbW9kdWxlcywgLi4uCiogSW1wb3J0czogT3JnYW5pemVkIGFuZCBzb3J0ZWQuCiogRXJyb3IgSGFuZGxpbmc6IFNwZWNpZmljIGV4Y2VwdGlvbnMgc2hvdWxkIGJlIC4uLg==)

### Python Style Guide

* Indentation: 2 spaces.

* Line Length: Maximum 80 characters.

* Naming Conventions**:

* ‘function_and_variable_names‘: ‘snake_case‘

* ‘ClassNames‘: ‘CamelCase‘

* ‘CONSTANTS‘: ‘UPPERCASE_SNAKE_CASE‘

* Docstrings: Required for all public modules, ...

* Imports: Organized and sorted.

* Error Handling: Specific exceptions should be ...

Fig. 7: Example of Lint Leakage (google/adk-python)

However, after creating our dataset (in January, 2026), we found that the project maintainers performed a major refactoring of the AGENTS.md file. Specifically, the Python Style Guide section, shown in Figure [7](https://arxiv.org/html/2606.15828#S6.F7 "Fig. 7 ‣ VI-C Lint Leakage ‣ VI Configuration Smells in the Wild ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents"), was moved to a separate skill file.
Therefore, this extraction confirms the relevance of the smell we initially detected in our dataset.

### VI-D Blind Reference

To help explain this smell, Figure [8](https://arxiv.org/html/2606.15828#S6.F8 "Fig. 8 ‣ VI-D Blind Reference ‣ VI Configuration Smells in the Wild ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents") shows an example in which an external reference is cited appropriately. Notice that the text references an external dependency, includes a link to its GitHub repository, and provides a brief explanation of its purpose (cdp-use only provides shallow typed interfaces for the websocket calls). Consequently, the agent is able to understand the role of the dependency without needing to load or inspect the external repository directly.

[⬇](data:text/plain;base64,IyMgQ0RQLVVzZQoKV2UgdXNlIGEgdGhpbiB3cmFwcGVyIGFyb3VuZCBDRFAgY2FsbGVkIGNkcC11c2U6IGh0dHBzOi8vZ2l0aHViLmNvbS9icm93c2VyLXVzZS9jZHAtdXNlLiBjZHAtdXNlIG9ubHkgcHJvdmlkZXMgc2hhbGxvdyB0eXBlZCBpbnRlcmZhY2VzIGZvciB0aGUgd2Vic29ja2V0IGNhbGxzLCBhbGwgQ0RQIGNsaWVudCBhbmQgc2Vzc2lvbiBtYW5hZ2VtZW50ICsgb3RoZXIgQ0RQIGhlbHBlcnMgc3RpbGwgbGl2ZSBpbiBicm93c2VyX3VzZS9icm93c2VyL3Nlc3Npb24ucHku)

## CDP-Use

We use a thin wrapper around CDP called cdp-use: https://github.com/browser-use/cdp-use. cdp-use only provides shallow typed interfaces for the websocket calls, all CDP client and session management + other CDP helpers still live in browser_use/browser/session.py.

Fig. 8: External reference described with context (browser-use/browser-use)

However, after applying the proposed heuristic, we were able to detect 16 instances of Blind Reference, i.e., references cited in AGENTS.md files without appropriate context. After a manual analysis, 14 cases were confirmed (87%). An example is shown in Figure [9](https://arxiv.org/html/2606.15828#S6.F9 "Fig. 9 ‣ VI-D Blind Reference ‣ VI Configuration Smells in the Wild ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents"). As we can see, this configuration references an external document (docs/plugin-reorg.md) to explain the planned plugin system, but it does not provide any contextual information about the document itself. Therefore, the agent would need to load and inspect the referenced file to understand the architecture and goals of the plugin system.

[⬇](data:text/plain;base64,IyMjIFBsdWdpbiBTeXN0ZW0gKHY1LjAgLSBOb3QgWWV0IEF2YWlsYWJsZSkKClRoZSBUeXBlU2NyaXB0IHBsdWdpbiBzeXN0ZW0gKGAuY2xhdWRlLXBsdWdpbi9gLCBtYXJrZXRwbGFjZSkgaXMgcGxhbm5lZCBmb3IgdjUuMC4KU2VlIGBkb2NzL3BsdWdpbi1yZW9yZy5tZGAgZm9yIGRldGFpbHMuCi4uLg==)

### Plugin System (v5.0 - Not Yet Available)

The TypeScript plugin system (‘.claude-plugin/‘, marketplace) is planned for v5.0.

See ‘docs/plugin-reorg.md‘ for details.

...

Fig. 9: Blind Reference (SuperClaude-Org/SuperClaude_Framework)

### VI-E Init Fossilization

We detected 24 cases of Init Fossilization, that is, AGENTS.md files with a single commit, as illustrated by the histogram in Figure [10](https://arxiv.org/html/2606.15828#S6.F10 "Fig. 10 ‣ VI-E Init Fossilization ‣ VI Configuration Smells in the Wild ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents"). The histogram also shows that configuration files are frequently updated in practice, thus reinforcing our argument that the absence of changes in such files is indeed a smell. For example, 14 of the analyzed files (14%) have between 11 and 15 commits, while 17 files (17%) have between 16 and 20 commits.

Fig. 10: Number of changes in AGENTS.md files (Init Fossilization corresponds to files with a single commit)

However, it is possible that the 24 projects exhibiting Init Fossilization were dormant projects, that is, projects with limited activity and few commits. Therefore, the histogram in Figure [11](https://arxiv.org/html/2606.15828#S6.F11 "Fig. 11 ‣ VI-E Init Fossilization ‣ VI Configuration Smells in the Wild ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents") shows the total number of commits made to these projects after the creation of their respective AGENTS.md files. As the histogram indicates, the hypothesis that these projects were inactive was not supported. In fact, we did not find a single project in such a situation, that is, with zero commits after the creation of the AGENTS.md file. On the contrary, we observed many projects with a substantial number of commits, including two projects with more than 1,500 commits, for example.

Fig. 11: Number of commits in projects exhibiting Init Fossilization (counting only commits made after the creation of AGENTS.md).

### VI-F Conflicting Instructions

The proposed heuristic detected 28 cases of Conflicting Instructions. However, after a manual analysis conducted by the first author, only 16 cases were confirmed (57%).
This lower precision is, to some extent, understandable, since identifying contradictory instructions is indeed a more complex task.
Figure [12](https://arxiv.org/html/2606.15828#S6.F12 "Fig. 12 ‣ VI-F Conflicting Instructions ‣ VI Configuration Smells in the Wild ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents") shows an example of this smell. As can be observed, the configuration specifies two directory paths for creating new components. An agent cannot satisfy the requirement to place components in packages/ui/components while simultaneously following the instruction to create them in packages/components.

[⬇](data:text/plain;base64,ICAgIC4uLgojIENvbXBvbmVudCBHdWlkZWxpbmVzCi0gQ29tcG9uZW50cyBzaG91bGQgYmUgcGxhY2VkIGluIHRoZSBgcGFja2FnZXMvdWkvY29tcG9uZW50c2AgZGlyZWN0b3J5Ci0gLi4uCgojIyBIb3cgdG8gY3JlYXRlIGEgbmV3IGNvbXBvbmVudAoKLSBDcmVhdGUgYSBuZXcgZm9sZGVyIGluIGBwYWNrYWdlcy9jb21wb25lbnRzYCB3aXRoIHRoZSBuYW1lIG9mIHRoZSBjb21wb25lbnQuCi4uLg==)

...

## Component Guidelines

- Components should be placed in the ‘packages/ui/components‘ directory

- ...

## How to create a new component

- Create a new folder in ‘packages/components‘ with the name of the component.

...

Fig. 12: Example of Conflicting Instructions (inkline/inkline)

TABLE IV: Co-existing smells detected by Apriori.

| Antecedent | | Consequent | Support | Confidence | Lift |
| --- | --- | --- | --- | --- | --- |
| Conflicting Instructions, Skill Leakage | $\rightarrow$ | Context Bloat | 0.06 | 0.83 | 1.81 |
| Init Fossilization, Skill Leakage | $\rightarrow$ | Lint Leakage | 0.06 | 0.83 | 1.31 |
| Conflicting Instructions | $\rightarrow$ | Context Bloat | 0.14 | 0.81 | 1.76 |
| Skill Leakage | $\rightarrow$ | Lint Leakage | 0.24 | 0.76 | 1.19 |
| Context Bloat, Skill Leakage | $\rightarrow$ | Lint Leakage | 0.10 | 0.75 | 1.18 |
| Conflicting Instructions, Lint Leakage | $\rightarrow$ | Context Bloat | 0.07 | 0.67 | 1.44 |

## VII Co-Occurrence Analysis

Besides analyzing smells individually, we also investigated which of them tend to co-exist in the same AGENTS.md files.
To discover such relationships, we used Apriori to mine association rules between the smells detected in our dataset [[1](https://arxiv.org/html/2606.15828#bib.bib30)].
This procedure is frequently used in software engineering research to associate code smells [[10](https://arxiv.org/html/2606.15828#bib.bib26), [17](https://arxiv.org/html/2606.15828#bib.bib27), [20](https://arxiv.org/html/2606.15828#bib.bib28)], source code files [[30](https://arxiv.org/html/2606.15828#bib.bib29)], and bug types [[7](https://arxiv.org/html/2606.15828#bib.bib25)].
In our case, we mapped each AGENTS.md as a transaction record, and the presence of each smell in the file as an item.
For instance, a given file $F_{1}$ with Context Bloat ($CB$), Skill Leakage ($SL$), and Lint Leakage ($LL$) is represented by the following transaction: $F_{1}=\{CB,SL,LL\}$.
For the 91 AGENTS.md files—our transactions—we applied Apriori with a support of $0.05$.

Table [IV](https://arxiv.org/html/2606.15828#S6.T4 "TABLE IV ‣ VI-F Conflicting Instructions ‣ VI Configuration Smells in the Wild ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents") presents the association rules.
The support varies between 0.06 and 0.24, i.e., the associated smells co-exist between 6% and 24% of the files in our dataset.
The confidence levels measure the probability of the consequent smell being present given the presence of the antecedent ones.
As we can see, the confidence levels are relatively high; for example, the presence of Conflicting Instructions and Skill Leakage increases the likelihood of Context Bloat to 83%.
Similar confidence appears in other rules, such as the one associating Init Fossilization and Skill Leakage with Lint Leakage (83%), and Conflicting Instructions with Context Bloat (81%).

Fig. 13: Smell accumulation in AGENTS.md files

Lift measures how much more likely items are to appear together than by chance.
A lift value greater than 1 indicates the smells appear in the same file more often than randomly.
We observe a strong association in two rules: Conflicting Instructions and Skill Leakage with Context Bloat (1.81), and Conflicting Instructions with Context Bloat (1.76).
In other words, the probability of Conflicting Instructions, Skill Leakage, and Context Bloat co-occurring in the same file is 1.81 times higher than if they were independent; likewise, Conflicting Instructions and Context Bloat are 1.76 times more likely to co-occur than by chance.

Figure [13](https://arxiv.org/html/2606.15828#S7.F13 "Fig. 13 ‣ VII Co-Occurrence Analysis ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents") depicts an Upset diagram showing the frequency AGENTS.md files—bar chart on top—for each unique smell combination—intersection matrix below.
In total, we detected 15 smell combinations with at least two occurrences.
Context Bloat and Lint Leakage stands out with 12 occurrences; i.e., they appeared together in 12 configuration files.
A second group of smells shows up next:
(a) Skill Leakage and Lint Leakage with seven occurrences;
(b) Skill Leakage, Lint Leakage, and Context Bloat in six files; and
(c) Lint Leakage and Init Fossilization in five files.
The other 11 remaining combinations were detected in three configuration files, at most.
We observe that configuration smells frequently overlap in AGENTS.md files, suggesting that multiple issues can compromise the performance of coding agents.

Summary: We leveraged six rules with co-existing smells.
Context Bloat is strongly associated with Conflicting Instructions and Skill Leakage, with lift values of 1.81 and 1.76, respectively.
This suggests that long AGENTS.md files often contain inconsistent or overly specific instructions.

## VIII Threats to Validity

Some steps of this work may be subject to threats to validity. In this section, we highlight and discuss these threats.

Bad Practices Annotations.
We manually annotated the sentences from the selected documents, which can introduce some bias in the smells identified further.
To mitigate this issue, another author performed a sanity check and reviewed all annotations from the selected documents to confirm whether the content accurately represented a good or bad practice in writing configuration files.

Google Search Limitations.
In a grey literature review, relevant results might be missed due to the specific combination of search terms.
To mitigate this threat, we used keywords to consider both bad and good practices to expand search coverage.
Furthermore, following the guidelines from other works [[8](https://arxiv.org/html/2606.15828#bib.bib4), [34](https://arxiv.org/html/2606.15828#bib.bib6)], we conducted preliminary search trials, adding and excluding keywords to refine our search strings.

Use of LLMs for Code Smell Detection.
In this work, we rely on LLMs to evaluate each AGENTS.md file and identify the presence of a specific smell.
Large Language Models (LLMs) are highly dynamic and frequently updated by their providers.
Another key factor is the non-deterministic nature of LLMs, which poses challenges for exact replication.
Consequently, the performance and results of code smell detection in configuration files may evolve over time.
To mitigate this issue, we set the model temperature to 0 and carefully analyzed the responses to ensure the identification of true positive cases.

## IX Related Work

We organize related work in three subsections: Context Engineering, Configuration Files, and Configuration Smells.

### IX-A Context Engineering

The effectiveness of LLMs in software engineering depends on the context provided to the model. Prior work has investigated how documentation, source code, retrieved artifacts, and prompt engineering can improve model responses [[18](https://arxiv.org/html/2606.15828#bib.bib15), [21](https://arxiv.org/html/2606.15828#bib.bib16)]. Other studies have examined how developers formulate prompts and how prompting practices can be systematized for programming tasks [[22](https://arxiv.org/html/2606.15828#bib.bib17), [26](https://arxiv.org/html/2606.15828#bib.bib18)]. Recent benchmarks have further highlighted the repository-level nature of realistic software engineering tasks. Through SWE-bench, Jimenez et al. [[13](https://arxiv.org/html/2606.15828#bib.bib14)] show that resolving real-world GitHub issues requires reasoning over repository context, modifying multiple files, and validating changes through tests. Thus, this observation motivates the study of project-level guidance for coding agents.

### IX-B Agent Configuration Files

Recent studies have started investigating configuration files for coding agents. Chatlatanagulchai et al. [[4](https://arxiv.org/html/2606.15828#bib.bib19)] refer to such files as Agentic Coding Manifests and show that CLAUDE.md files are predominantly action-oriented, commonly including build and run commands, implementation guidance, testing instructions, and architectural information.  [Santos et al. [25]](https://arxiv.org/html/2606.15828#bib.bib5) also analyzes CLAUDE.md files from public projects and identifies recurring sections such as architecture, development guidelines, project overview, and testing.
Together, these studies show that configuration files are becoming key artifacts in agentic software development. However, they focus on describing their structure and content. In this paper, we complement this line of work by investigating misconfiguration problems in AGENTS.md and CLAUDE.md files, including excessive context, lint leakage, blind references, outdated files, and conflicting instructions.

### IX-C Configuration Smells

Bad smells have long been studied as indicators of design, implementation, and maintenance problems, including their introduction [[32](https://arxiv.org/html/2606.15828#bib.bib20)], developers’ perceptions [[19](https://arxiv.org/html/2606.15828#bib.bib21)], and manifestations across different artifacts and paradigms [[6](https://arxiv.org/html/2606.15828#bib.bib22), [31](https://arxiv.org/html/2606.15828#bib.bib23)].
More recently, researchers have extended the smell concept to configuration and infrastructure artifacts. Rosa et al. [[23](https://arxiv.org/html/2606.15828#bib.bib24)] investigate Dockerfile smells, i.e., violations of Dockerfile best practices that may affect reliability, security, build time, image size, and reproducibility. Urdih et al. [[33](https://arxiv.org/html/2606.15828#bib.bib7)] study cache-related smells in GitLab CI/CD pipelines, proposing a catalog of ten smells and reporting that only 11% of 228 analyzed projects were smell-free. In this paper, we also focused on domain-specific smells, but with a focus on repository-level configuration files for coding agents. Unlike Dockerfile or CI/CD cache smells, which affect build and delivery processes, smells in AGENTS.md and CLAUDE.md may directly influence how coding agents interpret project conventions, prioritize instructions, and perform development tasks.

## X Conclusion

In this paper, we presented a catalog of smells that may affect configuration files for coding agents, such as AGENTS.md and CLAUDE.md. Based on a grey literature review of 14 documents, we identified six smells and proposed heuristics to detect them in a dataset of 100 popular open-source repositories. Our results show that these smells are widespread in practice, with 91 repositories exhibiting at least one smell. In particular, Lint Leakage was the most common smell, and we also observed recurring co-occurrence patterns involving Context Bloat, Skill Leakage, and Conflicting Instructions. Since configuration files are key artifacts in agentic software development, our findings suggest that their quality deserves effort and attention. We hope that the proposed catalog will serve as a foundation for future tools and techniques to detect and prevent configuration smells in coding-agent ecosystems.

## Replication Package

The data and results of this research are available at: https://doi.org/10.5281/zenodo.20600327.

## Acknowledgments

This research was supported by FAPEMIG and CNPq.

## References

- [1]
  R. Agrawal, H. Mannila, R. Srikant, H. Toivonen, and A. I. Verkamo (1996)
  Fast discovery of association rules.
  Advances in Knowledge Discovery and Data Mining.
  Cited by: [§VII](https://arxiv.org/html/2606.15828#S7.p1.1 "VII Co-Occurrence Analysis ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").
- [2]
  A. Almeida, L. Xavier, and M. T. Valente (2026)
  Using Copilot Agent Mode to Automate Library Migration: A Quantitative Assessment.
  In 1st International Workshop on Agentic Engineering,
  Cited by: [§I](https://arxiv.org/html/2606.15828#S1.p1.1 "I Introduction ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").
- [3]
  N. Alshahwan, J. Chheda, A. Finegenova, B. Gokkaya, M. Harman, I. Harper, A. Marginean, S. Sengupta, and E. Wang (2024)
  Automated Unit Test Improvement Using Large Language Models at Meta.
  In 32nd ACM Symposium on the Foundations of Software Engineering (FSE),
  Cited by: [§I](https://arxiv.org/html/2606.15828#S1.p1.1 "I Introduction ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").
- [4]
  W. Chatlatanagulchai, K. Thonglek, B. Reid, Y. Kashiwa, P. Leelaprute, A. Rungsawang, B. Manaskasemsak, and H. Iida (2025)
  On the use of agentic coding manifests: An empirical study of claude code.
  In International Conference on Product-Focused Software Process Improvement,
  Cited by: [§IX-B](https://arxiv.org/html/2606.15828#S9.SS2.p1.1 "IX-B Agent Configuration Files ‣ IX Related Work ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").
- [5]
  M. Chen, J. Tworek, H. Jun, Q. Yuan, H. P. D. O. Pinto, J. Kaplan, H. Edwards, Y. Burda, N. Joseph, G. Brockman, et al. (2021)
  Evaluating large language models trained on code.
  arXiv preprint arXiv:2107.03374.
  Cited by: [§I](https://arxiv.org/html/2606.15828#S1.p1.1 "I Introduction ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").
- [6]
  E. V. de Paulo Sobrinho, A. De Lucia, and M. de Almeida Maia (2021)
  A Systematic Literature Review on Bad Smells–5 W’s: Which, When, What, Who, Where.
  IEEE Transactions on Software Engineering.
  Cited by: [§IX-C](https://arxiv.org/html/2606.15828#S9.SS3.p1.1 "IX-C Configuration Smells ‣ IX Related Work ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").
- [7]
  T. L. De Santana, P. A. D. M. S. Neto, E. S. De Almeida, and I. Ahmed (2024)
  Bug Analysis in Jupyter Notebook Projects: An Empirical Study.
  ACM Transactions on Software Engineering and Methodology (TOSEM).
  Cited by: [§VII](https://arxiv.org/html/2606.15828#S7.p1.1 "VII Co-Occurrence Analysis ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").
- [8]
  V. Garousi, M. Felderer, and M. V. Mäntylä (2019)
  Guidelines for including grey literature and conducting multivocal literature reviews in software engineering.
  Information and Software Technology.
  Cited by: [§III-A](https://arxiv.org/html/2606.15828#S3.SS1.p1.1 "III-A Literature Review ‣ III Methods ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents"),
  [§VIII](https://arxiv.org/html/2606.15828#S8.p3.1 "VIII Threats to Validity ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").
- [9]
  I. Guelman, A. G. Leal, L. Xavier, and M. T. Valente (2026)
  On the Quality of AI-Generated Source Code Comments: A Comprehensive Evaluation.
  In 1st International Workshop on AI for Software Quality Evaluation (AI-SQE),
  Cited by: [§I](https://arxiv.org/html/2606.15828#S1.p1.1 "I Introduction ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").
- [10]
  O. Hamdi, A. Ouni, E. A. AlOmar, and M. W. Mkaouer (2021)
  An Empirical Study on Code Smells Co-occurrences in Android Applications.
  In 36th IEEE/ACM International Conference on Automated Software Engineering Workshops (ASEW),
  Cited by: [§VII](https://arxiv.org/html/2606.15828#S7.p1.1 "VII Co-Occurrence Analysis ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").
- [11]
  X. Hou, Y. Zhao, Y. Liu, Z. Yang, K. Wang, L. Li, X. Luo, D. Lo, J. Grundy, and H. Wang (2024)
  Large Language Models for Software Engineering: A Systematic Literature Review.
  ACM Transactions on Software Engineering and Methodology.
  Cited by: [§I](https://arxiv.org/html/2606.15828#S1.p1.1 "I Introduction ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").
- [12]
  C. Huyen (2025)
  AI Engineering: Building Applications with Foundation Models.
   O’Reilly.
  Cited by: [§IV-C](https://arxiv.org/html/2606.15828#S4.SS3.p1.1 "IV-C Lint Leakage ‣ IV Configuration Smells ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").
- [13]
  C. E. Jimenez, J. Yang, A. Wettig, S. Yao, K. Pei, O. Press, and K. R. Narasimhan (2024)
  SWE-bench: Can Language Models Resolve Real-World GitHub Issues?.
  In 12th International Conference on Learning Representations (ICLR),
  Cited by: [§IX-A](https://arxiv.org/html/2606.15828#S9.SS1.p1.1 "IX-A Context Engineering ‣ IX Related Work ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").
- [14]
  J. Lu, L. Yu, X. Li, L. Yang, and C. Zuo (2023)
  LLaMA-Reviewer: Advancing Code Review Automation with Large Language Models through Parameter-Efficient Fine-Tuning.
  In IEEE 34th International Symposium on Software Reliability Engineering (ISSRE),
  Cited by: [§I](https://arxiv.org/html/2606.15828#S1.p1.1 "I Introduction ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").
- [15]
  A. Mastropaolo, N. Cooper, D. N. Palacio, S. Scalabrino, D. Poshyvanyk, R. Oliveto, and G. Bavota (2023)
  Using Transfer Learning for Code-Related Tasks.
  IEEE Transactions on Software Engineering.
  Cited by: [§I](https://arxiv.org/html/2606.15828#S1.p1.1 "I Introduction ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").
- [16]
  S. Mohsenimofidi, M. Galster, C. Treude, and S. Baltes (2025)
  Context engineering for ai agents in open-source software.
  arXiv preprint arXiv:2510.21413.
  Cited by: [§II](https://arxiv.org/html/2606.15828#S2.p3.1 "II Coding Agents Configuration Files ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").
- [17]
  B. A. Muse, M. M. Rahman, C. Nagy, A. Cleve, F. Khomh, and G. Antoniol (2020)
  On the Prevalence, Impact, and Evolution of SQL Code Smells in Data-Intensive Systems.
  In 17th International Conference on Mining Software Repositories (MSR),
  Cited by: [§VII](https://arxiv.org/html/2606.15828#S7.p1.1 "VII Co-Occurrence Analysis ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").
- [18]
  D. Nam, A. Macvean, V. J. Hellendoorn, B. Vasilescu, and B. A. Myers (2024)
  Using an LLM to Help With Code Understanding.
  In 46th International Conference on Software Engineering (ICSE),
  Cited by: [§IX-A](https://arxiv.org/html/2606.15828#S9.SS1.p1.1 "IX-A Context Engineering ‣ IX Related Work ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").
- [19]
  F. Palomba, G. Bavota, M. Di Penta, R. Oliveto, and A. De Lucia (2014)
  Do They Really Smell Bad? A Study on Developers’ Perception of Bad Code Smells.
  In International Conference on Software Maintenance and Evolution (ICSME),
  Cited by: [§IX-C](https://arxiv.org/html/2606.15828#S9.SS3.p1.1 "IX-C Configuration Smells ‣ IX Related Work ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").
- [20]
  F. Palomba, R. Oliveto, and A. De Lucia (2017)
  Investigating Code Smell Co-Occurrences Using Association Rule Learning: A Replicated Study.
  In IEEE Workshop on Machine Learning Techniques for Software Quality Evaluation (MaLTeSQuE),
  Cited by: [§VII](https://arxiv.org/html/2606.15828#S7.p1.1 "VII Co-Occurrence Analysis ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").
- [21]
  G. Pinto, C. R. B. de Souza, J. B. Cordeiro Neto, A. de Souza, T. Gotto, and E. Monteiro (2024)
  Lessons from Building CodeBuddy: A Contextualized AI Coding Assistant.
  In 46th International Conference on Software Engineering: Software Engineering in Practice (ICSE-SEIP),
  Cited by: [§IX-A](https://arxiv.org/html/2606.15828#S9.SS1.p1.1 "IX-A Context Engineering ‣ IX Related Work ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").
- [22]
  K. Pister, D. J. Paul, P. Brophy, and I. Joshi (2024)
  PromptSet: A Programmer’s Prompting Dataset.
  In Proceedings of the 1st ACM International Conference on AI-Powered Software (AIware),
  Cited by: [§IX-A](https://arxiv.org/html/2606.15828#S9.SS1.p1.1 "IX-A Context Engineering ‣ IX Related Work ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").
- [23]
  G. Rosa, F. Zappone, S. Scalabrino, and R. Oliveto (2024)
  Fixing Dockerfile Smells: An Empirical Study.
  Empirical Software Engineering.
  Cited by: [§IX-C](https://arxiv.org/html/2606.15828#S9.SS3.p1.1 "IX-C Configuration Smells ‣ IX Related Work ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").
- [24]
  C. Sadowski, K. T. Stolee, and S. Elbaum (2015)
  How developers search for code: a case study.
  In Proceedings of the 2015 10th Joint Meeting on Foundations of Software Engineering,
  Cited by: [§III-A](https://arxiv.org/html/2606.15828#S3.SS1.p2.1 "III-A Literature Review ‣ III Methods ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").
- [25]
  H. V. F. Santos, V. Costa, J. E. Montandon, and M. T. Valente (2026)
  Decoding the Configuration of AI Coding Agents: Insights from Claude Code Projects.
  In 1st International Workshop on Agentic Engineering,
  Cited by: [§II](https://arxiv.org/html/2606.15828#S2.p2.1 "II Coding Agents Configuration Files ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents"),
  [§IX-B](https://arxiv.org/html/2606.15828#S9.SS2.p1.1 "IX-B Agent Configuration Files ‣ IX Related Work ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").
- [26]
  Y. Sasaki, H. Washizaki, J. Li, N. Yoshioka, N. Ubayashi, and Y. Fukazawa (2025)
  Landscape and Taxonomy of Prompt Engineering Patterns in Software Engineering.
  IT Professional.
  Cited by: [§IX-A](https://arxiv.org/html/2606.15828#S9.SS1.p1.1 "IX-A Context Engineering ‣ IX Related Work ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").
- [27]
  J. Shin, C. Tang, T. Mohati, M. Nayebi, S. Wang, and H. Hemmati (2023)
  Prompt Engineering or Fine Tuning: An Empirical Assessment of Large Language Models in Automated Software Engineering Tasks.
  ArXiv.
  Cited by: [§I](https://arxiv.org/html/2606.15828#S1.p1.1 "I Introduction ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").
- [28]
  M. L. Siddiq, J. C. S. Santos, R. H. Tanvir, N. Ulfat, F. A. Rifat, and V. C. Lopes (2024)
  Using Large Language Models to Generate JUnit Tests: An Empirical Study.
  In 28th International Conference on Evaluation and Assessment in Software Engineering (EASE),
  Cited by: [§I](https://arxiv.org/html/2606.15828#S1.p1.1 "I Introduction ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").
- [29]
  L. L. Silva, J. R. d. Silva, J. E. Montandon, M. Andrade, and M. T. Valente (2024)
  Detecting Code Smells Using ChatGPT: Initial Insights.
  In 18th ACM/IEEE International Symposium on Empirical Software Engineering and Measurement (ESEM),
  Cited by: [§I](https://arxiv.org/html/2606.15828#S1.p1.1 "I Introduction ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").
- [30]
  M. Soto and C. Le Goues (2018)
  Using a Probabilistic Model to Predict Bug Fixes.
  In IEEE 25th International Conference on Software Analysis, Evolution and Reengineering (SANER),
  Cited by: [§VII](https://arxiv.org/html/2606.15828#S7.p1.1 "VII Co-Occurrence Analysis ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").
- [31]
  D. Taibi and V. Lenarduzzi (2018)
  On the Definition of Microservice Bad Smells.
  IEEE Software.
  Cited by: [§IX-C](https://arxiv.org/html/2606.15828#S9.SS3.p1.1 "IX-C Configuration Smells ‣ IX Related Work ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").
- [32]
  M. Tufano, F. Palomba, G. Bavota, R. Oliveto, M. Di Penta, A. De Lucia, and D. Poshyvanyk (2015)
  When and Why Your Code Starts to Smell Bad.
  In 37th IEEE/ACM International Conference on Software Engineering (ICSE),
  Cited by: [§IX-C](https://arxiv.org/html/2606.15828#S9.SS3.p1.1 "IX-C Configuration Smells ‣ IX Related Work ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").
- [33]
  F. Urdih, T. Theodoropoulos, and U. Zdun (2026)
  Cache-Related Smells in GitLab CI/CD: Comprehensive Catalog, Automated Detection, and Empirical Evidence.
  arXiv preprint arXiv:2604.17890.
  Cited by: [§IX-C](https://arxiv.org/html/2606.15828#S9.SS3.p1.1 "IX-C Configuration Smells ‣ IX Related Work ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").
- [34]
  L. Vegi and M. T. Valente (2022)
  Code Smells in Elixir: Early Results from a Grey Literature Review.
  In 30th International Conference on Program Comprehension (ICPC),
  Cited by: [§III-A](https://arxiv.org/html/2606.15828#S3.SS1.p2.1 "III-A Literature Review ‣ III Methods ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents"),
  [§VIII](https://arxiv.org/html/2606.15828#S8.p3.1 "VIII Threats to Validity ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").
- [35]
  Z. Xi, W. Chen, X. Guo, W. He, Y. Ding, B. Hong, M. Zhang, J. Wang, S. Jin, E. Zhou, R. Zheng, X. Fan, X. Wang, L. Xiong, Y. Zhou, W. Wang, C. Jiang, Y. Zou, X. Liu, Z. Yin, S. Dou, R. Weng, W. Qin, Y. Zheng, X. Qiu, X. Huang, Q. Zhang, and T. Gui (2025)
  The rise and potential of large language model based agents: a survey.
  Science China Information Sciences.
  Cited by: [§II](https://arxiv.org/html/2606.15828#S2.p1.1 "II Coding Agents Configuration Files ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").
- [36]
  C. Ziftci, S. Nikolov, A. Sjövall, B. Kim, D. Codecasa, and M. Kim (2025)
  Migrating Code At Scale With LLMs At Google.
  In Proceedings of the 33rd ACM International Conference on the Foundations of Software Engineering,
  Cited by: [§I](https://arxiv.org/html/2606.15828#S1.p1.1 "I Introduction ‣ Configuration Smells in AGENTS.md Files: Common Mistakes in Configuring Coding Agents").
