from fastapi import APIRouter

from app.services.state_service import state_service


router = APIRouter()


@router.get("/state")
def get_state():

    return state_service.get_state()


@router.post("/state/reset")
def reset_state():

    state_service.reset_state()

    return {
        "message": "state reset"
    }