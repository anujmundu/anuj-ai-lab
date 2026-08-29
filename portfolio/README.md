# Project Showcase & System Blueprint

**Anuj AI Lab** is a high-performance local AI engineering workstation featuring multi-modal RAG, autonomous ReAct agents, multi-agent debate deliberation, semantic episodic memory, and real-time telemetry diagnostics.

---

## 🏛️ Architecture Highlights

```mermaid
graph TD
    Client["React 19 SPA (Vite + TailwindCSS)"]
    Gateway["FastAPI Async API Gateway"]
    
    subgraph "Core AI Services"
        Router["Dynamic Task Router"]
        RAG["Hybrid RAG (ChromaDB + BM25)"]
        ReAct["Autonomous ReAct Agent"]
        Debate["Blackboard Multi-Agent Debate"]
        Memory["Semantic Episodic Memory"]
    end

    subgraph "Local Execution Engine"
        Ollama["Ollama Local LLM Fleet"]
        Sandbox["Python AST & File Sandbox"]
        Whisper["faster-whisper Multi-Modal Audio/Video"]
    end

    Client -->|REST & SSE| Gateway
    Gateway --> Router
    Router --> RAG
    Router --> ReAct
    Router --> Debate
    Router --> Memory
    RAG --> Ollama
    ReAct --> Sandbox
    RAG --> Whisper
```

---

## 🌟 Key Capabilities
- **Grounded Semantic RAG**: ChromaDB dense vector indexing + BM25 sparse keyword ranking with parent-child hierarchical chunking.
- **Autonomous Tool Execution**: Sandboxed Python REPL, AST math calculator, and local directory file system manipulation.
- **Multi-Agent Consensus**: Collaborative blackboard deliberation with custom personas (Researcher, Skeptic, Architect, Synthesizer).
- **Adaptive UI Aesthetics**: 12 curated theme modes, 12 dedicated accent color palettes, and responsive multi-device layouts.
