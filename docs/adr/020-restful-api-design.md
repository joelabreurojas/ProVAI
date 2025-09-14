# ADR-020: RESTful, Resource-Oriented API Design

- **Status:** Accepted
- **Date:** 2025-08-25
- **Authors:** @joelabreurojas

---

## Context and Problem Statement

With the backend services architecturally pure and decoupled, a definitive methodology for exposing their functionality to the outside world was required. The design of the public API is the most critical contract in the system, as it dictates how all future clients (including our own Streamlit UI) will interact with the application.

A poorly designed API would be confusing, inconsistent, and difficult to scale. We needed to choose a professional, industry-standard pattern that was both powerful and aligned with our "Keep It Simple" philosophy.

---

## Considered Options

1.  **RPC-style (Remote Procedure Call):** Design the API around "verbs" or actions, such as `/createTutor` or `/enrollStudentInTutor`. This is simple for individual actions but becomes inconsistent and difficult to manage as the system grows.
2.  **GraphQL:** A powerful, flexible query language for APIs. While excellent for complex data needs, it introduces a significant amount of new complexity (schemas, resolvers, tooling) that violates our "Keep It Simple" principle for the MVP.
3.  **RESTful, Resource-Oriented (The Chosen Path):** Design the API around "nouns" or resources, using standard HTTP methods to operate on them. This is the undisputed industry standard for building predictable, scalable, and maintainable web APIs.

---

## Decision Outcome

**Chosen Option:** Option 3. The ProVAI API is a **pure, RESTful, resource-oriented API.**

This decision is implemented through the following definitive principles:

1.  **The API is Organized Around Resources:** Every core entity in our domain has its own dedicated resource endpoint. This is a direct reflection of our Screaming Architecture.
    - `/auth`: For authentication operations.
    - `/tutors`: For managing the `Tutor` resource.
    - `/invitations`: For managing the `Invitation` resource.
    - `/enrollments`: For creating `Enrollment` relationships.
    - `/chats`: For managing the `Chat` resource.

2.  **We Use Standard HTTP Methods:** All operations use the standard HTTP verbs for their intended purpose (`POST` to create, `GET` to read, etc.).

3.  **The API is Stateless:** All requests are authenticated using self-contained JWT Bearer Tokens. The server does not maintain session state.

4.  **The `Chat` Endpoint is the Primary Orchestrator:** As defined in [ADR-017](./017-the-chat-orchestrator-pattern.md), the `/chats` endpoints are the primary entry point for high-level user interactions, orchestrating the other, more specialized resources.

### Rationale

This RESTful approach was chosen because it is architecturally and conceptually superior:

- **Professional and Predictable:** It is the industry standard. Any developer, on any team, can immediately understand the structure and purpose of our API.
- **Scalable and Future-Proof:** This design makes it trivial to add new resources in the future without breaking existing ones. It is the perfect foundation for API versioning.
- **Perfect Architectural Alignment:** The resource-oriented nature of the API is a beautiful and direct reflection of our feature-based Screaming Architecture on the backend. The code "screams" the API, and the API "screams" the code.

---

## Consequences

- **Positive:** Our API is clean, professional, intuitive, and easy for any client (including our own UI) to consume. It is the perfect, robust "front door" for our application.
- **Negative:** A pure RESTful approach can sometimes be "chattier" than other methods (e.g., requiring multiple requests to get nested data). This is a well-understood and accepted trade-off for the massive gains in clarity and maintainability.
