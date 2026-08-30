import sys
import importlib
import importlib.abc
import importlib.util
from pathlib import Path

_RAG_DIR = Path(__file__).parent

# Map module names to their sub-package
_SUBPACKAGES = [
    "chunking", "embeddings", "retrieval", "context", "prompts",
    "guardrails", "post_processing", "matching", "ingestion",
    "observability", "routing", "pipelines", "cache", "batch",
    "builders", "evaluation", "graph", "intelligence", "production",
    "query", "sharding"
]

_MODULE_MAP = {}
for subpkg in _SUBPACKAGES:
    subpath = _RAG_DIR / subpkg
    if subpath.is_dir():
        for py_file in subpath.glob("*.py"):
            if py_file.name != "__init__.py":
                _MODULE_MAP[py_file.stem] = f"app.rag.{subpkg}.{py_file.stem}"

# Override priority conflicts
_MODULE_MAP["enums"] = "app.rag.ingestion.enums"

class _RAGLegacyModuleFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if fullname.startswith("app.rag."):
            parts = fullname.split(".")
            if len(parts) == 3:
                mod_name = parts[2]
                if mod_name in _MODULE_MAP:
                    target_pkg = _MODULE_MAP[mod_name]
                    return importlib.util.find_spec(target_pkg)
        return None

if not any(isinstance(finder, _RAGLegacyModuleFinder) for finder in sys.meta_path):
    sys.meta_path.insert(0, _RAGLegacyModuleFinder())

def __getattr__(name):
    if name in _MODULE_MAP:
        mod = importlib.import_module(_MODULE_MAP[name])
        return mod
    raise AttributeError(f"module 'app.rag' has no attribute '{name}'")
