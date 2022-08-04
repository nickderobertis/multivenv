from pathlib import Path

from multivenv._config import VenvConfig
from multivenv._create import create_venv_if_not_exists
from multivenv._find_reqs import find_requirements_file
from multivenv._run import ErrorHandling, run_in_venv
from multivenv._state import update_venv_state


def sync_venv(config: VenvConfig, errors: ErrorHandling = ErrorHandling.RAISE):
    create_venv_if_not_exists(config, errors=errors)
    requirements_file = find_requirements_file(config)
    pip_tools_sync(config, requirements_file)
    update_venv_state(config, requirements_file)
    if config.post_sync:
        for command in config.post_sync:
            result = run_in_venv(config, command, errors=errors)
            if errors == ErrorHandling.PROPAGATE and result.exit_code != 0:
                exit(result.exit_code)


def pip_tools_sync(config: VenvConfig, requirements_file: Path):
    run_in_venv(
        config,
        f"pip-sync {requirements_file}",
        stream=False,
        errors=ErrorHandling.RAISE,
    )
