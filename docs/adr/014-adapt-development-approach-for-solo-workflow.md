# ADR-014: Adapt Development Approach for Solo Developer Workflow

- **Status:** Accepted
- **Date:** 2025-08-22
- **Authors:** ProVAI Team

---

## Context and Problem Statement

The project was initiated with a two-person team, and our development process, as documented in [ADR-005](./005-development-approach.md), was designed around this collaborative model. A core tenet of that process was a strict mandatory peer review for all Pull Requests.

The project's core constraint has now changed: the team composition has been reduced to a single developer. Consequently, the mandatory peer review process is no longer feasible and acts as a permanent blocker to merging any new code. We must adapt our workflow to ensure development can proceed efficiently while still maintaining a high standard of code quality.

---

## Considered Options

1.  **Maintain the Existing Process:** Continue to require peer review, effectively blocking all progress. This is not a viable option.
2.  **Abandon All Process:** Remove all quality gates and commit directly to the `main` branch. This would sacrifice all the quality, stability, and traceability we have built and is unacceptable.
3.  **Adapt the Process (The Chosen Path):** Retain the core pillars of our workflow (feature branches, Pull Requests, automated checks) but replace the manual peer review with a formal self-review, making the automated CI/CD pipeline the primary gatekeeper for merges.

---

## Decision Outcome

**Chosen Option:** Option 3. We will adopt a **"Disciplined Solo-Developer Workflow."**

The new merge policy is as follows:

1.  **Feature Branches Remain Mandatory:** All work must be done on a descriptively named feature branch.
2.  **Pull Requests Remain Mandatory:** All merges to `main` must go through a Pull Request. The PR now serves as a formal checkpoint for self-review and as the trigger for our automated checks.
3.  **The CI Pipeline is the New Gatekeeper:** A Pull Request is not ready to merge until the `tox` suite (linting, type checking, testing) has passed completely in GitHub Actions.
4.  **Merge on Green:** Once the CI pipeline is green (✅), the author is authorized to merge their own PR.
5.  **Squash and Merge:** We will continue to exclusively use "Squash and Merge" to maintain a clean history.

### Rationale

-   **Unblocks Development:** This new policy removes the impossible constraint of a peer review, allowing the project to move forward.
-   **Maintains High Quality:** By making the automated CI pipeline the absolute, non-negotiable gatekeeper, we continue to programmatically enforce our standards for code style, correctness, and test coverage.
-   **Preserves Traceability:** The mandatory Pull Request process ensures that every commit on the `main` branch is still linked to a specific GitHub Issue, maintaining a clear and auditable project history.
-   **Promotes Discipline:** The formal self-review step in the PR process encourages a final, critical look at the code before it is merged.

---

## Consequences

-   The project can now proceed at a sustainable pace with a single developer.
-   The risk of introducing a *logical* error that automated tests cannot catch is slightly increased due to the absence of a "second pair of eyes." This is an accepted and understood trade-off. We will mitigate this risk through disciplined self-review and a commitment to comprehensive test coverage.
