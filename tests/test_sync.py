from multivenv.compile import compile_venv_requirements
from multivenv.config import VenvConfig
from multivenv.run import run_in_venv
from multivenv.sync import sync_venv
from tests.fixtures.venv_configs import *
from tests.venvutils import get_installed_packages_in_venv


def test_sync(compiled_venv_config: VenvConfig):
    venv_config = compiled_venv_config

    assert not venv_config.path.exists()
    sync_venv(venv_config)
    assert venv_config.path.exists()
    packages = get_installed_packages_in_venv(venv_config)
    assert "appdirs==1.4.4" in packages
