import json
from pathlib import Path


class MemoryService:

    def __init__(self):

        self.memory_file = (
            Path(__file__).parent /
            "memory_store.json"
        )

    def load_memory(self):

        try:

            with open(
                self.memory_file,
                "r",
                encoding="utf-8"
            ) as file:

                return json.load(
                    file
                )

        except:

            return []

    def save_memory(
        self,
        memory
    ):

        with open(
            self.memory_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                memory,
                file,
                indent=4
            )

    def add_message(
        self,
        role: str,
        content
    ):

        memory = self.load_memory()

        memory.append(
            {
                "role": role,
                "content": content
            }
        )

        self.save_memory(
            memory
        )

    def get_memory(self):

        return self.load_memory()

    def get_last_message(self):

        memory = self.load_memory()

        if len(
            memory
        ) == 0:

            return {
                "message": "Memory empty"
            }

        return memory[-1]

    def clear_memory(self):

        self.save_memory(
            []
        )


memory_service = MemoryService()