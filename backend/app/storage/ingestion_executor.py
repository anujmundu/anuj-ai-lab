from __future__ import annotations

from dataclasses import dataclass

from sqlmodel import Session, select

from app.db.ingestion_models import IngestionJob
from app.db.models import Asset
from app.storage.asset_reader import (
    AssetReader,
)
from app.storage.ingestion_job_service import (
    IngestionJobService,
)


@dataclass(frozen=True, slots=True)
class IngestionExecutionResult:
    job: IngestionJob
    asset: Asset
    result: dict | None = None


class IngestionExecutor:
    """
    Execution boundary for persistent ingestion jobs.

    This component manages job execution state and provides
    a streaming asset input to future ingestion processors.

    It does not implement:

        - document parsing
        - RAG
        - embeddings
        - vector storage
        - queue infrastructure
        - background workers
    """

    def __init__(
        self,
        *,
        job_service: IngestionJobService,
        asset_reader: AssetReader,
    ) -> None:

        self.job_service = job_service
        self.asset_reader = asset_reader

    def _load_job(
        self,
        session: Session,
        *,
        job_id: str,
    ) -> IngestionJob:

        job = self.job_service.get_job(
            session,
            job_id=job_id,
        )

        if job is None:
            raise ValueError(
                f"Ingestion job not found: {job_id}"
            )

        return job

    def _load_asset(
        self,
        session: Session,
        *,
        asset_id: str,
    ) -> Asset:

        asset = session.exec(
            select(Asset).where(
                Asset.asset_id == asset_id
            )
        ).first()

        if asset is None:
            raise ValueError(
                f"Asset not found: {asset_id}"
            )

        return asset

    def execute(
        self,
        session: Session,
        *,
        job_id: str,
    ) -> IngestionExecutionResult:

        job = self._load_job(
            session,
            job_id=job_id,
        )

        asset = self._load_asset(
            session,
            asset_id=job.asset_id,
        )

        if asset.status != "completed":
            raise ValueError(
                f"Asset is not ready for ingestion: "
                f"{asset.asset_id}"
            )

        if job.status == (
            self.job_service.STATUS_COMPLETED
        ):
            return IngestionExecutionResult(
                job=job,
                asset=asset,
                result=None,
            )

        if job.status == (
            self.job_service.STATUS_FAILED
        ):
            raise ValueError(
                f"Ingestion job has already failed: "
                f"{job.job_id}"
            )

        job = self.job_service.mark_running(
            session,
            job,
        )

        try:

            self.job_service.update_progress(
                session,
                job,
                progress=0.0,
            )

            with self.asset_reader.open(
                asset.storage_path
            ) as file:

                first_chunk = next(
                    self.asset_reader.iter_chunks(
                        file
                    ),
                    b"",
                )

            result = {
                "asset_id": asset.asset_id,
                "job_id": job.job_id,
                "status": "execution_ready",
                "input_available": bool(
                    first_chunk
                ),
            }

            job = self.job_service.mark_completed(
                session,
                job,
            )

            return IngestionExecutionResult(
                job=job,
                asset=asset,
                result=result,
            )

        except Exception as exc:

            self.job_service.mark_failed(
                session,
                job,
                error=str(exc),
            )

            raise


ingestion_executor = IngestionExecutor(
    job_service=IngestionJobService(),
    asset_reader=AssetReader(),
)
