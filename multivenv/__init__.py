"""
Python Virtualenv manager supporting multiple venvs and platforms in one project
"""
import warnings

warnings.filterwarnings(
    "ignore", category=UserWarning, message="Setuptools is replacing distutils."
)

from multivenv._cli import Venvs, compile, info, run, run_all, sync, update
from multivenv._config import VenvUserConfig
from multivenv._info import AllInfo, VenvInfo
from multivenv._run import ErrorHandling
