import os
import subprocess
from typing import Mapping, NamedTuple, Optional

from pydantic import BaseModel

from multivenv._styles import printer
from multivenv.exc import CommandExitException


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
    char_buffer = b""
    for c in iter(lambda: process.stdout.read(1), b""):  # type: ignore
        char_buffer += c
        if stream:
            try:
                printer.out(char_buffer.decode(), end="")
                char_buffer = b""
            except UnicodeDecodeError:
                char_buffer += c
        buffer += c
    process.wait()
    if check and process.returncode != 0:
        raise CommandExitException(process.returncode, command, buffer.decode())

    return CLIResult(
        output=buffer.decode(),
        exit_code=process.returncode,
    )


class FirstArgAndCommand(NamedTuple):
    first_arg: str
    command: str


def split_first_arg_of_command_from_rest(command: str) -> FirstArgAndCommand:
    # TODO: Support for running binaries with spaces in their names.
    #  This current approach is a bit of a hack. Tried to use shlex.split
    #  and join, but it does not work properly on Windows.
    args = command.split()
    bin = args[0]
    new_command = " ".join(args[1:])
    return FirstArgAndCommand(bin, new_command)
