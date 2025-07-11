# ADR-002: Prioritize Local, File-Based Databases for MVP

- **Status:** Accepted
- **Date:** 2025-07-06
- **Authors:** Joel Abreu Rojas

---

## Context and Problem Statement

For the MVP, we require two distinct types of data storage: a relational database for user, chat, and session metadata, and a vector database for storing and searching document embeddings. The choice of database technology for this initial phase has a significant impact on developer setup complexity, resource consumption on our target hardware (8GB RAM), and overall development velocity. We must select a stack that aligns with our core principles of "Keep It Simple" and our strict resource constraints, while not preventing future scalability.

---

## Considered Options

1.  **PostgreSQL for Everything:** Use a single PostgreSQL database instance running in Docker. Use standard tables for relational data and the `pgvector` extension to handle vector storage and similarity search.
2.  **Separate, File-Based Databases (The Chosen Path):** Use SQLite for relational data and ChromaDB (in its default file-based persistence mode) for vector data. Both would run directly within the application's file system without a separate server process.
3.  **Cloud-Hosted Free Tiers:** Use free-tier offerings from cloud providers (e.g., Supabase for Postgres, a free vector DB provider).

---

## Decision Outcome

**Chosen Option:** Option 2. For the MVP, we will use **SQLite** for all relational data and **ChromaDB** for all vector data.

### Rationale

This decision was made because it is the optimal choice when evaluated against our core project constraints:

- **Zero Setup Friction & Maximum Velocity:** SQLite and file-based ChromaDB require zero configuration or server management. They work out-of-the-box with a simple `pip install`. This drastically reduces the time spent on local environment setup and debugging, which is critical for a two-person team on a tight timeline. Option 1 would require managing a separate database container, networking, user credentials, and the installation of a specific extension.
- **Minimal Resource Footprint:** A running PostgreSQL container has a constant RAM and CPU overhead, even when idle. On our target hardware of 8GB RAM, every megabyte is precious and must be reserved for the memory-intensive LLM and embedding models. SQLite and ChromaDB have virtually zero resource footprint when not actively being queried, making them the superior choice for a resource-constrained environment.
- **Architectural Purity:** Using two separate, specialized databases forces us to create clean abstraction layers (the Repository Pattern) in our code. We cannot accidentally write PostgreSQL-specific SQL queries in our application services. This enforces the principles of our Onion Architecture and makes our application services more modular and portable by design.
- **Low-Risk, Deferred Complexity:** This decision is **for the MVP only**. Our Onion Architecture ensures that the database is an infrastructure detail. We have a dedicated Post-MVP issue (`#43: Plan and Execute DB Migration to PostgreSQL`) to handle the migration when the project requires the scalability and concurrency features of a client-server database. We are not creating technical debt; we are strategically deferring complexity.

Option 3 (Cloud-Hosted) was rejected because it violates our "local-first" development principle for the MVP and introduces network latency and external dependencies, which adds complexity and risk.

---

## Consequences

### Positive Consequences

- The development environment for new team members is incredibly simple: `git clone` and `docker-compose up`.
- Our local development setup will consume the absolute minimum amount of RAM and CPU, leaving maximum resources available for running and testing the AI models.
- Our data access layer will be, by necessity, cleanly abstracted, which is a significant long-term architectural benefit.

### Negative Consequences

- We will need to allocate time in a future milestone to perform the migration to PostgreSQL. This is a known and accepted future cost.
- SQLite has known limitations with high-concurrency write operations. This is an acceptable trade-off for the MVP phase, which will have a very limited number of users.
- We lose the ability to perform complex SQL `JOIN` operations between our relational user data and our vector data, which would be possible with `pgvector`. This capability is not required for any MVP features.
