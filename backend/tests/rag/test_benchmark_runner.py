from app.rag.evaluation.benchmark_runner import (
    BenchmarkRunner,
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


def make_result(
    filename: str,
    chunk_id: str,
) -> RetrievalResult:

    return RetrievalResult(
        doc_id=chunk_id,

        document=(
            "Python is a programming language."
        ),

        metadata=RetrievalMetadata(
            filename=filename,
            chunk_id=chunk_id,
            chunk_number=1,
            total_chunks=10,
        ),

        scores=RetrievalScores(
            semantic_score=0.9,
            keyword_score=0.8,
            combined_score=0.85,
        ),
    )


def make_sample(
    sample_id: str = "sample_001",
) -> EvaluationSample:

    return EvaluationSample(
        sample_id=sample_id,

        question="What is Python?",

        relevant_chunks=(
            RelevantChunk(
                filename="python.pdf",
                chunk_id="python_chunk_001",
                chunk_number=1,
            ),
        ),

        reference_answer=(
            "Python is a programming language."
        ),
    )


def test_runner_requires_callable():

    try:
        BenchmarkRunner(None)
    except TypeError:
        return

    raise AssertionError(
        "BenchmarkRunner should reject non-callable executors"
    )


def test_runner_evaluates_samples():

    sample = make_sample()

    def executor(
        current_sample,
    ):

        assert current_sample == sample

        return [
            make_result(
                "python.pdf",
                "python_chunk_001",
            ),
        ]

    runner = BenchmarkRunner(
        executor
    )

    result = runner.run(
        [sample]
    )

    assert result.total_samples == 1

    assert (
        result.metadata[
            "evaluation_type"
        ]
        == "retrieval"
    )

    assert (
        result.retrieval[
            "hit_at_1"
        ]
        == 1.0
    )

    assert (
        result.retrieval[
            "reciprocal_rank"
        ]
        == 1.0
    )


def test_runner_aggregates_multiple_samples():

    sample_1 = make_sample(
        "sample_001"
    )

    sample_2 = make_sample(
        "sample_002"
    )

    def executor(
        sample,
    ):

        if sample.sample_id == "sample_001":

            return [
                make_result(
                    "python.pdf",
                    "python_chunk_001",
                ),
            ]

        return [
            make_result(
                "other.pdf",
                "other_chunk_001",
            ),
        ]

    runner = BenchmarkRunner(
        executor
    )

    result = runner.run(
        [
            sample_1,
            sample_2,
        ]
    )

    assert result.total_samples == 2

    assert (
        result.retrieval[
            "hit_at_1"
        ]
        == 0.5
    )

    assert (
        result.retrieval[
            "reciprocal_rank"
        ]
        == 0.5
    )


def test_runner_handles_empty_dataset():

    runner = BenchmarkRunner(
        lambda sample: []
    )

    result = runner.run([])

    assert result.total_samples == 0

    assert result.retrieval == {}

    assert result.answers == {}

    assert (
        result.metadata[
            "evaluation_type"
        ]
        == "retrieval"
    )

    assert (
        result.runtime[
            "total_seconds"
        ]
        >= 0.0
    )


def test_runner_accepts_iterable():

    sample = make_sample()

    def executor(
        current_sample,
    ):

        return [
            make_result(
                "python.pdf",
                "python_chunk_001",
            ),
        ]

    runner = BenchmarkRunner(
        executor
    )

    def samples():

        yield sample

    result = runner.run(
        samples()
    )

    assert result.total_samples == 1

    assert (
        result.retrieval[
            "hit_at_1"
        ]
        == 1.0
    )


def test_runner_reports_runtime():

    sample = make_sample()

    runner = BenchmarkRunner(
        lambda current_sample: [
            make_result(
                "python.pdf",
                "python_chunk_001",
            )
        ]
    )

    result = runner.run(
        [sample]
    )

    assert (
        result.runtime[
            "total_seconds"
        ]
        >= 0.0
    )

    assert (
        result.runtime[
            "samples_per_second"
        ]
        >= 0.0
    )