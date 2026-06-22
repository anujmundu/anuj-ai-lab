from app.tools.calculator_tool import calculator_tool
from app.tools.datetime_tool import datetime_tool
from app.tools.weather_tool import weather_tool
from app.tools.news_tool import news_tool
from app.tools.currency_tool import currency_tool
from app.tools.wikipedia_tool import wikipedia_tool


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

        if "weather" in query_lower:

            return {
                "tool": "weather",
                "response": weather_tool.get_weather()
            }

        if "news" in query_lower:

            return {
                "tool": "news",
                "response": news_tool.get_news()
            }

        if "currency" in query_lower:

            return {
                "tool": "currency",
                "response": currency_tool.get_rates()
            }

        if "wiki" in query_lower:

            topic = query.replace(
                "wiki",
                ""
            ).strip()

            if topic == "":
                topic = "Artificial Intelligence"

            return {
                "tool": "wiki",
                "response": wikipedia_tool.search(
                    topic
                )
            }

        return None


tool_agent = ToolAgent()