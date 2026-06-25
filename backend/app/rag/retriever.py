from app.rag.vector_store import vector_store


class Retriever:

    def retrieve(
        self,
        query: str,
        k: int = 3
    ):

        return vector_store.search(
            query=query,
            k=k
        )


retriever = Retriever()