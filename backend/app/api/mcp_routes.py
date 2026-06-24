from fastapi import APIRouter

from app.mcp.tool_registry import tool_registry
from app.mcp.mcp_server import mcp_server


router = APIRouter()


@router.get("/mcp/tools")
def tools():

    return {
        "tools":
        tool_registry.list_tools()
    }


@router.get("/mcp/execute")
def execute(
    tool: str,
    query: str = ""
):

    return mcp_server.execute(
        tool,
        query
    )