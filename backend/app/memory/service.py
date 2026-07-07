from app.memory.repository import MemoryRepository
from app.memory.schemas import MemoryCreate
from app.memory.schemas import MemoryUpdate


class MemoryService:
    def __init__(
        self,
        repository: MemoryRepository,
    ):
        self.repository = repository

    def add_memory(
        self,
        memory: MemoryCreate,
    ):
        return self.repository.create(
            memory,
        )

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

    def update_memory(
        self,
        memory_id: int,
        update: MemoryUpdate,
    ):
        return self.repository.update(
            memory_id,
            update,
        )

    def delete_memory(
        self,
        memory_id: int,
    ):
        return self.repository.delete(
            memory_id,
        )

    def search_memories(
        self,
        query: str,
    ):
        return self.repository.search(
            query,
        )