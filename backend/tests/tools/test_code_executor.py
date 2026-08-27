from app.tools.code_executor import LocalCodeExecutor, code_executor


def test_code_executor_successful_run():
    code = "print('Result:', 10 + 20)"
    result = code_executor.execute(code)

    assert result.exit_code == 0
    assert "Result: 30" in result.stdout
    assert result.stderr == ""
    assert not result.timed_out
    assert result.execution_time_ms >= 0.0


def test_code_executor_syntax_error():
    code = "def broken(\n"
    result = code_executor.execute(code)

    assert result.exit_code != 0
    assert "SyntaxError" in result.stderr
    assert not result.timed_out


def test_code_executor_timeout():
    executor = LocalCodeExecutor(default_timeout=0.5)
    code = "import time\ntime.sleep(2.0)"
    result = executor.execute(code)

    assert result.timed_out
    assert "timed out" in result.stderr.lower()
