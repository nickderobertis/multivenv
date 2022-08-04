from typing import Dict

from packaging.markers import default_environment

Environment = Dict[str, str]


def get_default_environment() -> Environment:
    return default_environment()
