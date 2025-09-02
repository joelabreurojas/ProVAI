from pytest_mock import MockerFixture

from src.api.ai.application.services.embedding_service import EmbeddingService
from src.api.core.application.services.asset_service import AssetConfig


def test_get_embedding_model_loads_and_caches(mocker: MockerFixture) -> None:
    """
    Tests that the embedding model is loaded correctly and that the
    result is cached on subsequent calls.
    """
    TEST_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

    mock_asset_config = mocker.MagicMock(spec=AssetConfig)
    mock_asset_config.name = TEST_MODEL_NAME

    mock_asset_manager = mocker.MagicMock()
    mock_asset_manager.get_embedding_model_config.return_value = mock_asset_config

    mocker.patch(
        "src.api.ai.application.services.embedding_service.get_asset_manager_service",
        return_value=mock_asset_manager,
    )
    mock_fastembed_class = mocker.patch(
        "src.api.ai.application.services.embedding_service.TextEmbedding"
    )

    service = EmbeddingService()

    model_instance_1 = service.get_embedding_model()
    model_instance_2 = service.get_embedding_model()

    mock_fastembed_class.assert_called_once_with(model_name=TEST_MODEL_NAME)

    mock_asset_manager.get_embedding_model_config.assert_called_once()
    assert model_instance_1 is model_instance_2
