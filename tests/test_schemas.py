import pytest
from pydantic import ValidationError

from llm_eval import Benchmark, Criterion, Evaluation, Rubric


def test_rubric_weights_must_sum_to_one():
    with pytest.raises(ValidationError, match="sum to 1"):
        Rubric(
            id="bad",
            criteria=[
                Criterion(name="a", description="", weight=0.5),
                Criterion(name="b", description="", weight=0.4),
            ],
        )


def test_rubric_rejects_duplicate_criteria():
    with pytest.raises(ValidationError, match="duplicate"):
        Rubric(
            id="bad",
            criteria=[
                Criterion(name="a", description="", weight=0.5),
                Criterion(name="a", description="", weight=0.5),
            ],
        )


@pytest.mark.parametrize("value", [0, 6, -1])
def test_score_out_of_range_rejected(value):
    with pytest.raises(ValidationError, match="must be 1-5"):
        Evaluation(item_id="x", model="m", scores={"correctness": value})


def test_unknown_failure_tag_rejected():
    with pytest.raises(ValidationError):
        Evaluation(item_id="x", model="m", scores={"a": 3}, failure_tags=["not_a_tag"])


def test_item_must_reference_existing_rubric(rubric):
    with pytest.raises(ValidationError, match="unknown rubric"):
        Benchmark(
            name="b",
            rubrics=[rubric],
            items=[
                {
                    "id": "i1",
                    "category": "coding",
                    "prompt": "p",
                    "reference_solution": "s",
                    "rubric_id": "missing",
                }
            ],
        )


def test_sample_benchmark_loads(benchmark):
    assert len(benchmark.items) == 4
    assert benchmark.rubric_for("code-001").id == "coding-v1"
