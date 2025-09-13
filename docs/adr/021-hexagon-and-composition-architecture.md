# ADR-021: Adopt a Hexagonal Architecture with a Composition Root

- **Status:** Accepted
- **Date:** 2025-09-15
- **Authors:** [@joelabreurojas](https://github.com/joelabreurojas)

---

## Context and Problem Statement

As the ProVAI project matured with both a backend API (`api`) and a frontend UI (`ui`), a critical architectural inconsistency emerged. The UI module was directly importing domain models and dependency providers from the API module. This created tight coupling, violating our goal of a decoupled, modular system and making future maintenance difficult. We needed to adopt a definitive architectural pattern that would establish a single source of truth for our business logic and enforce strict separation between our delivery mechanisms.

---

## Decision Outcome

We have refactored the project to formally adopt **Hexagonal Architecture (Ports and Adapters)**, with a central **Composition Root** to wire the application together.

1.  **The Core/Hexagon (`src/core`):** All shared, cross-cutting business logic is now centralized. This includes the domain models, Pydantic schemas (data contracts), business-specific exceptions, and abstract service protocols (the "Ports"). The Core is pure and has zero knowledge of the `api` or `ui`.

2.  **The Adapters (`src/api`, `src/ui`):** These are independent consumer modules. The `api` adapter implements the core service protocols and exposes them via a JSON API. The `ui` adapter consumes the core service protocols to drive an HTML-based user interface. They are strictly forbidden from importing from each other and only depend on `core`.

3.  **The Composition Root (`src/core/infrastructure/app.py`):** The main application factory (`create_app`) is the single place in the application responsible for assembling the system. It uses FastAPI's `dependency_overrides` to connect the abstract protocols required by the adapters with their concrete implementations.

This decision supersedes all previous architectural ADRs, including ADR-001, ADR-006, and ADR-010.

---

## Rationale

This architecture is the superior and final choice because it perfectly embodies professional software engineering principles:

- **Single Source of Truth & DRY:** By centralizing all core business concepts in `core`, we eliminate duplication and ensure that both the API and UI are operating on the exact same definitions. This is our "Core Business Domain."
- **Dependency Inversion Principle:** The UI no longer depends on the concrete implementation details of the API. Both high-level adapters now depend on the stable, central abstractions defined in `core`.
- **True Decoupling and Scalability:** This change completely severs the link between the API and UI. This makes the system more robust, easier to reason about, and provides a clean path for adding new adapters (e.g., a `websocket` service) in the future without impacting existing ones.

---

## Consequences

- The project now has a clear, scalable, and architecturally pure structure that will support long-term maintainability.
- A one-time refactoring effort was completed to move the relevant files from `api` to `core` and update all import statements across the project. This is a necessary and highly beneficial investment.
- The application is now free of circular dependencies, allowing it to load and run correctly.
