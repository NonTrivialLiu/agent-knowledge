---
title: "Training Software Engineering Agents and Verifiers with SWE-Gym"
url: https://arxiv.org/abs/2412.21139
published: 2024-12-30
fetched: 2026-11-11
type: paper
topics: [training, multi-agent]
summary: "以2438条真实Python仓库问题、可执行环境与测试组织训练及验证，开放模型和轨迹；ICML 2025。"
---

# Training Software Engineering Agents and Verifiers with SWE-Gym

Jiayi Pan
Affiliation: UC Berkeley
Correspondence to: [jiayipan@berkeley.edu](mailto:jiayipan@berkeley.edu)
  
Xingyao Wang
Affiliation: UIUC
Correspondence to: [xingyao6@illinois.edu](mailto:xingyao6@illinois.edu)
  
Graham Neubig
Affiliation: CMU
  
Navdeep Jaitly
Affiliation: Apple
  
Heng Ji
Affiliation: UIUC
  
Alane Suhr
Affiliation: UC Berkeley
Correspondence to: [suhr@berkeley.edu](mailto:suhr@berkeley.edu)
  
Yizhe Zhang
Affiliation: Apple
Correspondence to: [yizzhang@apple.com](mailto:yizzhang@apple.com)

## Abstract

We present SWE-Gym, the first environment for training software engineering (SWE) agents.
SWE-Gym contains 2,438 real-world task instances, each comprising a Python codebase with an executable runtime environment, unit tests, and a task specified in natural language.
We use SWE-Gym to train language model based SWE agents, and achieve up to 19% absolute gains in resolution rate on the popular SWE-Bench Verified and Lite test sets.
We also experiment with inference-time scaling through verifiers trained on agent trajectories sampled from SWE-Gym.
When combined with our fine-tuned SWE agents, we achieve 32.0% and 26.0% on SWE-Bench Verified and Lite, respectively, reflecting a new state-of-the-art for open-weight SWE agents. To facilitate further research, we publicly release SWE-Gym,
models, and agent trajectories.

### Keywords:

Machine Learning, ICML

††affiliationnotice:  `*` Equal contribution. `{\dagger}` Equal supervision.

## 1 Introduction

Figure 1: SWE-Gym enables scalable improvements for software engineering agents.
Top: Scaling the amount of training data shows consistent performance improvements as we obtain more training trajectories, with no signs of saturation at 491 trajectories.
We use temperature `t=0` for evaluation.
Bottom: For inference time scaling, we generate a number of candidate trajectories per task and select the best using a verifier trained on SWE-Gym. This approach demonstrates roughly log-linear gains with the number of sampled solutions.
`t=0` (excluded from regression) is used as the first hypothesis to be consistent with the top figure; later rollouts use `t=0.5`.

Language models (LMs) have remarkable promise in automating software engineering (SWE) tasks, as most clearly measured by recent progress on benchmarks like SWE-Bench ([Jimenez et al., 2024](https://arxiv.org/html/2412.21139#bib.bib16)) and Commit0 ([Zhao et al., 2024](https://arxiv.org/html/2412.21139#bib.bib44)).
While LM-based SWE agents have shown significant performance gains through improving agent-computer interfaces ([Yang et al., 2024](https://arxiv.org/html/2412.21139#bib.bib37)) and prompting strategies ([Wang et al., 2024c](https://arxiv.org/html/2412.21139#bib.bib33)), advances in SWE agents have been limited by a reliance on proprietary models, with limited research to improve the underlying LM itself.

Unlike other domains where supervised fine-tuning and reinforcement learning have significantly improved LM capabilities, such as chat ([Ouyang et al., 2022](https://arxiv.org/html/2412.21139#bib.bib21)), math reasoning ([Shao et al., 2024](https://arxiv.org/html/2412.21139#bib.bib26); [Yuan et al., 2024](https://arxiv.org/html/2412.21139#bib.bib39)), and web navigation ([Pan et al., 2024](https://arxiv.org/html/2412.21139#bib.bib22)), software engineering currently lacks suitable training environments, and creating environments is uniquely challenging.
Real-world software engineering requires interaction with an executable runtime that has been prepared with the appropriate software dependencies and reproducible test suites, among other requirements.
These challenges are reflected in the existing resources (Tab. [1](https://arxiv.org/html/2412.21139#S1.T1 "Table 1 ‣ 1 Introduction ‣ Training Software Engineering Agents and Verifiers with SWE-Gym")).
For example, the SWE-Bench ([Jimenez et al., 2024](https://arxiv.org/html/2412.21139#bib.bib16)) training split contains only solutions (git patches that solve the task), missing the step-by-step actions taken by the developer to create each solution, and executable environments and reward signals. R2E ([Jain et al., 2024](https://arxiv.org/html/2412.21139#bib.bib15)) uses synthetic tasks that are very far from real-world problems, while datasets such as APPS ([Hendrycks et al., 2021a](https://arxiv.org/html/2412.21139#bib.bib10)) focus only on isolated tasks rather than realistic repository-level coding problems.

Table 1: SWE-Gym is the first publicly available training environment combining real-world SWE tasks from GitHub issues with pre-installed dependencies and executable test verification. Repository-level: whether each task is situated in a sophisticated repository;
Executable Environment: whether each task instance comes with an executable environment with all relevant dependencies pre-installed;
Real task: whether task instruction is collected from human developers.

|  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
| Dataset (split) | Repository-Level | Executable Environment | Real task | # Instances (total) | # Instances (train) |
| CodeFeedback ([Zheng et al., 2024b](https://arxiv.org/html/2412.21139#bib.bib46)) | ✗ | ✗ | ✓ | 66,383 | 66,383 |
| APPS ([Hendrycks et al., 2021a](https://arxiv.org/html/2412.21139#bib.bib10)) | ✗ | ✓ | ✓ | 10,000 | 5,000 |
| HumanEval ([Chen et al., 2021](https://arxiv.org/html/2412.21139#bib.bib7)) | ✗ | ✓ | ✓ | 164 | 0 |
| MBPP ([Tao et al., 2024](https://arxiv.org/html/2412.21139#bib.bib28)) | ✗ | ✓ | ✓ | 974 | 374 |
| R2E ([Jain et al., 2024](https://arxiv.org/html/2412.21139#bib.bib15)) | ✓ | ✓ | ✗ | 246 | 0 |
| SWE-Bench (train) ([Jimenez et al., 2024](https://arxiv.org/html/2412.21139#bib.bib16)) | ✓ | ✗ | ✓ | 19,008 | 19,008 |
| SWE-Gym Raw | ✓ | ✗ | ✓ | 64,689 | 64,689 |
| SWE-Bench (test) ([Jimenez et al., 2024](https://arxiv.org/html/2412.21139#bib.bib16)) | ✓ | ✓ | ✓ | 2,294 | 0 |
| SWE-Gym | ✓ | ✓ | ✓ | 2,438 | 2,438 |

To bridge this gap, we present SWE-Gym, the first training environment combining real-world software engineering tasks from GitHub issues with pre-installed dependencies and executable test verification.
SWE-Gym contains 2,438 Python tasks sourced from 11 popular open-source repositories (Tab. ), providing useful environments for training LMs as agents and verifiers.

SWE-Gym supports training state-of-the-art open-weight SWE agents.
Based on the OpenHands ([Wang et al., 2024c](https://arxiv.org/html/2412.21139#bib.bib33)) agent scaffold for general-purpose software development (§[2](https://arxiv.org/html/2412.21139#S2.SS0.SSS0.Px1 "Agents that solve GitHub issues. ‣ 2 Related Work ‣ Training Software Engineering Agents and Verifiers with SWE-Gym")), we fine-tune a 32B Qwen-2.5 coder model ([Hui et al., 2024b](https://arxiv.org/html/2412.21139#bib.bib14)) using only 491 agent-environment interaction trajectories sampled using SWE-Gym, and achieve substantial absolute improvements of +12.3% (to 15.3%) and +13.6% (to 20.6%) in resolution rate on SWE-Bench Lite and SWE-Bench Verified respectively (§[4.2](https://arxiv.org/html/2412.21139#S4.SS2 "4.2 Training General-Purpose Prompting Agents ‣ 4 Training LMs as Agents with SWE-Gym ‣ Training Software Engineering Agents and Verifiers with SWE-Gym")).

SWE-Gym is effective across agent scaffolds.
In another agent scaffold based on a specialized workflow (MoatlessTools; [Örwall 2024](https://arxiv.org/html/2412.21139#bib.bib47); §[2](https://arxiv.org/html/2412.21139#S2.SS0.SSS0.Px1 "Agents that solve GitHub issues. ‣ 2 Related Work ‣ Training Software Engineering Agents and Verifiers with SWE-Gym")), we experiment with self-improvement, where the LM interacts with SWE-Gym, receives reward from it, and learns to improve itself through rejection sampling fine-tuning.
This self-improvement boosts performance up to 19.7% on SWE-Bench Lite.

SWE-Gym supports training verifier models to enable inference-time scaling.
We use test suites included in SWE-Gym to determine whether sampled agent trajectories are successful or not.
Given these samples, we train a verifier model ([Cobbe et al., 2021](https://arxiv.org/html/2412.21139#bib.bib8), i.e., an outcome-supervised reward model; )
that estimates a trajectory’s probability of success.
This enables inference-time scaling, where we sample multiple agent trajectories and select the one with the highest estimated reward according to the verifier. This further improves the resolution rate to 32.0% (+11.4% absolute improvement) on SWE-Bench Verified (§[5.1.1](https://arxiv.org/html/2412.21139#S5.SS1.SSS1 "5.1.1 Verifier for General-Purpose Prompting ‣ 5.1 Inference-Time Scaling with Verifiers ‣ 5 Scaling Agent Performance with SWE-Gym ‣ Training Software Engineering Agents and Verifiers with SWE-Gym"); Fig. [1](https://arxiv.org/html/2412.21139#S1.F1 "Figure 1 ‣ 1 Introduction ‣ Training Software Engineering Agents and Verifiers with SWE-Gym") bottom) and 26.0% on SWE-Bench Lite (§[5.1.2](https://arxiv.org/html/2412.21139#S5.SS1.SSS2 "5.1.2 Verifier for Specialized Workflow ‣ 5.1 Inference-Time Scaling with Verifiers ‣ 5 Scaling Agent Performance with SWE-Gym ‣ Training Software Engineering Agents and Verifiers with SWE-Gym")), establishing a new state-of-the-art among systems with publicly accessible weights (Tab. [9](https://arxiv.org/html/2412.21139#A2.T9 "Table 9 ‣ Appendix B Experiment Details ‣ Training Software Engineering Agents and Verifiers with SWE-Gym")).

Our baseline training and inference-time scaling methods on SWE-Gym yield continuously improved results with increasing compute (Fig. [1](https://arxiv.org/html/2412.21139#S1.F1 "Figure 1 ‣ 1 Introduction ‣ Training Software Engineering Agents and Verifiers with SWE-Gym")).
In the training phase, performance scales with the number of sampled trajectories up to our current limit of 491 trajectories, suggesting that performance is currently limited by the compute budget for sampling rather than the number of tasks in SWE-Gym.
Similarly, using the agent and verifier trained by SWE-Gym, the bottom panel shows that using more compute during inference time steadily improves the performance.

## 2 Related Work

### Agents that solve GitHub issues.

We focus on software engineering agents designed to automatically resolve GitHub issues within the SWE-Bench framework ([Jimenez et al., 2024](https://arxiv.org/html/2412.21139#bib.bib16)). These agents take a GitHub issue and its associated code repository as input and generate a valid code modification (i.e., a git diff patch) to address the issue. The correctness of these modifications is verified using a human-written test suite.
Existing agent designs are categorized by the extent of human priors integrated into their workflows:
Specialized workflows ([Xia et al., 2024](https://arxiv.org/html/2412.21139#bib.bib36); [Örwall, 2024](https://arxiv.org/html/2412.21139#bib.bib47); [Zhang et al., 2024b](https://arxiv.org/html/2412.21139#bib.bib43); [Chen et al., 2024](https://arxiv.org/html/2412.21139#bib.bib6)) involve human-defined stages (e.g., localization, code editing, patch re-ranking), where a LM is iteratively prompted for each stage to produce the final result. This approach reduces the task horizon and minimizes the need for long-term planning. However, specialized workflows require significant human engineering, may not generalize to novel issue types, and can fail if intermediate steps encounter problems.
In contrast, general-purpose prompting (([Yang et al., 2024](https://arxiv.org/html/2412.21139#bib.bib37); [Wang et al., 2024c](https://arxiv.org/html/2412.21139#bib.bib33))) rely on LM’s ability to plan over long horizons and generate actions based on a history of interactions without heavily pre-defined workflows. While more flexible, general approaches demand higher capabilities from the underlying LM and can be computationally expensive due to multiple interaction rounds.
The most successful existing SWE agents are built on proprietary language models like GPT-4 or Claude and utilize specialized workflows to overcome these models’ limitations. This contrasts with other sequential decision-making domains ([Silver et al., 2017](https://arxiv.org/html/2412.21139#bib.bib27); [Akkaya et al., 2019](https://arxiv.org/html/2412.21139#bib.bib1)), where learning-based approaches, such as reinforcement learning, drive success by enabling systems to learn from interactions and rewards to develop task competence. A key barrier in the SWE agent domain is the lack of appropriate training environments. Our experiments show that SWE-Gym can be used to build strong learning-based agents, accelerating research in this area.

### Environments for training software agents.

There is no existing dataset suitable for training software engineering agents.
SWE-Bench ([Jimenez et al., 2024](https://arxiv.org/html/2412.21139#bib.bib16)) is widely used for evaluating software engineering performance, but its training split lacks executable environments and success signals present in the evaluation split, making it useful only for imitation learning approaches.
HumanEval ([Chen et al., 2021](https://arxiv.org/html/2412.21139#bib.bib7)) is designed for standalone code generation tasks, akin to coding competitions. Therefore, it falls short of addressing the complex challenges inherent in real-world, repository-level software engineering tasks, which involve thousands of files, millions of lines of code, and tasks such as bug fixing, feature development, and system optimization.
Similarly, R2E ([Jain et al., 2024](https://arxiv.org/html/2412.21139#bib.bib15)) is a small evaluation dataset with 246 instances and, due to its synthetic nature, lacks the realism and complexity in real-world software engineering scenario.
Our proposed SWE-Gym instead uses real-world GitHub issues as task, and associated executable unit tests for evaluation. This results in realistic and complex task formulations, aligning closely with real-world challenges.

### Post-training: From chatbots and reasoners to agents.

Post-training, which fine-tunes pre-trained language models using supervised or reinforcement learning, significantly improves model performance across various domains. Techniques like RLHF ([Ouyang et al., 2022](https://arxiv.org/html/2412.21139#bib.bib21)) have become standard for adapting language models into chatbots, improving both performance and alignment ([Qwen Team, 2024](https://arxiv.org/html/2412.21139#bib.bib24)). In math reasoning, datasets such as MATH ([Hendrycks et al., 2021b](https://arxiv.org/html/2412.21139#bib.bib11)) and GSM-8K ([Cobbe et al., 2021](https://arxiv.org/html/2412.21139#bib.bib8)) facilitate the training and evaluation of policy and verifier models ([Cobbe et al., 2021](https://arxiv.org/html/2412.21139#bib.bib8); [Wang et al., 2024a](https://arxiv.org/html/2412.21139#bib.bib31)).
Earlier works ([Wang et al., 2024b](https://arxiv.org/html/2412.21139#bib.bib32); [Chen et al., 2023](https://arxiv.org/html/2412.21139#bib.bib5); [Zeng et al., 2023](https://arxiv.org/html/2412.21139#bib.bib40); [Wu et al., 2024](https://arxiv.org/html/2412.21139#bib.bib34)) demonstrate that distilling agent trajectories from stronger models improve weaker models. Recent studies ([Xi et al., 2024](https://arxiv.org/html/2412.21139#bib.bib35); [Zhai et al., 2024](https://arxiv.org/html/2412.21139#bib.bib41); [Bai et al., 2024](https://arxiv.org/html/2412.21139#bib.bib3)) explore self-improving methods, showing that reinforcement learning or rejection sampling fine-tuning guided by reward enables LMs to enhance themselves without more capable teachers.

However, post-training typically depends on expert demonstration data or training environments with reliable reward signals, which are largely absent in the software engineering domain. This has led to a reliance on prompting-based methods with proprietary language models. Our work addresses this gap with SWE-Gym, a training environment based on real-world software engineering tasks that uses expert-written tests as reward signals. Our experiments demonstrate that SWE-Gym can build strong SWE agents without prompt engineering.

Category
Metric
SWE-Gym
SWE-Gym Lite

Size
## Instances
2,438 (2,294)
230 (300)

## Repos
11 (12)
11 (12)

Issue Text
Length by Words
239.8 (195.1)
186.2 (175.9)

Codebase
## Non-test Files
971.2 (2944.2)
818.8 (2988.5)

## Non-test Lines
340675.0 (363728.4)
340626.2 (377562.4)

Gold Patch
## Lines edited
69.8 (32.8)
10.6 (10.1)

## Files edited
2.5 (1.7)
1.0 (1.0)

## Func. edited
4.1 (3.0)
1.4 (1.34)

Tests
## Fail to Pass
10.0 (9.0)
2.04 (3.5)

## Total
760.8 (132.5)
99.9 (85.2)

Table 2: Statistics comparing SWE-Gym with the SWE-Bench test split (in parenthesis).
Except for size metrics, we report the average value across instances.

Figure 2: Repository distribution of SWE-Gym instances.

## 3 SWE-Gym Environment

SWE-Gym comprises 2,438 real-world software engineering tasks sourced from pull requests in 11 popular Python repositories, with pre-configured executable environments and expert-validated test cases, constructed in close alignment with SWE-Bench ([Jimenez et al., 2024](https://arxiv.org/html/2412.21139#bib.bib16)).
These repositories are separate from those used in SWE-Bench to avoid contamination.
These tasks require SWE agents to develop test-passing solutions for real-world GitHub issues using provided codebases and executable environments.
Such agents must map from natural language descriptions of the issue, as well as the initial state of the repository, to a pull request represented as a git patch.

We also identify a subset of 230 tasks, SWE-Gym Lite, which contains generally easier and more self-contained tasks that are suitable for rapid prototyping, in alignment with SWE-Bench Lite ([Jimenez et al., 2024](https://arxiv.org/html/2412.21139#bib.bib16)).
To support future research in SWE agent development and automatic dataset synthesis, we also release SWE-Gym Raw, a large set of Python GitHub issues without executable environments (64,689 instances spanning 358 Python repositories).

### 3.1 Dataset Construction

Identify Repositories.
We first use SEART GitHub search11
1
<https://seart-ghs.si.usi.ch/> to filter a list of initial repositories. Unlike SWE-Bench, which focuses on the top 5k most downloaded PyPI libraries ([Jimenez et al., 2024](https://arxiv.org/html/2412.21139#bib.bib16)), we select Python repositories that were created before July 1, 2022 and have more than 500 stars, with at least 300 lines of code, more than 500 pull requests (PRs) and 100 contributors. This results in 358 repositories.

Extracting Training Instances from Repositories.
We use SWE-Bench’s instance extraction script to convert these repositories into task instances, each corresponding to a GitHub issue including the natural language description of the issue, a snapshot of the repository in which the issue was created, and a set of unit tests.
Over the 358 repositories, we extract 64,689 task instances. We refer to this dataset as SWE-Gym Raw, which is over three times larger than the 19k instances gathered in previous work ([Jimenez et al., 2024](https://arxiv.org/html/2412.21139#bib.bib16)) and includes nearly ten times as many repositories.

While SWE-Gym Raw instances contain code, issue descriptions, and the solution, they do not contain executable environments or a guarantee that its unit tests are effective in evaluating the correctness of a solution.
Thus, we focus on 11 repositories with numerous instances and semi-manually create executable environments for them.

Version Training Instances.
Associating instances with their respective version numbers (e.g. 1.2.3) and setting up environments version-by-version makes the environment collection process more practical by avoiding redundant setup work.
We generalize SWE-Bench’s versioning script to support versioning via script execution, and semi-automatically collect versions for each instance based on information available in the repository (e.g., pyproject.toml, git tag, etc).

### Setup Executable Environments and Verify Instances.

Creating executable environments with pre-installed dependencies is crucial for developing software engineering agents, as it mirrors deployment settings and allows for incremental unit test feedback. Configuring dependencies for specific codebase versions is challenging due to the lack of a universal Python package installation method and backward compatibility issues, especially for older GitHub issues. Ignoring these environments could introduce distribution bias, diminishing SWE-Gym’s utility. To address this, we manually configure dependencies for each task instance using relevant configuration files (e.g., requirements.txt), CI scripts, or documentation from the repository snapshot at the time of issue creation.
We then use SWE-Bench’s execution-based validation script to ensure that the gold patch (the human-submitted code diff) passes more unit tests than the original code. This process required approximately 200 human annotation hours22
2
Annotations are done by a subset of the authors. and 10,000 CPU core hours. After validation and filtering out failed instances, we obtained 2,438 unit-test-validated instances from 11 repositories. For full reproducibility, we publicly release pre-built Docker images for each instance, totaling 6 TB.

### 3.2 SWE-Gym Lite

Solving software engineering tasks is computationally intensive, costing usually $1 or more per task with frontier models ([Wang et al., 2024c](https://arxiv.org/html/2412.21139#bib.bib33)).
To improve research efficiency via faster agent evaluation, [Jimenez et al. (2024)](https://arxiv.org/html/2412.21139#bib.bib16) introduce SWE-Bench Lite, a canonical subset of 300 instances from SWE-Bench.
Following the SWE-Bench Lite filtering pipeline,33
3
For details on its construction process, see <https://www.swebench.com/lite.html>. we delineate the SWE-Gym Lite split, comprising 230 instances. Similar to SWE-Bench Lite, this subset excludes tasks that require editing more than one file, tasks with poorly described problem statements, those with excessively complex ground-truth code diffs, and tests focused on error message validation.

### 3.3 Dataset Statistics

Fig. [2](https://arxiv.org/html/2412.21139#S2.F2 "Figure 2 ‣ Post-training: From chatbots and reasoners to agents. ‣ 2 Related Work ‣ Training Software Engineering Agents and Verifiers with SWE-Gym") illustrates that the task distribution across repositories exhibits a long-tail pattern. Notably, tasks associated with pandas comprise nearly one-third of the total, whereas tasks related to bokeh represent a mere one percent.

Our analysis suggests that tasks in SWE-Gym are on average harder than those included in SWE-Bench.
Tab.  shows that SWE-Gym has statistics similar to SWE-Bench, with several key differences.
Codebases in SWE-Gym, on average, have relatively fewer files than SWE-Bench, but a similar number of total lines of code.
However, gold patches in SWE-Gym have significantly more lines and files edited when compared to SWE-Bench’s gold patches.
Additionally, we find models have consistently lower performance on SWE-Gym compared to SWE-Bench.44
4
§[B.4](https://arxiv.org/html/2412.21139#A2.SS4 "B.4 Details of OpenHands Trajectory Sampling ‣ Appendix B Experiment Details ‣ Training Software Engineering Agents and Verifiers with SWE-Gym") contains details of these experiments.
Beyond models and scaffolds overfitting to SWE-Bench, the decreased performance on SWE-Gym may also be due to our inclusion of sophisticated repositories like pandas and MONAI.

## 4 Training LMs as Agents with SWE-Gym

We experiment with training language model agents using SWE-Gym.
We use two agent scaffolds (OpenHands, [Wang et al. 2024c](https://arxiv.org/html/2412.21139#bib.bib33), §[4.2](https://arxiv.org/html/2412.21139#S4.SS2 "4.2 Training General-Purpose Prompting Agents ‣ 4 Training LMs as Agents with SWE-Gym ‣ Training Software Engineering Agents and Verifiers with SWE-Gym"); Moatless Tools, [Örwall 2024](https://arxiv.org/html/2412.21139#bib.bib47), §[4.3](https://arxiv.org/html/2412.21139#S4.SS3 "4.3 Self-Improvement with Specialized Workflow ‣ 4 Training LMs as Agents with SWE-Gym ‣ Training Software Engineering Agents and Verifiers with SWE-Gym")).

### 4.1 Setting

Agent Scaffolds.
Recent LM-based SWE agents comprise a base language model, and a set of tools and prompts this base model has access to.
This set of tools and prompting strategies is referred to as an agent scaffold, and recent work has developed numerous scaffolds for different purposes (refer to §[2](https://arxiv.org/html/2412.21139#S2.SS0.SSS0.Px1 "Agents that solve GitHub issues. ‣ 2 Related Work ‣ Training Software Engineering Agents and Verifiers with SWE-Gym") for examples).
We experiment with two types of agent scaffolds: one for general-purpose prompting (OpenHands CodeAct; [Wang et al. 2024c](https://arxiv.org/html/2412.21139#bib.bib33)) and one for specialized workflows (MoatlessTools; [Örwall 2024](https://arxiv.org/html/2412.21139#bib.bib47)), which
allows us to
measure the efficacy of SWE-Gym across diverse deployment settings.

Policy Improvement Algorithm.
We use SWE-Gym to improve the underlying LM for a given SWE agent.
As a baseline, we employ a simple policy improvement algorithm: rejection sampling fine-tuning (a.k.a. filtered behavior cloning), where we fine-tune the base LM on success trajectories sampled from SWE-Gym.

Evaluation Metrics.
We use the standard SWE agent benchmarks SWE-Bench Lite and Verified ([Jimenez et al., 2024](https://arxiv.org/html/2412.21139#bib.bib16)) for evaluation.
We report (1) resolution rate (%), the proportion of resolved task instances, and (2) Empty Patch (%), the proportion of trajectories where none of the code in the repository is edited.
We use OpenHands remote runtime ([Neubig & Wang, 2024](https://arxiv.org/html/2412.21139#bib.bib20)) to parallelize evaluation (e.g., execute unit tests).

Technical Details.
For base LMs, we use Qwen-2.5-Coder-Instruct  ([Hui et al., 2024a](https://arxiv.org/html/2412.21139#bib.bib13)) 7B, 14B, and 32B. §[B.2](https://arxiv.org/html/2412.21139#A2.SS2 "B.2 OpenHands Agent Experiments ‣ Appendix B Experiment Details ‣ Training Software Engineering Agents and Verifiers with SWE-Gym") contains training run details.

### 4.2 Training General-Purpose Prompting Agents

Table 3: Model performance (fine-tuned on 491 SWE-Gym-sampled trajectories) on SWE-Bench ([Jimenez et al., 2024](https://arxiv.org/html/2412.21139#bib.bib16)) using OpenHands ([Wang et al., 2024c](https://arxiv.org/html/2412.21139#bib.bib33)) as agent scaffold. We use Qwen-2.5-Coder-Instruct as the base model.

|  |  |  |  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Model | Empty Patch (%, `\downarrow`) | | | Stuck in Loop (%, `\downarrow`) | | | Avg. Turn(s) | | | Resolve Rate (%, `\uparrow`) | | |
| Size | zero-shot | fine-tuned | `\Delta` | zero-shot | fine-tuned | `\Delta` | zero-shot | fine-tuned | `\Delta` | zero-shot | fine-tuned | `\Delta` |
| SWE-Bench Lite (300 instances) | | | | | | | | | | | | |
| 7B | 40.3 | 29.7 | -10.7 | 47.0 | 31.0 | -16.0 | 20.3 | 22.2 | +1.9 | 1.0 (`\pm` 1.0) | 10.0 (`\pm` 2.4) | +9.0 |
| 14B | 49.7 | 18.1 | -31.6 | 31.7 | 27.1 | -4.6 | 23.2 | 21.4 | -1.8 | 2.7 (`\pm` 1.9) | 12.7 (`\pm` 2.3) | +10.0 |
| 32B | 27.0 | 18.1 | -8.9 | 16.7 | 18.1 | +1.5 | 15.5 | 29.3 | +13.9 | 3.0 (`\pm` 1.4) | 15.3 (`\pm` 2.5) | +12.3 |
| SWE-Bench Verified (500 instances) | | | | | | | | | | | | |
| 7B | 45.8 | 33.8 | -12.0 | 39.6 | 21.0 | -18.6 | 21.9 | 35.3 | +13.4 | 1.8 (`\pm` 1.1) | 10.6 (`\pm` 2.1) | +8.8 |
| 14B | 44.9 | 14.5 | -30.4 | 32.1 | 21.3 | -10.7 | 25.5 | 30.1 | +4.6 | 4.0 (`\pm` 1.6) | 16.4 (`\pm` 2.0) | +12.4 |
| 32B | 9.5 | 13.8 | +4.3 | 29.4 | 23.8 | -5.6 | 24.6 | 31.6 | +7.0 | 7.0 (`\pm` 1.3) | 20.6 (`\pm` 2.1) | +13.6 |

In this section, we use OpenHands (version CodeActAgent 2.1, [Wang et al. 2024b](https://arxiv.org/html/2412.21139#bib.bib32); [Wang et al. 2024c](https://arxiv.org/html/2412.21139#bib.bib33)) as our agent scaffold, which is based on general-purpose ReAct-style prompting ([Yao et al., 2023](https://arxiv.org/html/2412.21139#bib.bib38)).
In contrast to specialized-workflows-agents (§[2](https://arxiv.org/html/2412.21139#S2.SS0.SSS0.Px1 "Agents that solve GitHub issues. ‣ 2 Related Work ‣ Training Software Engineering Agents and Verifiers with SWE-Gym")), it relies on the LM to generate actions and do planning. It equips the base LM with a bash terminal and a file editor. We disable the browser feature of OpenHands in this work.

Trajectory Collection.
By rejection sampling, we obtain 491 successful trajectories from SWE-Gym,.
These trajectories are sampled from gpt-4o-2024-08-06 and claude-3-5-sonnet-20241022 with different temperature settings.
Each successful trajectory, on average, has roughly 19 turns and approximately 19,000tokens.55
5
Tab. [8](https://arxiv.org/html/2412.21139#A2.T8 "Table 8 ‣ Appendix B Experiment Details ‣ Training Software Engineering Agents and Verifiers with SWE-Gym") contains more statistics of the sampled trajectories.
Although SWE-Gym offers many more tasks and allows repeated sampling, our 491 trajectories are limited primarily by computational budget.

Training on SWE-Gym trajectories turns LM into effective agents to fix issues.
As shown in Tab. [3](https://arxiv.org/html/2412.21139#S4.T3 "Table 3 ‣ 4.2 Training General-Purpose Prompting Agents ‣ 4 Training LMs as Agents with SWE-Gym ‣ Training Software Engineering Agents and Verifiers with SWE-Gym"), the pre-trained base model achieves resolution rates of 3.0% and 7.0% on SWE-Bench Lite and Verified, respectively. After fine-tuning on 491 trajectories66
6
We use a sampling temperature of 0 unless otherwise specified., it improves by up to 12.3% (3.0% → 15.3%) and 13.6% (7.0% → 20.6%).

Training reduces stuck-in-loop behavior.
For agent tasks, open-weight LMs
often get stuck in loops, where the model perpetually generates the same action for multiple turns, especially when prompted with general-purpose prompts (§[2](https://arxiv.org/html/2412.21139#S2.SS0.SSS0.Px1 "Agents that solve GitHub issues. ‣ 2 Related Work ‣ Training Software Engineering Agents and Verifiers with SWE-Gym")). Thus, we report Stuck in Loop (%), the percentage of trajectories where the agent repeats the same action three times consecutively.
As shown in Tab. [3](https://arxiv.org/html/2412.21139#S4.T3 "Table 3 ‣ 4.2 Training General-Purpose Prompting Agents ‣ 4 Training LMs as Agents with SWE-Gym ‣ Training Software Engineering Agents and Verifiers with SWE-Gym"), zero-shot pre-trained models often get stuck in loops; even the largest 32B model is trapped in 29.4% of SWE-Bench Verified tasks. Fine-tuning on trajectories from SWE-Gym consistently reduces the stuck-in-loop rate by 4.6–18.6% across both SWE-Bench Lite and Verified tasks, except for the 32B model on SWE-Bench Lite, which increases by 1.5% due to its already low loop rate. This coincides with a decrease in the empty patch rate, likely enabling the agent to perform more code edits.

Performance scales with model size. Rather unsurprisingly, larger base models consistently improve the resolution rate, empty patch rate, and stuck-in-loop rate (Tab. [3](https://arxiv.org/html/2412.21139#S4.T3 "Table 3 ‣ 4.2 Training General-Purpose Prompting Agents ‣ 4 Training LMs as Agents with SWE-Gym ‣ Training Software Engineering Agents and Verifiers with SWE-Gym")).

Self-improvement remains ineffective.
In addition to fine-tuning on trajectories sampled from strong teacher models, we also experiment with fine-tuning on trajectories sampled directly from the policy being updated.
We use the fine-tuned 32B model to sample 6 trajectories per SWE-Gym instance (using temperature `t=0.5`), obtaining 868 successful trajectories (i.e., on-policy trajectories). We further fine-tune the base 32B model on a mixture of 868 on-policy trajectories and the previously collected 491 off-policy trajectories.
When evaluating this fine-tuned model on SWE-Bench Lite, we observe the resolution rate drop from 15.3 to 8.7%, suggesting that self-improvement is not yet working. We hypothesize that we could achieve improved results using more advanced policy optimization methods, such as proximal policy optimization (PPO) ([Schulman et al., 2017](https://arxiv.org/html/2412.21139#bib.bib25)), or with a stronger base model. These directions remain promising avenues for future investigation.

### 4.3 Self-Improvement with Specialized Workflow

Unlike OpenHands, which offers freedom in long-horizon planning, MoatlessTools constrains the language model’s action space to pre-defined specialized workflows, reducing task horizons.
Specialized workflows outperform general-purpose prompting for open-weight LMs. In Tab. [3](https://arxiv.org/html/2412.21139#S4.T3 "Table 3 ‣ 4.2 Training General-Purpose Prompting Agents ‣ 4 Training LMs as Agents with SWE-Gym ‣ Training Software Engineering Agents and Verifiers with SWE-Gym") and Tab. [4](https://arxiv.org/html/2412.21139#S4.T4 "Table 4 ‣ 4.3 Self-Improvement with Specialized Workflow ‣ 4 Training LMs as Agents with SWE-Gym ‣ Training Software Engineering Agents and Verifiers with SWE-Gym"), the 7B and 32B LM achieve zero-shot resolution rates of 7% and 19% with MoatlessTools, compared to 1.0% and 3.0% with OpenHands on SWE-Bench Lite.

Given MoatlessTools’ improved zero-shot performance and shorter task horizon, we hypothesize that self-improvement without a strong teacher is achievable using this scaffold and training on SWE-Gym.
With a limited compute budget, we conduct this experiment with only 7B and 32B models, using LoRA ([Hu et al., 2022](https://arxiv.org/html/2412.21139#bib.bib12)) for the 32B model for improved efficiency.
We use the 7B model for ablation experiments.

We use iterative rejection sampling fine-tuning for policy improvement. Each iteration involves (a) performing 30 high-temperature (1.0) rollouts per task on SWE-Gym-Lite and adding successful trajectories to the fine-tuning dataset, and (b) fine-tuning the policy on these filtered trajectories. After two iterations, further improvements are negligible.

Data Bias Impacts Performance.
Repeated sampling, as in [Brown et al. (2024)](https://arxiv.org/html/2412.21139#bib.bib4), shows that task success probability follows a long-tail distribution (Fig. [6](https://arxiv.org/html/2412.21139#A1.F6 "Figure 6 ‣ Appendix A Comparison with Concurrent Works ‣ Training Software Engineering Agents and Verifiers with SWE-Gym")), where more samples increase solved instances. While broader task coverage benefits training, it introduces a bias toward easier tasks, making it suboptimal to train on all successful trajectories, as first observed in math reasoning [Tong et al. (2024)](https://arxiv.org/html/2412.21139#bib.bib29).

Mitigating Bias with Per-Instance Capping.
We introduce per-instance capping—a method that limits the maximum number of selected samples per task. As illustrated in Fig. [6](https://arxiv.org/html/2412.21139#A1.F6 "Figure 6 ‣ Appendix A Comparison with Concurrent Works ‣ Training Software Engineering Agents and Verifiers with SWE-Gym"), this balances dataset bias and size. A low cap reduces dataset size and performance (§[5.2](https://arxiv.org/html/2412.21139#S5.SS2 "5.2 Training-Time Scaling with Data ‣ 5 Scaling Agent Performance with SWE-Gym ‣ Training Software Engineering Agents and Verifiers with SWE-Gym")), while a high cap skews the distribution toward easier tasks. Empirically, a threshold of 2 achieves a good balance, slightly outperforming the full dataset and improving training speed (Tab. [6](https://arxiv.org/html/2412.21139#A1.T6 "Table 6 ‣ Appendix A Comparison with Concurrent Works ‣ Training Software Engineering Agents and Verifiers with SWE-Gym")). We rank trajectories by the number of model response rounds required, preferring fewer.

Results.
Results. After two policy improvement iterations (Tab. [4](https://arxiv.org/html/2412.21139#S4.T4 "Table 4 ‣ 4.3 Self-Improvement with Specialized Workflow ‣ 4 Training LMs as Agents with SWE-Gym ‣ Training Software Engineering Agents and Verifiers with SWE-Gym")), the 7B model’s resolution rate increased from 7.0% to 9.0% after the first iteration and to 10.0% after the second. In contrast, the 32B model improved from 19.0% to 19.7% after the first iteration with no further gains.
We attribute the limited gains in the 32B model to the scaffold’s restricted action space and the rejection sampling fine-tuning method.

Table 4: resolution rate (RR) and Empty patch rate (EP) on SWE-Bench Lite with the MoatlessTools Scaffold after online rejection sampling fine-tuning (temperature `t=0`).

| Setting | 7B Model | | 32B Model | |
| --- | --- | --- | --- | --- |
| EP(`\%,\downarrow`) | RR(`\%,\uparrow`) | EP(`\%,\downarrow`) | RR(`\%,\uparrow`) |
| Zero-Shot | 56.3% | 7.0% | 24.3% | 19.0% |
| Iteration 1 | 29.0% | 9.0% | 18.3% | 19.7% |
| Iteration 2 | 23.3% | 10.0% | 9.7% | 19.7% |

## 5 Scaling Agent Performance with SWE-Gym

We explore two scaling directions enabled by SWE-Gym to enhance agent performance: inference-time scaling (§[5.1](https://arxiv.org/html/2412.21139#S5.SS1 "5.1 Inference-Time Scaling with Verifiers ‣ 5 Scaling Agent Performance with SWE-Gym ‣ Training Software Engineering Agents and Verifiers with SWE-Gym")) and training-time data scaling (§[5.2](https://arxiv.org/html/2412.21139#S5.SS2 "5.2 Training-Time Scaling with Data ‣ 5 Scaling Agent Performance with SWE-Gym ‣ Training Software Engineering Agents and Verifiers with SWE-Gym")).

### 5.1 Inference-Time Scaling with Verifiers

Trajectories sampled from SWE-Gym can be used not only for training a policy, but also for training a verifier (i.e., reward) model.
We train an outcome-supervised reward model (ORM) ([Cobbe et al., 2021](https://arxiv.org/html/2412.21139#bib.bib8)) that, given the relevant context of the task execution (including the problem statement, agent trajectory, and current git diff), generates a score that estimates the probability that the agent has solved the problem.
We experiment with using this model to rerank candidate trajectories sampled from a SWE agent policy, and show that such learned verifiers enable effective inference-time scaling for further performance improvement.

### 5.1.1 Verifier for General-Purpose Prompting

For OpenHands agents ([Wang et al., 2024b](https://arxiv.org/html/2412.21139#bib.bib32); [Wang et al., 2024c](https://arxiv.org/html/2412.21139#bib.bib33)) with general-purpose prompting (§[2](https://arxiv.org/html/2412.21139#S2.SS0.SSS0.Px1 "Agents that solve GitHub issues. ‣ 2 Related Work ‣ Training Software Engineering Agents and Verifiers with SWE-Gym")), we train a verifier (ORM) that takes as input the trajectory `\tau=[o_{1},a_{1},o_{2},a_{2},\dots,o_{n},a_{n}]`, represented as an interleaved sequence of observations and actions, and generates a scalar reward `r\in[0,1]`.
Observations `o_{k}` include the task problem statement, command execution output, error messages, etc; action `a_{k}` can be bash command or file operations (e.g., edit, view) from the agent.

Training and Inference. We fine-tune 32B Qwen2.5-Coder-Instruct to label trajectories as successful or unsuccessful using output tokens <YES> and <NO> respectively.77
7
§[B.6](https://arxiv.org/html/2412.21139#A2.SS6 "B.6 OpenHands ORM Prompt ‣ Appendix B Experiment Details ‣ Training Software Engineering Agents and Verifiers with SWE-Gym") includes the verifier prompt template.
For training data, we re-use two sets of trajectories we sampled on SWE-Gym for agent training in §[4.2](https://arxiv.org/html/2412.21139#S4.SS2 "4.2 Training General-Purpose Prompting Agents ‣ 4 Training LMs as Agents with SWE-Gym ‣ Training Software Engineering Agents and Verifiers with SWE-Gym"): (1) off-policy trajectories which contain 443 successful trajectories; (2) on-policy trajectories which contain 875 successful trajectories sampled from the fine-tuned Qwen2.5-Coder-Instruct-32B.88
8
We keep only trajectories within 32k-token length for training, which may reduce their number compared to Section [4.2](https://arxiv.org/html/2412.21139#S4.SS2 "4.2 Training General-Purpose Prompting Agents ‣ 4 Training LMs as Agents with SWE-Gym ‣ Training Software Engineering Agents and Verifiers with SWE-Gym").
We combine both on-policy and off-policy trajectories, randomly sample the same amount of unsuccessful trajectories from each subset (1,318 each), and combine them as our dataset for verifier training (total 2,636 trajectories).
We fine-tune the model to predict <YES> for successful trajectories and <NO> for unsuccessful ones.

At inference time, conditioned on the prompt and the agent trajectory `\tau`, we use SGLang ([Zheng et al., 2024a](https://arxiv.org/html/2412.21139#bib.bib45)) to obtain the log probability of the next token being <YES> (`l_{y}`) or <NO> (`l_{n}`).
We then calculate the reward as the probability of success by normalizing the log probability: `r=\exp(l_{y})/(\exp(l_{y})+\exp(l_{n}))`.

Metrics. We report two metrics: (1) Pass@`k`, the proportion of tasks with at least one successful solution among `k` samples, and (2) Best@`k`, the success rate of the highest-reward trajectories selected by the verifier from `k` samples per task. Pass@`k` measures solution discovery (upper bound for Best@`k`); Best@`k` evaluates verifier accuracy. Mean and variance calculation are detailed in §[B.1](https://arxiv.org/html/2412.21139#A2.SS1 "B.1 Mean and Variance for Pass@N and Best@N. ‣ Appendix B Experiment Details ‣ Training Software Engineering Agents and Verifiers with SWE-Gym"), following [Lightman et al. (2023)](https://arxiv.org/html/2412.21139#bib.bib17).

Figure 3: Increasing inference-time compute improves performance on SWE-Bench Verified with a learnt verifier.
Both the agent and the verifier are a Qwen2.5-Coder-Instruct-32B model fine-tuned on the corresponding dataset (§[5.1.1](https://arxiv.org/html/2412.21139#S5.SS1.SSS1 "5.1.1 Verifier for General-Purpose Prompting ‣ 5.1 Inference-Time Scaling with Verifiers ‣ 5 Scaling Agent Performance with SWE-Gym ‣ Training Software Engineering Agents and Verifiers with SWE-Gym")). OpenHands is used as the agent scaffold.

Results. Fig. [3](https://arxiv.org/html/2412.21139#S5.F3 "Figure 3 ‣ 5.1.1 Verifier for General-Purpose Prompting ‣ 5.1 Inference-Time Scaling with Verifiers ‣ 5 Scaling Agent Performance with SWE-Gym ‣ Training Software Engineering Agents and Verifiers with SWE-Gym") shows how Pass@`k` and Best@K scale with the number of sampled agent trajectories using the fine-tuned 32B model as the agent model. Pass@`k` demonstrates strong improvement, rising from 20.6 to 37.8% resolution rate as `k` increases from 1 to 8, and up to 42.8@`k`=16.
The Best@`k` metric, which relies on our verifier’s ability to select the best trajectory, demonstrates more modest but steady progress, improving from a resolution rate of 20.6@1 to 29.8@8, and up to 32.0@16.
The gap between Pass@`k` and Best@`k`, due to the imperfect performance of our trained verifier, indicates there is room for improvements in reward modeling for coding agents.
Surprisingly, we found that fine-tuning the verifier model using LoRA ([Hu et al., 2022](https://arxiv.org/html/2412.21139#bib.bib12)) (29.8@8) with Unsloth ([Unsloth Team, 2024](https://arxiv.org/html/2412.21139#bib.bib30)) performs better than full-parameter fine-tuning (27.2@8), potentially due regularization. Furthermore, as shown in Fig. [1](https://arxiv.org/html/2412.21139#S1.F1 "Figure 1 ‣ 1 Introduction ‣ Training Software Engineering Agents and Verifiers with SWE-Gym") (bottom), the Best@`k` curve exhibits strong linearity on a logarithmic scale, indicating a promising scaling behavior.

Training data matters for verifier.
We experiment with variations on the choice of training data for our verifier model.
Using full-parameter fine-tuning on Qwen-2.5-Coder-Instruct-32B, we use different mixtures of on- and off-policy trajectories, as well as different distributions of successful and unsuccessful trajectories.
As shown in Fig. [8](https://arxiv.org/html/2412.21139#A1.F8 "Figure 8 ‣ Appendix A Comparison with Concurrent Works ‣ Training Software Engineering Agents and Verifiers with SWE-Gym"), our ablation study demonstrates that the choice of training data can significantly impact verifier performance.
Training with a mixture of off-policy and on-policy data yields the best results (our default setting), reaching a resolution rate of 27@8.
In contrast, using only on-policy data from the fine-tuned model shows moderate but limited improvement, while training exclusively on off-policy data from Claude and GPT leads to early performance plateaus around 22% resolution rate.
Our findings indicate that verifier training benefits most from a diverse dataset combining both off-policy and on-policy examples.

### 5.1.2 Verifier for Specialized Workflow

Figure 4: Scaling inference-time compute for MoatlessTools Agents (32B) with learned verifiers on SWE-Bench Lite. Temperature `t=0.5`.

For MoatlessTools agents with specialized workflows, given that it doesn’t have a turn-taking action-observation trajectory like OpenHands CodeActAgent,
we prepare verifier inputs through a parsing process adopted from [Zhang et al. (2024a)](https://arxiv.org/html/2412.21139#bib.bib42), which combines task descriptions, relevant agent context, and generated patches.99
9
We provide the prompt template in §[B.5](https://arxiv.org/html/2412.21139#A2.SS5 "B.5 MoatlessTools ORM Prompt ‣ Appendix B Experiment Details ‣ Training Software Engineering Agents and Verifiers with SWE-Gym").
We train the verifier to map from this input to a single token indicating task success.

Following the training procedure described in §[5.1.1](https://arxiv.org/html/2412.21139#S5.SS1.SSS1 "5.1.1 Verifier for General-Purpose Prompting ‣ 5.1 Inference-Time Scaling with Verifiers ‣ 5 Scaling Agent Performance with SWE-Gym ‣ Training Software Engineering Agents and Verifiers with SWE-Gym"), we train 7B and 32B verifiers using on-policy trajectories from the last (2nd round of sampling, applying LoRA ([Hu et al., 2022](https://arxiv.org/html/2412.21139#bib.bib12)). To address the easy-data bias in the training dataset, we cap the number of successful trajectories per instance at two and balance the data by subsampling failure cases to match the same number of successful ones.

Results. We evaluate the verifiers by sampling from an agent policy with `k=` 8 at temperature 0.5. As shown in Fig. [4](https://arxiv.org/html/2412.21139#S5.F4 "Figure 4 ‣ 5.1.2 Verifier for Specialized Workflow ‣ 5.1 Inference-Time Scaling with Verifiers ‣ 5 Scaling Agent Performance with SWE-Gym ‣ Training Software Engineering Agents and Verifiers with SWE-Gym") and Fig. [7](https://arxiv.org/html/2412.21139#A1.F7 "Figure 7 ‣ Appendix A Comparison with Concurrent Works ‣ Training Software Engineering Agents and Verifiers with SWE-Gym"), these verifiers enable effective scaling across verifier and policy sizes: the 7B verifier improves from 10 to 13.3% resolution rate on SWE-Bench Lite when paired with a 7B policy, while the 32B verifier improves from 19.7 to 26.3% when paired with a 32B policy. The 7B verifier plateaus after `k=` 4 samples when ranking trajectories from both 7B and 32B agents. In contrast, the 32B verifier continues improving even at `k=` 8, suggesting that verifier size significantly affects scaling behavior.

### 5.2 Training-Time Scaling with Data

We then examine how scaling the amount of training data affects agent performance using 491 sampled trajectories from §[4.2](https://arxiv.org/html/2412.21139#S4.SS2 "4.2 Training General-Purpose Prompting Agents ‣ 4 Training LMs as Agents with SWE-Gym ‣ Training Software Engineering Agents and Verifiers with SWE-Gym"). We simulate three scaling methods through subsampling: (1) Scaling trajectories, where trajectories are randomly dropped (Fig. [5](https://arxiv.org/html/2412.21139#S5.F5 "Figure 5 ‣ 5.2 Training-Time Scaling with Data ‣ 5 Scaling Agent Performance with SWE-Gym ‣ Training Software Engineering Agents and Verifiers with SWE-Gym")); (2) Scaling unique task instances, where only one successful trajectory per task instance is selected (Fig. [9](https://arxiv.org/html/2412.21139#A1.F9 "Figure 9 ‣ Appendix A Comparison with Concurrent Works ‣ Training Software Engineering Agents and Verifiers with SWE-Gym")); and (3) Scaling repositories, which sequentially includes all instances from each repository to assess repository-level diversity.

Setup. Using OpenHands ([Wang et al., 2024c](https://arxiv.org/html/2412.21139#bib.bib33)) and the fine-tuning approach described in §[4.2](https://arxiv.org/html/2412.21139#S4.SS2 "4.2 Training General-Purpose Prompting Agents ‣ 4 Training LMs as Agents with SWE-Gym ‣ Training Software Engineering Agents and Verifiers with SWE-Gym"), we evaluate these scaling approaches on SWE-Bench Verified: scaling the number of trajectories, by subsampling from the full trajectory dataset from §[4.2](https://arxiv.org/html/2412.21139#S4.SS2 "4.2 Training General-Purpose Prompting Agents ‣ 4 Training LMs as Agents with SWE-Gym ‣ Training Software Engineering Agents and Verifiers with SWE-Gym") (at most 491 trajectories); unique instance scaling on these trajectories deduplicated by instance ID (at most 294 trajectories), and repository-based scaling where we sort repositories alphabetically and include all trajectories from each repository in order (e.g., first 25% contains complete trajectories from the first N repositories).
We compare models trained on 25%, 50%, and 100% of the full dataset for each approach, sampling training subsets using the methods described above for each scaling approach.1010
10
Tab. [7](https://arxiv.org/html/2412.21139#A2.T7 "Table 7 ‣ Appendix B Experiment Details ‣ Training Software Engineering Agents and Verifiers with SWE-Gym") contains detailed statistics of these datasets.

Scaling trends suggest instance and repository diversity is not yet a bottleneck.
Fig. [5](https://arxiv.org/html/2412.21139#S5.F5 "Figure 5 ‣ 5.2 Training-Time Scaling with Data ‣ 5 Scaling Agent Performance with SWE-Gym ‣ Training Software Engineering Agents and Verifiers with SWE-Gym") demonstrates substantial scaling behavior, with consistent improvements in resolution rate as the number of training trajectories randomly increases, particularly for the 32B model.
These results suggest that SWE-Gym’s current size and repository diversity are likely not performance bottlenecks - further improvements could likely be achieved by allocating more computing resources to sampling more training trajectories.

Figure 5: 
Scaling effects of increasing the number of randomly sampled trajectories for training.

Fig. [9](https://arxiv.org/html/2412.21139#A1.F9 "Figure 9 ‣ Appendix A Comparison with Concurrent Works ‣ Training Software Engineering Agents and Verifiers with SWE-Gym") reveals comparable overall performance between different scaling approaches up to where deduplication takes effect. While Random Scaling (No Dedup.) achieves higher final performance, this is likely due to having more trajectories (491 vs 294) rather than better scaling efficiency.
Among deduplicated approaches, Repository Scaling shows stronger initial performance at 25% data, suggesting that complete repository coverage may provide more coherent learning signals early in training.
These results suggest that the repository and instance diversity of SWE-Gym is not yet a bottleneck - further improvements could likely be achieved by simply sampling more agent trajectory data for traning, regardless of duplication or repository distribution.

## 6 Conclusions, Limitations, and Future Work

In this paper, we introduce SWE-Gym, the first training environment that addresses critical gaps in enabling scalable learning for software engineering agents. By combining real-world Python tasks with repository-level context, pre-configured execution environments, and test verifications, SWE-Gym will be a foundation for advancing LM agent training research.
Through extensive experiments, we demonstrate that SWE-Gym enables both agent and verifier models to achieve significant improvements in resolving complex software tasks. Our findings highlight the scalability of these approaches, revealing potential for continuous performance gains with increased compute.

We see many research directions that we are excited to explore in the future:

1. 1.

   Automatic Environment Synthesis SWE-Gym, while effective, is limited by its environment diversity, including the number of repositories, types of tasks, and programming languages. We view environment synthesis—via automated environment creation, test-case generation, or task generation—as a critical next step.
2. 2.

   Self-Improvement with Reinforcement Learning Despite notable progress, our self-improvement results are modest. Training language model agents with large-scale online reinforcement learning is a promising direction for further improvements.
3. 3.

   Human-Agent Interaction Current SWE settings focus solely on task completion, neglecting human-in-the-loop collaboration, which is essential for real-world software engineering. Methods like user simulation or learning from offline human-agent interaction data might offer ways for developing collaborative agents that align with human.

## Impact Statement

This work presents SWE-Gym, an environment for training software engineering agents, with strong empirical results on its effectiveness. We discuss a few important societal implications to consider.
First, improving automated software engineering capabilities could increase developer’s productivity and accessibility across industries.
Although current models are primarily research artifacts and not yet production-ready, they can support critical open-source infrastructure and potentially make software development more accessible.
Secondly, as these agents become more capable, they may impact software engineering jobs and require careful consideration around code ownership, licensing, and attribution.
Additionally, while we focus on legitimate software engineering tasks, similar techniques could potentially be misused to automate the creation of malicious code.
We encourage future work to further explore frameworks for responsible deployment of software engineering agents, including considerations around security, safety, and economic impacts.

## Acknowledgments

We thank John Yang and Ofir Press for helpful discussions, and John Yang for assistance in reproducing data analysis results from SWE-Bench. We thank Modal Labs1111
11
<https://modal.com/> for the GPU compute support through its Academic Credits Program.
XW and HJ are partially supported by U.S. DARPA ITM Program No. FA8650-23-C-7316. The views and conclusions contained herein are those of the authors and should not be interpreted as necessarily representing the official policies, either expressed or implied, of DARPA, or the U.S. Government. The U.S. Government is authorized to reproduce and distribute reprints for governmental purposes notwithstanding any copyright annotation therein.

## References

- Akkaya et al. (2019)

  Akkaya, I., Andrychowicz, M., Chociej, M., Litwin, M., McGrew, B., Petron, A., Paino, A., Plappert, M., Powell, G., Ribas, R., et al.
  Solving rubik’s cube with a robot hand.
  *arXiv preprint arXiv:1910.07113*, 2019.
- Badertdinov et al. (2024)

  Badertdinov, I., Trofimova, M., Anapolskiy, Y., Abramov, S., Zainullina, K., Golubev, A., Polezhaev, S., Litvintseva, D., Karasik, S., Fisin, F., Skvortsov, S., Nekrashevich, M., Shevtsov, A., and Yangel, B.
  Scaling data collection for training software engineering agents.
  *Nebius blog*, 2024.
- Bai et al. (2024)

  Bai, H., Zhou, Y., Cemri, M., Pan, J., Suhr, A., Levine, S., and Kumar, A.
  Digirl: Training in-the-wild device-control agents with autonomous reinforcement learning.
  *ArXiv*, abs/2406.11896, 2024.
  URL <https://api.semanticscholar.org/CorpusID:270562229>.
- Brown et al. (2024)

  Brown, B., Juravsky, J., Ehrlich, R., Clark, R., Le, Q. V., R’e, C., and Mirhoseini, A.
  Large language monkeys: Scaling inference compute with repeated sampling.
  *ArXiv*, abs/2407.21787, 2024.
  URL <https://api.semanticscholar.org/CorpusID:271571035>.
- Chen et al. (2023)

  Chen, B., Shu, C., Shareghi, E., Collier, N., Narasimhan, K., and Yao, S.
  Fireact: Toward language agent fine-tuning.
  *ArXiv*, abs/2310.05915, 2023.
  URL <https://api.semanticscholar.org/CorpusID:263829338>.
- Chen et al. (2024)

  Chen, D., Lin, S., Zeng, M., Zan, D., Wang, J.-G., Cheshkov, A., Sun, J., Yu, H., Dong, G., Aliev, A., Wang, J., Cheng, X., Liang, G., Ma, Y., Bian, P., Xie, T., and Wang, Q.
  Coder: Issue resolving with multi-agent and task graphs.
  *CoRR in ArXiv*, abs/2406.01304, 2024.
- Chen et al. (2021)

  Chen, M., Tworek, J., Jun, H., Yuan, Q., Pondé, H., Kaplan, J., Edwards, H., Burda, Y., Joseph, N., Brockman, G., Ray, A., Puri, R., Krueger, G., Petrov, M., Khlaaf, H., Sastry, G., Mishkin, P., Chan, B., Gray, S., Ryder, N., Pavlov, M., Power, A., Kaiser, L., Bavarian, M., Winter, C., Tillet, P., Such, F. P., Cummings, D. W., Plappert, M., Chantzis, F., Barnes, E., Herbert-Voss, A., Guss, W. H., Nichol, A., Babuschkin, I., Balaji, S., Jain, S., Carr, A., Leike, J., Achiam, J., Misra, V., Morikawa, E., Radford, A., Knight, M. M., Brundage, M., Murati, M., Mayer, K., Welinder, P., McGrew, B., Amodei, D., McCandlish, S., Sutskever, I., and Zaremba, W.
  Evaluating large language models trained on code.
  *ArXiv*, abs/2107.03374, 2021.
  URL <https://api.semanticscholar.org/CorpusID:235755472>.
- Cobbe et al. (2021)

  Cobbe, K., Kosaraju, V., Bavarian, M., Chen, M., Jun, H., Kaiser, L., Plappert, M., Tworek, J., Hilton, J., Nakano, R., Hesse, C., and Schulman, J.
  Training verifiers to solve math word problems.
  *ArXiv*, abs/2110.14168, 2021.
  URL <https://api.semanticscholar.org/CorpusID:239998651>.
- Golubev et al. (2024)

  Golubev, A., Polezhaev, S., Zainullina, K., Trofimova, M., Badertdinov, I., Anapolskiy, Y., Litvintseva, D., Karasik, S., Fisin, F., Skvortsov, S., Nekrashevich, M., Shevtsov, A., Abramov, S., and Yangel, B.
  Leveraging training and search for better software engineering agents.
  *Nebius blog*, 2024.
  https://nebius.com/blog/posts/training-and-search-for-software-engineering-agents.
- Hendrycks et al. (2021a)

  Hendrycks, D., Basart, S., Kadavath, S., Mazeika, M., Arora, A., Guo, E., Burns, C., Puranik, S., He, H., Song, D., and Steinhardt, J.
  Measuring coding challenge competence with APPS.
  In Vanschoren, J. and Yeung, S. (eds.), *Proceedings of the Neural Information Processing Systems Track on Datasets and Benchmarks 1, NeurIPS Datasets and Benchmarks 2021, December 2021, virtual*, 2021a.
- Hendrycks et al. (2021b)

  Hendrycks, D., Burns, C., Kadavath, S., Arora, A., Basart, S., Tang, E., Song, D. X., and Steinhardt, J.
  Measuring mathematical problem solving with the math dataset.
  *ArXiv*, abs/2103.03874, 2021b.
  URL <https://api.semanticscholar.org/CorpusID:232134851>.
- Hu et al. (2022)

  Hu, E. J., Shen, Y., Wallis, P., Allen-Zhu, Z., Li, Y., Wang, S., Wang, L., and Chen, W.
  Lora: Low-rank adaptation of large language models.
  In *The Tenth International Conference on Learning Representations, ICLR 2022, Virtual Event, April 25-29, 2022*. OpenReview.net, 2022.
  URL <https://openreview.net/forum?id=nZeVKeeFYf9>.
- Hui et al. (2024a)

  Hui, B., Yang, J., Cui, Z., Yang, J., Liu, D., Zhang, L., Liu, T., Zhang, J., Yu, B., Dang, K., et al.
  Qwen2. 5-coder technical report.
  *arXiv preprint arXiv:2409.12186*, 2024a.
- Hui et al. (2024b)

  Hui, B., Yang, J., Cui, Z., Yang, J., Liu, D., Zhang, L., Liu, T., Zhang, J., Yu, B., Dang, K., et al.
  Qwen2. 5-coder technical report.
  *arXiv preprint arXiv:2409.12186*, 2024b.
- Jain et al. (2024)

  Jain, N., Shetty, M., Zhang, T., Han, K., Sen, K., and Stoica, I.
  R2E: turning any github repository into a programming agent environment.
  In *Forty-first International Conference on Machine Learning, ICML 2024, Vienna, Austria, July 21-27, 2024*. OpenReview.net, 2024.
  URL <https://openreview.net/forum?id=kXHgEYFyf3>.
- Jimenez et al. (2024)

  Jimenez, C. E., Yang, J., Wettig, A., Yao, S., Pei, K., Press, O., and Narasimhan, K. R.
  Swe-bench: Can language models resolve real-world github issues?
  In *The Twelfth International Conference on Learning Representations, ICLR 2024, Vienna, Austria, May 7-11, 2024*. OpenReview.net, 2024.
  URL <https://openreview.net/forum?id=VTF8yNQM66>.
- Lightman et al. (2023)

  Lightman, H., Kosaraju, V., Burda, Y., Edwards, H., Baker, B., Lee, T., Leike, J., Schulman, J., Sutskever, I., and Cobbe, K.
  Let’s verify step by step.
  *ArXiv*, abs/2305.20050, 2023.
  URL <https://api.semanticscholar.org/CorpusID:258987659>.
- Ma et al. (2024)

  Ma, Y., Cao, R., Cao, Y., Zhang, Y., Chen, J., Liu, Y., Liu, Y., Li, B., Huang, F., and Li, Y.
  Lingma swe-gpt: An open development-process-centric language model for automated software improvement.
  *arXiv preprint arXiv:2411.00622*, 2024.
- Modal (2024)

  Modal.
  Modal: High-performance AI infrastructure.
  <https://modal.com/>, 2024.
  Accessed: 2024-12-18.
- Neubig & Wang (2024)

  Neubig, G. and Wang, X.
  Evaluation of LLMs as Coding Agents on SWE-Bench (at 30x Speed!).
  *All Hands AI blog*, 2024.
- Ouyang et al. (2022)

  Ouyang, L., Wu, J., Jiang, X., Almeida, D., Wainwright, C., Mishkin, P., Zhang, C., Agarwal, S., Slama, K., Ray, A., et al.
  Training language models to follow instructions with human feedback.
  *Advances in neural information processing systems*, 35:27730–27744, 2022.
- Pan et al. (2024)

  Pan, J., Zhang, Y., Tomlin, N., Zhou, Y., Levine, S., and Suhr, A.
  Autonomous evaluation and refinement of digital agents.
  *ArXiv*, abs/2404.06474, 2024.
  URL <https://api.semanticscholar.org/CorpusID:269009430>.
- PyTorch Team (2024)

  PyTorch Team.
  torchtune: PyTorch native post-training library.
  <https://github.com/pytorch/torchtune>, 2024.
- Qwen Team (2024)

  Qwen Team.
  Qwen2.5: A party of foundation models, September 2024.
  URL <https://qwenlm.github.io/blog/qwen2.5/>.
- Schulman et al. (2017)

  Schulman, J., Wolski, F., Dhariwal, P., Radford, A., and Klimov, O.
  Proximal policy optimization algorithms.
  *ArXiv*, abs/1707.06347, 2017.
  URL <https://api.semanticscholar.org/CorpusID:28695052>.
- Shao et al. (2024)

  Shao, Z., Wang, P., Zhu, Q., Xu, R., Song, J., Bi, X., Zhang, H., Zhang, M., Li, Y., Wu, Y., et al.
  Deepseekmath: Pushing the limits of mathematical reasoning in open language models.
  *arXiv preprint arXiv:2402.03300*, 2024.
- Silver et al. (2017)

  Silver, D., Hubert, T., Schrittwieser, J., Antonoglou, I., Lai, M., Guez, A., Lanctot, M., Sifre, L., Kumaran, D., Graepel, T., Lillicrap, T. P., Simonyan, K., and Hassabis, D.
  Mastering chess and shogi by self-play with a general reinforcement learning algorithm.
  *ArXiv*, abs/1712.01815, 2017.
  URL <https://api.semanticscholar.org/CorpusID:33081038>.
- Tao et al. (2024)

  Tao, N., Ventresque, A., Nallur, V., and Saber, T.
  Enhancing program synthesis with large language models using many-objective grammar-guided genetic programming.
  *Algorithms*, 17(7):287, 2024.
  doi: 10.3390/A17070287.
  URL <https://doi.org/10.3390/a17070287>.
- Tong et al. (2024)

  Tong, Y., Zhang, X., Wang, R., Wu, R. M., and He, J.
  Dart-math: Difficulty-aware rejection tuning for mathematical problem-solving.
  *ArXiv*, abs/2407.13690, 2024.
  URL <https://api.semanticscholar.org/CorpusID:271270574>.
- Unsloth Team (2024)

  Unsloth Team.
  Easily finetune and train LLMs. Get faster with unsloth.
  <https://unsloth.ai/>, 2024.
- Wang et al. (2024a)

  Wang, P., Li, L., Shao, Z., Xu, R., Dai, D., Li, Y., Chen, D., Wu, Y., and Sui, Z.
  Math-shepherd: Verify and reinforce LLMs step-by-step without human annotations.
  In Ku, L.-W., Martins, A., and Srikumar, V. (eds.), *Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*, pp. 9426–9439, Bangkok, Thailand, August 2024a. Association for Computational Linguistics.
  doi: 10.18653/v1/2024.acl-long.510.
  URL <https://aclanthology.org/2024.acl-long.510>.
- Wang et al. (2024b)

  Wang, X., Chen, Y., Yuan, L., Zhang, Y., Li, Y., Peng, H., and Ji, H.
  Executable code actions elicit better LLM agents.
  In *Forty-first International Conference on Machine Learning, ICML 2024, Vienna, Austria, July 21-27, 2024*. OpenReview.net, 2024b.
  URL <https://openreview.net/forum?id=jJ9BoXAfFa>.
- Wang et al. (2024c)

  Wang, X., Li, B., Song, Y., Xu, F. F., Tang, X., Zhuge, M., Pan, J., Song, Y., Li, B., Singh, J., Tran, H. H., Li, F., Ma, R., Zheng, M., Qian, B., Shao, Y., Muennighoff, N., Zhang, Y., Hui, B., Lin, J., Brennan, R., Peng, H., Ji, H., and Neubig, G.
  OpenHands: An Open Platform for AI Software Developers as Generalist Agents.
  *CoRR in ArXiv*, abs/2407.16741, 2024c.
- Wu et al. (2024)

  Wu, Z., Bai, H., Zhang, A., Gu, J., Vinod Vydiswaran, V., Jaitly, N., and Zhang, Y.
  Divide-or-conquer? which part should you distill your llm?
  *ArXiv*, 2024.
- Xi et al. (2024)

  Xi, Z., Ding, Y., Chen, W., Hong, B., Guo, H., Wang, J., Yang, D., Liao, C., Guo, X., He, W., Gao, S., Chen, L., Zheng, R., Zou, Y., Gui, T., Zhang, Q., Qiu, X., Huang, X., Wu, Z., and Jiang, Y.-G.
  Agentgym: Evolving large language model-based agents across diverse environments.
  *ArXiv*, abs/2406.04151, 2024.
  URL <https://api.semanticscholar.org/CorpusID:270285866>.
- Xia et al. (2024)

  Xia, C. S., Deng, Y., Dunn, S., and Zhang, L.
  Agentless: Demystifying llm-based software engineering agents.
  *CoRR*, abs/2407.01489, 2024.
  doi: 10.48550/ARXIV.2407.01489.
  URL <https://doi.org/10.48550/arXiv.2407.01489>.
- Yang et al. (2024)

  Yang, J., Jimenez, C. E., Wettig, A., Lieret, K., Yao, S., Narasimhan, K., and Press, O.
  Swe-agent: Agent-computer interfaces enable automated software engineering.
  *CoRR*, abs/2405.15793, 2024.
  doi: 10.48550/ARXIV.2405.15793.
  URL <https://doi.org/10.48550/arXiv.2405.15793>.
- Yao et al. (2023)

  Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K. R., and Cao, Y.
  React: Synergizing reasoning and acting in language models.
  In *The Eleventh International Conference on Learning Representations, ICLR 2023, Kigali, Rwanda, May 1-5, 2023*. OpenReview.net, 2023.
  URL <https://openreview.net/forum?id=WE_vluYUL-X>.
- Yuan et al. (2024)

  Yuan, L., Cui, G., Wang, H., Ding, N., Wang, X., Deng, J., Shan, B., Chen, H., Xie, R., Lin, Y., Liu, Z., Zhou, B., Peng, H., Liu, Z., and Sun, M.
  Advancing LLM reasoning generalists with preference trees.
  *CoRR*, abs/2404.02078, 2024.
  doi: 10.48550/ARXIV.2404.02078.
  URL <https://doi.org/10.48550/arXiv.2404.02078>.
- Zeng et al. (2023)

  Zeng, A., Liu, M., Lu, R., Wang, B., Liu, X., Dong, Y., and Tang, J.
  Agenttuning: Enabling generalized agent abilities for llms.
  In *Annual Meeting of the Association for Computational Linguistics*, 2023.
  URL <https://api.semanticscholar.org/CorpusID:264306101>.
- Zhai et al. (2024)

  Zhai, Y., Bai, H., Lin, Z., Pan, J., Tong, S., Zhou, Y., Suhr, A., Xie, S., LeCun, Y., Ma, Y., and Levine, S.
  Fine-tuning large vision-language models as decision-making agents via reinforcement learning.
  *ArXiv*, abs/2405.10292, 2024.
  URL <https://api.semanticscholar.org/CorpusID:269790773>.
- Zhang et al. (2024a)

  Zhang, K., Yao, W., Liu, Z., Feng, Y., Liu, Z., Murthy, R., Lan, T., Li, L., Lou, R., Xu, J., Pang, B., Zhou, Y., Heinecke, S., Savarese, S., Wang, H., and Xiong, C.
  Diversity empowers intelligence: Integrating expertise of software engineering agents.
  *ArXiv*, abs/2408.07060, 2024a.
  URL <https://api.semanticscholar.org/CorpusID:271860093>.
- Zhang et al. (2024b)

  Zhang, Y., Ruan, H., Fan, Z., and Roychoudhury, A.
  Autocoderover: Autonomous program improvement.
  In *ISSTA*, 2024b.
- Zhao et al. (2024)

  Zhao, W., Jiang, N., Lee, C., Chiu, J. T., Cardie, C., Gallé, M., and Rush, A. M.
  Commit0: Library generation from scratch, 2024.
  URL <https://arxiv.org/abs/2412.01769>.
- Zheng et al. (2024a)

  Zheng, L., Yin, L., Xie, Z., Sun, C., Huang, J., Yu, C. H., Cao, S., Kozyrakis, C., Stoica, I., Gonzalez, J. E., Barrett, C., and Sheng, Y.
  Sglang: Efficient execution of structured language model programs, 2024a.
  URL <https://arxiv.org/abs/2312.07104>.
- Zheng et al. (2024b)

  Zheng, T., Zhang, G., Shen, T., Liu, X., Lin, B. Y., Fu, J., Chen, W., and Yue, X.
  Opencodeinterpreter: Integrating code generation with execution and refinement.
  *ArXiv*, abs/2402.14658, 2024b.
  URL <https://api.semanticscholar.org/CorpusID:267782452>.
- Örwall (2024)

  Örwall, A.
  Moatless Tool.
  <https://github.com/aorwall/moatless-tools>, 2024.
  Accessed: 2024-10-22.

## Appendix A Comparison with Concurrent Works

[Ma et al. (2024)](https://arxiv.org/html/2412.21139#bib.bib18) trains an LM agent, Lingma SWE-GPT, using a method similar to our rejection sampling fine-tuning baseline, with a dataset comparable to our SWE-Gym Raw splits. Without executable unit test feedback, they rely on manually defined heuristics to filter out low-quality trajectories, such as comparing similarity between submitted patches and edit locations with gold patches.
The model weights are publicly accessible but not the training pipeline or the dataset.

Most relevant to our work are two consecutive blog posts by
[Golubev et al. (2024)](https://arxiv.org/html/2412.21139#bib.bib9) and [Badertdinov et al. (2024)](https://arxiv.org/html/2412.21139#bib.bib2), who also construct an executable training environment with real-world tasks from GitHub.
Instead of manual configuration, they employ a general environment setup script and simply discard instances that fail the setup process.
This approach leads to key differences in dataset size and distribution: while it biases the environment away from tasks with complex dependencies, they successfully collect 6,415 instances, about 1.5 times larger than our dataset.
In [Golubev et al. (2024)](https://arxiv.org/html/2412.21139#bib.bib9), they also study training agents and verifiers with the environment.
Additionally, they explore a lookahead setting where a trained verifier ranks and selects the best next action.
With a substantially large collection of agent trajectories (80,036 compared to thousands in our experiments) and model size (72B compared to 32B),
Their best system achieves 40% accuracy on SWE-Bench Verified.
While their dataset and agent trajectories are publicly accessible, the model is not.

In comparison, with a comparable dataset size, our SWE-Gym has executable feedback, avoids potential dataset bias through manual configuration of environments, while providing comprehensive analysis of agent and verifier training, their scaling behaviors, and positive results on agent self-improvement. Our system achieves competitive results with significantly lower compute and a smaller model size (32B vs 72B). Lastly, we open source all artifacts of the project, including dataset, model weights, agent trajectory data and the training pipeline.

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| Model | SWE-Bench | | Openness | |
| Name, Model Size | Lite | Verified | Model | Environment |
| [Ma et al. (2024)](https://arxiv.org/html/2412.21139#bib.bib18), 72B | 22.0 | 30.2 | ✓ | ✗ |
| [Golubev et al. (2024)](https://arxiv.org/html/2412.21139#bib.bib9) Agent and Verifier, 72B | - | 40.6 | ✗ | ✓ |
| Our SWE-Gym Agent and Verifier, 32B | 26.0 | 32.0 | ✓ | ✓ |

Table 5: Comparison of model performance on SWE-Bench benchmark and if the model weights and environments are publically accessible (openness).

| Cap | # Traj | Empty Patch (`\%,\downarrow`) | resolution rate (`\%,\uparrow`) |
| --- | --- | --- | --- |
| 0 (Zero-shot) | 0 | 56.3 | 7.0 |
| 1 | 36 | 37.3 | 9.0 |
| 2 | 62 | 29.0 | 9.7 |
| 3 | 82 | 43.7 | 7.7 |
| No Cap (All) | 172 | 30.7 | 9.3 |

Table 6: resolution rate and empty patch rate on SWE-Bench Lite with a 7B model trained using different instance capping strategies (Cap).

Figure 6: 
Success distribution over 30 rounds on SWE-Gym Lite with 7B model in zero-shot. The distribution is naturally biased toward easy tasks. Per instance capping reduces this bias but lowers the total trajectory count for training. We set temperature `t=1` during sampling.

Figure 7: Scaling inference-time compute for MoatlessTools Agents (7B and 32B) with their corresponding learned verifiers. Temperature `t=0.5`.

Figure 8: Ablation study for verifier training (§[5.1.1](https://arxiv.org/html/2412.21139#S5.SS1.SSS1 "5.1.1 Verifier for General-Purpose Prompting ‣ 5.1 Inference-Time Scaling with Verifiers ‣ 5 Scaling Agent Performance with SWE-Gym ‣ Training Software Engineering Agents and Verifiers with SWE-Gym")). Performances are evaluated on SWE-Bench Verified.
Both the agent and the verifier are Qwen2.5-Coder-Instruct-32B model fine-tuned on the corresponding dataset.
OpenHands ([Wang et al., 2024c](https://arxiv.org/html/2412.21139#bib.bib33)) is used as the agent scaffold.

Figure 9: Comparison of three data sampling approaches using 32B LM:
scaling trajectories (dedup.), scaling unique task instances, and scaling repositories (§[5.2](https://arxiv.org/html/2412.21139#S5.SS2 "5.2 Training-Time Scaling with Data ‣ 5 Scaling Agent Performance with SWE-Gym ‣ Training Software Engineering Agents and Verifiers with SWE-Gym")).

## Appendix B Experiment Details

|  | Original | Dedup. | Sorted by Random (Dedup.) | | Sorted by Repo (Dedup.) | |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  | First 25% | First 50% | First 25% | First 50% |
| getmoto/moto | 155 | 72 | 12 | 33 | 0 | 46 |
| Project-MONAI/MONAI | 95 | 53 | 17 | 25 | 53 | 53 |
| pandas-dev/pandas | 70 | 61 | 14 | 30 | 0 | 0 |
| python/mypy | 46 | 27 | 7 | 12 | 0 | 0 |
| dask/dask | 45 | 29 | 8 | 17 | 6 | 29 |
| iterative/dvc | 36 | 24 | 8 | 12 | 0 | 0 |
| conan-io/conan | 20 | 12 | 1 | 7 | 12 | 12 |
| pydantic/pydantic | 11 | 7 | 2 | 4 | 0 | 0 |
| facebookresearch/hydra | 7 | 5 | 2 | 5 | 0 | 5 |
| bokeh/bokeh | 3 | 2 | 1 | 1 | 2 | 2 |
| modin-project/modin | 3 | 2 | 1 | 1 | 0 | 0 |
| Total | 491 | 294 | 73 | 147 | 73 | 147 |

Table 7: Distribution of success trajectories used in training-time scaling experiments (§[5.2](https://arxiv.org/html/2412.21139#S5.SS2 "5.2 Training-Time Scaling with Data ‣ 5 Scaling Agent Performance with SWE-Gym ‣ Training Software Engineering Agents and Verifiers with SWE-Gym")). Dedup. denotes that the trajectories are deduplicated by randomly select ONE success trajectory per instance ID; Sorted by random (repo) X% (Dedup.) denotes a subset of trajectories taken from the first X% from dedup. instances that are sorted randomly (by repository name).

|  |  |  |  |  |  | Percentiles | | | | | | |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | Resolved | Count | Mean | Std | Min | Max | 5% | 10% | 25% | 50% | 75% | 90% | 95% |
| Num. of Messages | ✗ | `5,557.0` | `39.2` | `31.9` | `7.0` | `101.0` | `9.0` | `9.0` | `9.0` | `29.0` | `61.0` | `100.0` | `101.0` |
| ✓ | `491.0` | `39.9` | `19.9` | `13.0` | `101.0` | `19.0` | `21.0` | `25.0` | `33.0` | `47.5` | `65.0` | `87.0` |
| Num. of Tokens | ✗ | `5,557.0` | `17,218.3` | `17,761.6` | `1,615.0` | `167,834.0` | `1,833.0` | `1,907.0` | `2,268.0` | `12,305.0` | `26,434.0` | `41,182.2` | `51,780.6` |
| ✓ | `491.0` | `18,578.5` | `11,361.4` | `2,560.0` | `81,245.0` | `5,813.0` | `8,357.0` | `11,559.5` | `15,999.0` | `22,040.5` | `31,632.0` | `39,512.5` |

Table 8: Statistics of SWE-Gym-sampled trajectories. We use the tokenizer from Qwen-2.5-Coder-Instruct-7B to estimate the number of tokens.

| Agent | Model | Model Size | Training Data | Resolved `(\%)` |
| --- | --- | --- | --- | --- |
| SWE-Bench Verified (500 instances) | | | | |
| RAG | SWE-Llama ([Jimenez et al., 2024](https://arxiv.org/html/2412.21139#bib.bib16)) | 7B | 10K instances | 1.4 |
| RAG | SWE-Llama ([Jimenez et al., 2024](https://arxiv.org/html/2412.21139#bib.bib16)) | 13B | 10K instances | 1.2 |
| Lingma Agent ([Ma et al., 2024](https://arxiv.org/html/2412.21139#bib.bib18)) | Lingma SWE-GPT (v0925) | 7B | 90K PRs from 4K repos | 18.2 |
| Lingma Agent ([Ma et al., 2024](https://arxiv.org/html/2412.21139#bib.bib18)) | Lingma SWE-GPT (v0925) | 72B | 90K PRs from 4K repos | 28.8 |
| OpenHands ([Wang et al., 2024c](https://arxiv.org/html/2412.21139#bib.bib33)) (Ours) | fine-tuned Qwen2.5-Coder-Instruct | 32B | 491 agent trajectories from 11 repos | 20.6 |
| OpenHands w/ Verifier ([Wang et al., 2024c](https://arxiv.org/html/2412.21139#bib.bib33)) (Ours) | fine-tuned Qwen2.5-Coder-Instruct | 32B (Agent & Verifier) | `491` agent trajectories from 11 repos for agent + `1318\times 2` success/failure agent trajectories for verifier | 32.0 |

Table 9: Performance comparison with SWE-Bench ([Jimenez et al., 2024](https://arxiv.org/html/2412.21139#bib.bib16)) baselines with publicly accessible weights.
Data source: <https://www.swebench.com/>, Accessed on Dec 21, 2024.

### B.1 Mean and Variance for Pass@N and Best@N.

We mostly follow ([Lightman et al., 2023](https://arxiv.org/html/2412.21139#bib.bib17)) for obtaining the mean and variance for the Pass@N and Best@N curve. Given a total of M rounds of rollouts, for `N<M`,
we calculate the mean and variance across 100 randomly selected sub-samples of size `N` from the `M` rollouts. For the OpenHands CodeActAgent inference-time scaling curve at §[3](https://arxiv.org/html/2412.21139#S5.F3 "Figure 3 ‣ 5.1.1 Verifier for General-Purpose Prompting ‣ 5.1 Inference-Time Scaling with Verifiers ‣ 5 Scaling Agent Performance with SWE-Gym ‣ Training Software Engineering Agents and Verifiers with SWE-Gym"), we exclude this calculation for N=1 , as we use a temperature of 0 for the first attempt.

### B.2 OpenHands Agent Experiments

During training, we use OpenHands’s remote runtime ([Neubig & Wang, 2024](https://arxiv.org/html/2412.21139#bib.bib20)) feature to execute agent trajectories in parallel on SWE-Gym.
We use torchtune ([PyTorch Team, 2024](https://arxiv.org/html/2412.21139#bib.bib23)) for full parameter fine-tuning with a learning rate of 1e-4, maximum 5 epochs, global batch size of 8, max context length of 32768. We fine-tuned both 7B, 14B, and 32B variant of the model, and experiments were performed with 2-8x NVIDIA H100 80G GPU on modal ([Modal, 2024](https://arxiv.org/html/2412.21139#bib.bib19)).
The only exception is in the main experiment of §[5.1.1](https://arxiv.org/html/2412.21139#S5.SS1.SSS1 "5.1.1 Verifier for General-Purpose Prompting ‣ 5.1 Inference-Time Scaling with Verifiers ‣ 5 Scaling Agent Performance with SWE-Gym ‣ Training Software Engineering Agents and Verifiers with SWE-Gym"), where we use LoRA ([Hu et al., 2022](https://arxiv.org/html/2412.21139#bib.bib12)) (29.8% `@8`) via Unsloth library ([Unsloth Team, 2024](https://arxiv.org/html/2412.21139#bib.bib30)) to train the verifier for max 2 epochs, while other hyper-parameter stays the same.

Inference during evaluation is bounded by either 100 interaction turns or the base LM’s 32k context window length, whichever is reached first.

### B.3 MoatlessTools Agent Experiments

All MoatlessTools models are trained with a context window of 10240.
For experiments with the 7B model, we use torchtune to train the policy model with full-finetuning using 4 H100 GPUs. We set batch size to 8, learning rate to `2\times 10^{-5}`, and train for 5 epochs.

For the 32B model, we use Unsloth ([Unsloth Team, 2024](https://arxiv.org/html/2412.21139#bib.bib30)) with a single H100 GPU for LoRA fine-tuning. We set the number of epochs to 5, batch size to 8, LoRA rank to 64, and learning rate to `5\times 10^{-4}`. We use the same configuration for verifier training.

For MoatlessAgent experiments, we serve the agent with FP8 quantization for improved throughput, which we found to have minimal effects on model performance.

### B.4 Details of OpenHands Trajectory Sampling

Trajectory Set
Sampled from Model
Sampled on Dataset
Temperature
Max Turns
Success trajectories

`D_{0}`
gpt-4o-2024-08-06
SWE-Gym Lite
0
30
19 (`8.26\%`)

(Cumulative) Total `D_{0}`
`\mathbf{19}`

`D_{1}\setminus D_{0}`
gpt-4o-2024-08-06
SWE-Gym Lite
0.2
30
11 (`4.78\%`)

gpt-4o-2024-08-06
SWE-Gym Lite
0.3
30
17 (`7.39\%`)

gpt-4o-2024-08-06
SWE-Gym Lite
0.4
30
21 (`9.13\%`)

gpt-4o-2024-08-06
SWE-Gym Lite
0.5
30
18 (`7.83\%`)

gpt-4o-2024-08-06
SWE-Gym Lite
0.8
30
20 (`8.70\%`)

(Cumulative) Total `D_{1}`
`\mathbf{106}`

`D_{2}\setminus D_{1}`
gpt-4o-2024-08-06
SWE-Gym Lite
0
50
19 (`8.26\%`)

claude-3-5-sonnet-20241022
SWE-Gym Lite
0
50
67 (`29.1\%`)

gpt-4o-2024-08-06
SWE-Gym Full
0
50
∗111 (`4.55\%`)

gpt-4o-2024-08-06
SWE-Gym Full
1
50
188 (`7.71\%`)

(Cumulative) Total `D_{2}`
`\mathbf{491}`

- *

  Run into infrastructure-related error where some instances failed to complete, this number might be under estimate of actual number of success trajectories.

Table 10: Summary of trajectories sampled from SWE-Gym.

As detailed in Tab. [10](https://arxiv.org/html/2412.21139#A2.T10 "Table 10 ‣ B.4 Details of OpenHands Trajectory Sampling ‣ Appendix B Experiment Details ‣ Training Software Engineering Agents and Verifiers with SWE-Gym"), we collect a few sets of trajectories for fine-tuning experiments.
We collect dataset `D_{0}` by sample gpt-4o-2024-08-06 on SWE-Gym Lite with temperature 0 and collected 19 trajectories that eventually solve the task (evaluated by unit test in SWE-Gym).
We then varied the temperatures (setting t={0.2, 0.3, 0.4, 0.5, 0.8}) and sample on SWE-Gym Lite. Combining these instances with `D_{0}`, we get 106 trajectories that solve the given problem (`D_{1}`).
We set the maximum number of turns to be 30 for both `D_{0}` and `D_{1}`.
To experiment on the effect of max turn, we set max number of turns to 50 and sample gpt-4o-2024-08-06 (19 resolved out of 230) and claude-3-5-sonnet-20241022 (67 resolved out of 230) with temperature 0 on SWE-Gym Lite, and sample gpt-4o-2024-08-06 (temperature t={0, 1}) on SWE-Gym full set (in total 299 resolved out of 4876 instances).
This gives us in in total 106 + 19 + 67 + 299 = 491 success trajectories, which forms our final training trajectories `D_{2}`.

### B.5 MoatlessTools ORM Prompt

The following is a pseudo-code that generates a prompt for MoatlessTools Verifier (ORM), which is modified from ([Zhang et al., 2024a](https://arxiv.org/html/2412.21139#bib.bib42)). Unlike ([Zhang et al., 2024a](https://arxiv.org/html/2412.21139#bib.bib42)), which relies on proprietary models like Claude-3.5-Sonnet for context extraction, we obtain context directly from the agent’s trajectory being evaluated.

[⬇](data:text/plain;base64,U1lTVEVNX01FU1NBR0UgPSAiIiJZb3UgYXJlIGFuIGV4cGVydCBpbiBweXRob24gZm9yIHNvZnR3YXJlIGVuZ2luZWVyaW5nIGFuZCBjb2RlIHJldmlldy4gWW91ciByZXNwb25zaWJpbGl0eSBpcyB0byByZXZpZXcgdGhlIHBhdGNoZXMgZ2VuZXJhdGVkIGJ5IGxhbmd1YWdlIG1vZGVscyB0byBmaXggc29tZSBpc3N1ZXMgYW5kIHByb3ZpZGUgZmVlZGJhY2sgb24gdGhlIHF1YWxpdHkgb2YgdGhlaXIgY29kZS4iIiIKClVTRVJfTUVTU0FHRT0iIiJJIHdhbnQgeW91IHRvIGV2YWx1YXRlIGFuIExMTS1nZW5lcmF0ZWQgY2FuZGlkYXRlIHBhdGNoIHRoYXQgdHJpZXMgdG8gcmVzb2x2ZSBhbiBpc3N1ZSBpbiBhIGNvZGViYXNlLgoKVG8gYXNzaXN0IHlvdSBpbiB0aGlzIHRhc2ssIHlvdSBhcmUgcHJvdmlkZWQgd2l0aCB0aGUgZm9sbG93aW5nIGluZm9ybWF0aW9uOgogLSBZb3UgYXJlIGdpdmVuIGFuIGlzc3VlIHRleHQgb24gYSBnaXRodWIgcmVwb3NpdG9yeSAod3JhcHBlZCB3aXRoIDxpc3N1ZV9kZXNjcmlwdGlvbj48L2lzc3VlX2Rlc2NyaXB0aW9uPikuCiAtIFlvdSBhcmUgYWxzbyBnaXZlbiBzb21lIGlkZW50aWZpZWQgY29kZSBzcGFucyB0aGF0IGFyZSByZWxldmFudCB0byB0aGUgaXNzdWUuCiAgICBFYWNoIGNvZGUgc3BhbiBpcyB3cmFwcGVkIHdpdGggPGNvZGVfc3BhbiBmaWxlX3BhdGg9RklMRV9QQVRIIHNwYW5faWQ9U1BBTl9JRD48L2NvZGVfc3Bhbj4gdGFncywgd2hlcmUgRklMRV9QQVRIIGlzIHRoZSBwYXRoIHRvIHRoZSBmaWxlIGNvbnRhaW5pbmcgdGhlIGNvZGUgc3BhbiwgYW5kIFNQQU5fSUQgaXMgdGhlIHVuaXF1ZSBpZGVudGlmaWVyIGZvciB0aGUgY29kZSBzcGFuLgogICAgRWFjaCBjb2RlIHNwYW4gYWxzbyBjb21lcyB3aXRoIHRoZSBsaW5lIG51bWJlcnMgZm9yIHlvdSB0byBiZXR0ZXIgdW5kZXJzdGFuZCB0aGUgY29udGV4dC4gSXQncyBwb3NzaWJsZSB0aGF0IHRoZSBjb2RlIHNwYW4gYXJlIG5vdCBzdWZmaWNpZW50IHRvIGZpeCB0aGUgaXNzdWUsIGFkanVzdCB5b3VyIHNjb3JlIGFjY29yZGluZ2x5LgogLSBZb3UgYXJlIGdpdmVuIHRoZSBjYW5kaWRhdGUgcGF0Y2ggdGhhdCB0cmllcyB0byByZXNvbHZlIHRoZSB0YXJnZXQgaXNzdWUuCiAgICBGb3IgeW91ciBjb252ZW5pZW5jZSwgeW91IGFyZSBnaXZlbiB0aGUgaHVua3Mgb2Ygb3JpZ2luYWwgY29kZSBhbmQgdGhlIGNvZGUgYWZ0ZXIgYXBwbHlpbmcgdGhlIHBhdGNoLgogICAgVGhlIGNvZGUgYmVmb3JlIHRoZSBwYXRjaCBpcyB3cmFwcGVkIHdpdGggPGJlZm9yZV9wYXRjaD48L2JlZm9yZV9wYXRjaD4gYW5kIHRoZSBjb2RlIGFmdGVyIHRoZSBwYXRjaCBpcyB3cmFwcGVkIHdpdGggPGFmdGVyX3BhdGNoPjwvYWZ0ZXJfcGF0Y2g+LgogICAgTm90ZSB0aGF0IHRoZSBmaWxlIG5hbWVzIGluIGJlZm9yZV9wYXRjaCBzdGFydHMgd2l0aCAnYS8nIGFuZCB0aGUgZmlsZSBuYW1lcyBpbiBhZnRlcl9wYXRjaCBzdGFydHMgd2l0aCAnYi8nLgoKCjxpc3N1ZV9kZXNjcmlwdGlvbj4Ke2lzc3VlX3RleHR9CjwvaXNzdWVfZGVzY3JpcHRpb24+Cgo8YmVmb3JlX3BhdGNoPgp7YmVmb3JlX3BhdGNofQo8L2JlZm9yZV9wYXRjaD4KCjxhZnRlcl9wYXRjaD4Ke2FmdGVyX3BhdGNofQo8L2FmdGVyX3BhdGNoPgoKe2NvZGVfc3BhbnN9CgpSZXNwb25zZSBpbiAiVHJ1ZSIgb3IgIkZhbHNlIiBmb3Igd2hldGhlciB0aGUgcGF0Y2ggaGFzIHJlc29sdmVkIHRoZSBpc3N1ZS4iIiI=)

SYSTEM_MESSAGE = ”””You are an expert in python for software engineering and code review. Your responsibility is to review the patches generated by language models to fix some issues and provide feedback on the quality of their code.”””

USER_MESSAGE=”””I want you to evaluate an LLM-generated candidate patch that tries to resolve an issue in a codebase.

To assist you in this task, you are provided with the following information:

- You are given an issue text on a github repository (wrapped with <issue_description></issue_description>).

- You are also given some identified code spans that are relevant to the issue.

Each code span is wrapped with <code_span file_path=FILE_PATH span_id=SPAN_ID></code_span> tags, where FILE_PATH is the path to the file containing the code span, and SPAN_ID is the unique identifier for the code span.

Each code span also comes with the line numbers for you to better understand the context. It’s possible that the code span are not sufficient to fix the issue, adjust your score accordingly.

- You are given the candidate patch that tries to resolve the target issue.

For your convenience, you are given the hunks of original code and the code after applying the patch.

The code before the patch is wrapped with <before_patch></before_patch> and the code after the patch is wrapped with <after_patch></after_patch>.

Note that the file names in before_patch starts with ’a/’ and the file names in after_patch starts with ’b/’.

<issue_description>

{issue_text}

</issue_description>

<before_patch>

{before_patch}

</before_patch>

<after_patch>

{after_patch}

</after_patch>

{code_spans}

Response in ”True” or ”False” for whether the patch has resolved the issue.”””

### B.6 OpenHands ORM Prompt

The following is a pseudo-code that generates a prompt for OpenHands Verifier (ORM).

[⬇](data:text/plain;base64,U1lTVEVNX01FU1NBR0UgPSAnJydZb3UgYXJlIGFuIGV4cGVydCBqdWRnZSBldmFsdWF0aW5nIEFJIGFzc2lzdGFudCBpbnRlcmFjdGlvbnMuIFlvdXIgdGFzayBpcyB0byBkZXRlcm1pbmUgaWYgdGhlIGFzc2lzdGFudCBzdWNjZXNzZnVsbHkgcmVzb2x2ZWQgdGhlIHVzZXIncyByZXF1ZXN0LgoKS2V5IGV2YWx1YXRpb24gY3JpdGVyaWE6CjEuIERpZCB0aGUgYXNzaXN0YW50IGNvbXBsZXRlIHRoZSBtYWluIHRhc2sgcmVxdWVzdGVkIGJ5IHRoZSB1c2VyPwoyLiBEaWQgdGhlIGFzc2lzdGFudCBoYW5kbGUgYWxsIGVkZ2UgY2FzZXMgYW5kIHJlcXVpcmVtZW50cyBzcGVjaWZpZWQ/CjMuIFdlcmUgdGhlcmUgYW55IGVycm9ycyBvciBpc3N1ZXMgaW4gdGhlIGZpbmFsIHNvbHV0aW9uPwo0LiBEaWQgdGhlIGFzc2lzdGFudCB2ZXJpZnkgdGhlIHNvbHV0aW9uIHdvcmtzIGFzIGludGVuZGVkPwoKUmVzcG9uZCBvbmx5IHdpdGggIjxqdWRnZW1lbnQ+WUVTPC9qdWRnZW1lbnQ+IiBvciAiPGp1ZGdlbWVudD5OTzwvanVkZ2VtZW50PiIuJycnCgpVU0VSX01FU1NBR0UgPSAnJydQbGVhc2UgZXZhbHVhdGUgdGhlIGZvbGxvd2luZyBpbnRlcmFjdGlvbiBiZXR3ZWVuIGFuIEFJIGFzc2lzdGFudCBhbmQgYSB1c2VyOgoKPT09IElOVEVSQUNUSU9OIExPRyA9PT0KJycnICsgdHJhal9zdHIgKyAnJycKPT09IEVORCBJTlRFUkFDVElPTiA9PT0KCkJhc2VkIG9uIHRoZSBhYm92ZSBpbnRlcmFjdGlvbiwgZGlkIHRoZSBhc3Npc3RhbnQgc3VjY2Vzc2Z1bGx5IHJlc29sdmUgdGhlIHVzZXIncyBpbml0aWFsIHJlcXVlc3Q/IFJlc3BvbmQgd2l0aCBZRVMgb3IgTk8uJycnCgptZXNzYWdlcyA9IFsKICAgIHsncm9sZSc6ICdzeXN0ZW0nLCAnY29udGVudCc6IFNZU1RFTV9NRVNTQUdFfSwKICAgIHsncm9sZSc6ICd1c2VyJywgJ2NvbnRlbnQnOiBVU0VSX01FU1NBR0V9LAogICAgeydyb2xlJzogJ2Fzc2lzdGFudCcsICdjb250ZW50JzogJzxqdWRnZW1lbnQ+JyArICgiWUVTIiBpZiByZXNvbHZlZCBlbHNlICJOTyIpICsgJzwvanVkZ2VtZW50Pid9Cl0=)

SYSTEM_MESSAGE = ”’You are an expert judge evaluating AI assistant interactions. Your task is to determine if the assistant successfully resolved the user’s request.

Key evaluation criteria:

1. Did the assistant complete the main task requested by the user?

2. Did the assistant handle all edge cases and requirements specified?

3. Were there any errors or issues in the final solution?

4. Did the assistant verify the solution works as intended?

Respond only with ”<judgement>YES</judgement>” or ”<judgement>NO</judgement>”.”’

USER_MESSAGE = ”’Please evaluate the following interaction between an AI assistant and a user:

=== INTERACTION LOG ===

”’ + traj_str + ”’

=== END INTERACTION ===

Based on the above interaction, did the assistant successfully resolve the user’s initial request? Respond with YES or NO.”’

messages = [

{’role’: ’system’, ’content’: SYSTEM_MESSAGE},

{’role’: ’user’, ’content’: USER_MESSAGE},

{’role’: ’assistant’, ’content’: ’<judgement>’ + (”YES” if resolved else ”NO”) + ’</judgement>’}

]

The last assistant messages that contains judgement is only provided during training time. At inference time, the trained verifier is responsible predicting the probability of ‘Yes’ and ‘No’.
