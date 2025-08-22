from pytest_mock import MockerFixture

from src.assistant.application.protocols import AssistantRepositoryProtocol
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
    mock_assistant_repo = mocker.MagicMock(spec=AssistantRepositoryProtocol)

    # Simulate the repo returning a list of valid hashes for the assistant
    mock_assistant_repo.get_chunk_hashes_for_assistant.return_value = ["hash1", "hash2"]

    mock_retriever = mocker.MagicMock()
    mock_vector_store.as_retriever.return_value = mock_retriever

    mock_chain = mocker.MagicMock()
    mock_chain.invoke.return_value = "This is the final answer."
    mocker.patch.object(RAGService, "_build_rag_chain", return_value=mock_chain)

    rag_service = RAGService(
        llm=mock_llm,
        vector_store=mock_vector_store,
        prompt=mock_prompt,
        assistant_repo=mock_assistant_repo,
    )

    result = rag_service.answer_query(query="test query", assistant_id=1)

    # It should have first fetched the valid chunk hashes for the assistant
    mock_assistant_repo.get_chunk_hashes_for_assistant.assert_called_once_with(1)

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
