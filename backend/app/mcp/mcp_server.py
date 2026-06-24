from app.mcp.tool_registry import tool_registry

from app.tools.weather_tool import weather_tool
from app.tools.news_tool import news_tool
from app.tools.currency_tool import currency_tool
from app.tools.wikipedia_tool import wikipedia_tool
from app.tools.search_tool import search_tool


tool_registry.register(
    "weather",
    weather_tool
)

tool_registry.register(
    "news",
    news_tool
)

tool_registry.register(
    "currency",
    currency_tool
)

tool_registry.register(
    "wiki",
    wikipedia_tool
)

tool_registry.register(
    "search",
    search_tool
)


class MCPServer:

    def execute(
        self,
        tool_name: str,
        query: str = ""
    ):

        tool = tool_registry.get_tool(
            tool_name
        )

        if not tool:

            return {
                "error":
                "Tool not found"
            }

        if tool_name == "weather":

            return tool.get_weather()

        if tool_name == "news":

            return tool.get_news()

        if tool_name == "currency":

            return tool.get_rates()

        if tool_name == "wiki":

            return tool.search(
                query
            )

        if tool_name == "search":

            return tool.search(
                query
            )

        return {
            "error":
            "Unsupported tool"
        }


mcp_server = MCPServer()