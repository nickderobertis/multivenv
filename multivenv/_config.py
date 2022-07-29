from pathlib import Path
from typing import List, Optional, TypeVar

from pydantic import BaseModel

from multivenv._dirutils import create_temp_path
from multivenv._platform import platform_to_pypi_tag


class VenvUserConfig(BaseModel):
    requirements_in: Optional[Path] = None
    requirements_out: Optional[Path] = None
    versions: Optional[List[str]] = None
    platforms: Optional[List[str]] = None
    persistent: bool = True


class VenvConfig(BaseModel):
    name: str
    path: Path
    requirements_in: Path
    requirements_out: Path
    versions: List[str]
    platforms: List[str]
    persistent: bool

    @classmethod
    def from_user_config(
        cls,
        user_config: Optional[VenvUserConfig],
        name: str,
        path: Path,
        global_versions: Optional[List[str]] = None,
        global_platforms: Optional[List[str]] = None,
        global_persistent: Optional[bool] = None,
    ):
        user_requirements_in = user_config.requirements_in if user_config else None
        user_requirements_out = user_config.requirements_out if user_config else None
        versions = _get_config_from_global_user_or_default(
            global_versions, user_config, "versions", []
        )
        raw_platforms = _get_config_from_global_user_or_default(
            global_platforms, user_config, "platforms", []
        )
        persistent = _get_config_from_global_user_or_default(
            global_persistent, user_config, "persistent", True
        )
        platforms = [platform_to_pypi_tag(plat) for plat in raw_platforms]  # type: ignore

        requirements_in = _get_requirements_in_path(user_requirements_in, name)
        requirements_out = user_requirements_out or requirements_in.with_suffix(".txt")

        use_path = path if persistent else create_temp_path() / path.name

        return cls(
            name=name,
            path=use_path,
            requirements_in=requirements_in,
            requirements_out=requirements_out,
            versions=versions,
            platforms=platforms,
            persistent=persistent,
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


T = TypeVar("T")


def _get_config_from_global_user_or_default(
    global_setting: Optional[T],
    user_config: Optional[VenvUserConfig],
    config_attr: str,
    default: T,
) -> T:
    if global_setting is not None:
        return global_setting
    if user_config is not None:
        possible_value = getattr(user_config, config_attr, default)
        if possible_value is not None:
            return possible_value
    return default
