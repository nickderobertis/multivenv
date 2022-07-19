import shutil
import sys
from unittest.mock import patch

import pytest

from multivenv import _platform
from multivenv._compile import compile_venv_requirements
from multivenv._config import VenvConfig
from multivenv._run import run_in_venv
from multivenv._sync import sync_venv
from multivenv.exc import CompiledRequirementsNotFoundException
from tests.fixtures.venv_configs import *
from tests.venvutils import get_installed_packages_in_venv


def test_sync(compiled_venv_config: VenvConfig):
    venv_config = compiled_venv_config

    assert not venv_config.path.exists()
    sync_venv(venv_config)
    assert venv_config.path.exists()
    packages = get_installed_packages_in_venv(venv_config)
    assert "appdirs==1.4.4" in packages


@patch.object(sys, "version_info", (3, 7, 0, "final", 0))
@patch.object(_platform, "get_platform", lambda: "win32")
def test_sync_specific_platform(compiled_multiplatform_venv_config: VenvConfig):
    venv_config = compiled_multiplatform_venv_config

    assert not venv_config.path.exists()
    sync_venv(venv_config)
    assert venv_config.path.exists()
    packages = get_installed_packages_in_venv(venv_config)
    assert "appdirs==1.4.4" in packages


@patch.object(sys, "version_info", (3, 7, 0, "final", 0))
@patch.object(_platform, "get_platform", lambda: "wrong")
def test_sync_on_wrong_platform_without_fallback(
    compiled_multiplatform_venv_config: VenvConfig,
):
    venv_config = compiled_multiplatform_venv_config

    with pytest.raises(CompiledRequirementsNotFoundException):
        sync_venv(venv_config)


@patch.object(sys, "version_info", (3, 7, 0, "final", 0))
@patch.object(_platform, "get_platform", lambda: "wrong")
def test_sync_on_wrong_platform_with_version_fallback(
    compiled_multiplatform_venv_config: VenvConfig,
):
    venv_config = compiled_multiplatform_venv_config
    project_path = venv_config.path.parent.parent
    shutil.copy(
        project_path / REQUIREMENTS_MULTIPLATFORM_OUT_PATH.name,
        project_path / "requirements-3.7.txt",
    )

    assert not venv_config.path.exists()
    sync_venv(venv_config)
    assert venv_config.path.exists()
    packages = get_installed_packages_in_venv(venv_config)
    assert "appdirs==1.4.4" in packages
