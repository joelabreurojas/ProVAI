from pytest_mock import MockerFixture

from src.chat.application.protocols import ChatRepositoryProtocol
from src.rag.application.services import RAGService


def test_answer_query_invokes_rag_chain_with_correct_parameters(
    mocker: MockerFixture,
) -> None:
    """
    Verify that the `answer_query` method correctly orchestrates the call to its
    internal, pre-configured LCEL `rag_chain`.
    """
    mock_llm = mocker.MagicMock()
    mock_vector_store = mocker.MagicMock()
    mock_prompt = mocker.MagicMock()
    mock_chat_repo = mocker.MagicMock(spec=ChatRepositoryProtocol)

    mock_chat_repo.get_chunk_hashes_for_chat.return_value = ["hash1", "hash2"]

    mock_retriever = mocker.MagicMock()
    mock_vector_store.as_retriever.return_value = mock_retriever

    mock_chain = mocker.MagicMock()
    mock_chain.invoke.return_value = "This is the final answer."

    mocker.patch.object(RAGService, "_build_rag_chain", return_value=mock_chain)

    rag_service = RAGService(
        llm=mock_llm,
        vector_store=mock_vector_store,
        prompt=mock_prompt,
        chat_repo=mock_chat_repo,
    )

    result = rag_service.answer_query(query="test query", chat_id=1)

    mock_chat_repo.get_chunk_hashes_for_chat.assert_called_once_with(1)

    mock_vector_store.as_retriever.assert_called_once_with(
        search_kwargs={
            "k": 4,
            "filter": {"content_hash": {"$in": ["hash1", "hash2"]}},
        }
    )

    mock_chain.invoke.assert_called_once_with("test query")
    assert result == "This is the final answer."
