# ADR-003: Prioritize `llama-cpp-python` over Ollama for MVP

- **Status:** Accepted
- **Date:** 2025-07-06
- **Authors:** Joel Abreu Rojas

---

## Context and Problem Statement

The core of the ProVAI engine requires running a local Large Language Model (LLM) for text generation. The choice of the tool used to serve and interact with this model has significant implications for resource consumption, development complexity, and performance, especially given our strict hardware constraints (8GB RAM, CPU-only inference). We need to select a serving strategy that provides the best balance of performance and control while minimizing operational overhead for the MVP.

---

## Considered Options

1.  **Direct Integration via `llama-cpp-python`:** Use the `llama-cpp-python` library directly within our FastAPI application process. The application itself would be responsible for loading the model into memory and calling it.
2.  **External Server via Ollama:** Use Ollama as a separate, background server process to manage and serve the LLM. Our FastAPI application would then make HTTP requests to the local Ollama API to interact with the model.
3.  **Docker Model Runner:** Use the experimental Docker Model Runner feature to serve the model as a containerized, OpenAI-compatible API.

---

## Decision Outcome

**Chosen Option:** Option 1. For the MVP, we will use the **`llama-cpp-python` library directly** within the ProVAI application.

### Rationale

This decision was made based on a direct analysis of our primary project constraints:

- **Minimal Resource Overhead (The Decisive Factor):** Every running process consumes a baseline amount of RAM. On an 8GB system where the LLM itself will consume a significant portion of memory, adding another persistent server process like Ollama creates unnecessary memory pressure. By integrating `llama-cpp-python` directly, the LLM lives inside the same process as our FastAPI application, eliminating the overhead of a separate server and giving us the most efficient memory footprint possible.
- **Maximum Control & Simplicity:** A direct library integration gives us fine-grained control over the model's lifecycle. We can load it when the application starts and unload it when it stops, all within our Python code. This is simpler to manage and debug than orchestrating a separate server process. There is no need to manage inter-process communication or worry about the Ollama server being down.
- **Architectural Purity:** Our Onion Architecture dictates that external concerns should be handled in the `infrastructure` layer. A direct library integration allows us to create a clean `LLMService` in our application layer that uses `llama-cpp-python` as an implementation detail. This service can be easily swapped out later to call a cloud API without changing the core application logic. Using Ollama would tie our application more tightly to a specific local hosting solution.
- **Production Readiness:** While Ollama is excellent for local experimentation, `llama-cpp-python` is a foundational library that is also suitable for production use within a custom-built inference server, giving us a clearer path to a scalable "Run" phase architecture.

Option 3 (Docker Model Runner) was rejected for the MVP because it is still an experimental feature and introduces another layer of containerization that adds complexity without providing a clear benefit over the direct library approach for our specific use case.

---

## Consequences

### Positive Consequences

- The total RAM usage of the ProVAI application will be minimized, which is critical for stability on our target hardware.
- The application is fully self-contained, with no dependency on a separate, running server process, making local development and debugging simpler.
- The architecture remains clean and modular, with the LLM interaction neatly encapsulated in a service layer.

### Negative Consequences

- We lose the convenience features provided by Ollama, such as its easy model downloading and management CLI. The team will be responsible for manually downloading and managing the GGUF model files. This is an acceptable trade-off for the performance and control benefits.
