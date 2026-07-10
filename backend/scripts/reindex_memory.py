from sqlmodel import Session

from app.db.database import engine
from app.memory.repository import MemoryRepository
from app.memory.vector_store import memory_vector_store


def main() -> None:
    """
    Rebuild the memory vector index from the SQL database.

    This utility should be used whenever the embedding
    model changes or the vector store needs to be
    synchronized with persistent storage.
    """

    print("=" * 60)
    print("Memory Vector Index Rebuild")
    print("=" * 60)

    with Session(engine) as session:

        repository = MemoryRepository(
            session,
        )

        memories = repository.get_all()

    print(
        f"\nFound {len(memories)} memories in SQL database."
    )

    print("\nClearing vector store...")

    memory_vector_store.clear()

    print("Vector store cleared.")

    print("\nRebuilding embeddings...")

    for memory in memories:

        memory_vector_store.add(
            memory_id=memory.id,
            text=memory.content,
        )

        print(
            f"Indexed memory {memory.id}"
        )

    print("\nRebuild complete.")

    print(
        f"Vector store now contains "
        f"{memory_vector_store.count()} memories."
    )


if __name__ == "__main__":
    main()