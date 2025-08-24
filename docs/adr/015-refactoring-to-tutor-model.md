# ADR-015: Refactoring of the Core Domain Model to Tutor/Chat

- **Status:** Accepted
- **Date:** 2025-08-24
- **Authors:** @joelabreurojas

---

## Context and Problem Statement

After a series of architectural refinements, a final, critical review of our domain terminology was required. The nomenclature chosen in [ADR-010](./010-refactor-domain-model-to-assistant-nomenclature.md), while an improvement, still used the generic term "Assistant." This did not fully capture the specific, educational purpose of our application and lacked the professional clarity we strive for. This ADR documents the final and definitive decision on our core domain language.

---

## Decision Outcome

We will perform the final refactoring of the project's domain model, services, and documentation to adopt the **`Tutor/Chat`** model. This decision **supersedes** the `Assistant/Chat` model proposed in ADR-010.

**The Definitive Nomenclature:**

| Generic Concept         | **Final Name** | The Real-World Analogy                                                |
| :---------------------- | :------------- | :-------------------------------------------------------------------- |
| The Knowledgeable Entity| `Tutor`        | A teacher creates a specialized **Tutor** for their course.             |
| The Conversation        | `Chat`         | A student starts a private **Chat** with that Tutor.                  |
| Membership Link         | `tutor_students` | A student is enrolled as a member of a Tutor's class.                 |

### Rationale

This final model was chosen because it is architecturally and conceptually superior in every way:

1.  **Perfect Domain Specificity:** The word "Tutor" is hyper-specific to education and instantly "screams" the application's purpose. It is impossible to misunderstand.
2.  **Perfect Connotation:** An "Assistant" is a passive tool that performs tasks. A "Tutor" is an active guide that helps you learn. This perfectly aligns with our project's proactive, supportive, and personalized vision.
3.  **Resolves All Ambiguity:** The user story is now crystal clear: "A teacher creates a `Tutor` for their course, uploads `Documents` to it, and enrolls `Students`. Each student then starts their own private `Chat` with that `Tutor` to learn."

---

## Consequences

- **Positive:** The entire project's codebase and documentation will be significantly clearer. The product's value proposition is easier to explain. The architecture is now perfectly aligned with our user-centric product vision.
- **Negative:** This required a final, disciplined refactoring effort across the entire codebase. This cost was accepted for the massive gain in long-term clarity and maintainability.
