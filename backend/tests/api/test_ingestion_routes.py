from io import BytesIO

from fastapi import UploadFile
from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_ingest_route_exists():
    response = client.post(
        "/ingest",
        files={
            "file": (
                "test.txt",
                BytesIO(b"hello world"),
                "text/plain",
            )
        },
    )

    assert response.status_code != 404


def test_ingest_route_requires_file():
    response = client.post("/ingest")

    assert response.status_code == 422


def test_ingest_route_accepts_uploaded_file():
    response = client.post(
        "/ingest",
        files={
            "file": (
                "test.txt",
                BytesIO(b"Anuj AI Lab ingestion test"),
                "text/plain",
            )
        },
    )

    assert response.status_code == 200


def test_ingest_route_streams_upload_to_asset_service(
    monkeypatch,
):
    import app.api.ingestion_routes as ingestion_routes
    from app.db.models import Asset
    from app.storage.asset_service import AssetServiceResult

    captured = {}

    def fake_upload(
        session,
        file,
        *,
        original_filename,
        mime_type,
    ):
        captured["file"] = file
        captured["original_filename"] = original_filename
        captured["mime_type"] = mime_type

        asset = Asset(
            asset_id="test-asset-id",
            filename=original_filename,
            original_filename=original_filename,
            mime_type=mime_type,
            size_bytes=1024 * 1024,
            storage_path="storage/test-asset-id/test.txt",
            checksum="test-checksum",
            status="completed",
            progress=1.0,
        )

        return AssetServiceResult(
            asset=asset,
        )

    monkeypatch.setattr(
        ingestion_routes.asset_service,
        "upload",
        fake_upload,
    )

    response = client.post(
        "/ingest",
        files={
            "file": (
                "large-test.txt",
                BytesIO(b"x" * (1024 * 1024)),
                "text/plain",
            )
        },
    )

    assert response.status_code == 200

    assert captured["original_filename"] == "large-test.txt"
    assert captured["mime_type"] == "text/plain"

    # The route passes the file stream directly to AssetService.
    assert captured["file"] is not None
    assert hasattr(captured["file"], "read")