from fastapi import APIRouter

from app.voice.voice_agent import voice_agent


router = APIRouter()


@router.get("/voice")
def voice(
    text: str
):

    return voice_agent.process(
        text
    )