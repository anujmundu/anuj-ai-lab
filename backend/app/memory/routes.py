from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlmodel import Session

from app.db.database import get_session

from app.memory.repository import MemoryRepository
from app.memory.schemas import MemoryCreate
from app.memory.schemas import MemoryResponse
from app.memory.schemas import MemoryUpdate
from app.memory.service import MemoryService


router = APIRouter(
    prefix="/memory",
    tags=["Memory"],
)


def get_memory_service(
    session: Session = Depends(get_session),
) -> MemoryService:
    repository = MemoryRepository(session)

    return MemoryService(repository)


@router.post(
    "",
    response_model=MemoryResponse,
)
def create_memory(
    memory: MemoryCreate,
    service: MemoryService = Depends(get_memory_service),
):
    return service.add_memory(memory)


@router.get(
    "",
    response_model=list[MemoryResponse],
)
def list_memories(
    service: MemoryService = Depends(get_memory_service),
):
    return service.list_memories()


@router.get(
    "/search",
    response_model=list[MemoryResponse],
)
def search_memories(
    query: str,
    service: MemoryService = Depends(get_memory_service),
):
    return service.search_memories(query)


@router.put(
    "/{memory_id}",
    response_model=MemoryResponse,
)
def update_memory(
    memory_id: int,
    update: MemoryUpdate,
    service: MemoryService = Depends(get_memory_service),
):
    memory = service.update_memory(
        memory_id,
        update,
    )

    if memory is None:
        raise HTTPException(
            status_code=404,
            detail="Memory not found",
        )

    return memory


@router.delete(
    "/{memory_id}",
)
def delete_memory(
    memory_id: int,
    service: MemoryService = Depends(get_memory_service),
):
    deleted = service.delete_memory(
        memory_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Memory not found",
        )

    return {
        "message": "Memory deleted",
    }