from pytest_mock import MockerFixture

from src.api.ai.application.services import LLMService


def test_get_llm_loads_model_on_first_call_and_caches(
    mocker: MockerFixture,
) -> None:
    """
    Tests that the LLM is loaded from a file path provided by the AssetManager
    and that the result is cached on subsequent calls.
    """
    mock_asset_config = mocker.MagicMock(filename="fake_model.gguf")
    mock_asset_manager = mocker.MagicMock()
    mock_asset_manager.get_llm_config.return_value = mock_asset_config

    mock_path = mocker.MagicMock()
    mock_path.exists.return_value = True

    mock_llama_class = mocker.patch(
        "src.api.ai.application.services.llm_service.LlamaCpp"
    )

    mocker.patch(
        "src.core.infrastructure.dependencies.get_asset_manager_service",
        return_value=mock_asset_manager,
    )
    mocker.patch(
        "src.api.ai.application.services.llm_service.PROJECT_ROOT",
        mock_path,
    )

    service = LLMService()

    llm_instance_1 = service.get_llm()
    llm_instance_2 = service.get_llm()

    # The loader should have been called, but only ONCE due to caching.
    mock_llama_class.assert_called_once_with(
        model_path=str(mock_path / "models" / "fake_model.gguf"),
        n_ctx=2048,
        n_gpu_layers=0,
        verbose=False,
        n_threads=4,
        n_batch=512,
    )
    # Both calls should return the exact same cached instance.
    assert llm_instance_1 is llm_instance_2
