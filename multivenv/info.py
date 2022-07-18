from enum import Enum
from pathlib import Path
from typing import List

from pydantic import BaseModel

from multivenv.config import VenvConfig


class InfoFormat(str, Enum):
    TEXT = "text"
    JSON = "json"


class VenvInfo(BaseModel):
    name: str
    path: Path
    exists: bool
    requirements_in: Path
    requirements_out: Path


class AllInfo(BaseModel):
    __root__: List[VenvInfo]


def create_venv_info(config: VenvConfig) -> VenvInfo:
    return VenvInfo(
        name=config.name,
        path=config.path,
        exists=config.path.exists(),
        requirements_in=config.requirements_in,
        requirements_out=config.requirements_out,
    )
