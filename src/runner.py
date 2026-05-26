import json
from typing import Any, Dict


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from a JSON file.

    Args:
        config_path (str): Path to the JSON configuration file

    Returns:
        dict: Configuration dict with attacker, defender, scenarios, formulas sections

    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If JSON is invalid
    """
    with open(config_path, 'r') as f:
        config = json.load(f)

    return config
