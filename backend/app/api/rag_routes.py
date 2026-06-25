from fastapi import APIRouter

from app.rag.vector_store import vector_store
from app.rag.models import DocumentRequest


router = APIRouter()


@router.post("/rag/add")
def add_document(document: DocumentRequest):

    vector_store.add_document(
        document.id,
        document.text
    )

    return {
        "message": "Document added successfully."
    }


@router.get("/rag/search")
def search(
    query: str,
    k: int = 3
):

    return vector_store.search(
        query,
        k
    )