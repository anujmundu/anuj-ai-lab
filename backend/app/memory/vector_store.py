import chromadb

from app.memory.embedding_service import (
    memory_embedding_service,
)


class MemoryVectorStore:
    """
    Persistent vector store for user memories.

    Responsibilities

    • Store memory embeddings.
    • Perform semantic similarity search.
    • Update memory embeddings.
    • Delete memory embeddings.

    The SQL database remains the source of truth for
    memory metadata. ChromaDB stores only embeddings
    and memory text for semantic retrieval.
    """

    def __init__(self):

        print("Initializing Memory Vector Store...")

        self.client = chromadb.PersistentClient(
            path="vector_db",
        )

        self.collection = (
            self.client.get_or_create_collection(
                name="memories",
            )
        )

        print("Memory Vector Store ready.")

    # --------------------------------------------------
    # Insert
    # --------------------------------------------------

    def add(
        self,
        memory_id: int,
        text: str,
    ) -> None:
        """
        Store a memory embedding.
        """

        embedding = (
            memory_embedding_service.embed(
                text,
            )
        )

        self.collection.add(
            ids=[
                str(memory_id),
            ],
            documents=[
                text,
            ],
            embeddings=[
                embedding,
            ],
        )

    # --------------------------------------------------
    # Search
    # --------------------------------------------------

    def search(
        self,
        query: str,
        limit: int = 5,
    ) -> dict:
        """
        Perform semantic memory search.
        """

        embedding = (
            memory_embedding_service.embed(
                query,
            )
        )

        return self.collection.query(
            query_embeddings=[
                embedding,
            ],
            n_results=limit,
        )
        
    # --------------------------------------------------
    # Maintenance
    # --------------------------------------------------

    def clear(
        self,
    ) -> None:
        """
        Remove all memory embeddings from the vector store.

        This is intended for administrative operations
        such as rebuilding the vector index.
        """

        self.client.delete_collection(
            name="memories",
        )

        self.collection = (
            self.client.get_or_create_collection(
                name="memories",
            )
        )

    # --------------------------------------------------
    # Delete
    # --------------------------------------------------

    def delete(
        self,
        memory_id: int,
    ) -> None:
        """
        Remove a memory embedding.
        """

        self.collection.delete(
            ids=[
                str(memory_id),
            ]
        )

    # --------------------------------------------------
    # Update
    # --------------------------------------------------

    def update(
        self,
        memory_id: int,
        text: str,
    ) -> None:
        """
        Update an existing memory embedding.
        """

        embedding = (
            memory_embedding_service.embed(
                text,
            )
        )

        self.collection.upsert(
            ids=[
                str(memory_id),
            ],
            documents=[
                text,
            ],
            embeddings=[
                embedding,
            ],
        )
        
        # --------------------------------------------------
    # Debug
    # --------------------------------------------------

    def count(self) -> int:
        """
        Return the number of embeddings stored in ChromaDB.
        """
        return self.collection.count()

    def dump(self) -> dict:
        """
        Return all records currently stored in ChromaDB.
        """
        return self.collection.get()


memory_vector_store = (
    MemoryVectorStore()
)