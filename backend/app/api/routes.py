from fastapi import APIRouter

from app.services.ollama_service import ollama_service


router = APIRouter()


@router.get("/health")
def health():

    return {
        "status": "healthy"
    }


@router.get("/test-llm")
def test_llm():

    response = ollama_service.generate(
        "Reply with exactly one word: Hello"
    )

    return {
        "response": response
    }