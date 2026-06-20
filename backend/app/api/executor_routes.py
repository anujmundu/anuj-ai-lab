from fastapi import APIRouter

from app.services.executor_service import executor_service


router = APIRouter()


@router.get("/execute")
def execute_workflow(
    goal: str
):

    return executor_service.run_workflow(
        goal
    )