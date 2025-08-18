from langchain_core.prompts import ChatPromptTemplate

RAG_PROMPT = """
Instruct: Answer the user's query based only on the following context. If the context does not contain the answer, you must say "I don't know".

Context: {context}

Query: {query}

Output:"""


def get_rag_prompt() -> ChatPromptTemplate:
    """
    Returns a ChatPromptTemplate configured with the standard RAG prompt.
    """

    return ChatPromptTemplate.from_template(RAG_PROMPT)
