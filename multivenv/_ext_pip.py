import contextlib
from typing import (
    TYPE_CHECKING,
    Generator,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    cast,
)

if TYPE_CHECKING:
    from packaging.tags import PythonVersion, Tag

from multivenv._config import PlatformConfig, PythonVersionConfig, TargetConfig
from multivenv._ext_packaging import Environment


@contextlib.contextmanager
def monkey_patch_pip_to_target(
    target: TargetConfig,
) -> Generator[None, None, None]:
    """
    Monkey patch pip internals to use the given platform and python version.

    This will make it return nested requirements as if on that system. See the docs
    for the individual helper functions it calls for more details on what is being patched.
    """
    # Combine multiple context managers into one
    with contextlib.ExitStack() as stack:
        for fn in [
            _monkey_patch_marker_evaluate,
            _monkey_patch_cpython_tags,
            _monkey_patch_compatible_tags,
        ]:
            stack.enter_context(fn(target))
        yield


@contextlib.contextmanager
def _monkey_patch_cpython_tags(target: TargetConfig) -> Generator[None, None, None]:
    """
    Monkey patch pip._vendor.packaging.tags.cpython_tags to use the given platform and python version.

    This will make it return nested requirements as if on that system.

    It works by providing defaults based on the target, rather than letting the
    original function set the defaults from the current system.
    """
    import pip._internal.utils.compatibility_tags
    import pip._vendor.packaging.tags

    orig_cpython_tags = pip._vendor.packaging.tags.cpython_tags

    def cpython_tags(
        python_version: Optional["PythonVersion"] = None,
        abis: Optional[Iterable[str]] = None,
        platforms: Optional[Iterable[str]] = None,
        *,
        warn: bool = False,
    ) -> Iterator["Tag"]:
        """
        This is a modified version of the original pip._vendor.packaging.tags.cpython_tags function

        Original docs below:

        Yields the tags for a CPython interpreter.

        The tags consist of:
        - cp<python_version>-<abi>-<platform>
        - cp<python_version>-abi3-<platform>
        - cp<python_version>-none-<platform>
        - cp<less than python_version>-abi3-<platform>  # Older Python versions down to 3.2.

        If python_version only specifies a major version then user-provided ABIs and
        the 'none' ABItag will be used.

        If 'abi3' or 'none' are specified in 'abis' then they will be yielded at
        their normal position and not at the beginning.
        """
        # Provide defaults based on target, rather than current system
        if python_version is None:
            python_version = (
                target.version.version.major,
                target.version.version.minor,
            )
        if not platforms:
            platforms = _platform_tags(target)

        # Call the original function with the updated python version and platforms
        return orig_cpython_tags(
            python_version=python_version,
            abis=abis,
            platforms=platforms,
            warn=warn,
        )

    # Patch in the original module
    pip._vendor.packaging.tags.cpython_tags = cpython_tags
    # Patch where it has been imported
    pip._internal.utils.compatibility_tags.cpython_tags = cpython_tags

    yield

    pip._vendor.packaging.tags.cpython_tags = orig_cpython_tags
    pip._internal.utils.compatibility_tags.cpython_tags = orig_cpython_tags


@contextlib.contextmanager
def _monkey_patch_compatible_tags(
    target: TargetConfig,
) -> Generator[None, None, None]:
    """
    Monkey patch pip._vendor.packaging.tags.compatible_tags to use the given platform and python version.

    This will make it return nested requirements as if on that system.

    It works by providing defaults based on the target, rather than letting the
    original function set the defaults from the current system.
    """
    import pip._internal.utils.compatibility_tags
    import pip._vendor.packaging.tags

    orig_compatible_tags = pip._vendor.packaging.tags.compatible_tags

    def compatible_tags(
        python_version: Optional["PythonVersion"] = None,
        interpreter: Optional[str] = None,
        platforms: Optional[Iterable[str]] = None,
    ) -> Iterator["Tag"]:
        """
        This is a modified version of the original pip._vendor.packaging.tags.cpython_tags function

        Original docs below:

        Yields the tags for a CPython interpreter.

        The tags consist of:
        - cp<python_version>-<abi>-<platform>
        - cp<python_version>-abi3-<platform>
        - cp<python_version>-none-<platform>
        - cp<less than python_version>-abi3-<platform>  # Older Python versions down to 3.2.

        If python_version only specifies a major version then user-provided ABIs and
        the 'none' ABItag will be used.

        If 'abi3' or 'none' are specified in 'abis' then they will be yielded at
        their normal position and not at the beginning.
        """
        # Provide defaults based on target, rather than current system
        if python_version is None:
            python_version = (
                target.version.version.major,
                target.version.version.minor,
            )
        if not platforms:
            platforms = _platform_tags(target)

        # Call the original function with the updated python version and platforms
        return orig_compatible_tags(
            python_version=python_version,
            interpreter=interpreter,
            platforms=platforms,
        )

    # Patch in the original module
    pip._vendor.packaging.tags.compatible_tags = compatible_tags
    # Patch where it has been imported
    pip._internal.utils.compatibility_tags.compatible_tags = compatible_tags

    yield

    pip._vendor.packaging.tags.compatible_tags = orig_compatible_tags
    pip._internal.utils.compatibility_tags.compatible_tags = orig_compatible_tags


@contextlib.contextmanager
def _monkey_patch_marker_evaluate(
    target: TargetConfig,
) -> Generator[None, None, None]:
    """
    Monkey patch ``pip._vendor.packaging.markers.Marker`` to use the given platform and python version.
    """
    import pip._vendor.packaging.markers
    from packaging.markers import default_environment

    orig_evaluate = pip._vendor.packaging.markers.Marker.evaluate

    def evaluate(
        self: pip._vendor.packaging.markers.Marker,
        environment: Optional[Environment] = None,
    ) -> bool:
        """
        This is a modified version of the original evaluate function.

        Original docs below:

        Evaluate a marker.

        Return the boolean from evaluating the given marker against the
        environment. environment is an optional argument to override all or
        part of the determined environment.

        The environment is determined from the current Python process.
        """
        current_environment = default_environment()
        if environment is not None:
            current_environment.update(environment)
        with_python_env = _with_updated_python_version_environment(
            current_environment, target.version
        )
        with_platform_env = _with_updated_platform(with_python_env, target.platform)

        return pip._vendor.packaging.markers._evaluate_markers(
            self._markers, with_platform_env
        )

    pip._vendor.packaging.markers.Marker.evaluate = evaluate  # type: ignore

    yield

    pip._vendor.packaging.markers.Marker.evaluate = orig_evaluate  # type: ignore


@contextlib.contextmanager
def _monkey_patch_sysconfig_get_platform(
    target: TargetConfig,
) -> Generator[None, None, None]:
    """
    Monkey patch ``sysconfig.get_platform`` to use the given platform.
    """
    import sysconfig

    orig_platform = sysconfig.get_platform

    def get_platform() -> str:
        """
        This is a modified version of the original get_platform function.

        Original docs below:

        Return a string that identifies the current platform.

        This is used mainly to distinguish platform-specific build directories and
        platform-specific built distributions.  Typically includes the OS name and
        version and the architecture (as supplied by 'os.uname()'), although the
        exact information included depends on the OS; on Linux, the kernel version
        isn't particularly important.

        Examples of returned values:
           linux-i586
           linux-alpha (?)
           solaris-2.6-sun4u

        Windows will return one of:
           win-amd64 (64bit Windows on AMD64 (aka x86_64, Intel64, EM64T, etc)
           win32 (all others - specifically, sys.platform is returned)

        For other non-POSIX platforms, currently just returns 'sys.platform'.
        """
        os_name = target.platform.os_name
        machine = target.platform.platform_machine
        platform_machine_lower = machine.lower()

        if os_name == "nt":
            if "amd64" in platform_machine_lower:
                return "win-amd64"
            if "(arm)" in platform_machine_lower:
                return "win-arm32"
            if "(arm64)" in platform_machine_lower:
                return "win-arm64"
            return target.platform.sys_platform

        # As the target is mac, os_release must be defined
        os_release = cast(str, target.platform.os_release)

        # TODO: removed check for hasattr(os, 'uname') as not sure how to handle
        if os_name != "posix":
            # XXX what about the architecture? NT is Intel or Alpha
            return target.platform.sys_platform

        # TODO: Removed check for _PYTHON_HOST_PLATFORM, is this a problem?

        if target.platform.sys_platform.lower()[:5] == "linux":
            # At least on Linux/Intel, 'machine' is the processor --
            # i386, etc.
            # XXX what about Alpha, SPARC, etc?
            return f"{target.platform.sys_platform}-{machine}"
        # TODO: Handle sunos, aix, cygwin properly (see what was removed from original sysconfig.get_platform)
        elif target.platform.sys_platform.lower()[:6] == "darwin":
            import _osx_support

            os_name, os_release, machine = _osx_support.get_platform_osx(
                {
                    "MACOSX_DEPLOYMENT_TARGET": os_release,
                },
                os_name,
                os_release,
                machine,
            )

        return f"{os_name}-{os_release}-{machine}"

    sysconfig.get_platform = get_platform  # type: ignore

    yield

    sysconfig.get_platform = orig_platform  # type: ignore


def _platform_tags(target: TargetConfig) -> List[str]:
    """
    Modified version of pip._vendor.packaging.tags.platform_tags that uses the given target
    rather than the current system.
    """
    from packaging.tags import _generic_platforms, _linux_platforms, mac_platforms

    with _monkey_patch_sysconfig_get_platform(target):
        if target.platform.platform_system == "Darwin":
            # As the target is mac, os_release must be defined
            os_release = cast(str, target.platform.os_release)
            release_tup = tuple(int(i) for i in os_release.split(".")[0:2])
            if len(release_tup) != 2:
                raise ValueError(
                    "Invalid MacOS version, should be major.minor, e.g. 10.15"
                )
            # Now must have two elements
            release_tup = cast(Tuple[int, int], release_tup)
            platforms_gen = mac_platforms(release_tup, target.platform.platform_machine)
        elif target.platform.platform_system == "Linux":
            platforms_gen = _linux_platforms()
        else:
            platforms_gen = _generic_platforms()
        return list(platforms_gen)


def _with_updated_python_version_environment(
    env: Environment, python_version: Optional[PythonVersionConfig]
) -> Environment:
    out_env = env.copy() or {}
    if python_version is None:
        return out_env
    full_version = str(python_version.version)
    out_env["python_version"] = python_version.main_version
    out_env["python_full_version"] = full_version
    out_env["implementation_version"] = full_version
    out_env["implementation_name"] = python_version.implementation_name
    out_env["platform_python_implementation"] = python_version.implementation_name
    return out_env


def _with_updated_platform(
    env: Environment, platform: Optional[PlatformConfig]
) -> Environment:
    out_env = env.copy() or {}
    if platform is None:
        return out_env
    out_env["os_name"] = platform.os_name
    out_env["platform_system"] = platform.platform_system
    out_env["sys_platform"] = platform.sys_platform
    out_env["platform_machine"] = platform.platform_machine
    return out_env
