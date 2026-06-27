from abc import ABC, abstractmethod


class BaseRetriever(ABC):
    """
    Base interface for all retrieval engines.

    Every retrieval implementation should inherit
    from this interface.

    Examples:

    • SemanticRetriever
    • KeywordRetriever
    • BM25Retriever
    • ElasticsearchRetriever
    • OpenSearchRetriever
    • SQLiteFTSRetriever
    """

    @abstractmethod
    def retrieve(
        self,
        query: str,
        k: int = 3
    ):
        """
        Retrieve the top-k documents.

        Implementations should return a dictionary
        compatible with the ChromaDB query format.
        """

        raise NotImplementedError