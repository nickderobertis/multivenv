from multivenv._config import VenvConfig
from multivenv._info import create_venv_info
from tests.dirutils import change_directory_to
from tests.fixtures.venv_configs import *


def test_info(venv_config: VenvConfig):
    temp_dir = venv_config.path.parent.parent
    with change_directory_to(temp_dir):
        info = create_venv_info(venv_config)
        assert info.name == venv_config.name
        assert info.path == venv_config.path
        assert info.exists == venv_config.path.exists()
        assert info.config_requirements.in_path == venv_config.requirements_in
        assert info.config_requirements.out_path == venv_config.requirements_out
        assert info.discovered_requirements.in_path == venv_config.requirements_in
        assert info.discovered_requirements.out_path is None
