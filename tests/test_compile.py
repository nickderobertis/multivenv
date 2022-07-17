from multivenv.compile import compile_venv_requirements
from multivenv.config import VenvConfig
from tests.fixtures.venv_configs import *


def test_compile(venv_config: VenvConfig):
    assert not venv_config.requirements_out.exists()
    compile_venv_requirements(venv_config)
    assert venv_config.requirements_out.exists()
    text = venv_config.requirements_out.read_text()
    assert "appdirs==1.4.4" in text
    assert "mvenv compile" in text
