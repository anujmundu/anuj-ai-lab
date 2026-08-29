from __future__ import annotations

from typing import Any
from app.tools.base import BaseTool
from app.tools.models import ToolParameter
from app.mcp.models import MCPToolDefinition


class MCPToolAdapter(BaseTool):
    """
    Adapts an MCP JSON-RPC 2.0 tool into a native BaseTool usable by ReAct agents and the ToolRegistry.
    """

    def __init__(self, server_name: str, mcp_tool: MCPToolDefinition, client_manager: Any) -> None:
        self.server_name = server_name
        self.mcp_tool = mcp_tool
        self.client_manager = client_manager

        self.name = f"mcp__{server_name}__{mcp_tool.name}"
        self.description = mcp_tool.description or f"MCP tool '{mcp_tool.name}' from server '{server_name}'"

        parsed_params = []
        props = mcp_tool.inputSchema.properties or {}
        reqs = mcp_tool.inputSchema.required or []

        for p_name, p_info in props.items():
            parsed_params.append(
                ToolParameter(
                    name=p_name,
                    type=p_info.get("type", "string"),
                    description=p_info.get("description", ""),
                    required=p_name in reqs,
                    default=p_info.get("default", None),
                )
            )
        self.parameters = parsed_params

    def _run(self, **kwargs: Any) -> Any:
        res = self.client_manager.call_tool(
            server_name=self.server_name,
            tool_name=self.mcp_tool.name,
            arguments=kwargs,
        )
        if isinstance(res, dict) and "content" in res:
            contents = res.get("content", [])
            text_chunks = [c.get("text", "") for c in contents if c.get("type") == "text"]
            return "\n".join(text_chunks) if text_chunks else str(res)
        return str(res)
