from multivenv.config import VenvConfig
from multivenv.ext_subprocess import run
from multivenv.run import run_in_venv


def create_venv(config: VenvConfig):
    run(f"virtualenv {config.path}")
    # Need pip-sync installed to install dependencies
    run_in_venv(config, "pip install pip-tools")


def create_venv_if_not_exists(config: VenvConfig):
    if not config.path.exists():
        create_venv(config)
