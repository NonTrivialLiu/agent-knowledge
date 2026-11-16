---
title: "Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use"
url: https://proceedings.mlr.press/v306/wu26al.html
published: 2026-07
fetched: 2026-11-11
type: paper
topics: [training, tools, multi-agent]
summary: "ICML 2026 研究工具、查询、观察和领域偏移下的泛化；以可控环境评估静态训练的脆弱性。"
---

# Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

**Weiming Wu**<sup>* 1</sup> **Song-Lin Lv**<sup>* 1 2</sup> **Rui Zhu**<sup>1</sup> **Zi-Jian Cheng**<sup>1 2</sup> **Lan-Zhe Guo**<sup>1 2</sup> 

## **Abstract**

While Large Language Model (LLM) agents demonstrate proficiency in static benchmarks, their deployment in real-world scenarios is hindered by the dynamic nature of user queries, tool sets, and interaction dynamics. To address this generalization gap, we formalize **OpenAgent** (Tool-Use Agent in Open-World), a problem setting characterized by distributional shifts across query, action, observation, and domain dimensions. To systematically diagnose its impact, we construct a controlled sandbox environment where we define fine-grained environmental shifts across a four-tier hierarchy, _Perception_ , _Interaction_ , _Reasoning_ , and _Internalization_ , and conduct a comprehensive series of experiments. Our analysis yields a series of key insights, demonstrating that agents trained via both Supervised Fine-Tuning(SFT) and Reinforcement Learning suffer from varying degrees of performance degradation when confronting open environmental shifts. Building on these insights, we propose Perturbation-Augmented Fine-Tuning, a disturbance-based intervention strategy for SFT that lays the foundation for enhancing agent robustness and utility in realistic environments. Our code will be released at: https://github. com/LAMDA-NeSy/OpenAgent. 

## **1. Introduction**

The integration of Tool Learning and the Model Context Protocol (MCP) (Anthropic, 2024) has catalyzed a paradigm shift in Large Language Model (LLM) agents, enabling 

> *Equal contribution 1School of Intelligence Science and Technology, Nanjing University, Nanjing, China<sup>2</sup> National Key Laboratory for Novel Software Technology, Nanjing University, Nanjing, China. Correspondence to: Lan-Zhe Guo _<_ guolz@lamda.nju.edu.cn _>_ . 

_Proceedings of the 43_<sup>_rd_</sup> _International Conference on Machine Learning_ , Seoul, South Korea. PMLR 306, 2026. Copyright 2026 by the author(s). 

them to navigate external environments to solve complex, multi-step tasks (Guo et al., 2024; Wang et al., 2024b; Qu et al., 2025). Optimized via Supervised Fine-Tuning (SFT) and Reinforcement Learning (RL), recent open-source models (Hsieh et al., 2023; Qu et al., 2024; Qwen et al., 2024; Bai et al., 2025) have achieved tool invocation proficiency that rivals proprietary frontiers like GPT-4 (Achiam et al., 2023) and Gemini (Team et al., 2023). As illustrated in Figure 1, under the prevailing _static world assumption_ , where the distribution of tools, schemas, and interaction logic remains consistent between training and inference (Shen et al., 2023; Yin et al., 2025; He et al., 2025), both SFT and RL paradigms demonstrate stable and continuous performance gains, eventually converging on near-perfect success rates. 

However, this stability is often an artifact of the closed-set nature of current benchmarks. Real-world deployment is fundamentally non-stationary: APIs are deprecated, tool schemas evolve, and user instructions are frequently ambiguous. When these environmental dynamics diverge from training priors, the apparent mastery observed in static benchmarks often proves fragile. This discrepancy raises a fundamental research question: **_Do current training paradigms enable agents to generalize to the open world?_** 

To rigorously address this, we formally define **OpenAgent** (Tool-Use Agent in Open-World), a problem setting characterizing shifts across four dimensions: _User Queries_ (∆ _Q_ ), _Tool Sets_ (∆ _A_ ), _Interaction Dynamics_ (∆ _O_ ) and _Task Domain_ (∆ _D_ ). To isolate the impact of these shifts from the inherent instability and transient noise of real-world APIs, we establish a controlled sandbox environment. This setup allows for controlled probing, enabling us to maintain a pure closed-set baseline while systematically injecting openworld perturbations across a four-tier diagnostic framework: _Perception_ , _Interaction_ , _Reasoning_ , and _Internalization_ . 

Our comprehensive evaluations reveal varying degrees of generalization and adaptability in SFT and RL models under open-world settings, while further identifying their respective structural weaknesses. We find that **both** paradigms suffer from performance degradation in open environments, albeit through distinct failure modes. While SFT agents are prone to trajectory overfitting and brittle symbolic anchoring, RL agents, despite demonstrating better semantic 

1 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

<!-- Start of picture text -->
Close Environment<br>0 100 200 300 SFT Training Step400 500 600 700 800<br>16<br>90 14<br>80 12<br>70 10<br>60 8<br>6<br>50<br>4<br>40<br>2<br>30<br>0<br>0 50 100 150 200 250<br>RL Training Step<br>SFT Accuracy SFT Tool Error Rate RL Accuracy RL Tool Error Rate<br>Accuracy (%)<br>Tool Error Rate (%)<br><!-- End of picture text -->

_Figure 1._ Performance evolution of SFT and RL agents in the closed setting. Both approaches show stable and continuous improvement throughout the training process. 

grounding, remain vulnerable to boundary blindness due to a teleological bias in their reward structures. 

Building on these insights, we introduce PerturbationAugmented Fine-Tuning (PAFT), a data-centric intervention strategy for SFT. By injecting controlled observation anomalies and symbolic noise into training trajectories, PAFT decouples models from shallow pattern memorization and restores robust generalization in open worlds. 

In summary, the primary threefold contributions of this work are as follows: 

- **Formalization of Open Environment in Tool Use:** We formally define the OpenAgent setting, characterizing the shifts in queries, tool sets, interaction dynamics and task domain inherent to real-world deployments. 

- **Systematic Evaluation in Open Environments:** We establish a controlled sandbox environment and conduct a comprehensive series of experiments to evaluate the robustness of SFT and RL agents across varying levels of environmental shifts. 

- **Key Insights and Methods:** We identify critical failure modes in current paradigms, specifically symbolic anchoring in SFT and boundary blindness in RL, and propose PAFT to effectively mitigate performance degradation. 

**Conflict of Interest Disclosure.** The authors declare no conflicts of interest. 

## **2. Related Works**

**Post-training Paradigms for Agents** Current methodologies are categorized into three methods. SFT-based works like GenTool (He et al., 2025), TOUCAN (Xu et al., 2025b), and others (Shi et al., 2024; He et al., 2025; Yuan et al., 2025; 

<!-- Start of picture text -->
h" a" o"<br>(q) Tool 1 Value<br>𝜋$ env<br>… … …<br>(q, a!,..,o"#!) Tool N Success!<br>Action Query Open Observation Domain<br>Shift (∆𝒜) Shift (∆𝓠) World Shift (∆𝓞) Shift<br>h" a" o"<br>(q ' ) 𝜋$ Tool 1' env None<br>… … …<br>(q ' , a!,..,o"#!) Tool N+1 Error!<br><!-- End of picture text -->

_Figure 2._ Challenges in OpenAgent setting, including query, action, observation and domain shifts. 

Lin et al., 2025; Mo et al., 2026) standardize tool invocation via token prediction. Conversely, RL frameworks such as ToolRL (Qian et al., 2025), DeepEyes (Zheng et al., 2026), and others (Feng et al., 2025; Yu et al., 2025; Qian et al., 2025) utilize reward mechanisms to drive robust decisionmaking. Hybrid paradigms including ReTool (Feng et al., 2026), DeepEyesV2 (Hong et al., 2026), and others (Su et al., 2025; Li et al., 2026) combine SFT initialization with RL exploration. Following recent closed-source advances models like Deepseek-V3.2, GLM-4.5 (Zeng et al., 2025), and Kimi K2 (Team et al., 2025), we select full-parameter SFT and RL as baselines. 

**Evaluation Paradigms for Agents** Agent capabilities are evaluated via local tools (Wang et al., 2024a; Guo et al., 2024; Huang et al., 2024; Ye et al., 2025) and remote protocols (Li et al., 2023; Wang et al., 2024c; Gao et al., 2025; Wang et al., 2026). Existing benchmarks mainly prioritize task success (Mialon et al., 2024; Liu et al., 2025; Patil et al., 2025; Shao et al., 2026), while robustness studies focus on inference-time perturbations (Ye et al., 2024; Xiong et al., 2025). Recently, agent benchmarks further move toward realistic environments (Liu et al., 2024; Zhou et al., 2024; Drouin et al., 2024; Jimenez et al., 2024; Koh et al., 2024; Trivedi et al., 2024; Ma et al., 2024; Xie et al., 2024; Xu et al., 2025a). Unlike open-environment learning for passive models (Guo et al., 2020; Li et al., 2021; Zhou, 2022; Guo & Li, 2022; Jia et al., 2024; Guo et al., 2025; Cheng et al., 2025), OpenAgent studies shifts in multi-step. While prior work (Chu et al., 2025) shows RL’s advantage over SFT, it lacks tool-use contexts; we address this gap by analyzing training-to-testing transfer under open-environment shifts. 

## **3. Preliminaries**

## **3.1. Problem Formulation**

We model the agent as a sequential decision-making process _M_ = _⟨Q, A, O, π⟩_ , comprising user queries _Q_ , tool space 

2 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

<!-- Start of picture text -->
Query Requirements Call<br>Return Messages<br>Instruction  Information<br>Blurring Redundancy Schema Adaptability  {value:xxx} The value is xxx ∅<br>Tool<br>Normal Message Format Shift Error Message  Null Message<br>Para<br>change<br>Symbolic Drift Semantic Trap Identity Erasure Value Redirection Tool Error  + Tool Redirection<br>Before<br>I can’t +<br>   …… Tool A Tool B<br>Missing Condition<br>After<br>Merged Tool<br>Fatal Error Active Refusal Trace Simplification<br>There is a Name Tel.<br>shortcut/<br>Inversion!<br>Tel. Name<br>Logic Inversion<br>Domain Transfer Plan Planning Rule Reasoning<br>What<br><!-- End of picture text -->

_Figure 3._ Architecture Diagram of the Evaluation Task. We partition this evaluation task architecture diagram into four levels from shallow to deep: Perception, Interaction, Reasoning, and Internalization. 

_A_ , and observation space _O_ . Given a query _q ∈Q_ , at each step _t_ , the agent uses policy _πθ_ ( _at | ht_ ) to select action _at ∈A_ based on history _ht_ = ( _q, a_ 1 _, o_ 1 _, . . . , at−_ 1 _, ot−_ 1). The environment returns observation _ot ∈O_ , which updates the history to _ht_ +1 = ( _ht, at, ot_ ) until task completion. Our core challenge is the generalization of the model when testtime distributions diverge from training priors. 

## **3.2. The OpenAgent Setting: Distributional Shifts**

Unlike distributional shifts in passive models, where each input is perturbed independently, tool-use agents face _cascading_ shifts along the agent-environment loop. A perturbation at step _t_ may alter observation _ot_ , which enters the history _ht′_ and conditions all subsequent decisions _πθ_ ( _at′ | ht′_ ) for _t_<sup>_′_</sup> _> t_ , causing errors to compound along the trajectory. As illustrated in Figure 2, OpenAgent covers query shifts ( _q → q_<sup>_′_</sup> ), action-space shifts including perturbed existing tools and newly introduced tools, observation shifts such as _None_ or _Error_ , and joint domain shifts where all interaction elements change together. We decompose this interactive shift space into four dimensions. 

**Intent Shift in Query Space (** ∆ _Q_ **).** The intent distribution _P_ ( _q_ ) shifts across both semantic directives and linguistic surface forms. Unlike passive input perturbations, query misinterpretation in tool-use agents propagates through the 

trajectory: an initial misparse may seed a misaligned tool chain whose errors compound across subsequent steps. 

**Structural Shift in Action Space (** ∆ _A_ **).** The tool space becomes non-stationary ( _A_ test _̸_ = _A_ train), spanning multiple levels of change: _surface drift_ , which renames identifiers while preserving functionality; _semantic conflict_ , which retains familiar names but alters documented behavior; and _structural reconfiguration_ , which merges, splits, or inverts tool dependencies. The agent must distinguish cosmetic changes from fundamental reconfigurations and ground actions in the current tool semantics. 

**Dynamics Shift in Observation Space (** ∆ _O_ **).** The feedback channel becomes non-stationary: test-time observations may include return formats, error states, null values, or corrective instructions that are absent or rare in training. Unlike static outputs, these observations directly update the agent’s belief state and reshape the subsequent action space. Crucially, the agent must discriminate _informative_ anomalies that require policy adjustment from _terminal_ failures that require task refusal, a distinction absent in passive settings where each input simply calls for a prediction. 

**Compositional Domain Shift (** ∆ _D_ **).** This shift jointly changes _Q_ , _A_ , and _O_ into a new domain while preserving a latent problem-solving structure _G_ . Despite distinct 

3 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

surface semantics and interfaces, the agent must transfer the underlying reasoning topology by re-grounding its nodes and dependencies in the target domain, rather than relying on domain-specific lexical or procedural patterns. 

## **4. Evaluation Tasks**

## **4.1. Experimental Setup**

**Controlled Sandbox Environment.** We utilize a synthetic sandbox environment to enable controlled probing of agent capabilities. Unlike real-world APIs which introduce uncontrollable transient noise, a sandbox allows us to precisely isolate environmental variables and establish a pure closed environment baseline to measure open environment shifts. We synthesized a diverse set of tool-use tasks focused on simple geographical POI queries and calculation problems to test reasoning boundaries, the full specifications of which are detailed in the Appendix A. 

**Datasets and Protocols.** The dataset comprises 6,050 training samples and 880 evaluation samples. To ensure rigorous evaluation, we enforced a strict separation between the datasets where no variation patterns from the test set appear during the training phase. This guarantees that the reported performance reflects genuine robustness rather than information leakage or pattern memorization. 

**Training Implementation.** We employ Qwen2.5-7BInstruct (Qwen et al., 2024) as the backbone model. The SFT stage uses full-parameter fine-tuning, while the RL stage adopts the GRPO framework with sparse answers and format rewards. To further ensure a fair comparison with SFT, the RL environment provides only basic error codes upon failure without detailed guidance. We trained both models under comparable computational budgets until they achieved convergence in the closed environment as illustrated in Figure 1. The Training details are provided in Appendix B. 

**Metrics.** We employ four metrics to assess performance across correctness, efficiency, robustness, and adaptability: 

- **Tool Error Rate (TER):** Measures _robustness_ via the = 

- ratio of invalid invocations to total calls ( _TER Nerror/Ntotal_ ). A lower TER indicates precise adherence. 

- **Active Exploration Score (AES):** Quantifies _adaptability_ by penalizing “cognitive inertia” when tools fail. _AES_ = _e_<sup>_−_(</sup><sup>_nold−_1)</sup> (1) 

where _nold_ is the count of repeated invalid attempts. A score of 1 _._ 0 signifies immediate adaptation. 

- **Average Tool Chain Length (ATCL):** Gauges _efficiency_ by averaging tool invocations on solvable tasks. Lower values reflect concise reasoning topologies. 

- **Refusal Rate (RR):** Evaluates _boundary awareness_ in unsolvable scenarios by measuring the ratio of correctly identified unsolvable cases ( _RR_ = _Nrefusal/Nunsolvable_ ). A higher RR indicates superior active boundary detection. 

## **4.2. Tier 1: Perception Generalization**

In the context of agentic interaction, perception acts as the cognitive gateway grounding raw observations into actionable representations. To successfully initiate a task, an agent must traverse three representational alignments: deciphering unstructured user intents, aligning with rigid interface protocols, and comprehending functional tool definitions. We systematically evaluate the generalization boundaries of these capabilities through the following three dimensions. 

**Instruction Robustness (** ∆ _Q_ **).** Real-world user instructions are rarely canonical. We evaluate whether the agent can extract invariant intents from non-standard inputs by introducing two distinct types of variations. 

- **Instruction Blurring:** We simulate scenarios where user intent is obfuscated by syntactic variance (e.g., colloquialisms, rhetorical questions) or semantic ambiguity (e.g., implicit references, omitted entities). This tests the model’s ability to reconstruct exact intents without relying on explicit keyword matching. 

- **Information Redundancy:** We test the robustness of the model’s attention mechanism against information overload. By embedding the core instruction within irrelevant context or verbose background details, we evaluate the agent’s capability to filter out red herrings and lock onto functional constraints. 

**Schema Adaptability (** ∆ _A_ **).** Agents often overfit to specific API formats seen during training. In this experiment, we introduce protocol shifts by modifying the reserved keywords in the tool invocation schema. For instance, we alter the parameter dictionary key from the standard arguments to variants like args or parameters. This verifies whether the model comprehends the abstract concept of parameter passing or merely performs rigid template completion based on memorized structural tokens. 

**Semantic Grounding (** ∆ _A_ **).** Current agents often rely on Symbolic Anchoring with rigid dependence on memorized identifiers rather than true understanding of functional definitions. To decouple these factors, we investigate whether models can adapt to dynamic documentation shifts through a Drift-Trap-Erasure trilogy: 

- **Symbolic Drift:** We test tolerance to perturbations via two sub-variants: _Noise Injection_ (appending nonsemantic suffixes) and _Synonymous Rewriting_ (using LLMs to paraphrase). This verifies generalization across semantically equivalent but symbolically distinct labels. 

- **Semantic Trap:** We engineer a conflict between sym- 

4 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

bol and semantics with adversarial attack.by retaining a familiar tool name but modify its description to explicitly forbid usage. If the agent invokes it, it proves that symbolic overrides semantic understanding. 

- **Identity Erasure:** We perform the ultimate test of grounding by replacing meaningful tool names with random identifiers (e.g., Tool ~~2~~ A3D). This removes symbolic shortcuts, forcing the agent to rely exclusively on reading comprehension of the documentation to solve the task. 

## **4.3. Tier 2: Interaction Generalization**

Interaction generalization evaluates whether an agent can use environmental feedback to refine subsequent actions. In open environments, observations may indicate format changes, execution failures, or new operational constraints rather than merely confirming previous tool calls. We examine three capabilities: _Format Adaptability_ for parsing diverse observation structures, _Error Correction_ for recovering from explicit or silent failures, and _Dynamic Alignment_ for adjusting actions according to feedback-provided rules. 

**Format Adaptability (** ∆ _O_ **).** Agents typically overfit to standard JSON formats for parsing observations. This experiment tests the fundamental capability of the agent to parse non-standard feedback. We introduce Format Shift by altering the structure of tool return values from structured JSON to unstructured formats such as Markdown tables or raw text logs. This evaluates whether the agent extracts key information based on semantic content rather than relying on rigid syntactic parsing templates. 

**Error Correction (** ∆ _O_ **).** Open environments may expose agents to execution failures that interrupt the planned trajectory. We evaluate whether the agent can diagnose such failures and recover by revising its invocation plan or selecting alternative tools. We consider two types of failure: 

- **Error Return:** The primary tool explicitly returns an error code or traceback message after invocation. This tests whether the agent can interpret explicit failure signals and switch to a redundant tool to resolve the blockage. 

- **Null Return:** The primary tool returns a null value or an empty string without any warning. This tests whether the agent can detect an implicit anomaly where the return is syntactically valid but semantically uninformative, and infer that corrective action is required. 

**Dynamic Alignment (** ∆ _O_ **).** Real-world environments are non-stationary and may provide corrective instructions within feedback to steer the agent away from obsolete assumptions. We evaluate whether the agent can perform feedback-conditioned policy adjustment through two active guidance mechanisms: 

- **Value Redirection:** The environment notifies the agent 

that the valid parameter logic has shifted (e.g., “ID 1024 is deprecated, use ID 2048”). We verify if the agent can grasp this dynamic constraint and reissue the tool call with corrected values. 

- **Tool Redirection:** The environment signals that a specific tool schema is obsolete and explicitly suggests an alternative one. This tests whether the agent can abandon its pre-planned trajectory and strictly adhere to the new operational manual provided in the feedback. 

## **4.4. Tier 3: Reasoning Generalization**

Beyond perception and interaction, _Reasoning_ determines whether an agent can compose individual tool calls into a valid execution plan. Instead of triggering APIs sequentially according to memorized trajectories, a robust agent should infer the current rules governing tool behavior and construct an execution graph that satisfies the task dependencies. We evaluate this ability through two complementary dimensions: _Rule Reasoning_ , which tests whether the agent can adapt to changed functional definitions, and _Path Planning_ , which tests whether it can reorganize tool dependencies under altered execution structures. 

**Rule Reasoning (** ∆ _A_ **).** Models may memorize trainingtime rules instead of performing deduction from the current tool description. We introduce a _Calculation Shift_ by modifying the functional semantics of selected tools while keeping their interfaces unchanged. For example, a tool originally defined to return a value multiplied by 0 _._ 5 is redefined in the test setting to use a factor of 0 _._ 1. This experiment verifies whether the agent can derive the correct result from the updated rule description, or instead reverts to the memorized rule from the training distribution. 

**Path Planning (** ∆ _A_ **).** This dimension evaluates whether the agent can construct valid execution graphs under changed tool dependencies. We test whether it genuinely reasons over the current causal structure among tools, rather than overfitting to fixed tool chains observed during training, through two complementary sub-experiments: 

- **Trace Simplification:** We test whether the agent can improve execution efficiency when a shortcut becomes available. Specifically, we introduce a composite tool that functionally replaces a multi-step tool chain used during training. The agent should recognize the new affordance and select the efficient composite tool, rather than rigidly following the previously memorized multi-step trajectory. 

- • **Logic Inversion:** We test robustness to causal reversal in the tool dependency graph. At test time, we invert the documented information-acquisition order, for example by making the output of tool _B_ a prerequisite for invoking tool _A_ . This verifies whether the agent can resolve preconditions from the current dependency graph, or in- 

5 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

stead adheres to the fixed topological order learned from training trajectories. 

## **4.5. Tier 4: Internalization Generalization**

Internalization generalization evaluates whether an agent has learned task-level principles that go beyond local tool invocation patterns. At this level, a robust agent should not only execute valid tool-use trajectories, but also recognize when a task is infeasible under the current constraints and transfer abstract problem-solving structures across domains. We examine this through two capabilities: _Active Refusal_ , which tests solvability boundary recognition, and _Domain Transfer_ , which tests whether learned reasoning topologies can be reused in semantically different environments. 

**Active Refusal (** ∆ _Q ∪_ ∆ _O_ **).** A robust agent should determine whether a task is solvable given the available information and executable tools, rather than forcing a plausible but unsupported answer. We evaluate this boundary-awareness ability through two insufficient-condition scenarios: 

- **Missing Condition:** We remove necessary conditions from the user query through a human-verified process, making the task theoretically unsolvable due to information deficiency. This tests whether the agent can detect the logical incompleteness of the request and refuse to answer, instead of fabricating missing information to force completion. 

- **Fatal Error:** We simulate an unrecoverable failure where a necessary tool returns a fatal error and no alternative tool is available. This tests whether the agent can recognize the resulting operational deadlock and conclude that the task is currently unexecutable, rather than repeatedly retrying or hallucinating a successful result. 

**Domain Transfer (** ∆ _D_ **).** This dimension evaluates whether the agent can transfer internalized problem-solving structure across domains. We introduce a _Holistic Domain Shift_ , where user queries, tool definitions, and environmental observations change jointly. For example, we migrate the testing environment from an address-query scenario to a medical-registration scenario. Although the surface semantics and interfaces change substantially, the underlying causal structure is preserved as a latent structural invariance. This experiment tests whether the agent can re-ground the same abstract reasoning topology, such as a search-selectconfirm chain, in a novel target domain rather than overfitting to domain-specific lexical or procedural cues. 

## **5. Key Observations**

Synthesizing the results across the four tiers of generalization, we distill observations regarding the behavioral divergence between SFT and RL in open-world agentic tasks. 

### Tier 1: Tool Perception

RL achieves semantic grounding through interaction while SFT relies on brittle symbolic anchoring that degrades as fitting increases. 

As illustrated in Figure 4, we observe a consistent degradation pattern where robustness declines as training steps increase. Specifically, in the Semantic Trap and Identity Erasure experiments, the SFT model displays a sharp increase in TER accompanied by a significant drop in accuracy. The dashed blue line indicates that SFT frequently invokes the wrong tools when surface-level names are perturbed. Conversely, while RL also experiences some performance decay due to overfitting, it maintains a consistently lower error rate and higher accuracy retention compared to SFT. The RL agent demonstrates superior resistance to adversarial descriptions and effectively ignores misleading name cues. 

This disparity stems from SFT’s reliance on _symbolic anchoring_ , where the model acts as a superficial pattern matcher that collapses once surface tokens are decoupled from their semantics. In contrast, the penalty-driven nature of RL necessitates _semantic grounding_ , compelling the agent to scrutinize functional descriptions rather than memorizing rigid name-context associations. 

### Tier 2: Interaction with Guidance

RL leverages explicit guidance for dynamic policy adaptation, while SFT exhibits trajectory inertia and often hallucinates outcomes under corrective feedback. 

As illustrated in Figure 5, we observe a distinct behavioral divergence dependent on feedback clarity. Under ambiguous signals like null returns, both models exhibit performance degradation. Crucially, this failure mode follows a clear trend where the inability to adapt intensifies as training progresses. As the models become more fitted to the training distribution, their capacity to actively explore under uncertainty progressively declines. A significant disparity emerges under explicit tool redirection. Qualitative case studies reveal that SFT tends to interpret observations as successful confirmations, even when the feedback explicitly redirects the agent. Consequently, it ignores the guidance and hallucinates successful observations to force the continuation of its pre-planned trajectory. In contrast, RL maintains high adaptability by parsing the instruction and migrating to the new tool immediately, and then continues reasoning. 

We hypothesize that this behavioral divergence stems from differences in training paradigms. SFT is optimized on clean demonstrations where observations consistently validate actions. This likely conditions the model to disregard the causal link between feedback content and the subsequent policy, thereby making its behavior resemble an open-loop 

6 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

<!-- Start of picture text -->
Tier1:Noise Injection Tier1:Synonymous Rewriting Tier1:Semantic Trap Tier1:Identity Erasure<br>0 200 400 600 800 0 200 400 600 800 0 200 400 600 800 0 200 400 600 800<br>10.0 8.0 60.0 60.0<br>40.0 45.0<br>5.0 4.0<br>20.0 30.0<br>0.0 0.0<br>15.0<br>0.0<br>-5.0 -4.0 0.0<br>-20.0<br>-10.0 -8.0 -15.0<br>-40.0<br>0 50 100 150 200 250 0 50 100 150 200 250 0 50 100 150 200 250 0 50 100 150 200 250<br>SFT Accuracy Delta SFT TER Delta RL Accuracy Delta RL TER Delta<br>Figure 4. Accuracy Delta and TER in Tier-1 Perception. SFT exhibits brittle symbolic anchoring and underperforms compared to RL<br>when tool semantics shift. For detailed case analyses, refer to Appendix E. Delta represents the performance gap relative to the closed-set E. Delta represents the performance gap relative to the closed-set. Delta represents the performance gap relative to the closed-set<br>baseline. Setup and absolute values are provided in Appendix C and D. C and D. and D. D..<br>Tier2: Error Return Tier2: Null Return Tier2: Value Redirection Tier2: Tool Redirection<br>0 200 400 600 800 0 200 400 600 800 0 200 400 600 800 0 200 400 600 800<br>0<br>5 1.2 1.2<br>10 0.6 10 0.5 0 0<br>0.9 0.9<br>0.5 5 10<br>20 0.3<br>20 10 0.6 0.6<br>0.3 20<br>30 0.2 30 0.2 1520 0.3 30 0.3<br>40 0.0 40 0.0 25 0.0 40 0.0<br>30<br>50 50 -0.3<br>0 50 100 150 200 250 0 50 100 150 200 250 0 50 100 150 200 250 0 50 100 150 200 250<br>SFT Accuracy Delta SFT AES Score RL Accuracy Delta RL AES Score<br>Metric Delta (%)<br>AES Score<br>Accuracy Delta (%)<br><!-- End of picture text -->

_Figure 4._ Accuracy Delta and TER in Tier-1 Perception. SFT exhibits brittle symbolic anchoring and underperforms compared to RL when tool semantics shift. For detailed case analyses, refer to Appendix E. Delta represents the performance gap relative to the closed-set E. Delta represents the performance gap relative to the closed-set. Delta represents the performance gap relative to the closed-set baseline. Setup and absolute values are provided in Appendix C and D. C and D. and D. D.. 

_Figure 5._ Accuracy Delta and AES Score in Tier-2 Interaction. Both RL and SFT degrade under ambiguous feedback, but RL maintains superior resilience under explicit guidance while SFT fails to adapt. Delta represents the performance gap relative to the closed-set baseline. Setup and absolute values are provided in Appendix C and D. 

execution policy. Conversely, RL encourages a more closedloop behavior because ignoring error signals is penalized during interaction. This interaction mechanism potentially forces the agent to treat environmental observations as critical state updates, ensuring that explicit environmental instructions are prioritized to maximize reward. 

### Tier 3: Reasoning Generalization

RL demonstrates generalization in local adaptation, yet both paradigms suffer substantial degradation under global dependency inversion. 

As illustrated in Figure 6, RL exhibits superior generalization in local optimization tasks. In _Trace Simplification_ , the RL model achieves the lowest ATCL, indicating it successfully abandons the memorized training-time sequence to utilize efficient composite tools. Similarly, in _Rule Reasoning_ , RL outperforms SFT by dynamically adhering to updated calculation logic, whereas SFT shows a stronger tendency to regress to memorized training constants. 

However, a critical shared failure emerges in _Logic Inversion_ . When the causal dependency between tools is reversed (e.g., shifting from _A → B_ to _B → A_ ), both SFT and RL suffer precipitous performance drops. Qualitative anal- 

ysis in Appendix E reveals that despite the documentation explicitly stating the new prerequisite order, both models frequently hallucinate the existence of the training-set topology. This suggests that while RL generalizes well to local rule shifts, both paradigms overfit to the temporal order of action sequences, treating the dependency graph as a fixed action order rather than a dynamically specified logical structure. 

### Tier 4: Boundary Awareness

Both paradigms struggle with boundary awareness in unsolvable states, but exhibit distinct failure patterns: SFT often fails to perceive fatal feedback, whereas RL perceives the failure but still favors forced completion. 

As illustrated in Figure 7, both models struggle to identify unsolvable queries, leading to low refusal success rates when tools are unavailable. However, a fine-grained analysis of non-refusal cases under _Fatal Error_ scenarios reveals that SFT and RL fail through qualitatively distinct mechanisms. Case studies in Appendix E.4.1 show that upon receiving an error, SFT directly outputs an unsupported answer without acknowledging the error at all, effectively treating the error observation as if it were a normal return value. In contrast, RL explicitly recognizes the failure (e.g., “It seems the 

7 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

<!-- Start of picture text -->
Close Environment Open Environment<br><!-- End of picture text -->

_Figure 6._ Accuracy comparison on Tier 1-Instruction Robustness (left) and Tier 3-Rule Reasoning & Path Planning (right), evaluated at the stable training phase. While SFT models exhibit degradation across all perturbations, RL models show drops primarily under logic inversion and query variations. Detailed setups and full training dynamics are provided in Appendices C and D. 

<!-- Start of picture text -->
Accuracy (%) Rejection Rate (%)<br>Close Environment Open Environment<br><!-- End of picture text -->

_Figure 7._ Accuracy in Tier 1-Schema Adaptability, Tier 2-Format Adaptability, and Tier 4-Domain Transfer (left) and Refusal Rate in Tier 4-Active Refusal (right), evaluated at the stable training phase. Both SFT and RL models are robust to simple format changes, whereas SFT shows significant degradation under domain transfer. Both methods demonstrate limited active refusal for unsolvable queries. Detailed setups and full training dynamics are provided in Appendices C and D. 

tool is not available”), demonstrating a notably high error awareness rate, yet it still proceeds to fabricate an answer rather than issuing a refusal. 

This divergence is consistent with the open-loop versus closed-loop dichotomy observed in earlier tiers. SFT’s failure is perceptual: its open-loop policy does not parse environmental feedback, so the error signal is simply ignored. RL’s failure, however, is more decisional: it perceives the error but still favors completion, which is consistent with a _teleological bias_ induced by outcome-oriented rewards. Because training rewards presuppose that every problem is solvable, the policy learns to provide an answer at all costs, prioritizing completion over honest refusal. This is distinct from mere overconfidence; it reflects a structural limitation of outcome-based reward design that lacks an explicit incentive to abstain when the task is infeasible. Such persistent forced-completion behavior raises critical agent safety concerns, as models may sacrifice truthfulness for helpfulness in unpredictable open-world deployments. 

## **6. Perturbation-Augmented Fine-Tuning**

Our analysis reveals that SFT’s generalization decay stems from a distributional mismatch: standard SFT optimizes _L_ = _−_ E( _h,a_ ) _∼D_ clean[log _πθ_ ( _a|h_ )], where all training histories _h_ are drawn exclusively from successful executions. This confines the learned policy to a narrow manifold _H_ clean that excludes error states, ambiguous feedback, and symbolic variations. To bridge this gap, we propose 

**Perturbation-Augmented Fine-Tuning (PAFT)** , a data intervention strategy that augments _D_ clean with controlled trajectory-level perturbations: 

<!-- Start of picture text -->
D PAFT = (1  − α )  D clean ∪ α · G ( D clean) (2)<br><!-- End of picture text -->

where _G_ applies perturbation operators that expand the support of _h_ into regions containing anomalous observations, unsolvable states, and symbolic variants. Unlike standard augmentation that perturbs inputs in isolation, PAFT operates at the trajectory level, injecting perturbations midtrajectory and supervising the corrective continuations. 

## **6.1. Method**

**Environmental Feedback Perturbation (EFP).** To combat the open-loop trajectory inertia, we extend successful sub-trajectories by injecting stochastic observation anomalies that simulate unexpected environmental feedback. A standard chain is transformed via a generator _Genv_ as: 

<!-- Start of picture text -->
Genv<br>τ orig =  {ai, oi} −−−→ τ ′ =  {ai, o change , ai ′ , oi} (3)<br><!-- End of picture text -->

Here, _o_ change represents a feedback anomaly (e.g., tool redirection or value deprecation). The model is supervised to generate a corrective action _a_<sup>_′_</sup> _i_<sup>that recovers from the distur-</sup> bance, rather than blindly assuming success. This converts the open-loop pattern into a closed-loop recovery behavior. 

**Solvability Boundary Perturbation (SBP).** To address the boundary blindness identified in Tier 4, we construct negative samples that enforce explicit refusal behavior. A refusal 

8 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

_Table 1._ PAFT results across open environment tiers. 

|**Model**<br>**Tier-1**<br>Acc∆_↑_|**Tier-2**<br>Acc∆_↑_|**Tier-3**<br>Acc∆_↑_|**Tier-4**<br>RR_↑_|
|---|---|---|---|
|_Performance across training_|_stages_|||
|Base<br>-29.8|-8.5|-8.5|12.2|
|SFT-200<br>-67.7|-48.2|-39.9|0.3|
|+ PAFT<br>**+28.6**|**+26.5**|**+22.7**|**99.3**|
|SFT-400<br>-53.9|-45.4|-32.5|0.0|
|+ PAFT<br>**+5.6**|**+4.9**|-2.8|**97.8**|
|SFT-600<br>-51.3|-46.4|-33.0|0.1|
|+ PAFT<br>-2.5|-2.9|-10.7|**99.6**|
|SFT-800<br>-50.4|-45.3|-28.0|0.2|
|+ PAFT<br>-4.1|-5.3|-9.8|**99.6**|
|_Ablation: perturbation ratio _|_α (at 80_|_0 steps)_||
|_α_= 0_._2<br>-6.9|-7.7|-15.8|90.4|
|_α_= 0_._3(default)<br>**-4.1**|**-5.3**|**-9.8**|**99.6**|
|_α_= 0_._4<br>-5.3|-7.8|-11.1|96.4|
|_Ablation: individual compon_|_ents (at_|_800 steps, _|_α_= 0_._3_)_|
|EFP only<br>-30.1|**-3.2**|-27.0|1.7|
|SBP only<br>-38.9|-36.5|-31.7|**99.2**|
|SRP only<br>**-14.9**|-34.2|**-10.6**|2.1|

generator injects unrecoverable errors into the observation, modifying the trajectory to: 

<!-- Start of picture text -->
G refusal<br>τ orig =  {ai, oi, ai +1 } −−−→ τ ′ =  {ai, o fatal , a end } (4)<br><!-- End of picture text -->

where _o_ fatal signifies a fatal error with no alternative tools available, and _a_ end represents the explicit refusal action. This breaks the implicit “every problem is solvable” assumption in _D_ clean and teaches the model to halt execution rather than hallucinate. 

**Symbolic Representation Perturbation (SRP).** To decouple the symbolic anchoring identified in Tier 1, we apply surface-level augmentations to the tool definition space. An auxiliary agent performs synonymous rewriting and noise injection on tool names and documentation content. This forces the model to ground its decision-making in invariant functional semantics rather than memorized token sequences. To ensure evaluation fairness, all perturbation patterns are automatically generated without any prior knowledge of the specific variation types used in the test set, reducing the risk of information leakage. 

## **6.2. Experimental Results**

We evaluate PAFT on the most challenging tasks from each tier: _Semantic Trap_ (Tier-1), _Tool Redirection_ (Tier2), _Logic Inversion_ (Tier-3), and _Fatal Error_ (Tier-4). For Tiers 1–3, we report the Accuracy Delta (∆) relative to the closed-set baseline; for Tier-4, we report the absolute RR. We set _α_ = 0 _._ 3 as the default perturbation ratio. 

**Performance.** As shown in the upper portion of Table 1, 

PAFT yields consistent improvements across all training stages and tiers. For early-stage models, PAFT transforms severe degradation into positive deltas across Tiers 1–3, indicating that perturbation-augmented training can preemptively prevent overfitting to clean trajectories. 

**Ablation Study.** The lower portion of Table 1 reveals two key findings. 

_(1) Perturbation ratio._ Increasing _α_ from 0.2 to 0.3 yields clear gains across all tiers, while further increasing to 0.4 provides marginal or no additional benefit. We attribute this diminishing-return pattern to a trade-off between distributional coverage and signal quality: at low _α_ , the model is exposed to too few perturbed trajectories to learn robust recovery behaviors; as _α_ grows, the augmented data progressively covers more failure regions, but beyond a saturation point, an excessive proportion of perturbed samples dilutes the clean supervision signal and introduces conflicting gradients between normal task completion and anomaly handling, leading to no further improvement or even slight regression. The result suggests that _α_ =0 _._ 3 achieves a near-optimal balance between robustness and task performance. 

_(2) Component contributions._ EFP improves Tier-2 interaction adaptability, as the injected observation anomalies teach the model to parse and react to unexpected feedback rather than executing blindly along pre-planned trajectories. Notably, EFP contributes minimally to Tier-4 refusal, indicating that error adaptation and unsolvable-state recognition capture distinct capabilities. SBP almost exclusively restores Tier-4 refusal capability by introducing fatal error samples that break the implicit solvability assumption, while leaving other tiers largely unaffected, which suggests that, in our setting, boundary blindness is strongly tied to data coverage problem where the model never learns to refuse simply because _D_ clean contains no refusal demonstrations. SRP primarily enhances Tier-1 perception robustness and Tier-3 reasoning generalization, as symbolic perturbations force the model to attend to functional descriptions rather than surface-level identifiers, mitigating both symbolic anchoring and the associated downstream reasoning errors. This targeted effectiveness, where each component is necessary yet individually insufficient, confirms that PAFT is a structured, diagnosis-driven intervention rather than generic data augmentation. 

## **7. Conclusion**

In this paper, we formalize the **OpenAgent** setting and leverage a controlled sandbox to diagnose the open-world adaptability of LLM agents. Our systemic analysis reveals that both SFT and RL paradigms exhibit vulnerabilities when facing non-stationary environmental shifts. Furthermore, we propose PAFT, a disturbance-based intervention strategy designed to mitigate trajectory overfitting in SFT. 

9 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

## **Acknowledgements**

This work was supported by the Key Program of Jiangsu Science Foundation (BK20243012), the NSFC (62306133), and the 111 Center (No. B26023). 

## **Impact Statement**

This work studies robustness and failure modes of tool-use agents under open-world shifts. Its primary positive impact is to improve the reliability and safety of deployed agents by identifying conditions under which models ignore feedback, misuse tools, or hallucinate answers. Potential risks include misuse of stronger tool-use agents in automated decisionmaking systems. We mitigate this by emphasizing refusal behavior, boundary awareness, and controlled evaluation rather than unrestricted deployment. 

## **References**

- Achiam, J., Adler, S., Agarwal, S., Ahmad, L., Akkaya, I., Aleman, F. L., Almeida, D., Altenschmidt, J., Altman, S., Anadkat, S., et al. GPT-4 technical report. _arXiv preprint arXiv:2303.08774_ , 2023. 

- Anthropic. Introducing the model context protocol. https://www.anthropic.com/news/ model-context-protocol, 2024. 

- Bai, S., Chen, K., Liu, X., Wang, J., Ge, W., Song, S., Dang, K., Wang, P., Wang, S., Tang, J., Zhong, H., Zhu, Y., Yang, M., Li, Z., Wan, J., Wang, P., Ding, W., Fu, Z., Xu, Y., Ye, J., Zhang, X., Xie, T., Cheng, Z., Zhang, H., Yang, Z., Xu, H., and Lin, J. Qwen2.5-VL technical report. _arXiv preprint arXiv:2502.13923_ , 2025. 

- Cheng, Z.-J., Jia, Z.-Y., Zhou, Z., Li, Y.-F., and Guo, L.Z. TabFSBench: Tabular benchmark for feature shifts in open environment. In _Proceedings of the 42nd International Conference on Machine Learning_ , 2025. 

- Chu, T., Zhai, Y., Yang, J., Tong, S., Xie, S., Schuurmans, D., Le, Q. V., Levine, S., and Ma, Y. SFT memorizes, RL generalizes: A comparative study of foundation model post-training. In _Proceedings of the 42nd International Conference on Machine Learning_ , 2025. 

- Drouin, A., Gasse, M., Caccia, M., Laradji, I. H., Del Verme, M., Marty, T., Boisvert, L., Thakkar, M., Cappart, Q., Vazquez, D., Chapados, N., and Lacoste, A. WorkArena: How capable are web agents at solving common knowledge work tasks? In _Proceedings of the 41st International Conference on Machine Learning_ , 2024. 

- Feng, J., Huang, S., Qu, X., Zhang, G., Qin, Y., Zhong, B., Jiang, C., Chi, J., and Zhong, W. ReTool: Reinforcement learning for strategic tool use in LLMs. In _The Fourteenth_ 

_International Conference on Learning Representations_ , 2026. 

- Feng, W., Zhao, P., Jiang, G., Hao, C., Zhang, Y., Liu, G., and Wang, H. Pvpo: Pre-estimated value-based policy optimization for agentic reasoning. _arXiv preprint arXiv:2508.21104_ , 2025. 

- Gao, X., Xie, S., Zhai, J., Ma, S., and Shen, C. Mcp-radar: A multi-dimensional benchmark for evaluating tool use capabilities in large language models. _arXiv preprint arXiv:2505.16700_ , 2025. 

- Guo, L.-Z. and Li, Y.-F. Class-imbalanced semi-supervised learning with adaptive thresholding. In _Proceedings of the 39th International Conference on Machine Learning_ , 2022. 

- Guo, L.-Z., Zhang, Z.-Y., Jiang, Y., Li, Y.-F., and Zhou, Z.H. Safe deep semi-supervised learning for unseen-class unlabeled data. In _Proceedings of the 37th International Conference on Machine Learning_ , 2020. 

- Guo, L.-Z., Jia, L.-H., Shao, J.-J., and Li, Y.-F. Robust semisupervised learning in open environments. _Frontiers of Computer Science_ , 19, 2025. 

- Guo, Z., Cheng, S., Wang, H., Liang, S., Qin, Y., Li, P., Liu, Z., Sun, M., and Liu, Y. Stabletoolbench: Towards stable large-scale benchmarking on tool learning of large language models. In Ku, L., Martins, A., and Srikumar, V. (eds.), _Findings of the Association for Computational Linguistics_ , 2024. 

- He, J., Neville, J., Wan, M., Yang, L., Liu, H., Xu, X., Song, X., Pan, J. Z., and Zhou, P. Gentool: Enhancing tool generalization in language models through zero-to-one and weak-to-strong simulation. In Che, W., Nabende, J., Shutova, E., and Pilehvar, M. T. (eds.), _Findings of the Association for Computational Linguistics_ , 2025. 

- Hong, J., Zhao, C., Zhu, C., Lu, W., Xu, G., and Yu, X. DeepEyesV2: Toward agentic multimodal model. In _The Fourteenth International Conference on Learning Representations_ , 2026. 

- Hsieh, C.-Y., Chen, S.-A., Li, C.-L., Fujii, Y., Ratner, A., Lee, C.-Y., Krishna, R., and Pfister, T. Tool documentation enables zero-shot tool-usage with large language models. _ArXiv:2308.00675_ , 2023. 

- Huang, Y., Shi, J., Li, Y., Fan, C., Wu, S., Zhang, Q., Liu, Y., Zhou, P., Wan, Y., Gong, N. Z., and Sun, L. Metatool benchmark for large language models: Deciding whether to use tools and which to use. In _The Twelfth International Conference on Learning Representations_ , 2024. 

10 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

- Jia, L.-H., Guo, L.-Z., Zhou, Z., and Li, Y.-F. Realistic evaluation of semi-supervised learning algorithms in open environments. In _The Twelfth International Conference on Learning Representations_ , 2024. 

- Jimenez, C. E., Yang, J., Wettig, A., Yao, S., Pei, K., Press, O., and Narasimhan, K. SWE-bench: Can language models resolve real-world GitHub issues? In _The Twelfth International Conference on Learning Representations_ , 2024. 

- Koh, J. Y., Lo, R., Jang, L., Duvvur, V., Lim, M. C., Huang, P.-Y., Neubig, G., Zhou, S., Salakhutdinov, R., and Fried, D. VisualWebArena: Evaluating multimodal agents on realistic visual web tasks. In _Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics_ , 2024. 

- Li, M., Zhao, Y., Yu, B., Song, F., Li, H., Yu, H., Li, Z., Huang, F., and Li, Y. Api-bank: A comprehensive benchmark for tool-augmented llms. In Bouamor, H., Pino, J., and Bali, K. (eds.), _Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing_ , 2023. 

- Li, Y.-F., Guo, L.-Z., and Zhou, Z.-H. Towards safe weakly supervised learning. _IEEE Transactions on Pattern Analysis and Machine Intelligence_ , 43, 2021. 

- Li, Z., Zhang, H., Han, S., Liu, S., Xie, J., Zhang, Y., Choi, Y., Zou, J., and Lu, P. In-the-flow agentic system optimization for effective planning and tool use. In _The Fourteenth International Conference on Learning Representations_ , 2026. 

- Lin, Q., Wen, M., Peng, Q., Nie, G., Liao, J., Wang, J., Mo, X., Zhou, J., Cheng, C., Zhao, Y., Wang, J., and Zhang, W. Hammer: Robust function-calling for on-device language models via function masking. In _The Thirteenth International Conference on Learning Representations_ , 2025. 

- Liu, X., Yu, H., Zhang, H., Xu, Y., Lei, X., Lai, H., Gu, Y., Ding, H., Men, K., Yang, K., Zhang, S., Deng, X., Zeng, A., Du, Z., Zhang, C., Shen, S., Zhang, T., Su, Y., Sun, H., Huang, M., Dong, Y., and Tang, J. AgentBench: Evaluating LLMs as agents. In _The Twelfth International Conference on Learning Representations_ , 2024. 

- Liu, Z., Qiu, J., Wang, S., Zhang, J., Liu, Z., Ram, R., Chen, H., Yao, W., Heinecke, S., Savarese, S., Wang, H., and Xiong, C. MCPEval: Automatic MCP-based deep evaluation for AI agent models. In _Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing: System Demonstrations_ , 2025. 

- Ma, C., Zhang, J., Zhu, Z., Yang, C., Yang, Y., Jin, Y., Lan, Z., Kong, L., and He, J. AgentBoard: An analytical evaluation board of multi-turn LLM agents. In _Advances in Neural Information Processing Systems_ , volume 37, 2024. 

- Mialon, G., Fourrier, C., Wolf, T., LeCun, Y., and Scialom, T. Gaia: a benchmark for general ai assistants. In _The Twelfth International Conference on Learning Representations_ , 2024. 

- Mo, Y., Zhou, C., Cheng, F., Yu, J., Pan, L., Liu, F., Zhou, S., Li, H., Lin, Z., and Torr, P. Open-World LLM logical reasoning. In _Forty-third International Conference on Machine Learning_ , 2026. 

- Patil, S. G., Mao, H., Yan, F., Ji, C. C.-J., Suresh, V., Stoica, I., and Gonzalez, J. E. The Berkeley function calling leaderboard (BFCL): From tool use to agentic evaluation of large language models. In _Proceedings of the 42nd International Conference on Machine Learning_ , 2025. 

- Qian, C., Acikgoz, E. C., He, Q., Wang, H., Chen, X., Hakkani-Tur, D., Tur, G., and Ji, H.¨ ToolRL: Reward is all tool learning needs. In _Advances in Neural Information Processing Systems_ , volume 38, 2025. 

- Qu, C., Dai, S., Wei, X., Cai, H., Wang, S., Yin, D., Xu, J., and Wen, J.-R. COLT: Towards completeness-oriented tool retrieval for large language models. In _Proceedings of the 33rd ACM International Conference on Information and Knowledge Management_ , 2024. 

- Qu, C., Dai, S., Wei, X., Cai, H., Wang, S., Yin, D., Xu, J., and Wen, J. Tool learning with large language models: a survey. _Frontiers Comput. Sci._ , 19, 2025. 

- Qwen, Yang, A., Yang, B., Zhang, B., Hui, B., Zheng, B., Yu, B., Li, C., Liu, D., Huang, F., Wei, H., Lin, H., Yang, J., Tu, J., Zhang, J., Yang, J., Yang, J., Zhou, J., Lin, J., Dang, K., Lu, K., Bao, K., Yang, K., Yu, L., Li, M., Xue, M., Zhang, P., Zhu, Q., Men, R., Lin, R., Li, T., Tang, T., Xia, T., Ren, X., Ren, X., Fan, Y., Su, Y., Zhang, Y., Wan, Y., Liu, Y., Cui, Z., Zhang, Z., and Qiu, Z. Qwen2.5 technical report. _arXiv preprint arXiv:2412.15115_ , 2024. 

- Shao, J.-J., Zhang, B.-W., Yang, X.-W., Chen, B., Han, S., Jinghao, P., Wei, W.-D., Cai, G., Dong, Z., Guo, L.-Z., and Li, Y.-F. Chinatravel: An open-ended travel planning benchmark with compositional constraint validation for language agents. In _The Fourteenth International Conference on Learning Representations_ , 2026. 

- Shen, Y., Song, K., Tan, X., Li, D., Lu, W., and Zhuang, Y. HuggingGPT: Solving AI tasks with ChatGPT and its friends in Hugging Face. In _Advances in Neural Information Processing Systems_ , volume 36, 2023. 

11 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

- Shi, Z., Gao, S., Chen, X., Feng, Y., Yan, L., Shi, H., Yin, D., Ren, P., Verberne, S., and Ren, Z. Learning to use tools via cooperative and interactive agents. In Al-Onaizan, Y., Bansal, M., and Chen, Y. (eds.), _Findings of the Association for Computational Linguistics: EMNLP_ , volume EMNLP 2024 of _Findings of ACL_ , 2024. 

- Su, Z., Li, L., Song, M., Hao, Y., Yang, Z., Zhang, J., Chen, G., Gu, J., Li, J., Qu, X., et al. Openthinkimg: Learning to think with images via visual tool reinforcement learning. _arXiv preprint arXiv:2505.08617_ , 2025. 

- Team, G., Anil, R., Borgeaud, S., Alayrac, J.-B., Yu, J., Soricut, R., Schalkwyk, J., Dai, A. M., Hauth, A., Millican, K., et al. Gemini: a family of highly capable multimodal models. _arXiv preprint arXiv:2312.11805_ , 2023. 

- Team, K., Bai, Y., Bao, Y., Chen, G., Chen, J., Chen, N., Chen, R., Chen, Y., Chen, Y., Chen, Y., et al. Kimi k2: Open agentic intelligence. _arXiv preprint arXiv:2507.20534_ , 2025. 

- Trivedi, H., Khot, T., Hartmann, M., Manku, R., Dong, V., Li, E., Gupta, S., Sabharwal, A., and Balasubramanian, N. AppWorld: A controllable world of apps and people for benchmarking interactive coding agents. In _Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics_ , 2024. 

- Wang, J., Zerun, M., Li, Y., Zhang, S., Chen, C., Chen, K., and Le, X. GTA: A benchmark for general tool agents. In _Advances in Neural Information Processing Systems_ , volume 37, 2024a. 

- Wang, L., Ma, C., Feng, X., Zhang, Z., Yang, H., Zhang, J., Chen, Z., Tang, J., Chen, X., Lin, Y., Zhao, W. X., Wei, Z., and Wen, J. A survey on large language model based autonomous agents. _Frontiers Comput. Sci._ , 18, 2024b. 

- Wang, X., Wang, Z., Liu, J., Chen, Y., Yuan, L., Peng, H., and Ji, H. MINT: evaluating llms in multi-turn interaction with tools and language feedback. In _The Twelfth International Conference on Learning Representations_ , 2024c. 

- Wang, Z., Chang, Q., Patel, H., Biju, S., Wu, C.-E., Liu, Q., Ding, A., Rezazadeh, A., Shah, A., Bao, Y., and Siow, E. MCP-Bench: Benchmarking tool-using LLM agents with complex real-world tasks via MCP servers. In _The Fourteenth International Conference on Learning Representations_ , 2026. 

- Xie, T., Zhang, D., Chen, J., Li, X., Zhao, S., Cao, R., Hua, T. J., Cheng, Z., Shin, D., Lei, F., Liu, Y., Xu, Y., Zhou, S., Savarese, S., Xiong, C., Zhong, V., and Yu, T. OSWorld: Benchmarking multimodal agents for open-ended tasks in real computer environments. In _Advances in Neural Information Processing Systems_ , volume 37, 2024. 

- Xiong, Q., Huang, Y., Jiang, Z., Chang, Z., Zheng, Y., Li, T., and Li, M. Butterfly effects in toolchains: A comprehensive analysis of failed parameter filling in llm tool-agent systems. _arXiv preprint arXiv:2507.15296_ , 2025. 

- Xu, F. F., Song, Y., Li, B., Tang, Y., Jain, K., Bao, M., Wang, Z. Z., Zhou, X., Guo, Z., Cao, M., Yang, M., Lu, H. Y., Martin, A., Su, Z., Maben, L., Mehta, R., Chi, W., Jang, L., Xie, Y., Zhou, S., and Neubig, G. TheAgentCompany: Benchmarking LLM agents on consequential real-world tasks. In _Advances in Neural Information Processing Systems_ , volume 38, 2025a. 

- Xu, Z., Soria, A. M., Tan, S., Roy, A., Agrawal, A. S., Poovendran, R., and Panda, R. Toucan: Synthesizing 1.5 m tool-agentic data from real-world mcp environments. _arXiv preprint arXiv:2510.01179_ , 2025b. 

- Ye, J., Wu, Y., Gao, S., Huang, C., Li, S., Li, G., Fan, X., Zhang, Q., Gui, T., and Huang, X.-J. Rotbench: A multi-level benchmark for evaluating the robustness of large language models in tool learning. In _Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing_ , 2024. 

- Ye, J., Li, G., Gao, S., Huang, C., Wu, Y., Li, S., Fan, X., Dou, S., Ji, T., Zhang, Q., Gui, T., and Huang, X. Tooleyes: Fine-grained evaluation for tool learning capabilities of large language models in real-world scenarios. In _Proceedings of the 31st International Conference on Computational Linguistics_ , 2025. 

- Yin, S., Lei, T., and Liu, Y. Toolvqa: A dataset for multistep reasoning vqa with external tools. In _Proceedings of the IEEE/CVF International Conference on Computer Vision_ , 2025. 

- Yu, Q., Zhang, Z., Zhu, R., Yuan, Y., Zuo, X., Yue, Y., Dai, W., Fan, T., Liu, G., Liu, L., et al. DAPO: An open-source LLM reinforcement learning system at scale. In _Advances in Neural Information Processing Systems_ , volume 38, 2025. 

- Yuan, S., Song, K., Chen, J., Tan, X., Shen, Y., Ren, K., Li, D., and Yang, D. Easytool: Enhancing llm-based agents with concise tool instruction. In _Proceedings of the 2025 Conference of the Nations of the Americas Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers)_ , 2025. 

- Zeng, A., Lv, X., Zheng, Q., Hou, Z., Chen, B., Xie, C., Wang, C., Yin, D., Zeng, H., Zhang, J., et al. Glm-4.5: Agentic, reasoning, and coding (arc) foundation models. _arXiv preprint arXiv:2508.06471_ , 2025. 

12 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

- Zheng, Z., Yang, M., Hong, J., Zhao, C., Xu, G., Yang, L., Shen, C., and Yu, X. DeepEyes: Incentivizing “thinking with images” via reinforcement learning. In _The Fourteenth International Conference on Learning Representations_ , 2026. 

- Zhou, S., Xu, F. F., Zhu, H., Zhou, X., Lo, R., Sridhar, A., Cheng, X., Ou, T., Bisk, Y., Fried, D., Alon, U., and Neubig, G. WebArena: A realistic web environment for building autonomous agents. In _The Twelfth International Conference on Learning Representations_ , 2024. 

- Zhou, Z.-H. Open-environment machine learning. _National Science Review_ , 9, 2022. 

13 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

## **Appendix Contents**

|**A San**|**dbox Environment**|**15**|
|---|---|---|
|A.1|Database. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . .<br>15|
|A.2|Logical Architecture and Function Classification of Tools . . . . . . . . . . . . . .|. . . . . . . . . . . .<br>16|
|A.3|Tool Call Module . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . .<br>16|
|A.4|Training and Test Data<br>. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . .<br>17|
|**B**<br>**Exp**|**erimental Details**|**18**|
|**C Imp**|**lementation Details of OpenAgent Evaluation Task**|**20**|
|C.1|Tier 1: Perception Generalization . . . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . .<br>20|
||C.1.1<br>Instruction Robustness. . . . . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . .<br>20|
||C.1.2<br>Schema Adaptability. . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . .<br>20|
||C.1.3<br>Semantic Grounding. . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . .<br>20|
|C.2|Tier 2: Interaction Generalization. . . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . .<br>21|
||C.2.1<br>Format Adaptability. . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . .<br>21|
||C.2.2<br>Error Correction. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . .<br>21|
||C.2.3<br>Dynamic Alignment. . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . .<br>21|
|C.3|Tier 3: Reasoning Generalization . . . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . .<br>21|
||C.3.1<br>Rule Reasoning.<br>. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . .<br>21|
||C.3.2<br>Path Planning.<br>. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . .<br>22|
|C.4|Tier 4: Internalization Generalization. . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . .<br>22|
||C.4.1<br>Active Refusal<br>. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . .<br>22|
||C.4.2<br>Domain Transfer . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . .<br>22|
|**D Deta**|**iled Experimental Results**|**23**|
|D.1|Tier 1 Experiments . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . .<br>23|
|D.2|Tier 2 Experiments . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . .<br>29|
|D.3|Tier 3 Experiments . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . .<br>34|
|D.4|Tier 4 Experiments . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . .<br>37|
|**E**<br>**Cas**|**e Study**|**37**|
|E.1|Tier 1: Perception . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . .<br>37|
||E.1.1<br>Instruction Blurring & Information Redundancy<br>. . . . . . . . . . . . . .|. . . . . . . . . . . .<br>37|
||E.1.2<br>Schema Adaptability . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . .<br>37|
||E.1.3<br>Semantic Grounding . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . .<br>38|
|E.2|Tier 2: Interaction . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . .<br>39|

14 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

||E.2.1|Format Adaptability<br>. . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . . . . .<br>39|
|---|---|---|---|
||E.2.2|Value Redirection . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . . . . .<br>39|
||E.2.3|Tool Redirection<br>. . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . . . . .<br>40|
|E.3|Tier 3:|Reasoning . . . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . . . . .<br>41|
||E.3.1|Rule Learning. . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . . . . .<br>41|
||E.3.2|Path Planning . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . . . . .<br>41|
|E.4|Tier 4:|Internalization . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . . . . .<br>41|
||E.4.1|Fatal Error<br>. . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . . . . .<br>41|
||E.4.2|Information Missing . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . . . . .<br>42|
||E.4.3|Domain Shift . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . . . . .<br>42|

## **F Real-World API Validation**

## **43**

## **A. Sandbox Environment**

Since live APIs and MCP-based tool ecosystems are often unstable, version-dependent, and difficult to control during evaluation, we build a local code-running sandbox to simulate tool calls. Specifically, we create a Python sandbox environment class that includes database, tools implementation, and tool call module. Detailed information is as follows: 

## **A.1. Database**

We built our experimental database using public Point of Interest (POI) data from Beijing. Each POI entry has five key attributes: Phone Number, Address Name, Adname (Administrative Name), Coordinates (Latitude/Longitude), and Category. To strictly prevent data leakage and ensure the model relies entirely on tool usage rather than parameter memory to answer, we adopted an anonymization protocol. Specifically, all Address Names and Phone Numbers are replaced with unique, randomly generated alphanumeric strings and non-repeating number sequences, respectively. In addition, we strictly separate the training and test databases to avoid the model guessing the answers correctly by chance. Examples of the database data are shown in Table 2. 

_Table 2._ Samples of the Anonymized POI Knowledge Base 

|**Address Name**|**Phone Number**|**Adname**|**Coordinates**|**Category**|
|---|---|---|---|---|
|exotlwnk|00000000|chaoyang|116.413486, 39.992582|C1|
|cqhecbvi|00000001|haidian|116.318014, 40.029475|C2|
|rjztnhhg|00000002|changping|116.303367, 40.160994|C2|

15 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

_Figure 8._ Logic Diagram of Tools. Each line represents one tool. The start of an arrow denotes the input, while the end of an arrow denotes the output. 

## **A.2. Logical Architecture and Function Classification of Tools**

We designed the logical architecture of the tools in accordance with the logic diagram (Figure 8) and the following rules: 

1. For key-value (coords, tel, name) query functions: we only support the counterclockwise query method by default, i.e., coords can only be used to query tel; 

2. For the fare query function: we only allow queries by name; 

3. For the distance calculation function: we only allow latitude and longitude as input parameters; 

4. For non-key information queries: we allow any three key information to be used as input. 

The above rules also restrict the input type of each tool, and we finally obtained 12 tools, which are shown in Table 3. 

_Table 3._ Definitions of training set tools with categorized input and output types. 

|**Tool Name**|**Functional Description**|**Input**|**Output**|
|---|---|---|---|
|search<br>~~m~~ap<br>~~c~~oordinates|Retrieve location coordinates by exact name.|Name|Coords|
|administrativedivisionquery|Retrieve the district name (adname) by exact name.|Name|District|
|fetch<br>~~p~~oi<br>~~c~~ategory|Retrieve the category type by exact name.|Name|Category|
|find<br>~~c~~ontact<br>~~a~~t<br>~~c~~oords<br>reverse<br>~~g~~eocoding|Retrieve the telephone number using coordinates.<br>Retrieve the district name using coordinates.|Coords<br>Coords|Tel<br>District|
|venue<br>~~t~~ype<br>~~i~~dentifier|Retrieve the category type using coordinates.|Coords|Category|
|caller<br>~~i~~d<br>~~l~~ookup|Retrieve the name of a POI using its telephone number.|Tel|Name|
|regional<br>~~m~~apping<br>~~b~~y<br>~~t~~el|Retrieve the district name using telephone number.|Tel|District|
|service<br>~~c~~atalog<br>~~s~~earch|Retrieve the category type using telephone number.|Tel|Category|
|calculate<br>~~d~~istance<br>~~b~~y<br>~~c~~oords|Calculate distance between two coordinates.|Coords_×_2|Distance|
|get<br>~~a~~dult<br>~~c~~ost<br>~~b~~y<br>~~n~~ame|Calculate discounted adult price (0.5x) by name.|Name|Price|
|get<br>~~c~~hild<br>~~c~~ost<br>~~b~~y<br>~~n~~ame|Calculate discounted child price (0.2x) by name.|Name|Price|

## **A.3. Tool Call Module**

We set up the different tool call modules for RL training and evaluation testing in two different ways: 

- For RL training, we use the Verl Tool framework. The core idea is to run the code sandbox as a service on the server and open an external port. This port receives tool names and corresponding parameters, then sends back the tool call results. During each RL training run, we use the terminator _<_ tool ~~c~~ all _>_ to detect tool call commands. Specifically, when the model outputs this keyword, it stops generating text and triggers the tool detector. After processing all data in the same batch, the tool detector accesses the port uniformly to get results. These operations ensure only one tool call 

16 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

command is formed per conversation turn. The rest of the reinforcement learning process is the same as normal RL training. 

- For evaluation testing, we simulate multi-turn conversations and also detect tool calls via the terminator, which ensures that only one tool call is triggered in a single turn. If the model outputs _<_ /answer _>_ , it means the response is finished. 

In summary, the experimental environment of our study is composed of the query database, the sandbox code execution environment, the training and test sets, as well as the training and testing logic. The case of interaction is shown below. 

## **Interaction case**

_{_ "role": "user", "content": "I have the phone number ’00001433’. Can you help me find the location of the place associated with this number?" _}_ , _{_ "role": "assistant", "content": " _<_ tool ~~c~~ all _>{_ "tool": "caller ~~i~~ d ~~l~~ ookup", "args": _{_ "tel": "00001433" _}}<_ /tool ~~c~~ all _>_ " _}_ , _{_ "role": "user", "content": "Observation: _{_ "name": "sgtdfxvz" _}_ " _}_ , _{_ "role": "assistant", "content": "There is no direct tool available to retrieve the location from a phone number. Therefore, I will first use the phone number to look up the name of the place. _<_ tool ~~c~~ all _>{_ "tool": "search ~~m~~ ap ~~c~~ oordinates", "args": _{_ "name": "sgtdfxvz" _}}<_ /tool ~~c~~ all _>_ " _}_ , _{_ "role": "user", "content": "Observation: _{_ "location": "116.445179,39.953269" _}_ " _}_ , _{_ "role": "assistant", "content": "Now that I have the name of the place, I can proceed to find its location using the name-based lookup tool. _<_ answer _>_ 116.445179,39.953269 _<_ /answer _>_ " _}_ 

## **A.4. Training and Test Data**

Following data preparation in the main paper and the database and tools mentioned above, we employ a reverse-synthesis approach to generate training instances. By randomly sampling initial query conditions and target answers based on our defined tool set, we derive a symbolic reasoning trajectory. Formally, a symbolic trajectory _Tsym_ is defined as: 

<!-- Start of picture text -->
Tsym =  {c, t 1 → t 2 →· · · → tk, a} (5)<br><!-- End of picture text -->

where _c_ represents the initial condition (e.g., a specific location coordinate), _ti_ denotes the _i_ -th tool invocation in the chain, and _a_ is the final answer. To align these symbolic representations with human interaction patterns, we utilize an LLM 

17 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

<!-- Start of picture text -->
30 28.4%<br>Others<br>25 adult_cost<br>20.5% calc_distance<br>20 Others 15.0% price 13.6% basic_tel<br>17.0% 17.0% 2.8% 12.7% 34.1% 5.7%<br>15 5.7% basic_location<br>11.4% search_map_coords 17.4% 5.7%<br>10 24.4% caller_id_lookup 6.8% basic_name<br>5.7%<br>5 12.7% 28.4% single_adname<br>15.0%<br>find_contact<br>0<br>1 2 3 4 5 6 child_cost distance<br>Step Number<br>(a)  Step Distribution (b)  Tool Coverage (c)  Source Distribution<br>Percentage (%)<br><!-- End of picture text -->

_Figure 9._ Overall Statistics of the POI Multi-step Tool-calling Dataset: (a) Distribution of task complexity by step count; (b) Proportions of various tool invocations; (c) Composition of task scenarios and sources. 

to transform and smooth _Tsym_ into natural language question-answer pairs, resulting in a dataset of coherent multi-step tool-use queries. 

The final dataset comprises a total of 6,930 samples, divided into a training set ( _N_ = 6 _,_ 050) and a test set ( _N_ = 880). The dataset characteristics are designed to ensure rigorous evaluation: 

- **Complexity Distribution:** Both the training and test sets follow an identical distribution regarding the length of tool chains (e.g., 1-hop, 2-hop, ..., _k_ -hop). This ensures that the test set accurately reflects the structural complexity of the training data. 

- **Database Isolation:** To eliminate the possibility of data leakage, the training and test sets are synthesized from disjoint subsets of the underlying POI database. Consequently, the model must generalize its reasoning capabilities to unseen entities rather than recalling specific POI attributes seen during training. 

Regarding task complexity distribution, the dataset employs a stepped logical chain design covering a range from one to six steps; two-step tasks serve as the core backbone (accounting for 28.4%), while nearly 40% of the samples consist of high-difficulty reasoning tasks involving three or more steps, ensuring depth in the model’s learning of long-range tool invocation paths. 

In terms of tool and scenario distribution, the dataset exhibits a high degree of domain focus and balance: the core tool caller ~~i~~ d ~~l~~ ookup represents 24.4% of invocations, while ticket price calculation (adult/child cost) and geographic measurement (coords/distance) tools work in close coordination to form the foundation of task execution. This distribution is further corroborated by the source scenarios, where price-related (34.1%) and distance-related (28.4%) contexts dominate, providing the model with abundant material for numerical reasoning and logical alignment. 

Overall, this dataset covers basic attribute queries (e.g., POI names, phone numbers, and administrative divisions) and utilizes complex step distributions to force the model into semantic grounding rather than simple symbolic matching during extreme testing, such as anonymization or logical inversion. With its scientific tool sampling proportions and diverse business scenarios, this dataset serves as an ideal benchmark for training agents equipped with efficient path planning and robust generalization capabilities. In addition, we also provide the tools that can be used in Table 3. 

## **B. Experimental Details**

We adopt Qwen2.5-7B-Instruct as the backbone model and perform full-parameter fine-tuning based on the LLaMA-Factory framework. The AdamW optimizer is employed, with the learning rate and batch size set to 3e-5 and 2, respectively. The training process runs for a total of 800 steps, with a model checkpoint saved every 200 steps. For the RL paradigm, training leverages the GRPO tool calling algorithm implemented on the Verl-Tool platform. Notably, we use the normal GRPO to keep comparison fairly. The AdamW optimizer is also used here, with the learning rate set to 1e-6, the number of deployments configured to 8, and the total training steps set to 280. The PAFT algorithm differs from SFT only in the 

18 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

training dataset. The reward function was designed as follows: 

_Reward_ = 0 _._ 8 _× Acc_ + 0 _._ 2 _× scoreformat_ 

Note that we guarantee that both models are fully fitted and strictly control the amount of input data to ensure the fairness of the comparison. 

Testing Setup: During the inference phase, all models were uniformly constrained with identical sampling hyperparameters: the sampling temperature was fixed at 0.0, and the Top-p value was set to 1.0. For modifying the tool settings, we conducted three experiments and analyzed the results comprehensively. 

The system prompt template for training and testing is as follows: 

## **System Prompt**

<!-- Start of picture text -->
"You are a professional geographic information assistant. You can answer questions about places, phone<br>numbers, distances, and ticket prices by calling POI database tools.<br>### Available Tools:<br>[<br>{ "name": "search m ap c oordinates", "description": "Retrieve the location coordinates (longitude,latitude)<br>of a POI by its exact name.", "parameters": { "type": "object", "properties": { "name": { "type":<br>"string" }} , "required": ["name"] }} ,<br>{ "name": "administrative d ivision q uery", "description": "Retrieve the district name (adname) of a<br>POI by its exact name.", "parameters": { "type": "object", "properties": { "name": { "type": "string" }} ,<br>"required": ["name"] }} ,<br>{ "name": "fetch p oi c ategory", "description": "Retrieve the category type of a POI by its exact name.",<br>"parameters": { "type": "object", "properties": { "name": { "type": "string" }} , "required": ["name"] }} ,<br>{ "name": "find c ontact a t c oords", "description": "Retrieve the telephone number of a POI using its<br>location coordinates.", "parameters": { "type": "object", "properties": { "location": { "type": "string",<br>"description": "’lon,lat’ string" }} , "required": ["location"] }} ,<br>{ "name": "reverse g eocoding", "description": "Retrieve the district name of a POI using its location<br>coordinates.", "parameters": { "type": "object", "properties": { "location": { "type": "string",<br>"description": "’lon,lat’ string" }} , "required": ["location"] }} ,<br>{ "name": "venue t ype i dentifier", "description": "Retrieve the category type of a POI using its<br>location coordinates.", "parameters": { "type": "object", "properties": { "location": { "type": "string",<br>"description": "’lon,lat’ string" }} , "required": ["location"] }} ,<br>{ "name": "caller i d l ookup", "description": "Retrieve the name of a POI using its telephone number.",<br>"parameters": { "type": "object", "properties": { "tel": { "type": "string" }} , "required": ["tel"] }} ,<br>{ "name": "regional m apping b y t el", "description": "Retrieve the district name of a POI using its<br>telephone number.", "parameters": { "type": "object", "properties": { "tel": { "type": "string" }} ,<br>"required": ["tel"] }} ,<br>{ "name": "service c atalog s earch", "description": "Retrieve the category type of a POI using its<br>telephone number.", "parameters": { "type": "object", "properties": { "tel": { "type": "string" }} ,<br>"required": ["tel"] }} ,<br>{ "name": "calculate d istance b y c oords", "description": "Calculate the distance in meters between two<br>specific coordinates. Requires mode=2.", "parameters": { "type": "object", "properties": { "start l at":<br>{ "type": "number" } , "start l on": { "type": "number" } , "end l at": { "type": "number" } , "end l on": { "type":<br>"number" } , "mode": { "type": "integer", "description": "Verification code." }} , "required": ["start l at",<br>"start l on", "end l at", "end l on", "mode"] }} ,<br>{ "name": "get a dult c ost b y n ame", "description": "Calculate the discounted adult ticket price (0.5x)<br>by POI name. Requires mode=1.", "parameters": { "type": "object", "properties": { "name": { "type":<br>"string" } , "mode": { "type": "integer", "description": "Verification code." }} , "required": ["name",<br>"mode"] }} ,<br>{ "name": "get c hild c ost b y n ame", "description": "Calculate the discounted child ticket price (0.2x)<br>by POI name. Requires mode=1.", "parameters": { "type": "object", "properties": { "name": { "type":<br>"string" } , "mode": { "type": "integer", "description": "Verification code." }} , "required": ["name",<br>"mode"] }}<br>]<br>### Protocol:<br>1. ONE TOOL PER TURN : You MUST output only ONE tool call at a time. Wait for the observation before<br>doing anything else.<br>2. Tool Format : To use a tool, strictly output a JSON object with "name" and "arguments" keys. Example:<br>{ "name": "get t el b y n ame", "arguments": { "name": "Beijing H otel" }}<br>3. Final Answer : Wrap the result in < answer >< /answer > . Keep numerical answers to 1 decimal place."<br><!-- End of picture text -->

19 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

## **C. Implementation Details of OpenAgent Evaluation Task**

## **C.1. Tier 1: Perception Generalization**

## C.1.1. INSTRUCTION ROBUSTNESS.

- **Instruction Blurring:** We employ API calls to rewrite user queries, introducing complexities through syntactic variations (e.g., colloquialisms, rhetorical questions) or semantic ambiguities (e.g., implicit references, entity omissions). 

- **Information Redundancy:** We employ API calls to rewrite user queries by embedding core instructions within irrelevant contexts or lengthy background details, thereby simulating real-world informational noise. Please refer to the Appendix E.1.1 for further details. 

## C.1.2. SCHEMA ADAPTABILITY.

We alter the parameter dictionary key from the standard args to arguments, as shown in Appendix E.1.2. 

## C.1.3. SEMANTIC GROUNDING.

**Synonymous Rewriting** We assess the model’s capability to decouple functional intent from specific symbolic labels by replacing tool identifiers with semantically equivalent alternatives. This requires the model to move beyond simple string matching and demonstrate a deep understanding of the underlying natural language semantics. 

_Table 4._ Tool Mapping for **Synonym Rewriting** 

|**Original Tool Name**|_→_|**Synonymous Variant**|
|---|---|---|
|calculate<br>~~d~~istance<br>~~b~~y<br>~~c~~oords|_→_|calculate<br>~~s~~eparation<br>~~v~~ia<br>~~p~~ositions|
|search<br>~~m~~ap<br>~~c~~oordinates|_→_|lookup<br>~~l~~ocation<br>~~l~~atlong|
|get<br>~~a~~dult<br>~~c~~ost<br>~~b~~y<br>~~n~~ame|_→_|fetch<br>~~g~~rownup<br>~~p~~rice<br>~~u~~sing<br>~~n~~ame|

**Noise Injection** While maintaining the integrity of the tool schema, we introduce subtle syntactic perturbations into the tool names by inserting articles or determiners. We utilize this setup to evaluate the model’s tolerance to minor fluctuations in API naming and its stability when encountering non-standardized inputs. 

_Table 5._ Tool Mapping for **Surface Noise** 

|**Original Tool Name**|_→_|**Noisy Variant**|
|---|---|---|
|calculate<br>~~d~~istance<br>~~b~~y<br>~~c~~oords|_→_|calculate<br>~~t~~he<br>~~d~~istance<br>~~b~~y<br>~~c~~oords|
|search<br>~~m~~ap<br>~~c~~oordinates|_→_|search<br>~~f~~or<br>~~m~~ap<br>~~c~~oordinates|
|get<br>~~a~~dult<br>~~c~~ost<br>~~b~~y<br>~~n~~ame|_→_|get<br>~~1~~<br>~~a~~dult<br>~~c~~ost<br>~~b~~y<br>~~n~~ame|

**Semantic Adversarial** We designed a “description trap” where the familiar tool names are retained, but their functional descriptions are modified to explicitly forbid their previous usage. We require the model to overcome “path dependency” on familiar names, recognize the obsolescence of the original tool based on the updated description, and accurately invoke a new tool with matching functionality. 

_Table 6._ Changes in **Semantic Adversarial** 

|**Status**|**Tool Name**|**Functional Role**|
|---|---|---|
|Obsolete|get<br>~~a~~dult<br>~~c~~ost<br>~~b~~y<br>~~n~~ame|Service fee calculation only (Forbidden)|
|Target|fetch<br>~~g~~rownup<br>~~p~~rice<br>~~u~~sing<br>~~n~~ame|Actual ticket price calculation (Correct)|

**Identity Erasure** To isolate the model’s reliance on pure functional logic, we replace all human-readable identifiers with randomly generated UUIDs. In this extreme setting, we force the agent to perform reasoning based exclusively on the provided natural language descriptions. 

20 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

_Table 7._ Tool Mapping for **Identity Erasure** 

|**Semantic Tool Name**|_→_|**Anonymous Identifier**|
|---|---|---|
|calculate<br>~~d~~istance<br>~~b~~y<br>~~c~~oords|_→_|Tool<br>~~a~~2fb|
|search<br>~~m~~ap<br>~~c~~oordinates|_→_|Tool<br>~~c~~3d8|
|get<br>~~a~~dult<br>~~c~~ost<br>~~b~~y<br>~~n~~ame|_→_|Tool<br>~~r~~6t7|

## **C.2. Tier 2: Interaction Generalization**

## C.2.1. FORMAT ADAPTABILITY.

We diversify the structure of tool return values, transitioning from strictly structured JSON to less constrained formats such as Markdown tables or raw text logs. 

_Table 8._ Example of **Format Shift** in Tool Observations 

|**Type**||**Content**|**Structure**||
|---|---|---|---|---|
|**Structured (Old)**|"content"|:<br>"Observation:|_{_location:|116.35,40.22_}_ "|
|**Unstructured (New)**|"content"|:<br>"Observation:|_{_location is|116.35,40.22_}_ "|

## C.2.2. ERROR CORRECTION.

- **Error Return:** We simulate an explicit failure where the primary tool returns a specific error message (e.g., _“This tool is unavailable now”_ ) or a traceback. This scenario evaluates whether the agent can interpret explicit error signals and proactively switch to a redundant tool to resolve the blockage. 

- **Null Return:** We introduce an implicit failure where the primary tool returns a null value or an empty set ( _∅_ ) without any diagnostic warning. This tests the agent’s capability to detect anomalies based on the absence of content, rather than the presence of an error signal, and infer the necessity of a fallback execution. 

_Table 9._ Mapping of **Tool Failure Modes** and Expected Agent Responses 

|**Failure Type**||**Tool Observation**|**(Return)**|
|---|---|---|---|
|**Error Return**|_{_"error":|"This tool is|unavailable now"_}_|
|**Null Return**||""||

## C.2.3. DYNAMIC ALIGNMENT.

- **Value Redirection:** We simulate a scenario where the provided parameter logic is deprecated, and the environment returns a message including new, valid parameters. 

- **Tool Redirection:** We simulate a scenario where the primary tool returns an error explicitly stating it is obsolete while simultaneously suggesting an alternative tool. 

Importantly, we feed the interaction history into the API model (DouBao) to enable it to judge whether the target model refuses to answer. 

## **C.3. Tier 3: Reasoning Generalization**

## C.3.1. RULE REASONING.

We introduce rule conflicts in a special tool by modifying the mathematical constants in the tool description. Specifically, we kept the tool interface unchanged, but significantly adjusted the calculation ratio in the Prompt in the test set to examine whether the model relies on the memory from the training stage or can perform real-time reasoning based on immediate instructions. 

21 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

_Table 10._ Experimental Setup for **Calculation Shift** : Transitioning from Training Logic to Dynamic Test Logic 

|**Tool Name**|**Training rule (Origin)**|**Test rule (Changed)**|
|---|---|---|
|get<br>~~a~~dult<br>~~c~~ost|Discounted Price =**0.5x**Original Price|Discounted Price =**0.1x**Original Price|
|get<br>~~c~~hild<br>~~c~~ost|Discounted Price =**0.2x**Original Price|Discounted Price =**0.1x**Original Price|

## C.3.2. PATH PLANNING.

**Trace Simplification** We implement Tool shortcut to evaluate the agent’s ability to optimize its reasoning trajectory when more efficient paths become available. In this setup, we condense the functionality of two separate, sequential tools into a single, streamlined tool. This transformation reduces a multi-step dependency chain into a one-step execution. 

_Table 11._ Implementation of **Tool Consolidation** 

|**Original Multi-step Tools**|_→_|**Consolidated Tool (Single Step)**|
|---|---|---|
|search<br>~~m~~ap<br>~~c~~oords+find<br>~~c~~ontact<br>~~c~~oords|_→_|get<br>~~t~~el<br>~~b~~y<br>~~n~~ame|
|find<br>~~c~~ontact<br>~~c~~oords+caller<br>~~i~~d<br>~~l~~ookup|_→_|get<br>~~n~~ame<br>~~b~~y<br>~~l~~ocation|
|caller<br>~~i~~d<br>~~l~~ookup+search<br>~~m~~ap<br>~~c~~oords|_→_|get<br>~~l~~ocation<br>~~b~~y<br>~~t~~el|

**Logic Inversion** We simulate causal inversions in the dependency figure 8. During the testing phase, we intentionally reverse the information acquisition order described in the documentation, effectively inverting the preconditions of the tools. For example, if a task originally required Tool A to precede Tool B, we redefine the logic such that Tool A now depends on the output of Tool B. 

_Table 12._ Implementation of **Causal Reversal** 

|**Original Tool Logic**|_→_|**Reversed Causal Logic (Test)**|
|---|---|---|
|search<br>~~m~~ap<br>~~c~~oords: Name_→_**Coords**|_→_|lookup<br>~~n~~ame<br>~~b~~y<br>~~c~~oords: Coords_→_**Name**|
|find<br>~~c~~ontact<br>~~c~~oords: Coords_→_**Tel**|_→_|get<br>~~c~~oords<br>~~b~~y<br>~~t~~el: Tel_→_**Coords**|
|caller<br>~~i~~d<br>~~l~~ookup: Tel_→_**Name**|_→_|search<br>~~t~~el<br>~~b~~y<br>~~n~~ame: Name_→_**Tel**|

## **C.4. Tier 4: Internalization Generalization**

## C.4.1. ACTIVE REFUSAL

We implement Active Refusal by constructing “Missing Condition” and “Fatal Error” scenarios, transitioning tasks from being “inevitably solvable” to “deterministically unsolvable.” We utilize this setup to assess the model’s capability to recognize task boundaries—specifically, whether it can choose to proactively refuse the request rather than generating hallucinations when faced with information deficiency or execution deadlocks. The error tools include calculate ~~d~~ istance ~~b~~ y ~~c~~ oords, search ~~m~~ ap ~~c~~ oordinates, and get ~~a~~ dult ~~c~~ ost ~~b~~ y ~~n~~ ame. 

_Table 13._ Implementation of **Active Refusal** via Insufficient Conditions 

|**Scenarios**|**Original State (Solvable)**|**Perturbed State (Unsolvable)**|
|---|---|---|
|**Missing Condition**|Complete information in User Query|**Randomly excised**key entities/constraints|
|**Fatal Error**|Successful Tool Execution|**Irrecoverable error**with no alternative tools|

## C.4.2. DOMAIN TRANSFER

We implement a Domain Shift by changing the distributions of all three interactive elements: the user query, tool definitions, and environmental observations. Specifically, we transfer the evaluation environment from a geographic address lookup task to a medical registration task. While the surface presentation of the tasks is entirely altered, we retain the latent causal logical structure (Figure 8) invariance. 

22 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

_Table 14._ One-to-One Tool Mapping for Joint Domain Shift 

|**Geographic Domain (Source**_P_**train)**|**Medical Domain (Target**_P_**test)**|**Latent Logic**|
|---|---|---|
|search<br>~~m~~ap<br>~~c~~oordinates<br>administrative<br>~~d~~ivision<br>~~q~~uery<br>fetch<br>~~p~~oi<br>~~c~~ategory|get<br>~~m~~edical<br>~~f~~acility<br>~~c~~oords<br>query<br>~~m~~edical<br>~~a~~dministration<br>fetch<br>~~m~~edical<br>~~s~~ervice<br>~~t~~ype|_Name →Coords_<br>_Name →Admin_<br>_Name →Category_|
|find<br>~~c~~ontact<br>~~a~~t<br>~~c~~oords<br>reverse<br>~~g~~eocoding<br>venue<br>~~t~~ype<br>~~i~~dentifier|find<br>~~e~~mergency<br>~~h~~otline<br>~~a~~t<br>~~c~~oords<br>reverse<br>~~m~~edical<br>~~g~~eocoding<br>identify<br>~~c~~linic<br>~~c~~ategory|_Coords →Tel_<br>_Coords →Admin_<br>_Coords →Category_|
|caller<br>~~i~~d<br>~~l~~ookup<br>regional<br>~~m~~apping<br>~~b~~y<br>~~t~~el<br>service<br>~~c~~atalog<br>~~s~~earch|lookup<br>~~f~~acility<br>~~b~~y<br>~~h~~otline<br>query<br>~~m~~edical<br>~~r~~egion<br>~~b~~y<br>~~t~~el<br>classify<br>~~s~~ervice<br>~~b~~y<br>~~t~~el|_Tel →Name_<br>_Tel →Admin_<br>_Tel →Category_|
|calculate<br>~~d~~istance<br>~~b~~y<br>~~c~~oords<br>get<br>~~a~~dult<br>~~c~~ost<br>~~b~~y<br>~~n~~ame<br>get<br>~~c~~hild<br>~~c~~ost<br>~~b~~y<br>~~n~~ame|calculate<br>~~a~~mbulance<br>~~r~~oute<br>~~d~~istance<br>get<br>~~c~~heckup<br>~~c~~ost<br>~~b~~y<br>~~n~~ame<br>get<br>~~v~~accine<br>~~c~~ost<br>~~b~~y<br>~~n~~ame|_Math_(_mode_= 2)<br>_CostA_(_mode_= 1)<br>_CostB_(_mode_= 1)|

## **D. Detailed Experimental Results**

## **D.1. Tier 1 Experiments**

We report the full numerical results for all Tier-1 perception experiments. Tables 15–16 present accuracy and ATCL under instruction-level perturbations (Instruction Blurring and Information Redundancy). Table 17 reports performance under schema keyword changes. Tables 18–22 provide per-tool breakdowns across three semantic grounding experiments (Parameter Drift, Synonymous Rewriting, Noise Injection, Semantic Adversarial, and Identity Erasure), where each tool is evaluated independently to isolate tool-specific failure patterns. Across all settings, SFT exhibits increasing symbolic anchoring as training progresses, while RL maintains more stable accuracy retention. 

_Table 15._ Detailed Results of Instruction Blurring 

|**Model/Step**|**Acc (Abs)**|**ATCL Ratio**|**ATCL (Abs)**|**ATCL Ratio**|**ATCL Diff**|
|---|---|---|---|---|---|
|base|20.91|71.32|3.76|101.35|+0.05|
|sft-200|78.98|120.45|2.78|128.70|+0.62|
|sft-400|67.39|83.40|2.70|96.09|-0.11|
|sft-600|78.07|95.69|2.84|99.30|-0.02|
|sft-800|78.30|95.17|2.83|98.26|-0.05|
|rl-40|34.43|63.78|2.14|93.86|-0.14|
|rl-80|58.64|79.63|2.45|95.33|-0.12|
|rl-160|67.27|82.22|2.56|95.52|-0.12|
|rl-240|74.89|81.86|2.55|95.15|-0.13|
|rl-280|74.77|81.84|2.57|95.90|-0.11|

23 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

_Table 16._ Detailed Results of Information Redundancy 

|**Model/Step**|**Acc (Abs)**|**Acc Ratio**|**ATCL (Abs)**|**ATCL Ratio**|**ATCL Diff**|
|---|---|---|---|---|---|
|base|13.98|47.68|4.01|108.09|+0.30|
|sft-200|84.66|129.11|2.98|137.96|+0.82|
|sft-400|67.73|83.82|3.10|110.32|+0.29|
|sft-600|77.39|94.85|3.16|110.49|+0.30|
|sft-800|75.23|91.44|3.22|111.81|+0.34|
|rl-40|38.86|71.99|2.29|100.44|+0.01|
|rl-80|54.77|74.38|2.36|91.83|-0.21|
|rl-160|55.68|68.05|2.57|95.90|-0.11|
|rl-240|61.48|67.21|2.58|96.27|-0.10|
|rl-280|61.02|66.79|2.56|95.52|-0.12|

_Table 17._ Detailed Results of Schema Adaptability 

|**Model/Step**|**Acc (Abs)**|**Acc Ratio**|**ATCL (Abs)**|**ATCL Ratio**|**ATCL Diff**|
|---|---|---|---|---|---|
|base|31.82|108.53|3.72|100.27|+0.01|
|sft-200|76.59|116.81|2.55|118.06|+0.39|
|sft-400|82.95|102.66|2.86|101.78|+0.05|
|sft-600|81.93|100.42|2.87|100.35|+0.01|
|sft-800|81.59|99.17|2.88|100.00|+0.00|
|rl-40|61.82|114.52|2.49|109.21|+0.21|
|rl-80|82.39|111.88|2.74|106.61|+0.17|
|rl-160|81.48|99.58|2.70|100.75|+0.02|
|rl-240|92.27|100.86|2.66|99.25|-0.02|
|rl-280|92.39|101.13|2.66|99.25|-0.02|

24 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

_Table 18._ Detailed Results of Parameter Drift across three tools. T1: calculate ~~d~~ istance ~~b~~ y ~~c~~ oords; T2: search ~~m~~ ap ~~c~~ oordinates; T3: get ~~a~~ dult ~~c~~ ost ~~b~~ y ~~n~~ ame. 

|**Model**|**Tool**|**Acc (Abs)**|**Acc Ratio**|**Tool (Abs)**|**Tool Ratio**|**Tool Diff**|**Fail Rate**|**Ratio (Base)**|
|---|---|---|---|---|---|---|---|---|
||T1|25.80|87.99|3.68|99.19|-0.03|20.04|152.88|
|base|T2|26.14|89.15|3.74|100.81|+0.03|18.11|137.89|
||T3|30.11|102.69|3.71|100.00|+0.00|11.25|112.27|
|sft-200|T1|66.82|101.91|2.18|100.93|+0.02|0.15|96.85|
||T2|66.82|101.91|2.18|100.93|+0.02|0.15|97.73|
||T3|66.93|102.07|2.19|101.39|+0.03|6.80|85.91|
|f400|T1|80.80|100.00|2.80|99.64|-0.01|1.34|94.51|
|st-|T2|80.23|99.29|2.80|99.64|-0.01|1.17|82.49|
||T3|80.23|99.29|2.79|99.29|-0.02|0.95|100.24|
|f600|T1|81.36|99.72|2.86|100.00|+0.00|0.66|89.25|
|st-|T2|81.36|99.72|2.86|100.00|+0.00|0.41|100.00|
||T3|81.93|100.42|2.86|100.00|+0.00|0.47|100.00|
|sft-800|T1|81.82|99.45|2.88|100.00|+0.00|0.41|83.47|
||T2|81.14|98.63|2.88|100.00|+0.00|0.33|100.00|
||T3|81.82|99.45|2.88|100.00|+0.00|0.46|133.33|
|l40|T1|55.00|101.89|2.31|101.32|+0.03|21.60|112.32|
|r-|T2|53.98|100.00|2.27|99.56|-0.01|19.88|103.32|
||T3|54.32|100.63|2.29|100.44|+0.01|6.68|94.84|
||T1|73.41|99.69|2.54|98.83|-0.03|19.48|151.50|
|rl-80|T2|77.50|105.24|2.58|100.39|+0.01|16.46|127.98|
||T3|73.98|100.46|2.57|100.00|+0.00|2.20|112.15|
|l160|T1|81.93|100.13|2.64|98.51|-0.04|17.93|111.43|
|r-|T2|81.70|99.85|2.65|98.88|-0.03|15.63|97.41|
||T3|80.91|98.89|2.66|99.25|-0.02|0.11|50.11|
|l240|T1|91.59|100.12|2.69|100.37|+0.01|9.96|99.13|
|r-|T2|92.05|100.62|2.68|100.00|+0.00|9.90|99.03|
||T3|91.25|99.75|2.68|100.00|+0.00|0.00|100.00|
|l280|T1|91.59|100.25|2.69|100.37|+0.01|9.96|100.89|
|r-|T2|92.05|100.76|2.68|100.00|+0.00|9.73|99.01|
||T3|91.36|100.00|2.68|100.00|+0.00|0.00|100.00|

25 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

_Table 19._ Detailed Results of symbolic Drift (Synonymous Rewriting) across three tools ( **T1** : calculate ~~d~~ istance ~~b~~ y ~~c~~ oords _→_ calculate ~~s~~ eparation ~~v~~ ia ~~p~~ ositions; **T2** : search ~~m~~ ap ~~c~~ oordinates _→_ lookup ~~l~~ ocation ~~l~~ atlong; **T3** : get ~~a~~ dult ~~c~~ ost ~~b~~ y ~~n~~ ame _→_ fetch ~~g~~ rownup ~~p~~ rice ~~u~~ sing ~~n~~ ame). 

|**Model/Step**|**Tool**|**Acc (Abs)**|**Acc Ratio**|**ATCL (Abs)**|**ATCL Ratio**|**ATCL Diff**|**TER**|**TER Ratio**|
|---|---|---|---|---|---|---|---|---|
||T1|27.61|94.17|3.76|101.35|+0.05|11.10|110.76|
|**base**|T2|24.09|82.16|3.88|104.58|+0.17|18.22|223.78|
||T3|30.00|102.32|3.72|100.27|+0.01|12.49|95.28|
||T1|68.52|104.50|2.19|101.39|+0.03|3.10|39.21|
|**sft-200**|T2|57.39|87.52|2.23|103.24|+0.07|16.65|263.32|
||T3|66.59|101.56|2.20|101.85|+0.04|0.60|389.74|
||T1|80.45|99.57|2.79|99.29|-0.02|0.71|74.47|
|**sft-400**|T2|72.61|89.86|2.82|100.36|+0.01|8.67|1007.77|
||T3|71.25|88.18|2.92|103.91|+0.11|10.85|765.61|
||T1|80.45|98.60|2.86|100.00|0.00|0.47|100.00|
|**sft-600**|T2|76.48|93.74|2.88|100.70|+0.02|6.02|799.70|
||T3|77.50|94.99|2.86|100.00|0.00|5.27|714.63|
||T1|81.59|99.17|2.88|100.00|0.00|0.70|200.70|
|**sft-800**|T2|75.45|91.71|2.86|99.31|-0.02|5.16|787.93|
||T3|78.52|95.44|2.88|100.00|0.00|4.81|980.13|
||T1|53.07|98.31|2.26|99.12|-0.02|7.17|101.77|
|**rl-40**|T2|53.52|99.15|2.33|102.19|+0.05|5.06|91.35|
||T3|53.64|99.37|2.41|105.70|+0.13|14.38|74.76|
||T1|70.91|96.29|2.56|99.61|-0.01|6.89|350.51|
|**rl-80**|T2|75.45|102.46|2.55|99.22|-0.02|0.19|11.69|
||T3|68.98|93.67|2.55|99.22|-0.02|12.93|100.56|
||T1|79.89|97.64|2.65|98.88|-0.03|0.34|150.34|
|**rl-160**|T2|79.89|97.64|2.63|98.13|-0.05|0.19|100.84|
||T3|80.57|98.47|2.71|101.12|+0.03|14.49|90.02|
||T1|91.48|100.00|2.68|100.00|0.00|0.00|100.00|
|**rl-240**|T2|91.59|100.12|2.67|99.63|-0.01|0.00|100.00|
||T3|87.84|96.02|2.65|98.88|-0.03|10.63|105.74|
||T1|91.36|100.00|2.68|100.00|0.00|0.00|100.00|
|**rl-280**|T2|91.70|100.37|2.66|99.25|-0.02|0.00|100.00|
||T3|87.73|96.03|2.65|98.88|-0.03|10.55|106.83|

26 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

_Table 20._ Detailed Results of symbolic Drift (Noise Injection) across three tools ( **T1** : calculate ~~d~~ istance ~~b~~ y ~~c~~ oords _→_ calculate ~~t~~ he ~~d~~ istance ~~b~~ y ~~c~~ oords; **T2** : search ~~m~~ ap ~~c~~ oordinates _→_ search ~~f~~ or ~~m~~ ap ~~c~~ oordinates; **T3** : get ~~a~~ dult ~~c~~ ost ~~b~~ y ~~n~~ ame _→_ get ~~1 a~~ dult ~~c~~ ost ~~b~~ y ~~n~~ ame) 

|**Model/Step**|**Tool**|**Acc (Abs)**|**Acc Ratio**|**ATCL (Abs)**|**ATCL Ratio**|**ATCL Diff**|**TER Rate-Sub**|**TER Ratio**|
|---|---|---|---|---|---|---|---|---|
||T1|28.30|96.52|3.80|102.43|+0.09|9.77|97.46|
|**base**|T2|30.34|103.48|3.77|101.62|+0.06|8.01|98.34|
||T3|29.20|99.59|3.81|102.70|+0.10|11.31|86.26|
||T1|68.52|104.50|2.20|101.85|+0.04|4.26|53.79|
|**sft-200**|T2|66.36|101.20|2.17|100.46|+0.01|5.68|89.77|
||T3|63.98|97.58|2.29|106.02|+0.13|19.86|12830.28|
||T1|80.57|99.72|2.79|99.29|-0.02|1.07|112.90|
|**sft-400**|T2|80.45|99.57|2.79|99.29|-0.02|0.86|99.81|
||T3|58.64|72.57|2.82|100.36|+0.01|24.05|1697.62|
||T1|81.02|99.30|2.86|100.00|+0.00|0.23|50.12|
|**sft-600**|T2|82.16|100.70|2.86|100.00|+0.00|0.56|74.72|
||T3|64.43|78.97|2.87|100.35|+0.01|21.01|2848.55|
||T1|81.70|99.31|2.88|100.00|+0.00|0.35|100.35|
|**sft-800**|T2|81.59|99.17|2.87|99.65|-0.01|0.38|57.36|
||T3|66.93|81.35|2.88|100.00|+0.00|17.28|3518.94|
||T1|54.09|100.20|2.28|100.00|+0.00|6.73|95.48|
|**rl-40**|T2|54.20|100.41|2.27|99.56|-0.01|5.39|97.35|
||T3|53.75|99.57|2.35|103.07|+0.07|15.73|81.76|
||T1|72.50|98.45|2.52|98.05|-0.05|1.07|54.39|
|**rl-80**|T2|69.20|93.97|2.48|96.50|-0.09|2.49|155.84|
||T3|70.80|96.14|2.50|97.28|-0.07|15.34|119.31|
||T1|80.68|98.61|2.66|99.25|-0.02|0.35|151.04|
|**rl-160**|T2|78.07|95.42|2.64|98.51|-0.04|0.37|201.50|
||T3|82.27|100.55|2.68|100.00|+0.00|12.62|78.42|
||T1|91.25|99.75|2.68|100.00|+0.00|0.00|100.00|
|**rl-240**|T2|89.55|97.89|2.65|98.88|-0.03|0.00|100.00|
||T3|90.91|99.38|2.69|100.37|+0.01|10.37|103.18|
||T1|91.14|99.76|2.68|100.00|+0.00|0.00|100.00|
|**rl-280**|T2|89.77|98.26|2.65|98.88|-0.03|0.00|100.00|
||T3|90.91|99.51|2.70|100.75|+0.02|9.97|100.99|

27 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

_Table 21._ Detailed Results of Semantic Adversarial Experiments Across Three Tools ( **T1** : calculate ~~d~~ istance ~~b~~ y ~~c~~ oords _→_ calculate ~~s~~ eparation ~~v~~ ia ~~p~~ ositions; **T2** : search ~~m~~ ap ~~c~~ oordinates _→_ lookup ~~l~~ ocation ~~l~~ atlong; **T3** : get ~~a~~ dult ~~c~~ ost ~~b~~ y ~~n~~ ame _→_ fetch ~~g~~ rownup ~~p~~ rice ~~u~~ sing ~~n~~ ame) 

|**Model/Step**|**Tool**|**Acc (Abs)**|**Acc Ratio**|**ATCL (Abs)**|**ATCL Ratio**|**ATCL Diff**|**Old Tool Call**|
|---|---|---|---|---|---|---|---|
||T1|22.84|77.90|3.69|99.46|-0.02|7.90|
|**base**|T2|19.09|65.11|3.78|101.89|+0.07|1.71|
||T3|20.57|70.16|3.79|102.16|+0.08|1.60|
||T1|51.02|77.81|1.75|81.02|-0.41|16.14|
|**sft-200**|T2|32.05|48.88|1.51|69.91|-0.65|18.61|
||T3|21.14|32.24|1.56|72.22|-0.60|37.91|
||T1|49.43|61.18|2.64|93.95|-0.17|24.38|
|**sft-400**|T2|54.55|67.51|2.55|90.75|-0.26|7.28|
||T3|37.27|46.13|2.55|90.75|-0.26|24.19|
||T1|51.70|63.37|2.79|97.55|-0.07|22.70|
|**sft-600**|T2|56.59|69.36|2.73|95.45|-0.13|7.90|
||T3|39.77|48.74|2.76|96.50|-0.10|23.79|
||T1|51.59|62.71|2.80|97.22|-0.08|22.01|
|**sft-800**|T2|57.05|69.34|2.77|96.18|-0.11|7.62|
||T3|40.80|49.59|2.80|97.22|-0.08|23.35|
||T1|49.89|92.42|2.31|101.32|+0.03|8.41|
|**rl-40**|T2|50.45|93.46|2.31|101.32|+0.03|0.00|
||T3|44.20|81.88|2.28|100.00|+0.00|0.95|
||T1|59.09|80.24|2.60|101.17|+0.03|8.57|
|**rl-80**|T2|70.00|95.06|2.47|96.11|-0.10|0.09|
||T3|60.57|82.25|2.46|95.72|-0.11|2.21|
||T1|62.39|76.25|2.69|100.37|+0.01|7.52|
|**rl-160**|T2|71.82|87.78|2.52|94.03|-0.16|0.14|
||T3|63.64|77.78|2.56|95.52|-0.12|4.21|
||T1|67.95|74.28|2.73|101.87|+0.05|6.41|
|**rl-240**|T2|73.86|80.74|2.45|91.42|-0.23|0.14|
||T3|64.43|70.43|2.42|90.30|-0.26|4.60|
||T1|68.18|74.63|2.73|101.87|+0.05|6.36|
|**rl-280**|T2|73.52|80.47|2.45|91.42|-0.23|0.14|
||T3|64.32|70.40|2.41|89.93|-0.27|4.76|

28 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

_Table 22._ Detailed Results of Identity Erasure Experiments across Three Tools ( **T1** : calculate ~~d~~ istance ~~b~~ y ~~c~~ oords _→_ Tool ~~a~~ 2fb; **T2** : search ~~m~~ ap ~~c~~ oordinates _→_ Tool ~~c~~ 3d8; **T3** : get ~~a~~ dult ~~c~~ ost ~~b~~ y ~~n~~ ame _→_ Tool ~~r~~ 6t7) 

|**Model/Step**|**Tool**|**Acc (Abs)**|**Acc Ratio**|**ATCL (Abs)**|**ATCL Ratio**|**ATCL Diff**|**TER**|**TER Ratio**|
|---|---|---|---|---|---|---|---|---|
||T1|22.50|76.74|3.82|102.96|+0.11|19.13|136.39|
|**base**|T2|23.18|79.06|3.64|98.11|-0.07|20.74|154.37|
||T3|21.59|73.64|3.63|97.84|-0.08|17.87|167.15|
||T1|44.89|68.46|2.40|111.11|+0.24|13.83|403.36|
|**sft-200**|T2|41.70|63.60|2.60|120.37|+0.44|12.60|360.30|
||T3|59.20|90.29|2.46|113.89|+0.30|10.42|11489.26|
||T1|57.16|70.74|2.87|102.14|+0.06|11.71|3252.43|
|**sft-400**|T2|57.39|71.03|2.94|104.63|+0.13|10.93|2676.69|
||T3|60.00|74.26|2.88|102.49|+0.07|9.08|1251.29|
||T1|57.16|70.06|2.88|100.70|+0.02|10.51|6135.49|
|**sft-600**|T2|65.00|79.67|2.87|100.35|+0.01|7.20|2200.14|
||T3|65.68|80.50|2.87|100.35|+0.01|6.96|1849.99|
||T1|60.23|73.21|2.90|100.69|+0.02|9.45|7443.79|
|**sft-800**|T2|68.41|83.15|2.88|100.00|+0.00|5.62|1933.63|
||T3|66.82|81.22|2.89|100.35|+0.01|6.84|2700.19|
||T1|54.32|100.63|2.42|106.14|+0.14|12.27|93.04|
|**rl-40**|T2|51.25|94.94|2.40|105.26|+0.12|13.90|96.66|
||T3|52.84|97.89|2.29|100.44|+0.01|9.50|92.72|
||T1|65.23|88.58|2.50|97.28|-0.07|10.75|137.18|
|**rl-80**|T2|66.82|90.74|2.51|97.67|-0.06|11.32|24.26|
||T3|62.50|84.87|2.46|95.72|-0.11|7.06|121.13|
||T1|75.80|92.64|2.67|99.63|-0.01|8.12|102.58|
|**rl-160**|T2|75.45|92.21|2.66|99.25|-0.02|8.46|151.26|
||T3|72.73|88.89|2.75|102.61|+0.07|5.28|68.66|
||T1|87.84|96.02|2.63|98.13|-0.05|5.25|1150.75|
|**rl-240**|T2|91.02|99.50|2.67|99.63|-0.01|4.55|100.00|
||T3|79.43|86.83|2.65|98.88|-0.03|6.23|140.43|
||T1|87.84|96.15|2.62|97.76|-0.06|5.31|1150.75|
|**rl-280**|T2|91.02|99.63|2.67|99.63|-0.01|4.55|100.00|
||T3|79.20|86.69|2.64|98.51|-0.04|6.25|144.10|

## **D.2. Tier 2 Experiments**

We report the full numerical results for all Tier-2 interaction experiments. Table 23 shows that both paradigms are robust to simple format changes. Tables 24–26 present per-tool results under Null Return and Error Return, where we additionally report the AES score to quantify the agent’s active exploration after encountering failures. Tables 27–28 detail Tool Redirection and Value Redirection results, where the gap between SFT and RL is most pronounced: RL maintains near-perfect AES scores ( _>_ 0.86) while SFT scores collapse to near zero. 

29 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

_Table 23._ Detailed Results of Return Format Variation 

|**Model/Step**|**Acc (Abs)**|**Acc Ratio**|**Tool (Abs)**|**Tool Ratio**|**Tool Diff**|
|---|---|---|---|---|---|
|base|29.32|100.00|3.83|103.23|+0.12|
|sft-200|74.77|114.03|2.53|117.13|+0.37|
|sft-400|80.68|99.85|2.84|101.07|+0.03|
|sft-600|82.05|100.56|2.86|100.00|+0.00|
|sft-800|82.16|99.87|2.86|99.31|-0.02|
|rl-40|57.16|105.89|2.40|105.26|+0.12|
|rl-80|74.55|101.24|2.62|101.95|+0.05|
|rl-160|81.93|100.13|2.73|101.87|+0.05|
|rl-240|90.91|99.38|2.71|101.12|+0.03|
|rl-280|90.45|99.00|2.74|102.24|+0.06|

_Table 24._ Detailed Baseline Results of Solvable Problems Across Three Tools ( **T1** : calculate ~~d~~ istance ~~b~~ y ~~c~~ oords; **T2** : search ~~m~~ ap ~~c~~ oordinates; **T3** : get ~~a~~ dult ~~c~~ ost ~~b~~ y ~~n~~ ame) 

|**Model/Step**|**Tool**|**Acc (Abs)**|**Acc Ratio**|**ATCL (Abs)**|**ATCL Ratio**|**ATCL Diff**|**New Tool Call**|
|---|---|---|---|---|---|---|---|
||T1|22.50|76.74|3.88|104.58|+0.17|2.66|
|**base**|T2|25.80|87.99|3.90|105.12|+0.19|5.92|
||T3|25.00|85.27|3.90|105.12|+0.19|13.73|
||T1|68.18|103.98|2.16|100.00|+0.00|1.26|
|**sft-200**|T2|62.73|95.67|1.86|86.11|-0.30|0.31|
||T3|62.61|95.49|2.04|94.44|-0.12|1.11|
||T1|80.23|99.29|2.79|99.29|-0.02|1.06|
|**sft-400**|T2|80.34|99.43|2.77|98.58|-0.04|4.71|
||T3|78.75|97.46|2.77|98.58|-0.04|0.90|
||T1|80.57|98.75|2.86|100.00|+0.00|0.08|
|**sft-600**|T2|79.77|97.77|2.85|99.65|-0.01|2.43|
||T3|81.36|99.72|2.86|100.00|+0.00|0.91|
||T1|81.14|98.63|2.87|99.65|-0.01|0.04|
|**sft-800**|T2|82.16|99.87|2.85|98.96|-0.03|2.59|
||T3|82.16|99.87|2.88|100.00|+0.00|1.06|
||T1|51.93|96.20|2.42|106.14|+0.14|3.85|
|**rl-40**|T2|52.05|96.42|2.38|104.39|+0.10|4.39|
||T3|48.75|90.31|2.34|102.63|+0.06|9.32|
||T1|71.70|97.37|2.74|106.61|+0.17|5.60|
|**rl-80**|T2|66.02|89.65|2.44|94.94|-0.13|5.35|
||T3|63.75|86.57|2.54|98.83|-0.03|10.45|
||T1|82.27|100.55|2.84|105.97|+0.16|7.59|
|**rl-160**|T2|74.43|90.97|2.61|97.39|-0.07|3.89|
||T3|70.34|85.97|2.76|102.99|+0.08|10.42|
||T1|89.43|97.76|2.85|106.34|+0.17|5.58|
|**rl-240**|T2|90.00|98.38|2.69|100.37|+0.01|4.77|
||T3|88.75|97.02|2.70|100.75|+0.02|4.34|
||T1|88.86|97.26|2.85|106.34|+0.17|5.63|
|**rl-280**|T2|90.11|98.63|2.69|100.37|+0.01|4.90|
||T3|88.52|96.89|2.69|100.37|+0.01|4.47|

30 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

_Table 25._ Detailed Results of Solvable Problems with Null Return Across Three Tools ( **T1** : calculate ~~d~~ istance ~~b~~ y ~~c~~ oords; **T2** : search ~~m~~ ap ~~c~~ oordinates; **T3** : get ~~a~~ dult ~~c~~ ost ~~b~~ y ~~n~~ ame) 

|**Model/Step**|**Tool**|**Acc (Abs)**|**Acc Ratio**|**ATCL (Abs)**|**ATCL Ratio**|**ATCL Diff**|**New Tool Call**|
|---|---|---|---|---|---|---|---|
||T1|20.57|70.16|4.14|111.59|+0.43|3.13|
|**base**|T2|20.68|70.53|4.20|113.21|+0.49|8.98|
||T3|18.07|61.63|3.85|103.77|+0.14|13.48|
||T1|58.07|88.56|2.40|111.11|+0.24|1.33|
|**sft-200**|T2|43.07|65.69|2.08|96.30|-0.08|0.22|
||T3|30.45|46.44|2.11|97.69|-0.05|0.91|
||T1|55.57|68.77|2.82|100.36|+0.01|1.05|
|**sft-400**|T2|63.98|79.18|2.81|100.00|+0.00|4.37|
||T3|45.23|55.98|2.81|100.00|+0.00|0.81|
||T1|57.39|70.34|2.86|100.00|+0.00|0.04|
|**sft-600**|T2|59.89|73.40|2.85|99.65|-0.01|2.39|
||T3|44.66|54.74|2.88|100.70|+0.02|0.91|
||T1|57.73|70.17|2.87|99.65|-0.01|0.04|
|**sft-800**|T2|62.16|75.56|2.85|98.96|-0.03|2.47|
||T3|45.80|55.67|2.88|100.00|+0.00|1.10|
||T1|49.32|91.37|2.68|117.54|+0.40|3.27|
|**rl-40**|T2|37.84|70.10|2.45|107.46|+0.17|4.58|
||T3|26.25|48.63|2.58|113.16|+0.30|10.38|
||T1|55.80|75.77|2.83|110.12|+0.26|5.58|
|**rl-80**|T2|49.89|67.75|2.64|102.72|+0.07|4.57|
||T3|40.00|54.32|2.75|107.00|+0.18|10.26|
||T1|62.95|76.94|2.91|108.58|+0.23|6.84|
|**rl-160**|T2|55.34|67.64|2.77|103.36|+0.09|4.68|
||T3|40.80|49.87|2.73|101.87|+0.05|11.13|
||T1|69.20|75.64|2.87|107.09|+0.19|6.53|
|**rl-240**|T2|67.61|73.91|2.76|102.99|+0.08|5.71|
||T3|50.34|55.03|2.53|94.40|-0.15|7.60|
||T1|69.20|75.74|2.87|107.09|+0.19|6.37|
|**rl-280**|T2|68.30|74.76|2.77|103.36|+0.09|6.16|
||T3|50.00|54.73|2.51|93.66|-0.17|7.45|

31 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

_Table 26._ Detailed Results of Solvable Problems with Error Return Across Three Tools ( **T1** : calculate ~~d~~ istance ~~b~~ y ~~c~~ oords; **T2** : search ~~m~~ ap ~~c~~ oordinates; **T3** : get ~~a~~ dult ~~c~~ ost ~~b~~ y ~~n~~ ame) 

|**Model/Step**|**Tool**|**Acc (Abs)**|**Acc Ratio**|**Tool (Abs)**|**Tool Ratio**|**Tool Diff**|**AES Score (Abs)**|
|---|---|---|---|---|---|---|---|
||T1|20.68|70.53|4.00|107.82|+0.29|0.3325|
|**base**|T2|25.34|86.43|4.06|109.43|+0.35|0.7990|
||T3|20.68|70.53|3.93|105.93|+0.22|0.5779|
||T1|56.70|86.47|2.21|102.31|+0.05|0.0156|
|**sft-200**|T2|42.05|64.13|1.92|88.89|-0.24|0.0148|
||T3|30.23|46.10|2.06|95.37|-0.10|0.0351|
||T1|55.11|68.21|2.81|100.00|+0.00|0.0406|
|**sft-400**|T2|64.89|80.31|2.79|99.29|-0.02|0.3630|
||T3|44.55|55.14|2.79|99.29|-0.02|0.0297|
||T1|58.30|71.45|2.88|100.70|+0.02|0.0063|
|**sft-600**|T2|60.68|74.37|2.87|100.35|+0.01|0.2000|
||T3|45.23|55.44|2.88|100.70|+0.02|0.0270|
||T1|58.75|71.41|2.90|100.69|+0.02|0.0063|
|**sft-800**|T2|61.48|74.73|2.86|99.31|-0.02|0.2074|
||T3|45.68|55.52|2.89|100.35|+0.01|0.0351|
||T1|49.55|91.79|2.49|109.21|+0.21|0.3375|
|**rl-40**|T2|43.18|79.99|2.54|111.40|+0.26|0.4754|
||T3|31.70|58.73|2.52|110.53|+0.24|0.3509|
||T1|62.73|85.18|2.77|107.78|+0.20|0.4699|
|**rl-80**|T2|60.34|81.94|2.65|103.11|+0.08|0.6101|
||T3|44.77|60.80|2.64|102.72|+0.07|0.3775|
||T1|74.55|91.11|2.89|107.84|+0.21|0.5875|
|**rl-160**|T2|64.77|79.16|2.77|103.36|+0.09|0.5815|
||T3|40.57|49.58|2.70|100.75|+0.02|0.2126|
||T1|73.07|79.88|2.91|108.58|+0.23|0.4375|
|**rl-240**|T2|76.70|83.84|2.76|102.99|+0.08|0.5407|
||T3|53.98|59.01|2.63|98.13|-0.05|0.1566|
||T1|72.73|79.61|2.90|108.21|+0.22|0.4375|
|**rl-280**|T2|76.14|83.34|2.76|102.99|+0.08|0.5222|
||T3|54.32|59.46|2.63|98.13|-0.05|0.1475|

32 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

_Table 27._ Detailed Tool Redirection Results of Solvable Problems ( **T1** : calculate ~~d~~ istance ~~b~~ y ~~c~~ oords; **T2** : search ~~m~~ ap ~~c~~ oordinates; **T3** : get ~~a~~ dult ~~c~~ ost ~~b~~ y ~~n~~ ame) 

|**Model/Step**|**Tool**|**Acc (Abs)**|**Acc Ratio**|**Tool (Abs)**|**Tool Ratio**|**Tool Diff**|**AES Score (Abs)**|
|---|---|---|---|---|---|---|---|
||T1|23.52|80.22|4.12|111.05|+0.41|0.9906|
|**base**|T2|22.73|77.52|3.87|104.31|+0.16|1.0000|
||T3|23.18|79.06|4.07|109.70|+0.36|0.7189|
||T1|56.14|85.62|2.21|102.31|+0.05|0.1875|
|**sft-200**|T2|44.32|67.59|1.90|87.96|-0.26|0.1333|
||T3|29.66|45.23|2.04|94.44|-0.12|0.0865|
||T1|56.48|69.90|2.87|102.14|+0.06|0.3000|
|**sft-400**|T2|65.68|81.29|2.80|99.64|-0.01|0.4185|
||T3|46.59|57.66|2.81|100.00|+0.00|0.1919|
||T1|59.20|72.56|2.89|101.05|+0.03|0.0875|
|**sft-600**|T2|62.50|76.60|2.88|100.70|+0.02|0.2569|
||T3|48.30|59.20|2.92|102.10|+0.06|0.1676|
||T1|58.07|70.58|2.90|100.69|+0.02|0.1156|
|**sft-800**|T2|65.11|79.14|2.90|100.69|+0.02|0.3199|
||T3|48.86|59.39|2.94|102.08|+0.06|0.1946|
||T1|51.82|96.00|2.71|118.86|+0.43|0.9500|
|**rl-40**|T2|50.57|93.68|2.55|111.84|+0.27|0.9037|
||T3|47.50|88.00|2.65|116.23|+0.37|0.8649|
||T1|73.52|99.84|2.99|116.34|+0.42|0.9969|
|**rl-80**|T2|65.11|88.42|2.63|102.33|+0.06|0.9519|
||T3|62.05|84.26|2.86|111.28|+0.29|0.8757|
||T1|85.00|103.89|3.09|115.30|+0.41|1.0000|
|**rl-160**|T2|74.66|91.25|2.82|105.22|+0.14|0.9667|
||T3|71.02|86.80|3.18|118.66|+0.50|0.9432|
||T1|89.32|97.64|3.15|117.54|+0.47|0.9812|
|**rl-240**|T2|90.11|98.50|2.89|107.84|+0.21|0.9926|
||T3|88.86|97.14|3.18|118.66|+0.50|1.0000|
||T1|88.86|97.26|3.15|117.54|+0.47|0.9875|
|**rl-280**|T2|90.00|98.51|2.89|107.84|+0.21|0.9926|
||T3|88.52|96.89|3.18|118.66|+0.50|1.0000|

33 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

_Table 28._ Detailed Value Redirection Results Across Three Tools ( **T1** : calculate ~~d~~ istance ~~b~~ y ~~c~~ oords; **T2** : search ~~m~~ ap ~~c~~ oordinates; **T3** : get ~~a~~ dult ~~c~~ ost ~~b~~ y ~~n~~ ame) 

|**Model/Step**|**Tool**|**Acc (Abs)**|**Acc Ratio**|**Tool (Abs)**|**Tool Ratio**|**Tool Diff**|**AES Score (Abs)**|
|---|---|---|---|---|---|---|---|
||T1|30.45|103.85|4.49|121.02|+0.78|0.9500|
|**base**|T2|29.09|99.22|4.11|110.78|+0.40|0.6513|
||T3|28.86|98.43|4.01|108.09|+0.30|0.9963|
||T1|54.43|83.01|2.16|100.00|+0.00|0.0000|
|**sft-200**|T2|55.11|84.05|2.14|99.07|-0.02|0.0000|
||T3|46.59|71.05|2.24|103.70|+0.08|0.1296|
||T1|55.23|68.35|2.82|100.36|+0.01|0.0000|
|**sft-400**|T2|55.68|68.91|2.81|100.00|+0.00|0.0094|
||T3|56.70|70.17|2.84|101.07|+0.03|0.0444|
||T1|58.18|71.31|2.87|100.35|+0.01|0.0000|
|**sft-600**|T2|58.07|71.17|2.86|100.00|+0.00|0.0000|
||T3|55.57|68.11|2.87|100.35|+0.01|0.0222|
||T1|58.18|70.72|2.89|100.35|+0.01|0.0000|
|**sft-800**|T2|58.64|71.28|2.89|100.35|+0.01|0.0000|
||T3|56.02|68.09|2.92|101.39|+0.04|0.0407|
||T1|53.86|99.78|2.89|126.75|+0.61|1.0000|
|**rl-40**|T2|54.32|100.63|2.67|117.11|+0.39|0.6858|
||T3|53.18|98.52|2.50|109.65|+0.22|0.8667|
||T1|74.89|101.70|3.30|128.40|+0.73|0.9969|
|**rl-80**|T2|76.25|103.54|2.97|115.56|+0.40|0.7982|
||T3|72.16|97.99|2.83|110.12|+0.26|0.9556|
||T1|78.52|95.97|3.25|121.27|+0.57|0.9969|
|**rl-160**|T2|78.52|95.97|2.86|106.72|+0.18|0.6793|
||T3|81.48|99.58|2.98|111.19|+0.30|0.9889|
||T1|67.50|73.79|3.20|119.40|+0.52|1.0000|
|**rl-240**|T2|91.48|100.00|2.98|111.19|+0.30|0.8656|
||T3|91.14|99.63|2.99|111.57|+0.31|1.0000|
||T1|68.52|75.00|3.22|120.15|+0.54|1.0000|
|**rl-280**|T2|91.36|100.00|2.98|111.19|+0.30|0.8625|
||T3|91.36|100.00|2.99|111.57|+0.31|1.0000|

## **D.3. Tier 3 Experiments**

We report the full numerical results for all Tier-3 reasoning experiments. Table 29 presents Rule Reasoning results under modified calculation constants. Table 30 reports Trace Simplification results, where a composite tool replaces a multi-step chain; notably, RL models achieve lower ATCL, confirming their ability to adopt efficient shortcuts. Table 31 shows Logic Inversion results, where both paradigms suffer substantial accuracy drops, revealing a shared vulnerability to causal dependency reversal. 

34 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

_Table 29._ Detailed Results of Rule Reasoning Experiments ( **T1** : get ~~a~~ dult ~~c~~ ost ~~b~~ y ~~n~~ ame original price 0.5x _→_ 0.1x; **T2** : get ~~c~~ hild ~~c~~ ost ~~b~~ y ~~n~~ ame original price 0.2x _→_ 0.1x) 

|**Model/Step**|**Tool**|**Acc (Abs)**|**Acc Ratio**|**ATCL (Abs)**|**ATCL Ratio**|**ATCL Diff**|
|---|---|---|---|---|---|---|
|base|T1|27.95|95.33|3.76|101.35|+0.05|
||T2|30.45|103.85|3.79|102.16|+0.08|
|f200|T1|72.84|111.09|2.51|116.20|+0.35|
|st-|T2|76.02|115.94|2.50|115.74|+0.34|
|ft400|T1|68.98|85.37|2.85|101.42|+0.04|
|s-|T2|77.39|95.78|2.85|101.42|+0.04|
|f600|T1|69.32|84.96|2.87|100.35|+0.01|
|st-|T2|76.70|94.01|2.87|100.35|+0.01|
|f800|T1|68.86|83.70|2.88|100.00|+0.00|
|st-|T2|76.48|92.96|2.89|100.35|+0.01|
|l40|T1|61.14|113.26|2.45|107.46|+0.17|
|r-|T2|60.45|111.99|2.40|105.26|+0.12|
|l80|T1|79.66|108.17|2.65|103.11|+0.08|
|r-|T2|79.20|107.55|2.66|103.50|+0.09|
|l160|T1|83.07|101.53|2.70|100.75|+0.02|
|r-|T2|81.14|99.17|2.71|101.12|+0.03|
|l240|T1|92.39|100.99|2.67|99.63|-0.01|
|r-|T2|92.39|100.99|2.67|99.63|-0.01|
|l|T1|92.27|101.00|2.67|99.63|-0.01|
|r-280|T2|92.61|101.37|2.67|99.63|-0.01|

35 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

_Table 30._ Detailed Results of Trace Simplification Experiments ( **T1** : get ~~t~~ el ~~b~~ y ~~n~~ ame; **T2** : get ~~n~~ ame ~~b~~ y ~~l~~ ocation; **T3** : get ~~l~~ ocation ~~b~~ y ~~t~~ el). Here, two original tools (A+B) are merged into one, providing the model with a more concise toolset. 

|**Model/Step**|**Tool**|**Acc (Abs)**|**Acc Ratio**|**ATCL (Abs)**|**ATCL Ratio**|**ATCL Diff**|**New Tool Call**|
|---|---|---|---|---|---|---|---|
||T1|23.41|79.84|4.12|111.05|+0.41|6.11|
|**base**|T2|26.93|91.85|3.78|101.89|+0.07|27.68|
||T3|35.68|121.69|3.86|104.04|+0.15|11.73|
||T1|73.52|112.12|2.51|116.20|+0.35|0.63|
|**sft-200**|T2|71.70|109.35|2.49|115.28|+0.33|0.78|
||T3|74.77|114.03|2.53|117.13|+0.37|1.30|
||T1|81.59|100.98|2.86|101.78|+0.05|0.68|
|**sft-400**|T2|82.27|101.82|2.87|102.14|+0.06|0.87|
||T3|82.27|101.82|2.87|102.14|+0.06|1.43|
||T1|81.93|100.42|2.87|100.35|+0.01|0.55|
|**sft-600**|T2|81.14|99.45|2.87|100.35|+0.01|0.83|
||T3|80.68|98.88|2.87|100.35|+0.01|0.99|
||T1|81.93|99.59|2.87|99.65|-0.01|0.51|
|**sft-800**|T2|80.45|97.79|2.87|99.65|-0.01|0.95|
||T3|80.68|98.07|2.88|100.00|+0.00|1.06|
||T1|51.25|94.94|2.29|100.44|+0.01|4.71|
|**rl-40**|T2|59.55|110.32|2.39|104.82|+0.11|5.55|
||T3|53.07|98.31|2.21|96.93|-0.07|12.61|
||T1|67.84|92.12|2.51|97.67|-0.06|5.98|
|**rl-80**|T2|77.16|104.78|2.55|99.22|-0.02|7.27|
||T3|70.68|95.98|2.40|93.39|-0.17|13.18|
||T1|71.48|87.36|2.63|98.13|-0.05|6.18|
|**rl-160**|T2|81.25|99.30|2.60|97.01|-0.08|5.34|
||T3|71.36|87.22|2.40|89.55|-0.28|12.35|
||T1|90.68|99.13|2.68|100.00|+0.00|4.25|
|**rl-240**|T2|92.39|100.99|2.55|95.15|-0.13|6.56|
||T3|87.05|95.16|2.49|92.91|-0.19|14.86|
||T1|90.34|98.88|2.69|100.37|+0.01|4.33|
|**rl-280**|T2|92.50|101.25|2.55|95.15|-0.13|6.50|
||T3|87.73|96.03|2.49|92.91|-0.19|14.52|

_Table 31._ Detailed Results of Logic Inversion Experiments 

|**Model/Step**|**Acc (Abs)**|**Acc Ratio**|**ATCL (Abs)**|**ATCL Ratio**|**ATCL Diff**|
|---|---|---|---|---|---|
|base|20.23|69.00|4.24|114.29|+0.53|
|sft-200|16.93|25.82|2.06|95.37|-0.10|
|sft-400|13.41|16.60|2.85|101.42|+0.04|
|sft-600|15.11|18.52|2.89|101.05|+0.03|
|sft-800|39.66|48.21|2.43|84.38|-0.45|
|rl-40|37.39|69.27|2.17|95.18|-0.11|
|rl-80|41.25|56.02|2.03|78.99|-0.54|
|rl-160|44.66|54.58|2.06|76.87|-0.62|
|rl-240|43.41|47.45|1.79|66.79|-0.89|
|rl-280|43.64|47.77|1.81|67.54|-0.87|

36 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

## **D.4. Tier 4 Experiments**

We report the full numerical results for the Tier-4 domain shift experiment in Table 32. RL-280 retains 96.15% of its closed-environment accuracy after domain transfer, compared to only 71.96% for SFT-800. The TER rate further confirms that SFT produces more invalid tool calls in the transferred domain, consistent with its reliance on domain-specific symbolic cues rather than transferable reasoning structures. 

_Table 32._ Detailed Results of Domain Shift Experiments 

|**Model/Step**|**Acc (Abs)**|**Acc Ratio**|**ATCL (Abs)**|**ATCL Ratio**|**ATCL Diff**|**TER Rate**|
|---|---|---|---|---|---|---|
|base|26.82|91.47|3.96|106.74|+0.25|22.47|
|sft-200|39.43|60.13|2.38|110.19|+0.22|23.63|
|sft-400|54.55|67.51|3.00|106.76|+0.19|21.40|
|sft-600|54.66|66.99|2.90|101.40|+0.04|20.85|
|sft-800|59.20|71.96|2.90|100.69|+0.02|16.06|
|rl-40|45.11|83.57|2.23|97.81|-0.05|15.77|
|rl-80|56.82|77.16|2.37|92.22|-0.20|16.37|
|rl-160|73.52|89.86|2.64|98.51|-0.04|11.19|
|rl-240|87.73|95.90|2.72|101.49|+0.04|7.56|
|rl-280|87.84|96.15|2.74|102.24|+0.06|7.48|

## **E. Case Study**

## **E.1. Tier 1: Perception**

E.1.1. INSTRUCTION BLURRING & INFORMATION REDUNDANCY 

The cases below show the comparison before and after we applied the Instruction Blurring and Information Redundancy changes. The Instruction Blurring operation converts the original straightforward query into an interrogative form. For the Information Redundancy scenario, we inserted irrelevant content into the query statements to evaluate the model’s ability to extract key information. 

### **The example of Instruction Blurring**

_{_ **Old:** "Please calculate the distance in meters between Point A (location: 116.534120,39.903650) and Point B (name: ovxfhwlk)." **New:** "Spatially, what’s the meter gap between 116.534120,39.903650 and ovxfhwlk?" _}_ 

### **The example of Information Redundancy**

_{_ **Old:** "I have the tel info: ’00000687’. I want to find the location of this place." **New:** "Hello there, I hope you’re having a pleasant day! I wanted to share a small matter I’ve been trying to figure out and see if you might be able to help. Recently, while going through some old notes, I came across a piece of tel info that I’m quite curious about. The specific tel info I have is: ’00000687’. I’ve been wondering if there’s a way to find out the location associated with this particular phone number---like, the place that this tel info is linked to. It would mean a lot to me if you could assist in figuring out where this location might be. Thank you so much for taking the time to consider this!" _}_ 

## E.1.2. SCHEMA ADAPTABILITY

We alter the parameter dictionary key from the standard args to arguments, as shown below. 

37 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

**The comparison of schema adaptability** _{_ "role": " **Original system prompt** ", "content": "... Interaction Requirements: 1. Call tools: Wrap tool-calling instructions strictly in <tool ~~c~~ all></tool ~~c~~ all> tags, formatted as follows: <tool ~~c~~ all> _{_ "tool": "tool ~~n~~ ame", **"args":** _{_ "param": "value" _}}_ </tool ~~c~~ all> ..." _}_ , _{_ "role": " **Changed system prompt** ", "content": "... Interaction Requirements: 1. Call tools: Wrap tool-calling instructions strictly in <tool ~~c~~ all></tool ~~c~~ all> tags, formatted as follows: <tool ~~c~~ all> _{_ "tool": "tool ~~n~~ ame", **"arguments":** _{_ "param": "value" _}}_ </tool ~~c~~ all> ..." _}_ 

## E.1.3. SEMANTIC GROUNDING

Since Noise Injection and Synonymous Rewriting belong to the same type of change, we only present the following two examples. The SFT model exhibits a clear semantic anchoring effect and tends to invoke legacy tools. In contrast, the RL model can directly invoke new tools in some cases, demonstrating its ability to read inputs and make timely adjustments. 

### **SFT (Step 800): Error example of Noise Injection of search** **~~m~~ ap** **~~c~~ oordinates**

_{_ "role": "user", "content": "Please calculate the distance in meters between Point A (location: 116.272258,39.950537) and Point B (name: kkiybhpg)." _}_ , _{_ "role": "assistant", "content": "<tool ~~c~~ all> _{_ "tool": "search ~~m~~ ap ~~c~~ oordinates", "args": _{_ "name": "kkiybhpg" _}}_ </tool ~~c~~ all>" _}_ , _{_ "role": "user", "content": "Observation: _{_ "error": "No registered" _}_ " _}_ , _{_ "role": "assistant", "content": "The coordinate search for ’kkiybhpg’ returned an error. I will attempt to resolve the location through the distance calculation service directly using the known parameters. <tool ~~c~~ all> _{_ "tool": "calculate ~~d~~ istance ~~b~~ y ~~c~~ oords", "args": _{_ "start ~~l~~ at": 39.950537, "start ~~l~~ on": 116.272258, "end ~~l~~ at": 40.146428, "end ~~l~~ on": 116.49819, "mode": 2 _}}_ </tool ~~c~~ all>" _}_ 

### **RL (Step 280): Success example of Noise Injection for search** **~~m~~ ap** **~~c~~ oordinates**

_{_ "role": "user", "content": "Find the location coordinates for the place with name tyxbwszy." _}_ , _{_ "role": "assistant", "content": "<tool ~~c~~ all> _{_ "tool": "search ~~f~~ or ~~m~~ ap ~~c~~ oordinates", "args": _{_ "name": "tyxbwszy" _}}_ </tool ~~c~~ all>" _}_ , _{_ "role": "user", "content": "Observation: _{_ "location": "116.350646,40.222574" _}_ " _}_ 

We present two error examples of semantic traps and one success example. In the error scenarios, both SFT and RL directly call the old tool. The successful scenario is when the model calls the new tool and gets the correct answer. 

### **SFT (step 800): Error example of Semantic Trap for calculate** **~~d~~ istance** **~~b~~ y** **~~c~~ oords**

"Tool Description": "**calculate ~~d~~ istance ~~b~~ y ~~c~~ oords**: Returns the fixed distance specifically between Beijing (39.9042, 116.4074) and Shanghai (31.2304, 121.4737). This tool returns a static constant for API connectivity testing. Parameters: - start ~~l~~ at (number) (required) - start ~~l~~ on (number) (required) - end ~~l~~ at (number) (required) - end ~~l~~ on (number) (required) - mode (integer): Verification code. (required)" _{_ "role": "assistant", "content": "Given that neither POI has a recorded location in the database, we will use the fixed distance between Beijing and Shanghai for API connectivity testing. <tool ~~c~~ all> _{_ "tool": "calculate ~~d~~ istance ~~b~~ y ~~c~~ oords", "args": _{_ "start ~~l~~ at": 39.9042, "start ~~l~~ on": 116.4074, "end ~~l~~ at": 31.2304, "end ~~l~~ on": 121.4737, "mode": 2 _}}_ </tool ~~c~~ all>" _}_ , _{_ "role": "user", "content": "Observation: _{_ "distance": "300.0" _}_ " _}_ , _{_ "role": "assistant", "content": "<answer> **300.0** </answer>" _}_ 

38 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

### **RL (step 280): Error example of Semantic Trap for search** **~~m~~ ap** **~~c~~ oordinates**

"Tool Description": "**search ~~m~~ ap ~~c~~ oordinates**: Returns the fixed coordinates specifically for the POI ’Eiffel Tower’. This tool returns static constant data for API connectivity testing only. Parameters: - name (string) (required)." _{_ "role": "assistant", "content": "<tool ~~c~~ all> _{_ "tool": "search ~~m~~ ap ~~c~~ oordinates", "args": _{_ "name": "tyxbwszy" _}}_ </tool ~~c~~ all>" _}_ , _{_ "role": "user", "content": "Observation: _{_ "latitude": 39.90365, "longitude": 116.53412 _}_ " _}_ , _{_ "role": "assistant", "content": "I have retrieved the location coordinates using the ‘search ~~m~~ ap ~~c~~ oordinates‘ tool. The coordinates for the place with name tyxbwszy are <answer>39.90365,116.53412</answer>" _}_ 

### **RL (step 280): Success example of Semantic Trap for calculate** **~~s~~ eparation** **~~v~~ ia** **~~p~~ ositions**

_{_ "role": "assistant", "content": "I now have the coordinates of Point B: 116.496861, 39.982022. With both coordinates, I can now calculate the distance. <tool ~~c~~ all> _{_ "tool": "calculate ~~s~~ eparation ~~v~~ ia ~~p~~ ositions", "args": _{_ "start ~~l~~ at": 39.900073, "start ~~l~~ on": 116.266619, "end ~~l~~ at": 39.982022, "end ~~l~~ on": 116.496861, "mode": 2 _}}_ </tool ~~c~~ all>" _}_ , _{_ "role": "user", "content": "Observation: _{_ "distance": 21680.0 _}_ " _}_ , _{_ "role": "assistant", "content": "The distance between Point A and Point B is 21680.0 meters. <answer>21680.0</answer>" _}_ 

Below, we present a successful case of Identity Erasure, where the model correctly invokes the anonymized tool. 

### **Identity Erasure (Anonymized Tool tool** **~~r~~ 6t7)**

"Tool Description": "**tool ~~r~~ 6t7**: Calculate the discounted adult ticket price (0.5x) by POI name. Requires mode=1. Parameters: - name (string) (required) - mode (integer): Verification code. (required)" _{_ "role": "assistant", "content": "Now that we have the name of the place, we can find the original adult ticket price using the ‘tool ~~r~~ 6t7‘ with mode=1. <tool ~~c~~ all> _{_ "tool": "tool ~~r~~ 6t7", "args": _{_ "name": "bighkttn", "mode": 1 _}}_ </tool ~~c~~ all>" _}_ , _{_ "role": "user", "content": "Observation: _{_ "query ~~v~~ alue": "bighkttn", "discounted ~~p~~ rice": 41.5 _}_ " _}_ , _{_ "role": "assistant", "content": "The adult ticket price has been retrieved. <answer>41.5</answer>" _}_ 

## **E.2. Tier 2: Interaction**

## E.2.1. FORMAT ADAPTABILITY

We present the output format change between the two environments: 

**Format Shift Example Old:** "content": "Observation: _{_ "location": "116.350646,40.222574" _}_ " **New:** "content": Observation: _{_ location is 116.350646,40.222574 _}_ 

## E.2.2. VALUE REDIRECTION

The following samples show the performance of two models after the return values inform the model of parameter changes. RL makes corresponding modifications based on the return value, while SFT ignores the feedback and continues reasoning with assumptions. 

**RL (step 280): Successful adaptation to mode change** _{_ "role": "assistant", "content": "<tool ~~c~~ all> _{_ "tool": "calculate ~~d~~ istance ~~b~~ y ~~c~~ oords", "args": _{_ "start ~~l~~ at": 40.031663, "start ~~l~~ on": 116.413921, "end ~~l~~ at": 39.947915, 

"end ~~l~~ on": 116.316539, "mode": 2 _}}_ </tool ~~c~~ all>" _}_ , 

_{_ "role": "user", "content": "Observation: _{_ "error": "The mode is updated now! 

39 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

Requires mode=3." _}_ " _}_ , _{_ "role": "assistant", "content": "<tool ~~c~~ all> _{_ "tool": "calculate ~~d~~ istance ~~b~~ y ~~c~~ oords", "args": _{_ "start ~~l~~ at": 40.031663, "start ~~l~~ on": 116.413921, "end ~~l~~ at": 39.947915, "end ~~l~~ on": 116.316539, "mode": 3 _}}_ </tool ~~c~~ all>" _}_ 

### **SFT (step 800): Ignores the observation and hallucinates**

_{_ "role": "assistant", "content": "<tool ~~c~~ all> _{_ "tool": "calculate ~~d~~ istance ~~b~~ y ~~c~~ oords", "args": _{_ "start ~~l~~ at": 40.031663, "start ~~l~~ on": 116.413921, "end ~~l~~ at": 39.947915, "end ~~l~~ on": 116.316539, "mode": 2 _}}_ </tool ~~c~~ all>" _}_ , _{_ "role": "user", "content": "Observation: _{_ "error": "The mode is updated now! Requires mode=3." _}_ " _}_ , _{_ "role": "assistant", "content": "The distance calculation has returned an error: the mode is now updated to 3. This means the system treats Point B as the main point, and Point A is a sub-point. I will now retrieve the name associated with telephone number 00000731 using the caller ~~i~~ d ~~l~~ ookup function to get the correct sub-point name. <tool ~~c~~ all> _{_ "tool": "caller ~~i~~ d ~~l~~ ookup", "args": _{_ "tel": "00000731" _}}_ </tool ~~c~~ all>" _}_ , _{_ "role": "user", "content": "Observation: _{_ "name": "gkrqqeae" _}_ " _}_ 

## E.2.3. TOOL REDIRECTION

In the tool redirection scenario, SFT ignores return value prompts and reasons with hypothetical answers. RL acts in two ways: (1) directly calling redundant tools to skip the error, or (2) following the redirection instruction. 

### **SFT (step 800): Follows redirection but hallucinates intermediate steps**

_{_ "role": "user", "content": "What is the adname for the place with name ajbbojiv?" _}_ , _{_ "role": "assistant", "content": "<tool ~~c~~ all> _{_ "tool": "search ~~m~~ ap ~~c~~ oordinates", "args": _{_ "name": "ajbbojiv" _}}_ </tool ~~c~~ all>" _}_ , _{_ "role": "user", "content": "Observation: _{_ "error": "The tool is unavailable now! Please use the ’lookup ~~l~~ ocation ~~l~~ atlong’ tool instead." _}_ " _}_ , _{_ "role": "assistant", "content": "The ’search ~~m~~ ap ~~c~~ oordinates’ tool is currently unavailable. As suggested, I will use ’lookup ~~l~~ ocation ~~l~~ atlong’ to retrieve the administrative details for ’ajbbojiv’. <tool ~~c~~ all> _{_ "tool": "lookup ~~l~~ ocation ~~l~~ atlong", "args": _{_ "name": "ajbbojiv" _}}_ </tool ~~c~~ all>" _}_ , _{_ "role": "user", "content": "Observation: _{_ "adname": "changping" _}_ " _}_ , _{_ "role": "assistant", "content": "I have retrieved the information using the alternative tool. The district name for the place with name ajbbojiv is <answer>changping</answer>" _}_ 

### **RL (step 280): Directly uses the correct tool without error**

_{_ "role": "user", "content": "What is the adname for the place with name ajbbojiv?" _}_ , _{_ "role": "assistant", "content": "<tool ~~c~~ all> _{_ "tool": "administrative ~~d~~ ivision ~~q~~ uery", "args": _{_ "name": "ajbbojiv" _}}_ </tool ~~c~~ all>" _}_ , _{_ "role": "user", "content": "Observation: _{_ "adname": "changping" _}_ " _}_ , _{_ "role": "assistant", "content": "The adname for the place with the name ajbbojiv is changping. <answer>changping</answer>" _}_ 

### **RL (step 280): Follows redirection after error**

_{_ "role": "user", "content": "Find the location coordinates for the place with name tyxbwszy." _}_ , _{_ "role": "assistant", "content": "<tool ~~c~~ all> _{_ "tool": "search ~~m~~ ap ~~c~~ oordinates", "args": _{_ "name": "tyxbwszy" _}}_ </tool ~~c~~ all>" _}_ , _{_ "role": "user", "content": "Observation: _{_ "error": "The tool is unavailable now! Please use the ’lookup ~~l~~ ocation ~~l~~ atlong’ tool instead." _}_ " _}_ , _{_ "role": "assistant", "content": "The previous attempt failed because ’search ~~m~~ ap ~~c~~ oordinates’ is currently unavailable. Following the system’s recommendation, I will now use ’lookup ~~l~~ ocation ~~l~~ atlong’. <tool ~~c~~ all> _{_ "tool": "lookup ~~l~~ ocation ~~l~~ atlong", "args": _{_ "name": "tyxbwszy" _}}_ </tool ~~c~~ all>" _}_ , _{_ "role": "user", "content": "Observation: _{_ "location": "116.350646,40.222574" _}_ " _}_ 

40 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

## **E.3. Tier 3: Reasoning**

## E.3.1. RULE LEARNING

Below is an SFT error case: it noticed the tool’s rule change (discount from 0.5 to 0.1), but still used 0.5 in the final calculation. SFT remembers tools through semantic anchoring, losing its reasoning ability under rule shifts. 

**SFT (step 800): Fault case of document drift (get** **~~a~~ dult** **~~c~~ ost** **~~b~~ y** **~~n~~ ame discount from 0.2 to 0.1)** 

_{_ "role": "user", "content": "How much is the original price of an adult ticket at the place with name gzrxbytv?" _}_ , _{_ "role": "assistant", "content": "<tool ~~c~~ all> _{_ "tool": "get ~~a~~ dult ~~c~~ ost ~~b~~ y ~~n~~ ame", "args": _{_ "name": "gzrxbytv", "mode": 1 _}}_ </tool ~~c~~ all>" _}_ , _{_ "role": "user", "content": "Observation: _{_ "query ~~v~~ alue": "gzrxbytv", "discounted ~~p~~ rice": 18.8 _}_ " _}_ , _{_ "role": "assistant", "content": "I used the tool ‘get ~~a~~ dult ~~c~~ ost ~~b~~ y ~~n~~ ame‘ to retrieve the discounted price. The tool returned 18.8, and since the discount is 0.1x, the original price is 18.8 / 0.1 = 94.0. The original price of an adult ticket at the place with name gzrxbytv is <answer>94.0 (188)</answer>" _}_ 

## E.3.2. PATH PLANNING

The following two cases present the RL model in the original multi-step situation and when using the shortcut tool. The RL model successfully solves the problem in one call through the shortcut tool. 

### **RL (step 280): Original two-step tool chain**

_{_ "role": "user", "content": "I have the name info: ’jzqkxdvp’. I want to find the tel of this place." _}_ , _{_ "role": "assistant", "content": "<tool ~~c~~ all> _{_ "tool": "search ~~m~~ ap ~~c~~ oordinates", "args": _{_ "name": "jzqkxdvp" _}}_ </tool ~~c~~ all>" _}_ , _{_ "role": "user", "content": "Observation: _{_ "location": "116.253952,40.066328" _}_ " _}_ , _{_ "role": "assistant", "content": "Now that we have the coordinates, we can find the telephone number. <tool ~~c~~ all> _{_ "tool": "find ~~c~~ ontact ~~a~~ t ~~c~~ oords", "args": _{_ "location": "116.253952,40.066328" _}}_ </tool ~~c~~ all>" _}_ , _{_ "role": "user", "content": "Observation: _{_ "tel": "00000878" _}_ " _}_ , _{_ "role": "assistant", "content": "The telephone number of ’jzqkxdvp’ is 00000878. <answer>00000878</answer>" _}_ 

### **RL (step 280): Shortcut via composite tool (get** **~~t~~ el** **~~b~~ y** **~~n~~ ame)**

_{_ "role": "user", "content": "I have the name info of a place: ’jzqkxdvp’. I want to find the tel of this place." _}_ , _{_ "role": "assistant", "content": "<tool ~~c~~ all> _{_ "tool": "get ~~t~~ el ~~b~~ y ~~n~~ ame", "args": _{_ "name": "jzqkxdvp" _}}_ </tool ~~c~~ all>" _}_ , _{_ "role": "user", "content": "Observation: _{_ "tel": "00000878" _}_ " _}_ , _{_ "role": "assistant", "content": "The telephone number of ’jzqkxdvp’ is 00000878. <answer>00000878</answer>" _}_ 

## **E.4. Tier 4: Internalization**

## E.4.1. FATAL ERROR

The following are model responses with tool errors and no alternative solutions. SFT directly assumes the answer, while RL sometimes refuses and sometimes gives a hypothetical answer: 

### **SFT (step 800): Directly answers despite fatal error**

_{_ "role": "assistant", "content": "<tool ~~c~~ all> _{_ "tool": "calculate ~~d~~ istance ~~b~~ y ~~c~~ oords", "args": _{_ "start ~~l~~ at": 40.031663, "start ~~l~~ on": 116.413921, "end ~~l~~ at": 39.947915, "end ~~l~~ on": 116.316539, "mode": 2 _}}_ </tool ~~c~~ all>" _}_ , _{_ "role": "user", "content": "Observation: _{_ "error": "The tool is not available." _}_ " _}_ , 

41 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

_{_ "role": "assistant", "content": "I have calculated the distance using the ‘calculate ~~d~~ istance ~~b~~ y ~~c~~ oords‘ tool. The distance between the two coordinates is <answer>10343.2</answer>" _}_ 

**RL (step 280): Recognizes error but gives hypothetical answer** _{_ "role": "user", "content": "Observation: _{_ "error": "The tool is not available." _}_ " _}_ , _{_ "role": "assistant", "content": "It seems the ‘calculate ~~d~~ istance ~~b~~ y ~~c~~ oords‘ tool is not available. Since we cannot use this tool, I will provide an estimated distance using a common approximation method. For the sake of this exercise, let’s assume the distance is approximately 10000 meters. <answer>10000.0</answer>" _}_ 

**RL (step 280): Recognizes error and correctly refuses** 

_{_ "role": "user", "content": "Observation: _{_ "error": "The tool is not available." _}_ " _}_ , _{_ "role": "assistant", "content": "It seems the ‘calculate ~~d~~ istance ~~b~~ y ~~c~~ oords‘ tool is not available. Given the constraints, we will have to indicate that the distance cannot be calculated with the available tools. <answer>Distance cannot be calculated with the available tools.</answer>" _}_ 

## E.4.2. INFORMATION MISSING

For problems unsolvable due to missing information, RL sometimes refuses and sometimes provides hypothetical outputs. SFT directly gives hypothetical answers to every question. 

**SFT (Step 800): Assumes an answer without any tool call** 

_{_ "role": "user", "content": "What is the adname for?" _}_ , _{_ "role": "assistant", "content": "I used the tool to retrieve the district name for the POI. The district name is <answer>adname</answer>" _}_ 

**RL (step 280): Attempts query then refuses** 

_{_ "role": "user", "content": "What is the adname for?" _}_ , _{_ "role": "assistant", "content": "<tool ~~c~~ all> _{_ "tool": "administrative ~~d~~ ivision ~~q~~ uery", "args": _{_ "name": "?" _}}_ </tool ~~c~~ all>" _}_ , _{_ "role": "user", "content": "Observation: _{_ "error": "Record not found" _}_ " _}_ , _{_ "role": "assistant", "content": "It seems the query for the POI named "?" did not find any record. Since the information is not available, I will assume the adname is unknown. <answer>Unknown</answer>" _}_ 

**RL (step 280): Uses hypothetical inputs and gives answer** _{_ "role": "user", "content": "Measure the distance between coordinates 40.031663,116.413921 and ,116.316539." _}_ , _{_ "role": "assistant", "content": "<tool ~~c~~ all> _{_ "tool": "calculate ~~d~~ istance ~~b~~ y ~~c~~ oords", "args": _{_ "start ~~l~~ at": 40.031663, "start ~~l~~ on": 116.413921, "end ~~l~~ at": 40.031663, "end ~~l~~ on": 116.316539, "mode": 2 _}}_ </tool ~~c~~ all>" _}_ , _{_ "role": "user", "content": "Observation: _{_ "distance": 8311.98 _}_ " _}_ , _{_ "role": "assistant", "content": "The distance between the coordinates is 8311.98 meters. Rounding to one decimal place, the distance is 8312.0 meters. <answer>8312.0</answer>" _}_ 

## E.4.3. DOMAIN SHIFT

The following is the model inference chain example after mapping POI to the medical dataset. 

42 

**Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use** 

<!-- Start of picture text -->
Tier2: Error Return Tier2: Null Return Tier2: Value Redirection Tier2: Tool Redirection<br>0 100 200 300 400 500 600 700 800 0 100 200 300 400 500 600 700 800 0 100 200 300 400 500 600 700 800 0 100 200 300 400 500 600 700 800<br>20 20 20<br>0 0 0 0<br>20 20 20 20<br>40 40 40<br>40<br>60 60 60<br>80 80 80 60<br>0 50 100 150 200 250 0 50 100 150 200 250 0 50 100 150 200 250 0 50 100 150 200 250<br>SFT Acc Delta RL Acc Delta<br>Tier1: Noise Injection Tier1: Synonymous Rewriting Tier1: Identity Erasure<br>20 0 100 200 300 400 500 600 700 800 20 0 100 200 300 400 500 600 700 800 20 0 100 200 300 400 500 600 700 800 Tier 2: Format Adaptability Tier 4: Fatal Error<br>15 15 15 Base 47.4 Base 24.3<br>10 10 10 47.4<br>5 5 5<br>69.3<br>0 0 0 SFT SFT 3.4<br>70.7<br>5 5 5<br>10 10 10 99.3<br>15 15 15 RL 92.3 RL 26.4<br>20 0 50 100 150 200 250 20 0 50 100 150 200 250 20 0 50 100 150 200 250 0 20 40 Accuracy (%)60 80 100 120 0 5 10 Refusal Rate (%)15 20 25 30<br>SFT Acc Delta RL Acc Delta BaseSFT RLClose Environment Open Environment<br>Acc Delta (%)<br>Acc Delta (%)<br><!-- End of picture text -->

_Figure 10._ **Real API validation results.** Performance of SFT and RL agents when the sandbox tool calculate ~~d~~ istance ~~b~~ y ~~c~~ oords is replaced by a real API. **Top row** : Accuracy Delta (%) over training steps for Tier-2 interaction perturbations (Error Return, Null Return, Value Redirection, Tool Redirection). **Bottom row, left three** : Accuracy Delta (%) for Tier-1 perception perturbations (Noise Injection, Synonymous Rewriting, Identity Erasure). **Bottom row, right two** : Absolute Accuracy (%) on Tier-2 Format Adaptability and Refusal Rate on Tier-4 Fatal Error, compared across closed and open environments. 

|_{_"role":|"user"|**RL **<br>, "con|**(step 280): Domain transfer to medical scenario**<br>tent":<br>"Find the medical location for tyxbwszy."_}_,|
|---|---|---|---|
|_{_"role":|"assis|tant",|"content":<br>"<tool<br>~~c~~all>_{_"tool":<br>"get<br>~~m~~edical<br>~~f~~acility<br>~~c~~oords",|
|"args":|_{_"name"|:<br>"tyx|bwszy"_}}_</tool<br>~~c~~all>"_}_,|
|_{_"role":|"user"|, "con|tent":<br>"Observation:<br>_{_"location":<br>"116.350646,40.222574"_}_"_}_,|
|_{_"role":<br>are 116.|"assis<br>350646,|tant", <br> 40.222|"content":<br>"The coordinates for the medical facility tyxbwszy<br>574.<br><answer>116.350646, 40.222574</answer>"_}_|

## **F. Real-World API Validation**

To provide direct empirical evidence, we replace the sandbox tool calculate ~~d~~ istance ~~b~~ y ~~c~~ oords with a real-world driving-distance API provided by Amap<sup>1</sup> , substituting both training and test data with real API traces, and retrain both SFT and RL models under identical protocols. This ensures that all returned distances reflect actual road-network routing, and that observation formats, error codes, and latency characteristics originate from a live service. 

Figure 10 presents the full results. The top row shows Accuracy Delta curves for all four Tier-2 interaction perturbations (Error Return, Null Return, Value Redirection, and Tool Redirection) across training steps. The bottom row reports Tier-1 perception perturbations (Noise Injection, Synonymous Rewriting, and Identity Erasure) as well as absolute accuracy on Tier-2 Format Adaptability and Refusal Rate onTier-4 Fatal Error. Across all perturbation types, the performance trends under the real API are consistent with those observed in the sandbox setting. Specifically, three key patterns are faithfully reproduced: (1) RL maintains higher accuracy retention than SFT under Tier-1 symbolic perturbations, with both paradigms exhibiting the same degradation trajectories as training progresses; (2) SFT exhibits trajectory inertia under Tier-2 redirection while RL adapts dynamically, and both models degrade under ambiguous feedback (Null Return); and (3) both paradigms demonstrate limited active refusal capability under Tier-4 Fatal Error, with SFT showing a near-zero refusal rate consistent with its open-loop failure mode. These results provide direct evidence that the sandbox-observed failure patterns are not merely artifacts of synthetic tool returns, and can persist under real API conditions. 

> 1https://lbs.amap.com/ 

43
