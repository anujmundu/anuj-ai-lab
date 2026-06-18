from fastapi import APIRouter

from app.services.model_compare_service import (
    model_compare_service
)


router = APIRouter(
    prefix="/compare",
    tags=["Compare"]
)


@router.get("/")
def compare_models():

    prompt = (
        "Explain Artificial Intelligence in one sentence."
    )

    return model_compare_service.compare_models(
        prompt
    )