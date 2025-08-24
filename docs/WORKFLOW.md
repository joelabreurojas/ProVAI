# ProVAI Project Workflow

The single source of truth for all active and planned work is our official **GitHub Project board**. This board provides a real-time view of the status of every task and milestone.

### Accessing the Kanban Board

The ProVAI GitHub Project board is private. To request access, please contact the project owner, [Joel Abreu Rojas](https://github.com/joelabreurojas). Access is typically granted to collaborators, stakeholders, or academic reviewers who need to see the live status of the project's development.

---

## The Kanban Workflow

Our workflow follows a simple left-to-right progression through six distinct stages. An issue can only move forward, with a clear process for handling work that is blocked or requires further attention.

### 1. 🗄️ Backlog

This is the "idea freezer". It contains **all potential future work** and long-term ideas that are not part of the current, active milestone. Nothing in this column is considered committed work.

- **Entry Criteria:** Any new idea, feature request, or low-priority task.
- **Exit Criteria:** The issue is prioritized and moved into the `Ready` column for an upcoming milestone.

### 2. ✅ Ready

This column contains the **fully planned and prioritized tasks for the current milestone**. It is our immediate to-do list. When a developer is free, they should pull the highest-priority issue from the top of this column.

- **Entry Criteria:** The issue is essential for completing the current milestone.
- **Exit Criteria:** A developer assigns the issue to themselves and moves it to `In Progress`.

### 3. 🚧 In Progress

This column shows what is **actively being developed right now**.

- **Rule:** A developer should have **only one or two issues** in this column at a time to maintain focus.
- **Entry Criteria:** A developer has started working on a task from the `Ready` column.
- **Exit Criteria:** The developer has completed the work on a feature branch and opened a Pull Request. The issue is then moved to `In Review`.

### 4. 🔬 In Review

This column means the work is code-complete, a Pull Request is open, and it is **waiting for the CI pipeline to pass.**

- **Entry Criteria:** A Pull Request has been opened and is ready for its automated checks.
- **Handling Failures:** If the CI pipeline fails, the developer must fix the issues on the _same feature branch_ and push the changes, which automatically re-runs the CI pipeline.
- **Exit Criteria:** The CI pipeline passes successfully (all checks are green ✅). The PR is then ready to be merged.

### 5. 🛑 Stopped

This column is for issues that were `In Progress` or `Ready` but are currently **on hold or blocked**.

- **Entry Criteria:** An issue is blocked by an external dependency or is intentionally paused.
- **Exit Criteria:** The blocker is resolved, and the issue moves back to `In Progress` or `Ready`.

### 6. 🎉 Done

This column contains all completed work. A task is only "Done" when its code has been successfully merged into the `main` branch.

- **Entry Criteria:** The associated Pull Request has been successfully "Squashed and Merged."

---

## Custom Field System (The Legend)

We use a two-part field system to categorize every issue. This helps us filter the board and quickly understand the nature of the work.

### 1. How important is this?

- `priority:critical` - Must be fixed immediately; blocks other work.
- `priority:high` - Essential for the current milestone; a top priority.
- `priority:medium` - Standard task that should be completed in a timely manner.
- `priority:low` - A nice-to-have or optimization that can be deferred.

### 2. What kind of work is this?

- `type:feature` - A new feature or user-facing functionality.
- `type:bug` - A bug fix that corrects incorrect behavior.
- `type:chore` - Maintenance, refactoring, or DevOps tasks that aren't features or bugs.
- `type:research` - A time-boxed investigation or technical spike (e.g., evaluating a new library).
- `type:testing` - A task focused exclusively on adding or improving tests.
- `type:documentation` - A task related to writing or updating documentation.

### 3. What part of the codebase does this touch?

- `module:api` - Related to FastAPI endpoints and the API layer.
- `module:auth` - Related to user authentication and authorization logic.
- `module:database` - Related to the database schema (SQLAlchemy) or migrations (Alembic).
- `module:devops` - Related to Docker, CI/CD (GitHub Actions), or deployment.
- `module:general` - A task that spans multiple modules or is project-wide.
- `module:learning` - Related to the Learning Support Module (e.g., quizzes).
- `module:observability` - Related to logging, metrics, or analytics.
- `module:rag` - Related to the core RAG pipeline (ingestion, retrieval, generation).
- `module:ui` - Related to the Streamlit frontend.
