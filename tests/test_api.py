from fastapi.testclient import TestClient

from llm_eval.api import app

client = TestClient(app)

RUBRIC = {
    "id": "r1",
    "criteria": [
        {"name": "correctness", "description": "", "weight": 0.75},
        {"name": "style", "description": "", "weight": 0.25},
    ],
}


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_score_endpoint():
    body = {
        "rubric": RUBRIC,
        "evaluation": {"item_id": "x", "model": "m", "scores": {"correctness": 5, "style": 1}},
    }
    response = client.post("/score", json=body)
    assert response.status_code == 200
    assert response.json() == {"item_id": "x", "model": "m", "score": 75.0}


def test_score_endpoint_rejects_mismatched_criteria():
    body = {
        "rubric": RUBRIC,
        "evaluation": {"item_id": "x", "model": "m", "scores": {"correctness": 5}},
    }
    response = client.post("/score", json=body)
    assert response.status_code == 422
    assert "missing" in response.json()["detail"]


def test_score_endpoint_rejects_invalid_rubric():
    bad_rubric = {**RUBRIC, "criteria": [{"name": "a", "description": "", "weight": 0.3}]}
    body = {
        "rubric": bad_rubric,
        "evaluation": {"item_id": "x", "model": "m", "scores": {"a": 3}},
    }
    assert client.post("/score", json=body).status_code == 422
