import contextlib
from typing import Generator, Optional

from multivenv._config import PlatformConfig, PythonVersionConfig, TargetConfig
from multivenv._ext_packaging import Environment


@contextlib.contextmanager
def monkey_patch_pip_packaging_markers_to_target(
    target: TargetConfig,
) -> Generator[None, None, None]:
    """
    Monkey patch ``pip._vendor.packaging.markers.Marker`` to use the given platform and python version.

    This will make it return nested requirements as if on that system
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
