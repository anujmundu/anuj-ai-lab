from app.agents.models import AgentStep
from app.agents.reflection import ReflectionEvaluator


def test_reflection_successful_step():
    evaluator = ReflectionEvaluator()
    step = AgentStep(
        step_number=1,
        thought="Calculating square root",
        action="calculator",
        action_input={"expression": "sqrt(144)"},
        observation="12.0",
        success=True,
    )

    result = evaluator.evaluate_step(step)
    assert result.is_successful
    assert not result.should_retry
    assert "completed successfully" in result.feedback


def test_reflection_failed_step():
    evaluator = ReflectionEvaluator()
    step = AgentStep(
        step_number=1,
        thought="Running invalid script",
        action="python_interpreter",
        action_input={"code": "broken"},
        observation="NameError: name 'broken' is not defined",
        success=False,
    )

    result = evaluator.evaluate_step(step)
    assert not result.is_successful
    assert result.should_retry
    assert result.suggested_fix is not None
