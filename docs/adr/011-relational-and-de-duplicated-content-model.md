# ADR-011: Relational and De-Duplicated Content Model

- **Status:** Accepted
- **Date:** 2025-08-22
- **Authors:** @joelabreurojas

---

## Context and Problem Statement

The core of the ProVAI application involves managing documents and their constituent text chunks. A simple data model would link a `Chunk` directly to a `Document` and a `Document` directly to an `Assistant`. However, this naive approach has two critical long-term flaws:

1.  **Data Duplication:** If two different documents contain the exact same paragraph (e.g., a shared legal disclaimer or a common introductory chapter), a simple model would store and embed that identical text chunk multiple times, wasting storage and computational resources.
2.  **Inflexible Sharing:** A simple model makes it difficult to share a single uploaded `Document` across multiple `Assistants` without creating duplicate records.

We needed a data model that was efficient, scalable, and reflected the many-to-many reality of educational content.

---

## Decision Outcome

We have implemented a **fully relational, de-duplicated content model** using many-to-many relationships.

1.  **Chunk De-duplication:** A `Chunk` is now identified by a unique `content_hash`. The text content itself is stored in the vector database, keyed by this hash. The relational `chunks` table stores only this unique hash. A `document_chunk_link` association table creates a many-to-many relationship, allowing a single, unique chunk to be linked to multiple documents.
2.  **Document Sharing:** A `Document` is a standalone entity. A new `assistant_document_link` association table creates a many-to-many relationship between `Assistants` and `Documents`, allowing a single uploaded document to be included in multiple assistants.

### Rationale

-   **Efficiency:** This model is highly storage-efficient. A text chunk, no matter how many times it appears across the entire system, is only stored and embedded **once**. This saves significant space and reduces the cost of embedding.
-   **Idempotency:** The `IngestionService` is now idempotent by design. Re-uploading the same document is a safe and cheap operation, as the service will recognize all existing chunks and simply create new links.
-   **Robustness:** This model allows for safe "garbage collection." When a document is deleted, we can confidently check if its associated chunks are still linked to any *other* documents. If they are not, we can safely delete them from both the relational and vector databases.
-   **Scalability:** This model provides a clean foundation for future features, such as a centralized "document library" that teachers can pull from.

---

## Consequences

-   The application logic (especially for ingestion and deletion) is more complex than a simple foreign-key model. This is an accepted trade-off for the massive gains in efficiency and robustness.
-   The retrieval logic in the `RAGService` is also more complex, requiring a relational query to gather valid chunk hashes before performing the vector search. This is an accepted trade-off for ensuring strict data isolation between assistants.
