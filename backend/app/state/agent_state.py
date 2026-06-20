from datetime import datetime

from pydantic import BaseModel


class AgentState(BaseModel):

    active_agent: str = "none"

    current_task: str = ""

    status: str = "idle"

    last_response: str = ""

    timestamp: datetime = datetime.now()