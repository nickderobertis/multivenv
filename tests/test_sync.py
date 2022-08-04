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
from tests.fixtures.targets import windows_37_environment, wrong_environment
from tests.fixtures.venv_configs import *
from tests.venvutils import get_installed_packages_in_venv


def test_sync(compiled_venv_config: VenvConfig):
    venv_config = compiled_venv_config

    assert not venv_config.path.exists()
    sync_venv(venv_config)
    assert venv_config.path.exists()
    packages = get_installed_packages_in_venv(venv_config)
    assert "appdirs==1.4.4" in packages


def test_sync_specific_platform(
    compiled_multiplatform_venv_config: VenvConfig, windows_37_environment
):
    venv_config = compiled_multiplatform_venv_config

    assert not venv_config.path.exists()
    sync_venv(venv_config)
    assert venv_config.path.exists()
    packages = get_installed_packages_in_venv(venv_config)
    assert "appdirs==1.4.4" in packages


def test_sync_on_wrong_platform_without_fallback(
    compiled_multiplatform_venv_config: VenvConfig, wrong_environment
):
    venv_config = compiled_multiplatform_venv_config

    with pytest.raises(CompiledRequirementsNotFoundException):
        sync_venv(venv_config)


def test_sync_on_wrong_platform_with_version_fallback(
    compiled_multiplatform_venv_config: VenvConfig, wrong_environment
):
    venv_config = compiled_multiplatform_venv_config
    project_path = venv_config.path.parent.parent
    shutil.copy(
        project_path / REQUIREMENTS_MULTIPLATFORM_OUT_PATH.name,
        project_path / "requirements-2.7.0.txt",
    )

    assert not venv_config.path.exists()
    sync_venv(venv_config)
    assert venv_config.path.exists()
    packages = get_installed_packages_in_venv(venv_config)
    assert "appdirs==1.4.4" in packages


def test_post_create(compiled_venv_config: VenvConfig):
    venv_config = compiled_venv_config
    expect_path = (venv_config.path / "post_create.txt").resolve()
    venv_config.post_create = [
        f"""python -c 'from pathlib import Path;import sys;p = Path(sys.executable).parent.parent / "post_create.txt";p.touch()'"""
    ]

    assert not venv_config.path.exists()
    assert not expect_path.exists()
    sync_venv(venv_config)
    assert venv_config.path.exists()
    assert expect_path.exists()
    packages = get_installed_packages_in_venv(venv_config)
    assert "appdirs==1.4.4" in packages


def test_post_sync(compiled_venv_config: VenvConfig):
    venv_config = compiled_venv_config
    venv_config.post_sync = ["pip install flake8==5.0.3"]

    assert not venv_config.path.exists()
    sync_venv(venv_config)
    assert venv_config.path.exists()
    packages = get_installed_packages_in_venv(venv_config)
    assert "appdirs==1.4.4" in packages
    assert "flake8==5.0.3" in packages
