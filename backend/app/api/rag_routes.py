from fastapi import APIRouter

from app.rag.rag_service import rag_service
from app.rag.vector_store import vector_store

from app.schemas.rag import (
    AskRequest,
    AskResponse,
)

router = APIRouter(
    tags=["Retrieval-Augmented Generation"],
)


@router.get("/rag/search")
def search(
    query: str,
    k: int = 3,
):
    return vector_store.search(
        query=query,
        k=k,
    )


@router.post(
    "/rag/ask",
    response_model=AskResponse,
)
def ask(
    request: AskRequest,
):
    return rag_service.ask(
        question=request.question,
        conversation=request.conversation,
    )


@router.get("/rag/diagnostics")
def diagnostics():
    return rag_service.diagnostics()