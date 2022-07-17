from multivenv.config import VenvConfig
from multivenv.create import create_venv_if_not_exists
from multivenv.ext_subprocess import CLIResult
from multivenv.run import run_in_venv


def sync_venv(config: VenvConfig):
    pip_tools_sync(config)


def pip_tools_sync(config: VenvConfig) -> CLIResult:
    create_venv_if_not_exists(config)
    return run_in_venv(config, f"pip-sync {config.requirements_out}")
