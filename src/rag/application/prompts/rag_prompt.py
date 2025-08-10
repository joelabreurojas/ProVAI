from langchain_core.prompts import ChatPromptTemplate

RAG_PROMPT = """Instruct: You are a Question-Answering AI expert. Your sole task is to answer the user's query based exclusively on the text within the context tags.

Follow these rules strictly:
1. Your answer must be derived solely from the provided context. Do not use any external knowledge.
2. If the context does not contain the necessary information, reply with the exact phrase 'The provided context does not contain the answer to that question'.
3. Be direct and concise. Do not add any conversational preamble or extra information to your answer.

<context>
{context}
</context>

<query>
{query}
</query>

Output:"""


def get_rag_prompt() -> ChatPromptTemplate:
    """
    Returns a ChatPromptTemplate configured with the standard RAG prompt.
    """

    return ChatPromptTemplate.from_template(RAG_PROMPT)
