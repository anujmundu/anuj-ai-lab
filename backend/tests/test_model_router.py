from app.rag.routing.model_router import (
    DynamicModelRouter,
    TaskType,
)


def test_infer_task_type_code():
    router = DynamicModelRouter()
    assert router.infer_task_type("def calculate_fibonacci(n):") == TaskType.CODE_EXECUTION
    assert router.infer_task_type("debug this python function") == TaskType.CODE_EXECUTION


def test_infer_task_type_deep_reasoning():
    router = DynamicModelRouter()
    assert router.infer_task_type("prove step by step why this algorithm is O(n log n)") == TaskType.DEEP_REASONING
    assert router.infer_task_type("calculate the mathematical derivative") == TaskType.DEEP_REASONING


def test_infer_task_type_fast():
    router = DynamicModelRouter()
    assert router.infer_task_type("hello") == TaskType.FAST_INTENT
    assert router.infer_task_type("hi there") == TaskType.FAST_INTENT


def test_infer_task_type_vision():
    router = DynamicModelRouter()
    assert router.infer_task_type("what is this?", has_image=True) == TaskType.VISION_OCR


def test_route_model_auto_and_override():
    router = DynamicModelRouter()
    res = router.route_model("write a python script to parse logs")
    assert res.task_type == TaskType.CODE_EXECUTION
    assert res.selected_model in router.preferred_models[TaskType.CODE_EXECUTION]
    assert not res.is_override

    # Test override
    res_override = router.route_model("write python", user_override_model="deepseek-r1:8b")
    assert res_override.selected_model == "deepseek-r1:8b"
    assert res_override.is_override
