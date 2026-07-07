from fastapi import APIRouter

from app.memory.memory_service import memory_service


router = APIRouter(
    prefix="/conversation-memory",
    tags=["Conversation Memory"],
)


@router.get("")
def get_memory():
    return memory_service.get_memory()


@router.get("/last")
def get_last_message():
    return memory_service.get_last_message()


@router.delete("")
def clear_memory():
    memory_service.clear_memory()

    return {
        "message": "Memory cleared",
    }