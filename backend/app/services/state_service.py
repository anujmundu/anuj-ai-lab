from datetime import datetime

from app.state.agent_state import AgentState


class StateService:

    def __init__(self):

        self.state = AgentState()

    def update_state(
        self,
        active_agent: str,
        current_task: str,
        status: str,
        last_response: str
    ):

        self.state.active_agent = active_agent

        self.state.current_task = current_task

        self.state.status = status

        self.state.last_response = last_response

        self.state.timestamp = datetime.now()

    def get_state(self):

        return self.state

    def reset_state(self):

        self.state = AgentState()


state_service = StateService()