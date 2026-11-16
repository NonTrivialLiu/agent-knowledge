---
title: "DeepSeek-V3.2: Pushing the Frontier of Open Large Language Models"
url: https://deepseek.com/en/news/deepseek-v3-2/
published: 2025-12-01
fetched: 2026-11-11
type: engineering-blog
topics: [training]
summary: "Thinking in Tool-Use：推理与工具交互结合；官方称合成 1800 多种环境及 85000 多条复杂指令，早期关键基础。"
---

# DeepSeek-V3.2: Pushing the Frontier of Open Large Language Models

Launching DeepSeek-V3.2 & DeepSeek-V3.2-Speciale — Reasoning-first models built for agents!

- DeepSeek-V3.2: Official successor to V3.2-Exp. Now live on App, Web & API.
- DeepSeek-V3.2-Speciale: Pushing the boundaries of reasoning capabilities. API-only for now.

Tech report: [DeepSeek-V3.2 Tech Report - Hugging Face](https://huggingface.co/deepseek-ai/DeepSeek-V3.2/resolve/main/assets/paper.pdf)

![V3.2 Benchmark](https://deepseek.com/images/blog/deepseek-v3-2/v3.2_251201_benchmark.webp)

---

## World-Leading Reasoning

- V3.2: Balanced inference vs. length. Your daily driver at GPT-5 level performance.
- V3.2-Speciale: Maxed-out reasoning capabilities. Rivals Gemini-3.0-Pro.
- Gold-Medal Performance: V3.2-Speciale attains gold-level results in IMO, CMO, ICPC World Finals & IOI 2025.

Note: V3.2-Speciale dominates complex tasks but requires higher token usage. Currently API-only (no tool-use) to support community evaluation & research.

![V3.2 Benchmark Table](https://deepseek.com/images/blog/deepseek-v3-2/v3.2_251201_benchmark_table_en.png)

---

## Thinking in Tool-Use

- Introduces a new massive agent training data synthesis method covering 1,800+ environments & 85k+ complex instructions.
- DeepSeek-V3.2 is our first model to integrate thinking directly into tool-use, and also supports tool-use in both thinking and non-thinking modes.

![V3.2 Agent Benchmark](https://deepseek.com/images/blog/deepseek-v3-2/v3.2_251201_agent_benchmark.webp)

---

## API Update

- V3.2: Same usage pattern as V3.2-Exp.
- V3.2-Speciale: Served via a temporary endpoint: `base_url="https://api.deepseek.com/v3.2_speciale_expires_on_20251215"`. Same pricing as V3.2, no tool calls, available until Dec 15th, 2025, 15:59 (UTC Time).
- V3.2 now supports Thinking in Tool-Use — details: [Thinking Mode Guide - API Docs](https://api-docs.deepseek.com/guides/thinking_mode)

![Thinking with Tools](https://deepseek.com/images/blog/deepseek-v3-2/v3.2_thinking_with_tools_en.jpeg)

---

## Open Source Release

- [DeepSeek-V3.2 - Hugging Face](https://huggingface.co/deepseek-ai/DeepSeek-V3.2)
- [DeepSeek-V3.2-Speciale - Hugging Face](https://huggingface.co/deepseek-ai/DeepSeek-V3.2-Speciale)
- [DeepSeek-V3.2 Tech Report - Hugging Face](https://huggingface.co/deepseek-ai/DeepSeek-V3.2/resolve/main/assets/paper.pdf)
