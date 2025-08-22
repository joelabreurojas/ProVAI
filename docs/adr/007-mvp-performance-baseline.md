# ADR-007: MVP RAG Performance Baseline

- **Status:** Superseded by [ADR-009](./009-performance-optimization-strategy.md)
- **Date:** 2025-08-18
- **Authors:** @joelabreurojas

---

## Context and Problem Statement

With the initial "headless" RAG engine for the MVP feature-complete and debugged, it was critical to establish a formal, quantitative performance baseline. This baseline served as the "control group" against which the performance optimization epic was measured.

---

## Decision Outcome

We executed our repeatable benchmarking script (`scripts/benchmark_rag.py`) on our target hardware to establish the official initial performance baseline. The results highlighted significant performance bottlenecks, providing the data-driven justification to proceed with the upgrades documented in [ADR-009](./009-performance-optimization-strategy.md).

### Recorded Historical Baseline (`phi-2`)

-   **LLM:** `phi-2.Q4_K_M.gguf`
-   **Embedding Model:** `HuggingFaceEmbeddings` with `bge-small-en-v1.5`
-   **Test Document:** `attention_is_all_you_need.pdf` (42 chunks)
-   **Hardware:** Ubuntu 22.04 WSL2 on Windows 11, Intel Core i5-7500 (4 cores), 6GB RAM limit, SSD Storage

| Metric                  | Average Result  |
| :---------------------- | :-------------- |
| Document Ingestion Time | ~8 seconds      |
| RAG Query Latency       | ~22 seconds     |
| Peak RAM Usage          | ~3900 MB        |

---

## Consequences

-   This benchmark successfully provided the objective data needed to justify and measure the impact of our performance optimization work.
-   It now serves as a permanent historical record of the project's performance at the end of the initial "Crawl" phase.
