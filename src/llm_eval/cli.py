"""Command-line entry point: llm-eval BENCHMARK EVALUATIONS [-o REPORT]"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .loader import LoadError, load_benchmark, load_evaluations
from .report import render_markdown
from .scoring import ScoringError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="llm-eval", description="Score model evaluations and print a report."
    )
    parser.add_argument("benchmark", help="benchmark JSON file")
    parser.add_argument("evaluations", help="evaluations JSONL file")
    parser.add_argument("-o", "--output", help="write the report to this file")
    args = parser.parse_args(argv)

    try:
        benchmark = load_benchmark(args.benchmark)
        evaluations = load_evaluations(args.evaluations)
        report = render_markdown(benchmark, evaluations)
    except (LoadError, ScoringError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
