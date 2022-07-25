from multivenv._config import VenvConfig
from multivenv._ext_subprocess import run
from multivenv._run import ErrorHandling, run_in_venv
from multivenv._state import create_venv_state


def create_venv(config: VenvConfig):
    run(f"virtualenv {config.path}", stream=False)
    # Need pip-sync installed to install dependencies
    run_in_venv(
        config, "pip install pip-tools", stream=False, errors=ErrorHandling.RAISE
    )
    create_venv_state(config)


def create_venv_if_not_exists(config: VenvConfig):
    if not config.path.exists():
        create_venv(config)
