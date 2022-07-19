import itertools

from multivenv._compile import compile_venv_requirements
from multivenv._config import VenvConfig
from tests.fixtures.venv_configs import *


def test_compile(venv_config: VenvConfig):
    assert not venv_config.requirements_out.exists()
    compile_venv_requirements(venv_config)
    assert venv_config.requirements_out.exists()
    text = venv_config.requirements_out.read_text()
    assert "appdirs==1.4.4" in text
    assert "mvenv compile" in text


def test_compile_multiple_versions_and_platforms(multiplatform_venv_config: VenvConfig):
    venv_config = multiplatform_venv_config
    python_versions = ["3.7", "3.10"]
    platforms = ["linux_x86_64", "win32"]
    for version, platform in itertools.product(python_versions, platforms):
        assert not venv_config.requirements_out_path_for(version, platform).exists()

    compile_venv_requirements(venv_config)

    for version, platform in itertools.product(python_versions, platforms):
        assert venv_config.requirements_out_path_for(version, platform).exists()
        text = venv_config.requirements_out_path_for(version, platform).read_text()
        assert "appdirs==1.4.4" in text
        assert "mvenv compile" in text
