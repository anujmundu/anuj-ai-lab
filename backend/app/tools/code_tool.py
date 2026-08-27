from __future__ import annotations

from typing import Any
from app.tools.base import BaseTool
from app.tools.code_executor import code_executor
from app.tools.models import ToolParameter


class PythonCodeTool(BaseTool):
    """
    Executes Python code in an isolated subprocess sandbox.
    """

    name = "python_interpreter"
    description = "Executes Python 3 code in an isolated sandbox environment and returns stdout and stderr."
    parameters = [
        ToolParameter(
            name="code",
            type="string",
            description="The Python code to execute.",
            required=True,
        ),
        ToolParameter(
            name="timeout",
            type="number",
            description="Maximum execution timeout in seconds (default 5.0).",
            required=False,
            default=5.0,
        ),
    ]

    def _run(self, code: str = "", timeout: float = 5.0, **kwargs: Any) -> dict[str, Any]:
        if not code or not code.strip():
            raise ValueError("Code snippet cannot be empty")

        res = code_executor.execute(code, timeout=timeout)
        return {
            "stdout": res.stdout,
            "stderr": res.stderr,
            "exit_code": res.exit_code,
            "timed_out": res.timed_out,
            "execution_time_ms": res.execution_time_ms,
        }


python_code_tool = PythonCodeTool()
