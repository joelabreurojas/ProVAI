from pydantic_settings import BaseSettings, SettingsConfigDict

from src.config import get_config


class EnvironmentSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ENV_STATE: str = "dev"


env_settings = EnvironmentSettings()
settings = get_config(env_settings.ENV_STATE)
