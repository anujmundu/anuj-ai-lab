from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.database import get_session
from app.services.experiment_service import experiment_service


router = APIRouter(
    prefix="/experiments",
    tags=["Experiments"]
)

SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/")
def get_experiments(
    session: SessionDep
):

    return experiment_service.get_experiments(
        session
    )