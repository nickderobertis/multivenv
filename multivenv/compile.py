from pathlib import Path

from multivenv.config import VenvConfig
from multivenv.ext_subprocess import CLIResult, run


def compile_venv_requirements(config: VenvConfig):
    pip_tools_compile(config.requirements_in, config.requirements_out)


def pip_tools_compile(requirements_in: Path, requirements_out: Path) -> CLIResult:
    return run(f"pip-compile {requirements_in} -o {requirements_out}")
