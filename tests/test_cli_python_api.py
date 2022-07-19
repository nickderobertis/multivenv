import shutil
from pathlib import Path

import multivenv
from tests.config import BASIC_CONFIG_PATH, REQUIREMENTS_IN_PATH, REQUIREMENTS_OUT_PATH
from tests.dirutils import change_directory_to
from tests.fixtures.temp_dir import temp_dir


def test_info(temp_dir: Path):
    shutil.copy(REQUIREMENTS_IN_PATH, temp_dir)
    shutil.copy(REQUIREMENTS_OUT_PATH, temp_dir)
    shutil.copy(BASIC_CONFIG_PATH, temp_dir)
    with change_directory_to(temp_dir):
        multivenv.sync()
        all_info = multivenv.info(["basic"])
        assert len(all_info) == 1
        info = all_info[0]
        assert info.name == "basic"
        assert info.path == Path("venvs", "basic")
        assert info.config_requirements.in_path == "requirements.in"
        assert info.config_requirements.out_path == "requirements.txt"
        assert info.discovered_requirements.in_path == "requirements.in"
        assert info.discovered_requirements.out_path == "requirements.txt"
        assert info.exists is True
