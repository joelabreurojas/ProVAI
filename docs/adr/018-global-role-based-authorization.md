# ADR-018: Global Role-Based Authorization for Action Guarding

- **Status:** Accepted
- **Date:** 2025-08-24
- **Authors:** @joelabreurojas

---

## Context and Problem Statement

Our initial "pure" contextual authorization model (where a user's role was determined solely by their relationship to a `Tutor`) had a critical security and business logic flaw: there was nothing to stop a user with a "student" account from creating their *own* `Tutor` and becoming a "teacher" in that context.

This would violate the business rules of the platform and create a potential security risk. We needed a simple, robust mechanism to act as a high-level gatekeeper for core system actions.

---

## Decision Outcome

We have re-introduced a non-nullable, global **`role` attribute on the `User` model.**

Our authorization strategy is now a definitive two-level check:

1.  **Global Role Check (Gatekeeper):** For high-level actions (like creating a Tutor), the service first checks the user's global `role`. If `user.role` is not `"teacher"`, the action is immediately denied with an `InsufficientPermissionsError`.
2.  **Contextual Ownership/Membership Check:** For actions on a *specific* resource (like uploading a document to Tutor #5), the service then performs the contextual check (is this user the owner of this Tutor, or an enrolled student?).

### Rationale

This two-level system is the professional standard for robust application security:

-   **Security:** It provides a simple, foolproof way to prevent users from performing actions they are fundamentally not allowed to. It is impossible for a student to create a Tutor because the very first check in the service will fail.
-   **Efficiency:** The global role check is fast and happens before any complex database queries for contextual checks, making the system more performant.
-   **Clarity:** It makes the codebase's security model explicit and easy to understand.

---

## Consequences

- **Positive:** The application's security posture is significantly strengthened. The business rules are now enforced at both a global and a contextual level.
- **Negative:** This introduces a small degree of coupling between the `auth` module (which defines the `User` and `role`) and other services that need to perform this check. This is an accepted and necessary trade-off for core security.
