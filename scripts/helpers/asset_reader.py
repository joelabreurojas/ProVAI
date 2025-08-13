import sys
from pathlib import Path

import yaml


def main() -> None:
    """
    Parses asset YAML files and prints details for shell scripting.
    Example: python -m scripts.helpers.asset_reader llm default
    """
    config_dir = Path(__file__).parent.parent.parent / "assets"

    asset_type = sys.argv[1]
    asset_name = sys.argv[2]

    if asset_type == "llm":
        config = yaml.safe_load((config_dir / "llms.yml").read_text())
        asset_key = config.get("default") if asset_name == "default" else asset_name
        asset = config[asset_key]
        url = f"https://huggingface.co/{asset['repo_id']}/resolve/main/{asset['filename']}"
        print(f"{asset['filename']} {url}")

    elif asset_type == "doc":
        config = yaml.safe_load((config_dir / "sample_docs.yml").read_text())
        asset_key = config.get("default") if asset_name == "default" else asset_name
        asset = config[asset_key]
        print(f"{asset['name']} {asset['url']}")


if __name__ == "__main__":
    main()
