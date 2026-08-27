from __future__ import annotations

import json
import re
from typing import Any
from app.tools.models import ToolResult
from app.tools.registry import ToolRegistry, tool_registry


class ToolOrchestrator:
    """
    Parses LLM responses for tool calls, executes them via ToolRegistry,
    and structures observations for iterative reasoning.
    """

    def __init__(self, registry: ToolRegistry | None = None) -> None:
        self.registry = registry or tool_registry

    def extract_tool_calls(self, response_text: str) -> list[tuple[str, dict[str, Any]]]:
        """
        Extracts tool calls from LLM output across multiple formats:
        1. JSON blocks: ```json {"tool": "...", "arguments": {...}} ```
        2. ReAct format: Action: <tool_name>\nAction Input: <json_args>
        """
        calls: list[tuple[str, dict[str, Any]]] = []

        # 1. JSON blocks with tool/function name
        json_pattern = r"```(?:json)?\s*(\{(?:[^{}]|(?R))*\})\s*```"
        for match in re.finditer(r"```(?:json)?\s*(\{.*?\})\s*```", response_text, re.DOTALL):
            try:
                data = json.loads(match.group(1))
                tool_name = data.get("tool") or data.get("name") or data.get("function")
                args = data.get("arguments") or data.get("parameters") or data.get("args") or {}
                if tool_name and isinstance(tool_name, str):
                    calls.append((tool_name, args))
            except Exception:
                pass

        # 2. ReAct Action / Action Input pattern
        react_pattern = r"(?i)Action:\s*([a-zA-Z0-9_-]+)\s*\nAction Input:\s*(\{.*?\}|[^\n]+)"
        for match in re.finditer(react_pattern, response_text, re.DOTALL):
            tool_name = match.group(1).strip()
            raw_input = match.group(2).strip()
            try:
                args = json.loads(raw_input)
            except Exception:
                args = {"input": raw_input}
            calls.append((tool_name, args))

        return calls

    def execute_calls(
        self,
        calls: list[tuple[str, dict[str, Any]]],
    ) -> list[dict[str, Any]]:
        """
        Executes a batch of extracted tool calls and returns formatted observations.
        """
        results: list[dict[str, Any]] = []

        for tool_name, args in calls:
            res: ToolResult = self.registry.execute(tool_name, **args)
            results.append({
                "tool": tool_name,
                "arguments": args,
                "success": res.success,
                "output": res.output,
                "error": res.error,
                "execution_time_ms": res.execution_time_ms,
            })

        return results

    def format_observations(self, results: list[dict[str, Any]]) -> str:
        """
        Formats tool results into structured observation text for prompt feedback.
        """
        if not results:
            return ""

        blocks = []
        for r in results:
            status = "SUCCESS" if r["success"] else "FAILED"
            content = json.dumps(r["output"], indent=2) if r["output"] is not None else r["error"]
            blocks.append(
                f"OBSERVATION from [{r['tool']}] ({status} in {r['execution_time_ms']}ms):\n{content}"
            )

        return "\n\n".join(blocks)


tool_orchestrator = ToolOrchestrator()
