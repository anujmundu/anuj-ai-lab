import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

MEMORY_FILE = BASE_DIR / "data" / "memory.json"


class ConversationMemory:

    def load_memory(self):

        if not MEMORY_FILE.exists():
            return []

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    def save_interaction(
        self,
        user_input: str,
        assistant_response: str
    ):

        memory = self.load_memory()

        memory.append(
            {
                "user": user_input,
                "assistant": assistant_response
            }
        )

        with open(
            MEMORY_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                memory,
                file,
                indent=4
            )

    def recent_context(
        self,
        n: int = 3
    ):

        memory = self.load_memory()

        recent = memory[-n:]

        context = ""

        for item in recent:

            context += (
                f"User: {item['user']}\n"
                f"Assistant: {item['assistant']}\n\n"
            )

        return context


conversation_memory = ConversationMemory()