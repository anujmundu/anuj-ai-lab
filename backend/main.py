from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.experiment_routes import router as experiment_router
from app.api.prompt_routes import router as prompt_router
from app.api.routes import router
from app.db.database import create_db_and_tables


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


@app.get("/")
def health():

    return {
        "status": "running",
        "project": "Anuj AI Lab"
    }