---
title: "Agent World Model (AWM) for Scalable Agentic RL Environments"
url: https://www.snowflake.com/en/blog/engineering/agent-world-model-for-agentic-reinforment-learning/
published: 2026-02
fetched: 2026-11-11
type: engineering-blog
topics: [training, snowflake]
summary: "从100个种子生成1000个SQL状态驱动可执行工具环境，以可查询状态构造奖励；博客清楚解释场景、数据库、工具、检查器和训练。"
---

# Agent World Model (AWM) for Scalable Agentic RL Environments

LLM-powered agents that interact with external tools and environments are one of the most exciting frontiers in AI — from booking flights and managing databases to navigating complex multistep workflows. Yet training such agents at scale has been blocked by a critical bottleneck: **the lack of diverse, executable and reliable agentic environments**.

Collecting real-world environments is expensive and hard to scale. Human-crafted benchmarks often contain only 3-5 environments, far too few for large-scale agentic reinforcement learning (RL). And simulating environments with LLMs introduces hallucinations and high inference latency.

In this post, we present **Agent World Model (AWM)**, a fully synthetic environment generation pipeline that *produces 1,000 executable, SQL-backed tool-use environments* for agentic reinforcement learning. Specifically, this post covers:

- How AWM synthesizes executable environments end to end, from scenarios and tasks to databases, tools and verification.
- How these environments enable fast, large-scale reinforcement learning with massive parallelism (1,024 environment instances per training step).
- Results demonstrating strong out-of-distribution generalization across three benchmarks.
- How to use the open-sourced pipeline, environments and a family of RL-trained Arctic-AWM models to train and evaluate tool-use agents.

All of these components are publicly available via open source, and we provide links to the code, environments, models and paper below.

1. [Published paper](https://arxiv.org/abs/2602.10090)
2. [GitHub repo](https://github.com/Snowflake-Labs/agent-world-model)
3. Hugging Face environment: [AgentWorldModel-1K](https://huggingface.co/datasets/Snowflake/AgentWorldModel-1K)
4. Hugging Face model family: [Arctic-AWM-4B / 8B / 14B](https://huggingface.co/collections/Snowflake/agent-world-model)

## Why environment synthesis matters

Training tool-use agents with reinforcement learning requires the agent to interact with environments thousands of times — making tool calls, observing results, adjusting strategies and eventually completing tasks. This requires environments that are:

1. **Executable:** Agents must actually run tools and receive grounded observations, not hallucinated responses.
2. **Diverse:** Training on a handful of environments leads to overfitting; agents need hundreds or thousands or even more.
3. **Resettable and parallelizable:** Online RL demands fast resets and many concurrent instances.
4. **Equipped with reliable reward signals:** The environment must tell whether the agent succeeded.

AWM addresses all four requirements in a synthesis approach.

## How Agent World Model (AWM) works

The key insight behind AWM is that agent environments share a common structure: a **stateful backend** (database); a **tools interface layer** (MCP interface); and **task-specific success criteria** (verification). By decomposing synthesis into these components, we can generate each part systematically while maintaining consistency.

AWM mirrors how software is built in practice. As shown in Figure 1, starting from a high-level scenario description (e.g., "an online shopping platform"), we progressively synthesize all the components, including scenario synthesis, task synthesis, database synthesis, interface synthesis and verification synthesis, needed for a fully functional environment. Finally, we perform online agentic RL training on these fully synthetic environments.

### Step 1: Scenario generation — from 100 seeds to 1,000 diverse scenarios

We start with just 100 popular domain names (e.g., Snowflake) as seeds and use a Self-Instruct–style expansion to generate 1,000 unique scenario descriptions. Embedding-based deduplication ensures diversity, and category caps prevent the collection from collapsing to a few dominant types like ecommerce.

The result: 1,000 unique scenarios spanning finance, travel, retail, social media, healthcare, IoT, education and more. Figure 2 shows the category distribution of these synthesized scenarios. Figure 3 further shows the wordcloud of the synthesized scenarios.

### Step 2: Task generation — functional requirements for each environment

Following software engineering principles, we generate 10 user tasks per scenario that serve as functional requirements. These tasks dictate what database entities, API endpoints and verification logic the environment needs. Tasks are designed to be API-solvable (no UI clicks) and assume the user is already authenticated to focus on deep functionalities.

This yields **10,000 executable tasks** across all scenarios.

### Step 3: Database synthesis — the state backend

The database is the heart of each environment; it defines the state space. Given the scenario and tasks, the LLM infers the required entities, attributes and relationships, then it generates a SQLite schema and populates it with realistic sample data.

Using SQLite as a relational backend (rather than simplified key-value stores) provides structured state management with explicit keys and constraints. This is critical for reliable state transitions and verification.

Each environment averages **18.5 database tables** and **129 sample data records**. Figure 4 shows an example of the synthesized database schema.

### Step 4: Interface synthesis — the tool layer

Agents can't manipulate the database directly; they need an interface. AWM generates a Python interface layer exposed via **Model Context Protocol (MCP)**, the emerging standard for LLM-tool interaction. This is done in two stages:

1. **API specification:** The LLM designs a toolset schema (endpoint names, parameters, response types) ensuring every task is executable.
2. **Code generation:** A complete Python file (FastAPI + SQLAlchemy + MCP) is generated, averaging \~2,000 lines of code and 35 tools per environment.

The two-stage approach (schema first, then code) significantly reduces hallucination in long-code generation. The unified MCP interface means agents interact with all environments through the same protocol.

### Step 5: Verification synthesis — reward signals for RL

To complete the picture, AWM generates task-specific verification code that compares the database state before and after agent execution. This code extracts structured signals, changed records, expected outcomes and diagnostic information, which are then combined with an LLM-as-a-Judge to produce robust reward signals.

*Why not use pure code verification?* In practice, even well-crafted environments can have imperfections, such as transient failures, edge cases and partial executions. Purely rigid checks can produce false negatives. AWM's **code-augmented LLM-as-a-Judge** combines the precision of code-based verification with the flexibility of LLM reasoning, resulting in more robust rewards for RL training.

### Self-correction: Handling generation errors

Across all synthesis stages, AWM employs execution-based self-correction: If generated code fails to run, the error message is fed back to the LLM for correction (up to five retries). This achieves **over 85% first-attempt success rates** with only **1.13 correction iterations** on average for failed cases, confirming that the pipeline design is sound.

## AWM by the numbers

The complete synthesis pipeline produces environments far more complex than existing toy benchmarks:

| # Metric | Mean | Median | Top 90% | 
|---|---|---|---|
| Database tables | 18.5 | 18.0 | 25.0 | 
| Sample data records | 129.3 | 121.0 | 192.0 | 
| Exposed tools | 35.1 | 35.0 | 45.0 | 
| Environment code lines | 1,984.7 | 1,944.0 | 2,586.0 | 
| Agent steps per task | 8.5 | 6.0 | 20.0 | 
| Unique tools used per task | 7.1 | 6.0 | 12.0 | 

Compared to existing environment sets, AWM achieves the largest scale with minimal human involvement:

| Method | Synthesized? | Human reliance | SQL-backed? | # Envs | # Tools | # Code lines | 
|---|---|---|---|---|---|---|
| τ²-bench | No | Full human design | No | 3 | 22.7 | — | 
| MCP-Universe | No | Real APIs | — | 11 | 12.1 | — | 
| EnvScaler | Yes | Existing task set | No | 191 | 18.6 | 662 | 
| AWM | Yes | Names only | Yes | 1,000 | 35.1 | 1,985 | 

AWM produces **5x more environments** than the closest concurrent work, with nearly **2x more tools per environment** and **3x more code per environment**, while requiring only 100 seed scenario names as input.

## Training agents with agentic reinforcement learning

With 1,000 executable environments in hand, we perform large-scale online RL to train multiturn tool-use agents.

### Training setup

1. **Algorithm:** Group Relative Policy Optimization (GRPO)
2. **Base models:** Qwen3-4B, 8B and 14B (thinking models with reasoning and tool-use capabilities)
3. **Scale:** 1,024 parallel environment instances per training step
4. **Training:** Up to 96 optimization steps with learning rate 7×10⁻⁷

### Reward design: Hybrid step-level + task-level

Purely outcome-based rewards can be insufficient for long-horizon agentic tasks. AWM uses a hybrid reward:

1. Step-level: Format correctness checks at each turn. Invalid tool calls trigger early termination with negative reward (-1.0), saving computation and discouraging malformed actions.
2. Task-level: After normal completion, the code-augmented LLM-as-a-Judge assigns:

- 1.0 for completed
- 0.1 for partially completed
- 0.0 for agent error or environment error

This design rapidly reduces format error rates and improves training efficiency by \~27%.

### History-aware training: Aligning training with inference

A subtle but critical detail: At inference time, real agent frameworks often truncate long interaction histories using a sliding window. But most RL training pipelines optimize with full histories, creating a distribution mismatch.

AWM addresses this by applying the **same sliding-window truncation during training** (window size w=3). Each multiturn trajectory is split into subtrajectories, each conditioned on its own truncated history — ensuring the learned policy is consistent with how the agent actually runs in deployment.

## Results: Strong out-of-distribution generalization

We evaluate on **three benchmarks that differ substantially from our training environments**. None of our synthetic environments were designed to match any specific benchmark. This ensures that performance gains reflect genuine out-of-distribution generalization, rather than benchmark overlap or task-specific tuning.

1. **BFCLv3:** Comprehensive function-calling evaluation (single-turn, multiturn, synthetic tools, real-world tools, hallucination tests)
2. **τ²-bench:** Multiturn conversational agentic tasks (airline, retail, telecom)
3. **MCP-universe:** Real-world MCP servers (location, financial, browser, web, multiserver workflows)

We compare against:

1. **Base:** Original Qwen3 models without additional training
2. **Simulator:** RL training with LLM-simulated environments (GPT-5 as the simulator)
3. **EnvScaler:** Concurrent method with 191 synthesized environments

### Key findings

**AWM is the only method that consistently improves over Base on every benchmark.** This indicates that training on our synthetic environments builds robust, transferable tool-use capabilities, rather than overfitting to specific environment patterns.

**On BFCLv3**, AWM improves performance across all model scales. For the 8B model, the overall score jumps from 53.83 to **65.94** (+12.11), surpassing both Simulator and EnvScaler. The 14B model reaches **70.18**, the best among all methods.

**On τ²-bench**, AWM is competitive with EnvScaler and consistently exceeds Simulator. Notably, EnvScaler regresses on BFCLv3 (-8.93 for 8B) and MCP-Universe (-1.39 average), suggesting its environments may overlap with τ²-bench, whereas AWM improves over Base across all benchmarks.

**On MCP-Universe**, AWM achieves the best overall results, with particularly large gains in Financial and Location categories. The 8B model jumps from 6.70 to **11.17** (+4.47).

The comparison with Simulator also highlights an important finding: **Code-driven, database-backed environments provide a more stable learning signal than LLM-simulated interactions**, while being substantially more efficient (no LLM call per environment step).

Further, Figure 5 demonstrates the effectiveness of scaling the environments for agentic RL training, as the environments become more diverse, the model becomes increasingly generalizable.

## Getting started with AWM

To help you experiment with AWM quickly, we provide a [fully open source implementation](https://github.com/Snowflake-Labs/agent-world-model) and a simple CLI for generating environments and running agents. You can also directly download and use the presynthesized 1,000 environments from [Snowflake/AgentWorldModel-1K](https://huggingface.co/datasets/Snowflake/AgentWorldModel-1K) on Hugging Face.

The synthesis pipeline is exposed through a simple CLI:

```
# Install
uv sync
# step by step:
awm gen scenario --input_path outputs/seed_scenario.jsonl --output_path outputs/gen_scenario.jsonl --target_count 1000
awm gen task --input outputs/gen_scenario.jsonl --output outputs/gen_tasks.jsonl
awm gen db --input outputs/gen_tasks.jsonl --output outputs/gen_db.jsonl
awm gen sample --input_task outputs/gen_tasks.jsonl --input_db outputs/gen_db.jsonl --output outputs/gen_sample.jsonl
awm gen spec --input_task outputs/gen_tasks.jsonl --input_db outputs/gen_db.jsonl --output outputs/gen_spec.jsonl
awm gen env --input_spec outputs/gen_spec.jsonl --input_db outputs/gen_db.jsonl --output outputs/gen_envs.jsonl
awm gen verifier --mode sql --input_task outputs/gen_tasks.jsonl --output outputs/gen_verifier.jsonl
```
**Start and interact with any environment:**

```
# Launch an environment
awm env start --scenario "spotify" --envs_load_path outputs/gen_envs.jsonl --port 8001
# Check it's running
awm env check --url http://localhost:8001/mcp
# Run the agent demo (requires a vLLM-served model)
awm agent \
--task "Create a playlist called 'Chill Vibes' and add the top 5 most-played songs" \
--mcp_url http://localhost:8001/mcp \
--vllm_url http://localhost:8000/v1 \
--model Snowflake/Arctic-AWM-4B
```
## What's next

AWM opens up several exciting directions:

1. **Self-evolving environments:** Trained agents could contribute to synthesizing even harder environments, creating a virtuous cycle of improvement.
2. **Cross-environment tasks:** Synthesizing tasks that span multiple scenarios (e.g., "book a flight on Expedia, then add it to your Google Calendar").
3. **Scaling beyond 1,000:** The pipeline's diversity properties suggest it can scale to 10,000+ environments with sustained benefits; we were limited only by compute budget.
4. **Community contributions:** AWM is model-agnostic. The environments and pipeline work with any LLM, and we welcome the community to extend the scenario set, improve synthesis quality, and train larger agents.

We believe that scalable, executable environment synthesis is a critical missing piece for the next generation of AI agents. AWM provides both the pipeline and the resources to make this accessible to the research community.

## Authors

**Zhaoyang Wang** (UNC-Chapel Hill), **Canwen Xu** (Snowflake AI Research), **Boyi Liu** (Snowflake AI Research), **Yite Wang** (Snowflake AI Research), **Siwei Han** (UNC-Chapel Hill), **Zhewei Yao** (Snowflake AI Research), **Huaxiu Yao** (UNC-Chapel Hill), **Yuxiong He** (Snowflake AI Research)
