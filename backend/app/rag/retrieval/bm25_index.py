from app.rag.bm25_retriever import BM25Retriever


class BM25Index:
    """
    Persistent BM25 index.

    Responsibilities

    • Own a BM25Retriever instance
    • Cache indexed documents
    • Build and rebuild the keyword index
    • Provide keyword search

    Future responsibilities

    • Incremental updates
    • Persistent storage
    • Background rebuilding
    • Statistics
    """

    def __init__(self):

        self.retriever = BM25Retriever()

        self.documents: list[str] = []

        self.is_ready = False

    # --------------------------------------------------
    # Build
    # --------------------------------------------------

    def build(
        self,
        documents: list[str],
    ) -> None:
        """
        Build a fresh BM25 index.
        """

        self.documents = documents.copy()

        self.retriever.build(
            self.documents,
        )

        self.is_ready = True

    def rebuild(
        self,
        documents: list[str],
    ) -> None:
        """
        Rebuild the complete BM25 index.
        """

        self.build(
            documents,
        )

    def clear(
        self,
    ) -> None:

        self.documents = []

        self.retriever = BM25Retriever()

        self.is_ready = False

    # --------------------------------------------------
    # Search
    # --------------------------------------------------

    def search(
        self,
        query: str,
        k: int = 5,
    ) -> list[tuple[int, float]]:
        """
        Search the BM25 index.

        Returns
        -------
        [
            (
                document_index,
                bm25_score
            )
        ]
        """

        if not self.is_ready:
            return []

        return self.retriever.search(
            query=query,
            k=k,
        )

    # --------------------------------------------------
    # Diagnostics
    # --------------------------------------------------

    @property
    def document_count(
        self,
    ) -> int:

        return len(
            self.documents
        )


bm25_index = BM25Index()