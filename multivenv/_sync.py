from pathlib import Path

from multivenv._config import VenvConfig
from multivenv._create import create_venv_if_not_exists
from multivenv._find_reqs import find_requirements_file
from multivenv._run import ErrorHandling, run_in_venv
from multivenv._state import update_venv_state


def sync_venv(config: VenvConfig):
    reqs_path = pip_tools_sync(config)
    update_venv_state(config, reqs_path)


def pip_tools_sync(config: VenvConfig) -> Path:
    create_venv_if_not_exists(config)
    requirements_file = find_requirements_file(config)
    run_in_venv(
        config,
        f"pip-sync {requirements_file}",
        stream=False,
        errors=ErrorHandling.RAISE,
    )
    return requirements_file
