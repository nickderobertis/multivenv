from multivenv._run import run_in_venv
from tests.fixtures.venvs import *


def test_run_in_venv(synced_venv: VenvConfig):
    assert "appdirs==1.4.4" in run_in_venv(synced_venv, "pip freeze")
