from fastapi import APIRouter

from app.services.prompt_service import prompt_service


router = APIRouter(
    prefix="/prompts",
    tags=["Prompts"]
)


@router.get("/summarize")
def summarize():

    prompt = prompt_service.load_prompt(
        "summarize",
        text="Artificial intelligence is transforming healthcare and education."
    )

    return {
        "prompt": prompt
    }