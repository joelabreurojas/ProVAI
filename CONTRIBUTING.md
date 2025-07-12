# Contributing to ProVAI

Welcome to the ProVAI project! We're excited to have you on the team. To ensure our project remains high-quality, maintainable, and easy to work on, we adhere to a simple set of development guidelines.

This document is our single source of truth for the development workflow.

## Guiding Philosophy

Our primary philosophy is **"Keep It Simple."** This applies to our code, architecture, and processes. We favor clarity and simplicity over unnecessary complexity.

## Development Workflow

All development work, from new features to bug fixes, follows our Kanban workflow and must adhere to our merge policy.

### The ProVAI Merge Policy

Since this is a private repository on a free plan, we cannot use GitHub's automated branch protection rules. Instead, we manually enforce these rules as a team. **Adherence to this policy is non-negotiable.**

**1. All Work Must Be on a Feature Branch**

- No developer will ever push a commit directly to the `main` branch.
- For every new issue, create a descriptively named branch from `main`.
- **Branch Naming Convention:** `[type]/[issue-number]-[short-description]`
  - **Examples:**
    - `feature/m1-issue-8-branch-policy`
    - `bugfix/m3-issue-31-fix-login-button`
    - `chore/m2-issue-15-update-benchmarks`

**2. All Merges Must Go Through a Pull Request**

- The only way code gets into `main` is by merging an approved Pull Request.
- When you create a PR, link it to the corresponding issue using GitHub's "Development" sidebar.

**3. All Status Checks Must Pass**

- A Pull Request is **not ready for review** until the CI pipeline (GitHub Actions) has run and all checks are green (✅).
- If CI fails, you are responsible for fixing it on your branch _before_ requesting a review.

**4. All Pull Requests Must Be Peer-Reviewed and Approved**

- A Pull Request **cannot be merged** until the other team member has reviewed the code and formally "Approved" it.
- **Process for the Author:**
  1.  Open the PR.
  2.  Verify that CI is passing.
  3.  Assign the other team member as the "Reviewer."
- **Process for the Reviewer:**
  1.  Review the code for correctness, clarity, and adherence to our standards.
  2.  If changes are needed, use the "Request changes" feature and provide clear, actionable comments.
  3.  If the code is good, click "Approve."

### Code Quality and Tooling

We use a suite of tools to maintain high code quality. These checks are run automatically in our CI pipeline.

- **Dependency Management:** All dependencies are managed in `pyproject.toml` and locked with `uv.lock`. Use `uv sync` to install them.
- **Linting & Formatting:** We use `ruff` to enforce a consistent code style. Before committing, you can run `tox -e fix` to automatically format your code.
- **Type Checking:** We use `mypy` in strict mode. All new code must be fully type-hinted. Run `tox -e check` to check your code.
- **Testing:** We use `pytest`. All new features should be accompanied by corresponding unit or end-to-end tests. Run `tox -e test` to execute the test suite.

### Architecture

This project follows the principles of **Onion Architecture**. Please respect the separation of layers:

- **`src/domain`**: Core business models and logic. Knows nothing about other layers.
- **`src/application`**: Services and use cases. Orchestrates the domain logic. Depends only on the domain layer.
- **`src/infrastructure`**: External concerns like the FastAPI app, database connections, and third-party API clients. Depends on the application layer.

By following these simple guidelines, we can build a robust, high-quality, and successful product together.
