from sqlmodel import Session
from sqlmodel import select

from app.memory.models import Memory
from app.memory.schemas import MemoryCreate
from app.memory.schemas import MemoryUpdate


class MemoryRepository:
    def __init__(
        self,
        session: Session,
    ):
        self.session = session

    # ==========================================
    # Create
    # ==========================================

    def create(
        self,
        memory: MemoryCreate,
    ) -> Memory:
        db_memory = Memory(
            **memory.model_dump(),
        )

        self.session.add(db_memory)
        self.session.commit()
        self.session.refresh(db_memory)

        return db_memory

    # ==========================================
    # Read
    # ==========================================

    def get_all(
        self,
    ) -> list[Memory]:
        statement = (
            select(Memory)
            .order_by(
                Memory.created_at.desc()
            )
        )

        return list(
            self.session.exec(statement)
        )

    def get_by_id(
        self,
        memory_id: int,
    ) -> Memory | None:
        return self.session.get(
            Memory,
            memory_id,
        )
        
    def get_by_ids(
        self,
        memory_ids: list[int],
    ) -> list[Memory]:
        """
        Retrieve multiple memories by their IDs.

        The returned order matches the order of
        the supplied IDs.
        """

        if not memory_ids:
            return []

        statement = (
            select(Memory)
            .where(
                Memory.id.in_(memory_ids)
            )
        )

        memories = list(
            self.session.exec(statement)
        )

        memory_map = {
            memory.id: memory
            for memory in memories
        }

        return [
            memory_map[memory_id]
            for memory_id in memory_ids
            if memory_id in memory_map
        ]

    def exists(
        self,
        memory_id: int,
    ) -> bool:
        return (
            self.get_by_id(memory_id)
            is not None
        )

    def find_duplicate(
        self,
        content: str,
    ) -> Memory | None:
        statement = (
            select(Memory)
            .where(
                Memory.content == content
            )
        )

        return self.session.exec(
            statement
        ).first()

    def get_recent(
        self,
        limit: int = 10,
    ) -> list[Memory]:
        statement = (
            select(Memory)
            .order_by(
                Memory.created_at.desc()
            )
            .limit(limit)
        )

        return list(
            self.session.exec(statement)
        )

    def get_pinned(
        self,
    ) -> list[Memory]:
        statement = (
            select(Memory)
            .where(
                Memory.pinned.is_(True)
            )
            .order_by(
                Memory.created_at.desc()
            )
        )

        return list(
            self.session.exec(statement)
        )

    def get_by_category(
        self,
        category: str,
    ) -> list[Memory]:
        statement = (
            select(Memory)
            .where(
                Memory.category == category
            )
            .order_by(
                Memory.created_at.desc()
            )
        )

        return list(
            self.session.exec(statement)
        )

    def count(
        self,
    ) -> int:
        statement = select(Memory)

        return len(
            list(
                self.session.exec(statement)
            )
        )

    # ==========================================
    # Update
    # ==========================================

    def update(
        self,
        memory_id: int,
        update: MemoryUpdate,
    ) -> Memory | None:
        memory = self.get_by_id(
            memory_id,
        )

        if memory is None:
            return None

        data = update.model_dump()

        for key, value in data.items():
            setattr(
                memory,
                key,
                value,
            )

        self.session.add(memory)
        self.session.commit()
        self.session.refresh(memory)

        return memory

    # ==========================================
    # Delete
    # ==========================================

    def delete(
        self,
        memory_id: int,
    ) -> bool:
        memory = self.get_by_id(
            memory_id,
        )

        if memory is None:
            return False

        self.session.delete(memory)
        self.session.commit()

        return True

    # ==========================================
    # Search
    # ==========================================

    def search(
        self,
        query: str,
    ) -> list[Memory]:
        statement = (
            select(Memory)
            .where(
                Memory.content.contains(query)
            )
            .order_by(
                Memory.created_at.desc()
            )
        )

        return list(
            self.session.exec(statement)
        )
        
    