from multivenv._state import (
    VenvState,
    create_venv_state,
    update_venv_state,
    venv_needs_sync,
)
from tests.config import BASIC_REQUIREMENTS_HASH
from tests.fixtures.venv_configs import *


def test_create_state(venv_config: VenvConfig):
    venv_config.path.mkdir(parents=True, exist_ok=True)
    shutil.copy(REQUIREMENTS_OUT_PATH, venv_config.requirements_out)
    create_venv_state(venv_config)
    config_path = venv_config.path / "mvenv-state.json"
    assert config_path.exists()
    state = VenvState.load(config_path)
    assert state.hash_for(venv_config.requirements_out) is None
    assert (
        state.needs_sync(venv_config.sync_paths(venv_config.requirements_out)) is True
    )


def test_update_state(compiled_venv_config: VenvConfig):
    venv_config = compiled_venv_config
    update_venv_state(venv_config, venv_config.requirements_out)
    config_path = venv_config.path / "mvenv-state.json"
    assert config_path.exists()
    state = VenvState.load(config_path)
    assert state.hash_for(venv_config.requirements_out) == BASIC_REQUIREMENTS_HASH
    assert (
        state.needs_sync(venv_config.sync_paths(venv_config.requirements_out)) is False
    )


def test_needs_sync_bad_state_json(compiled_venv_config: VenvConfig):
    venv_config = compiled_venv_config
    config_path = venv_config.path / "mvenv-state.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text("bad state")
    assert venv_needs_sync(venv_config)


def test_needs_sync_bad_state_wrong_types(compiled_venv_config: VenvConfig):
    venv_config = compiled_venv_config
    config_path = venv_config.path / "mvenv-state.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    state = VenvState.create_empty(venv_config.path)
    state.hashes = "not a dict"
    state.settings.custom_config_folder = config_path.parent
    state.save()
    assert venv_needs_sync(venv_config)


def test_needs_sync_changed_extra_file(compiled_venv_config: VenvConfig):
    venv_config = compiled_venv_config
    extra_path = venv_config.path.parent.parent / "extra.txt"
    extra_path.write_text("extra")
    venv_config.auto_sync_changed = [extra_path]
    update_venv_state(venv_config, venv_config.requirements_out)
    config_path = venv_config.path / "mvenv-state.json"
    assert config_path.exists()
    state = VenvState.load(config_path)
    assert state.hash_for(venv_config.requirements_out) == BASIC_REQUIREMENTS_HASH
    assert state.hash_for(extra_path) == "ea9f91b2cda019730f2891bd12a7a4d6"
    assert (
        state.needs_sync(venv_config.sync_paths(venv_config.requirements_out)) is False
    )
    extra_path.write_text("new extra")
    state = VenvState.load(config_path)
    assert (
        state.needs_sync(venv_config.sync_paths(venv_config.requirements_out)) is True
    )
