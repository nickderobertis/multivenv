import distutils.util
import sys


def get_platform() -> str:
    # TODO: Add handling for manylinux1
    #  See: https://peps.python.org/pep-0513/

    platform = distutils.util.get_platform()
    return platform_to_pypi_tag(platform)


# TODO: better python version matching
def get_python_version() -> str:
    return f"{sys.version_info[0]}.{sys.version_info[1]}"


def platform_to_pypi_tag(platform: str) -> str:
    # See: https://peps.python.org/pep-0425/#platform-tag
    return platform.replace("-", "_").replace(".", "_")
