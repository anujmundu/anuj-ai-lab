from app.rag.evaluation.benchmark_service import (
    BenchmarkService,
)
from app.rag.evaluation.models import (
    EvaluationSample,
    RelevantChunk,
)
from app.rag.retrieval_models import (
    RetrievalMetadata,
    RetrievalResult,
    RetrievalScores,
)


def _sample():
    return EvaluationSample(
        sample_id="qa_001",
        question="What is Python?",
        relevant_chunks=(
            RelevantChunk(
                filename="python_notes",
                chunk_id="python_notes_chunk_001",
                chunk_number=1,
            ),
        ),
    )


def _retrieval():
    return RetrievalResult(
        doc_id="python_notes_chunk_001",
        document="Python is a programming language.",
        metadata=RetrievalMetadata(
            filename="python_notes",
            chunk_id="python_notes_chunk_001",
            chunk_number=1,
            total_chunks=5,
        ),
        scores=RetrievalScores(
            semantic_score=0.95,
            keyword_score=0.90,
            combined_score=0.93,
        ),
    )


def _executor(_sample):
    return {
        "retrieval": [_retrieval()],
        "grounding": {
            "metrics": {
                "evidence": {
                    "grounding_score": 0.9,
                    "supported_ratio": 1.0,
                    "unsupported_ratio": 0.0,
                    "average_confidence": 0.95,
                }
            }
        },
        "hallucination": {
            "hallucination_risk": 0.05,
        },
        "citations": {
            "coverage": {
                "coverage": 0.9,
            }
        },
    }


def test_benchmark_service_runs_full_evaluation():

    service = BenchmarkService(
        executor=_executor,
    )

    result = service.run(
        [_sample()]
    )

    assert result.total_samples == 1

    assert result.retrieval["hit_at_1"] == 1.0
    assert result.retrieval["recall_at_1"] == 1.0

    assert result.answers["grounding_score"] == 0.9
    assert result.answers["supported_ratio"] == 1.0
    assert result.answers["hallucination_risk"] == 0.05
    assert result.answers["citation_coverage"] == 0.9


def test_benchmark_service_handles_empty_dataset():

    service = BenchmarkService(
        executor=_executor,
    )

    result = service.run([])

    assert result.total_samples == 0
    assert result.retrieval == {}
    assert result.answers == {}
    assert result.runtime["samples_per_second"] == 0.0


def test_benchmark_service_preserves_multiple_samples():

    samples = [
        _sample(),
        EvaluationSample(
            sample_id="qa_002",
            question="What is a variable?",
            relevant_chunks=(),
        ),
    ]

    service = BenchmarkService(
        executor=_executor,
    )

    result = service.run(samples)

    assert result.total_samples == 2
    assert result.metadata["evaluation_type"] == "full_rag"
    assert result.metadata["retrieval_samples"] == 2
    assert result.metadata["answer_samples"] == 2


def test_benchmark_service_requires_callable():

    try:
        BenchmarkService(
            executor=None,
        )
    except TypeError:
        return

    raise AssertionError(
        "Expected TypeError"
    )


def test_benchmark_service_handles_missing_verification_data():

    def executor(_sample):
        return {
            "retrieval": [_retrieval()],
        }

    service = BenchmarkService(
        executor=executor,
    )

    result = service.run(
        [_sample()]
    )

    assert result.total_samples == 1
    assert result.answers["grounding_score"] == 0.0
    assert result.answers["supported_ratio"] == 0.0
    assert result.answers["hallucination_risk"] == 0.0
    assert result.answers["citation_coverage"] == 0.0