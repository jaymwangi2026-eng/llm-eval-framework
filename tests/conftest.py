from pathlib import Path

import pytest

from llm_eval import Criterion, Rubric, load_benchmark, load_evaluations

DATA = Path(__file__).resolve().parent.parent / "data"


@pytest.fixture
def benchmark():
    return load_benchmark(DATA / "sample_benchmark.json")


@pytest.fixture
def evaluations():
    return load_evaluations(DATA / "sample_evaluations.jsonl")


@pytest.fixture
def rubric():
    return Rubric(
        id="r1",
        criteria=[
            Criterion(name="correctness", description="", weight=0.75),
            Criterion(name="style", description="", weight=0.25),
        ],
    )
