from app.memory.extractor import memory_extractor
from app.memory.repository import MemoryRepository
from app.memory.retriever import MemoryRetriever
from app.memory.service import MemoryService

from sqlmodel import Session


class MemoryManager:
    """
    Coordinates the complete memory pipeline.

    Responsibilities

    • Extract memories
    • Prevent duplicates
    • Persist memories
    • Retrieve recent memories
    • Prepare memory context
    """

    def __init__(
        self,
        session: Session,
    ):
        repository = MemoryRepository(
            session,
        )

        self.service = MemoryService(
            repository,
        )
        
        self.retriever = MemoryRetriever(
            repository,
        )

    # --------------------------------------------------
    # Memory Extraction
    # --------------------------------------------------

    def process(
        self,
        text: str,
    ):
        memory = (
            memory_extractor.extract(
                text,
            )
        )

        if memory is None:
            return None

        return self.service.add_memory(
            memory,
        )

    # --------------------------------------------------
    # Memory Retrieval
    # --------------------------------------------------

    def recent_context(
        self,
        limit: int = 5,
    ) -> str:

        memories = (
            self.service.get_recent_memories(
                limit,
            )
        )

        if not memories:
            return ""

        context = []

        for memory in memories:

            context.append(
                f"- {memory.content}"
            )

        return "\n".join(
            context,
        )
        
    def relevant_context(
        self,
        query: str,
    ) -> str:
        """
        Build prompt context using memories that
        are relevant to the supplied query.
        """

        memories = (
            self.retriever.relevant(
                query,
            )
        )

        if not memories:
            return ""

        context = []

        for memory in memories:

            context.append(
                f"- {memory.content}"
            )

        return "\n".join(
            context,
        )    

    # --------------------------------------------------
    # Statistics
    # --------------------------------------------------

    def count(
        self,
    ) -> int:
        return self.service.memory_count()