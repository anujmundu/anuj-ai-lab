from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.assistant_routes import router as assistant_router
from app.api.collaboration_routes import router as collaboration_router
from app.api.compare_routes import router as compare_router
from app.api.connector_routes import router as connector_router
from app.api.executor_routes import router as executor_router
from app.api.experiment_routes import router as experiment_router
from app.api.file_routes import router as file_router
from app.api.memory_routes import router as memory_router
from app.api.planner_routes import router as planner_router
from app.api.prompt_routes import router as prompt_router
from app.api.router_routes import router as router_agent_router
from app.api.routes import router
from app.api.search_routes import router as search_router
from app.api.state_routes import router as state_router
from app.api.tool_routes import router as tool_router
from app.api.voice_routes import router as voice_router
from app.api.workflow_routes import router as workflow_router
from app.db.database import create_db_and_tables
from app.api.mcp_routes import router as mcp_router
from app.mcp import mcp_server
from app.api.rag_routes import router as rag_router
from app.api.rag_routes import router as rag_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    create_db_and_tables()

    yield


app = FastAPI(
    title="Anuj AI Lab",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)

app.include_router(prompt_router)
app.include_router(experiment_router)
app.include_router(compare_router)
app.include_router(workflow_router)

app.include_router(router_agent_router)
app.include_router(tool_router)
app.include_router(state_router)
app.include_router(planner_router)
app.include_router(executor_router)
app.include_router(collaboration_router)
app.include_router(assistant_router)

app.include_router(connector_router)
app.include_router(file_router)
app.include_router(search_router)
app.include_router(voice_router)
app.include_router(memory_router)
app.include_router(mcp_router)
app.include_router(rag_router)
app.include_router(rag_router)


@app.get("/")
def health():

    return {
        "status": "running",
        "project": "Anuj AI Lab"
    }