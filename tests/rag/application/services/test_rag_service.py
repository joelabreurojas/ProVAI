from pytest_mock import MockerFixture

from src.rag.application.services.rag_service import RAGService


def test_answer_query_invokes_rag_chain_with_correct_parameters(
    mocker: MockerFixture,
) -> None:
    """
    Verify that the `answer_query` method correctly orchestrates the call to its
    internal, pre-configured LCEL `rag_chain`.
    """
    # Mock dependencies
    mock_llm = mocker.MagicMock()
    mock_vector_store = mocker.MagicMock()
    mock_prompt = mocker.MagicMock()

    # Mock retriever and its | operator
    mock_retriever = mocker.MagicMock()
    mock_vector_store.as_retriever.return_value = mock_retriever

    # Patch _build_rag_chain to return a mock chain
    mock_chain = mocker.MagicMock()
    mock_chain.invoke.return_value = "This is the final, correct answer."
    mocker.patch.object(
        RAGService,
        "_build_rag_chain",
        return_value=mock_chain,
    )
    rag_service = RAGService(
        llm=mock_llm,
        vector_store=mock_vector_store,
        prompt=mock_prompt,
    )

    query = "Why is the sky blue?"
    chat_id = 123
    result = rag_service.answer_query(query, chat_id)

    # Assert that the final chain's invoke was called with the query string
    mock_chain.invoke.assert_called_once_with(query)
    assert result == "This is the final, correct answer."
