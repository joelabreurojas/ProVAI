import pytest
from pytest_mock import MockerFixture

from src.core.application.services.asset_service import AssetConfig
from src.rag.application.exceptions import ModelLoadError, ModelNotFoundError
from src.rag.infrastructure import model_loader


def test_get_llm_raises_model_not_found_error_if_file_missing(
    mocker: MockerFixture,
) -> None:
    """
    Tests that get_llm correctly raises ModelNotFoundError when the GGUF file
    does not exist at the configured path.
    """
    mock_path_exists = mocker.patch("pathlib.Path.exists")
    mock_path_exists.return_value = False

    model_loader.get_llm.cache_clear()

    with pytest.raises(ModelNotFoundError) as exc_info:
        model_loader.get_llm()

    assert "phi-2.Q4_K_M.gguf" in str(exc_info.value)


def test_get_llm_raises_model_load_error_on_library_failure(
    mocker: MockerFixture,
) -> None:
    """
    Tests that get_llm correctly wraps a generic exception from the LlamaCpp
    library into our custom ModelLoadError.
    """
    mocker.patch("pathlib.Path.exists", return_value=True)

    mock_llamacpp = mocker.patch("src.rag.infrastructure.model_loader.LlamaCpp")
    mock_llamacpp.side_effect = Exception("Mocked LlamaCpp hardware failure")

    mock_asset_manager = mocker.patch(
        "src.rag.infrastructure.model_loader.get_asset_manager_service"
    )
    mock_asset_manager.return_value.get_llm_config.return_value = AssetConfig(
        name="dummy", filename="dummy.gguf"
    )

    model_loader.get_llm.cache_clear()

    with pytest.raises(ModelLoadError):
        model_loader.get_llm()
