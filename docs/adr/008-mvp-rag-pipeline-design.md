# ADR-008: RAG Pipeline Design for MVP

- **Status:** Superseded by ADR-009
- **Date:** 2025-08-19
- **Authors:** @joelabreurojas

---

## Context and Problem Statement

The initial implementation of the headless RAG engine required a series of iterative tests and refinements to arrive at a stable, high-quality configuration. We needed to formally document the final design decisions for the initial "Crawl" phase RAG engine to serve as a definitive record and a baseline for future improvements. This ADR captures the state of the engine at the end of the initial build, before the major performance optimization pass.

---

## Decision Outcome

After extensive iterative testing, we finalized the following configuration for the initial MVP RAG engine.

### 1. LLM: `phi-2 (Q4_K_M)`

**Decision:** The initial MVP was built and stabilized using the `phi-2` GGUF model.

**Rationale:**
-   `phi-2` was chosen as a capable small language model that could run on CPU-only hardware. However, testing revealed significant limitations.
-   **Finding:** The model struggled to reliably follow complex instructions and had a strong bias towards generating code, which required significant prompt engineering to mitigate.
-   **Finding:** Its performance characteristics (~3.9GB RAM usage, ~22-30s query latency) were deemed too high for a responsive user experience.
-   **Conclusion:** While functional, this model was identified as the primary bottleneck and the top candidate for a performance-focused upgrade.

### 2. Chunking Strategy: `RecursiveCharacterTextSplitter`

**Decision:** We will use LangChain's `RecursiveCharacterTextSplitter` with a chunk size of ~300 tokens and zero overlap.

**Rationale:**
-   **Effectiveness & Simplicity:** This splitter provides an excellent balance of semantic coherence (by respecting paragraph and sentence boundaries) and simplicity. It avoids the computational overhead of more advanced semantic chunking methods, aligning with our "Keep It Simple" philosophy for the MVP.

### 3. Retrieval Strategy: `k=4` with Relational Filtering

**Decision:** The RAG pipeline will retrieve the top `k=4` most relevant document chunks for any given query. Critically, the retrieval is filtered by first querying the relational database to get a list of valid `content_hash` IDs for the active `chat_id`.

**Rationale:**
-   `k=4` was chosen as a balanced starting point to provide sufficient context to the LLM without excessive noise.
-   The two-step retrieval process (relational query first, then vector search) is architecturally pure and guarantees strict data isolation between different chats, which is a non-negotiable security and privacy requirement.

### 4. Prompt Engineering: `Instruct/Output` Format

**Decision:** The prompt sent to the LLM will use a direct `Instruct: ... Query: ... Output:` format, stripped of complex role-playing or XML tags.

**Rationale:**
-   Iterative testing proved that `phi-2` was highly sensitive to prompt format. Complex prompts led to "prompt bleed" and the model regurgitating instructions.
-   The simple, direct `Instruct/Output` format was the most effective at forcing the model to switch into an instruction-following mode and produce clean, natural language answers.

---

## Consequences

-   We successfully created a stable, end-to-end functional RAG engine.
-   We formally documented the decisions that led to this stability.
-   The performance testing of this configuration (recorded in ADR-007) provided the clear, data-driven justification needed to immediately proceed with a full performance optimization epic. This ADR is therefore superseded by ADR-009, which documents the results of those optimizations.
