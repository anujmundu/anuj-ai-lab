from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Any

from app.mcp.client import mcp_manager
from app.mcp.models import MCPServerConfig

router = APIRouter(prefix="/mcp", tags=["Model Context Protocol (MCP)"])


class ToolCallRequest(BaseModel):
    server_name: str
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


@router.get("/servers", response_model=list[dict[str, Any]])
def list_mcp_servers() -> list[dict[str, Any]]:
    """List all configured MCP servers and their active connection states."""
    configs = mcp_manager.get_server_configs()
    results = []
    for cfg in configs:
        client = mcp_manager._clients.get(cfg.name)
        connected = client.is_connected() if client else False
        results.append({
            "name": cfg.name,
            "command": cfg.command,
            "args": cfg.args,
            "connected": connected,
        })
    return results


@router.post("/servers/register", response_model=dict[str, str])
def register_mcp_server(config: MCPServerConfig) -> dict[str, str]:
    """Register a new MCP server configuration."""
    mcp_manager.register_server(config)
    return {"message": f"Server '{config.name}' registered successfully."}


@router.post("/servers/{name}/connect", response_model=dict[str, Any])
def connect_and_discover(name: str) -> dict[str, Any]:
    """Connect to a registered MCP server and discover its available tools."""
    success = mcp_manager.connect_server(name)
    if not success:
        raise HTTPException(status_code=500, detail=f"Failed to connect to MCP server '{name}'.")

    tools = mcp_manager.discover_tools(name)
    return {
        "connected": True,
        "tools_discovered": len(tools),
        "tools": [t.model_dump() for t in tools],
    }


@router.get("/tools", response_model=dict[str, Any])
def list_mcp_tools() -> dict[str, Any]:
    """List all currently imported MCP tools grouped by server name."""
    return mcp_manager.list_all_mcp_tools()


@router.post("/tools/call", response_model=dict[str, Any])
def call_mcp_tool(req: ToolCallRequest) -> dict[str, Any]:
    """Directly execute an MCP tool on a connected server."""
    try:
        res = mcp_manager.call_tool(
            server_name=req.server_name,
            tool_name=req.tool_name,
            arguments=req.arguments,
        )
        return {"success": True, "result": res}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"MCP tool call failed: {str(exc)}")