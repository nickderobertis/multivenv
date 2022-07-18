from enum import Enum
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel

from multivenv.config import VenvConfig
from multivenv.exc import CompiledRequirementsNotFoundException
from multivenv.sync import _find_requirements_file


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
