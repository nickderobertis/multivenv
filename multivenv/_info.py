from enum import Enum
from pathlib import Path
from typing import Iterator, List, Optional

from pydantic import BaseModel

from multivenv._config import VenvConfig
from multivenv._sync import _find_requirements_file
from multivenv.exc import CompiledRequirementsNotFoundException


class InfoFormat(str, Enum):
    TEXT = "text"
    JSON = "json"


class RequirementsInfo(BaseModel):
    in_path: Path
    out_path: Optional[Path]


class VenvInfo(BaseModel):
    name: str
    path: Path
    exists: bool
    config_requirements: RequirementsInfo
    discovered_requirements: RequirementsInfo


class AllInfo(BaseModel):
    __root__: List[VenvInfo]

    def __getitem__(self, item) -> VenvInfo:
        return self.__root__[item]

    def __iter__(self) -> Iterator[VenvInfo]:
        return iter(self.__root__)

    def __len__(self) -> int:
        return len(self.__root__)

    def __contains__(self, item) -> bool:
        return item in self.__root__


def create_venv_info(config: VenvConfig) -> VenvInfo:
    config_requirements = RequirementsInfo(
        in_path=config.requirements_in,
        out_path=config.requirements_out,
    )

    try:
        discovered_out_path = _find_requirements_file(config)
    except CompiledRequirementsNotFoundException:
        discovered_out_path = None

    discovered_requirements = RequirementsInfo(
        in_path=config.requirements_in,
        out_path=discovered_out_path,
    )

    return VenvInfo(
        name=config.name,
        path=config.path,
        exists=config.path.exists(),
        config_requirements=config_requirements,
        discovered_requirements=discovered_requirements,
    )
