import shutil

from multivenv._config import VenvConfig


def delete_venv(config: VenvConfig):
    shutil.rmtree(config.path)
