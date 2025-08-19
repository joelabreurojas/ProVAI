# ADR-009: RAG Performance Optimization Strategy

- **Status:** Accepted
- **Date:** 2025-08-19
- **Authors:** @joelabreurojas

---

## Context and Problem Statement

The MVP performance baseline (ADR-007) revealed critical performance bottlenecks that made the application unsuitable for an interactive user experience. With a query latency of ~22 seconds, an ingestion time of ~8 seconds, and a peak RAM usage of ~3.9GB, the system was too slow and resource-intensive for our target hardware. This ADR documents the successful execution of a multi-faceted performance optimization epic.

---

## Decision Outcome

We have implemented a series of targeted optimizations across the entire RAG pipeline, focusing on the AI models, data processing libraries, and inference configurations.

1.  **LLM Upgrade:** Replaced the `phi-2` model with the smaller, faster **`Qwen1.5-1.8B-Chat`** (Q4_K_M GGUF).
2.  **Inference Tuning:** Explicitly configured `LlamaCpp` with `n_threads=4` and `n_batch=512` to maximize CPU performance.
3.  **Embedding Engine Upgrade:** Replaced the standard `HuggingFaceEmbeddings` with the ONNX-optimized **`fastembed`** library.
4.  **PDF Parsing Upgrade:** Replaced the pure-Python `pypdf` with the high-performance, C-based **`PyMuPDF`** library.

---

## Performance Comparison

The following table compares the benchmark results before and after the full optimization pass, using the `attention_is_all_you_need.pdf` test document.

| Metric             | Baseline (`phi-2`) | **Final Optimized** | Improvement |
| :----------------- | :----------------- | :------------------ | :---------- |
| **Ingestion Time** | ~8 seconds         | **~1.3 seconds**    | **-84%**    |
| **Query Latency**  | ~22 seconds        | **~15 seconds**     | **-32%**    |
| **Peak RAM Usage** | ~3900 MB           | **~2600 MB**        | **-33%**    |

---

## Consequences

-   The application is now **dramatically faster and more responsive.** Query latency is now within an acceptable range for an interactive MVP.
-   The **1.3 GB reduction in RAM usage** makes the system significantly more stable on our 8GB target hardware and provides ample resources for the future Streamlit UI.
-   **Document ingestion is now nearly instantaneous** for small-to-medium documents, representing a massive improvement in user experience.
-   We have established a new, **high-performance baseline** for the project going forward.
