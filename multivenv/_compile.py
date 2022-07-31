import itertools
from contextlib import nullcontext
from pathlib import Path
from typing import List, Optional

import click
from click.utils import LazyFile
from piptools.scripts.compile import cli as compile_click_command

from multivenv._config import TargetConfig, VenvConfig
from multivenv._env import with_pip_tools_custom_compile_command_as_mvenv_compile
from multivenv._ext_pip import monkey_patch_pip_packaging_markers_to_target
from multivenv._ext_subprocess import CLIResult, run


def compile_venv_requirements(config: VenvConfig):
    if not config.targets:
        # Targeting only current system, compile on the current
        return pip_tools_compile(config.requirements_in, config.requirements_out)

    # Multiple targets, compile on each
    # TODO: unsure why type ignores are needed here, seems accurate
    for target in config.targets:
        pip_tools_compile(
            config.requirements_in,
            config.requirements_out_path_for(target),
            target,
        )


def pip_tools_compile(
    requirements_in: Path, requirements_out: Path, target: Optional[TargetConfig] = None
) -> CLIResult:
    ctx = click.Context(compile_click_command)

    # Determine whether to patch for target
    if target is not None:
        target_context_manager = monkey_patch_pip_packaging_markers_to_target(target)
    else:
        target_context_manager = nullcontext()

    with LazyFile(
        str(requirements_out), mode="w+b", atomic=True
    ) as f, target_context_manager, with_pip_tools_custom_compile_command_as_mvenv_compile():
        ctx.invoke(
            compile_click_command,
            src_files=[str(requirements_in)],
            output_file=f,
            generate_hashes=True,
            rebuild=True,
        )
    return

    env = {"CUSTOM_COMPILE_COMMAND": "mvenv compile"}
    base_command = (
        f"pip-compile --generate-hashes {requirements_in} -o {requirements_out}"
    )
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
