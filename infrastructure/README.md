# Infrastructure & Deployment

This directory contains infrastructure configuration, environment orchestration, and deployment specifications for **Anuj AI Lab**.

---

## 🏗️ Architecture & Deployment Overview

### 1. Local Development Stack
- **API Gateway**: FastAPI (`uvicorn main:app --reload --port 8000`)
- **Frontend SPA**: React 19 + TypeScript + Vite (`npm run dev -- --port 5173`)
- **Vector Database**: Embedded ChromaDB with persistent vector store
- **Relational Storage**: SQLite (`experiments.db`) orchestrated via SQLModel
- **Local Model Runtime**: Ollama daemon (`http://localhost:11434`)

---

## 💻 System & Hardware Recommendations

| Component | Minimum Specification | Recommended Specification |
| :--- | :--- | :--- |
| **CPU** | 8 cores (x86_64 or ARM64) | 16+ cores |
| **RAM** | 16 GB DDR4/DDR5 | 32 GB – 64 GB DDR5 |
| **GPU (VRAM)** | 8 GB VRAM (RTX 3060/4060) | 12 GB – 24 GB VRAM (RTX 4070/4080/4090 or Apple M-series) |
| **Storage** | 50 GB NVMe SSD | 100+ GB NVMe PCIe 4.0 |

---

## 🚀 Environment Variables (`.env`)

```env
OLLAMA_BASE_URL=http://localhost:11434
CHROMA_PERSIST_DIR=./backend/vector_db
SQLITE_DB_PATH=./backend/experiments.db
LOG_LEVEL=INFO
```
