from app.rag.bm25_index import bm25_index
from app.rag.vector_store import vector_store


class BM25Initializer:
    """
    Initializes the in-memory BM25 index
    from the persisted ChromaDB corpus.

    Responsibilities

    • Load all indexed chunks
    • Build BM25 index
    • Report initialization statistics

    Future responsibilities

    • Incremental loading
    • Startup diagnostics
    • Index persistence
    """

    def initialize(self) -> dict:

        corpus = vector_store.get_all_chunks()

        documents = corpus.get(
            "documents",
            [],
        )

        bm25_index.build(
            documents,
        )

        return {
            "documents_loaded": len(documents),
            "bm25_documents": (
                bm25_index.document_count
            ),
        }


bm25_initializer = BM25Initializer()