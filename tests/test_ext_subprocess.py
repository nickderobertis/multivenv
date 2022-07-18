import subprocess

import pytest

from multivenv.ext_subprocess import run


def test_run_command_with_success():
    result = run("echo 'Hello World'")
    assert result.exit_code == 0
    assert result.output == "Hello World\n"


def test_run_command_with_failure_and_no_raise():
    fake_command = "this-command-does-not-exist"
    result = run(fake_command, check=False)
    assert result.exit_code != 0
    assert "Exited with code 1" in result
    assert f"{fake_command}: not found" in result


def test_run_command_with_failure_and_raise():
    fake_command = "this-command-does-not-exist"
    # TODO: custom error
    with pytest.raises(subprocess.CalledProcessError):
        run(fake_command)
