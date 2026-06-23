from app.agents.router_agent import router_agent
from app.voice.tts_service import tts_service
from app.voice.whisper_service import whisper_service


class VoiceAgent:

    def process(
        self,
        text: str
    ):

        query = whisper_service.transcribe(
            text
        )

        response = router_agent.route(
            query
        )

        tts_service.speak(
            str(response)
        )

        return response


voice_agent = VoiceAgent()