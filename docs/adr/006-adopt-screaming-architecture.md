# ADR-006: Adopt Screaming Architecture

- **Status:** Superseded by [ADR-021](./021-hexagon-and-composition-architecture.md)
- **Date:** 2025-07-12
- **Authors:** Joel Abreu Rojas

---

## Context and Problem Statement

The initial project structure followed a classic "layer-first" Onion Architecture. While correct, this pattern can become difficult to navigate as the project grows, as code for a single feature (like authentication) is spread across multiple top-level directories (`/domain`, `/application`, `/infrastructure`). To ensure high cohesion and long-term maintainability, we need a more modular organizational structure.

---

## Decision Outcome

We will refactor the project to follow a **"Screaming Architecture"** pattern. The top-level `src` directory will be organized by business features (e.g., `auth`, `rag`).

**Within each feature module, we will continue to strictly enforce the principles of Onion Architecture**, maintaining separate `domain`, `application`, and `infrastructure` layers specific to that feature.

A `core` module will house truly cross-cutting concerns like the main application factory, global configuration, and database engine setup.

### Rationale

This approach provides the best of both worlds:

- **High Cohesion & Loose Coupling:** All code related to a single feature is co-located in one place, making it easier to develop and maintain. Changes to the `auth` module are less likely to impact the future `rag` module.
- **Clarity & Scalability:** The project's structure "screams" what it does. This makes navigation intuitive and provides a clear path for scaling, as each feature folder is a "proto-microservice" that could be extracted in the future.
- **Architectural Purity:** It allows us to maintain the strict, inward-pointing dependency rules of Onion Architecture within the clean, high-level boundaries of each feature.

---

## Consequences

### Positive Consequences

- The codebase will be significantly more modular and easier to navigate.
- The risk of creating unintended dependencies between features is reduced.
- The project is architecturally prepared for future growth and potential migration to microservices.

### Negative Consequences

- There is a slight increase in the number of directories and initial boilerplate. This is an accepted trade-off for long-term maintainability.
