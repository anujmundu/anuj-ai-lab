from __future__ import annotations

import asyncio
import time
from typing import Any
from app.collaboration.blackboard import AgentBlackboard
from app.collaboration.models import (
    AgentMessage,
    AgentRole,
    CollaborationSession,
    CollaborationStatus,
)
from app.collaboration.roles import (
    coder_agent,
    critic_agent,
    orchestrator_agent,
    researcher_agent,
)


class MultiAgentOrchestrator:
    """
    Coordinates structured multi-agent collaboration sessions with real-time event broadcasting.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, CollaborationSession] = {}
        self._listeners: dict[str, list[asyncio.Queue]] = {}

    def get_session(self, session_id: str) -> CollaborationSession | None:
        return self._sessions.get(session_id)

    def list_sessions(self) -> list[CollaborationSession]:
        return list(self._sessions.values())

    def subscribe(self, session_id: str) -> asyncio.Queue:
        if session_id not in self._listeners:
            self._listeners[session_id] = []
        queue: asyncio.Queue = asyncio.Queue()
        self._listeners[session_id].append(queue)
        return queue

    def unsubscribe(self, session_id: str, queue: asyncio.Queue) -> None:
        if session_id in self._listeners:
            if queue in self._listeners[session_id]:
                self._listeners[session_id].remove(queue)
            if not self._listeners[session_id]:
                del self._listeners[session_id]

    def _broadcast(self, session_id: str, event: dict[str, Any]) -> None:
        if session_id in self._listeners:
            for queue in self._listeners[session_id]:
                queue.put_nowait(event)

    def run_collaboration(
        self,
        goal: str,
        session_id: str | None = None,
    ) -> CollaborationSession:
        """
        Executes a 4-role multi-agent collaboration dialogue.
        """
        session = CollaborationSession(goal=goal)
        if session_id:
            session.session_id = session_id

        self._sessions[session.session_id] = session
        blackboard = AgentBlackboard()

        session.status = CollaborationStatus.IN_PROGRESS
        self._broadcast(session.session_id, {"type": "session_started", "session": session.to_dict()})

        # Round 1: Orchestrator delegates
        msg1 = AgentMessage(
            sender_role=AgentRole.ORCHESTRATOR,
            recipient_role="all",
            content=f"Team, our goal is: '{goal}'. Researcher, please gather domain facts. Coder, prepare the technical solution.",
        )
        session.messages.append(msg1)
        self._broadcast(session.session_id, {"type": "message", "message": msg1.to_dict()})

        # Round 2: Researcher gathers domain context
        research_out = researcher_agent.research(goal, blackboard)
        msg2 = AgentMessage(
            sender_role=AgentRole.RESEARCHER,
            recipient_role="coder",
            content=f"I have extracted the domain knowledge. Summary: {research_out}",
        )
        session.messages.append(msg2)
        self._broadcast(session.session_id, {"type": "message", "message": msg2.to_dict()})

        # Round 3: Coder implements solution
        code_out = coder_agent.develop(goal, blackboard)
        msg3 = AgentMessage(
            sender_role=AgentRole.CODER,
            recipient_role="critic",
            content=f"Technical solution developed. Output: {code_out}",
        )
        session.messages.append(msg3)
        self._broadcast(session.session_id, {"type": "message", "message": msg3.to_dict()})

        # Round 4: Critic reviews
        critique_out = critic_agent.review(blackboard)
        msg4 = AgentMessage(
            sender_role=AgentRole.CRITIC,
            recipient_role="orchestrator",
            content=f"Verification complete: {critique_out}",
        )
        session.messages.append(msg4)
        self._broadcast(session.session_id, {"type": "message", "message": msg4.to_dict()})

        # Round 5: Orchestrator synthesizes consensus
        final_synth = orchestrator_agent.synthesize(goal, blackboard)
        session.final_synthesis = final_synth
        session.blackboard = blackboard.list_entries()
        session.status = CollaborationStatus.COMPLETED
        session.updated_at = time.time()

        msg5 = AgentMessage(
            sender_role=AgentRole.ORCHESTRATOR,
            recipient_role="user",
            content=final_synth,
            message_type="synthesis",
        )
        session.messages.append(msg5)
        self._broadcast(session.session_id, {"type": "session_completed", "session": session.to_dict()})

        return session


multi_agent_orchestrator = MultiAgentOrchestrator()
