from app.tools.base import BaseTool
from app.tools.models import ToolParameter, ToolResult
from app.tools.registry import ToolRegistry


class DummyTool(BaseTool):
    name = "dummy_echo"
    description = "Echoes back the input message."
    parameters = [
        ToolParameter(
            name="message",
            type="string",
            description="The message to echo",
            required=True,
        )
    ]

    def _run(self, message: str = "", **kwargs):
        if not message:
            raise ValueError("message cannot be empty")
        return f"Echo: {message}"


def test_tool_registry_registration_and_lookup():
    registry = ToolRegistry()
    tool = DummyTool()

    registry.register(tool)
    assert registry.list_tools() == ["dummy_echo"]
    assert registry.get("dummy_echo") is tool


def test_tool_registry_schema_generation():
    registry = ToolRegistry()
    registry.register(DummyTool())

    schemas = registry.get_schemas()
    assert len(schemas) == 1
    assert schemas[0]["type"] == "function"
    assert schemas[0]["function"]["name"] == "dummy_echo"
    assert "message" in schemas[0]["function"]["parameters"]["properties"]
    assert "message" in schemas[0]["function"]["parameters"]["required"]


def test_tool_registry_successful_execution():
    registry = ToolRegistry()
    registry.register(DummyTool())

    result: ToolResult = registry.execute("dummy_echo", message="Hello World")
    assert result.success
    assert result.output == "Echo: Hello World"
    assert result.error is None
    assert result.execution_time_ms >= 0.0


def test_tool_registry_error_handling():
    registry = ToolRegistry()
    registry.register(DummyTool())

    # Empty message raises error in DummyTool._run
    result: ToolResult = registry.execute("dummy_echo", message="")
    assert not result.success
    assert result.output is None
    assert "message cannot be empty" in result.error


def test_tool_registry_nonexistent_tool():
    registry = ToolRegistry()
    result = registry.execute("unknown_tool")
    assert not result.success
    assert "not found in registry" in result.error
