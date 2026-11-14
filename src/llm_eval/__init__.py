"""llm_eval: validated schemas, weighted scoring and reports for LLM evaluations."""

from .loader import load_benchmark, load_evaluations
from .schemas import Benchmark, BenchmarkItem, Category, Criterion, Evaluation, FailureTag, Rubric
from .scoring import ScoringError, weighted_score

__all__ = [
    "Benchmark",
    "BenchmarkItem",
    "Category",
    "Criterion",
    "Evaluation",
    "FailureTag",
    "Rubric",
    "ScoringError",
    "load_benchmark",
    "load_evaluations",
    "weighted_score",
]
__version__ = "0.1.0"
