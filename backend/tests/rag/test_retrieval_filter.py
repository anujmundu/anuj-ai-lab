from app.rag.retrieval_filter import (
    RetrievalFilter,
)
from app.rag.retrieval_config import (
    RetrievalConfig,
)


def make_results(
    *,
    ids=None,
    documents=None,
    metadatas=None,
    distances=None,
    retrieval=None,
    embeddings=None,
):
    ids = ids or ["chunk-1"]
    documents = documents or ["machine learning fundamentals"]
    metadatas = metadatas or [
        {
            "filename": "research.pdf",
        }
    ]
    distances = distances or [0.1]
    retrieval = retrieval or [
        {
            "semantic_score": 0.9,
        }
    ]
    embeddings = embeddings or []

    return {
        "ids": [ids],
        "documents": [documents],
        "metadatas": [metadatas],
        "distances": [distances],
        "retrieval": [retrieval],
        "embeddings": [embeddings],
    }


def test_filter_keeps_valid_result():

    retrieval_filter = RetrievalFilter()

    results = make_results()

    filtered = retrieval_filter.apply(
        results,
        k=5,
    )

    assert filtered["ids"] == [
        ["chunk-1"]
    ]

    assert filtered["documents"] == [
        ["machine learning fundamentals"]
    ]

    assert filtered["metadatas"] == [
        [
            {
                "filename": "research.pdf",
            }
        ]
    ]


def test_filter_applies_top_k():

    retrieval_filter = RetrievalFilter()

    results = make_results(
        ids=[
            "chunk-1",
            "chunk-2",
            "chunk-3",
        ],
        documents=[
            "machine learning fundamentals",
            "deep learning fundamentals",
            "retrieval augmented generation",
        ],
        metadatas=[
            {"filename": "a.pdf"},
            {"filename": "b.pdf"},
            {"filename": "c.pdf"},
        ],
        distances=[
            0.1,
            0.2,
            0.3,
        ],
        retrieval=[
            {"semantic_score": 0.9},
            {"semantic_score": 0.8},
            {"semantic_score": 0.7},
        ],
    )

    filtered = retrieval_filter.apply(
        results,
        k=2,
    )

    assert filtered["ids"] == [
        [
            "chunk-1",
            "chunk-2",
        ]
    ]

    assert len(
        filtered["documents"][0]
    ) == 2


def test_filter_removes_low_semantic_score():

    config = RetrievalConfig(
        min_semantic_score=0.5,
    )

    retrieval_filter = RetrievalFilter(
        config=config,
    )

    results = make_results(
        ids=[
            "good",
            "bad",
        ],
        documents=[
            "good semantic result",
            "bad semantic result",
        ],
        metadatas=[
            {"filename": "good.pdf"},
            {"filename": "bad.pdf"},
        ],
        distances=[
            0.1,
            0.9,
        ],
        retrieval=[
            {"semantic_score": 0.9},
            {"semantic_score": 0.2},
        ],
    )

    filtered = retrieval_filter.apply(
        results,
        k=5,
    )

    assert filtered["ids"] == [
        ["good"]
    ]

    assert (
        filtered["diagnostics"][0]["status"]
        == "KEPT"
    )

    assert (
        filtered["diagnostics"][1]["reason"]
        == "LOW_SEMANTIC_SCORE"
    )


def test_filter_allows_keyword_results_without_semantic_threshold():

    config = RetrievalConfig(
        retrieval_strategy="keyword",
        min_semantic_score=0.9,
    )

    retrieval_filter = RetrievalFilter(
        config=config,
    )

    results = make_results(
        retrieval=[
            {
                "semantic_score": 0.1,
                "keyword_score": 0.8,
            }
        ]
    )

    filtered = retrieval_filter.apply(
        results,
        k=5,
    )

    assert filtered["ids"] == [
        ["chunk-1"]
    ]


def test_filter_removes_near_duplicate_documents():

    config = RetrievalConfig(
        remove_near_duplicates=True,
        duplicate_similarity_threshold=0.8,
    )

    retrieval_filter = RetrievalFilter(
        config=config,
    )

    results = make_results(
        ids=[
            "chunk-1",
            "chunk-2",
        ],
        documents=[
            "machine learning fundamentals and concepts",
            "machine learning fundamentals and concepts",
        ],
        metadatas=[
            {"filename": "a.pdf"},
            {"filename": "b.pdf"},
        ],
        distances=[
            0.1,
            0.2,
        ],
        retrieval=[
            {"semantic_score": 0.9},
            {"semantic_score": 0.8},
        ],
    )

    filtered = retrieval_filter.apply(
        results,
        k=5,
    )

    assert filtered["ids"] == [
        ["chunk-1"]
    ]

    assert (
        filtered["diagnostics"][1]["reason"]
        == "DUPLICATE"
    )


def test_filter_respects_max_chunks_per_document():

    config = RetrievalConfig(
        max_chunks_per_document=1,
    )

    retrieval_filter = RetrievalFilter(
        config=config,
    )

    results = make_results(
        ids=[
            "chunk-1",
            "chunk-2",
            "chunk-3",
        ],
        documents=[
            "first document chunk",
            "second document chunk",
            "third document chunk",
        ],
        metadatas=[
            {"filename": "research.pdf"},
            {"filename": "research.pdf"},
            {"filename": "other.pdf"},
        ],
        distances=[
            0.1,
            0.2,
            0.3,
        ],
        retrieval=[
            {"semantic_score": 0.9},
            {"semantic_score": 0.8},
            {"semantic_score": 0.7},
        ],
    )

    filtered = retrieval_filter.apply(
        results,
        k=5,
    )

    assert filtered["ids"] == [
        [
            "chunk-1",
            "chunk-3",
        ]
    ]

    assert (
        filtered["diagnostics"][1]["reason"]
        == "MAX_CHUNKS_PER_DOCUMENT"
    )


def test_filter_diversifies_documents():

    config = RetrievalConfig(
        diversify_documents=True,
        max_chunks_per_document=5,
    )

    retrieval_filter = RetrievalFilter(
        config=config,
    )

    results = make_results(
        ids=[
            "chunk-1",
            "chunk-2",
            "chunk-3",
        ],
        documents=[
            "first document chunk",
            "second document chunk",
            "third document chunk",
        ],
        metadatas=[
            {"filename": "research.pdf"},
            {"filename": "research.pdf"},
            {"filename": "other.pdf"},
        ],
        distances=[
            0.1,
            0.2,
            0.3,
        ],
        retrieval=[
            {"semantic_score": 0.9},
            {"semantic_score": 0.8},
            {"semantic_score": 0.7},
        ],
    )

    filtered = retrieval_filter.apply(
        results,
        k=5,
    )

    assert filtered["ids"] == [
        [
            "chunk-1",
            "chunk-3",
        ]
    ]

    assert (
        filtered["diagnostics"][1]["reason"]
        == "DOCUMENT_DIVERSIFICATION"
    )


def test_filter_preserves_embeddings():

    results = make_results(
        embeddings=[
            [0.1, 0.2, 0.3],
        ]
    )

    retrieval_filter = RetrievalFilter()

    filtered = retrieval_filter.apply(
        results,
        k=5,
    )

    assert filtered["embeddings"] == [
        [
            [0.1, 0.2, 0.3],
        ]
    ]


def test_filter_returns_diagnostics_for_kept_result():

    retrieval_filter = RetrievalFilter()

    results = make_results()

    filtered = retrieval_filter.apply(
        results,
        k=5,
    )

    assert len(
        filtered["diagnostics"]
    ) == 1

    diagnostic = filtered["diagnostics"][0]

    assert diagnostic["chunk_id"] == "chunk-1"
    assert diagnostic["filename"] == "research.pdf"
    assert diagnostic["status"] == "KEPT"
    assert diagnostic["reason"] == "KEPT"


def test_filter_handles_empty_results():

    retrieval_filter = RetrievalFilter()

    results = {
        "ids": [[]],
        "documents": [[]],
        "metadatas": [[]],
        "distances": [[]],
        "retrieval": [[]],
        "embeddings": [[]],
    }

    filtered = retrieval_filter.apply(
        results,
        k=5,
    )

    assert filtered["ids"] == [[]]
    assert filtered["documents"] == [[]]
    assert filtered["metadatas"] == [[]]
    assert filtered["distances"] == [[]]
    assert filtered["retrieval"] == [[]]
    assert filtered["embeddings"] == [[]]
    assert filtered["diagnostics"] == []