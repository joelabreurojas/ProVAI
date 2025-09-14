# ADR-021: Pivot Frontend from Streamlit to FastAPI+HTMX

- **Status:** Accepted
- **Date:** 2025-08-31
- **Authors:** @joelabreurojas

---

## Context and Problem Statement

The project's initial plan was to build the user interface with Streamlit. The primary rationale was to leverage the team's deep Python expertise and accelerate the delivery of a Minimum Viable Product. However, as our backend architecture matured into a highly professional, decoupled, and performance-oriented system, a fundamental architectural conflict became apparent.

Streamlit operates as an opinionated, "all-in-one" framework with a "rerun-on-interaction" model. This creates a "black box" that sacrifices the very principles of control, performance, and architectural purity that we have fought so hard to establish in our backend. We require a UI strategy that is a natural extension of our core architecture, not a departure from it.

---

## Decision Outcome

We will **completely abandon Streamlit** for the primary user-facing application.

The new, definitive frontend stack for ProVAI will be a tightly integrated, high-performance solution built directly on our existing FastAPI application:

1.  **Server & Templating:** **FastAPI + Jinja2**
2.  **Styling:** **Tailwind CSS**
3.  **Server Interactivity:** **HTMX**
4.  **Client-Side Interactivity:** **Alpine.js**

---

## Rationale

This decision is a direct parallel to the architectural principles that led us to choose `llama-cpp-python` over a managed service like Ollama. It is a strategic choice in favor of performance, flexibility, and architectural consistency.

| Aspect                          | Streamlit (The "Ollama" Approach)                                                                                                                                      | FastAPI + HTMX/Alpine (The "`llama-cpp`" Approach)                                                                                                                          |
| :------------------------------ | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Control**                     | **Low.** We operate within Streamlit's world, with limited control over the final HTML, network requests, and application lifecycle. It is an opinionated "black box." | **Maximum.** We have 100%, fine-grained control over every line of HTML, every CSS class, and every HTTP request. It is a transparent "white box."                          |
| **Performance**                 | **Lower.** The "rerun-on-interaction" model is inherently less efficient for complex UIs, leading to higher latency and a less responsive feel.                        | **Higher.** We are serving static HTML and small, targeted snippets. This is an incredibly lightweight and fast paradigm that results in a near-instant user experience.    |
| **Architecture**                | **Conflicting.** It introduces a second, separate web server and state model, fighting our clean FastAPI + Onion architecture.                                         | **Cohesive.** The UI is a natural extension of our existing FastAPI application, served from the same process. It is one single, unified system.                            |
| **Storage (Docker Image Size)** | **Larger.** Requires the full Streamlit library and all of its numerous transitive dependencies, resulting in a bloated production image.                              | **Minimal.** The final Docker image only needs FastAPI and Jinja2. The frontend assets are lightweight static files, resulting in a lean, secure, and fast-to-deploy image. |

**Conclusion:** The FastAPI + HTMX/Alpine stack is leverages our core architectural philosophy. It is more flexible, more performant, and a more professional and scalable solution in the long term.

---

## Consequences

### Positive Consequences

- The entire application will be served from a single, cohesive FastAPI process, simplifying our architecture and deployment.
- The user experience will be significantly faster and more responsive.
- Our final Docker image will be leaner, more secure, and cheaper to store and run.
- The development process fully leverages the team's existing skills in HTML/CSS/JS, allowing for the creation of a truly high-quality, custom UI.

### Negative Consequences

- This represents a significant pivot, invalidating the previous Streamlit-based UI code. This is an accepted cost for the massive gain in quality and architectural integrity.
- The initial setup for the templating, static files, and Tailwind build process is more complex than a simple `streamlit run` command.
