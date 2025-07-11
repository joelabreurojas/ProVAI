# ADR-001: Adopt Onion Architecture

- **Status:** Accepted
- **Date:** 2025-07-06
- **Authors:** Joel Abreu Rojas

---

## Context and Problem Statement

For the ProVAI project, we need a foundational architecture that supports our long-term goals of maintainability, testability, and scalability. Given our small team size and the "Keep It Simple" philosophy, we must avoid overly complex patterns while still ensuring a clean separation of concerns. The primary problem is to prevent the business logic from becoming tightly coupled to external frameworks and infrastructure (like the web server or database), which would make the system brittle and difficult to test.

---

## Considered Options

1.  **Standard Monolithic App:** A simple, flat structure where business logic is often mixed within the web controller/view layer (common in simple Flask/Django apps).
2.  **Onion Architecture:** A layered architecture that enforces the Dependency Inversion Principle, where inner layers (domain, application) define abstractions and outer layers (infrastructure) implement them.
3.  **Full Microservices Architecture:** Breaking down every component into separate, independently deployable services from the start.

---

## Decision Outcome

**Chosen Option:** Option 2, Onion Architecture.

### Rationale

We will structure the ProVAI codebase using the principles of Onion Architecture, with clear boundaries between the following layers:

- **`src/domain`**: The core of the application, containing our business entities (models) and rules. It has zero dependencies on other layers.
- **`src/application`**: Contains our use cases and service logic (e.g., `RAGService`, `AuthService`). It depends only on the `domain` layer.
- **`src/infrastructure`**: Contains external concerns like the FastAPI app, database connections, and API clients. It depends on the `application` layer.

This choice was made for several key reasons:

- **High Testability:** This architecture allows us to test the core application and domain logic completely independently of FastAPI, databases, or any other external service. This is a critical requirement for building a reliable system.
- **Flexibility & Scalability:** It makes swapping out external components trivial. For example, migrating from SQLite to PostgreSQL or from a local LLM to a cloud API will not require changes to the core business logic.
- **Clarity for a Small Team:** The strict boundaries enforce a clean and organized codebase, making it easier for a small team to navigate and contribute without confusion.
- **Balanced Complexity:** It provides the benefits of separation of concerns without the significant operational overhead and complexity of a full microservices architecture, which is not appropriate for our current team size and MVP goals. The simple monolithic app (Option 1) was rejected as it does not provide sufficient separation for long-term maintainability.

---

## Consequences

### Positive Consequences

- The codebase will be highly modular and maintainable.
- Unit testing of core business logic will be simple and fast.
- The project is architecturally prepared for future growth and change.

### Negative Consequences

- There is slightly more initial setup and boilerplate code required compared to a simple, flat application structure.
- Developers must be disciplined about respecting the layer boundaries and the direction of dependencies.
