import itertools

from multivenv._compile import compile_venv_requirements
from multivenv._config import TargetConfig, TargetsConfig, TargetUserConfig, VenvConfig
from tests.config import REQUIREMENTS_MULTIPLATFORM_REQUIREMENTS_IN_PATH
from tests.fixtures.venv_configs import *


def test_compile(venv_config: VenvConfig):
    assert not venv_config.requirements_out.exists()
    compile_venv_requirements(venv_config)
    assert venv_config.requirements_out.exists()
    text = venv_config.requirements_out.read_text()
    assert "appdirs==1.4.4" in text
    assert "mvenv compile" in text


def test_compile_installs_platform_specific_for_target_platform(
    venv_config: VenvConfig,
):
    target = TargetConfig.from_user_config(
        TargetUserConfig(version="3.7", platform="windows")
    )
    venv_config.targets = [target]
    venv_config.requirements_in = REQUIREMENTS_MULTIPLATFORM_REQUIREMENTS_IN_PATH
    requirements_out = venv_config.default_requirements_out_path_for(target)
    assert not requirements_out.exists()
    compile_venv_requirements(venv_config)
    assert requirements_out.exists()
    text = requirements_out.read_text()

    # Check contents that should be there one all platforms
    assert "pytest==7.1.2" in text
    assert "mvenv compile" in text

    # Check contents that should be there only on windows
    assert "colorama" in text

    # Check contents that should only be there on 3.7
    assert "importlib-metadata" in text


def test_compile_multiple_versions_and_platforms(multiplatform_venv_config: VenvConfig):
    venv_config = multiplatform_venv_config
    user_targets_config = TargetsUserConfig(
        platforms=["linux", "windows"], versions=["3.7", "3.10"]
    )
    targets = TargetsConfig.from_user_config(user_targets_config)
    for target in targets:
        assert not venv_config.default_requirements_out_path_for(target).exists()

    compile_venv_requirements(venv_config)

    for target in targets:
        assert venv_config.default_requirements_out_path_for(target).exists()
        text = venv_config.default_requirements_out_path_for(target).read_text()
        assert "appdirs==1.4.4" in text
        assert "mvenv compile" in text


def test_compile_upgrade(needs_upgrade_compiled_venv_config: VenvConfig):
    venv_config = needs_upgrade_compiled_venv_config
    compile_venv_requirements(venv_config)
    text = venv_config.requirements_out.read_text()
    assert "appdirs==1.4.4" in text
    assert "mvenv compile" in text


def test_compile_prevent_upgrade(needs_upgrade_compiled_venv_config: VenvConfig):
    venv_config = needs_upgrade_compiled_venv_config
    venv_config.upgrade = False
    compile_venv_requirements(venv_config)
    text = venv_config.requirements_out.read_text()
    assert "appdirs==1.4.3" in text
    assert "mvenv compile" in text
