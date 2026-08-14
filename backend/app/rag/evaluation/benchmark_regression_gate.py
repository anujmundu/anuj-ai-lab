from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.rag.evaluation.benchmark_comparator import (
    BenchmarkComparison,
)


@dataclass(slots=True, frozen=True)
class RegressionGateResult:
    """
    Decision produced from a benchmark comparison.

    The gate does not execute benchmarks and does not
    calculate metric deltas. It only applies regression
    policy to an existing BenchmarkComparison.
    """

    passed: bool

    regressed_metrics: tuple[str, ...] = ()

    critical_regressions: tuple[str, ...] = ()

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


class BenchmarkRegressionGate:
    """
    Applies a regression policy to a BenchmarkComparison.

    The comparator answers:
        What changed?

    The regression gate answers:
        Is the change acceptable?

    By default, any regression in a critical metric
    causes the gate to fail.
    """

    DEFAULT_CRITICAL_METRICS = frozenset(
        {
            "hit_at_1",
            "grounding_score",
            "hallucination_risk",
            "citation_coverage",
        }
    )

    def __init__(
        self,
        *,
        critical_metrics: set[str] | frozenset[str] | None = None,
    ) -> None:

        self.critical_metrics = frozenset(
            critical_metrics
            if critical_metrics is not None
            else self.DEFAULT_CRITICAL_METRICS
        )

    def evaluate(
        self,
        comparison: BenchmarkComparison,
    ) -> RegressionGateResult:

        if not isinstance(
            comparison,
            BenchmarkComparison,
        ):
            raise TypeError(
                "comparison must be a BenchmarkComparison"
            )

        regressed_metrics = tuple(
            metric.metric
            for metric in comparison.metrics
            if metric.regressed
        )

        critical_regressions = tuple(
            metric
            for metric in regressed_metrics
            if metric in self.critical_metrics
        )

        passed = not critical_regressions

        return RegressionGateResult(
            passed=passed,
            regressed_metrics=regressed_metrics,
            critical_regressions=critical_regressions,
            metadata={
                "critical_metrics": tuple(
                    sorted(self.critical_metrics)
                ),
                "total_regressions": len(
                    regressed_metrics
                ),
                "critical_regression_count": len(
                    critical_regressions
                ),
            },
        )


benchmark_regression_gate = BenchmarkRegressionGate()