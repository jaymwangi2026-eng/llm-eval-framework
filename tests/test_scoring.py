import pytest

from llm_eval import Evaluation, ScoringError, weighted_score
from llm_eval.scoring import score_all


def make_eval(**scores):
    return Evaluation(item_id="x", model="m", scores=scores)


def test_perfect_scores_give_100(rubric):
    assert weighted_score(make_eval(correctness=5, style=5), rubric) == 100.0


def test_lowest_scores_give_0(rubric):
    assert weighted_score(make_eval(correctness=1, style=1), rubric) == 0.0


def test_weights_are_applied(rubric):
    # correctness 5 -> 1.0 * 0.75, style 1 -> 0.0 * 0.25
    assert weighted_score(make_eval(correctness=5, style=1), rubric) == 75.0
    # correctness 3 -> 0.5 * 0.75 = 0.375, style 5 -> 0.25
    assert weighted_score(make_eval(correctness=3, style=5), rubric) == 62.5


def test_missing_criterion_raises(rubric):
    with pytest.raises(ScoringError, match="missing"):
        weighted_score(make_eval(correctness=5), rubric)


def test_unknown_criterion_raises(rubric):
    with pytest.raises(ScoringError, match="unknown"):
        weighted_score(make_eval(correctness=5, style=5, speed=3), rubric)


def test_score_all_on_sample_data(benchmark, evaluations):
    rows = score_all(benchmark, evaluations)
    assert len(rows) == len(evaluations)
    assert all(0 <= r["score"] <= 100 for r in rows)
    first = rows[0]
    assert first["category"] == "coding"
