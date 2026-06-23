import pyttsx3


class TTSService:

    def speak(
        self,
        text: str
    ):

        try:

            engine = pyttsx3.init()

            engine.say(
                text
            )

            engine.runAndWait()

            engine.stop()

        except Exception as e:

            print(
                f"TTS Error: {e}"
            )


tts_service = TTSService()