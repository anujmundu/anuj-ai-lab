from fastapi import APIRouter

from app.agents.router_agent import router_agent

router = APIRouter()


@router.get("/route")
def route_query(
    query: str
):

    return router_agent.route(query)