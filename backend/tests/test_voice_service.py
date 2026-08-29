import io
import soundfile as sf
from app.media.voice_service import local_voice_service


def test_speech_synthesis():
    wav_bytes = local_voice_service.synthesize_speech("Test voice audio.")
    assert len(wav_bytes) > 1000
    # Verify WAV header
    assert wav_bytes[:4] == b"RIFF"

    # Read back with soundfile
    data, samplerate = sf.read(io.BytesIO(wav_bytes))
    assert len(data) > 0
    assert samplerate == 24000
