import os
from enum import Enum

from multivenv._config import VenvConfig
from multivenv._ext_subprocess import CLIResult, run
from multivenv.exc import VenvNotSyncedException


class ErrorHandling(str, Enum):
    IGNORE = "ignore"
    RAISE = "raise"
    PROPAGATE = "propagate"

    @property
    def should_check(self) -> bool:
        return self == ErrorHandling.RAISE


def run_in_venv(
    config: VenvConfig,
    command: str,
    stream: bool = True,
    errors: ErrorHandling = ErrorHandling.PROPAGATE,
) -> CLIResult:
    return _activate_and_run(config, command, stream=stream, errors=errors)


def _activate_and_run(
    config: VenvConfig,
    command: str,
    stream: bool = True,
    errors: ErrorHandling = ErrorHandling.PROPAGATE,
) -> CLIResult:
    bin_path = config.path / "bin"
    if not bin_path.exists():
        raise VenvNotSyncedException(
            f"Must sync the {config.name} venv as it is a persistent venv and auto-sync is disabled."
        )
    current_path = os.getenv("PATH")
    extra_env = {
        "VIRTUAL_ENV": str(config.path),
        "PATH": f"{bin_path}{os.path.pathsep}{current_path}"
        if current_path
        else str(bin_path),
    }
    return run(
        command,
        stream=stream,
        check=errors.should_check,
        env=extra_env,
        extend_existing_env=True,
    )
