from __future__ import annotations

import ast
import math
import operator
from typing import Any
from app.tools.base import BaseTool
from app.tools.models import ToolParameter


class CalculatorTool(BaseTool):
    """
    Safely evaluates mathematical and statistical expressions without arbitrary code execution.
    """

    name = "calculator"
    description = "Evaluates a mathematical expression and returns the numerical result."
    parameters = [
        ToolParameter(
            name="expression",
            type="string",
            description="The mathematical expression to evaluate, e.g. '(15 * 4) / 2 + math.sqrt(144)'",
            required=True,
        )
    ]

    _SAFE_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.BitXor: operator.pow,  # Math caret notation support (e.g. 2^3 -> 8)
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    _SAFE_FUNCTIONS = {
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "log10": math.log10,
        "exp": math.exp,
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "sum": sum,
    }

    _SAFE_CONSTANTS = {
        "pi": math.pi,
        "e": math.e,
    }

    def _eval_node(self, node: ast.AST) -> Any:
        if isinstance(node, ast.Constant):
            return node.value

        if isinstance(node, ast.Name):
            if node.id in self._SAFE_CONSTANTS:
                return self._SAFE_CONSTANTS[node.id]
            if node.id in self._SAFE_FUNCTIONS:
                return self._SAFE_FUNCTIONS[node.id]
            raise ValueError(f"Unsupported variable or identifier: {node.id}")

        if isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name) and node.value.id == "math":
                if node.attr in self._SAFE_FUNCTIONS:
                    return self._SAFE_FUNCTIONS[node.attr]
                if node.attr in self._SAFE_CONSTANTS:
                    return self._SAFE_CONSTANTS[node.attr]
            raise ValueError(f"Unsupported attribute access: {ast.dump(node)}")

        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type in self._SAFE_OPERATORS:
                operand = self._eval_node(node.operand)
                return self._SAFE_OPERATORS[op_type](operand)
            raise ValueError(f"Unsupported unary operator: {op_type}")

        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type in self._SAFE_OPERATORS:
                left = self._eval_node(node.left)
                right = self._eval_node(node.right)
                return self._SAFE_OPERATORS[op_type](left, right)
            raise ValueError(f"Unsupported binary operator: {op_type}")

        if isinstance(node, ast.Call):
            func = self._eval_node(node.func)
            args = [self._eval_node(arg) for arg in node.args]
            return func(*args)

        raise ValueError(f"Unsupported syntax expression: {type(node).__name__}")

    def _run(self, expression: str = "", **kwargs: Any) -> str:
        if not expression or not expression.strip():
            raise ValueError("Expression cannot be empty")

        clean_expr = expression.strip().replace(",", "")
        if "=" in clean_expr:
            clean_expr = clean_expr.split("=")[0].strip()

        parsed = ast.parse(clean_expr, mode="eval")
        result = self._eval_node(parsed.body)
        return str(result)

    def calculate(self, expression: str) -> str:
        """Backwards compatibility helper."""
        res = self.execute(expression=expression)
        return str(res.output) if res.success else "Invalid expression"


calculator_tool = CalculatorTool()