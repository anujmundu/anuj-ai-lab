from __future__ import annotations

import httpx
from enum import Enum
from typing import Any
from pydantic import BaseModel


class TaskType(str, Enum):
    FAST_INTENT = "fast_intent"
    CODE_EXECUTION = "code_execution"
    DEEP_REASONING = "deep_reasoning"
    VISION_OCR = "vision_ocr"
    GENERAL_CHAT = "general_chat"


class ModelRecommendation(BaseModel):
    task_type: TaskType
    selected_model: str
    is_override: bool = False
    fallback_used: bool = False


class DynamicModelRouter:
    """
    Intelligent dynamic router that maps tasks to the optimal locally installed Ollama model.
    """

    def __init__(self, ollama_host: str = "http://localhost:11434"):
        self.ollama_host = ollama_host
        self.preferred_models: dict[TaskType, list[str]] = {
            TaskType.FAST_INTENT: ["qwen2.5:1.5b", "llama3.2:3b", "qwen3.5:9b"],
            TaskType.CODE_EXECUTION: ["qwen2.5-coder:7b", "qwen3.5:9b", "gemma2:9b"],
            TaskType.DEEP_REASONING: ["deepseek-r1:8b", "deepseek-r1:1.5b", "gemma2:9b", "qwen3.5:9b"],
            TaskType.VISION_OCR: ["qwen2.5vl:3b", "moondream:latest", "llava:7b-v1.6-mistral-q5_1", "llava:latest"],
            TaskType.GENERAL_CHAT: ["qwen3.5:9b", "gemma2:9b", "llama3.2:3b", "qwen2.5:1.5b"],
        }

    def get_installed_models(self) -> list[str]:
        """Fetch list of all models currently installed in local Ollama."""
        try:
            with httpx.Client(timeout=3.0) as client:
                res = client.get(f"{self.ollama_host}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    return [m["name"] for m in data.get("models", [])]
        except Exception:
            pass
        return ["qwen2.5:1.5b", "qwen3.5:9b", "llama3.2:3b", "qwen2.5-coder:7b", "deepseek-r1:8b", "qwen2.5vl:3b"]

    def infer_task_type(self, query: str, has_image: bool = False) -> TaskType:
        """Heuristically determines the task category based on query characteristics."""
        if has_image:
            return TaskType.VISION_OCR

        q_lower = query.lower()

        # Code keywords
        if any(kw in q_lower for kw in ["def ", "class ", "function", "python", "code", "debug", "refactor", "import "]):
            return TaskType.CODE_EXECUTION

        # Deep reasoning / math keywords
        if any(kw in q_lower for kw in ["calculate", "step by step", "prove", "derive", "solve", "math", "why does", "analyze complexity"]):
            return TaskType.DEEP_REASONING

        # Fast intent keywords
        if len(query.split()) <= 4 or any(kw in q_lower for kw in ["hello", "hi", "summarize in 1 word", "yes or no"]):
            return TaskType.FAST_INTENT

        return TaskType.GENERAL_CHAT

    def route_model(
        self,
        query: str = "",
        task_type: TaskType | None = None,
        has_image: bool = False,
        user_override_model: str | None = None,
    ) -> ModelRecommendation:
        """Determines the optimal model to execute the given query or task."""
        installed = self.get_installed_models()

        if user_override_model:
            return ModelRecommendation(
                task_type=task_type or self.infer_task_type(query, has_image),
                selected_model=user_override_model,
                is_override=True,
                fallback_used=False,
            )

        inferred_type = task_type or self.infer_task_type(query, has_image)
        candidates = self.preferred_models.get(inferred_type, ["qwen3.5:9b"])

        for candidate in candidates:
            # Check exact match or base tag match (e.g. 'qwen2.5:1.5b' in 'qwen2.5:1.5b')
            if any(candidate in m for m in installed):
                return ModelRecommendation(
                    task_type=inferred_type,
                    selected_model=candidate,
                    is_override=False,
                    fallback_used=False,
                )

        # Fallback to first installed or default
        fallback = installed[0] if installed else "qwen2.5:1.5b"
        return ModelRecommendation(
            task_type=inferred_type,
            selected_model=fallback,
            is_override=False,
            fallback_used=True,
        )


dynamic_model_router = DynamicModelRouter()
