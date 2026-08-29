from fastapi.testclient import TestClient
from main import app
from app.db.database import create_db_and_tables
from app.mcp.client import mcp_manager
from app.mcp.models import MCPServerConfig
from tests.mcp.test_mcp_client_manager import MockStdioClient

client = TestClient(app)


def setup_module():
    create_db_and_tables()


def test_mcp_routes_full_flow():
    # 1. Register server
    reg_res = client.post(
        "/mcp/servers/register",
        json={"name": "test_server", "command": "python", "args": ["script.py"]},
    )
    assert reg_res.status_code == 200

    # 2. Inject mock client
    cfg = MCPServerConfig(name="test_server", command="python", args=["script.py"])
    mcp_manager._clients["test_server"] = MockStdioClient(cfg)

    # 3. List servers
    list_res = client.get("/mcp/servers")
    assert list_res.status_code == 200
    servers = list_res.json()
    assert any(s["name"] == "test_server" for s in servers)

    # 4. Connect & discover
    conn_res = client.post("/mcp/servers/test_server/connect")
    assert conn_res.status_code == 200
    conn_data = conn_res.json()
    assert conn_data["tools_discovered"] >= 1

    # 5. List tools
    tools_res = client.get("/mcp/tools")
    assert tools_res.status_code == 200
    assert "test_server" in tools_res.json()

    # 6. Call tool
    call_res = client.post(
        "/mcp/tools/call",
        json={
            "server_name": "test_server",
            "tool_name": "sqlite_query",
            "arguments": {"query": "SELECT 1;"},
        },
    )
    assert call_res.status_code == 200
    assert call_res.json()["success"] is True
