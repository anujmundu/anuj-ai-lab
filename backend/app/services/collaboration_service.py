from app.collaboration.collaboration_manager import (
    collaboration_manager
)


class CollaborationService:

    def execute(
        self,
        goal: str
    ):

        return collaboration_manager.collaborate(
            goal
        )


collaboration_service = CollaborationService()