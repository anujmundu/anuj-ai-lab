from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.rag.evaluation.benchmark_report import BenchmarkReport


@dataclass(slots=True, frozen=True)
class MetricComparison:
    """
    Comparison of one benchmark metric against a baseline.
    """

    metric: str
    baseline: float
    current: float
    delta: float
    direction: str
    improved: bool
    regressed: bool


@dataclass(slots=True, frozen=True)
class BenchmarkComparison:
    """
    Aggregate comparison between a baseline and current report.
    """

    improved: int = 0
    regressed: int = 0
    unchanged: int = 0

    metrics: tuple[MetricComparison, ...] = ()

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


class BenchmarkComparator:
    """
    Compares benchmark reports without executing the RAG system.

    Higher-is-better metrics:
        retrieval quality
        answer grounding
        supported ratio
        consistency
        citation coverage

    Lower-is-better metrics:
        hallucination risk
        runtime
    """

    HIGHER_IS_BETTER = frozenset(
        {
            "hit_at_1",
            "hit_at_3",
            "hit_at_5",
            "hit_at_10",
            "precision_at_1",
            "precision_at_3",
            "precision_at_5",
            "precision_at_10",
            "recall_at_1",
            "recall_at_3",
            "recall_at_5",
            "recall_at_10",
            "reciprocal_rank",
            "ndcg_at_5",
            "ndcg_at_10",
            "grounding_score",
            "supported_ratio",
            "average_confidence",
            "consistency_score",
            "citation_coverage",
            "grounded_ratio",
            "repairable_ratio",
        }
    )

    LOWER_IS_BETTER = frozenset(
        {
            "unsupported_ratio",
            "hallucination_risk",
            "total_seconds",
            "average_seconds_per_sample",
        }
    )

    def __init__(
        self,
        *,
        tolerance: float = 0.0,
    ) -> None:

        if tolerance < 0:
            raise ValueError(
                "tolerance must be greater than or equal to zero"
            )

        self.tolerance = float(tolerance)

    @staticmethod
    def _numeric(
        value: object,
    ) -> float | None:

        if isinstance(value, bool):
            return None

        if isinstance(value, (int, float)):
            return float(value)

        return None

    def _compare_metric(
        self,
        *,
        metric: str,
        baseline: float,
        current: float,
    ) -> MetricComparison:

        delta = current - baseline

        if abs(delta) <= self.tolerance:
            improved = False
            regressed = False

        elif metric in self.HIGHER_IS_BETTER:
            improved = delta > 0
            regressed = delta < 0

        elif metric in self.LOWER_IS_BETTER:
            improved = delta < 0
            regressed = delta > 0

        else:
            raise ValueError(
                f"Unknown metric direction: {metric}"
            )

        if metric in self.HIGHER_IS_BETTER:
            direction = "higher_is_better"
        else:
            direction = "lower_is_better"

        return MetricComparison(
            metric=metric,
            baseline=baseline,
            current=current,
            delta=delta,
            direction=direction,
            improved=improved,
            regressed=regressed,
        )

    def compare(
        self,
        baseline: BenchmarkReport,
        current: BenchmarkReport,
    ) -> BenchmarkComparison:

        if not isinstance(
            baseline,
            BenchmarkReport,
        ):
            raise TypeError(
                "baseline must be a BenchmarkReport"
            )

        if not isinstance(
            current,
            BenchmarkReport,
        ):
            raise TypeError(
                "current must be a BenchmarkReport"
            )

        comparisons: list[MetricComparison] = []

        sections = (
            baseline.retrieval,
            baseline.answers,
            baseline.runtime,
        )

        current_sections = (
            current.retrieval,
            current.answers,
            current.runtime,
        )

        for baseline_section, current_section in zip(
            sections,
            current_sections,
        ):
            for metric, baseline_value in baseline_section.items():

                current_value = current_section.get(
                    metric
                )

                baseline_numeric = self._numeric(
                    baseline_value
                )
                current_numeric = self._numeric(
                    current_value
                )

                if (
                    baseline_numeric is None
                    or current_numeric is None
                ):
                    continue

                if (
                    metric not in self.HIGHER_IS_BETTER
                    and metric not in self.LOWER_IS_BETTER
                ):
                    continue

                comparisons.append(
                    self._compare_metric(
                        metric=metric,
                        baseline=baseline_numeric,
                        current=current_numeric,
                    )
                )

        improved = sum(
            comparison.improved
            for comparison in comparisons
        )

        regressed = sum(
            comparison.regressed
            for comparison in comparisons
        )

        unchanged = (
            len(comparisons)
            - improved
            - regressed
        )

        return BenchmarkComparison(
            improved=improved,
            regressed=regressed,
            unchanged=unchanged,
            metrics=tuple(comparisons),
            metadata={
                "tolerance": self.tolerance,
                "baseline_samples": baseline.total_samples,
                "current_samples": current.total_samples,
            },
        )


benchmark_comparator = BenchmarkComparator()