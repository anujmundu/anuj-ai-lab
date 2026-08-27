from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TaskStatus(str, Enum):
    PENDING = "pending"
    PLANNING = "planning"
    RUNNING = "running"
    REFLECTING = "reflecting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(slots=True)
class SubTask:
    id: str
    description: str
    tool_name: str | None = None
    dependencies: list[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "tool_name": self.tool_name,
            "dependencies": self.dependencies,
            "status": self.status.value,
            "result": self.result,
        }


@dataclass(slots=True)
class AgentStep:
    step_number: int
    thought: str
    action: str
    action_input: dict[str, Any] = field(default_factory=dict)
    observation: Any = None
    reflection: str = ""
    success: bool = True
    execution_time_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_number": self.step_number,
            "thought": self.thought,
            "action": self.action,
            "action_input": self.action_input,
            "observation": self.observation,
            "reflection": self.reflection,
            "success": self.success,
            "execution_time_ms": self.execution_time_ms,
        }


@dataclass(slots=True)
class AgentPlan:
    goal: str
    subtasks: list[SubTask] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "goal": self.goal,
            "subtasks": [st.to_dict() for st in self.subtasks],
        }


@dataclass(slots=True)
class AgentTask:
    task_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    goal: str = ""
    status: TaskStatus = TaskStatus.PENDING
    plan: AgentPlan | None = None
    steps: list[AgentStep] = field(default_factory=list)
    result: str | None = None
    error: str | None = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "goal": self.goal,
            "status": self.status.value,
            "plan": self.plan.to_dict() if self.plan else None,
            "steps": [s.to_dict() for s in self.steps],
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
