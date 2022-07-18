import os
import shlex
import subprocess
from typing import Mapping, NamedTuple, Optional

from pydantic import BaseModel


class CLIResult(BaseModel):
    stdout: str
    stderr: str
    exit_code: int

    def __str__(self) -> str:
        output = ""
        if self.exit_code == 0:
            output += f"Exited with code {self.exit_code}."
        if self.stderr:
            output += f"\nStderr:\n{self.stderr}"
        if self.stdout:
            output += f"\nStdout:\n{self.stdout}"
        return output


def run(
    command: str,
    env: Optional[Mapping[str, str]] = None,
    extend_existing_env: bool = False,
) -> CLIResult:
    use_env = env
    if env is not None:
        if extend_existing_env:
            use_env = os.environ.copy()
            use_env.update(env)
        else:
            use_env = env
    result = subprocess.run(
        command, capture_output=True, check=True, env=use_env, shell=True
    )
    return CLIResult(
        stdout=result.stdout.decode(),
        stderr=result.stderr.decode(),
        exit_code=result.returncode,
    )


class FirstArgAndCommand(NamedTuple):
    first_arg: str
    command: str


def split_first_arg_of_command_from_rest(command: str) -> FirstArgAndCommand:
    args = shlex.split(command)
    return FirstArgAndCommand(args[0], " ".join(args[1:]))
