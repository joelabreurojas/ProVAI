from functools import lru_cache

from src.api.core.application.services import AssetManagerService
from src.api.core.constants import PROJECT_ROOT


@lru_cache(maxsize=1)
def get_asset_manager_service() -> AssetManagerService:
    """Provides a singleton instance of the AssetManagerService."""
    assets_dir = PROJECT_ROOT / "assets"
    return AssetManagerService(assets_dir)
