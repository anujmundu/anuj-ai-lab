from fastapi import APIRouter

from app.rag.models import DocumentRequest
from app.rag.rag_service import rag_service
from app.rag.vector_store import vector_store


router = APIRouter()


@router.post("/rag/add")
def add_document(
    document: DocumentRequest
):

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


@router.get("/rag/ask")
def ask(
    question: str,
    conversation: str | None = None
):

    return rag_service.ask(
        question=question,
        conversation=conversation
    )


@router.get("/rag/diagnostics")
def diagnostics():

    return rag_service.diagnostics()