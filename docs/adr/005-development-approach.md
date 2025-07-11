# **ADR-005: Adopt "Crawl, Walk, Run" for RAG Development**

- **Status:** Accepted
- **Date:** 2025-07-06
- **Authors:** Joel Abreu Rojas

---

## Context and Problem Statement

The field of Retrieval-Augmented Generation (RAG) is evolving at an incredible pace, with numerous advanced techniques (e.g., RAG-Fusion, Decomposition, Parent Document Retrieval, CRAG, Self-RAG) being published regularly. Our project vision includes many of these sophisticated features to build a truly intelligent tutor. However, attempting to implement multiple advanced techniques at once under our strict constraints (2-person team, 4-5 month timeline, limited hardware) would introduce unmanageable complexity and risk project failure. We need a formal strategy for sequencing the implementation of these features to ensure we deliver value incrementally without being overwhelmed.

---

## Decision Outcome

**Chosen Strategy:** We will adopt a formal **"Crawl, Walk, Run"** phased approach for the development of the ProVAI RAG engine.

1.  **Crawl (MVP - Milestones 1-3):** The absolute priority is to build the simplest possible, end-to-end functional RAG pipeline. This includes only the most basic, essential components:
    - **Indexing:** `RecursiveCharacterTextSplitter` only.
    - **Retrieval:** Basic vector similarity search with a fixed `k`.
    - **Generation:** A simple prompt template with no self-correction or web search.

2.  **Walk (Post-MVP - Milestone 4 High-Priority):** After the MVP is stable and deployed, we will focus on the most impactful, resource-efficient upgrades to improve retrieval quality. The initial "Walk" phase will prioritize:
    - `Parent Document Retriever`
    - `Query Structuring with Metadata Filters`
    - `Corrective RAG (Web Search Fallback)`

3.  **Run (Future - Milestone 4 Lower-Priority):** Once the "Walk" phase features are mature, we will explore the most advanced, computationally intensive, and architecturally complex features. This phase will be built upon a LangGraph state machine and will include:
    - `RAG-Fusion` / `Multi-Query`
    - `Self-Correction / Self-Critique loops`
    - `Decomposition` and other agentic reasoning patterns.

---

## Rationale

This phased approach was chosen as the optimal strategy to manage risk and deliver value.

- **De-risks the Project:** By focusing on a simple "Crawl" phase first, we guarantee that we can deliver a functional core product within the timeline. We prove the foundational technology works before adding layers of complexity.
- **Aligns with Constraints:** The "Crawl" phase is designed to be achievable on our limited hardware. The more resource-intensive techniques are explicitly deferred until we have a stable baseline to benchmark against.
- **Provides a Clear Roadmap:** This strategy transforms our long-term vision from a daunting list of features into a clear, sequenced, and logical development roadmap. It gives the team a framework for prioritizing all future RAG-related work.
- **Prevents Scope Creep:** This ADR serves as a formal charter. When a new RAG technique is discovered, its place can be evaluated against the "Crawl, Walk, Run" framework. It will almost certainly belong in the "Walk" or "Run" phase, protecting the integrity and timeline of the MVP.

---

## Consequences

### Positive Consequences

- The development team has a clear, shared understanding of what is in scope for the MVP and what is not.
- The project is significantly more likely to succeed in delivering a valuable initial product on time.
- Future development is structured and strategic, not reactive.

### Negative Consequences

- The MVP will not be as "intelligent" or feature-rich as the final vision. This is an explicit and accepted trade-off in favor of feasibility and stability.
