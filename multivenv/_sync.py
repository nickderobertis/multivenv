import sys
from pathlib import Path

from multivenv import _platform
from multivenv._config import VenvConfig
from multivenv._create import create_venv_if_not_exists
from multivenv._ext_subprocess import CLIResult
from multivenv._run import run_in_venv
from multivenv.exc import CompiledRequirementsNotFoundException


def sync_venv(config: VenvConfig):
    pip_tools_sync(config)


def pip_tools_sync(config: VenvConfig) -> CLIResult:
    create_venv_if_not_exists(config)
    requirements_file = _find_requirements_file(config)
    return run_in_venv(config, f"pip-sync {requirements_file}", stream=False)


# TODO: Add options to make requirement finding for sync more flexible (strict versus loose)
def _find_requirements_file(config: VenvConfig) -> Path:
    # TODO: better python version matching
    current_python_version = f"{sys.version_info[0]}.{sys.version_info[1]}"
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
