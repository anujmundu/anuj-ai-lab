from pathlib import Path
import shutil

from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File

from app.rag.ingestion_service import ingestion_service


router = APIRouter()


UPLOAD_DIR = "uploads"

Path(UPLOAD_DIR).mkdir(
    exist_ok=True
)


@router.post("/ingest")
def ingest_document(
    file: UploadFile = File(...)
):

    file_path = Path(UPLOAD_DIR) / file.filename

    with open(
        file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    return ingestion_service.ingest(
        str(file_path)
    )