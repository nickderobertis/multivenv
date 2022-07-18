from multivenv.config import VenvConfig
from multivenv.info import create_venv_info
from tests.fixtures.venv_configs import *


def test_info(venv_config: VenvConfig):
    info = create_venv_info(venv_config)
    assert info.name == venv_config.name
    assert info.path == venv_config.path
    assert info.exists == venv_config.path.exists()
    assert info.requirements_in == venv_config.requirements_in
    assert info.requirements_out == venv_config.requirements_out
