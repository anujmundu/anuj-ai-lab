from fastapi import APIRouter

from app.services.planner_service import planner_service


router = APIRouter()


@router.get("/plan")
def create_plan(
    goal: str
):

    return planner_service.generate_plan(
        goal
    )