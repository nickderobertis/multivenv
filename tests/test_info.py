import shutil

from multivenv import _platform
from multivenv._config import TargetConfig, VenvConfig
from multivenv._info import SystemInfo, create_venv_info
from multivenv._state import create_venv_state, update_venv_state
from tests.config import BASIC_REQUIREMENTS_HASH
from tests.dirutils import change_directory_to
from tests.fixtures.venv_configs import *


def test_info(venv_config: VenvConfig):
    temp_dir = venv_config.path.parent.parent
    with change_directory_to(temp_dir):
        shutil.copy(REQUIREMENTS_OUT_PATH, venv_config.requirements_out)
        create_venv_state(venv_config)
        info = create_venv_info(venv_config)
        assert info.name == venv_config.name
        assert info.path == venv_config.path
        assert info.exists == venv_config.path.exists()
        assert info.config_requirements.in_path == venv_config.requirements_in
        assert info.config_requirements.out_path == venv_config.requirements_out
        assert info.discovered_requirements.in_path == venv_config.requirements_in
        assert info.discovered_requirements.out_path == venv_config.requirements_out
        assert info.state.needs_sync is True
        assert info.state.requirements_hash == ""
        update_venv_state(venv_config, info.discovered_requirements.out_path)
        new_info = create_venv_info(venv_config)
        assert new_info.state.needs_sync is False
        assert new_info.state.requirements_hash == BASIC_REQUIREMENTS_HASH


def test_system_info():
    info = SystemInfo.from_system()
    current_target = TargetConfig.from_system()
    assert info.version == current_target.version
    assert info.platform == current_target.platform
