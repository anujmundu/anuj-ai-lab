from unittest.mock import Mock

from app.rag.multi_query_retriever import MultiQueryRetriever
from app.rag.query.models import QueryAnalysisResult


def make_analysis() -> QueryAnalysisResult:
    """
    Minimal QueryAnalysisResult suitable for MultiQueryRetriever tests.

    The retriever passes this object to QueryGenerator, but the mocked
    QueryGenerator does not depend on its internal values.
    """

    return Mock(spec=QueryAnalysisResult)


def make_result(
    *,
    ids,
    documents,
    metadatas,
    distances,
    retrieval,
    embeddings=None,
):
    if embeddings is None:
        embeddings = [None] * len(ids)

    return {
        "ids": [ids],
        "documents": [documents],
        "metadatas": [metadatas],
        "distances": [distances],
        "embeddings": [embeddings],
        "retrieval": [retrieval],
    }


def make_metadata(
    filename: str,
    chunk_id: str,
    chunk_number: int = 1,
    total_chunks: int = 1,
):
    return {
        "filename": filename,
        "chunk_id": chunk_id,
        "chunk_number": chunk_number,
        "total_chunks": total_chunks,
    }


def make_retrieval(
    *,
    semantic_score: float,
    keyword_score: float,
    combined_score: float,
):
    return {
        "semantic_score": semantic_score,
        "keyword_score": keyword_score,
        "combined_score": combined_score,
        "semantic_rank": 1,
        "keyword_rank": 1,
    }


def test_multi_query_retriever_returns_generated_queries(monkeypatch):
    retriever = MultiQueryRetriever()

    generated_queries = [
        "python",
        "python overview",
        "python fundamentals",
    ]

    monkeypatch.setattr(
        "app.rag.multi_query_retriever.query_generator.generate",
        lambda **kwargs: generated_queries,
    )

    monkeypatch.setattr(
        "app.rag.multi_query_retriever.hybrid_retriever.retrieve",
        lambda **kwargs: make_result(
            ids=["doc-1"],
            documents=["Python is a programming language."],
            metadatas=[
                make_metadata(
                    "python.txt",
                    "chunk-1",
                )
            ],
            distances=[0.1],
            retrieval=[
                make_retrieval(
                    semantic_score=0.9,
                    keyword_score=0.8,
                    combined_score=0.85,
                )
            ],
        ),
    )

    result = retriever.retrieve(
        query="python",
        k=3,
        analysis=make_analysis(),
    )

    assert result["pipeline"]["strategy"] == "multi_query"
    assert result["pipeline"]["generated_queries"] == generated_queries
    assert result["pipeline"]["query_count"] == 3


def test_multi_query_retriever_deduplicates_documents(monkeypatch):
    retriever = MultiQueryRetriever()

    monkeypatch.setattr(
        "app.rag.multi_query_retriever.query_generator.generate",
        lambda **kwargs: [
            "python",
            "python overview",
        ],
    )

    def retrieve(**kwargs):
        query = kwargs["query"]

        if query == "python":
            return make_result(
                ids=["doc-1", "doc-2"],
                documents=[
                    "Python programming.",
                    "Python variables.",
                ],
                metadatas=[
                    make_metadata(
                        "python.txt",
                        "chunk-1",
                    ),
                    make_metadata(
                        "python.txt",
                        "chunk-2",
                    ),
                ],
                distances=[0.1, 0.2],
                retrieval=[
                    make_retrieval(
                        semantic_score=0.9,
                        keyword_score=0.8,
                        combined_score=0.85,
                    ),
                    make_retrieval(
                        semantic_score=0.7,
                        keyword_score=0.6,
                        combined_score=0.65,
                    ),
                ],
            )

        return make_result(
            ids=["doc-1", "doc-3"],
            documents=[
                "Python programming.",
                "Python functions.",
            ],
            metadatas=[
                make_metadata(
                    "python.txt",
                    "chunk-1",
                ),
                make_metadata(
                    "python.txt",
                    "chunk-3",
                ),
            ],
            distances=[0.1, 0.3],
            retrieval=[
                make_retrieval(
                    semantic_score=0.8,
                    keyword_score=0.7,
                    combined_score=0.75,
                ),
                make_retrieval(
                    semantic_score=0.6,
                    keyword_score=0.5,
                    combined_score=0.55,
                ),
            ],
        )

    monkeypatch.setattr(
        "app.rag.multi_query_retriever.hybrid_retriever.retrieve",
        retrieve,
    )

    result = retriever.retrieve(
        query="python",
        k=10,
        analysis=make_analysis(),
    )

    assert result["pipeline"]["unique_documents"] == 3
    assert len(result["ids"][0]) == 3
    assert len(set(result["ids"][0])) == 3


def test_cross_query_score_is_accumulated(monkeypatch):
    retriever = MultiQueryRetriever()

    monkeypatch.setattr(
        "app.rag.multi_query_retriever.query_generator.generate",
        lambda **kwargs: [
            "query one",
            "query two",
        ],
    )

    def retrieve(**kwargs):
        query = kwargs["query"]

        score = (
            0.80
            if query == "query one"
            else 0.70
        )

        return make_result(
            ids=["doc-1"],
            documents=["Shared evidence."],
            metadatas=[
                make_metadata(
                    "evidence.txt",
                    "chunk-1",
                )
            ],
            distances=[0.1],
            retrieval=[
                make_retrieval(
                    semantic_score=score,
                    keyword_score=score,
                    combined_score=score,
                )
            ],
        )

    monkeypatch.setattr(
        "app.rag.multi_query_retriever.hybrid_retriever.retrieve",
        retrieve,
    )

    result = retriever.retrieve(
        query="test",
        k=5,
        analysis=make_analysis(),
    )

    retrieval = result["retrieval"][0][0]

    assert retrieval["combined_score"] == 1.5
    assert retrieval["query_hits"] == 2


def test_cross_query_semantic_and_keyword_scores_use_maximum(
    monkeypatch,
):
    retriever = MultiQueryRetriever()

    monkeypatch.setattr(
        "app.rag.multi_query_retriever.query_generator.generate",
        lambda **kwargs: [
            "query one",
            "query two",
        ],
    )

    def retrieve(**kwargs):
        query = kwargs["query"]

        if query == "query one":
            semantic = 0.60
            keyword = 0.90
            combined = 0.70
        else:
            semantic = 0.95
            keyword = 0.50
            combined = 0.80

        return make_result(
            ids=["doc-1"],
            documents=["Shared evidence."],
            metadatas=[
                make_metadata(
                    "evidence.txt",
                    "chunk-1",
                )
            ],
            distances=[0.1],
            retrieval=[
                make_retrieval(
                    semantic_score=semantic,
                    keyword_score=keyword,
                    combined_score=combined,
                )
            ],
        )

    monkeypatch.setattr(
        "app.rag.multi_query_retriever.hybrid_retriever.retrieve",
        retrieve,
    )

    result = retriever.retrieve(
        query="test",
        k=5,
        analysis=make_analysis(),
    )

    retrieval = result["retrieval"][0][0]

    assert retrieval["semantic_score"] == 0.95
    assert retrieval["keyword_score"] == 0.90
    assert retrieval["combined_score"] == 1.50
    assert retrieval["query_hits"] == 2


def test_multi_query_retriever_respects_k(monkeypatch):
    retriever = MultiQueryRetriever()

    monkeypatch.setattr(
        "app.rag.multi_query_retriever.query_generator.generate",
        lambda **kwargs: [
            "query",
        ],
    )

    monkeypatch.setattr(
        "app.rag.multi_query_retriever.hybrid_retriever.retrieve",
        lambda **kwargs: make_result(
            ids=[
                "doc-1",
                "doc-2",
                "doc-3",
                "doc-4",
                "doc-5",
            ],
            documents=[
                "Document 1",
                "Document 2",
                "Document 3",
                "Document 4",
                "Document 5",
            ],
            metadatas=[
                make_metadata(
                    "test.txt",
                    f"chunk-{i}",
                    chunk_number=i,
                    total_chunks=5,
                )
                for i in range(1, 6)
            ],
            distances=[
                0.1,
                0.2,
                0.3,
                0.4,
                0.5,
            ],
            retrieval=[
                make_retrieval(
                    semantic_score=0.9 - (i * 0.1),
                    keyword_score=0.9 - (i * 0.1),
                    combined_score=0.9 - (i * 0.1),
                )
                for i in range(5)
            ],
        ),
    )

    result = retriever.retrieve(
        query="test",
        k=2,
        analysis=make_analysis(),
    )

    assert len(result["ids"][0]) == 2
    assert len(result["documents"][0]) == 2
    assert len(result["metadatas"][0]) == 2
    assert len(result["retrieval"][0]) == 2


def test_empty_generated_queries_return_empty_result(monkeypatch):
    retriever = MultiQueryRetriever()

    monkeypatch.setattr(
        "app.rag.multi_query_retriever.query_generator.generate",
        lambda **kwargs: [],
    )

    result = retriever.retrieve(
        query="",
        k=5,
        analysis=make_analysis(),
    )

    assert result["ids"] == [[]]
    assert result["documents"] == [[]]
    assert result["metadatas"] == [[]]
    assert result["distances"] == [[]]
    assert result["embeddings"] == [[]]
    assert result["retrieval"] == [[]]

    assert result["pipeline"]["strategy"] == "multi_query"
    assert result["pipeline"]["generated_queries"] == []
    assert result["pipeline"]["query_count"] == 0
    assert result["pipeline"]["unique_documents"] == 0