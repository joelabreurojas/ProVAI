from pydantic_settings import BaseSettings, SettingsConfigDict

from src.config import BaseConfig, DevConfig, ProdConfig, TestConfig


class _EnvironmentSettings(BaseSettings):
    """Internal class to load raw variables from a .env file."""

    ENV_STATE: str = "dev"
    DB_URL: str | None = None
    SECRET_KEY: str | None = None
    LANGCHAIN_TRACING_V2: str = "false"
    LANGCHAIN_ENDPOINT: str | None = None
    LANGCHAIN_API_KEY: str | None = None
    LANGCHAIN_PROJECT: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


def _load_settings() -> BaseConfig:
    """Load validated environment variables."""
    settings = _EnvironmentSettings()

    _validate_settings(settings)

    if settings.ENV_STATE == "dev":
        return DevConfig(
            SECRET_KEY=settings.SECRET_KEY,
            LANGCHAIN_TRACING_V2=settings.LANGCHAIN_TRACING_V2,
            LANGCHAIN_ENDPOINT=settings.LANGCHAIN_ENDPOINT,
            LANGCHAIN_API_KEY=settings.LANGCHAIN_API_KEY,
            LANGCHAIN_PROJECT=settings.LANGCHAIN_PROJECT,
        )

    if settings.ENV_STATE == "test":
        return TestConfig(SECRET_KEY=settings.SECRET_KEY)

    return ProdConfig(SECRET_KEY=settings.SECRET_KEY, DB_URL=settings.DB_URL)


def _validate_settings(settings: BaseConfig) -> BaseConfig:
    if settings.ENV_STATE not in ["dev", "test", "prod"]:
        raise ValueError("ENV_STATE must be 'dev', 'test' or 'prod'.")

    if not settings.SECRET_KEY:
        raise ValueError("SECRET_KEY is a required environment variable.")

    if settings.ENV_STATE == "prod" and not settings.DB_URL:
        raise ValueError("DB_URL must be set in the 'prod' environment.")


# The single, validated settings object the rest of the app will import.
settings = _load_settings()
