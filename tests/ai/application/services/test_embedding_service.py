from pytest_mock import MockerFixture

from src.ai.application.services import EmbeddingService


def test_get_embedding_model_loads_and_caches(mocker: MockerFixture) -> None:
    """
    Tests that the embedding model is loaded from HuggingFace and that the
    result is cached on subsequent calls.
    """
    mock_asset_config = mocker.MagicMock(name="BAAI/bge-small-en-v1.5")
    mock_asset_manager = mocker.MagicMock()
    mock_asset_manager.get_embedding_model_config.return_value = mock_asset_config

    mock_hf_embeddings_class = mocker.patch(
        "src.ai.application.services.embedding_service.HuggingFaceEmbeddings"
    )

    mocker.patch(
        "src.core.dependencies.get_asset_manager_service",
        return_value=mock_asset_manager,
    )

    service = EmbeddingService()

    model_instance_1 = service.get_embedding_model()
    model_instance_2 = service.get_embedding_model()

    # The HuggingFaceEmbeddings class should have been initialized, but only ONCE.
    mock_hf_embeddings_class.assert_called_once_with(
        model_name="BAAI/bge-small-en-v1.5",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    # Both calls should return the exact same cached instance.
    assert model_instance_1 is model_instance_2
