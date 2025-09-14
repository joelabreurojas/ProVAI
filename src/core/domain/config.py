from pydantic import BaseModel


class _BaseConfig(BaseModel):
    """Defines the shared configuration for all environments."""

    # Application metadata
    TITLE: str = "ProVAI"
    DESCRIPTION: str = "A RAG-powered educational tutor."
    VERSION: str = "0.1.0"
    API_ROOT_PATH: str = "/api/v1"

    # General information
    CONTACT: dict[str, str] = {
        "name": "Joel Abreu Rojas",
        "email": "joelabreurojas@gmail.com",
        "url": "https://github.com/joelabreurojas/ProVAI",
    }
    LICENSE_INFO: dict[str, str] = {
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    }

    # Environment variables
    SECRET_KEY: str
    DB_URL: str
    ENV_STATE: str

    # Security settings
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    MAX_UPLOAD_SIZE_MB: int = 20


class DevConfig(_BaseConfig):
    """Development-specific settings."""

    DB_URL: str = "sqlite:///./databases/provai_dev.db"


class TestConfig(_BaseConfig):
    """Test-specific settings."""

    DB_URL: str = "sqlite:///:memory:"


class ProdConfig(_BaseConfig):
    """Production-specific settings."""

    pass
