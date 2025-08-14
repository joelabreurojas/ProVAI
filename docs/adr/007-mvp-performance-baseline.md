# ADR-007: Establish MVP RAG Performance Baseline

- **Status:** Accepted
- **Date:** 2025-08-14
- **Authors:** ProVAI Team

---

## Context and Problem Statement

With the "headless" RAG engine for the MVP now feature-complete and fully debugged, it is critical to establish a formal, quantitative performance baseline. This baseline will serve as the "control group" against which all future optimizations.

---

## Decision Outcome

We have executed our repeatable benchmarking script (`scripts/benchmark_rag.py`) on our target hardware to establish the official MVP performance baseline.

The results clearly indicate significant performance bottlenecks in ingestion time, query latency, and memory usage. These metrics strongly justify prioritizing performance optimization tasks (such as model upgrades and pipeline improvements) in the next phase of development.

### Recorded MVP Baseline

-   **LLM:** `phi-2.Q4_K_M.gguf`
-   **Embedding Model:** `bge-small-en-v1.5`
-   **Test Document:** `scipy-lectures.pdf` (1255 chunks)
-   **Hardware:** WSL2 Ubuntu on Windows 11, Intel i5-7500 (4 cores), 6GB RAM limit

| Metric                  | Result          |
| :---------------------- | :-------------- |
| Document Ingestion Time | 182.18 seconds  |
| RAG Query Latency       | 104.14 seconds  |
| Peak RAM Usage          | 4376.99 MB      |

---

## Consequences

-   We now have a clear, objective, and data-driven benchmark to measure all future RAG improvements against.
-   The data provides a strong mandate to focus on reducing memory footprint and latency as the highest priority.
