import shlex
import shutil
from typing import Sequence

from click.testing import Result
from cliconf import CLIConf
from cliconf.testing import CLIRunner

from multivenv.cli import cli
from multivenv.config import VenvConfig
from tests import ext_click
from tests.config import BASIC_CONFIG_PATH, REQUIREMENTS_IN_PATH, REQUIREMENTS_OUT_PATH
from tests.dirutils import change_directory_to
from tests.fixtures.temp_dir import *
from tests.venvutils import get_installed_packages_in_venv

runner = CLIRunner()


class CLIRunnerException(Exception):
    pass


def run_cli(command: str) -> Result:
    args = shlex.split(command)
    result = runner.invoke(cli, args, catch_exceptions=False)
    return result


def test_compile_cli(temp_dir: Path):
    expect_out_path = temp_dir / "requirements.txt"
    shutil.copy(REQUIREMENTS_IN_PATH, temp_dir)
    shutil.copy(BASIC_CONFIG_PATH, temp_dir)
    with change_directory_to(temp_dir):
        assert not expect_out_path.exists()
        run_cli("compile")
        assert expect_out_path.exists()
        assert "appdirs==1.4.4" in expect_out_path.read_text()


def test_sync_cli(temp_dir: Path):
    venv_name = "basic"
    venvs_folder = temp_dir / "venvs"
    venv_folder = venvs_folder / venv_name
    shutil.copy(REQUIREMENTS_IN_PATH, temp_dir)
    shutil.copy(REQUIREMENTS_OUT_PATH, temp_dir)
    shutil.copy(BASIC_CONFIG_PATH, temp_dir)
    with change_directory_to(temp_dir):
        config = VenvConfig(
            name=venv_name,
            path=venv_folder,
            requirements_in=temp_dir / "requirements.in",
            requirements_out=temp_dir / "requirements.txt",
            versions=[],
            platforms=[],
        )
        run_cli("sync")
        assert "appdirs==1.4.4" in get_installed_packages_in_venv(config)


def test_update_cli(temp_dir: Path):
    venv_name = "basic"
    venvs_folder = temp_dir / "venvs"
    venv_folder = venvs_folder / venv_name
    expect_requirements_out_path = temp_dir / "requirements.txt"
    shutil.copy(REQUIREMENTS_IN_PATH, temp_dir)
    shutil.copy(BASIC_CONFIG_PATH, temp_dir)
    with change_directory_to(temp_dir):
        config = VenvConfig(
            name=venv_name,
            path=venv_folder,
            requirements_in=temp_dir / "requirements.in",
            requirements_out=temp_dir / "requirements.txt",
            versions=[],
            platforms=[],
        )
        assert not expect_requirements_out_path.exists()
        run_cli("update")
        assert expect_requirements_out_path.exists()
        assert "appdirs==1.4.4" in get_installed_packages_in_venv(config)


def test_run_cli(temp_dir: Path):
    shutil.copy(REQUIREMENTS_IN_PATH, temp_dir)
    shutil.copy(REQUIREMENTS_OUT_PATH, temp_dir)
    shutil.copy(BASIC_CONFIG_PATH, temp_dir)
    with change_directory_to(temp_dir):
        run_cli("sync")
        output = run_cli("run basic pip freeze")
        assert "appdirs==1.4.4" in output.stdout


def test_run_all_cli(temp_dir: Path):
    shutil.copy(REQUIREMENTS_IN_PATH, temp_dir)
    shutil.copy(REQUIREMENTS_OUT_PATH, temp_dir)
    shutil.copy(BASIC_CONFIG_PATH, temp_dir)
    with change_directory_to(temp_dir):
        run_cli("sync")
        output = run_cli("run-all pip freeze")
        assert "appdirs==1.4.4" in output.stdout
