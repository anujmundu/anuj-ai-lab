from __future__ import annotations

import io
import os
import soundfile as sf
from typing import Any


class LocalVoiceService:
    """
    100% offline, zero-latency Speech-to-Text (STT) and Text-to-Speech (TTS) engine.
    """

    def __init__(
        self,
        kokoro_onnx_path: str = "models/kokoro/kokoro-v0_19.onnx",
        kokoro_voices_path: str = "models/kokoro/voices.bin",
    ):
        self.kokoro_onnx_path = os.path.abspath(kokoro_onnx_path)
        self.kokoro_voices_path = os.path.abspath(kokoro_voices_path)
        self._kokoro = None
        self._whisper = None

    def _get_tts_engine(self):
        if self._kokoro is None:
            if not os.path.exists(self.kokoro_onnx_path) or not os.path.exists(self.kokoro_voices_path):
                raise FileNotFoundError(f"Kokoro model assets not found at {self.kokoro_onnx_path}")
            from kokoro_onnx import Kokoro
            self._kokoro = Kokoro(self.kokoro_onnx_path, self.kokoro_voices_path)
        return self._kokoro

    def _get_stt_engine(self):
        if self._whisper is None:
            from faster_whisper import WhisperModel
            self._whisper = WhisperModel("base", device="cpu", compute_type="int8")
        return self._whisper

    def transcribe_audio_file(self, audio_file_path: str) -> dict[str, Any]:
        """Transcribe an audio file to text using Faster-Whisper."""
        stt = self._get_stt_engine()
        segments, info = stt.transcribe(audio_file_path, beam_size=5)
        text_segments = [s.text.strip() for s in segments]
        full_text = " ".join(text_segments)
        return {
            "transcription": full_text,
            "language": info.language,
            "language_probability": round(info.language_probability, 2),
            "duration": round(info.duration, 2),
        }

    def transcribe_audio_bytes(self, audio_bytes: bytes) -> dict[str, Any]:
        """Transcribe raw audio bytes by passing a BytesIO buffer."""
        buffer = io.BytesIO(audio_bytes)
        return self.transcribe_audio_file(buffer)

    def synthesize_speech(
        self,
        text: str,
        voice: str = "af_sarah",
        speed: float = 1.0,
        lang: str = "en-us",
    ) -> bytes:
        """Synthesize text into WAV audio bytes using Kokoro-82M ONNX."""
        tts = self._get_tts_engine()
        available_voices = tts.get_voices()
        if voice not in available_voices:
            voice = "af_sarah"

        samples, sample_rate = tts.create(text, voice=voice, speed=speed, lang=lang)

        wav_buffer = io.BytesIO()
        sf.write(wav_buffer, samples, sample_rate, format="WAV")
        wav_buffer.seek(0)
        return wav_buffer.read()


local_voice_service = LocalVoiceService()
