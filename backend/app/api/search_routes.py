from fastapi import APIRouter

from app.tools.search_tool import search_tool


router = APIRouter()


@router.get("/search")
def search(
    q: str
):

    return search_tool.search(
        q
    )