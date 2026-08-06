from sqlmodel import Session

from app.db.database import engine
from app.memory.manager import MemoryManager


class MemoryPipeline:
    """
    Handles retrieval and persistence of
    long-term conversational memory.
    """

    def prepare(
        self,
        *,
        question: str,
        conversation: str | None,
    ) -> str:
        """
        Prepare persistent memory for prompt construction.

        Conversation support is reserved for future
        conversation-specific memory retrieval.
        """

        with Session(engine) as session:

            manager = MemoryManager(
                session=session,
            )

            return manager.relevant_context(
                query=question,
            )

    def store(
        self,
        *,
        question: str,
    ) -> None:
        """
        Extract and persist useful user memories.

        This currently stores only the user's message.
        Future versions may also process assistant
        responses and conversation history.
        """

        with Session(engine) as session:

            manager = MemoryManager(
                session=session,
            )

            manager.process(
                question,
            )


memory_pipeline = MemoryPipeline()