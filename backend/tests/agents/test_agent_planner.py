from app.agents.planner import AgentPlanner
from app.tools.calculator_tool import CalculatorTool
from app.tools.code_tool import PythonCodeTool
from app.tools.registry import ToolRegistry


def test_agent_planner_calculation_goal():
    registry = ToolRegistry()
    registry.register(CalculatorTool())

    planner = AgentPlanner(registry=registry)
    plan = planner.plan("Calculate the total revenue from 1500 units at 45 dollars each")

    assert plan.goal.startswith("Calculate")
    assert len(plan.subtasks) >= 2
    assert any(st.tool_name == "calculator" for st in plan.subtasks)


def test_agent_planner_code_goal():
    registry = ToolRegistry()
    registry.register(PythonCodeTool())

    planner = AgentPlanner(registry=registry)
    plan = planner.plan("Write and execute a python script to process dataset records")

    assert len(plan.subtasks) >= 2
    assert any(st.tool_name == "python_interpreter" for st in plan.subtasks)


def test_agent_planner_general_goal():
    registry = ToolRegistry()
    planner = AgentPlanner(registry=registry)
    plan = planner.plan("Explain the key differences between dense and sparse retrieval")

    assert len(plan.subtasks) >= 2
    # Final step is synthesis
    assert "Synthesize" in plan.subtasks[-1].description
