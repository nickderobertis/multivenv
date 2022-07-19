import pytest

from multivenv._config import VenvConfig
from multivenv._sync import sync_venv
from tests.fixtures.venv_configs import *


@pytest.fixture
def synced_venv(compiled_venv_config: VenvConfig) -> VenvConfig:
    sync_venv(compiled_venv_config)
    yield compiled_venv_config
