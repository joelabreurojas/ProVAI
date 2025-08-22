# ADR-013: AI Model Selection for the MVP

- **Status:** Accepted
- **Date:** 2025-08-22
- **Authors:** ProVAI Team

---

## Context and Problem Statement

The ProVAI application is fundamentally constrained by its target deployment environment: a CPU-only machine with a strict ~8GB RAM budget. The choice of the core AI models is the single most critical factor in determining the application's performance, resource consumption, and the quality of the user experience. We must select a set of models that provide the best possible balance of speed, memory efficiency, and intelligence.

---

## Considered Options

### Large Language Model (LLM)

1.  **`phi-2` (2.7B parameters):** A highly capable model from Microsoft. Our initial choice, but benchmarks showed high RAM usage (~3.9GB) and query latency (~22s).
2.  **`Mistral-7B` (7B parameters):** A much larger and more powerful model. Rejected as too resource-intensive for our target hardware.
3.  **`Qwen1.5-1.8B` (1.8B parameters):** A smaller, highly-optimized model known for excellent performance and a low memory footprint.
4.  **`TinyLlama-1.1B` (1.1B parameters):** An even smaller, ultra-efficient model, considered as a final option for the most resource-constrained scenarios.

### Embedding Model

1.  **Standard `HuggingFaceEmbeddings` with `bge-small-en-v1.5`:** A high-quality model run via the standard `sentence-transformers` library.
2.  **`fastembed` with `all-MiniLM-L6-v2`:** A library that uses the ONNX runtime for highly-optimized, CPU-first inference with a smaller, very fast embedding model.

---

## Decision Outcome

After comprehensive benchmarking (documented in [ADR-009](./009-performance-optimization-strategy.md)), we have made the following definitive choices for the ProVAI MVP:

-   **Primary LLM:** **Option 3 - `Qwen1.5-1.8B-Chat`** using the `Q4_K_M` GGUF quantization.
-   **Fallback LLM:** **Option 4 - `TinyLlama-1.1B`** is formally designated as our official fallback model for ultra-low-resource environments or if `Qwen1.5-1.8B` proves unstable.
-   **Embedding Model:** **Option 2 - `fastembed`** using the `sentence-transformers/all-MiniLM-L6-v2` model.

### Rationale

This combination was chosen because it delivered the optimal balance of all our key requirements.

-   **Meets Strict Memory Constraints (Primary Factor):** The `Qwen1.5-1.8B` model has a peak RAM usage of **~2.6GB**, a massive **33% reduction** compared to `phi-2`. This is a critical victory for stability on an 8GB machine. `TinyLlama` would reduce this even further, providing a crucial safety net.
-   **Achieves Excellent Performance:** The final optimized stack resulted in a **query latency of ~15 seconds** and an **ingestion time of ~1.3 seconds**. This provides a responsive user experience.
-   **Maintains High Quality:** `Qwen1.5-1.8B` demonstrated excellent instruction-following capabilities and produced high-quality answers on par with `phi-2`. While `TinyLlama`'s quality is slightly lower, it is still highly capable for a factual RAG task.
-   **Architectural Flexibility:** Our config-driven `AssetManager` allows us to switch between `Qwen1.5-1.8B` and `TinyLlama` simply by changing a single line in `assets/llms.yml`, making our choice of fallback model operationally trivial to implement.

---

## Consequences

-   The application is now performant and resource-efficient enough for our target hardware.
-   We have a primary model for quality and a secondary model for extreme efficiency, giving us a robust and flexible deployment strategy.
-   We have formally accepted the trade-off of using a smaller LLM in exchange for critical performance gains.
