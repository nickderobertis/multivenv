from pathlib import Path

from pydantic import BaseModel

from multivenv.config import VenvConfig


class VenvInfo(BaseModel):
    name: str
    path: Path
    exists: bool
    requirements_in: Path
    requirements_out: Path


def create_venv_info(config: VenvConfig) -> VenvInfo:
    return VenvInfo(
        name=config.name,
        path=config.path,
        exists=config.path.exists(),
        requirements_in=config.requirements_in,
        requirements_out=config.requirements_out,
    )
