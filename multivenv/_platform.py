import distutils.util


def get_platform() -> str:
    # TODO: Add handling for manylinux1
    #  See: https://peps.python.org/pep-0513/

    platform = distutils.util.get_platform()
    return platform_to_pypi_tag(platform)


def platform_to_pypi_tag(platform: str) -> str:
    # See: https://peps.python.org/pep-0425/#platform-tag
    return platform.replace("-", "_").replace(".", "_")
