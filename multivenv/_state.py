import datetime
import hashlib
from pathlib import Path

from pyappconf import AppConfig, BaseConfig, ConfigFormats

from multivenv._config import VenvConfig
from multivenv._find_reqs import find_requirements_file


def create_venv_state(config: VenvConfig) -> "VenvState":
    state = VenvState.create_empty(config.path)
    state.save()
    return state


def update_venv_state(config: VenvConfig, requirements_file: Path) -> "VenvState":
    new_state = VenvState.create_from_requirements(requirements_file, config.path)
    new_state.save()
    return new_state


def venv_needs_sync(config: VenvConfig) -> bool:
    try:
        state = VenvState.load(config.path)
    except FileNotFoundError:
        return True
    requirements_file = find_requirements_file(config)
    return state.needs_sync(requirements_file)


class VenvState(BaseConfig):
    last_synced: datetime.datetime
    requirements_hash: str
    _settings = AppConfig(
        app_name="multivenv",
        config_name="mvenv-state",
        default_format=ConfigFormats.JSON,
        multi_format=False,
    )

    @classmethod
    def create_from_requirements(
        cls, requirements_path: Path, venv_path: Path
    ) -> "VenvState":
        settings = cls._settings.copy(custom_config_folder=venv_path)
        return cls(
            last_synced=datetime.datetime.now(),
            requirements_hash=_hash_from_path(requirements_path),
            settings=settings,
        )

    @classmethod
    def create_empty(cls, venv_path: Path) -> "VenvState":
        settings = cls._settings.copy(custom_config_folder=venv_path)
        return cls(
            last_synced=datetime.datetime.now(),
            requirements_hash="",
            settings=settings,
        )

    def needs_sync(self, requirements_path: Path) -> bool:
        return _hash_from_path(requirements_path) != self.requirements_hash


def _hash_from_path(path: Path) -> str:
    """
    Load the file at path and calculate an MD5 hash of its contents.
    :param path:
    :return: MD5 hash of the file contents
    """
    bytes_content = path.read_bytes()
    return hashlib.md5(bytes_content).hexdigest()
