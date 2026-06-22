from fastapi import APIRouter

from app.tools.calculator_tool import calculator_tool
from app.tools.datetime_tool import datetime_tool
from app.tools.weather_tool import weather_tool
from app.tools.news_tool import news_tool
from app.tools.currency_tool import currency_tool
from app.tools.wikipedia_tool import wikipedia_tool


router = APIRouter()


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