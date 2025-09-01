# ADR-004: Prioritize Streamlit over HTMX/Alpine.js for MVP UI

- **Status:** Superseded by [ADR-020](./020-pivot-frontend-to-fastapi-htmx.md)
- **Date:** 2025-06-29
- **Authors:** Joel Abreu Rojas

---

## Context and Problem Statement

The ProVAI project requires a functional web-based user interface for its MVP. This includes views for user authentication, chat session management, and the core chat interaction itself. Given that the two-person development team's expertise is in backend Python and they have **no prior experience with modern frontend frameworks**, the choice of UI technology presents a significant project risk. We must select a framework that minimizes the learning curve and maximizes development velocity to meet our tight 4-5 month timeline, while still delivering a usable and functional interface.

---

## Considered Options

1.  **Pure Python Framework (Streamlit):** Use Streamlit, a Python-native library, to build the entire user interface. This allows developers to create web apps using only Python code.
2.  **Lightweight JavaScript Enhancement (HTMX/Alpine.js):** Build a traditional server-side rendered application using FastAPI (with Jinja2 templates) and enhance it with the HTMX and Alpine.js libraries for interactivity.
3.  **Full JavaScript Framework (e.g., React, Vue):** Build a full single-page application (SPA) frontend that communicates with our FastAPI backend.

---

## Decision Outcome

**Chosen Option:** Option 1. For the MVP, we will build the entire user interface **exclusively with Streamlit**.

### Rationale

This decision is driven directly by our most critical project constraints: team skills and timeline.

- **Mitigates Skill-Gap Risk:** The development team's primary strength is Python. HTMX/Alpine.js, while simpler than a full SPA framework, still requires a solid understanding of modern JavaScript, DOM manipulation, and frontend build tooling. By choosing Streamlit, we allow the team to leverage their existing expertise and build the entire application in a single language, drastically reducing the learning curve and the risk of getting bogged down in unfamiliar frontend challenges.
- **Maximizes Development Velocity:** Streamlit is designed for extreme speed. Building a functional chat interface with components like `st.chat_message` and `st.sidebar` can be accomplished in a matter of hours or days, not weeks. For a team on a 4-5 month timeline, this rapid prototyping capability is a massive strategic advantage. It allows us to deliver a usable MVP far more quickly and focus the majority of our engineering effort on the complex backend RAG engine.
- **Sufficient for MVP Functionality:** While Streamlit may not offer the granular control or visual polish of a custom HTML/CSS solution, it is more than capable of delivering all the core functionality required for the MVP: user authentication forms, a two-panel layout with a sidebar, a chat input box, and a message display area. It perfectly aligns with the MVP goal of prioritizing function over form.
- **Defers Complexity:** HTMX/Alpine.js remains an excellent choice for a future "Walk" phase enhancement. Once the core backend is stable and deployed, the team can dedicate time to learning these technologies and potentially rebuilding the UI for a more polished V2. This decision is about strategic sequencing, not permanent rejection.

Option 3 (Full JS Framework) was rejected immediately as it would require learning an entire new ecosystem and would be impossible to deliver within the project's timeline and team structure.

---

## Consequences

### Positive Consequences

- The development timeline for the MVP user interface is significantly reduced and de-risked.
- The team can remain focused on a single language (Python), increasing overall productivity.
- A functional, testable, and deployable product can be delivered much faster.

### Negative Consequences

- We will have less granular control over the final look and feel of the UI compared to a custom HTML/CSS solution. The UI may not perfectly match the "three-panel layout" from the original vision for the MVP.
- Streamlit has known limitations regarding complex state management and highly custom interactive components. This is an acceptable trade-off for the MVP, as our initial requirements are simple.
