# LLM Eval Framework

[![CI](https://github.com/jaymwangi2026-eng/llm-eval-framework/actions/workflows/ci.yml/badge.svg)](https://github.com/jaymwangi2026-eng/llm-eval-framework/actions/workflows/ci.yml)

A small, tested Python framework for grading language-model responses against weighted rubrics and reporting where models fail.

It takes a **benchmark** (prompts, reference solutions and rubrics) and a file of **evaluations** (a grader's 1–5 scores per criterion, plus failure tags), validates both, turns the scores into a weighted 0–100 score, and produces a report comparing models by category and failure type. The same scoring is available as a FastAPI service.

## Why

Grading model outputs by hand is error-prone in quiet ways: a misspelled criterion, rubric weights that add up to 1.1, a score of 6 on a 1–5 scale. This project makes those mistakes fail loudly when files are loaded, so the numbers in the final report can be trusted.

## Features

- **Validated schemas** (Pydantic): rubric weights must sum to 1, criterion names must be unique, scores must be 1–5, every item must point to a real rubric, failure tags come from a fixed list.
- **Weighted scoring**: each 1–5 grade is rescaled to 0–1, weighted, and summed to a 0–100 score. Evaluations with missing or unknown criteria are rejected.
- **Failure categorization**: tags such as `missed_edge_case`, `flawed_reasoning` and `ignored_constraint` are counted per model.
- **Reports** (pandas): a leaderboard by model and category, and a failure-tag breakdown, as Markdown.
- **REST API** (FastAPI): `POST /score` scores one evaluation against a rubric.
- **Tests and CI**: 24 pytest tests and a GitHub Actions workflow that lints and tests on Python 3.10–3.12.

## Quick start

```bash
git clone https://github.com/jaymwangi2026-eng/llm-eval-framework.git
cd llm-eval-framework
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

pytest                              # run the tests
llm-eval data/sample_benchmark.json data/sample_evaluations.jsonl
```

Example output:

```
## Scores by model

| model   |   overall |   n |   coding |   instruction_following |   reasoning |
|:--------|----------:|----:|---------:|------------------------:|------------:|
| model-a |     80.31 |   4 |    85    |                      55 |       96.25 |
| model-b |     46.56 |   4 |    38.12 |                      90 |       20    |

## Failure tags

| failure_tags         |   model-a |   model-b |
|:---------------------|----------:|----------:|
| missed_edge_case     |         1 |         1 |
| code_error           |         0 |         1 |
| ...
```

## Running the API

```bash
uvicorn llm_eval.api:app --reload
```

Open http://127.0.0.1:8000/docs for interactive documentation, or call it directly:

```bash
curl -X POST http://127.0.0.1:8000/score -H "Content-Type: application/json" -d '{
  "rubric": {"id": "r1", "criteria": [
    {"name": "correctness", "description": "", "weight": 0.75},
    {"name": "style", "description": "", "weight": 0.25}]},
  "evaluation": {"item_id": "q1", "model": "model-a",
    "scores": {"correctness": 5, "style": 1}}
}'
# {"item_id":"q1","model":"model-a","score":75.0}
```

## File formats

**Benchmark** (`.json`): a name, a list of rubrics, and a list of items. See [`data/sample_benchmark.json`](data/sample_benchmark.json).

```json
{
  "name": "My benchmark",
  "rubrics": [{"id": "coding-v1", "criteria": [
    {"name": "correctness", "description": "...", "weight": 0.6},
    {"name": "edge_cases",  "description": "...", "weight": 0.4}]}],
  "items": [{"id": "code-001", "category": "coding", "prompt": "...",
             "reference_solution": "...", "rubric_id": "coding-v1"}]
}
```

**Evaluations** (`.jsonl`): one evaluation per line. See [`data/sample_evaluations.jsonl`](data/sample_evaluations.jsonl).

```json
{"item_id": "code-001", "model": "model-a", "scores": {"correctness": 5, "edge_cases": 3}, "failure_tags": ["missed_edge_case"], "rationale": "Fails on an empty list."}
```

## How scoring works

For a rubric with criteria weights *w* and grades *g* on a 1–5 scale:

```
score = 100 × Σ w_i × (g_i − 1) / 4
```

So all 5s gives 100, all 1s gives 0, and a criterion's influence on the score equals its weight.

## Project layout

```
src/llm_eval/
  schemas.py   Pydantic models and validation rules
  scoring.py   weighted scoring
  loader.py    reading JSON / JSONL files with clear error messages
  report.py    pandas summaries and the Markdown report
  api.py       FastAPI service
  cli.py       the llm-eval command
tests/         pytest suite
data/          sample benchmark and evaluations
```

## Roadmap

- Inter-grader agreement (Cohen's kappa) when several graders score the same item
- Confidence intervals on model scores via bootstrapping
- Pairwise preference (A vs B) evaluations alongside rubric scores
- HTML report with charts

## License

MIT
