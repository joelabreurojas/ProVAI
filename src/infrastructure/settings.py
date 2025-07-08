from pydantic_settings import BaseSettings, SettingsConfigDict

from src.config import get_config


class EnvironmentSettings(BaseSettings):
    ENV_STATE: str | None = None
    DB_URL: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )


env_settings = EnvironmentSettings()

if env_settings.ENV_STATE is None:
    raise ValueError("ENV_STATE is not set. Check your configuration.")

if env_settings.ENV_STATE == "prod" and env_settings.DB_URL is None:
    raise ValueError("DB_URL is not set. Check your configuration.")

settings = get_config(env_settings.ENV_STATE, env_settings.DB_URL)
