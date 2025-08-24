<h1 align='center'>
    ProVAI
</h1>

<p align='center'>
    <em>An intelligent, RAG-powered AI tutor for education.</em>
</p>

<h6 align='center'>
    <a href="/LICENSE">
        <img alt='Apache 2.0 License' src='https://img.shields.io/static/v1.svg?label=License&message=Apache%202.0&logoColor=d9e0ee&colorA=302d41&colorB=3094FF'/>
    </a>
    <a href="/docs/">
      <img alt='See Documentation' src='https://img.shields.io/static/v1.svg?label=See&message=Documentation&logoColor=d9e0ee&colorA=302d41&colorB=3094FF'/>
  </a>
</h6>

&nbsp;

### ✨ Overview

ProVAI (Professor Virtual with AI) is an intelligent learning tutor designed to enhance educational experiences. It uses a Retrieval-Augmented Generation (RAG) engine to provide personalized support by interacting with teacher-provided course materials.

**ProVAI helps:**

- **Students** to master their course material through:
  - On-demand, context-aware answers grounded in their documents.
  - Automated, non-graded quizzes for effective self-assessment.

- **Teachers** to provide scalable, personalized support with:
  - An AI tutor that handles common student questions 24/7.
  - Privacy-preserving analytics that identify classroom-wide learning gaps.

- **Educational Institutions** to deploy a secure, self-hostable, and resource-efficient AI learning tool.

&nbsp;

### 🚀 Getting Started

> [!NOTE]
> Before you start, make sure you have Docker installed and running.

1.  Clone the repository:

    ```fish
    git clone https://github.com/joelabreurojas/ProVAI.git
    cd ProVAI
    ```

2.  Download assets:

    ```fish
    chmod +x ./scripts/download_assets.sh
    ./scripts/download_assets.sh
    ```

    > This will download the LLM and a sample document.

3.  Configure your environment:

    ```fish
    cp .env.template .env
    ```

    > Open the `.env` file. The comments explain what should be set.

4.  Build and run:

    ```fish
    docker compose watch

    ```

    > Embedding model will be downloaded in the first _run_.

5.  Run database migrations:
    ```fish
    docker compose exec api python -m alembic upgrade head
    ```

<br>

> [!IMPORTANT]
> The API will be available at `http://localhost:8000`.
>
> Check out the OpenAPI documentation at `http://localhost:8000/docs`.

&nbsp;

### 🛠 Tech Stack

ProVAI is built on a foundation of modern, high-performance technologies, guided by professional software engineering principles to ensure it is maintainable, testable, and scalable.

<div align="center">

|      Category       |              Tool              |        Notes         |
| :-----------------: | :----------------------------: | :------------------: |
|  Core Architecture  | Screaming + Onion Architecture |                      |
|  Backend Framework  |            FastAPI             |                      |
|      Frontend       |           Streamlit            |      _for MVP_       |
| Relational Database |             SQLite             |      _for MVP_       |
|   Vector Database   |            ChromaDB            | _file-based for MVP_ |
|  AI Orchestration   |           LangChain            |                      |
|     LLM Serving     |        llama-cpp-python        |                      |
|      LLM Model      |             phi-2              |      _for MVP_       |
|   Embedding Model   |       bge-small-en-v1.5        |                      |
|   Dev Environment   |          Docker & uv           |                      |
|  Quality Assurance  |    tox, pytest, ruff, mypy     |                      |

</div>

&nbsp;

### 🗺 Roadmap

This is a high-level overview of our development milestones, focusing on the path to our Minimum Viable Product (MVP).

**Milestone 1: The Walking Skeleton (Completed)**

- [x] Establish professional project structure, tooling, and CI/CD foundation.

**Milestone 2: The Core Engine (Completed)**
- [x] Implement secure, headless User Authentication.
- [x] Integrate local LLM and Embedding models.
- [x] Build the Document Ingestion and core RAG services.
- [x] Implement the **Chat** and **Message** service for conversation persistence.

**Milestone 3: The Minimum Viable Interface (In Progress)**
- [ ] Build the Streamlit UI for user interaction, login, and document upload.
- [ ] Implement "Teacher" and "Student" role-based access control.
- [ ] Deploy the complete MVP to a public platform.

<details>
  <summary><strong>Post-MVP Vision (Milestone 4):</strong></summary>
  <br>
  <ul>
      <li>Implement the Learning Support module (Quiz Generation, Roadmaps).</li>
      <li>Build the Teacher Analytics Dashboard for classroom insights.</li>
      <li>Explore advanced RAG techniques (Parent Document Retrieval, CRAG).</li>
      <li>Refactor the core engine into a LangGraph state machine for agentic behavior.</li>
      <li>...and much more!</li>
  </ul>
</details>

&nbsp;

### 📌 Disclaimer

> [!WARNING]
> This is an academic project under active development.

- Always verify critical information against the source documents.
- This tool is a study aid, not a substitute for professional instruction.
- This project is provided as is, without any warranty. **Use at your own risk.**

&nbsp;

### 👐 Contribute

- Found a bug? Feel free to open a new [issue](https://github.com/joelabreurojas/ProVAI/issues/new)!
- Have a question or an idea? Join our [community](https://github.com/joelabreurojas/ProVAI/discussions).

Please, read our [Contribution Guidelines](/CONTRIBUTING.md) to take part in the project.
