# ADR-019: Centralized API Error Handling Strategy

- **Status:** Accepted
- **Date:** 2025-08-24
- **Authors:** @joelabreurojas

---

## Context and Problem Statement

A professional API must return error responses that are consistent, predictable, and informative. A naive approach where each endpoint formats its own error messages leads to an inconsistent client experience and mixes presentation concerns with business logic.

We needed a centralized, robust strategy for handling all application-specific errors and translating them into a standard JSON format for our API.

---

## Decision Outcome

We have implemented a three-part centralized error handling strategy:

1.  **`AppException` Base Class:** A custom base exception class (`src/core/application/exceptions/app_exception.py`) from which all our custom business exceptions inherit. It defines the standard attributes: `status_code`, `error_code`, and `message`.
2.  **`ErrorCode` Enum:** A central enum (`src/core/domain/errors.py`) that defines all unique, application-wide error codes. This allows clients to programmatically identify errors without parsing message strings.
3.  **Global Exception Handler:** A FastAPI exception handler (`@app.exception_handler(AppException)`) is registered in our application factory. This single function is responsible for catching any `AppException` that bubbles up to the API layer and formatting it into a standard JSON response.

### Rationale

This pattern is the professional standard for API error handling:

-   **Single Source of Truth:** All error messages and their corresponding HTTP status codes are defined in one place (the feature-specific exception classes), making them easy to manage and keep consistent.
-   **Clean Services:** Our application services are now pure business logic. They simply `raise UserAlreadyExistsError()` without needing to know anything about HTTP or JSON. This is a perfect separation of concerns.
-   **Robust and Predictable API:** This strategy guarantees that *all* of our business logic errors will be translated into a consistent, well-formatted JSON response for the frontend, which is a hallmark of a high-quality, developer-friendly API.

---

## Consequences

- **Positive:** Our API is significantly more robust, predictable, and easier for a client to consume. Our application services are cleaner and more focused.
- **Negative:** None. This is a foundational best practice for building professional web applications.
