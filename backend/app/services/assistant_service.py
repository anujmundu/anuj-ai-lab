from app.assistant.autonomous_assistant import (
    autonomous_assistant
)


class AssistantService:

    def execute(
        self,
        goal: str
    ):

        return autonomous_assistant.run(
            goal
        )


assistant_service = AssistantService()