from types import SimpleNamespace

import pytest

from app.rag.evaluation.models import (
    EvaluationSample,
)
from app.rag.evaluation.production_adapter import (
    ProductionRetrievalAdapter,
)
from app.rag.evaluation.production_benchmark_executor import (
    ProductionBenchmarkExecutor,
)


class FakeRetrievalAdapter:

    def retrieve(
        self,
        sample,
        *,
        k,
        profiler=None,
    ):

        return [
            SimpleNamespace(
                document="Python is a programming language.",
                filename="python_notes",
                chunk_id="python_001",
                chunk_number=1,
                total_chunks=5,
                source="",
                semantic_score=0.9,
                keyword_score=0.2,
                combined_score=0.8,
            )
        ]


class FakeContextPipeline:

    def run(
        self,
        *,
        documents,
        metadatas,
    ):

        return SimpleNamespace(
            context="Python is a programming language."
        )


class FakePromptPipeline:

    def run(
        self,
        *,
        question,
        context,
        conversation,
        memory,
    ):

        return (
            SimpleNamespace(
                prompt="Explain Python.",
                quality={
                    "balanced": True,
                },
            ),
            0.01,
        )


class FakeGenerationPipeline:

    def run(
        self,
        *,
        prompt,
        profiler=None,
    ):

        return SimpleNamespace(
            raw_answer=(
                "Python is a programming language."
            )
        )


class FakePostProcessingPipeline:

    def run(
        self,
        *,
        raw_answer,
        context,
        sources,
        documents,
        metadatas,
        profiler=None,
    ):

        return SimpleNamespace(
            answer=raw_answer,
            confidence=0.95,
            alignment={},
            grounding={
                "metrics": {
                    "evidence": {
                        "grounding_score": 0.9,
                        "supported_ratio": 1.0,
                        "unsupported_ratio": 0.0,
                        "average_confidence": 0.95,
                    }
                }
            },
            hallucination={
                "hallucination_risk": 0.05,
            },
            consistency={
                "consistency_score": 0.95,
            },
            answer_quality={
                "compression_ratio": 0.8,
            },
            citation_result={
                "coverage": {
                    "coverage": 0.9,
                }
            },
        )


def _sample():

    return EvaluationSample(
        sample_id="python_001",
        question="What is Python?",
    )


def _executor():

    return ProductionBenchmarkExecutor(
        retrieval_adapter=FakeRetrievalAdapter(),
        context_pipeline_instance=FakeContextPipeline(),
        prompt_pipeline_instance=FakePromptPipeline(),
        generation_pipeline_instance=FakeGenerationPipeline(),
        post_processing_pipeline_instance=(
            FakePostProcessingPipeline()
        ),
    )


def test_executor_runs_production_flow():

    result = _executor().execute(
        _sample()
    )

    assert result["answer"] == (
        "Python is a programming language."
    )

    assert result["confidence"] == 0.95

    assert len(
        result["retrieval"]
    ) == 1

    assert result["hallucination"][
        "hallucination_risk"
    ] == 0.05

    assert result["citations"][
        "coverage"
    ]["coverage"] == 0.9


def test_executor_preserves_retrieval_results():

    result = _executor().execute(
        _sample()
    )

    retrieval = result["retrieval"][0]

    assert retrieval.chunk_id == (
        "python_001"
    )

    assert retrieval.semantic_score == 0.9


def test_executor_passes_retrieval_to_context():

    executor = _executor()

    result = executor.execute(
        _sample()
    )

    assert result["context"] == (
        "Python is a programming language."
    )


def test_executor_rejects_invalid_sample():

    with pytest.raises(
        TypeError,
        match="EvaluationSample",
    ):
        _executor().execute(
            "What is Python?"
        )


def test_executor_rejects_invalid_k():

    with pytest.raises(
        ValueError,
        match="greater than zero",
    ):
        _executor().execute(
            _sample(),
            k=0,
        )


def test_executor_returns_prompt_quality():

    result = _executor().execute(
        _sample()
    )

    assert result["prompt_quality"] == {
        "balanced": True,
    }
