# LLM Evaluation Framework

A portfolio-grade demo of a **hybrid LLM evaluation architecture** that combines:

- **Deterministic checks** for objective signals such as tests, execution status, task validation, and pass/fail outcomes.
- **LLM-as-a-Judge** for qualitative dimensions such as correctness, reasoning quality, minimality/safety, and instruction following.
- **Score fusion** to combine objective and qualitative evidence into a single benchmark view.
- **Traceability and production controls** for reproducibility, retries, observability, latency, token usage, and cost.

The project is intentionally synthetic and contains **no customer data or confidential production infrastructure**.

---

## Why this project exists

Production GenAI systems cannot be evaluated reliably with a single metric.

Some behaviors are best measured deterministically:

- Did the code compile?
- Did tests pass?
- Did the task complete successfully?
- Was the expected output produced?

Other behaviors require judgment:

- Is the answer actually correct beyond the test coverage?
- Is the reasoning coherent?
- Did the model make unnecessary or risky changes?
- Did it follow the user's instructions?

This project demonstrates how those two evaluation modes can be combined into a practical evaluation workflow.

---

## What the demo includes

The synthetic benchmark contains four task families:

1. **Repository Bug Fix** — SWE-bench inspired
2. **Terminal Troubleshooting** — Terminal-Bench inspired
3. **Code Generation + Tests**
4. **Repository Refactor / Regression Fix** — SWE-bench inspired

Candidate models are anonymized as:

- Candidate Model A
- Candidate Model B
- Candidate Model C

The Streamlit application includes four views:

- **Benchmark Run** — execute the synthetic evaluation workflow and compare models.
- **Task & Judge Trace** — inspect deterministic signals, judge scores, and rationale.
- **Scale** — explain how the architecture evolves toward large evaluation volumes.
- **Architecture** — show the end-to-end production evaluation pattern.

---

## Evaluation methodology

### 1. Deterministic evaluation

Where the task allows it, the system first captures objective signals such as:

- Unit and regression test results
- Build or execution status
- Exit codes
- Task-specific validation
- Environment checks

These signals provide a reproducible baseline.

### 2. LLM-as-a-Judge

The qualitative judge scores each candidate across four dimensions:

| Dimension | What it measures |
|---|---|
| Correctness | Whether the solution actually satisfies the task |
| Reasoning quality | Whether the approach is coherent and technically sound |
| Minimality / safety | Whether the solution avoids unnecessary or risky changes |
| Instruction following | Whether the response follows the requested constraints |

### 3. Hybrid score

The local demo combines the two signal types:

```text
Hybrid Score =
    70% qualitative judge score
  + 30% deterministic task signal
```

This weighting is illustrative. In a production system, weights should be selected and validated against the use case, human review, and business risk.

---

## Architecture

```text
Coding / Agent Tasks
        |
        v
Candidate Model Outputs
        |
        v
+-------------------------------+
|       Hybrid Evaluation       |
|                               |
|  Deterministic checks         |
|  +                            |
|  LLM-as-a-Judge               |
+-------------------------------+
        |
        v
Score Fusion
        |
        v
Leaderboard / Regression Views
        |
        v
Tracing, Metrics, Cost, Review
```

A production-scale execution layer would typically add:

```text
Scheduler
   |
   v
Queue / Backpressure
   |
   v
Evaluation Workers
   |
   +--> Deterministic Evaluators
   |
   +--> LLM Judge
   |
   v
Idempotent Results Store
   |
   v
Metrics / Traces / Cost / Regression Analysis
```

---

## Repository structure

```text
llm-evaluation-framework/
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
├── .streamlit/
│   └── config.toml
├── data/
│   └── benchmark_tasks.json
└── src/
    └── judge.py
```

### Key files

**`app.py`**  
Streamlit application containing the benchmark UI, leaderboard, traces, scaling view, and architecture view.

**`src/judge.py`**  
Synthetic LLM-as-a-Judge implementation used by the local demo.

**`data/benchmark_tasks.json`**  
Synthetic benchmark tasks, candidate outputs, references, and deterministic evaluation signals.

---

## Quick start

### Prerequisites

- Python 3.10 or newer
- `pip`
- Git is optional unless you want to publish or contribute

### macOS / Linux

Clone the repository:

```bash
git clone https://github.com/vinokri/llm-evaluation-framework.git
cd llm-evaluation-framework
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
streamlit run app.py
```

Streamlit should open the application in your browser automatically.

### Windows PowerShell

```powershell
git clone https://github.com/vinokri/llm-evaluation-framework.git
cd llm-evaluation-framework

py -m venv .venv
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
streamlit run app.py
```

---

## Run without cloning

If you downloaded the project ZIP instead:

1. Unzip the folder.
2. Open Terminal or PowerShell in the extracted folder.
3. Create a virtual environment.
4. Install the requirements.
5. Start Streamlit.

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

---

## Recommended demo walkthrough

For a short technical walkthrough:

### 1. Benchmark Run

Explain that the benchmark evaluates anonymized candidate models across several synthetic coding-task families.

Run the benchmark and show:

- Hybrid score
- Deterministic pass rate
- Correctness
- Reasoning quality
- Minimality / safety
- Instruction following
- Judge latency

### 2. Task & Judge Trace

Pick an individual task and explain:

- The task prompt
- Candidate output
- Deterministic results
- Qualitative scores
- Judge rationale

The main point is that **tests alone can miss qualitative failures, while an LLM judge alone lacks objective execution evidence**.

### 3. Architecture

Explain the hybrid pattern:

```text
Task -> Candidate Model -> Deterministic Checks + LLM Judge
     -> Score Fusion -> Analysis
```

Then describe the production execution controls:

- Partitioning
- Queuing
- Backpressure
- Worker fan-out
- Retries
- Idempotency
- Versioning
- Traceability
- Token and cost monitoring

### 4. Scale

Use the scale view to explain architecture, not to claim that the local application processed production-scale traffic.

---

## Important demo disclosure

The local portfolio application uses:

- Synthetic tasks
- Synthetic candidate outputs
- Simulated LLM judge responses
- Illustrative scale figures

It does **not** make live Amazon Bedrock calls.

It does **not** claim that this local repository processed millions of evaluations.

A precise way to describe the project is:

> This repository is a synthetic recreation of a production LLM evaluation pattern. It demonstrates how deterministic signals and LLM-as-a-Judge can be combined into a reproducible evaluation architecture without exposing customer data or production infrastructure.

---

## How this would evolve for production

The local project intentionally keeps infrastructure out of the critical path so the evaluation design is easy to inspect.

A production implementation could add:

### Real judge invocation

Replace the simulated judge with a model API such as:

- Amazon Bedrock
- Anthropic API
- OpenAI API
- Another approved enterprise model endpoint

The judge should use:

- Temperature near zero for consistency
- Structured output / JSON schema enforcement
- Versioned prompts and rubrics
- Retry and timeout policies
- Judge-model version tracking

### Dataset management

Store versioned evaluation datasets containing:

- Input
- Expected behavior
- Reference answers where appropriate
- Metadata and evaluation slices
- Risk category
- Difficulty
- Human labels

### Distributed execution

For larger workloads:

- Partition evaluation jobs
- Put independent units of work on a queue
- Fan out across worker processes
- Enforce service quotas and concurrency limits
- Apply backpressure
- Use idempotent result writes

### Evaluation observability

Capture per evaluation:

- Candidate model version
- Judge model version
- Dataset version
- Rubric version
- Latency
- Input/output token usage
- Cost
- Retry count
- Deterministic results
- Judge scores
- Judge rationale
- Trace ID

### Regression testing

Store a trusted baseline and compare new model, prompt, retrieval, or agent versions against it.

Useful views include:

- Overall score change
- Category-level regressions
- Safety regressions
- Pairwise win rate
- Cost / quality trade-offs
- Latency / quality trade-offs

---

## LLM-as-a-Judge limitations

LLM judges are useful, but they are not ground truth.

Important failure modes include:

- Position bias
- Verbosity bias
- Self-preference or model-family bias
- Sensitivity to rubric wording
- Inconsistent judgments
- Reference-answer leakage
- Failure to recognize subtle domain errors
- Correlated errors between candidate and judge

Mitigations can include:

- Deterministic checks whenever possible
- Strong, explicit rubrics
- Structured judge output
- Multiple judge passes
- Pairwise evaluation
- Position swapping
- Human calibration sets
- Inter-rater agreement analysis
- Ground-truth datasets
- Periodic judge validation

---

## Security and privacy

Do not commit:

- API keys
- AWS credentials
- `.env` files
- Streamlit secrets
- Customer data
- Proprietary prompts or datasets
- Internal architecture documents
- Confidential performance or commercial metrics

The included `.gitignore` excludes common local secret and environment files, but always inspect `git status` before publishing.

---

## Publish this project to GitHub

Create a new **public** GitHub repository named:

```text
llm-evaluation-framework
```

Suggested repository description:

> Hybrid LLM evaluation framework combining deterministic checks and LLM-as-a-Judge for correctness, reasoning, safety, instruction following, and regression analysis.

Do not initialize the GitHub repository with another README if you are pushing this folder directly.

From this project folder:

```bash
git init -b main
git status
```

Review the files carefully.

Then:

```bash
git add .
git status
```

Verify that no credentials or private files are staged.

Commit:

```bash
git commit -m "Initial release: LLM evaluation framework"
```

Connect the repository:

```bash
git remote add origin https://github.com/vinokri/llm-evaluation-framework.git
```

Push:

```bash
git push -u origin main
```

---

## Suggested GitHub metadata

**Repository name**

```text
llm-evaluation-framework
```

**Description**

```text
Hybrid LLM evaluation framework combining deterministic checks and LLM-as-a-Judge for production-oriented model and agent evaluation.
```

**Suggested topics**

```text
llm-evaluation
llm-as-a-judge
generative-ai
agentic-ai
evals
rag
benchmarking
streamlit
ai-agents
```

---

## Portfolio positioning

This project is intended to demonstrate practical understanding of:

- LLM evaluation design
- Hybrid deterministic and model-based evaluation
- LLM-as-a-Judge
- Evaluation rubrics
- Judge consistency and bias
- Regression testing
- Distributed evaluation architecture
- Reliability and idempotency
- Observability
- Token and cost management
- Enterprise AI production patterns

It is a portfolio demonstration rather than a customer production artifact.

---

## Next extensions

Useful future additions would include:

1. Live model-provider integration behind an explicit configuration flag
2. Pairwise evaluation
3. Position-swapped judging
4. Judge-consistency analysis
5. Human-labeled calibration data
6. Regression gates for CI/CD
7. Cost-versus-quality analysis
8. Evaluation slices by task category
9. Exportable JSON/CSV evaluation reports
10. Automated red-team and safety evaluation suites
