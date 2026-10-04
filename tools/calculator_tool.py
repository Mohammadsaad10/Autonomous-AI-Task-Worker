"""
Calculator Tool - Safe mathematical expression evaluator.
"""
from __future__ import annotations

import ast
import operator
import math

from .base import BaseTool, ToolResult


class CalculatorTool(BaseTool):
    name = "calculator"
    description = (
        "Perform mathematical calculations. Evaluates arithmetic expressions "
        "safely. Supports +, -, *, /, ** (power), % (modulo), and parentheses. "
        "Can also sum lists of numbers."
    )
    parameters_schema = {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Mathematical expression to evaluate, e.g. '(1500 + 450) * 1.1' or '2 ** 10'",
            }
        },
        "required": ["expression"],
    }

    _operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def _eval_expr(self, node):
        """Safely evaluate an AST node."""
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise TypeError(f"Unsupported constant: {node.value}")
        elif isinstance(node, ast.BinOp):
            left = self._eval_expr(node.left)
            right = self._eval_expr(node.right)
            op = self._operators.get(type(node.op))
            if op is None:
                raise TypeError(f"Unsupported operator: {type(node.op).__name__}")
            # Safety: prevent huge exponentiation
            if isinstance(node.op, ast.Pow) and isinstance(right, (int, float)) and abs(right) > 1000:
                raise ValueError("Exponent too large (max 1000)")
            return op(left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_expr(node.operand)
            op = self._operators.get(type(node.op))
            if op is None:
                raise TypeError(f"Unsupported unary operator: {type(node.op).__name__}")
            return op(operand)
        elif isinstance(node, ast.Call):
            # Support limited built-in math functions
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                args = [self._eval_expr(a) for a in node.args]
                safe_funcs = {
                    "abs": abs,
                    "round": round,
                    "min": min,
                    "max": max,
                    "sum": sum,
                    "sqrt": math.sqrt,
                }
                if func_name in safe_funcs:
                    return safe_funcs[func_name](*args)
                raise TypeError(f"Unsupported function: {func_name}")
        elif isinstance(node, ast.List):
            return [self._eval_expr(el) for el in node.elts]
        elif isinstance(node, ast.Tuple):
            return tuple(self._eval_expr(el) for el in node.elts)
        raise TypeError(f"Unsupported expression type: {type(node).__name__}")

    async def execute(self, expression: str, **kwargs) -> ToolResult:
        try:
            tree = ast.parse(expression.strip(), mode="eval")
            result = self._eval_expr(tree.body)

            # Format the result nicely
            if isinstance(result, float):
                if result == int(result) and abs(result) < 1e15:
                    formatted = str(int(result))
                else:
                    formatted = f"{result:,.4f}".rstrip("0").rstrip(".")
            else:
                formatted = str(result)

            return ToolResult(
                success=True,
                output=f"{expression} = {formatted}",
                metadata={"raw_result": result},
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Error evaluating '{expression}': {e}",
            )
