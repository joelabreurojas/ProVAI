# ADR-007: Establish MVP RAG Performance Baseline

- **Status:** Accepted
- **Date:** 2025-08-18
- **Authors:** @joelabreurojas

---

## Context and Problem Statement

With the "headless" RAG engine for the MVP now feature-complete, architecturally refactored, and fully debugged, it is critical to establish a formal, quantitative performance baseline. This baseline will serve as the definitive "control group" against which all future optimizations in Milestone 4 will be measured.

---

## Decision Outcome

We have executed our repeatable benchmarking script (`scripts/benchmark_rag.py`) on our target hardware to establish the official MVP performance baseline.

The results demonstrate that the engine is functional and produces high-quality answers, but also highlight the high memory usage of the `phi-2` model and provide clear targets for our upcoming performance optimization epic.

### Recorded MVP Baseline

-   **LLM:** `phi-2.Q4_K_M.gguf`
-   **Embedding Model:** `bge-small-en-v1.5`
-   **Test Document:** `attention_is_all_you_need.pdf` (42 chunks)
-   **Hardware:** Ubuntu 22.04 WSL2 on Windows 11, Intel Core i5-7500 (4 cores), 6GB RAM limit, SSD Storage

| Metric                  | Average Result  | Notes                                        |
| :---------------------- | :-------------- | :------------------------------------------- |
| Document Ingestion Time | ~8 seconds      | Excellent for a small, focused document.     |
| RAG Query Latency       | ~22 seconds     | Good, but a clear target for optimization.   |
| Peak RAM Usage          | ~3.9 GB         | High, making a model upgrade a top priority. |


---

## Consequences

-   We now have a clear, objective, and data-driven benchmark to measure all future RAG improvements against.
-   The data provides a strong mandate to focus on reducing memory footprint and latency as the highest priority in the "Walk" phase (Milestone 4).
