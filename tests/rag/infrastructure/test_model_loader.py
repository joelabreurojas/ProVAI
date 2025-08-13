import pytest
from pytest_mock import MockerFixture

from src.rag.application.exceptions.model_errors import (
    ModelLoadError,
    ModelNotFoundError,
)
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
    mock_llamacpp = mocker.patch("src.rag.infrastructure.model_loader.LlamaCpp")
    mock_llamacpp.side_effect = Exception("Mocked LlamaCpp loading error")

    model_loader.get_llm.cache_clear()

    with pytest.raises(ModelLoadError):
        model_loader.get_llm()
