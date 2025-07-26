from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.config import DevConfig, ProdConfig, TestConfig


class _EnvironmentSettings(BaseSettings):
    """Reads environment variables from the .env file."""

    SECRET_KEY: str = ""
    ENV_STATE: str = ""
    DB_URL: str = ""
    LANGCHAIN_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )


def _validate_settings(env: _EnvironmentSettings) -> None:
    """Validates environment variables from the .env file."""
    if env.ENV_STATE not in ["dev", "test", "prod"]:
        raise ValueError("ENV_STATE must be 'dev', 'test', or 'prod'.")

    if not env.SECRET_KEY:
        raise ValueError("SECRET_KEY is a required environment variable.")

    if env.ENV_STATE == "dev" and not env.LANGCHAIN_API_KEY:
        raise ValueError("LANGCHAIN_API_KEY must be set in the 'dev' environment.")

    if env.ENV_STATE == "prod" and not env.DB_URL:
        raise ValueError("DB_URL must be set in the 'prod' environment.")


def _load_settings() -> DevConfig | TestConfig | ProdConfig:
    """Returns the application settings object."""
    env = _EnvironmentSettings()

    _validate_settings(env)

    if env.ENV_STATE == "dev":
        return DevConfig(
            SECRET_KEY=env.SECRET_KEY,
            LANGCHAIN_API_KEY=env.LANGCHAIN_API_KEY,
        )

    if env.ENV_STATE == "test":
        return TestConfig(SECRET_KEY=env.SECRET_KEY)

    assert env.DB_URL is not None
    return ProdConfig(SECRET_KEY=env.SECRET_KEY, DB_URL=env.DB_URL)


settings = _load_settings()
