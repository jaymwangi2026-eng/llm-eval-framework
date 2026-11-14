"""Validated data models for benchmarks and evaluations.

Every input file is parsed into these models, so bad data (a typo in a
criterion name, weights that don't add up, a score out of range) fails
loudly at load time instead of silently skewing results.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator

SCORE_MIN = 1
SCORE_MAX = 5


class Category(str, Enum):
    """The kind of skill a benchmark item tests."""

    REASONING = "reasoning"
    CODING = "coding"
    INSTRUCTION_FOLLOWING = "instruction_following"


class FailureTag(str, Enum):
    """Why a response fell short. One response can have several tags."""

    INCORRECT_ANSWER = "incorrect_answer"
    FLAWED_REASONING = "flawed_reasoning"
    WRONG_ASSUMPTION = "wrong_assumption"
    MISSED_EDGE_CASE = "missed_edge_case"
    CODE_ERROR = "code_error"
    INEFFICIENT_SOLUTION = "inefficient_solution"
    IGNORED_CONSTRAINT = "ignored_constraint"
    FORMAT_VIOLATION = "format_violation"
    HALLUCINATION = "hallucination"


class Criterion(BaseModel):
    """One dimension a response is graded on, e.g. 'correctness'."""

    name: str = Field(min_length=1)
    description: str
    weight: float = Field(gt=0, le=1)


class Rubric(BaseModel):
    """A set of weighted criteria. Weights must sum to 1."""

    id: str = Field(min_length=1)
    criteria: list[Criterion] = Field(min_length=1)

    @field_validator("criteria")
    @classmethod
    def names_are_unique(cls, criteria: list[Criterion]) -> list[Criterion]:
        names = [c.name for c in criteria]
        if len(names) != len(set(names)):
            raise ValueError(f"duplicate criterion names: {names}")
        return criteria

    @field_validator("criteria")
    @classmethod
    def weights_sum_to_one(cls, criteria: list[Criterion]) -> list[Criterion]:
        total = sum(c.weight for c in criteria)
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"criterion weights must sum to 1, got {total:.4f}")
        return criteria

    def criterion_names(self) -> set[str]:
        return {c.name for c in self.criteria}


class BenchmarkItem(BaseModel):
    """A single prompt in the benchmark, with its reference solution."""

    id: str = Field(min_length=1)
    category: Category
    prompt: str = Field(min_length=1)
    reference_solution: str
    rubric_id: str


class Benchmark(BaseModel):
    """A named collection of rubrics and the items graded with them."""

    name: str
    rubrics: list[Rubric] = Field(min_length=1)
    items: list[BenchmarkItem] = Field(min_length=1)

    @model_validator(mode="after")
    def check_references(self) -> Benchmark:
        rubric_ids = [r.id for r in self.rubrics]
        if len(rubric_ids) != len(set(rubric_ids)):
            raise ValueError("duplicate rubric ids")
        item_ids = [i.id for i in self.items]
        if len(item_ids) != len(set(item_ids)):
            raise ValueError("duplicate item ids")
        for item in self.items:
            if item.rubric_id not in rubric_ids:
                raise ValueError(
                    f"item {item.id!r} uses unknown rubric {item.rubric_id!r}"
                )
        return self

    def rubric_for(self, item_id: str) -> Rubric:
        item = self.item(item_id)
        return next(r for r in self.rubrics if r.id == item.rubric_id)

    def item(self, item_id: str) -> BenchmarkItem:
        for item in self.items:
            if item.id == item_id:
                return item
        raise KeyError(f"unknown item id {item_id!r}")


class Evaluation(BaseModel):
    """A grader's scores for one model's response to one item."""

    item_id: str
    model: str = Field(min_length=1)
    scores: dict[str, int]
    failure_tags: list[FailureTag] = Field(default_factory=list)
    rationale: str = ""

    @field_validator("scores")
    @classmethod
    def scores_in_range(cls, scores: dict[str, int]) -> dict[str, int]:
        for name, value in scores.items():
            if not SCORE_MIN <= value <= SCORE_MAX:
                raise ValueError(
                    f"score for {name!r} must be {SCORE_MIN}-{SCORE_MAX}, got {value}"
                )
        return scores
