"""Turn per-criterion grades into a single weighted score."""

from __future__ import annotations

from .schemas import SCORE_MAX, SCORE_MIN, Benchmark, Evaluation, Rubric


class ScoringError(ValueError):
    """An evaluation doesn't match the rubric it's scored against."""


def weighted_score(evaluation: Evaluation, rubric: Rubric) -> float:
    """Return a 0-100 score for one evaluation.

    Each criterion's 1-5 grade is rescaled to 0-1, multiplied by the
    criterion's weight, and summed. A response graded 5 on everything
    scores 100; graded 1 on everything scores 0.
    """
    expected = rubric.criterion_names()
    given = set(evaluation.scores)
    if missing := expected - given:
        raise ScoringError(f"{evaluation.item_id}: missing scores for {sorted(missing)}")
    if extra := given - expected:
        raise ScoringError(f"{evaluation.item_id}: unknown criteria {sorted(extra)}")

    span = SCORE_MAX - SCORE_MIN
    total = sum(
        c.weight * (evaluation.scores[c.name] - SCORE_MIN) / span
        for c in rubric.criteria
    )
    return round(total * 100, 2)


def score_all(benchmark: Benchmark, evaluations: list[Evaluation]) -> list[dict]:
    """Score every evaluation and return flat rows ready for a DataFrame."""
    rows = []
    for ev in evaluations:
        item = benchmark.item(ev.item_id)
        rows.append(
            {
                "item_id": ev.item_id,
                "model": ev.model,
                "category": item.category.value,
                "score": weighted_score(ev, benchmark.rubric_for(ev.item_id)),
                "failure_tags": [t.value for t in ev.failure_tags],
            }
        )
    return rows
