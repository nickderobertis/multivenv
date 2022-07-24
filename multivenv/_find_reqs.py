from pathlib import Path

from multivenv import _platform
from multivenv._config import VenvConfig
from multivenv.exc import CompiledRequirementsNotFoundException


# TODO: Add options to make requirement finding for sync more flexible (strict versus loose)
def find_requirements_file(config: VenvConfig) -> Path:
    current_python_version = _platform.get_python_version()
    current_platform = _platform.get_platform()
    exact_path = config.requirements_out_path_for(
        current_python_version, current_platform
    )
    if exact_path.exists():
        return exact_path

    # Try matching only on one of version or platform
    platform_path = config.requirements_out_path_for(None, current_platform)
    if platform_path.exists():
        return platform_path
    version_path = config.requirements_out_path_for(current_python_version, None)
    if version_path.exists():
        return version_path

    # Fall back to default requirements.txt
    fallback_path = config.requirements_out
    if not fallback_path.exists():
        raise CompiledRequirementsNotFoundException(
            f"Could not find requirements file at any of "
            f"{exact_path}, {platform_path}, {version_path}, or {fallback_path}"
        )
    return fallback_path
