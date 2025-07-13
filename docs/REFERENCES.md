# Core Concepts & References

This document serves as a central hub, linking our project's key architectural decisions and development tasks to our detailed research notes. It is the bridge between our "why" and our "how."

---

## **1. Foundational Project Philosophy**

- **[The 7-Step Software Design Guide](https://github.com/joelabreurojas/notes/blob/main/06-software-engineering/design-principles/7-step-software-design-guide.md):** The formal process we use for designing all new features.
- **[10 Tips for Simpler, More Maintainable Code](https://github.com/joelabreurojas/notes/blob/main/06-software-engineering/design-principles/10-tips-for-simpler-code.md):** The day-to-day coding standards we adhere to.
- **[The Done Manifesto](https://github.com/joelabreurojas/notes/blob/main/06-software-engineering/design-principles/the-done-manifesto.md):** Our philosophy for avoiding perfectionism and maintaining momentum.
- **[Code Diagnosis Principles](https://github.com/joelabreurojas/notes/blob/main/06-software-engineering/python-best-practices/code-diagnosis.md):** The framework we use for reviewing and refactoring existing code.

---

## **2. Core AI & RAG Concepts**

- **[AI Concepts Explained](https://github.com/joelabreurojas/notes/blob/main/01-ai-foundations/ai-concepts-explained.md):** Defines the relationship between AI, ML, Deep Learning, and GenAI.
- **[Large Language Models (LLMs)](https://github.com/joelabreurojas/notes/blob/main/03-generative-ai-and-llms/large-language-models.md):** The core technology we are augmenting.
- **[Comprehensive RAG Resources](https://github.com/joelabreurojas/notes/blob/main/03-generative-ai-and-llms/retrieval-augmented-generation/comprehensive-rag-resources.md):** Our master list of tutorials and papers that guide our RAG implementation.

### **2.1. Indexing**

- **[Vector Databases](https://github.com/joelabreurojas/notes/blob/main/03-generative-ai-and-llms/data-representation/vector-databases.md):** Explains why we use ChromaDB for semantic search.
- **[Word Embeddings](https://github.com/joelabreurojas/notes/blob/main/03-generative-ai-and-llms/data-representation/word-embeddings.md):** Explains how our text is converted into a searchable format.
- **[The 5 Levels of Text Splitting](https://github.com/joelabreurojas/notes/blob/main/03-generative-ai-and-llms/retrieval-augmented-generation/text-splitting-levels.md):** Justifies our MVP choice of `RecursiveCharacterTextSplitter`.
- **[Advanced Indexing: RAPTOR](https://github.com/joelabreurojas/notes/blob/main/03-generative-ai-and-llms/retrieval-augmented-generation/raptor-and-long-context.md):** A "Run" phase technique for future exploration.

### **2.2. Retrieval & Generation**

- **[Advanced RAG Concepts Overview](https://github.com/joelabreurojas/notes/blob/main/03-generative-ai-and-llms/retrieval-augmented-generation/advanced-rag-concepts.md):** Defines our "Walk" and "Run" phase goals (CRAG, Self-RAG, etc.).
- **[Graph RAG Concepts](https://github.com/joelabreurojas/notes/blob/main/03-generative-ai-and-llms/retrieval-augmented-generation/graph-rag.md):** Foundational reading for our long-term vision.

---

## **3. Software & Infrastructure**

- **[The Perfect Dockerfile](https://github.com/joelabreurojas/notes/blob/main/06-software-engineering/python-best-practices/perfect-dockerfile.md):** The principles our project's `Dockerfile` is built upon.
- **[Python Type Hints Best Practices](https://github.com/joelabreurojas/notes/blob/main/06-software-engineering/python-best-practices/type-hints.md):** Justifies our strict use of type hints and `Protocols`.
- **[REST API Design Principles](https://github.com/joelabreurojas/notes/blob/main/06-software-engineering/api-design/rest-api-design.md):** The guidelines we follow for building our FastAPI backend.
