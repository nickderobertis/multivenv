from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel

from multivenv._platform import platform_to_pypi_tag


class VenvUserConfig(BaseModel):
    requirements_in: Optional[Path] = None
    requirements_out: Optional[Path] = None
    versions: Optional[List[str]] = None
    platforms: Optional[List[str]] = None


class VenvConfig(BaseModel):
    name: str
    path: Path
    requirements_in: Path
    requirements_out: Path
    versions: List[str]
    platforms: List[str]

    @classmethod
    def from_user_config(
        cls,
        user_config: Optional[VenvUserConfig],
        name: str,
        path: Path,
        global_versions: Optional[List[str]] = None,
        global_platforms: Optional[List[str]] = None,
    ):
        user_requirements_in = user_config.requirements_in if user_config else None
        user_requirements_out = user_config.requirements_out if user_config else None
        versions = (
            global_versions or (user_config.versions if user_config else None) or []
        )
        raw_platforms = (
            global_platforms or (user_config.platforms if user_config else None) or []
        )
        platforms = [platform_to_pypi_tag(plat) for plat in raw_platforms]

        requirements_in = _get_requirements_in_path(user_requirements_in, name)
        requirements_out = user_requirements_out or requirements_in.with_suffix(".txt")
        return cls(
            name=name,
            path=path,
            requirements_in=requirements_in,
            requirements_out=requirements_out,
            versions=versions,
            platforms=platforms,
        )

    def requirements_out_path_for(
        self, version: Optional[str] = None, platform: Optional[str] = None
    ) -> Path:
        suffix = ""
        if version:
            suffix += f"-{version}"
        if platform:
            suffix += f"-{platform}"
        suffix += ".txt"
        name = self.requirements_out.with_suffix("").name + suffix
        return self.requirements_out.parent / name


def _get_requirements_in_path(user_requirements_in: Optional[Path], name: str) -> Path:
    if user_requirements_in is not None:
        return user_requirements_in
    for path in [Path(f"{name}-requirements.in"), Path("requirements.in")]:
        if path.exists():
            return path
    raise ValueError("Could not find requirements file")
