# ProVAI Software Architecture

This document provides a high-level overview of the logical software architecture for the ProVAI project. It explains the core principles that guide how our code is organized and how dependencies are managed.

Our architecture is a synthesis of two key patterns: **Screaming Architecture** for high-level modularity and **Onion Architecture** for implementation-level decoupling.

---

## 1. High-Level Organization: Screaming Architecture

The primary organizational principle of this project is to structure the codebase around its **business capabilities (features)**, not its technical layers. The top-level directories in the `src/` folder "scream" what the application does.

This feature-based structure ensures that all code related to a single domain concept (e.g., Authentication, RAG, Analytics) is highly cohesive and co-located.

### Core Modules:

- **`src/core/`:** This module is an exception to the feature-first rule. It houses truly cross-cutting concerns that are shared by all other modules, such as the main application factory, global configuration, and the shared database engine.
- **`src/feature_name/` (e.g., `src/auth/`):** Each additional module represents a distinct business capability. This modular approach makes the system easier to navigate, maintain, and scale.

---

## 2. Module-Level Implementation: Onion Architecture

Within each high-level feature module, we strictly enforce the principles of **Onion Architecture**. This pattern governs the direction of dependencies and ensures a clean separation of concerns, making our business logic independent of external frameworks and tools.

### The Dependency Rule: All Dependencies Point Inwards

1.  **`domain` (Innermost Layer):**
    - **Responsibility:** Contains the core business entities, value objects, and rules that are central to the feature.
    - **Dependencies:** Has **zero** dependencies on any other layer in the application. It is pure business logic.

2.  **`application` (Middle Layer):**
    - **Responsibility:** Orchestrates the business logic to fulfill application-specific use cases. It defines the abstract interfaces (protocols) for any external operations it needs to perform (e.g., "save a user," "get a document").
    - **Dependencies:** Depends only on the `domain` layer.

3.  **`infrastructure` (Outermost Layer):**
    - **Responsibility:** Contains the concrete implementations of the interfaces defined in the application layer. This includes all interactions with the "outside world": database connections (SQLAlchemy), API endpoints (FastAPI), third-party libraries, etc.
    - **Dependencies:** Depends on the `application` and `domain` layers to implement their contracts.

This layered approach within each feature module makes our codebase highly testable, as the core business logic can be tested in complete isolation from the web server, database, or any other external service.
