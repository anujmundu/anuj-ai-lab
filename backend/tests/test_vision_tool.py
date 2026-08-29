from app.tools.vision_tool import VisionAnalysisTool


def test_vision_tool_schema():
    tool = VisionAnalysisTool()
    assert tool.name == "analyze_image"
    defn = tool.get_definition()
    assert defn.name == "analyze_image"
    param_names = [p.name for p in defn.parameters]
    assert "image_path" in param_names
    assert "prompt" in param_names


def test_vision_tool_missing_file():
    tool = VisionAnalysisTool()
    res = tool.execute(image_path="non_existent_image_12345.png")
    assert not res.success
    assert "not found" in (res.error or "").lower()
