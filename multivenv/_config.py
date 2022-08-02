from pathlib import Path
from typing import Iterator, List, Literal, Optional, TypeVar, Union

from packaging import version as packaging_version
from packaging.version import Version as PackagingVersion
from pydantic import BaseModel

from multivenv import _ext_packaging
from multivenv._dirutils import create_temp_path
from multivenv.exc import NoSuchPlatformStringException

PlatformString = Literal["linux", "macos", "windows"]


class PlatformUserConfig(BaseModel):
    sys_platform: str
    os_name: str
    platform_system: str
    platform_machine: str = "x86_64"


UserPlatformConfig = Union[PlatformUserConfig, PlatformString]


class PlatformConfig(BaseModel):
    sys_platform: str
    os_name: str
    platform_system: str
    platform_machine: str

    def __str__(self) -> str:
        return f"{self.sys_platform}-{self.platform_system}-{self.platform_machine}"

    @classmethod
    def from_ambiguous(
        cls, config: Optional[UserPlatformConfig] = None
    ) -> "PlatformConfig":
        if isinstance(config, str):
            return cls.from_str(config)  # type: ignore
        return cls.from_user_config(config)

    @classmethod
    def from_user_config(
        cls, user_config: Optional[PlatformUserConfig] = None
    ) -> "PlatformConfig":
        default_env = _ext_packaging.get_default_environment()
        sys_platform = (
            user_config.sys_platform if user_config else default_env["sys_platform"]
        )
        os_name = user_config.os_name if user_config else default_env["os_name"]
        platform_machine = (
            user_config.platform_machine
            if user_config
            else default_env["platform_machine"]
        )
        platform_system = (
            user_config.platform_system
            if user_config
            else default_env["platform_system"]
        )
        return cls(
            sys_platform=sys_platform,
            os_name=os_name,
            platform_system=platform_system,
            platform_machine=platform_machine,
        )

    @classmethod
    def from_str(cls, platform: PlatformString) -> "PlatformConfig":
        if platform == "linux":
            user_config = PlatformUserConfig(
                sys_platform="linux",
                os_name="posix",
                platform_system="Linux",
            )
        elif platform == "macos":
            user_config = PlatformUserConfig(
                sys_platform="darwin",
                os_name="posix",
                platform_system="Darwin",
            )
        elif platform == "windows":
            user_config = PlatformUserConfig(
                sys_platform="win32",
                os_name="nt",
                platform_system="Windows",
                platform_machine="AMD64",
            )
        else:
            raise NoSuchPlatformStringException(
                f"No such platform: {platform}. Choose one of linux, macos, windows, or define a custom platform object."
            )
        return cls.from_user_config(user_config)


class PythonVersionUserConfig(BaseModel):
    version: str
    platform_python_implementation: str = "CPython"
    implementation_name: str = "cpython"


UserPythonVersionConfig = Union[PythonVersionUserConfig, str]

# TODO: handling of version modifiers e.g alpha, beta, post, dev, etc.
class Version(BaseModel):
    full: str
    major: int
    minor: Optional[int] = None
    micro: Optional[int] = None

    def __str__(self) -> str:
        return self.full

    @classmethod
    def from_str(cls, version: str) -> "Version":
        parsed = packaging_version.parse(version)
        return cls.from_packaging_version(parsed)

    @classmethod
    def from_packaging_version(cls, version: PackagingVersion) -> "Version":
        return cls(
            full=str(version),
            major=version.major,
            minor=version.minor if (version.minor or version.micro) else None,
            micro=version.micro or None,
        )

    def without_micro(self) -> "Version":
        new_full = f"{self.major}.{self.minor}"
        return self.copy(update=dict(micro=None, full=new_full))

    def without_minor(self) -> "Version":
        new_full = f"{self.major}"
        return self.copy(update=dict(minor=None, micro=None, full=new_full))


class PythonVersionConfig(BaseModel):
    version: Version
    platform_python_implementation: str
    implementation_name: str

    @classmethod
    def from_ambiguous(
        cls, config: Optional[UserPythonVersionConfig] = None
    ) -> "PythonVersionConfig":
        if isinstance(config, str):
            return cls.from_str(config)
        return cls.from_user_config(config)

    @classmethod
    def from_user_config(
        cls, user_config: Optional[PythonVersionUserConfig] = None
    ) -> "PythonVersionConfig":
        default_env = _ext_packaging.get_default_environment()
        version = (
            user_config.version if user_config else default_env["python_full_version"]
        )
        platform_python_implementation = (
            user_config.platform_python_implementation
            if user_config
            else default_env["platform_python_implementation"]
        )
        implementation_name = (
            user_config.implementation_name
            if user_config
            else default_env["implementation_name"]
        )
        return cls(
            version=Version.from_str(version),
            platform_python_implementation=platform_python_implementation,
            implementation_name=implementation_name,
        )

    @classmethod
    def from_str(cls, version: str) -> "PythonVersionConfig":
        return cls.from_user_config(PythonVersionUserConfig(version=version))

    @property
    def main_version(self) -> str:
        return f"{self.version.major}.{self.version.minor}"

    def without_micro(self) -> "PythonVersionConfig":
        new_version = self.version.without_micro()
        return self.copy(update=dict(version=new_version))

    def without_minor(self) -> "PythonVersionConfig":
        new_version = self.version.without_minor()
        return self.copy(update=dict(version=new_version))


class TargetUserConfig(BaseModel):
    version: Optional[UserPythonVersionConfig] = None
    platform: Optional[UserPlatformConfig] = None


class TargetConfig(BaseModel):
    version: Optional[PythonVersionConfig] = None
    platform: Optional[PlatformConfig] = None

    @classmethod
    def from_user_config(cls, user_config: TargetUserConfig) -> "TargetConfig":
        return cls(
            version=PythonVersionConfig.from_ambiguous(user_config.version)
            if user_config.version
            else None,
            platform=PlatformConfig.from_ambiguous(user_config.platform)
            if user_config.platform
            else None,
        )

    @classmethod
    def from_system(cls) -> "TargetConfig":
        default_env = _ext_packaging.get_default_environment()
        version = PythonVersionConfig(
            version=Version.from_str(default_env["python_full_version"]),
            platform_python_implementation=default_env[
                "platform_python_implementation"
            ],
            implementation_name=default_env["implementation_name"],
        )
        platform = PlatformConfig(
            sys_platform=default_env["sys_platform"],
            os_name=default_env["os_name"],
            platform_system=default_env["platform_system"],
            platform_machine=default_env["platform_machine"],
        )
        return cls(version=version, platform=platform)

    def without_version(self) -> "TargetConfig":
        return self.copy(update=dict(version=None))

    def without_platform(self) -> "TargetConfig":
        return self.copy(update=dict(platform=None))

    def without_micro(self) -> "TargetConfig":
        new_version = self.version.without_micro() if self.version else None
        return self.copy(update=dict(version=new_version))

    def without_minor(self) -> "TargetConfig":
        new_version = self.version.without_minor() if self.version else None
        return self.copy(update=dict(version=new_version))

    @property
    def requirements_out_file_extension(self) -> str:
        suffix = ""
        if self.version:
            suffix += f"-{self.version.version}"
        if self.platform:
            suffix += f"-{self.platform}"
        return suffix

    @property
    def requirements_out_possible_file_extensions(self) -> List[str]:
        exts = [self.requirements_out_file_extension]

        if self.version:
            # Try matching with less-specific python versions
            exts.append(self.without_micro().requirements_out_file_extension)
            exts.append(self.without_minor().requirements_out_file_extension)
            # Try matching without version
            exts.append(self.without_version().requirements_out_file_extension)
        if self.platform:
            # Try matching without platform
            exts.append(self.without_platform().requirements_out_file_extension)

        return exts


class TargetsUserConfig(BaseModel):
    versions: Optional[List[UserPythonVersionConfig]] = None
    platforms: Optional[List[UserPlatformConfig]] = None
    targets: Optional[List[TargetUserConfig]] = None
    extend_targets: Optional[List[TargetUserConfig]] = None
    skip_targets: Optional[List[TargetUserConfig]] = None


class TargetsConfig(BaseModel):
    targets: List[TargetConfig]

    def __getitem__(self, item) -> TargetConfig:
        return self.targets[item]

    def __iter__(self) -> Iterator[TargetConfig]:
        return iter(self.targets)

    @classmethod
    def from_user_config(cls, user_config: TargetsUserConfig) -> "TargetsConfig":
        targets = _resolve_target_config(
            versions=user_config.versions or [],
            platforms=user_config.platforms or [],
            targets=user_config.targets,
            extend_targets=user_config.extend_targets,
            skip_targets=user_config.skip_targets,
        )
        return cls(targets=targets)


UserRunConfig = Union[List[str], str]


class VenvUserConfig(BaseModel):
    requirements_in: Optional[Path] = None
    requirements_out: Optional[Path] = None
    targets: Optional[TargetsUserConfig] = None
    persistent: bool = True
    upgrade: bool = True
    post_create: Optional[UserRunConfig] = None
    post_sync: Optional[UserRunConfig] = None


class VenvConfig(BaseModel):
    name: str
    path: Path
    requirements_in: Path
    requirements_out: Path
    targets: List[TargetConfig]
    persistent: bool
    upgrade: bool
    post_create: List[str]
    post_sync: List[str]

    @classmethod
    def from_user_config(
        cls,
        user_config: Optional[VenvUserConfig],
        name: str,
        path: Path,
        global_targets: Optional[TargetsUserConfig] = None,
        global_persistent: Optional[bool] = None,
        global_auto_upgrade: Optional[bool] = None,
        global_post_create: Optional[UserRunConfig] = None,
        global_post_sync: Optional[UserRunConfig] = None,
    ):
        user_requirements_in = user_config.requirements_in if user_config else None
        user_requirements_out = user_config.requirements_out if user_config else None
        user_targets = _get_config_from_global_user_or_default(
            global_targets, user_config, "targets", TargetsUserConfig(targets=[])
        )
        targets = TargetsConfig.from_user_config(user_targets)
        persistent = _get_config_from_global_user_or_default(
            global_persistent, user_config, "persistent", True
        )
        upgrade = _get_config_from_global_user_or_default(
            global_auto_upgrade, user_config, "auto_upgrade", True
        )

        default_run_config: UserRunConfig = []
        post_create = _get_config_from_global_user_or_default(
            global_post_create, user_config, "post_create", default_run_config
        )
        if isinstance(post_create, str):
            post_create = [post_create]

        post_sync = _get_config_from_global_user_or_default(
            global_post_sync, user_config, "post_sync", default_run_config
        )
        if isinstance(post_sync, str):
            post_sync = [post_sync]

        requirements_in = _get_requirements_in_path(user_requirements_in, name)
        requirements_out = user_requirements_out or requirements_in.with_suffix(".txt")

        use_path = path if persistent else create_temp_path() / path.name

        return cls(
            name=name,
            path=use_path,
            requirements_in=requirements_in,
            requirements_out=requirements_out,
            targets=targets.targets,
            persistent=persistent,
            upgrade=upgrade,
            post_create=post_create,
            post_sync=post_sync,
        )

    def default_requirements_out_path_for(
        self,
        target: TargetConfig,
    ) -> Path:
        suffix = target.requirements_out_file_extension
        suffix += ".txt"
        name = self.requirements_out.with_suffix("").name + suffix
        return self.requirements_out.parent / name

    def possible_requirements_out_paths_for(
        self, target: TargetConfig
    ) -> Iterator[Path]:
        for ext in target.requirements_out_possible_file_extensions:
            name = self.requirements_out.with_suffix("").name + ext + ".txt"
            yield self.requirements_out.parent / name
        # Go to default configured path (no version or platform extension)
        yield self.requirements_out


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


def _resolve_target_config(
    versions: List[UserPythonVersionConfig],
    platforms: List[UserPlatformConfig],
    targets: Optional[List[TargetUserConfig]] = None,
    extend_targets: Optional[List[TargetUserConfig]] = None,
    skip_targets: Optional[List[TargetUserConfig]] = None,
) -> List[TargetConfig]:
    if targets is not None:
        # If targets are explicitly specified, use them
        out_targets = [TargetConfig.from_user_config(t) for t in targets]
    else:
        # Otherwise, use the versions and platforms to generate targets
        out_targets = []
        for version in versions:
            for platform in platforms:
                out_targets.append(
                    TargetConfig.from_user_config(
                        TargetUserConfig(
                            version=version,
                            platform=platform,
                        )
                    )
                )
    if extend_targets is not None:
        out_targets.extend(TargetConfig.from_user_config(t) for t in extend_targets)
    if skip_targets is not None:
        compare_skip_targets = [TargetConfig.from_user_config(t) for t in skip_targets]
        return [t for t in compare_skip_targets if t not in compare_skip_targets]
    return out_targets
