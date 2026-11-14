"""Summarize scored evaluations with pandas."""

from __future__ import annotations

import pandas as pd

from .schemas import Benchmark, Evaluation
from .scoring import score_all


def build_frame(benchmark: Benchmark, evaluations: list[Evaluation]) -> pd.DataFrame:
    """One row per evaluation: item, model, category, score, failure tags."""
    return pd.DataFrame(score_all(benchmark, evaluations))


def model_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Mean score per model, overall and per category, best model first."""
    by_category = df.pivot_table(
        index="model", columns="category", values="score", aggfunc="mean"
    )
    by_category.insert(0, "overall", df.groupby("model")["score"].mean())
    by_category.insert(1, "n", df.groupby("model").size())
    return by_category.sort_values("overall", ascending=False).round(2)


def failure_counts(df: pd.DataFrame) -> pd.DataFrame:
    """How often each failure tag appears, per model."""
    exploded = df.explode("failure_tags").dropna(subset=["failure_tags"])
    if exploded.empty:
        return pd.DataFrame()
    return (
        exploded.groupby(["failure_tags", "model"])
        .size()
        .unstack(fill_value=0)
        .sort_values(by=list(exploded["model"].unique()), ascending=False)
    )


def render_markdown(benchmark: Benchmark, evaluations: list[Evaluation]) -> str:
    """A full Markdown report: model leaderboard plus failure breakdown."""
    df = build_frame(benchmark, evaluations)
    parts = [
        f"# {benchmark.name}: evaluation report",
        f"{len(df)} evaluations across {df['model'].nunique()} models "
        f"and {df['item_id'].nunique()} items. Scores are 0-100.",
        "## Scores by model",
        model_summary(df).to_markdown(),
    ]
    failures = failure_counts(df)
    if not failures.empty:
        parts += ["## Failure tags", failures.to_markdown()]
    return "\n\n".join(parts) + "\n"
