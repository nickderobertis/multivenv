from multivenv._delete import delete_venv
from tests.fixtures.venvs import *


def test_delete_venv(synced_venv: VenvConfig):
    venv_config = synced_venv

    assert venv_config.path.exists()
    delete_venv(venv_config)
    assert not venv_config.path.exists()
