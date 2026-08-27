from app.rag.graph.graph_store import KnowledgeGraphStore
from app.rag.graph.models import Relation
from app.tools.calculator_tool import CalculatorTool
from app.tools.file_system_tool import FileSystemTool
from app.tools.graph_query_tool import KnowledgeGraphQueryTool
from app.tools.orchestrator import ToolOrchestrator
from app.tools.registry import ToolRegistry


def test_calculator_tool():
    calc = CalculatorTool()

    # Basic arithmetic
    res = calc.execute(expression="(12 * 5) + 40 / 2")
    assert res.success
    assert float(res.output) == 80.0

    # Math functions and constants
    res2 = calc.execute(expression="sqrt(144) + pi * 0")
    assert res2.success
    assert float(res2.output) == 12.0

    # Invalid expression
    res3 = calc.execute(expression="invalid_identifier + 1")
    assert not res3.success


def test_file_system_tool(tmp_path):
    fs = FileSystemTool()
    test_file = tmp_path / "note.txt"

    # Write
    write_res = fs.execute(action="write", path=str(test_file), content="Hello, Tool System!")
    assert write_res.success

    # Read
    read_res = fs.execute(action="read", path=str(test_file))
    assert read_res.success
    assert read_res.output == "Hello, Tool System!"

    # Exists
    exists_res = fs.execute(action="exists", path=str(test_file))
    assert exists_res.success
    assert exists_res.output["exists"]
    assert exists_res.output["is_file"]

    # List
    list_res = fs.execute(action="list", path=str(tmp_path))
    assert list_res.success
    assert "note.txt" in list_res.output["items"]


def test_graph_query_tool(monkeypatch):
    store = KnowledgeGraphStore()
    store.add_relation(Relation(source="FastAPI", relation="uses", target="Pydantic"))
    store.add_relation(Relation(source="Pydantic", relation="validates", target="ToolSchema"))

    import app.tools.graph_query_tool as gqt_module
    monkeypatch.setattr(gqt_module, "knowledge_graph_store", store)

    tool = KnowledgeGraphQueryTool()

    # Neighbors
    res_neighbors = tool.execute(query_type="neighbors", entity_name="FastAPI")
    assert res_neighbors.success
    assert len(res_neighbors.output) >= 1
    assert res_neighbors.output[0]["target"] == "Pydantic"

    # Path
    res_path = tool.execute(query_type="path", entity_name="FastAPI", target_entity="ToolSchema")
    assert res_path.success
    assert res_path.output["paths_found"] == 1


def test_tool_orchestrator():
    registry = ToolRegistry()
    registry.register(CalculatorTool())

    orchestrator = ToolOrchestrator(registry=registry)

    # ReAct pattern
    llm_response = (
        "I need to compute the area.\n"
        "Action: calculator\n"
        "Action Input: {\"expression\": \"25 * 4\"}\n"
    )
    calls = orchestrator.extract_tool_calls(llm_response)
    assert len(calls) == 1
    assert calls[0][0] == "calculator"

    # Execution
    results = orchestrator.execute_calls(calls)
    assert len(results) == 1
    assert results[0]["success"]
    assert float(results[0]["output"]) == 100.0

    # Observation formatting
    observation = orchestrator.format_observations(results)
    assert "OBSERVATION from [calculator] (SUCCESS" in observation
    assert "100" in observation

