import shutil
from pathlib import Path

import multivenv
from multivenv import _platform
from multivenv._config import (
    PlatformConfig,
    PythonVersionConfig,
    TargetConfig,
    TargetsUserConfig,
    TargetUserConfig,
    VenvUserConfig,
)
from tests.config import (
    BASIC_REQUIREMENTS_HASH,
    REQUIREMENTS_IN_PATH,
    REQUIREMENTS_OUT_PATH,
)
from tests.dirutils import change_directory_to
from tests.fixtures.temp_dir import temp_dir


def test_info(temp_dir: Path):
    shutil.copy(REQUIREMENTS_IN_PATH, temp_dir)
    shutil.copy(REQUIREMENTS_OUT_PATH, temp_dir)
    venvs: multivenv.Venvs = {"basic": None}
    with change_directory_to(temp_dir):
        multivenv.sync(venvs=venvs)
        all_info = multivenv.info(["basic"], venvs=venvs)
        assert len(all_info) == 1
        current_target = TargetConfig.from_system()
        assert all_info.system.version == current_target.version
        assert all_info.system.platform == current_target.platform
        assert (
            all_info.system.file_extensions.default
            == current_target.requirements_out_file_extension
        )
        assert (
            all_info.system.file_extensions.all
            == current_target.requirements_out_possible_file_extensions
        )
        info = all_info[0]
        assert info.name == "basic"
        assert info.path == Path("venvs", "basic")
        assert info.config_requirements.in_path == Path("requirements.in")
        assert info.config_requirements.out_path == Path("requirements.txt")
        assert info.discovered_requirements.in_path == Path("requirements.in")
        assert info.discovered_requirements.out_path == Path("requirements.txt")
        assert info.exists is True
        assert info.state.needs_sync is False
        assert info.state.requirements_hash == BASIC_REQUIREMENTS_HASH


def test_target_info(temp_dir: Path):
    shutil.copy(REQUIREMENTS_IN_PATH, temp_dir)
    shutil.copy(REQUIREMENTS_OUT_PATH, temp_dir)
    targets = TargetsUserConfig(
        targets=[TargetUserConfig(version="3.7", platform="windows")]
    )
    venvs: multivenv.Venvs = {"basic": None}
    with change_directory_to(temp_dir):
        multivenv.sync(venvs=venvs)
        all_info = multivenv.info(["basic"], venvs=venvs, targets=targets)
        assert len(all_info) == 1
        info = all_info[0]
        assert len(info.targets) == 1
        target = info.targets[0]
        assert target.version == PythonVersionConfig.from_str("3.7")
        assert target.platform == PlatformConfig.from_str("windows")
        assert target.file_extensions.default == "-3.7-win32-Windows-AMD64"
        assert target.file_extensions.all == [
            "-3.7-win32-Windows-AMD64",
            "-3.7-win32-Windows-AMD64",
            "-3-win32-Windows-AMD64",
            "-win32-Windows-AMD64",
            "-3.7",
        ]
