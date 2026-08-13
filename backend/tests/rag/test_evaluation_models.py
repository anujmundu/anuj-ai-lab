from app.rag.evaluation.models import (
    AnswerEvaluationResult,
    BenchmarkResult,
    EvaluationSample,
    RelevantChunk,
    RetrievalEvaluationResult,
)


def test_relevant_chunk_defaults():
    chunk = RelevantChunk(
        filename="paper.pdf",
        chunk_id="paper_chunk_10",
    )

    assert chunk.filename == "paper.pdf"
    assert chunk.chunk_id == "paper_chunk_10"
    assert chunk.chunk_number == 0


def test_evaluation_sample():
    sample = EvaluationSample(
        sample_id="qa_001",
        question="What is Python?",
        relevant_chunks=(
            RelevantChunk(
                filename="python.pdf",
                chunk_id="python_chunk_10",
                chunk_number=10,
            ),
        ),
        reference_answer="Python is a programming language.",
    )

    assert sample.sample_id == "qa_001"
    assert sample.question == "What is Python?"
    assert len(sample.relevant_chunks) == 1
    assert sample.relevant_chunks[0].chunk_id == "python_chunk_10"


def test_retrieval_evaluation_result_defaults():
    result = RetrievalEvaluationResult(
        sample_id="qa_001",
    )

    assert result.sample_id == "qa_001"
    assert result.hit_at_1 == 0.0
    assert result.reciprocal_rank == 0.0
    assert result.ndcg_at_10 == 0.0


def test_answer_evaluation_result_supports_unavailable_hallucination_risk():
    result = AnswerEvaluationResult(
        sample_id="qa_001",
        hallucination_risk=None,
        grounding_decision="reject",
    )

    assert result.hallucination_risk is None
    assert result.grounding_decision == "reject"


def test_benchmark_result_defaults():
    result = BenchmarkResult(
        total_samples=10,
    )

    assert result.total_samples == 10
    assert result.retrieval == {}
    assert result.answers == {}
    assert result.runtime == {}