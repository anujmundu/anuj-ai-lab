from app.memory.repository import MemoryRepository
from app.memory.schemas import MemoryCreate
from app.memory.schemas import MemoryUpdate
from app.memory.vector_store import memory_vector_store


class MemoryService:
    def __init__(
        self,
        repository: MemoryRepository,
    ):
        self.repository = repository

    # ==========================================
    # Create
    # ==========================================

    def add_memory(
        self,
        memory: MemoryCreate,
    ):
        memory.category = (
            memory.category
            .strip()
            .lower()
        )

        memory.importance = max(
            1,
            min(
                5,
                memory.importance,
            ),
        )

        duplicate = (
            self.repository.find_duplicate(
                memory.content,
            )
        )

        if duplicate is not None:
            return duplicate

        saved_memory = self.repository.create(
            memory,
        )

        memory_vector_store.add(
            memory_id=saved_memory.id,
            text=saved_memory.content,
        )

        return saved_memory

    # ==========================================
    # Read
    # ==========================================

    def list_memories(
        self,
    ):
        return self.repository.get_all()

    def get_memory(
        self,
        memory_id: int,
    ):
        return self.repository.get_by_id(
            memory_id,
        )

    def search_memories(
        self,
        query: str,
    ):
        return self.repository.search(
            query,
        )

    def get_relevant_memories(
        self,
        query: str,
    ):
        """
        Retrieve memories that are relevant
        to the supplied query.
        """

        return self.repository.search(
            query,
        )

    def get_recent_memories(
        self,
        limit: int = 10,
    ):
        return self.repository.get_recent(
            limit,
        )

    def get_pinned_memories(
        self,
    ):
        return self.repository.get_pinned()

    def get_memories_by_category(
        self,
        category: str,
    ):
        return self.repository.get_by_category(
            category.lower(),
        )

    def memory_count(
        self,
    ):
        return self.repository.count()

    # ==========================================
    # Update
    # ==========================================

    def update_memory(
        self,
        memory_id: int,
        update: MemoryUpdate,
    ):
        update.category = (
            update.category
            .strip()
            .lower()
        )

        update.importance = max(
            1,
            min(
                5,
                update.importance,
            ),
        )

        updated = self.repository.update(
            memory_id,
            update,
        )

        if updated is not None:

            memory_vector_store.update(
                memory_id=updated.id,
                text=updated.content,
            )

        return updated

    # ==========================================
    # Delete
    # ==========================================

    def delete_memory(
        self,
        memory_id: int,
    ):
        deleted = self.repository.delete(
            memory_id,
        )

        if deleted:

            memory_vector_store.delete(
                memory_id,
            )

        return deleted