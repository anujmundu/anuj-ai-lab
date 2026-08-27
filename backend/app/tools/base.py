from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any
from app.tools.models import ToolDefinition, ToolParameter, ToolResult


class BaseTool(ABC):
    """
    Abstract Base Class for all tools in the platform.
    """

    name: str = ""
    description: str = ""
    parameters: list[ToolParameter] = []

    def get_definition(self) -> ToolDefinition:
        """Returns the full tool definition schema."""
        return ToolDefinition(
            name=self.name,
            description=self.description,
            parameters=self.parameters,
        )

    def execute(self, **kwargs: Any) -> ToolResult:
        """
        Executes the tool with timing and error handling.
        """
        start_time = time.perf_counter()
        try:
            output = self._run(**kwargs)
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            return ToolResult(
                success=True,
                output=output,
                execution_time_ms=round(duration_ms, 2),
            )
        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            return ToolResult(
                success=False,
                output=None,
                error=str(exc),
                execution_time_ms=round(duration_ms, 2),
            )

    @abstractmethod
    def _run(self, **kwargs: Any) -> Any:
        """Core tool logic implemented by concrete tools."""
        raise NotImplementedError
