import subprocess

from multivenv._run import ErrorHandling, run_in_venv
from multivenv.exc import CommandExitException
from tests.fixtures.venv_configs import *
from tests.fixtures.venvs import *
from tests.osutils import is_not_found_output


def test_run_in_venv(synced_venv: VenvConfig):
    assert "appdirs==1.4.4" in run_in_venv(synced_venv, "pip freeze")


def test_run_in_venv_with_emoji_output(synced_venv: VenvConfig):
    run_in_venv(synced_venv, "pip install black")
    assert "All done! ✨ 🍰 ✨" in run_in_venv(synced_venv, "black .")


def test_run_with_error(synced_venv: VenvConfig):
    with pytest.raises(CommandExitException) as exc_info:
        run_in_venv(synced_venv, "sdfsdfsgsdfgsdfgf", errors=ErrorHandling.RAISE)

    error = exc_info.value
    assert error.exit_code != 0
    assert is_not_found_output(error.output)
    assert is_not_found_output(str(error))


def test_run_binary_not_in_venv(synced_venv: VenvConfig):
    result = run_in_venv(synced_venv, "bash -c 'pip freeze'")
    assert "appdirs==1.4.4" in result
