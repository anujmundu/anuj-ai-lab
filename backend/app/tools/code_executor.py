from __future__ import annotations

import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ExecutionResult:
    stdout: str
    stderr: str
    exit_code: int
    execution_time_ms: float
    timed_out: bool = False


class LocalCodeExecutor:
    """
    Safely executes arbitrary Python code in an isolated subprocess.
    """

    def __init__(
        self,
        default_timeout: float = 5.0,
        max_output_length: int = 10000,
    ) -> None:
        self.default_timeout = default_timeout
        self.max_output_length = max_output_length

    def execute(
        self,
        code: str,
        *,
        timeout: float | None = None,
    ) -> ExecutionResult:
        """
        Execute python code string in an isolated subprocess.
        """
        effective_timeout = timeout if timeout is not None else self.default_timeout
        start_time = time.perf_counter()

        try:
            process = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=effective_timeout,
            )
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            stdout = process.stdout[: self.max_output_length]
            stderr = process.stderr[: self.max_output_length]

            return ExecutionResult(
                stdout=stdout,
                stderr=stderr,
                exit_code=process.returncode,
                execution_time_ms=round(duration_ms, 2),
                timed_out=False,
            )

        except subprocess.TimeoutExpired as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            stdout = (exc.stdout or "")[: self.max_output_length] if isinstance(exc.stdout, str) else ""
            stderr = (exc.stderr or "")[: self.max_output_length] if isinstance(exc.stderr, str) else ""

            return ExecutionResult(
                stdout=stdout,
                stderr=f"Execution timed out after {effective_timeout}s\n{stderr}".strip(),
                exit_code=-1,
                execution_time_ms=round(duration_ms, 2),
                timed_out=True,
            )
        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            return ExecutionResult(
                stdout="",
                stderr=str(exc),
                exit_code=-1,
                execution_time_ms=round(duration_ms, 2),
                timed_out=False,
            )


code_executor = LocalCodeExecutor()
