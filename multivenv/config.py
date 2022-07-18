from pathlib import Path
from typing import Optional

from pydantic import BaseModel


class VenvUserConfig(BaseModel):
    requirements_in: Optional[Path] = None
    requirements_out: Optional[Path] = None


class VenvConfig(BaseModel):
    name: str
    path: Path
    requirements_in: Path
    requirements_out: Path

    @classmethod
    def from_user_config(
        cls, user_config: Optional[VenvUserConfig], name: str, path: Path
    ):
        user_requirements_in = user_config.requirements_in if user_config else None
        user_requirements_out = user_config.requirements_out if user_config else None

        requirements_in = _get_requirements_in_path(user_requirements_in, name)
        requirements_out = user_requirements_out or requirements_in.with_suffix(".txt")
        return cls(
            name=name,
            path=path,
            requirements_in=requirements_in,
            requirements_out=requirements_out,
        )


def _get_requirements_in_path(user_requirements_in: Optional[Path], name: str) -> Path:
    if user_requirements_in is not None:
        return user_requirements_in
    for path in [Path(f"{name}-requirements.in"), Path("requirements.in")]:
        if path.exists():
            return path
    raise ValueError("Could not find requirements file")
