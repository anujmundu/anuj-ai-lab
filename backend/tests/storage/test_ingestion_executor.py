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
from app.storage.ingestion_processor import (
    IngestionProcessorResult,
    InspectionIngestionProcessor,
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
def processor():

    return InspectionIngestionProcessor(
        chunk_size=4,
    )


@pytest.fixture()
def executor(
    job_service,
    processor,
):

    return IngestionExecutor(
        job_service=job_service,
        asset_reader=AssetReader(
            chunk_size=4,
        ),
        processor=processor,
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


def create_database_asset(
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

    asset = create_database_asset(
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


def test_executor_delegates_to_processor(
    session,
    asset_service,
    job_service,
):

    class RecordingProcessor:

        def __init__(self):

            self.called = False
            self.bytes_processed = 0

        def process(
            self,
            file,
            *,
            asset,
        ):

            self.called = True

            data = file.read()

            self.bytes_processed = len(data)

            return IngestionProcessorResult(
                status="processed",
                bytes_processed=len(data),
                metadata={
                    "asset_id": asset.asset_id,
                },
            )

    processor = RecordingProcessor()

    executor = IngestionExecutor(
        job_service=job_service,
        asset_reader=AssetReader(),
        processor=processor,
    )

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

    assert processor.called is True
    assert processor.bytes_processed == asset.size_bytes
    assert result.result["processor_status"] == "processed"