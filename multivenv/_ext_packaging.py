from typing import Dict, Optional

from packaging.markers import default_environment

Environment = Optional[Dict[str, str]]


def get_default_environment() -> Environment:
    return default_environment()
