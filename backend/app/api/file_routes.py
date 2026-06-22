from fastapi import APIRouter

from app.tools.txt_tool import txt_tool
from app.tools.csv_tool import csv_tool
from app.tools.pdf_tool import pdf_tool


router = APIRouter()


@router.get("/reader/txt")
def read_txt(
    filepath: str
):

    return {
        "content": txt_tool.read(
            filepath
        )
    }


@router.get("/reader/csv")
def read_csv(
    filepath: str
):

    return {
        "content": csv_tool.read(
            filepath
        )
    }


@router.get("/reader/pdf")
def read_pdf(
    filepath: str
):

    return {
        "content": pdf_tool.read(
            filepath
        )
    }