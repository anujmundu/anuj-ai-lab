from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.database import get_session
from app.services.experiment_service import experiment_service
from app.services.ollama_service import ollama_service
from app.services.prompt_service import prompt_service
from app.core.config import settings


router = APIRouter(
    prefix="/prompts",
    tags=["Prompts"]
)

SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/summarize")
def summarize(
    session: SessionDep
):

    input_text = (
        "Artificial intelligence is transforming healthcare and education."
    )

    prompt = prompt_service.load_prompt(
        "summarize",
        text=input_text
    )

    output = ollama_service.generate(
        prompt
    )

    experiment_service.create_experiment(
        session=session,
        prompt_name="summarize",
        input_text=input_text,
        output_text=output,
        model_name=settings.DEFAULT_MODEL
    )

    return {
        "response": output
    }