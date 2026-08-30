from __future__ import annotations

import re
from app.agents.models import AgentPlan, SubTask, TaskStatus
from app.tools.registry import ToolRegistry, tool_registry


class AgentPlanner:
    """
    Decomposes high-level user goals into structured subtask DAGs.
    """

    def __init__(self, registry: ToolRegistry | None = None) -> None:
        self.registry = registry or tool_registry

    def plan(self, goal: str) -> AgentPlan:
        """
        Decomposes a user goal into an ordered sequence of subtasks.
        """
        if not goal or not goal.strip():
            raise ValueError("Goal cannot be empty")

        available_tools = self.registry.list_tools()
        subtasks: list[SubTask] = []

        # Analyze keywords in goal to select appropriate tools
        goal_lower = goal.lower()

        # Check for file system operations
        if any(w in goal_lower for w in ["file", "directory", "folder", "main.py", "read file", "write file", "save to", "list dir", "exists", "inspect"]):
            if "file_system" in available_tools:
                subtasks.append(
                    SubTask(
                        id=f"subtask_{len(subtasks) + 1}",
                        description=f"Perform file system operations for: {goal}",
                        tool_name="file_system",
                    )
                )

        # Check for code execution
        elif any(w in goal_lower for w in ["python", "code", "script", "program", "execute python", "run code"]):
            if "python_interpreter" in available_tools:
                subtasks.append(
                    SubTask(
                        id=f"subtask_{len(subtasks) + 1}",
                        description=f"Execute Python code required for: {goal}",
                        tool_name="python_interpreter",
                    )
                )

        # Check for calculation (explicit math words, avoiding '/' which appears in paths)
        elif any(w in goal_lower for w in ["calculate", "compute", "arithmetic", "sum", "multiply", "divide", "compound", "interest", "rate", "math", "percentage", "formula", "sqrt"]):
            if "calculator" in available_tools:
                subtasks.append(
                    SubTask(
                        id=f"subtask_{len(subtasks) + 1}",
                        description=f"Calculate numerical values required for: {goal}",
                        tool_name="calculator",
                    )
                )

        # Check for knowledge graph query
        if any(w in goal_lower for w in ["relationship", "path between", "graph", "how is", "connected to"]):
            if "knowledge_graph_query" in available_tools:
                subtasks.append(
                    SubTask(
                        id=f"subtask_{len(subtasks) + 1}",
                        description=f"Query knowledge graph relationships for: {goal}",
                        tool_name="knowledge_graph_query",
                    )
                )

        # Default fallback subtask if no specific keywords matched
        if not subtasks:
            subtasks.append(
                SubTask(
                    id="subtask_1",
                    description=f"Execute reasoning and information gathering for: {goal}",
                    tool_name=None,
                )
            )

        # Final synthesis subtask
        subtasks.append(
            SubTask(
                id=f"subtask_{len(subtasks) + 1}",
                description=f"Synthesize final verified answer for: {goal}",
                tool_name=None,
                dependencies=[st.id for st in subtasks],
            )
        )

        return AgentPlan(goal=goal, subtasks=subtasks)


agent_planner = AgentPlanner()
