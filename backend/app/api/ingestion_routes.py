from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile
from sqlmodel import Session

from app.db.database import get_session
from app.storage.asset_service import asset_service


router = APIRouter()


@router.post("/ingest")
def ingest_document(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    if not file.filename:
        return {
            "status": "failed",
            "error": "filename is required",
        }

    result = asset_service.upload(
        session,
        file.file,
        original_filename=Path(file.filename).name,
        mime_type=file.content_type
        or "application/octet-stream",
    )

    asset = result.asset

    return {
        "asset_id": asset.asset_id,
        "filename": asset.filename,
        "original_filename": asset.original_filename,
        "mime_type": asset.mime_type,
        "size_bytes": asset.size_bytes,
        "storage_path": asset.storage_path,
        "checksum": asset.checksum,
        "status": asset.status,
        "progress": asset.progress,
    }