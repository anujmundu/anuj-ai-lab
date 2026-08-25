import asyncio
import json
from pathlib import Path

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select

from app.db.database import engine, get_session
from app.db.ingestion_models import IngestionJob
from app.storage.asset_service import asset_service
from app.storage.ingestion_executor import ingestion_executor
from app.storage.ingestion_job_service import ingestion_job_service


router = APIRouter()


def _run_ingestion_job(job_id: str):
    """Background task worker to execute the ingestion pipeline."""
    with Session(engine) as session:
        try:
            ingestion_executor.execute(session, job_id=job_id)
        except Exception:
            # Error state is already recorded in the DB by IngestionExecutor
            pass


@router.post("/ingest")
def ingest_document(
    background_tasks: BackgroundTasks,
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

    # Create ingestion job and dispatch to background worker
    job = ingestion_job_service.create_job(
        session,
        asset_id=asset.asset_id,
    )
    background_tasks.add_task(_run_ingestion_job, job.job_id)

    return {
        "asset_id": asset.asset_id,
        "job_id": job.job_id,
        "job_status": job.status,
        "filename": asset.filename,
        "original_filename": asset.original_filename,
        "mime_type": asset.mime_type,
        "size_bytes": asset.size_bytes,
        "storage_path": asset.storage_path,
        "checksum": asset.checksum,
        "status": asset.status,
        "progress": asset.progress,
    }


@router.get("/ingestion/jobs/{job_id}")
def get_ingestion_job(
    job_id: str,
    session: Session = Depends(get_session),
):
    job = ingestion_job_service.get_job(session, job_id=job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Ingestion job {job_id} not found",
        )
    return {
        "job_id": job.job_id,
        "asset_id": job.asset_id,
        "status": job.status,
        "progress": job.progress,
        "attempts": job.attempts,
        "error": job.error,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "updated_at": job.updated_at.isoformat() if job.updated_at else None,
    }


@router.get("/ingestion/jobs")
def list_ingestion_jobs(
    limit: int = 50,
    session: Session = Depends(get_session),
):
    statement = (
        select(IngestionJob)
        .order_by(IngestionJob.created_at.desc())
        .limit(limit)
    )
    jobs = session.exec(statement).all()
    return [
        {
            "job_id": j.job_id,
            "asset_id": j.asset_id,
            "status": j.status,
            "progress": j.progress,
            "attempts": j.attempts,
            "error": j.error,
            "created_at": j.created_at.isoformat() if j.created_at else None,
            "completed_at": j.completed_at.isoformat() if j.completed_at else None,
        }
        for j in jobs
    ]


@router.post("/ingestion/jobs/{job_id}/retry")
def retry_ingestion_job(
    job_id: str,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
):
    job = ingestion_job_service.get_job(session, job_id=job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Ingestion job {job_id} not found",
        )

    # Reset job to queued state
    job.status = ingestion_job_service.STATUS_QUEUED
    job.error = None
    job.progress = 0.0
    session.add(job)
    session.commit()
    session.refresh(job)

    background_tasks.add_task(_run_ingestion_job, job.job_id)
    return {
        "job_id": job.job_id,
        "status": job.status,
        "message": "Ingestion job queued for retry",
    }


@router.get("/ingestion/jobs/{job_id}/stream")
async def stream_ingestion_progress(
    job_id: str,
):
    """Server-Sent Events (SSE) streaming endpoint for live job progress."""

    async def event_generator():
        last_status = None
        last_progress = None

        while True:
            with Session(engine) as session:
                job = ingestion_job_service.get_job(
                    session,
                    job_id=job_id,
                )

            if not job:
                yield f"data: {json.dumps({'error': 'Job not found'})}\n\n"
                break

            # Send update if state changed
            if job.status != last_status or job.progress != last_progress:
                last_status = job.status
                last_progress = job.progress

                payload = {
                    "job_id": job.job_id,
                    "asset_id": job.asset_id,
                    "status": job.status,
                    "progress": job.progress,
                    "error": job.error,
                }
                yield f"data: {json.dumps(payload)}\n\n"

            if job.status in {
                ingestion_job_service.STATUS_COMPLETED,
                ingestion_job_service.STATUS_FAILED,
            }:
                break

            await asyncio.sleep(0.5)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )