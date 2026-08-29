# Research, Evaluation & Benchmarking Notebooks

This directory contains Jupyter notebooks used for experimental analysis, retrieval benchmarking, hallucination evaluation, and embedding model comparisons.

---

## 🔬 Benchmark Workflows

1. **RAG Retrieval Quality & Recall**:
   - Compare dense embeddings (`nomic-embed-text`, `bge-large`, `all-MiniLM-L6-v2`) against BM25 sparse keyword search.
   - Measure Recall@K, NDCG@10, and Context Relevance.

2. **Multi-Agent Deliberation Trials**:
   - Trace convergence speed and consensus quality in multi-agent blackboard debates across diverse complex reasoning tasks.

3. **ReAct Agent Tool-Calling Accuracy**:
   - Evaluate single-turn vs. multi-step tool trajectory success rate across Python sandbox code execution, AST math evaluation, and filesystem manipulation.
