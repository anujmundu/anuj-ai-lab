from fastapi import APIRouter

from app.tools.calculator_tool import calculator_tool
from app.tools.datetime_tool import datetime_tool


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
def current_time():

    return {
        "time": datetime_tool.current_time()
    }