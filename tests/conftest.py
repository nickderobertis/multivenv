import os

import pytest

from tests.config import PROJECT_DIR


@pytest.fixture(autouse=True)
def around_each():
    yield
    # Sometimes if a test fails, it is left in a temp directory that gets deleted
    # Reset the working directory to the project directory between tests
    os.chdir(PROJECT_DIR)
