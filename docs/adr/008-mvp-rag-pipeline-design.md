# ADR-008: Final RAG Pipeline Design for MVP

- **Status:** Accepted
- **Date:** 2025-08-14
- **Authors:** ProVAI Team

---

## Context and Problem Statement

The development of the MVP's "headless" RAG engine involved a series of iterative tests and refinements to arrive at a stable, high-quality configuration. We need to formally document the final design decisions—covering the model, its invocation, the prompt, and the retrieval strategy—to serve as a definitive record and a baseline for future improvements. This ADR documents the "why" behind our final MVP architecture.

---

## Decision Outcome

After a series of tests, we have finalized the following configuration and patterns for the MVP RAG engine.

### 1. LLM: `phi-2 (Q4_K_M)` as the Baseline Model

**Decision:** The initial MVP will use the `phi-2` GGUF model as its core LLM.

**Rationale:**
-   `phi-2` was selected as a capable and resource-efficient starting point. However, extensive testing revealed significant limitations in instruction following and a strong bias towards code generation. While we have mitigated these with advanced prompt engineering, this experience has provided a strong, data-driven justification for upgrading to a more robust instruction-tuned model (like Mistral-7B) as a high-priority task in the "Walk" phase (Milestone 4).

### 2. Model Invocation: LangChain `LlamaCpp` Wrapper

**Decision:** The LLM will be invoked via the official `langchain_community.llms.llamacpp.LlamaCpp` wrapper class, not by calling the base `llama_cpp.Llama` object directly in the LCEL chain.

**Rationale:**
-   Direct invocation of the base `Llama` object within an LCEL chain proved unreliable. Critical generation parameters like `max_tokens` were not consistently respected, leading to truncated outputs. The official `LlamaCpp` wrapper is designed specifically for LCEL integration, correctly handles invocation-time parameters, and seamlessly integrates with standard components like `StrOutputParser`. This is the architecturally pure and most reliable method.

### 3. Prompt Engineering: "Role-Playing" Instruct Format

**Decision:** The prompt sent to the LLM will use a "role-playing" `Instruct: ... Output:` format, which includes explicit positive and negative constraints.

**Rationale:**
-   Iterative testing proved that a simple prompt was insufficient to control the `phi-2` model's behavior. The final, more forceful prompt format was necessary to:
    1.  Establish a clear "AI Tutor" persona.
    2.  Explicitly forbid code generation unless requested.
    3.  Reinforce the critical RAG guardrail of answering only from the provided context.
    4.  Prime the model with the `Output:` token to prevent prompt regurgitation.

### 4. Retrieval Strategy: Simple `k=4` with Metadata Filtering

**Decision:** The RAG pipeline will retrieve the top `k=4` most relevant document chunks for any given query, filtered by the active `chat_id`.

**Rationale:**
-   `k=4` was chosen as a balanced starting point for the MVP.
-   Testing revealed that this simple retrieval strategy can be a bottleneck, sometimes returning low-quality or repetitive context for broad queries. This provides a strong justification for prioritizing more advanced retrieval strategies (like `ParentDocumentRetriever`) in the "Walk" phase.

---

## Consequences

-   The ProVAI RAG engine is now a stable, well-understood, and fully documented system.
-   We have a clear record of not just our final decisions, but the engineering challenges that led to them.
-   This ADR, combined with `ADR-007` (Performance Baseline), provides a complete picture of the MVP engine and a strong foundation for planning future improvements.
