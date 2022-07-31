from unittest.mock import patch

import pytest

from multivenv import _ext_packaging


@pytest.fixture
def windows_37_environment() -> _ext_packaging.Environment:
    windows_env: _ext_packaging.Environment = dict(
        os_name="nt",
        sys_platform="win32",
        platform_machine="AMD64",
        platform_python_implementation="CPython",
        platform_system="Windows",
        python_version="3.7",
        python_full_version="3.7.0",
        implementation_version="3.7.0",
        implementation_name="cpython",
    )
    with patch.object(_ext_packaging, "get_default_environment", lambda: windows_env):
        yield windows_env


@pytest.fixture
def linux_310_environment() -> _ext_packaging.Environment:
    linux_env: _ext_packaging.Environment = dict(
        os_name="posix",
        sys_platform="linux",
        platform_machine="x86_64",
        platform_python_implementation="CPython",
        platform_system="Linux",
        python_version="3.10",
        python_full_version="3.10.0",
        implementation_version="3.10.0",
        implementation_name="cpython",
    )
    with patch.object(_ext_packaging, "get_default_environment", lambda: linux_env):
        yield linux_env


@pytest.fixture
def wrong_environment() -> _ext_packaging.Environment:
    wrong_env: _ext_packaging.Environment = dict(
        os_name="Wrong",
        sys_platform="wrong",
        platform_machine="wrong",
        platform_python_implementation="Wrong",
        platform_system="Wrong",
        python_version="2.7",
        python_full_version="2.7.0",
        implementation_version="2.7.0",
        implementation_name="Wrong",
    )
    with patch.object(_ext_packaging, "get_default_environment", lambda: wrong_env):
        yield wrong_env
