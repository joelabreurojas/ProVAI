# ADR-021: The Definitive Application Architecture

- **Status:** Accepted
- **Date:** 2025-09-12
- **Authors:** [@joelabreurojas](https://github.com/joelabreurojas)

---

## Context and Problem Statement

Throughout the foundational phase of ProVAI, our architecture has undergone a series of rapid and necessary evolutions. Our initial plans, while functional, contained inconsistencies, circular dependencies, and violations of the Single Responsibility and DRY principles. The project required a single, unified, and architecturally pure blueprint that could support long-term scalability and maintainability for both the backend API and the frontend UI.

---

## Decision Outcome

We have adopted an architecture based on the **Composition Root** pattern.

The ProVAI application is structured as a single FastAPI server that assembles two distinct "application areas" (`api` and `ui`) on top of a pure, foundational `core` module.

1.  **The `core` Module (The Foundation/Provider):**
    - It contains all shared, cross-cutting infrastructure (the app factory, database connection, middleware definitions, discovery utilities).
    - The `create_app` function in `src/core/infrastructure/app.py` is the one and only place in the application that knows about both the `api` and `ui` areas.

2.  **The `api` and `ui` Modules (The Consumer Areas):**
    - These are independent, top-level consumer areas. `api` is responsible for serving JSON. `ui` is responsible for serving HTML.
    - They depend **only** on the `core` module. They have **zero knowledge** of each other.

3.  **The "Foreman" Modules (`api/module.py`, `ui/module.py`):**
    - Each consumer area has its own `module.py` file, which acts as the "foreman" for that area.
    - Its single responsibility is to use the discovery utilities from `core` to find and register all of its own features (routers, templates, etc.).

---

## Rationale

This architecture is the superior and final choice because it perfectly embodies professional software engineering principles:

- **Single Responsibility Principle:** Each module (`core`, `api/module`, `ui/module`, `app.py`) now has one, clear, and unambiguous job.
- **Inversion of Control:** The dependency flow is a perfect, one-way street (`api` -> `core`, `ui` -> `core`). The foundation does not know about the pillars being built upon it. This eliminates circular dependencies and makes the system robust.
- **Don't Repeat Yourself (DRY):** The logic for discovering features is now a single, generic utility in `core`, which is then reused by both the `api` and `ui` foremen.

---

## Consequences

- The project has a clear, scalable, and maintainable structure that can easily accommodate new features or even new consumer areas (like a `websockets` area) in the future.
- The codebase is easy to reason about, and the risk of creating unintended dependencies is drastically reduced.
- All previous architectural ADRs that conflict with this definitive pattern are now formally superseded.
