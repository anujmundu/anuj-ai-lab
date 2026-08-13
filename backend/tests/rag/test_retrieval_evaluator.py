from app.rag.evaluation.models import (
    EvaluationSample,
    RelevantChunk,
)
from app.rag.evaluation.retrieval_evaluator import (
    RetrievalEvaluator,
)
from app.rag.retrieval_models import (
    RetrievalMetadata,
    RetrievalResult,
    RetrievalScores,
)


def make_result(
    filename: str,
    chunk_id: str,
    chunk_number: int = 0,
) -> RetrievalResult:
    return RetrievalResult(
        doc_id=chunk_id,
        document=f"content for {chunk_id}",
        metadata=RetrievalMetadata(
            filename=filename,
            chunk_id=chunk_id,
            chunk_number=chunk_number,
            total_chunks=20,
        ),
        scores=RetrievalScores(
            semantic_score=0.9,
            keyword_score=0.8,
            combined_score=0.85,
        ),
    )


def make_sample(
    relevant_chunks: tuple[RelevantChunk, ...],
) -> EvaluationSample:
    return EvaluationSample(
        sample_id="qa_001",
        question="What is Python?",
        relevant_chunks=relevant_chunks,
    )


def test_hit_at_k_and_recall():
    evaluator = RetrievalEvaluator()

    sample = make_sample(
        (
            RelevantChunk(
                filename="python.pdf",
                chunk_id="python_chunk_3",
                chunk_number=3,
            ),
        )
    )

    results = [
        make_result(
            "other.pdf",
            "other_chunk_1",
        ),
        make_result(
            "python.pdf",
            "python_chunk_3",
            3,
        ),
    ]

    result = evaluator.evaluate(
        sample=sample,
        results=results,
    )

    assert result.hit_at_1 == 0
    assert result.hit_at_3 == 1

    assert result.recall_at_1 == 0.0
    assert result.recall_at_3 == 1.0


def test_precision_at_k():
    evaluator = RetrievalEvaluator()

    sample = make_sample(
        (
            RelevantChunk(
                filename="python.pdf",
                chunk_id="python_chunk_1",
            ),
            RelevantChunk(
                filename="python.pdf",
                chunk_id="python_chunk_2",
            ),
        )
    )

    results = [
        make_result(
            "python.pdf",
            "python_chunk_1",
        ),
        make_result(
            "other.pdf",
            "other_chunk_1",
        ),
        make_result(
            "python.pdf",
            "python_chunk_2",
        ),
    ]

    result = evaluator.evaluate(
        sample=sample,
        results=results,
    )

    assert result.precision_at_1 == 1.0
    assert result.precision_at_3 == 2 / 3


def test_reciprocal_rank():
    evaluator = RetrievalEvaluator()

    sample = make_sample(
        (
            RelevantChunk(
                filename="python.pdf",
                chunk_id="python_chunk_3",
            ),
        )
    )

    results = [
        make_result(
            "other.pdf",
            "other_chunk_1",
        ),
        make_result(
            "other.pdf",
            "other_chunk_2",
        ),
        make_result(
            "python.pdf",
            "python_chunk_3",
        ),
    ]

    result = evaluator.evaluate(
        sample=sample,
        results=results,
    )

    assert result.reciprocal_rank == 1 / 3


def test_ndcg_perfect_ranking():
    evaluator = RetrievalEvaluator()

    sample = make_sample(
        (
            RelevantChunk(
                filename="python.pdf",
                chunk_id="python_chunk_1",
            ),
            RelevantChunk(
                filename="python.pdf",
                chunk_id="python_chunk_2",
            ),
        )
    )

    results = [
        make_result(
            "python.pdf",
            "python_chunk_1",
        ),
        make_result(
            "python.pdf",
            "python_chunk_2",
        ),
    ]

    result = evaluator.evaluate(
        sample=sample,
        results=results,
    )

    assert result.ndcg_at_5 == 1.0
    assert result.ndcg_at_10 == 1.0


def test_no_relevant_results():
    evaluator = RetrievalEvaluator()

    sample = make_sample(
        (
            RelevantChunk(
                filename="python.pdf",
                chunk_id="python_chunk_1",
            ),
        )
    )

    results = [
        make_result(
            "other.pdf",
            "other_chunk_1",
        ),
        make_result(
            "other.pdf",
            "other_chunk_2",
        ),
    ]

    result = evaluator.evaluate(
        sample=sample,
        results=results,
    )

    assert result.hit_at_1 == 0
    assert result.hit_at_10 == 0
    assert result.reciprocal_rank == 0.0
    assert result.ndcg_at_5 == 0.0


def test_empty_results():
    evaluator = RetrievalEvaluator()

    sample = make_sample(
        (
            RelevantChunk(
                filename="python.pdf",
                chunk_id="python_chunk_1",
            ),
        )
    )

    result = evaluator.evaluate(
        sample=sample,
        results=[],
    )

    assert result.hit_at_1 == 0
    assert result.precision_at_5 == 0.0
    assert result.recall_at_10 == 0.0
    assert result.reciprocal_rank == 0.0