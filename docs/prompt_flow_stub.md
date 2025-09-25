# Azure Prompt Flow (Stub)

This template uses a deterministic FastAPI endpoint for demo.
To use Prompt Flow:
1) Open Azure AI Studio (Prompt Flow).
2) Create a flow that calls your API or LLM with a fixed prompt.
3) Create an Evaluation flow with a CSV dataset (mirror `evals/golden_set.csv`).
4) Define pass/fail metrics (e.g., "answer contains expected substring").
5) Export eval results (CSV/JSON) and drop into `reports/evals.json` for evidence.

Notes:
- Use Content Safety for PII/toxicity checks in eval flows.
- Gate releases on Prompt Flow eval pass % thresholds.
