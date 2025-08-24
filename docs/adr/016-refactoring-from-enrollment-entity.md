# ADR-016: Refactoring from Enrollment Entity to a Many-to-Many Relationship

- **Status:** Accepted
- **Date:** 2025-08-24
- **Authors:** @joelabreurojas

---

## Context and Problem Statement

The initial domain model included a dedicated `Enrollment` entity to manage the relationship between a `User` and a `Tutor`. This entity contained a `role` field to specify if the user was a "teacher" or a "student" for that specific Tutor.

However, a critical architectural review revealed that this model was redundant and overly complex. The user's role within the context of a Tutor could be **derived** from more fundamental relationships, making a dedicated `Enrollment` table an unnecessary layer of abstraction that violated our "Keep It Simple" philosophy.

---

## Considered Options

1.  **Keep the `Enrollment` Entity:** Maintain the explicit `Enrollment` table and a corresponding `EnrollmentService`. This is a common pattern but adds significant complexity (more tables, services, and code).
2.  **Remove `Enrollment` (The Chosen Path):** Eliminate the `Enrollment` entity entirely. The teacher's role is defined by the direct `Tutor.teacher_id` foreign key. A student's role is defined simply by their membership in a new `tutor_students` many-to-many association table.

---

## Decision Outcome

**Chosen Option:** Option 2. We have completely **removed the `Enrollment` entity** and its associated service.

### Rationale

This decision was made because it is architecturally and conceptually superior in every way:

1.  **Massive Simplification:** This change eliminated an entire database table, a SQLAlchemy model, multiple Pydantic schemas, and a dedicated service. The codebase is now significantly smaller and easier to understand.
2.  **Architectural Purity (Single Source of Truth):** The user's role is no longer stored in a separate table; it is now *derived* from the fundamental relationships in the domain model.
    - **A user is a "teacher" of a Tutor if `user.id == tutor.teacher_id`.**
    - **A user is a "student" of a Tutor if their `user.id` is present in the `tutor_students` table for that `tutor.id`.**
    This is a more robust and less error-prone design.
3.  **Improved Cohesion:** All logic related to managing a Tutor's members (inviting, enrolling, authorizing) is now cohesively located within the `TutorService`.

---

## Consequences

- **Positive:** The entire project's codebase is simpler, cleaner, more robust, and easier to maintain. The domain model is a perfect, elegant reflection of the real-world relationships.
- **Negative:** None. This is a rare, purely beneficial architectural refactoring.
