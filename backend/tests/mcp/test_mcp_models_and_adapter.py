from app.mcp.models import MCPToolDefinition, MCPToolParameterSchema
from app.mcp.adapter import MCPToolAdapter


class MockMCPClientManager:
    def call_tool(self, server_name: str, tool_name: str, arguments: dict):
        return {"content": [{"type": "text", "text": f"Output for {tool_name} with {arguments}"}]}


def test_mcp_tool_adapter():
    mcp_tool = MCPToolDefinition(
        name="read_file",
        description="Reads a file from local filesystem.",
        inputSchema=MCPToolParameterSchema(
            type="object",
            properties={
                "path": {"type": "string", "description": "Path to the file"},
                "limit": {"type": "integer", "description": "Max bytes", "default": 1000},
            },
            required=["path"],
        ),
    )

    manager = MockMCPClientManager()
    adapter = MCPToolAdapter(server_name="filesystem_server", mcp_tool=mcp_tool, client_manager=manager)

    assert adapter.name == "mcp__filesystem_server__read_file"
    assert "Reads a file" in adapter.description

    # Test parameters conversion
    param_names = [p.name for p in adapter.parameters]
    assert "path" in param_names
    assert "limit" in param_names

    # Test execution
    res = adapter.execute(path="test.txt", limit=50)
    assert res.success
    assert "Output for read_file" in str(res.output)
