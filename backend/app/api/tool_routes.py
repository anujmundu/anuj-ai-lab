from typing import Any
from fastapi import APIRouter
from pydantic import BaseModel

from app.tools.calculator_tool import calculator_tool
from app.tools.datetime_tool import datetime_tool
from app.tools.weather_tool import weather_tool
from app.tools.news_tool import news_tool
from app.tools.currency_tool import currency_tool
from app.tools.wikipedia_tool import wikipedia_tool
from app.tools.registry import tool_registry


router = APIRouter()


class ToolExecuteRequest(BaseModel):
    tool_name: str
    parameters: dict[str, Any] = {}


@router.get("/tools/catalog")
def get_tools_catalog():
    """Return all registered system tools with schema definitions."""
    tools = []
    for name in tool_registry.list_tools():
        tool = tool_registry.get(name)
        if tool:
            definition = tool.get_definition()
            tools.append({
                "name": definition.name,
                "description": definition.description,
                "parameters": [
                    {
                        "name": p.name,
                        "type": p.type,
                        "description": p.description,
                        "required": p.required,
                        "default": p.default,
                    }
                    for p in definition.parameters
                ],
            })
    return {"tools": tools}


@router.post("/tools/execute")
def execute_tool(req: ToolExecuteRequest):
    """Execute a registered tool in the local sandbox."""
    result = tool_registry.execute(req.tool_name, **req.parameters)
    return {
        "tool_name": req.tool_name,
        "success": result.success,
        "output": result.output,
        "error": result.error,
        "execution_time_ms": result.execution_time_ms,
    }


@router.get("/tool/calculate")
def calculate(
    expression: str
):

    return {
        "expression": expression,
        "result": calculator_tool.calculate(
            expression
        )
    }


@router.get("/tool/time")
def time():

    return {
        "time": datetime_tool.current_time()
    }


@router.get("/tool/weather")
def weather():

    return weather_tool.get_weather()


@router.get("/tool/news")
def news():

    return news_tool.get_news()


@router.get("/tool/currency")
def currency():

    return currency_tool.get_rates()


@router.get("/tool/wiki")
def wiki(
    topic: str = "Artificial Intelligence"
):

    return wikipedia_tool.search(
        topic
    )