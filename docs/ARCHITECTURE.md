# ProVAI Software Architecture

This document provides a high-level overview of the software architecture for the ProVAI project. Our architecture is a synthesis of professional patterns designed for maintainability, testability, and scalability.

It is best understood as a blueprint for a well-built house, using four complementary concepts:

1.  **Screaming Architecture** is our **Floor Plan**.
2.  **Hexagonal Architecture** is our **Utilities Plan**.
3.  **Onion Architecture** is our **Internal Building Code**.
4.  **The Composition Root** is our **General Contractor**.

---

### 1. The Floor Plan: Screaming Architecture

The primary organization of our adapters (`api/` and `ui/`) is by business feature. The top-level folders "scream" what the application does. This makes the system easy to navigate and ensures that feature-specific code is highly cohesive.

- `src/api/auth/`
- `src/api/tutor/`
- `src/ui/dashboard/`

### 2. The Utilities Plan: Hexagonal Architecture (Ports & Adapters)

This pattern ensures our core business logic is independent of the outside world.

- **The Hexagon (`src/core`):** The heart of the application. It contains all the pure business logic, entities, and rules. It has zero dependencies on FastAPI or any other web framework.
- **The Ports (`core/application/protocols` & `exceptions`):** These are the abstract interfaces that define _how_ the outside world can interact with the Core.
- **The Adapters (`src/api` & `src/ui`):** These are the bridges that connect external technologies (like HTTP requests) to the Ports of the Core. They depend on the Core, but the Core never depends on them.

### 3. The Internal Building Code: Onion Architecture

Within every module (both in the Core and in the Adapters), we enforce a strict, layered structure to control the flow of dependencies.

- **`domain`:** The innermost layer. Contains our business entities (SQLAlchemy models, Pydantic schemas).
- **`application`:** The middle layer. Orchestrates the domain entities and defines the use cases and interfaces (Protocols).
- **`infrastructure`:** The outermost layer. Contains concrete implementations and interactions with external tools (database sessions, API routers).

**The Golden Rule:** Dependencies must only ever point inwards, from `infrastructure` to `application` to `domain`.

### 4. The General Contractor: The Composition Root

This is the single place where the entire application is assembled.

- **Location:** `src/core/infrastructure/app.py`
- **Responsibility:** The `create_app` factory is the "General Contractor." It is the only part of the application that knows about both the abstract Ports (from `core`) and the concrete Adapters (from `api`). It uses FastAPI's `dependency_overrides` to wire everything together, creating a fully functional application from decoupled parts.

This cohesive architectural strategy ensures ProVAI is robust, maintainable, and ready for future growth.
