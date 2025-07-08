from pydantic_settings import BaseSettings


class BaseConfig(BaseSettings):
    API_V1_STR: str = "/api/v1"
    TITLE: str = "ProVAI"
    DESCRIPTION: str = "A RAG-powered educational tutor."
    VERSION: str = "0.1.0"
    CONTACT: dict[str, str] = {
        "name": "Joel Abreu Rojas",
        "email": "joelabreurojas@gmail.com",
        "url": "https://github.com/joelabreurojas/ProVAI",
    }
    LICENSE_INFO: dict[str, str] = {
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    }
    TAGS_METADATA: list[dict[str, str]] = [
        {"name": "Status", "description": "API health and monitoring."},
        {"name": "Root", "description": "Say hello to the API."},
    ]


class DevConfig(BaseConfig):
    DB_URL: str = "sqlite:///./databases/provai_dev.db"


class TestConfig(BaseConfig):
    DB_URL: str = "sqlite:///:memory:"


class ProdConfig(BaseConfig):
    DB_URL: str | None = None  # loaded from environment variable


def get_config(env_state: str) -> DevConfig | TestConfig | ProdConfig:
    if env_state == "dev":
        return DevConfig()
    elif env_state == "test":
        return TestConfig()
    elif env_state == "prod":
        return ProdConfig()
    raise ValueError(f"Invalid environment state: {env_state}")
