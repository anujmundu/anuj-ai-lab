from __future__ import annotations

import base64
import os
import httpx
from typing import Any
from app.tools.base import BaseTool
from app.tools.models import ToolParameter


class VisionAnalysisTool(BaseTool):
    """
    Tool for analyzing images, architectural diagrams, screenshots, and chart schematics using local Vision LLMs.
    """

    name = "analyze_image"
    description = (
        "Analyzes an image or architectural diagram from a local file path "
        "and answers questions about its visual content, layout, text, and structure."
    )
    parameters = [
        ToolParameter(
            name="image_path",
            type="string",
            description="The local path to the image file to analyze (PNG, JPG, JPEG, WEBP).",
            required=True,
        ),
        ToolParameter(
            name="prompt",
            type="string",
            description="Specific question or instruction for analyzing the image.",
            required=False,
            default="Describe this image in detail and extract all key text and diagram elements.",
        ),
        ToolParameter(
            name="model",
            type="string",
            description="Optional vision model override (e.g. qwen2.5vl:3b, moondream:latest).",
            required=False,
            default="qwen2.5vl:3b",
        ),
    ]

    def __init__(self, ollama_host: str = "http://localhost:11434"):
        self.ollama_host = ollama_host

    def _run(self, **kwargs: Any) -> str:
        image_path = kwargs.get("image_path", "")
        prompt = kwargs.get("prompt", "Describe this image in detail.")
        model = kwargs.get("model", "qwen2.5vl:3b")

        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found at path: {image_path}")

        with open(image_path, "rb") as img_file:
            b64_image = base64.b64encode(img_file.read()).decode("utf-8")

        with httpx.Client(timeout=45.0) as client:
            res = client.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "images": [b64_image],
                    "stream": False,
                },
            )

            if res.status_code == 200:
                data = res.json()
                return data.get("response", "").strip()
            else:
                raise RuntimeError(f"Ollama Vision API error (HTTP {res.status_code}): {res.text}")


vision_analysis_tool = VisionAnalysisTool()
