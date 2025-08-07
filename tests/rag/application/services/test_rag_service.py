from pytest_mock import MockerFixture

from src.rag.application.services.rag_service import RAGService


def test_answer_query_invokes_rag_chain_with_correct_parameters(
    mocker: MockerFixture,
) -> None:
    """
    Verify that the `answer_query` method correctly orchestrates the call to its
    internal, pre-configured LCEL `rag_chain`.
    """
    rag_service = RAGService(
        llm=mocker.MagicMock(),
        vector_store=mocker.MagicMock(),
        prompt=mocker.MagicMock(),
    )

    # Replace the compiled `rag_chain` with a mock to isolate the test.
    mock_rag_chain = mocker.patch.object(rag_service, "rag_chain")
    mock_rag_chain.invoke.return_value = "This is the final, correct answer."

    query = "Why is the sky blue?"
    chat_id = 123
    result = rag_service.answer_query(query, chat_id)

    # Assert that the chain was called with the correct dictionary payload.
    mock_rag_chain.invoke.assert_called_once_with({"query": query, "chat_id": chat_id})

    assert result == "This is the final, correct answer."
