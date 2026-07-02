from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    """
    Standard success response used across the API.
    """

    message: str = Field(
        ...,
        description="Human-readable success message.",
        examples=["Operation completed successfully."],
    )


class ErrorResponse(BaseModel):
    """
    Standard error response.
    """

    detail: str = Field(
        ...,
        description="Human-readable error description.",
        examples=["Document not found."],
    )