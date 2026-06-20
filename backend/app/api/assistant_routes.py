from fastapi import APIRouter

from app.services.assistant_service import assistant_service


router = APIRouter()


@router.get("/assistant")
def assistant(
    goal: str
):

    return assistant_service.execute(
        goal
    )