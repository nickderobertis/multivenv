import shutil

from multivenv._config import VenvConfig


def delete_venv(config: VenvConfig, ignore_errors: bool = False):
    shutil.rmtree(config.path, ignore_errors=ignore_errors)
