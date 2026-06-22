from fastapi import APIRouter

from app.connectors.weather_connector import weather_connector
from app.connectors.news_connector import news_connector
from app.connectors.currency_connector import currency_connector
from app.connectors.wikipedia_connector import wikipedia_connector


router = APIRouter()


@router.get("/weather")
def weather():

    return weather_connector.get_weather()


@router.get("/news")
def news():

    return news_connector.get_news()


@router.get("/currency")
def currency():

    return currency_connector.get_rates()


@router.get("/wiki")
def wiki(
    topic: str = "Artificial Intelligence"
):

    return wikipedia_connector.search(
        topic
    )