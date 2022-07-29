import contextlib
import os
from pathlib import Path

from multivenv._dirutils import create_temp_path


@contextlib.contextmanager
def change_directory_to(path: Path):
    current_path = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(current_path)
