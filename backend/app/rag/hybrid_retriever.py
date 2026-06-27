from app.rag.retriever import retriever


class BaseRetriever:
    """
    Base interface for all retrieval engines.
    """

    def retrieve(
        self,
        query: str,
        k: int = 3
    ):
        raise NotImplementedError


class SemanticRetriever(BaseRetriever):
    """
    Semantic retrieval powered by ChromaDB embeddings.
    """

    def retrieve(
        self,
        query: str,
        k: int = 3
    ):

        return retriever.retrieve(
            query=query,
            k=k
        )


class KeywordRetriever(BaseRetriever):
    """
    Placeholder implementation.

    In the next commit this will be replaced with
    a BM25-backed keyword retriever.

    Keeping this interface now means future keyword
    search engines can be swapped without modifying
    the rest of the RAG pipeline.
    """

    def retrieve(
        self,
        query: str,
        k: int = 3
    ):

        return {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]]
        }


class HybridRetriever:
    """
    Combines multiple retrieval engines.

    Current:
        • Semantic Search

    Next commit:
        • Semantic Search
        • BM25 Keyword Search
        • Result Fusion
    """

    def __init__(self):

        self.semantic = SemanticRetriever()

        self.keyword = KeywordRetriever()

    def retrieve(
        self,
        query: str,
        k: int = 3
    ):

        semantic_results = self.semantic.retrieve(
            query=query,
            k=k
        )

        keyword_results = self.keyword.retrieve(
            query=query,
            k=k
        )

        # Currently return semantic results.
        # In the next commit we will merge both.
        return semantic_results


hybrid_retriever = HybridRetriever()