import shutil
from pathlib import Path

import pytest

from multivenv._config import TargetsUserConfig, VenvConfig, VenvUserConfig
from tests.config import (
    REQUIREMENTS_IN_PATH,
    REQUIREMENTS_MULTIPLATFORM_OUT_PATH,
    REQUIREMENTS_OUT_PATH,
    UPGRADE_REQUIREMENTS_IN_PATH,
    UPGRADE_REQUIREMENTS_OUT_PATH,
)
from tests.fixtures.temp_dir import temp_dir


@pytest.fixture
def venv_config(temp_dir: Path) -> VenvConfig:
    name = "basic"
    requirements_in_path = temp_dir / "requirements.in"
    shutil.copy(REQUIREMENTS_IN_PATH, requirements_in_path)
    venv_path = temp_dir / "venvs" / name
    yield VenvConfig.from_user_config(
        VenvUserConfig(requirements_in=requirements_in_path), name, venv_path
    )


@pytest.fixture
def compiled_venv_config(venv_config: VenvConfig) -> VenvConfig:
    shutil.copy(REQUIREMENTS_OUT_PATH, venv_config.requirements_out)
    yield venv_config


@pytest.fixture
def multiplatform_venv_config(temp_dir: Path) -> VenvConfig:
    name = "basic"
    requirements_in_path = temp_dir / "requirements.in"
    shutil.copy(REQUIREMENTS_IN_PATH, requirements_in_path)
    venv_path = temp_dir / "venvs" / name
    targets = TargetsUserConfig(
        platforms=["linux", "windows"], versions=["3.7", "3.10"]
    )
    yield VenvConfig.from_user_config(
        VenvUserConfig(requirements_in=requirements_in_path),
        name,
        venv_path,
        global_targets=targets,
    )


@pytest.fixture
def compiled_multiplatform_venv_config(
    multiplatform_venv_config: VenvConfig,
) -> VenvConfig:
    venv_config = multiplatform_venv_config

    shutil.copy(
        REQUIREMENTS_MULTIPLATFORM_OUT_PATH, venv_config.requirements_out.parent
    )
    yield venv_config


@pytest.fixture
def needs_upgrade_compiled_venv_config(temp_dir: Path) -> VenvConfig:
    name = "basic"
    requirements_in_path = temp_dir / "requirements.in"
    shutil.copy(UPGRADE_REQUIREMENTS_IN_PATH, requirements_in_path)
    venv_path = temp_dir / "venvs" / name
    venv_config = VenvConfig.from_user_config(
        VenvUserConfig(requirements_in=requirements_in_path), name, venv_path
    )
    shutil.copy(UPGRADE_REQUIREMENTS_OUT_PATH, venv_config.requirements_out)
    yield venv_config
