# ADR-010: Refactor Domain Model to Assistant/Chat Nomenclature

- **Status:** Superseded by [ADR-015](./015-refactoring-to-tutor-model.md)
- **Date:** 2025-08-22
- **Authors:** @joelabreurojas

---

## Context and Problem Statement

After implementing the initial headless engine, the "explain it to a stranger" test revealed a critical flaw in our domain model's terminology. The concepts of `Chat` (as a classroom) and `Session` (as a chat) were ambiguous and did not align with the intuitive mental model of students and teachers. This ambiguity made the system's purpose difficult to explain and would have led to a confusing user experience. We needed to establish a definitive, unambiguous, and professional ubiquitous language for our core domain.

---

## Decision Outcome

We will perform a complete refactoring of the project's domain model, services, and documentation to adopt the following, superior nomenclature:

| Old Name     | **Definitive New Name** | The Real-World Analogy                                         |
| :----------- | :---------------------- | :------------------------------------------------------------- |
| `Chat`       | `Assistant`             | A teacher creates a specialized **Assistant** for their class. |
| `Session`    | `Chat`                  | A student starts a private **Chat** with that Assistant.       |
| `ChatMember` | `Enrollment`            | A student is **Enrolled** with an Assistant to gain access.    |
| `src/chat`   | `src/assistant`         | The feature module is named after the core entity it manages.  |

### Rationale

This new model was chosen because it is architecturally and conceptually superior in every way:

1.  **Resolves All Ambiguity:** The term `Assistant` perfectly captures the entity's role as a support tool for a teacher, avoiding the implication that ProVAI is a replacement for a human-led class.
2.  **Intuitive User Model:** The user story is now crystal clear: "A teacher creates an `Assistant` and enrolls `Students`. Students then have `Chats` with the `Assistant`." This is instantly understandable.
3.  **Handles Domain Complexity:** The model correctly distinguishes between unique instances of a course (e.g., "Math Section 01" and "Math Section 02" are two different `Assistant` records), which was a key requirement.
4.  **Professional & Industry-Standard:** The concepts are now aligned with modern AI and educational software patterns.

---

## Consequences

### Positive Consequences

- The entire project codebase and documentation will be significantly clearer and easier to understand.
- The product's value proposition is easier to explain to users, stakeholders, and evaluators.
- The architecture is now perfectly aligned with our user-centric product vision.

### Negative Consequences

- This decision requires a significant, one-time refactoring effort across the entire codebase, including models, services, tests, and all documentation. This is an accepted cost for the massive gain in long-term clarity and maintainability.
