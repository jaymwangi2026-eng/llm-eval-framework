import pytest

from llm_eval.cli import main
from llm_eval.loader import LoadError, load_evaluations
from llm_eval.report import build_frame, failure_counts, model_summary, render_markdown

from .conftest import DATA


def test_model_summary_ranks_models(benchmark, evaluations):
    summary = model_summary(build_frame(benchmark, evaluations))
    assert list(summary.index) == ["model-a", "model-b"]
    assert summary.loc["model-a", "n"] == 4
    assert {"overall", "coding", "reasoning", "instruction_following"} <= set(summary.columns)


def test_failure_counts(benchmark, evaluations):
    counts = failure_counts(build_frame(benchmark, evaluations))
    assert counts.loc["missed_edge_case", "model-a"] == 1
    assert counts.loc["missed_edge_case", "model-b"] == 1
    assert counts.loc["code_error", "model-b"] == 1


def test_render_markdown(benchmark, evaluations):
    report = render_markdown(benchmark, evaluations)
    assert report.startswith("# Sample benchmark")
    assert "## Scores by model" in report
    assert "## Failure tags" in report


def test_bad_jsonl_reports_line_number(tmp_path):
    path = tmp_path / "evals.jsonl"
    path.write_text('{"item_id": "x", "model": "m", "scores": {"a": 3}}\n{not json}\n')
    with pytest.raises(LoadError, match="line 2"):
        load_evaluations(path)


def test_cli_writes_report(tmp_path):
    out = tmp_path / "report.md"
    benchmark = str(DATA / "sample_benchmark.json")
    evaluations = str(DATA / "sample_evaluations.jsonl")
    code = main([benchmark, evaluations, "-o", str(out)])
    assert code == 0
    assert "Scores by model" in out.read_text()


def test_cli_returns_error_code_on_bad_input(tmp_path, capsys):
    bad = tmp_path / "evals.jsonl"
    bad.write_text('{"item_id": "nope", "model": "m", "scores": {"a": 3}}\n')
    code = main([str(DATA / "sample_benchmark.json"), str(bad)])
    assert code == 1
    assert "error" in capsys.readouterr().err
