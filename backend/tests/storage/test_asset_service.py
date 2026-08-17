from __future__ import annotations

import io

from sqlmodel import Session
from sqlmodel import SQLModel
from sqlmodel import create_engine
from sqlalchemy.pool import StaticPool

from app.db.models import Asset
from app.storage.asset_service import (
    AssetService,
)
from app.storage.asset_storage import (
    AssetStorage,
)


def _session():
    engine = create_engine(
        "sqlite://",
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
    )

    SQLModel.metadata.create_all(
        engine
    )

    return engine


def test_create_asset_creates_created_record(
    tmp_path,
):

    engine = _session()

    service = AssetService(
        AssetStorage(tmp_path)
    )

    with Session(engine) as session:

        asset = service.create_asset(
            session,
            original_filename="document.pdf",
            mime_type="application/pdf",
        )

        assert asset.id is not None
        assert asset.asset_id
        assert asset.filename == "document.pdf"
        assert asset.original_filename == "document.pdf"
        assert asset.mime_type == "application/pdf"
        assert asset.size_bytes == 0
        assert asset.storage_path == ""
        assert asset.status == "created"
        assert asset.progress == 0.0


def test_upload_completes_asset(
    tmp_path,
):

    engine = _session()

    service = AssetService(
        AssetStorage(tmp_path)
    )

    content = (
        b"Anuj AI Lab persistent asset"
    )

    with Session(engine) as session:

        result = service.upload(
            session,
            io.BytesIO(content),
            original_filename="test.txt",
            mime_type="text/plain",
        )

        asset = result.asset

        assert result.stored is not None

        assert asset.status == "completed"
        assert asset.progress == 1.0
        assert asset.size_bytes == len(
            content
        )
        assert asset.storage_path
        assert asset.checksum

        stored_path = tmp_path / asset.asset_id

        assert stored_path.exists()
        assert (
            stored_path.read_bytes()
            == content
        )


def test_upload_persists_completed_record(
    tmp_path,
):

    engine = _session()

    service = AssetService(
        AssetStorage(tmp_path)
    )

    with Session(engine) as session:

        result = service.upload(
            session,
            io.BytesIO(b"persistent"),
            original_filename="persistent.txt",
            mime_type="text/plain",
        )

        asset_id = result.asset.asset_id

    with Session(engine) as session:

        stored_asset = session.get(
            Asset,
            result.asset.id,
        )

        assert stored_asset is not None
        assert (
            stored_asset.asset_id
            == asset_id
        )
        assert (
            stored_asset.status
            == "completed"
        )
        assert (
            stored_asset.progress
            == 1.0
        )


def test_failed_upload_marks_asset_failed(
    tmp_path,
):

    engine = _session()

    class FailingStorage:

        def store(
            self,
            file,
            *,
            original_filename,
            asset_id,
        ):

            raise RuntimeError(
                "simulated storage failure"
            )

    service = AssetService(
        FailingStorage()
    )

    with Session(engine) as session:

        try:

            service.upload(
                session,
                io.BytesIO(
                    b"will fail"
                ),
                original_filename="failed.bin",
            )

        except RuntimeError as exc:

            assert (
                str(exc)
                == "simulated storage failure"
            )

        else:

            raise AssertionError(
                "Expected storage failure"
            )

        assets = session.exec(
            Asset.__table__.select()
        ).all()

        assert len(assets) == 1

        asset = assets[0]

        assert asset.status == "failed"
        assert asset.progress == 0.0


def test_failed_upload_does_not_report_completed(
    tmp_path,
):

    engine = _session()

    class FailingStorage:

        def store(
            self,
            file,
            *,
            original_filename,
            asset_id,
        ):

            raise IOError(
                "disk failure"
            )

    service = AssetService(
        FailingStorage()
    )

    with Session(engine) as session:

        try:

            service.upload(
                session,
                io.BytesIO(b"data"),
                original_filename="file.bin",
            )

        except IOError:
            pass

        asset = session.exec(
            Asset.__table__.select()
        ).first()

        assert asset is not None
        assert asset.status != "completed"