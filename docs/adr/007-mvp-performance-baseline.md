# ADR-007: Establish MVP RAG Performance Baseline

- **Status:** Accepted
- **Date:** 2025-07-30
- **Authors:** Joel Abreu Rojas

---

## Context and Problem Statement

As we prepare to develop more advanced RAG features, it is critical to have a formal, quantitative baseline of the MVP's performance. Without this baseline, we cannot make data-driven decisions about whether future optimizations are a net benefit.

This ADR formally records the initial performance of the "Crawl" phase RAG engine.

---

## Decision Outcome

We have created a repeatable benchmarking script at `scripts/benchmark_rag.py`. We have executed this script on our target hardware (CPU-only, 8GB RAM) using a representative test document to establish the official MVP performance baseline.

All future architectural changes to the RAG pipeline must be benchmarked using this script and compared against this baseline.

### Recorded MVP Baseline

- **Test Document:** `clean_coder.pdf`
- **Document Size:** 113 Chunks
- **Hardware:** Ubuntu 22.04 (WSL2), 4-core, 6GB RAM limit

| Metric                  | Result         |
| :---------------------- | :------------- |
| Document Ingestion Time | 9.94 seconds   |
| RAG Query Latency       | 30.85 seconds  |
| Peak RAM Usage          | 3.90 GB        |

---

## Consequences

### Positive Consequences

- We now have a clear, objective benchmark to measure all future RAG improvements against.
- This enforces engineering discipline and ensures that we evaluate the performance trade-offs of any new feature we add.

### Negative Consequences

- None. This is a purely additive process that improves our engineering rigor.
