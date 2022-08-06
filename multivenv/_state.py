import datetime
import hashlib
from json import JSONDecodeError
from pathlib import Path
from typing import Dict, Optional, Sequence

from pyappconf import AppConfig, BaseConfig, ConfigFormats
from pydantic import ValidationError

from multivenv._config import VenvConfig
from multivenv._find_reqs import find_requirements_file


def create_venv_state(config: VenvConfig) -> "VenvState":
    state = VenvState.create_empty(config.path)
    state.save()
    return state


def update_venv_state(config: VenvConfig, requirements_file: Path) -> "VenvState":
    new_state = VenvState.create_from_sync_paths(
        config.sync_paths(requirements_file), config.path
    )
    new_state.save()
    return new_state


def venv_needs_sync(config: VenvConfig) -> bool:
    try:
        state = VenvState.load(config.path)
    except (FileNotFoundError, JSONDecodeError, ValidationError):
        return True
    requirements_file = find_requirements_file(config)
    return state.needs_sync(config.sync_paths(requirements_file))


class VenvState(BaseConfig):
    last_synced: datetime.datetime
    hashes: Dict[str, str]
    _settings = AppConfig(
        app_name="multivenv",
        config_name="mvenv-state",
        default_format=ConfigFormats.JSON,
        multi_format=False,
    )

    @classmethod
    def create_from_sync_paths(
        cls, sync_paths: Sequence[Path], venv_path: Path
    ) -> "VenvState":
        settings = cls._settings.copy(custom_config_folder=venv_path)
        return cls(
            last_synced=datetime.datetime.now(),
            hashes=_hash_dict_from_paths(sync_paths),
            settings=settings,
        )

    @classmethod
    def create_empty(cls, venv_path: Path) -> "VenvState":
        settings = cls._settings.copy(custom_config_folder=venv_path)
        return cls(
            last_synced=datetime.datetime.now(),
            hashes={},
            settings=settings,
        )

    def needs_sync(self, sync_paths: Sequence[Path]) -> bool:
        return _hash_dict_from_paths(sync_paths) != self.hashes

    def hash_for(self, path: Path) -> Optional[str]:
        return self.hashes.get(str(path))


def _hash_from_path(path: Path) -> str:
    """
    Load the file at path and calculate an MD5 hash of its contents.
    :param path:
    :return: MD5 hash of the file contents
    """
    bytes_content = path.read_bytes()
    return hashlib.md5(bytes_content).hexdigest()


def _hash_dict_from_paths(paths: Sequence[Path]) -> Dict[str, str]:
    """
    Calculate an MD5 hash of the contents of all files in paths.
    :param paths:
    :return: MD5 hash of the file contents
    """
    return {str(path): _hash_from_path(path) for path in paths}
