from app.rag.vector_store import vector_store


class Retriever:
    """
    Adapter around the vector store.

    Returns the native ChromaDB response. Mapping into the
    RetrievalResult domain model is performed after the
    retrieval pipeline has completed.
    """

    def retrieve(
        self,
        query: str,
        k: int = 3,
    ):

        return vector_store.search(
            query=query,
            k=k,
        )


retriever = Retriever()