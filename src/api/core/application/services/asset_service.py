from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel


class AssetConfig(BaseModel):
    """A Pydantic model to represent a configured asset."""

    name: str
    repo_id: str | None = None
    filename: str | None = None
    url: str | None = None


class AssetManagerService:
    """A service to manage and provide configuration for external assets."""

    def __init__(self, assets_dir: Path):
        self._llms_config = self._load_yaml(assets_dir / "llms.yml")
        self._embed_config = self._load_yaml(assets_dir / "embedding_models.yml")
        self._docs_config = self._load_yaml(assets_dir / "sample_docs.yml")

    def _load_yaml(self, path: Path) -> dict[str, Any]:
        with open(path, "r") as f:
            config: dict[str, Any] = yaml.safe_load(f)
            return config

    def get_llm_config(self, name: str | None = None) -> AssetConfig:
        if name is None:
            name = self._llms_config["default"]
        return AssetConfig(**self._llms_config[name])

    def get_embedding_model_config(self, name: str | None = None) -> AssetConfig:
        if name is None:
            name = self._embed_config["default"]
        return AssetConfig(**self._embed_config[name])

    def get_sample_doc_config(self, name: str | None = None) -> AssetConfig:
        if name is None:
            name = self._docs_config["default"]
        return AssetConfig(**self._docs_config[name])
