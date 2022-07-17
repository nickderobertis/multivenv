import shutil
from pathlib import Path

import pytest

from multivenv.config import VenvConfig, VenvUserConfig
from tests.config import REQUIREMENTS_IN_PATH
from tests.fixtures.temp_dir import temp_dir


@pytest.fixture
def venv_config(temp_dir: Path) -> VenvConfig:
    name = "basic"
    requirements_in_path = temp_dir / "requirements.in"
    shutil.copy(REQUIREMENTS_IN_PATH, requirements_in_path)
    venv_path = temp_dir / "venvs" / name
    yield VenvConfig.from_user_config(
        VenvUserConfig(name=name, requirements_in=requirements_in_path), venv_path
    )
