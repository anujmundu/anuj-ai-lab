from datetime import datetime

from sqlmodel import Field, SQLModel


class Asset(SQLModel, table=True):
    __tablename__ = "assets"

    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    asset_id: str = Field(
        index=True,
        unique=True,
    )

    filename: str

    original_filename: str

    mime_type: str = Field(
        default="application/octet-stream",
    )

    size_bytes: int = Field(
        default=0,
    )

    storage_path: str

    checksum: str | None = Field(
        default=None,
        index=True,
    )

    status: str = Field(
        default="created",
        index=True,
    )

    progress: float = Field(
        default=0.0,
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
    )
