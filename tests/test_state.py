from multivenv._state import VenvState, create_venv_state, update_venv_state
from tests.config import BASIC_REQUIREMENTS_HASH
from tests.fixtures.venv_configs import *


def test_create_state(venv_config: VenvConfig):
    venv_config.path.mkdir(parents=True, exist_ok=True)
    shutil.copy(REQUIREMENTS_OUT_PATH, venv_config.requirements_out)
    create_venv_state(venv_config)
    config_path = venv_config.path / "mvenv-state.json"
    assert config_path.exists()
    state = VenvState.load(config_path)
    assert state.requirements_hash == ""
    assert state.needs_sync(venv_config.requirements_out) is True


def test_update_state(compiled_venv_config: VenvConfig):
    venv_config = compiled_venv_config
    update_venv_state(venv_config, venv_config.requirements_out)
    config_path = venv_config.path / "mvenv-state.json"
    assert config_path.exists()
    state = VenvState.load(config_path)
    assert state.requirements_hash == BASIC_REQUIREMENTS_HASH
    assert state.needs_sync(venv_config.requirements_out) is False
