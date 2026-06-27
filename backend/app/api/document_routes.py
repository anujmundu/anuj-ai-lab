from fastapi import APIRouter

from app.rag.document_manager import document_manager

router = APIRouter(
    tags=["Document Management"]
)


@router.get("/documents")
def list_documents():

    return document_manager.list_documents()


@router.delete("/documents/{filename}")
def delete_document(
    filename: str
):

    return document_manager.delete_document(
        filename
    )