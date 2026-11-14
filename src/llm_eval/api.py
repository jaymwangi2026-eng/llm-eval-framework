"""A small HTTP API for scoring evaluations.

Run it with:  uvicorn llm_eval.api:app --reload
Then open http://127.0.0.1:8000/docs for interactive documentation.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .schemas import Evaluation, Rubric
from .scoring import ScoringError, weighted_score

app = FastAPI(title="LLM Eval API", version="0.1.0")


class ScoreRequest(BaseModel):
    rubric: Rubric
    evaluation: Evaluation


class ScoreResponse(BaseModel):
    item_id: str
    model: str
    score: float


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/score", response_model=ScoreResponse)
def score(request: ScoreRequest) -> ScoreResponse:
    try:
        value = weighted_score(request.evaluation, request.rubric)
    except ScoringError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return ScoreResponse(
        item_id=request.evaluation.item_id,
        model=request.evaluation.model,
        score=value,
    )
