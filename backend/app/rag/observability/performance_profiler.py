from __future__ import annotations

from collections.abc import Generator
from collections import defaultdict
from collections.abc import Generator
from contextlib import contextmanager
from time import perf_counter
from typing import Any

from app.rag.performance_models import (
    PerformanceMetrics,
    PerformanceProfilingResult,
    PerformanceStage,
)


class PerformanceProfiler:
    """
    Profiles execution time of pipeline stages.

    Supports both:

        profiler.start(...)
        profiler.stop(...)

    and

        with profiler.measure(...):
            ...

    The profiler is intentionally unaware of the RAG pipeline.
    Its sole responsibility is measuring execution time.
    """

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        """
        Reset the profiler state.

        Allows the same profiler instance to be reused safely.
        """

        self._active_timers: defaultdict[str, list[float]] = defaultdict(list)

        self._completed_stages: list[PerformanceStage] = []

    def start(self, stage_name: str) -> None:
        """
        Start timing a pipeline stage.

        Parameters
        ----------
        stage_name:
            Logical stage name.
        """

        self._active_timers[stage_name].append(
            perf_counter()
        )

    def stop(
        self,
        stage_name: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> PerformanceStage:
        """
        Stop timing a pipeline stage.

        Parameters
        ----------
        stage_name:
            Stage previously started.

        metadata:
            Optional diagnostic metadata.

        Returns
        -------
        PerformanceStage
        """

        stack = self._active_timers[stage_name]

        if not stack:
            raise ValueError(
                f"Stage '{stage_name}' has not been started."
            )

        start_time = stack.pop()

        if not stack:
            del self._active_timers[stage_name]

        duration = perf_counter() - start_time

        stage = PerformanceStage(
            name=stage_name,
            duration_seconds=duration,
            metadata=metadata or {},
        )

        self._completed_stages.append(stage)

        return stage

    @contextmanager
    def measure(
        self,
        stage_name: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> Generator[None, None, None]:
        """
        Context manager for profiling a stage.

        Example
        -------

        with profiler.measure("vector_search"):
            vector_store.search(...)
        """

        self.start(stage_name)

        try:
            yield

        finally:
            self.stop(
                stage_name,
                metadata=metadata,
            )
            
    def _calculate_percentages(
        self,
        total_duration: float,
    ) -> None:
        """
        Calculate the percentage contribution of each stage.
        """

        if total_duration <= 0:
            return

        for stage in self._completed_stages:
            stage.percentage = (
                stage.duration_seconds
                / total_duration
            ) * 100.0
            
    def _build_metrics(
        self,
        total_duration: float,
        stage_count: int,
    ) -> PerformanceMetrics:
        """
        Build aggregated performance metrics.
        """

        slowest = max(
            self._completed_stages,
            key=lambda stage: stage.duration_seconds,
        )

        fastest = min(
            self._completed_stages,
            key=lambda stage: stage.duration_seconds,
        )

        return PerformanceMetrics(
            total_duration_seconds=total_duration,
            average_stage_duration_seconds=(
                total_duration / stage_count
            ),
            slowest_stage=slowest.name,
            fastest_stage=fastest.name,
            stage_count=stage_count,
        )

    def build_result(
        self,
    ) -> PerformanceProfilingResult:
        """
        Build the final profiling result.

        Computes:

        - stage percentages
        - total duration
        - average duration
        - slowest stage
        - fastest stage
        """

        if not self._completed_stages:
            return PerformanceProfilingResult()

        total_duration = sum(
            stage.duration_seconds
            for stage in self._completed_stages
        )
        
        stage_count = len(self._completed_stages)

        self._calculate_percentages(
            total_duration
        )

        metrics = self._build_metrics(
            total_duration,
            stage_count,
        )

        return PerformanceProfilingResult(
            metrics=metrics,
            stages=self._completed_stages.copy(),
        )