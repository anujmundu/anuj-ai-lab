from fastapi import FastAPI

app = FastAPI(
    title="Anuj AI Lab",
    version="1.0.0"
)

@app.get("/")
def health():
    return {
        "status": "running",
        "project": "Anuj AI Lab"
    }