import itertools
from pathlib import Path
from typing import Optional

from multivenv.config import VenvConfig
from multivenv.ext_subprocess import CLIResult, run


def compile_venv_requirements(config: VenvConfig):
    if not config.versions and not config.platforms:
        # Single version/platform, compile on the current
        return pip_tools_compile(config.requirements_in, config.requirements_out)

    # Multiple versions/platforms, compile on each
    versions = config.versions or [None]
    platforms = config.platforms or [None]
    for version, platform in itertools.product(versions, platforms):
        pip_tools_compile(
            config.requirements_in,
            config.requirements_out_path_for(version, platform),
            version,
            platform,
        )


def pip_tools_compile(
    requirements_in: Path,
    requirements_out: Path,
    version: Optional[str] = None,
    platform: Optional[str] = None,
) -> CLIResult:
    env = {"CUSTOM_COMPILE_COMMAND": "mvenv compile"}
    base_command = f"pip-compile {requirements_in} -o {requirements_out}"
    if platform or version:
        pip_args = []
        if platform:
            pip_args.append(f"--platform {platform}")
        if version:
            pip_args.append(f"--python-version {version}")
        command = f'{base_command} --pip-args "{" ".join(pip_args)}"'
    else:
        command = base_command
    return run(
        command,
        env=env,
        extend_existing_env=True,
        stream=False,
    )
