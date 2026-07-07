from datetime import datetime

from sqlmodel import Field
from sqlmodel import SQLModel


class Memory(SQLModel, table=True):
    __tablename__ = "memories"

    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    content: str

    category: str = Field(
        default="general",
    )

    importance: int = Field(
        default=1,
    )

    pinned: bool = Field(
        default=False,
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
    )