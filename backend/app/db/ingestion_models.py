from datetime import datetime

from sqlmodel import Field, SQLModel


class IngestionJob(SQLModel, table=True):
    __tablename__ = "ingestion_jobs"

    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    job_id: str = Field(
        index=True,
        unique=True,
    )

    asset_id: str = Field(
        index=True,
    )

    status: str = Field(
        default="queued",
        index=True,
    )

    progress: float = Field(
        default=0.0,
    )

    attempts: int = Field(
        default=0,
    )

    error: str | None = Field(
        default=None,
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
    )

    started_at: datetime | None = Field(
        default=None,
    )

    completed_at: datetime | None = Field(
        default=None,
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
    )
