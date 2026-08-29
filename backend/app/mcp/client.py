from __future__ import annotations

import json
import subprocess
import threading
from typing import Any
from app.mcp.models import (
    MCPServerConfig,
    MCPRequest,
    MCPResponse,
    MCPToolDefinition,
)
from app.mcp.adapter import MCPToolAdapter
from app.tools.registry import tool_registry


class MCPStdioClient:
    """
    Client for communicating with an MCP server process over standard input/output (stdio).
    """

    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.process: subprocess.Popen | None = None
        self._lock = threading.Lock()
        self._request_counter = 0

    def connect(self) -> bool:
        """Starts the MCP server subprocess."""
        if self.process is not None and self.process.poll() is None:
            return True

        try:
            cmd = [self.config.command] + self.config.args
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
            return True
        except Exception:
            return False

    def is_connected(self) -> bool:
        return self.process is not None and self.process.poll() is None

    def send_request(self, method: str, params: dict[str, Any] | None = None) -> MCPResponse:
        """Sends a JSON-RPC 2.0 request over stdin and waits for stdout response."""
        with self._lock:
            self._request_counter += 1
            req_id = self._request_counter
            request = MCPRequest(
                id=req_id,
                method=method,
                params=params or {},
            )

            if not self.is_connected() and not self.connect():
                return MCPResponse(
                    id=req_id,
                    error={"code": -32000, "message": f"Cannot connect to server '{self.config.name}'"},
                )

            req_line = json.dumps(request.model_dump()) + "\n"
            try:
                assert self.process and self.process.stdin and self.process.stdout
                self.process.stdin.write(req_line)
                self.process.stdin.flush()

                res_line = self.process.stdout.readline()
                if not res_line:
                    return MCPResponse(
                        id=req_id,
                        error={"code": -32001, "message": "Server closed stdout stream"},
                    )
                data = json.loads(res_line)
                return MCPResponse(**data)
            except Exception as exc:
                return MCPResponse(
                    id=req_id,
                    error={"code": -32603, "message": f"Internal JSON-RPC error: {str(exc)}"},
                )

    def close(self) -> None:
        if self.process is not None:
            try:
                self.process.terminate()
                self.process.wait(timeout=2.0)
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass
            self.process = None


class MCPClientManager:
    """
    Central manager for multiple MCP servers, tool discovery, and tool registry registration.
    """

    def __init__(self):
        self._servers: dict[str, MCPServerConfig] = {}
        self._clients: dict[str, MCPStdioClient] = {}
        self._tools: dict[str, list[MCPToolDefinition]] = {}

    def register_server(self, config: MCPServerConfig) -> None:
        self._servers[config.name] = config
        self._clients[config.name] = MCPStdioClient(config)

    def get_server_configs(self) -> list[MCPServerConfig]:
        return list(self._servers.values())

    def connect_server(self, server_name: str) -> bool:
        client = self._clients.get(server_name)
        if not client:
            return False
        return client.connect()

    def discover_tools(self, server_name: str) -> list[MCPToolDefinition]:
        """Queries `tools/list` on the server and registers adapter BaseTools into ToolRegistry."""
        client = self._clients.get(server_name)
        if not client:
            return []

        response = client.send_request("tools/list")
        if response.error or not response.result:
            return []

        tools_data = response.result.get("tools", [])
        mcp_tools = []
        for td in tools_data:
            tool_def = MCPToolDefinition(**td)
            mcp_tools.append(tool_def)
            adapter = MCPToolAdapter(server_name=server_name, mcp_tool=tool_def, client_manager=self)
            tool_registry.register(adapter)

        self._tools[server_name] = mcp_tools
        return mcp_tools

    def call_tool(self, server_name: str, tool_name: str, arguments: dict[str, Any]) -> Any:
        client = self._clients.get(server_name)
        if not client:
            raise ValueError(f"Server '{server_name}' is not registered.")

        response = client.send_request(
            "tools/call",
            {"name": tool_name, "arguments": arguments},
        )
        if response.error:
            raise RuntimeError(f"MCP error from '{server_name}': {response.error.get('message')}")
        return response.result

    def list_all_mcp_tools(self) -> dict[str, list[dict[str, Any]]]:
        result = {}
        for s_name, t_list in self._tools.items():
            result[s_name] = [t.model_dump() for t in t_list]
        return result

    def close_all(self) -> None:
        for client in self._clients.values():
            client.close()


mcp_manager = MCPClientManager()
