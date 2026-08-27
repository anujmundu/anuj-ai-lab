from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from app.tools.base import BaseTool
from app.tools.models import ToolParameter


class FileSystemTool(BaseTool):
    """
    Safely reads, writes, and lists files within the workspace.
    """

    name = "file_system"
    description = "Provides file system operations: read, write, list, and inspect files."
    parameters = [
        ToolParameter(
            name="action",
            type="string",
            description="The operation to perform: 'read', 'write', 'list', 'exists'",
            required=True,
        ),
        ToolParameter(
            name="path",
            type="string",
            description="The relative or absolute file or directory path.",
            required=True,
        ),
        ToolParameter(
            name="content",
            type="string",
            description="Content to write when action is 'write'.",
            required=False,
            default="",
        ),
    ]

    def _resolve_safe_path(self, path_str: str) -> Path:
        target = Path(path_str).resolve()
        return target

    def _run(
        self,
        action: str = "",
        path: str = "",
        content: str = "",
        **kwargs: Any,
    ) -> Any:
        if not action or not path:
            raise ValueError("Both 'action' and 'path' parameters are required")

        safe_path = self._resolve_safe_path(path)

        if action == "read":
            if not safe_path.exists():
                raise FileNotFoundError(f"File not found: {path}")
            if safe_path.is_dir():
                raise IsADirectoryError(f"Path is a directory: {path}")
            return safe_path.read_text(encoding="utf-8", errors="replace")

        elif action == "write":
            safe_path.parent.mkdir(parents=True, exist_ok=True)
            safe_path.write_text(content, encoding="utf-8")
            return f"Successfully written {len(content)} characters to {path}"

        elif action == "list":
            if not safe_path.exists():
                raise FileNotFoundError(f"Directory not found: {path}")
            if not safe_path.is_dir():
                raise NotADirectoryError(f"Path is not a directory: {path}")
            items = [item.name for item in safe_path.iterdir()]
            return {"directory": str(safe_path), "items": sorted(items)}

        elif action == "exists":
            return {"path": path, "exists": safe_path.exists(), "is_file": safe_path.is_file(), "is_dir": safe_path.is_dir()}

        else:
            raise ValueError(f"Unknown action '{action}'. Supported actions: 'read', 'write', 'list', 'exists'")


file_system_tool = FileSystemTool()
