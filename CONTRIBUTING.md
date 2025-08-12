# Contributing to ProVAI

Welcome to the ProVAI project! We're excited to have you on the team. To ensure our project remains high-quality, maintainable, and easy to work on, we adhere to a simple set of development guidelines.

If you have a question or a feature idea, before writing code, please [start a new discussion](https://github.com/joelabreurojas/ProVAI/discussions) first.

## Guiding Philosophy

Our primary philosophy is **"Keep It Simple."** This applies to our code, architecture, and processes. We favor clarity and simplicity over unnecessary complexity.

## Development Workflow

All development work, from new features to bug fixes, follows our [Kanban Workflow](docs/WORKFLOW.md) and must adhere to our merge policy.

### Merge Policy

The following rules are the formal rules for merging code into the `main` branch.

**1. All Work Must Be on a Feature Branch**

- No commit will ever be pushed directly to the `main` branch.
- For every new issue, create a descriptively named branch from `main`.
- **Branch Naming Convention:** `[type]/[milestone]-[issue-number]-[short-description]`
  - **Examples:**
    - `feat/m1-8-branch-policy`
    - `fix/m3-31-update-login-button`
    - `docs/m2-15-add-benchmarks`

**2. All Merges Must Go Through a Pull Request**

- The only way code gets into `main` is by merging a Pull Request.
- The PR serves three critical functions:
  1.  **It triggers the CI pipeline.**
  2.  **It provides a formal opportunity for self-review.**
  3.  **It links the code to the project plan (the GitHub Issue).**

**3. The CI Pipeline is the Gatekeeper**

- A Pull Request is **not ready to merge** until the CI pipeline (GitHub Actions running `tox`) has completed and all checks are green (✅).
- If CI fails, you are responsible for fixing it on your branch before merging.

**4. Merge on Green**

- Once the CI pipeline has passed, you are authorized to merge your own Pull Request.
- Always use the **"Squash and Merge"** option to maintain a clean, readable history on the `main` branch.

### Code Quality and Tooling

We use `tox` as the single source of truth for all quality checks. Run `tox` locally to verify your changes before pushing.

### Architecture

This project follows the principles of **Screaming Architecture** and **Onion Architecture**. Please refer to the [Architecture Overview](docs/ARCHITECTURE.md) for a detailed explanation.
