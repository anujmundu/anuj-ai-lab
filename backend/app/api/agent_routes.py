from __future__ import annotations

import asyncio
import json
from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.agents.executor import agent_executor
from app.agents.models import AgentTask, TaskStatus
from app.agents.task_store import agent_task_store

router = APIRouter(prefix="/agents", tags=["Agents"])


class CreateTaskRequest(BaseModel):
    goal: str = Field(..., description="The high-level goal for the autonomous agent to solve")
    max_steps: int = Field(default=8, ge=1, le=20, description="Maximum execution steps")


@router.post("/tasks", response_model=dict)
def create_agent_task(
    request: CreateTaskRequest,
    background_tasks: BackgroundTasks,
) -> dict:
    """Create and start an autonomous agent task in background worker."""
    task = AgentTask(goal=request.goal)
    agent_task_store.save(task)

    background_tasks.add_task(
        agent_executor.run_task,
        goal=request.goal,
        task_id=task.task_id,
        max_steps=request.max_steps,
    )

    return {
        "task_id": task.task_id,
        "goal": task.goal,
        "status": task.status.value,
        "created_at": task.created_at,
    }


@router.get("/tasks/{task_id}", response_model=dict)
def get_agent_task(task_id: str) -> dict:
    """Get the current execution state, plan, steps, and result of an agent task."""
    task = agent_task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Agent task not found")
    return task.to_dict()


@router.get("/tasks", response_model=list[dict])
def list_agent_tasks() -> list[dict]:
    """List all registered agent tasks."""
    tasks = agent_task_store.list_tasks()
    return [t.to_dict() for t in tasks]


@router.get("/tasks/{task_id}/stream")
async def stream_agent_task_progress(task_id: str):
    """Real-time Server-Sent Events (SSE) stream of agent thought and execution steps."""
    task = agent_task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Agent task not found")

    queue = agent_task_store.subscribe(task_id)

    async def event_generator():
        try:
            # Yield initial state
            yield f"data: {json.dumps({'type': 'init', 'task': task.to_dict()})}\n\n"

            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=1.0)
                    yield f"data: {json.dumps(event)}\n\n"

                    # Stop streaming once task completes or fails
                    task_data = event.get("task", {})
                    status = task_data.get("status")
                    if status in {TaskStatus.COMPLETED.value, TaskStatus.FAILED.value, TaskStatus.CANCELLED.value}:
                        break
                except asyncio.TimeoutError:
                    # Keep-alive heartbeat
                    yield ": heartbeat\n\n"
                    current = agent_task_store.get(task_id)
                    if current and current.status in {TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED}:
                        break
        finally:
            agent_task_store.unsubscribe(task_id, queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
