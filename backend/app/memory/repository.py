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