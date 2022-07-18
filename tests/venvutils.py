from multivenv.config import VenvConfig
from multivenv.run import run_in_venv


def get_installed_packages_in_venv(venv_config: VenvConfig):
    return run_in_venv(venv_config, "pip freeze").output.splitlines()
