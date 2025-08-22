# ADR-012: The `tox`-driven Quality Assurance Strategy

- **Status:** Accepted
- **Date:** 2025-08-22
- **Authors:** @joelabreurojas

---

## Context and Problem Statement

A modern software project requires a robust, automated, and repeatable process for ensuring code quality. We need a system that can run our linter (`ruff`), type checker (`mypy`), and test suite (`pytest`) consistently in different environments. A common problem in development is the "it works on my machine" syndrome, where local tests pass but fail in the Continuous Integration (CI) environment due to subtle differences in dependencies or configuration. We must eliminate this risk.

---

## Decision Outcome

We have adopted **`tox`** as the **single source of truth** for our entire quality assurance (QA) suite.

1.  **Local Workflow:** Developers will run a single `tox` command locally to execute the full suite of checks in a clean, isolated virtual environment.
2.  **CI Workflow:** Our GitHub Actions CI pipeline is a thin wrapper that performs only two core steps: `pip install tox` and `tox`.

### Rationale

-   **Eliminates Environment Drift:** This is the most critical benefit. By using `tox` in both environments, we guarantee that the commands run by a developer locally are **byte-for-byte identical** to the commands run by the CI server. This completely solves the "it works on my machine" problem.
-   **Simplicity and Speed:** `tox` manages its own virtual environments, caching dependencies between runs. This makes subsequent local test runs significantly faster. It also simplifies the CI `workflow.yml` file down to just two commands, making it cleaner and easier to maintain.
-   **Single Source of Truth:** The `tox.ini` file becomes the definitive "recipe" for our project's quality checks. If we need to add a new check or change a command, we edit it in one single place, and that change is instantly reflected in both local and CI environments.
-   **Reproducibility:** This strategy ensures that any developer, on any machine, can reproduce our full QA process with a single command, which is a hallmark of a professional and well-configured project.

---

## Consequences

-   There is a small, one-time cost of configuring the `tox.ini` file correctly. This is a negligible trade-off for the massive long-term benefits in consistency and reliability.
-   Developers must have `tox` installed or use the provided Docker environment, which includes it.
