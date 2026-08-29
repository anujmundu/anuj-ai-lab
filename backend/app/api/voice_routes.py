from __future__ import annotations

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
from typing import Any

from app.media.voice_service import local_voice_service

router = APIRouter(prefix="/voice", tags=["Local Voice STT & TTS"])


class SynthesisRequest(BaseModel):
    text: str = Field(..., description="Text string to synthesize into speech")
    voice: str = Field(default="af_sarah", description="Voice profile ID (e.g., af_sarah, af_bella, am_adam)")
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Playback speed multiplier")
    lang: str = Field(default="en-us", description="Language code")


@router.post("/transcribe", response_model=dict[str, Any])
async def transcribe_audio(file: UploadFile = File(...)) -> dict[str, Any]:
    """Transcribe an uploaded audio file using Faster-Whisper."""
    try:
        content = await file.read()
        return local_voice_service.transcribe_audio_bytes(content)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(exc)}")


@router.post("/synthesize")
def synthesize_speech(req: SynthesisRequest):
    """Synthesize text into WAV audio stream using Kokoro-82M ONNX."""
    try:
        wav_bytes = local_voice_service.synthesize_speech(
            text=req.text,
            voice=req.voice,
            speed=req.speed,
            lang=req.lang,
        )
        return Response(content=wav_bytes, media_type="audio/wav")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Speech synthesis failed: {str(exc)}")