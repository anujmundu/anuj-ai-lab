from __future__ import annotations

from typing import Any
from app.tools.base import BaseTool
from app.tools.models import ToolResult


class ToolRegistry:
    """
    Central repository for registering, inspecting, and executing tools.
    """

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Register a tool instance."""
        if not tool.name:
            raise ValueError("Tool name cannot be empty")
        self._tools[tool.name] = tool

    def unregister(self, tool_name: str) -> bool:
        """Unregister a tool by name."""
        return self._tools.pop(tool_name, None) is not None

    def get(self, tool_name: str) -> BaseTool | None:
        """Retrieve a registered tool by name."""
        return self._tools.get(tool_name)

    def list_tools(self) -> list[str]:
        """List names of all registered tools."""
        return list(self._tools.keys())

    def get_schemas(self) -> list[dict[str, Any]]:
        """Get OpenAI / Ollama compatible function schemas for all tools."""
        return [tool.get_definition().to_openai_schema() for tool in self._tools.values()]

    def execute(self, tool_name: str, **kwargs: Any) -> ToolResult:
        """Execute a registered tool by name."""
        tool = self.get(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                output=None,
                error=f"Tool '{tool_name}' not found in registry",
            )
        return tool.execute(**kwargs)

    def clear(self) -> None:
        """Clear all registered tools."""
        self._tools.clear()


tool_registry = ToolRegistry()
