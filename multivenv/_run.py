import platform
from enum import Enum

from multivenv._config import VenvConfig
from multivenv._ext_subprocess import (
    CLIResult,
    run,
    split_first_arg_of_command_from_rest,
)


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
    new_command = _venv_command(config, command)
    return run(new_command, stream=stream, check=errors.should_check)


def _venv_command(config: VenvConfig, command: str) -> str:
    if platform.system() == "Windows":
        return _venv_command_windows(config, command)
    return _venv_command_unix(config, command)


def _venv_command_unix(config: VenvConfig, command: str):
    executable, command = split_first_arg_of_command_from_rest(command)
    bin_path = config.path / "bin" / executable
    venv_command = f"{bin_path} {command}"
    return venv_command


def _venv_command_windows(config: VenvConfig, command: str):
    executable, command = split_first_arg_of_command_from_rest(command)
    scripts_path = config.path / "Scripts"
    bin_path = scripts_path / f"{executable}.exe"
    venv_command = f"{bin_path} {command}"
    return venv_command
