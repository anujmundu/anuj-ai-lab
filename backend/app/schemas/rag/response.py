from pydantic import BaseModel, Field


class SourceInfo(BaseModel):
    """
    Metadata describing a retrieved source.
    """

    filename: str = Field(
        ...,
        description="Source document filename.",
    )

    chunk_id: str = Field(
        ...,
        description="Unique chunk identifier.",
    )

    chunk_number: int = Field(
        ...,
        description="Chunk number within the document.",
    )

    total_chunks: int = Field(
        ...,
        description="Total number of chunks in the document.",
    )


class AskResponse(BaseModel):
    """
    Response returned by the RAG pipeline.
    """

    question: str = Field(
        ...,
        description="Original user question.",
    )

    answer: str = Field(
        ...,
        description="Generated answer.",
    )

    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score assigned to the generated answer.",
    )

    sources: list[SourceInfo] = Field(
        default_factory=list,
        description="Retrieved sources used during answer generation.",
    )