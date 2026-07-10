from app.memory.vector_store import (
    memory_vector_store,
)


class MemoryRetriever:
    """
    Retrieves semantically relevant memories.

    The retriever intentionally asks the vector store
    for more candidates than are ultimately needed.
    This improves recall and leaves room for future
    reranking strategies.
    """

    SEARCH_CANDIDATES = 20

    def __init__(
        self,
        repository,
    ):
        self.repository = repository

    def relevant(
        self,
        query: str,
    ):
        """
        Retrieve memories using semantic search.
        """

        results = memory_vector_store.search(
            query=query,
            limit=self.SEARCH_CANDIDATES,
        )

        ids = results.get(
            "ids",
            [],
        )

        if not ids:
            return []

        ids = ids[0]

        if not ids:
            return []

        memory_ids = [
            int(memory_id)
            for memory_id in ids
        ]

        return self.repository.get_by_ids(
            memory_ids,
        )

    def recent(
        self,
        limit: int = 5,
    ):
        return self.repository.get_recent(
            limit,
        )