from app.tools.calculator_tool import calculator_tool
from app.tools.datetime_tool import datetime_tool


class ToolAgent:

    def route(
        self,
        query: str
    ):

        query_lower = query.lower()

        if any(
            op in query
            for op in ["+", "-", "*", "/"]
        ):

            return {
                "tool": "calculator",
                "response": calculator_tool.calculate(
                    query
                )
            }

        if "time" in query_lower:

            return {
                "tool": "datetime",
                "response": datetime_tool.current_time()
            }

        return None


tool_agent = ToolAgent()