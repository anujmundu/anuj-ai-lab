from types import SimpleNamespace

import pytest

from app.rag.evaluation.models import (
    EvaluationSample,
)
from app.rag.evaluation.production_adapter import (
    ProductionRetrievalAdapter,
)


class FakePipeline:

    def __init__(self):
        self.calls = []

    def run(
        self,
        *,
        question,
        k,
        profiler=None,
    ):

        self.calls.append(
            {
                "question": question,
                "k": k,
                "profiler": profiler,
            }
        )

        return SimpleNamespace(
            documents=[
                "Python is a programming language.",
                "Python is widely used in data science.",
            ],
            metadatas=[
                {
                    "filename": "python_notes",
                    "chunk_id": "python_notes_chunk_002",
                    "chunk_number": 2,
                    "total_chunks": 9,
                },
                {
                    "filename": "python_notes",
                    "chunk_id": "python_notes_chunk_003",
                    "chunk_number": 3,
                    "total_chunks": 9,
                },
            ],
            retrieval=[
                {
                    "semantic_score": 0.91,
                    "keyword_score": 0.20,
                    "combined_score": 0.75,
                },
                {
                    "semantic_score": 0.80,
                    "keyword_score": 0.10,
                    "combined_score": 0.65,
                },
            ],
        )


def _sample():

    return EvaluationSample(
        sample_id="python_001",
        question="What is Python?",
    )


def test_adapter_rejects_invalid_pipeline():

    with pytest.raises(
        TypeError,
        match="pipeline must provide",
    ):
        ProductionRetrievalAdapter(
            pipeline=object()
        )


def test_adapter_rejects_invalid_sample():

    adapter = ProductionRetrievalAdapter(
        pipeline=FakePipeline()
    )

    with pytest.raises(
        TypeError,
        match="EvaluationSample",
    ):
        adapter.retrieve(
            "What is Python?"
        )


def test_adapter_rejects_invalid_k():

    adapter = ProductionRetrievalAdapter(
        pipeline=FakePipeline()
    )

    with pytest.raises(
        ValueError,
        match="greater than zero",
    ):
        adapter.retrieve(
            _sample(),
            k=0,
        )


def test_adapter_calls_production_pipeline():

    pipeline = FakePipeline()

    adapter = ProductionRetrievalAdapter(
        pipeline=pipeline
    )

    sample = _sample()

    results = adapter.retrieve(
        sample,
        k=5,
    )

    assert len(results) == 2

    assert pipeline.calls == [
        {
            "question": "What is Python?",
            "k": 5,
            "profiler": None,
        }
    ]


def test_adapter_builds_canonical_retrieval_results():

    adapter = ProductionRetrievalAdapter(
        pipeline=FakePipeline()
    )

    results = adapter.retrieve(
        _sample()
    )

    first = results[0]

    assert first.doc_id == (
        "python_notes_chunk_002"
    )

    assert first.filename == (
        "python_notes"
    )

    assert first.chunk_id == (
        "python_notes_chunk_002"
    )

    assert first.chunk_number == 2

    assert first.total_chunks == 9

    assert first.semantic_score == pytest.approx(
        0.91
    )

    assert first.keyword_score == pytest.approx(
        0.20
    )

    assert first.combined_score == pytest.approx(
        0.75
    )


def test_adapter_preserves_rank_order():

    adapter = ProductionRetrievalAdapter(
        pipeline=FakePipeline()
    )

    results = adapter.retrieve(
        _sample()
    )

    assert [
        result.chunk_id
        for result in results
    ] == [
        "python_notes_chunk_002",
        "python_notes_chunk_003",
    ]


def test_adapter_handles_missing_metadata():

    class MinimalPipeline:

        def run(
            self,
            *,
            question,
            k,
            profiler=None,
        ):

            return SimpleNamespace(
                documents=[
                    "Python."
                ],
                metadatas=[
                    {}
                ],
                retrieval=[
                    {}
                ],
            )

    adapter = ProductionRetrievalAdapter(
        pipeline=MinimalPipeline()
    )

    results = adapter.retrieve(
        _sample()
    )

    assert len(results) == 1

    assert results[0].chunk_id == (
        "retrieved_chunk_0"
    )

    assert results[0].semantic_score == 0.0

    assert results[0].combined_score == 0.0


def test_adapter_handles_missing_retrieval_entry():

    class Pipeline:

        def run(
            self,
            *,
            question,
            k,
            profiler=None,
        ):

            return SimpleNamespace(
                documents=[
                    "Python."
                ],
                metadatas=[
                    {
                        "filename": "notes",
                        "chunk_id": "notes_001",
                    }
                ],
                retrieval=[],
            )

    adapter = ProductionRetrievalAdapter(
        pipeline=Pipeline()
    )

    results = adapter.retrieve(
        _sample()
    )

    assert results[0].combined_score == 0.0


def test_adapter_accepts_profiler():

    pipeline = FakePipeline()

    adapter = ProductionRetrievalAdapter(
        pipeline=pipeline
    )

    profiler = object()

    adapter.retrieve(
        _sample(),
        profiler=profiler,
    )

    assert pipeline.calls[0]["profiler"] is profiler
