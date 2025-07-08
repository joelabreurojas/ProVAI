# ProVAI - Professor Virtual with AI

ProVAI is an intelligent learning assistant designed to enhance educational experiences through Retrieval-Augmented Generation (RAG).

## Overview

This project aims to build a scalable and intelligent tutor that provides personalized support to students by interacting with course materials.

## Tech Stack (MVP)

- **Architecture:** Onion Architecture
- **Frontend:** Streamlit
- **Backend:** FastAPI
- **Relational DB:** SQLite
- **Vector DB:** ChromaDB
- **AI/ML Models & Tooling:**
  - **LLM:** Phi-2
  - **Embedding Model:** BGE-small-en-v1.5
  - **Orchestration:** LangChain & llama-cpp

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.13+

### Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/joelabreurojas/ProVAI.git
    cd ProVAI
    ```

2.  **Create the environment file:**
    Copy `.env.template` to `.env`. The defaults are configured for development.

    ```bash
    cp .env.template .env
    ```

3.  **Build and run the application:**

    ```bash
    docker compose up --build -d
    ```

4.  **Run database migrations:**

    ```bash
    docker compose exec api alembic upgrade head
    ```

The API will be available at `http://localhost:8000`. You can view the OpenAPI documentation at `http://localhost:8000/docs`.

## License

This project is licensed under the Apache 2.0 License.
