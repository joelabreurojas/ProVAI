from pytest_mock import MockerFixture

from src.rag.application.services import RAGService


def test_answer_query_invokes_rag_chain_with_correct_parameters(
    mocker: MockerFixture,
) -> None:
    """
    Verify that the `answer_query` method correctly fetches valid chunk hashes
    and uses them to create a filtered retriever for the LCEL chain.
    """
    mock_llm = mocker.MagicMock()
    mock_vector_store = mocker.MagicMock()
    mock_prompt = mocker.MagicMock()

    mock_retriever = mocker.MagicMock()
    mock_vector_store.as_retriever.return_value = mock_retriever

    mock_chain = mocker.MagicMock()
    mock_chain.invoke.return_value = "This is the final answer."
    mocker.patch.object(RAGService, "_build_rag_chain", return_value=mock_chain)

    rag_service = RAGService(
        llm=mock_llm,
        vector_store=mock_vector_store,
        prompt=mock_prompt,
    )

    # Define the context filter that the CALLER is now responsible for
    test_context_filter = {"content_hash": {"$in": ["hash1", "hash2"]}}

    result = rag_service.answer_query(
        query="test query", context_filter=test_context_filter
    )

    # It should have used those hashes to create a filtered retriever
    mock_vector_store.as_retriever.assert_called_once_with(
        search_kwargs={
            "k": 4,
            "filter": {"content_hash": {"$in": ["hash1", "hash2"]}},
        }
    )

    # It should have invoked the final chain with the user's query
    mock_chain.invoke.assert_called_once_with("test query")
    assert result == "This is the final answer."
