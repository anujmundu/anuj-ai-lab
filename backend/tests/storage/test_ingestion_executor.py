import io
import uuid

import pytest

from sqlmodel import Session, SQLModel

from app.db.database import engine
from app.db.ingestion_models import IngestionJob
from app.db.models import Asset
from app.storage.asset_reader import AssetReader
from app.storage.asset_service import AssetService
from app.storage.asset_storage import AssetStorage
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
def storage(tmp_path):

    return AssetStorage(
        root_dir=tmp_path,
    )


@pytest.fixture()
def asset_service(storage):

    return AssetService(
        storage=storage,
    )


@pytest.fixture()
def job_service():

    return IngestionJobService()


@pytest.fixture()
def executor(job_service):

    return IngestionExecutor(
        job_service=job_service,
        asset_reader=AssetReader(),
    )


def create_asset(
    session,
    asset_service,
):

    result = asset_service.upload(
        session,
        io.BytesIO(
            b"test asset content"
        ),
        original_filename="test.txt",
        mime_type="text/plain",
    )

    return result.asset


def test_executor_completes_job(
    session,
    asset_service,
    job_service,
    executor,
):

    asset = create_asset(
        session,
        asset_service,
    )

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
    assert result.result["input_available"] is True


def test_executor_records_attempt(
    session,
    asset_service,
    job_service,
    executor,
):

    asset = create_asset(
        session,
        asset_service,
    )

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
            job_id=(
                f"missing-job-"
                f"{uuid.uuid4().hex}"
            ),
        )


def test_executor_rejects_missing_asset(
    session,
    job_service,
    executor,
):

    job = IngestionJob(
        job_id=(
            f"job-{uuid.uuid4().hex}"
        ),
        asset_id=(
            f"missing-asset-"
            f"{uuid.uuid4().hex}"
        ),
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

    asset = Asset(
        asset_id=(
            f"asset-{uuid.uuid4().hex}"
        ),
        filename="pending.txt",
        original_filename="pending.txt",
        mime_type="text/plain",
        size_bytes=0,
        storage_path="",
        checksum=None,
        status="uploading",
        progress=0.5,
    )

    session.add(asset)
    session.commit()
    session.refresh(asset)

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


def test_executor_fails_when_storage_file_is_missing(
    session,
    job_service,
    executor,
):

    asset = Asset(
        asset_id=(
            f"asset-{uuid.uuid4().hex}"
        ),
        filename="missing.txt",
        original_filename="missing.txt",
        mime_type="text/plain",
        size_bytes=10,
        storage_path=(
            "storage/assets/"
            "does-not-exist"
        ),
        checksum=None,
        status="completed",
        progress=1.0,
    )

    session.add(asset)
    session.commit()
    session.refresh(asset)

    job = job_service.create_job(
        session,
        asset_id=asset.asset_id,
    )

    with pytest.raises(
        FileNotFoundError,
        match="Asset storage file not found",
    ):

        executor.execute(
            session,
            job_id=job.job_id,
        )

    refreshed = job_service.get_job(
        session,
        job_id=job.job_id,
    )

    assert refreshed.status == "failed"
    assert refreshed.error is not None


def test_completed_job_is_idempotent(
    session,
    asset_service,
    job_service,
    executor,
):

    asset = create_asset(
        session,
        asset_service,
    )

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
