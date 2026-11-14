"""Read benchmark and evaluation files from disk."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from .schemas import Benchmark, Evaluation


class LoadError(ValueError):
    """A file couldn't be parsed; the message says where and why."""


def load_benchmark(path: str | Path) -> Benchmark:
    """Load a benchmark from a JSON file."""
    text = Path(path).read_text(encoding="utf-8")
    try:
        return Benchmark.model_validate_json(text)
    except ValidationError as exc:
        raise LoadError(f"{path}: invalid benchmark\n{exc}") from exc


def load_evaluations(path: str | Path) -> list[Evaluation]:
    """Load evaluations from a JSONL file (one JSON object per line).

    Blank lines are skipped. Errors report the line number so bad rows
    are easy to find in large files.
    """
    evaluations = []
    with Path(path).open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            if not line.strip():
                continue
            try:
                evaluations.append(Evaluation.model_validate(json.loads(line)))
            except (json.JSONDecodeError, ValidationError) as exc:
                raise LoadError(f"{path}, line {line_no}: {exc}") from exc
    return evaluations
