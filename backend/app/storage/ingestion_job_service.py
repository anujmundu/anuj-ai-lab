from __future__ import annotations

import uuid

from datetime import datetime

from sqlmodel import Session, select

from app.db.ingestion_models import IngestionJob


class IngestionJobService:
    """
    Persists the lifecycle of an asset ingestion job.

    This service owns job state only.

    It deliberately does not execute ingestion and does not
    depend on FastAPI, RAG, embeddings, parsing, or workers.
    """

    STATUS_QUEUED = "queued"
    STATUS_RUNNING = "running"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"

    def create_job(
        self,
        session: Session,
        *,
        asset_id: str,
    ) -> IngestionJob:

        if not asset_id:
            raise ValueError(
                "asset_id must not be empty"
            )

        job = IngestionJob(
            job_id=uuid.uuid4().hex,
            asset_id=asset_id,
            status=self.STATUS_QUEUED,
            progress=0.0,
            attempts=0,
        )

        session.add(job)
        session.commit()
        session.refresh(job)

        return job

    def get_job(
        self,
        session: Session,
        *,
        job_id: str,
    ) -> IngestionJob | None:

        statement = select(IngestionJob).where(
            IngestionJob.job_id == job_id
        )

        return session.exec(statement).first()

    def mark_running(
        self,
        session: Session,
        job: IngestionJob,
    ) -> IngestionJob:

        job.status = self.STATUS_RUNNING
        job.progress = max(
            0.0,
            min(1.0, job.progress),
        )
        job.attempts += 1
        job.started_at = (
            job.started_at
            or datetime.utcnow()
        )
        job.updated_at = datetime.utcnow()

        session.add(job)
        session.commit()
        session.refresh(job)

        return job

    def update_progress(
        self,
        session: Session,
        job: IngestionJob,
        *,
        progress: float,
    ) -> IngestionJob:

        if not 0.0 <= progress <= 1.0:
            raise ValueError(
                "progress must be between 0.0 and 1.0"
            )

        if job.status not in {
            self.STATUS_RUNNING,
            self.STATUS_QUEUED,
        }:
            raise ValueError(
                "progress can only be updated for "
                "queued or running jobs"
            )

        job.progress = progress
        job.updated_at = datetime.utcnow()

        session.add(job)
        session.commit()
        session.refresh(job)

        return job

    def mark_completed(
        self,
        session: Session,
        job: IngestionJob,
    ) -> IngestionJob:

        job.status = self.STATUS_COMPLETED
        job.progress = 1.0
        job.completed_at = datetime.utcnow()
        job.updated_at = datetime.utcnow()

        session.add(job)
        session.commit()
        session.refresh(job)

        return job

    def mark_failed(
        self,
        session: Session,
        job: IngestionJob,
        *,
        error: str,
    ) -> IngestionJob:

        if not error:
            raise ValueError(
                "error must not be empty"
            )

        job.status = self.STATUS_FAILED
        job.error = error
        job.updated_at = datetime.utcnow()

        session.add(job)
        session.commit()
        session.refresh(job)

        return job


ingestion_job_service = IngestionJobService()
