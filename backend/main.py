from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Core APIs
from app.api.routes import router
from app.api.prompt_routes import router as prompt_router
from app.api.experiment_routes import router as experiment_router
from app.api.compare_routes import router as compare_router

# Workflow & Agent APIs
from app.api.workflow_routes import router as workflow_router
from app.api.router_routes import router as router_agent_router
from app.api.tool_routes import router as tool_router
from app.api.state_routes import router as state_router
from app.api.planner_routes import router as planner_router
from app.api.executor_routes import router as executor_router
from app.api.collaboration_routes import router as collaboration_router
from app.api.assistant_routes import router as assistant_router

# Integration APIs
from app.api.connector_routes import router as connector_router
from app.api.file_routes import router as file_router
from app.api.search_routes import router as search_router
from app.api.voice_routes import router as voice_router
from app.api.memory_routes import router as memory_router
from app.api.mcp_routes import router as mcp_router

# RAG APIs
from app.api.rag_routes import router as rag_router
from app.api.ingestion_routes import router as ingestion_router
from app.api.document_routes import router as document_router

# Stage 4 Persistent Memory
from app.memory.routes import router as persistent_memory_router

from app.db.database import create_db_and_tables
from app.rag.vector_store import vector_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle.

    Startup
    --------
    • Create database tables
    • Synchronize the in-memory BM25 index with
      the persisted ChromaDB corpus

    Shutdown
    --------
    • Reserved for future cleanup tasks
    """

    create_db_and_tables()

    # ------------------------------------------
    # Build the BM25 index from all persisted
    # ChromaDB chunks during startup.
    # ------------------------------------------

    stats = vector_store.sync_bm25_index()

    print("\n===== BM25 Initialized =====")
    print(f'Documents indexed: {stats["documents_loaded"]}')
    print(
        f'BM25 documents: {stats["bm25_documents"]}'
    )
    print("============================\n")

    yield

    # Future shutdown hooks can be added here.


app = FastAPI(
    title="Anuj AI Lab",
    version="1.2.0",
    lifespan=lifespan,
)

# ==========================================
# CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# Core APIs
# ==========================================

app.include_router(router)
app.include_router(prompt_router)
app.include_router(experiment_router)
app.include_router(compare_router)

# ==========================================
# Workflow & Agents
# ==========================================

app.include_router(workflow_router)
app.include_router(router_agent_router)
app.include_router(tool_router)
app.include_router(state_router)
app.include_router(planner_router)
app.include_router(executor_router)
app.include_router(collaboration_router)
app.include_router(assistant_router)

# ==========================================
# Integrations
# ==========================================

app.include_router(connector_router)
app.include_router(file_router)
app.include_router(search_router)
app.include_router(voice_router)
app.include_router(memory_router)
app.include_router(mcp_router)

# ==========================================
# RAG
# ==========================================

app.include_router(rag_router)
app.include_router(ingestion_router)
app.include_router(document_router)

# ==========================================
# Stage 4 Persistent Memory
# ==========================================

app.include_router(persistent_memory_router)


@app.get("/")
def health():
    return {
        "status": "running",
        "project": "Anuj AI Lab",
        "version": "1.2.0",
    }