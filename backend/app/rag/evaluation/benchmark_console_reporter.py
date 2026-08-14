from __future__ import annotations

from app.rag.evaluation.benchmark_report import (
    BenchmarkReport,
)


class BenchmarkConsoleReporter:
    """
    Formats a BenchmarkReport as a deterministic,
    human-readable console report.

    This component only presents existing metrics.
    It does not calculate or modify benchmark results.
    """

    @staticmethod
    def _metric(
        value: object,
        digits: int = 4,
    ) -> str:
        if isinstance(value, bool):
            return str(value)

        if isinstance(value, (int, float)):
            return f"{float(value):.{digits}f}"

        return "N/A"

    def render(
        self,
        report: BenchmarkReport,
    ) -> str:
        if not isinstance(
            report,
            BenchmarkReport,
        ):
            raise TypeError(
                "report must be a BenchmarkReport"
            )

        retrieval = report.retrieval
        answers = report.answers
        runtime = report.runtime

        lines = [
            "========================================",
            "        RAG BENCHMARK REPORT",
            "========================================",
            "",
            f"Samples: {report.total_samples}",
            "",
            "RETRIEVAL",
            "----------------------------------------",
            (
                "Hit@1       : "
                f"{self._metric(retrieval.get('hit_at_1'))}"
            ),
            (
                "Hit@3       : "
                f"{self._metric(retrieval.get('hit_at_3'))}"
            ),
            (
                "Hit@5       : "
                f"{self._metric(retrieval.get('hit_at_5'))}"
            ),
            (
                "Hit@10      : "
                f"{self._metric(retrieval.get('hit_at_10'))}"
            ),
            (
                "Recall@1    : "
                f"{self._metric(retrieval.get('recall_at_1'))}"
            ),
            (
                "Recall@3    : "
                f"{self._metric(retrieval.get('recall_at_3'))}"
            ),
            (
                "Recall@5    : "
                f"{self._metric(retrieval.get('recall_at_5'))}"
            ),
            (
                "Recall@10   : "
                f"{self._metric(retrieval.get('recall_at_10'))}"
            ),
            (
                "MRR         : "
                f"{self._metric(retrieval.get('reciprocal_rank'))}"
            ),
            (
                "nDCG@5      : "
                f"{self._metric(retrieval.get('ndcg_at_5'))}"
            ),
            (
                "nDCG@10     : "
                f"{self._metric(retrieval.get('ndcg_at_10'))}"
            ),
            "",
            "ANSWERS",
            "----------------------------------------",
            (
                "Grounding   : "
                f"{self._metric(answers.get('grounding_score'))}"
            ),
            (
                "Supported   : "
                f"{self._metric(answers.get('supported_ratio'))}"
            ),
            (
                "Unsupported : "
                f"{self._metric(answers.get('unsupported_ratio'))}"
            ),
            (
                "Confidence  : "
                f"{self._metric(answers.get('average_confidence'))}"
            ),
            (
                "Hallucination Risk : "
                f"{self._metric(answers.get('hallucination_risk'))}"
            ),
            (
                "Consistency  : "
                f"{self._metric(answers.get('consistency_score'))}"
            ),
            (
                "Citation Coverage : "
                f"{self._metric(answers.get('citation_coverage'))}"
            ),
            (
                "Grounded Ratio : "
                f"{self._metric(answers.get('grounded_ratio'))}"
            ),
            (
                "Repairable Ratio : "
                f"{self._metric(answers.get('repairable_ratio'))}"
            ),
            "",
            "RUNTIME",
            "----------------------------------------",
            (
                "Total        : "
                f"{self._metric(runtime.get('total_seconds'))} s"
            ),
            (
                "Per Sample   : "
                f"{self._metric(runtime.get('average_seconds_per_sample'))} s"
            ),
            (
                "Samples/sec  : "
                f"{self._metric(runtime.get('samples_per_second'))}"
            ),
            "",
            "========================================",
        ]

        return "\n".join(lines)


benchmark_console_reporter = (
    BenchmarkConsoleReporter()
)