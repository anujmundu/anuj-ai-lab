from __future__ import annotations

import asyncio
from typing import Any, Callable
from app.agents.models import AgentTask


class AgentTaskStore:
    """
    Manages storage, retrieval, and real-time event broadcasting for agent tasks.
    """

    def __init__(self) -> None:
        self._tasks: dict[str, AgentTask] = {}
        self._listeners: dict[str, list[asyncio.Queue]] = {}

    def save(self, task: AgentTask) -> None:
        self._tasks[task.task_id] = task
        self.notify(task.task_id, {"type": "task_updated", "task": task.to_dict()})

    def get(self, task_id: str) -> AgentTask | None:
        return self._tasks.get(task_id)

    def list_tasks(self) -> list[AgentTask]:
        return list(self._tasks.values())

    def subscribe(self, task_id: str) -> asyncio.Queue:
        if task_id not in self._listeners:
            self._listeners[task_id] = []
        queue: asyncio.Queue = asyncio.Queue()
        self._listeners[task_id].append(queue)
        return queue

    def unsubscribe(self, task_id: str, queue: asyncio.Queue) -> None:
        if task_id in self._listeners:
            if queue in self._listeners[task_id]:
                self._listeners[task_id].remove(queue)
            if not self._listeners[task_id]:
                del self._listeners[task_id]

    def notify(self, task_id: str, event: dict[str, Any]) -> None:
        if task_id in self._listeners:
            for queue in self._listeners[task_id]:
                queue.put_nowait(event)

    def clear(self) -> None:
        self._tasks.clear()
        self._listeners.clear()


agent_task_store = AgentTaskStore()
