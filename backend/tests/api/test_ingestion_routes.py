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


def test_ingest_route_returns_job_id():
    response = client.post(
        "/ingest",
        files={
            "file": (
                "job_test.txt",
                BytesIO(b"Job tracking test content"),
                "text/plain",
            )
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert "job_status" in data

    # Verify job lookup endpoint
    job_id = data["job_id"]
    job_resp = client.get(f"/ingestion/jobs/{job_id}")
    assert job_resp.status_code == 200
    job_data = job_resp.json()
    assert job_data["job_id"] == job_id
    assert "status" in job_data


def test_list_ingestion_jobs():
    response = client.get("/ingestion/jobs")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_nonexistent_job_returns_404():
    response = client.get("/ingestion/jobs/nonexistent-job-id-9999")
    assert response.status_code == 404


def test_retry_ingestion_job():
    # First create a job via upload
    resp = client.post(
        "/ingest",
        files={
            "file": (
                "retry_test.txt",
                BytesIO(b"Content for retry test"),
                "text/plain",
            )
        },
    )
    job_id = resp.json()["job_id"]

    retry_resp = client.post(f"/ingestion/jobs/{job_id}/retry")
    assert retry_resp.status_code == 200
    retry_data = retry_resp.json()
    assert retry_data["job_id"] == job_id
    assert retry_data["status"] == "queued"