from pydantic import BaseModel


class BaseConfig(BaseModel):
    """Defines the application's configuration schema."""

    TITLE: str = "ProVAI"
    DESCRIPTION: str = "A RAG-powered educational tutor."
    VERSION: str = "0.1.0"
    LICENSE_INFO: dict[str, str] = {
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    }
    TAGS_METADATA: list[dict[str, str]] = [
        {"name": "Status", "description": "API health and monitoring."},
        {"name": "Root", "description": "Say hello to the API."},
    ]
    JWT_SECRET_KEY: str  # Must be provided by the environment loader
    JWT_ALGORITHM: str = "HS26"
    JWT_TOKEN_EXPIRE_MINUTES: int = 30


class DevConfig(BaseConfig):
    """Defines the development environment configuration schema."""

    DB_URL: str = "sqlite:///./databases/provai_dev.db"

    LANGCHAIN_TRACING_V2: str = "true"
    LANGCHAIN_API_KEY: str  # Must be provided by the environment loader
    LANGCHAIN_ENDPOINT: str = "https://api.langchain.plus"
    LANGCHAIN_PROJECT: str = "ProVAI"


class TestConfig(BaseConfig):
    """Test-specific settings."""

    DB_URL: str = "sqlite:///:memory:"


class ProdConfig(BaseConfig):
    """Production-specific settings."""

    DB_URL: str  # Must be provided by the environment loader
