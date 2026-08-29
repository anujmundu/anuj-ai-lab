from app.mcp.client import MCPClientManager
from app.mcp.models import MCPServerConfig, MCPResponse
from app.tools.registry import tool_registry


class MockStdioClient:
    def __init__(self, config: MCPServerConfig):
        self.config = config

    def connect(self) -> bool:
        return True

    def is_connected(self) -> bool:
        return True

    def send_request(self, method: str, params: dict | None = None) -> MCPResponse:
        if method == "tools/list":
            return MCPResponse(
                id=1,
                result={
                    "tools": [
                        {
                            "name": "sqlite_query",
                            "description": "Executes a SQL query.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {"query": {"type": "string"}},
                                "required": ["query"],
                            },
                        }
                    ]
                },
            )
        elif method == "tools/call":
            return MCPResponse(
                id=2,
                result={"content": [{"type": "text", "text": "Rows: [(1, 'Anuj')]"}]},
            )
        return MCPResponse(id=0, result={})

    def close(self) -> None:
        pass


def test_mcp_client_manager_flow():
    mgr = MCPClientManager()
    cfg = MCPServerConfig(name="database_server", command="python", args=["db_server.py"])
    mgr.register_server(cfg)

    # Inject mock client
    mgr._clients["database_server"] = MockStdioClient(cfg)

    # Discover tools
    tools = mgr.discover_tools("database_server")
    assert len(tools) == 1
    assert tools[0].name == "sqlite_query"

    # Verify adapter registered in tool_registry
    tool_in_registry = tool_registry.get("mcp__database_server__sqlite_query")
    assert tool_in_registry is not None

    # Call tool
    res = mgr.call_tool("database_server", "sqlite_query", {"query": "SELECT * FROM users;"})
    assert "content" in res
