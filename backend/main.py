from fastapi import FastAPI

from app.api.routes import router
from app.api.prompt_routes import router as prompt_router


app = FastAPI(
    title="Anuj AI Lab",
    version="1.0.0"
)

app.include_router(router)
app.include_router(prompt_router)


@app.get("/")
def health():

    return {
        "status": "running",
        "project": "Anuj AI Lab"
    }