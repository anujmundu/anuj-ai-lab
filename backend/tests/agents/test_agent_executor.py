from app.agents.executor import AgentExecutor
from app.agents.models import TaskStatus
from app.agents.planner import AgentPlanner
from app.agents.reflection import ReflectionEvaluator
from app.agents.task_store import AgentTaskStore
from app.tools.calculator_tool import CalculatorTool
from app.tools.registry import ToolRegistry


def test_agent_executor_end_to_end():
    registry = ToolRegistry()
    registry.register(CalculatorTool())

    store = AgentTaskStore()
    planner = AgentPlanner(registry=registry)
    evaluator = ReflectionEvaluator()

    executor = AgentExecutor(
        planner=planner,
        evaluator=evaluator,
        registry=registry,
        store=store,
    )

    task = executor.run_task(goal="Calculate 50 * 4")

    assert task.status == TaskStatus.COMPLETED
    assert len(task.steps) >= 2
    assert task.result is not None
    assert "Goal achieved" in task.result
    assert store.get(task.task_id) is not None
