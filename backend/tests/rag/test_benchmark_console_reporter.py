import pytest

from app.rag.evaluation.benchmark_console_reporter import (
    BenchmarkConsoleReporter,
)
from app.rag.evaluation.benchmark_report import (
    BenchmarkReport,
)
from app.rag.evaluation.models import (
    BenchmarkResult,
)


def _report():
    result = BenchmarkResult(
        total_samples=2,
        retrieval={
            "hit_at_1": 1.0,
            "hit_at_3": 1.0,
            "hit_at_5": 1.0,
            "hit_at_10": 1.0,
            "recall_at_1": 0.4167,
            "recall_at_3": 1.0,
            "recall_at_5": 1.0,
            "recall_at_10": 1.0,
            "reciprocal_rank": 1.0,
            "ndcg_at_5": 0.9599,
            "ndcg_at_10": 0.9599,
        },
        answers={
            "grounding_score": 0.8335,
            "supported_ratio": 1.0,
            "unsupported_ratio": 0.0,
            "average_confidence": 0.69,
            "hallucination_risk": 0.215,
            "consistency_score": 0.0,
            "citation_coverage": 0.33,
            "grounded_ratio": 0.5,
            "repairable_ratio": 0.5,
        },
        runtime={
            "total_seconds": 11.948789,
            "average_seconds_per_sample": 5.974395,
            "samples_per_second": 0.1674,
        },
    )

    return BenchmarkReport.from_result(result)


def test_report_contains_sections():

    reporter = BenchmarkConsoleReporter()

    output = reporter.render(_report())

    assert "RAG BENCHMARK REPORT" in output
    assert "RETRIEVAL" in output
    assert "ANSWERS" in output
    assert "RUNTIME" in output


def test_report_contains_metrics():

    reporter = BenchmarkConsoleReporter()

    output = reporter.render(_report())

    assert "Hit@1       : 1.0000" in output
    assert "Recall@3    : 1.0000" in output
    assert "MRR         : 1.0000" in output
    assert "nDCG@5      : 0.9599" in output

    assert "Grounding   : 0.8335" in output
    assert "Supported   : 1.0000" in output
    assert "Hallucination Risk : 0.2150" in output
    assert "Citation Coverage : 0.3300" in output


def test_report_contains_runtime():

    reporter = BenchmarkConsoleReporter()

    output = reporter.render(_report())

    assert "Total        : 11.9488 s" in output
    assert "Per Sample   : 5.9744 s" in output
    assert "Samples/sec  : 0.1674" in output


def test_report_handles_missing_metrics():

    reporter = BenchmarkConsoleReporter()

    report = BenchmarkReport(
        total_samples=0,
    )

    output = reporter.render(report)

    assert "Hit@1       : N/A" in output
    assert "Grounding   : N/A" in output
    assert "Total        : N/A s" in output


def test_report_requires_benchmark_report():

    reporter = BenchmarkConsoleReporter()

    with pytest.raises(
        TypeError,
        match="BenchmarkReport",
    ):
        reporter.render(object())