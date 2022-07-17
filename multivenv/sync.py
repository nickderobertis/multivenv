
from multivenv.config import VenvConfig
from multivenv.ext_subprocess import CLIResult
from multivenv.run import run_in_venv


def sync_venv(config: VenvConfig):
    pip_tools_sync(config)


def pip_tools_sync(config: VenvConfig) -> CLIResult:
    return run_in_venv(
        config, f"pip-sync {config.requirements_in} -o {config.requirements_out}"
    )
