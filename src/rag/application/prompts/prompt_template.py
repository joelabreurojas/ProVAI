from langchain_core.prompts import ChatPromptTemplate

# This template is the instruction set for the LLM.
# 1. It sets the persona ("You are an expert assistant...").
# 2. It gives a clear instruction ("Use the following retrieved context...").
# 3. It provides a crucial guardrail ("If you don't know the answer...").
# 4. It defines placeholders for the dynamic content ({context}, {question}).
RAG_PROMPT_TEMPLATE = """
You are an expert assistant for answering questions based on provided context.
Your goal is to provide accurate and concise answers.

Use the following retrieved context to answer the user's question.
If you don't know the answer from the context, just say that you don't know.
Do not make up an answer or provide information not present in the context.
Provide only the answer to the question, do not add any other information.

<context>
{context}
</context>

Question: {question}

Answer: """


def get_rag_prompt() -> ChatPromptTemplate:
    """
    Returns a ChatPromptTemplate configured with the standard RAG prompt.
    """

    return ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
