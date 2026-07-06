# 🚀 Anuj AI Lab

> A production-grade local AI engineering platform built with FastAPI, React, TypeScript, Ollama, and Retrieval-Augmented Generation (RAG).

Build modern AI systems locally with document ingestion, semantic retrieval, diagnostics, memory, and agent workflows—all inside a modular engineering platform.

![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python)

![FastAPI](https://img.shields.io/badge/FastAPI-Framework-green?logo=fastapi)

![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)

![TypeScript](https://img.shields.io/badge/TypeScript-5-blue?logo=typescript)

![Vite](https://img.shields.io/badge/Vite-8-purple?logo=vite)

![Tailwind](https://img.shields.io/badge/TailwindCSS-v4-38BDF8?logo=tailwindcss)

![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-black)

![ChromaDB](https://img.shields.io/badge/VectorDB-Chroma-orange)

![License](https://img.shields.io/badge/License-MIT-yellow)

![Version](https://img.shields.io/badge/Version-v0.5.0-blue)

![Status](https://img.shields.io/badge/Development-Active-brightgreen)

# Overview

A modular AI engineering platform for developing production-ready Retrieval-Augmented Generation systems, document intelligence, diagnostics, memory, and autonomous AI workflows.

This project demonstrates how to build a local AI system featuring agents, tools, memory, planning, orchestration, experiment tracking, and autonomous execution.

---

# Portfolio Summary

Current Version: v0.5.0

Completed Stages

✅ Stage 1 — AI Foundations

✅ Stage 2 — Connectors & Voice

✅ Stage 3 — RAG Platform

✅ Stage 3.5 — Modern React Client

Current Focus

🚧 Stage 4 — Persistent Memory

---

# Features

## Core AI Platform

* Local LLM Integration (Ollama)
* FastAPI REST APIs
* Prompt Template Engine
* Multi-Model Evaluation

## Memory & Persistence

* SQLite Experiment Tracking
* Local Conversation Memory
* Persistent Memory System
* Agent State Manager

## Agents

* BaseAgent
* SummarizerAgent
* EmailAgent
* CodeReviewAgent
* RouterAgent
* ToolAgent
* VoiceAgent
* Mini Autonomous Assistant

## External Connectors

* Weather Connector
* News Connector
* Currency Connector
* Wikipedia Connector
* Search Connector

## File Processing

* TXT Reader
* CSV Reader
* PDF Reader

## Voice AI

* Whisper Service
* Text-to-Speech Service
* Voice Agent API

## MCP (Model Context Protocol)

* MCP Tool Registry
* MCP Tool Discovery
* MCP Tool Execution Server

## Orchestration

* Workflow Engine
* Task Planner
* Sequential Workflow Executor
* Multi-Agent Collaboration

### Frontend

- React 19
- TypeScript
- Vite
- Tailwind CSS v4
- React Router
- React Query
- Radix UI
- Lucide React
- Zustand

## Documentation

* Swagger UI
* Architecture Documentation
* Screenshots & Proofs

## Workspace

* Modern React Dashboard
* Responsive Layout
* Theme Switching
* React Query
* Zustand State Management

## Document Intelligence

* Upload Documents
* Automatic Parsing
* Chunking
* Embeddings
* Vector Search

## RAG

* Semantic Retrieval
* Context Builder
* Prompt Builder
* Ollama Integration

## Diagnostics

* Pipeline Diagnostics
* Execution Timings
* Confidence Score
* Citation Mapping
* Hallucination Detection
* Prompt Statistics
* Response Statistics
* Source Attribution

---

# 🛠 Tech Stack

### Backend
- Python
- FastAPI
- Uvicorn

### AI Models
- Ollama
- qwen2.5:1.5b
- gemma2:9b

### Database
- SQLite
- SQLModel
- SQLAlchemy

### Configuration
- Pydantic
- pydantic-settings
- python-dotenv

### HTTP & APIs
- Requests
- HTTPX

### Logging
- Loguru

### Testing
- Pytest

### Version Control
- Git
- GitHub

### Frontend
- Streamlit

---

# Architecture

```text
                          React + TypeScript UI
                     (Vite • Tailwind • React Query)
                                   │
                                   ▼
                        Modern Workspace Interface
      ┌──────────────┬──────────────┬──────────────┐
      │              │              │              │
      ▼              ▼              ▼              ▼
    Chat         Documents      Settings      Inspector
      │              │              │              │
      └──────────────┴──────────────┴──────────────┘
                                   │
                                   ▼
                           FastAPI Backend API
                                   │
══════════════════════════════════════════════════════════════════════
                                   │
      ┌──────────────┬──────────────┬──────────────┬──────────────┐
      ▼              ▼              ▼              ▼
 Document        Retrieval      Diagnostics      System
 Ingestion          RAG             Engine       Services
      │              │              │              │
      ▼              ▼              ▼              ▼
 File Parser   Semantic Search   Timing Metrics   Health Check
 Chunking      Context Builder   Citations       Configuration
 Metadata      Prompt Builder    Confidence      Model Info
 Embeddings    Response Engine   Hallucination
                                   │
══════════════════════════════════════════════════════════════════════
                                   │
                     Local AI Inference Layer
      ┌─────────────────────────────┴─────────────────────────────┐
      ▼                                                           ▼
  Ollama Server                                          Local Embedding Model
      │                                                           │
      └─────────────────────────────┬─────────────────────────────┘
                                    ▼
                           Vector Database
                              (ChromaDB)
                                    │
══════════════════════════════════════════════════════════════════════
                                    │
      ┌──────────────┬──────────────┬──────────────┬──────────────┐
      ▼              ▼              ▼              ▼
 Documents      Embeddings      Metadata      Source Chunks
                                    │
══════════════════════════════════════════════════════════════════════
                                    │
                     Future Platform Expansion
      ┌──────────────┬──────────────┬──────────────┬──────────────┐
      ▼              ▼              ▼              ▼
   Memory          Tools         Agents      Multi-Agent
   (Stage 4)      (Stage 5)     (Stage 6)    (Stage 7)
```

---

## Project Structure

```text
anuj-ai-lab
│
├── backend
│   │
│   ├── app
│   │   │
│   │   ├── api
│   │   │   ├── assistant_routes.py
│   │   │   ├── collaboration_routes.py
│   │   │   ├── compare_routes.py
│   │   │   ├── connector_routes.py
│   │   │   ├── document_routes.py
│   │   │   ├── ingestion_routes.py
│   │   │   ├── rag_routes.py
│   │   │   ├── search_routes.py
│   │   │   ├── system_routes.py
│   │   │   ├── workflow_routes.py
│   │   │   └── voice_routes.py
│   │   │
│   │   ├── core
│   │   │
│   │   ├── db
│   │   │
│   │   ├── models
│   │   │
│   │   ├── rag
│   │   │   ├── chunking.py
│   │   │   ├── embeddings.py
│   │   │   ├── ingestion_service.py
│   │   │   ├── prompt_builder.py
│   │   │   ├── rag_service.py
│   │   │   ├── retrieval_models.py
│   │   │   └── vector_store.py
│   │   │
│   │   ├── services
│   │   │
│   │   ├── utils
│   │   │
│   │   └── future
│   │       ├── memory
│   │       ├── tools
│   │       ├── agents
│   │       └── workflows
│   │
│   ├── data
│   │   ├── documents
│   │   ├── embeddings
│   │   └── sample_documents
│   │
│   ├── tests
│   │
│   ├── main.py
│   └── requirements.txt
│
├── web
│   │
│   ├── public
│   │
│   ├── src
│   │   │
│   │   ├── app
│   │   │
│   │   ├── components
│   │   │   ├── chat
│   │   │   ├── documents
│   │   │   ├── inspector
│   │   │   ├── layout
│   │   │   ├── navigation
│   │   │   ├── ui
│   │   │   └── workspace
│   │   │
│   │   ├── hooks
│   │   │   ├── chat
│   │   │   ├── document
│   │   │   ├── rag
│   │   │   └── system
│   │   │
│   │   ├── lib
│   │   │
│   │   ├── pages
│   │   │   ├── ChatPage.tsx
│   │   │   ├── DocumentsPage.tsx
│   │   │   ├── MemoryPage.tsx
│   │   │   ├── PipelinePage.tsx
│   │   │   ├── SettingsPage.tsx
│   │   │   └── ToolsPage.tsx
│   │   │
│   │   ├── providers
│   │   │
│   │   ├── services
│   │   │
│   │   ├── stores
│   │   │
│   │   ├── types
│   │   │
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   │
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── docs
│   ├── architecture
│   ├── screenshots
│   └── roadmap
│
├── infrastructure
│
├── notebooks
│
├── portfolio
│
├── scripts
│
├── .github
│
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```
---

# Installation

Clone the repository:

```bash
git clone https://github.com/anujmundu/anuj-ai-lab.git
cd anuj-ai-lab/backend
```

Create virtual environment:

```bash
python -m venv venv
```

Activate:

Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Ollama Setup

Start Ollama:

```bash
ollama serve
```

Pull models:

```bash
ollama pull qwen2.5:1.5b
ollama pull gemma2:9b
```

---

# Run FastAPI

```bash
uvicorn main:app --reload
```

Open:

```
http://127.0.0.1:8000
```

Swagger UI:

```
http://127.0.0.1:8000/docs
```

---

## Quick Start

### Terminal 1

```bash
cd backend
uvicorn main:app --reload
```

### Terminal 2

```bash
cd web
npm install
npm run dev
```

Backend:
http://127.0.0.1:8000

Frontend:
http://localhost:5173

Swagger:
http://127.0.0.1:8000/docs

---

# Major Endpoints

| Endpoint            | Description               |
| ------------------- | ------------------------- |
| /test-llm           | Ollama Test               |
| /prompts/summarize  | Prompt Templates          |
| /experiments        | Experiment Tracking       |
| /compare            | Multi-Model Evaluation    |
| /workflow/summarize | Workflow Engine           |
| /route              | Router Agent              |
| /tool/calculate     | Calculator Tool           |
| /state              | Agent State Manager       |
| /plan               | Task Planner              |
| /execute            | Sequential Executor       |
| /collaborate        | Multi-Agent Collaboration |
| /assistant          | Autonomous Assistant      |
| /search             | Search Connector          |
| /reader/txt         | TXT Reader                |
| /reader/csv         | CSV Reader                |
| /reader/pdf         | PDF Reader                |
| /voice              | Voice Agent               |
| /mcp/tools          | MCP Discovery             |
| /mcp/execute        | MCP Execution             |
| /docs               | Swagger Documentation     |


---

# 📸 Screenshots

## Chat Workspace

![Chat Workspace](assets/screenshots/chat-workspace.png)

---

## Chat

![Chat](assets/screenshots/chat.png)

---

## Documents

![Documents](assets/screenshots/documents.png)

---

## Document Upload

![Document Upload](assets/screenshots/document-upload.png)

---

## Pipeline Diagnostics

![Pipeline Diagnostics](assets/screenshots/pipeline-diagnostics.png)

---

## Pipeline Citations

![Pipeline Citations](assets/screenshots/pipeline-citations.png)

---

## Settings

![Settings](assets/screenshots/settings.png)

---

## Dark Theme

![Dark Theme](assets/screenshots/dark-theme.png)

---

## Light Theme

![Light Theme](assets/screenshots/light-theme.png)

---

## Additional Screenshots

Additional screenshots demonstrating the platform architecture, backend APIs, and future development stages are available in:

```text
assets/screenshots/
```

Examples include:

- Backend Health
- RAG Responses
- Document Retrieval
- Citation Mapping
- Prompt Diagnostics
- Hallucination Analysis
- Project Architecture
- Future Platform Development

---

Additional screenshots demonstrating every module are available in:

```text
assets/screenshots/
```

Including:

- Root Endpoint
- Test LLM Endpoint
- Prompt Template Engine
- SQLite Experiment Tracking
- Multi-Model Evaluation
- Workflow Engine
- Router Agent
- Tool Agent
- State Manager
- Task Planner
- Sequential Workflow Executor
- Multi-Agent Collaboration Engine
- Mini Autonomous Assistant
- Swagger API Documentation
- Terminal Proof Logs
- Project Tree Structure

---

# Development Timeline

Stage 1

FastAPI Foundations

✔

Stage 2

Connectors & Voice

✔

Stage 3

RAG Backend

✔

Stage 3.5

Modern React Client

✔

Stage 4

Memory

🚧

Stage 5

Tools

⏳

Stage 6

Agents

⏳

Stage 7

Multi-Agent Platform

⏳
---

#  Release History

## v0.5.0 — Modern React AI Platform

**Released:** July 2026

### Added

- Modern React 19 + TypeScript frontend
- Vite-powered development environment
- Responsive application workspace
- Dark / Light theme support
- React Query data layer
- Document upload workflow
- Automatic document refresh after upload
- RAG document management
- Pipeline Diagnostics dashboard
- Execution timing metrics
- Citation mapping
- Hallucination analysis
- Confidence scoring
- Backend health monitoring
- Settings dashboard
- Inspector panel
- Improved UI component library
- Toast notifications
- Production-ready application layout

---

## v0.4.0 — Retrieval-Augmented Generation (RAG)

**Released:** July 2026

### Added

- Document ingestion pipeline
- Automatic chunking
- Embedding generation
- ChromaDB vector database integration
- Semantic document retrieval
- Prompt builder
- Context builder
- Citation generation
- Source mapping
- Local Ollama integration
- FastAPI RAG APIs

---

## v0.3.0 — AI Platform Foundations

**Released:** June 2026

### Added

- FastAPI backend architecture
- REST API foundation
- Local AI inference using Ollama
- Modular project structure
- Configuration management
- Logging system
- Testing framework
- Core AI service layer

---

## v0.2.0 — Connectors & Voice

**Released:** June 2026

### Added

- External connectors
- Search services
- File processing
- Voice AI foundations
- Workflow improvements

---

## v0.1.0 — Initial Release

**Released:** June 2026

### Added

- Project initialization
- Local LLM experimentation
- Prompt engineering
- Early workflow engine
- Agent architecture foundation

---

#  Future Roadmap

## ✅ Stage 1 — AI Foundations

- FastAPI Backend
- Local LLM Integration (Ollama)
- Prompt Engineering
- Workflow Foundations
- API Architecture

---

## ✅ Stage 2 — Connectors & Voice

- External Connectors
- Search Services
- File Processing
- Voice AI Foundations
- Workflow Improvements

---

## ✅ Stage 3 — Retrieval-Augmented Generation (RAG)

- Document Ingestion
- Automatic Chunking
- Embedding Generation
- ChromaDB Vector Database
- Semantic Search
- Context Builder
- Prompt Builder
- Citation Mapping
- Pipeline Diagnostics
- Hallucination Detection

---

## ✅ Stage 3.5 — Modern React Platform

- React 19 + TypeScript Frontend
- Vite Development Environment
- Tailwind CSS UI
- Responsive Workspace
- Document Management
- Live Pipeline Inspector
- Backend Health Monitoring
- Settings Dashboard
- Dark / Light Theme
- React Query Integration

---

##  Stage 4 — Memory

- Persistent Conversation Memory
- Session Management
- User Profiles
- Memory Retrieval
- Memory Visualization

---

## ⏳ Stage 5 — Tool Calling

- Function Calling
- Local Tool Registry
- File System Tools
- Python Execution
- Web Search Integration
- Tool Permission System

---

## ⏳ Stage 6 — AI Agents

- Autonomous Agents
- Planning Engine
- Multi-Step Reasoning
- Task Execution
- Agent Collaboration

---

## ⏳ Stage 7 — Multi-Agent Platform

- Agent Orchestration
- Shared Memory
- Workflow Automation
- Parallel Agent Execution
- Production AI Engineering Platform

---

#  Project Status

## ✅ Stage 1 — AI Foundations

- FastAPI Backend
- Local LLM Integration
- Prompt Engineering
- Workflow Engine
- REST APIs

---

## ✅ Stage 2 — Connectors & Voice

- External Connectors
- Search Services
- File Processing
- Voice AI
- Workflow Improvements

---

## ✅ Stage 3 — RAG Platform

- Document Upload
- Chunking
- Embeddings
- ChromaDB
- Semantic Retrieval
- Prompt Builder
- Citation Mapping
- Diagnostics Engine

---

## ✅ Stage 3.5 — Modern React Client

- React + TypeScript
- Responsive Workspace
- Document Management
- Pipeline Inspector
- Settings Dashboard
- Theme Switching
- Backend Health Monitoring
- Toast Notifications

---

## 🚧 Currently Working On

**Stage 4 — Memory System**

- Persistent Memory
- Conversation History
- User Sessions
- Memory Retrieval

---

### Current Release

**v0.5.0**

---

# Highlights

- Built completely from scratch using a modular architecture.
- Modern React 19 + TypeScript frontend.
- FastAPI-powered backend APIs.
- Local AI inference using Ollama.
- Retrieval-Augmented Generation (RAG) pipeline.
- ChromaDB vector database integration.
- Semantic document retrieval.
- Automatic document ingestion and chunking.
- Live Pipeline Diagnostics dashboard.
- Execution timing analysis.
- Citation mapping and source attribution.
- Hallucination detection and confidence scoring.
- Responsive multi-page workspace.
- Dark and Light theme support.
- React Query for efficient server state management.
- Production-ready project structure.
- Fully documented with architecture diagrams, screenshots, and API documentation.

---

## 👨‍💻 Author

**Anuj Mundu**

Master of Computer Applications (MCA)  
Maulana Azad National Institute of Technology (MANIT), Bhopal

**Interests**
- Artificial Intelligence
- Retrieval-Augmented Generation (RAG)
- AI Agents
- Data Science
- Machine Learning
- Full-Stack AI Engineering

GitHub: https://github.com/anujmundu

Current Focus:
Building Production-Ready Agentic AI Systems
