import pytest

from app.db.database import engine
from app.db.ingestion_models import IngestionJob
from app.storage.ingestion_job_service import (
    IngestionJobService,
)
from sqlmodel import Session, SQLModel


@pytest.fixture()
def session():

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture()
def service():

    return IngestionJobService()


def test_create_job(session, service):

    job = service.create_job(
        session,
        asset_id="asset-001",
    )

    assert job.job_id
    assert job.asset_id == "asset-001"
    assert job.status == "queued"
    assert job.progress == 0.0
    assert job.attempts == 0


def test_get_job(session, service):

    created = service.create_job(
        session,
        asset_id="asset-002",
    )

    loaded = service.get_job(
        session,
        job_id=created.job_id,
    )

    assert loaded is not None
    assert loaded.job_id == created.job_id


def test_job_lifecycle(session, service):

    job = service.create_job(
        session,
        asset_id="asset-003",
    )

    job = service.mark_running(
        session,
        job,
    )

    assert job.status == "running"
    assert job.attempts == 1
    assert job.started_at is not None

    job = service.update_progress(
        session,
        job,
        progress=0.5,
    )

    assert job.progress == 0.5

    job = service.mark_completed(
        session,
        job,
    )

    assert job.status == "completed"
    assert job.progress == 1.0
    assert job.completed_at is not None


def test_failed_job(session, service):

    job = service.create_job(
        session,
        asset_id="asset-004",
    )

    job = service.mark_running(
        session,
        job,
    )

    job = service.mark_failed(
        session,
        job,
        error="Unsupported file format",
    )

    assert job.status == "failed"
    assert job.error == "Unsupported file format"


def test_validation(session, service):

    with pytest.raises(
        ValueError,
        match="asset_id",
    ):
        service.create_job(
            session,
            asset_id="",
        )

    job = service.create_job(
        session,
        asset_id="asset-005",
    )

    with pytest.raises(
        ValueError,
        match="progress",
    ):
        service.update_progress(
            session,
            job,
            progress=2.0,
        )

    with pytest.raises(
        ValueError,
        match="error",
    ):
        service.mark_failed(
            session,
            job,
            error="",
        )
