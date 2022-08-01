import datetime
from enum import Enum
from pathlib import Path
from typing import Iterator, List, Optional

from pydantic import BaseModel, Field

from multivenv._config import (
    PlatformConfig,
    PythonVersionConfig,
    TargetConfig,
    VenvConfig,
)
from multivenv._find_reqs import find_requirements_file
from multivenv._state import VenvState
from multivenv.exc import CompiledRequirementsNotFoundException


class InfoFormat(str, Enum):
    TEXT = "text"
    JSON = "json"


class RequirementsInfo(BaseModel):
    in_path: Path
    out_path: Optional[Path]


class FileExtensions(BaseModel):
    all: List[str]
    default: str

    @classmethod
    def from_target(cls, target: TargetConfig) -> "FileExtensions":
        return cls(
            all=target.requirements_out_possible_file_extensions,
            default=target.requirements_out_file_extension,
        )

    @classmethod
    def from_system(cls) -> "FileExtensions":
        target = TargetConfig.from_system()
        return cls.from_target(target)


class SystemInfo(BaseModel):
    version: PythonVersionConfig
    platform: PlatformConfig
    file_extensions: FileExtensions = Field(default_factory=FileExtensions.from_system)

    @classmethod
    def from_system(cls) -> "SystemInfo":
        current_target = TargetConfig.from_system()
        return cls(
            version=current_target.version,
            platform=current_target.platform,
        )


class VenvStateInfo(BaseModel):
    last_synced: Optional[datetime.datetime]
    requirements_hash: Optional[str]
    needs_sync: bool

    @classmethod
    def from_venv_state(
        cls, state: VenvState, requirements_path: Path
    ) -> "VenvStateInfo":
        return cls(
            last_synced=state.last_synced,
            requirements_hash=state.requirements_hash,
            needs_sync=state.needs_sync(requirements_path),
        )

    @classmethod
    def from_venv_config(cls, venv_config: VenvConfig) -> "VenvStateInfo":
        state_path = venv_config.path / "mvenv-state.json"
        if not state_path.exists():
            return cls(
                last_synced=None,
                requirements_hash=None,
                needs_sync=True,
            )
        state = VenvState.load(venv_config.path / "mvenv-state.json")
        requirements_path = find_requirements_file(venv_config)
        return cls.from_venv_state(state, requirements_path)


class TargetInfo(BaseModel):
    version: PythonVersionConfig
    platform: PlatformConfig
    file_extensions: FileExtensions

    @classmethod
    def from_target(cls, target: TargetConfig) -> "TargetInfo":
        return cls(
            version=target.version,
            platform=target.platform,
            file_extensions=FileExtensions.from_target(target),
        )


class VenvInfo(BaseModel):
    name: str
    path: Path
    exists: bool
    config_requirements: RequirementsInfo
    discovered_requirements: RequirementsInfo
    state: VenvStateInfo
    targets: List[TargetInfo]


class AllInfo(BaseModel):
    venv_info: List[VenvInfo]
    system: SystemInfo = Field(default_factory=SystemInfo.from_system)

    def __getitem__(self, item) -> VenvInfo:
        return self.venv_info[item]

    def __iter__(self) -> Iterator[VenvInfo]:
        return iter(self.venv_info)

    def __len__(self) -> int:
        return len(self.venv_info)

    def __contains__(self, item) -> bool:
        return item in self.venv_info


def create_venv_info(config: VenvConfig) -> VenvInfo:
    config_requirements = RequirementsInfo(
        in_path=config.requirements_in,
        out_path=config.requirements_out,
    )

    try:
        discovered_out_path = find_requirements_file(config)
    except CompiledRequirementsNotFoundException:
        discovered_out_path = None

    discovered_requirements = RequirementsInfo(
        in_path=config.requirements_in,
        out_path=discovered_out_path,
    )

    state_info = VenvStateInfo.from_venv_config(config)
    targets = [TargetInfo.from_target(target) for target in config.targets]

    return VenvInfo(
        name=config.name,
        path=config.path,
        exists=config.path.exists(),
        config_requirements=config_requirements,
        discovered_requirements=discovered_requirements,
        state=state_info,
        targets=targets,
    )
