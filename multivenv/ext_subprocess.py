import shlex
import subprocess
from typing import NamedTuple

from pydantic import BaseModel


class CLIResult(BaseModel):
    stdout: str
    stderr: str


def run(command: str) -> CLIResult:
    result = subprocess.run(shlex.split(command), capture_output=True, check=True)
    return CLIResult(stdout=result.stdout.decode(), stderr=result.stderr.decode())


class FirstArgAndCommand(NamedTuple):
    first_arg: str
    command: str


def split_first_arg_of_command_from_rest(command: str) -> FirstArgAndCommand:
    args = shlex.split(command)
    return FirstArgAndCommand(args[0], " ".join(args[1:]))
