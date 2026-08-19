import uuid

import pytest

from sqlmodel import Session, SQLModel, select

from app.db.database import engine
from app.db.ingestion_models import IngestionJob
from app.db.models import Asset
from app.storage.ingestion_executor import (
    IngestionExecutor,
)
from app.storage.ingestion_job_service import (
    IngestionJobService,
)


@pytest.fixture()
def session():

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture()
def job_service():

    return IngestionJobService()


@pytest.fixture()
def executor(job_service):

    return IngestionExecutor(
        job_service=job_service,
    )


def create_asset(
    session,
    *,
    status="completed",
    progress=1.0,
):

    asset = Asset(
        asset_id=f"asset-{uuid.uuid4().hex}",
        filename="test.txt",
        original_filename="test.txt",
        mime_type="text/plain",
        size_bytes=18,
        storage_path="storage/assets/test",
        checksum=None,
        status=status,
        progress=progress,
    )

    session.add(asset)
    session.commit()
    session.refresh(asset)

    return asset


def test_executor_completes_job(
    session,
    job_service,
    executor,
):

    asset = create_asset(session)

    job = job_service.create_job(
        session,
        asset_id=asset.asset_id,
    )

    result = executor.execute(
        session,
        job_id=job.job_id,
    )

    assert result.asset.asset_id == asset.asset_id
    assert result.job.job_id == job.job_id
    assert result.job.status == "completed"
    assert result.job.progress == 1.0
    assert result.result["status"] == "execution_ready"


def test_executor_records_attempt(
    session,
    job_service,
    executor,
):

    asset = create_asset(session)

    job = job_service.create_job(
        session,
        asset_id=asset.asset_id,
    )

    result = executor.execute(
        session,
        job_id=job.job_id,
    )

    assert result.job.attempts == 1
    assert result.job.started_at is not None
    assert result.job.completed_at is not None


def test_executor_rejects_missing_job(
    session,
    executor,
):

    with pytest.raises(
        ValueError,
        match="Ingestion job not found",
    ):

        executor.execute(
            session,
            job_id=f"missing-job-{uuid.uuid4().hex}",
        )


def test_executor_rejects_missing_asset(
    session,
    job_service,
    executor,
):

    job = IngestionJob(
        job_id=f"job-{uuid.uuid4().hex}",
        asset_id=f"missing-asset-{uuid.uuid4().hex}",
        status="queued",
    )

    session.add(job)
    session.commit()
    session.refresh(job)

    with pytest.raises(
        ValueError,
        match="Asset not found",
    ):

        executor.execute(
            session,
            job_id=job.job_id,
        )


def test_executor_requires_completed_asset(
    session,
    job_service,
    executor,
):

    asset = create_asset(
        session,
        status="uploading",
        progress=0.5,
    )

    job = job_service.create_job(
        session,
        asset_id=asset.asset_id,
    )

    with pytest.raises(
        ValueError,
        match="Asset is not ready",
    ):

        executor.execute(
            session,
            job_id=job.job_id,
        )


def test_completed_job_is_idempotent(
    session,
    job_service,
    executor,
):

    asset = create_asset(session)

    job = job_service.create_job(
        session,
        asset_id=asset.asset_id,
    )

    first = executor.execute(
        session,
        job_id=job.job_id,
    )

    second = executor.execute(
        session,
        job_id=job.job_id,
    )

    assert first.job.job_id == second.job.job_id
    assert second.job.status == "completed"
    assert second.job.attempts == 1