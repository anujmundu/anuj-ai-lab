from fastapi import APIRouter

from app.services.collaboration_service import (
    collaboration_service
)


router = APIRouter()


@router.get("/collaborate")
def collaborate(
    goal: str
):

    return collaboration_service.execute(
        goal
    )