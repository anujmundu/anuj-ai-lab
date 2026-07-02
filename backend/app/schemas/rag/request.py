from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    """
    Request payload for asking a question
    through the Retrieval-Augmented Generation pipeline.
    """

    question: str = Field(
        ...,
        min_length=1,
        description="Question submitted to the RAG pipeline.",
        examples=[
            "Explain Retrieval-Augmented Generation."
        ],
    )

    conversation: str | None = Field(
        default=None,
        description="Optional conversation identifier for future conversational memory support.",
        examples=[
            "session-001"
        ],
    )


class AddDocumentRequest(BaseModel):
    """
    Request payload for adding a document
    directly to the vector store.
    """

    id: str = Field(
        ...,
        description="Unique document identifier.",
        examples=[
            "python_notes"
        ],
    )

    text: str = Field(
        ...,
        min_length=1,
        description="Raw document text.",
    )