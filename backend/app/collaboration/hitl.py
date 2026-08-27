from __future__ import annotations

from dataclasses import dataclass, field
import time


@dataclass(slots=True)
class ApprovalRequest:
    session_id: str
    action_description: str
    is_decided: bool = False
    is_approved: bool = False
    requested_at: float = field(default_factory=time.time)
    decided_at: float | None = None


class HumanInTheLoopGate:
    """
    Manages interactive human-in-the-loop approvals for sensitive agent actions.
    """

    def __init__(self) -> None:
        self._requests: dict[str, ApprovalRequest] = {}

    def request_approval(self, session_id: str, action_description: str) -> ApprovalRequest:
        req = ApprovalRequest(
            session_id=session_id,
            action_description=action_description,
        )
        self._requests[session_id] = req
        return req

    def submit_decision(self, session_id: str, approved: bool) -> ApprovalRequest:
        if session_id not in self._requests:
            raise KeyError(f"No pending approval request found for session {session_id}")
        req = self._requests[session_id]
        req.is_decided = True
        req.is_approved = approved
        req.decided_at = time.time()
        return req

    def get_status(self, session_id: str) -> ApprovalRequest | None:
        return self._requests.get(session_id)

    def is_approved(self, session_id: str) -> bool:
        req = self._requests.get(session_id)
        return req is not None and req.is_decided and req.is_approved


hitl_gate = HumanInTheLoopGate()
