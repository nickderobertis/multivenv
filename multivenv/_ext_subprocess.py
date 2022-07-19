import os
import shlex
import subprocess
from typing import Mapping, NamedTuple, Optional

from pydantic import BaseModel

from multivenv._styles import printer


class CLIResult(BaseModel):
    output: str
    exit_code: int

    def __str__(self) -> str:
        output = ""
        if self.exit_code != 0:
            output += f"Exited with code {self.exit_code}.\n"
        output += self.output
        return output

    def __contains__(self, item):
        return item in str(self)


def run(
    command: str,
    env: Optional[Mapping[str, str]] = None,
    extend_existing_env: bool = False,
    check: bool = True,
    stream: bool = True,
) -> CLIResult:
    use_env = env
    if env is not None:
        if extend_existing_env:
            use_env = os.environ.copy()
            use_env.update(env)
        else:
            use_env = env
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=use_env,
        shell=True,
    )
    buffer = b""
    for c in iter(lambda: process.stdout.read(1), b""):  # type: ignore
        if stream:
            printer.print(c.decode(), end="")
        buffer += c
    process.wait()
    if check and process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, command)

    return CLIResult(
        output=buffer.decode(),
        exit_code=process.returncode,
    )


class FirstArgAndCommand(NamedTuple):
    first_arg: str
    command: str


def split_first_arg_of_command_from_rest(command: str) -> FirstArgAndCommand:
    args = shlex.split(command)
    return FirstArgAndCommand(args[0], " ".join(args[1:]))
