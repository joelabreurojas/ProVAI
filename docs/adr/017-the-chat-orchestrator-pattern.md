# ADR-017: The Chat Orchestrator Pattern

- **Status:** Accepted
- **Date:** 2025-08-24
- **Authors:** @joelabreurojas

---

## Context and Problem Statement

After refactoring our core features (`auth`, `tutor`, `rag`) into decoupled, self-contained modules, a new architectural question arose: which component is responsible for coordinating them? A user action, such as asking a question, requires a sequence of operations across these modules (authorize the user, get the tutor's documents, query the RAG engine, log the message).

Placing this orchestration logic in the API layer (`router`) would make it bloated and difficult to test. Placing it in the `TutorService` would re-introduce the tight coupling we had just removed. We needed a dedicated, high-level service to act as the central "brain" of the application.

---

## Decision Outcome

We have designated the **`ChatService`**, located in its own `chat` module, as the **central application orchestrator.**

### Rationale

This decision establishes a clean, multi-layered service architecture:

1.  **Low-Level Services (e.g., `TutorService`, `RAGService`):** These are specialized, "worker" services. They are experts at a single domain (managing tutors, running RAG pipelines) and have no knowledge of each other.
2.  **High-Level Orchestrator (`ChatService`):** This is the "manager" service. It is the only component in the application that is aware of the other services. Its sole responsibility is to handle a high-level user request, call the necessary worker services in the correct order, and synthesize their results.

This pattern is superior because:
-   **It preserves perfect decoupling:** The `tutor` and `rag` modules remain completely independent and reusable.
-   **It centralizes complexity:** All complex, multi-step business logic is located in one single, cohesive place (`ChatService`), making it easy to understand, test, and debug.
-   **It keeps the API layer thin:** Our API endpoints in the `chat_router` are simple and declarative. They just receive a request and pass it to the `ChatService`, which does all the heavy lifting.

---

## Consequences

- **Positive:** The application has a clear and logical flow of control. The separation between orchestration and specialized business logic makes the entire system more robust and maintainable.
- **Negative:** None. This is the definitive and correct pattern for our architecture.
