from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, TypeVar

import cliconf
import typer
from rich.progress import Progress

from multivenv.compile import compile_venv_requirements
from multivenv.config import VenvConfig, VenvUserConfig
from multivenv.exc import MutlivenvConfigVenvsNotDefinedException, NoSuchVenvException
from multivenv.run import run_in_venv
from multivenv.styles import printer, styled
from multivenv.sync import sync_venv

cli = cliconf.CLIConf(name="mvenv")
conf_settings = cliconf.CLIAppConfig(
    app_name="mvenv", config_name="mvenv", multi_format=True
)
cliconf_settings = cliconf.CLIConfSettings(recursive_loading=True)

COMMAND_ARG = typer.Argument(..., help="Command to run")
PLATFORMS_OPTION = typer.Option(
    None,
    "-p",
    "--platform",
    help="Platform (OS) to compile for. Defaults to the current platform",
    show_default=False,
)
PYTHON_VERSIONS_OPTION = typer.Option(
    None,
    "-v",
    "--version",
    help="Python versions to compile for. Defaults to the current python version",
    show_default=False,
)
VENV_NAMES_ARG = typer.Argument(
    None,
    help="Names of the virtual environments to work on. Defaults to all",
    show_default=False,
)

VENV_FOLDER_OPTION = typer.Option(
    Path("venvs"),
    "-f",
    "--folder",
    help="Folder to put venvs in. Defaults to venvs folder in current directory",
    show_default=False,
)

Venvs = Dict[str, Optional[VenvUserConfig]]


@cli.command()
@cliconf.configure(conf_settings, cliconf_settings)
def sync(
    venv_names: Optional[List[str]] = VENV_NAMES_ARG,
    venvs: Optional[Venvs] = None,
    venv_folder: Path = VENV_FOLDER_OPTION,
):
    venv_configs = _create_internal_venv_configs(venvs, venv_names, venv_folder)
    return _loop_sequential_progress(
        venv_configs,
        sync_venv,
        lambda v: f"Syncing {v.name}",
        lambda v: f"Synced {v.name}",
    )


@cli.command()
@cliconf.configure(conf_settings, cliconf_settings)
def compile(
    venv_names: Optional[List[str]] = VENV_NAMES_ARG,
    venvs: Optional[Venvs] = None,
    venv_folder: Path = VENV_FOLDER_OPTION,
    versions: Optional[List[str]] = PYTHON_VERSIONS_OPTION,
    platforms: Optional[List[str]] = PLATFORMS_OPTION,
):
    venv_configs = _create_internal_venv_configs(
        venvs, venv_names, venv_folder, versions=versions, platforms=platforms
    )
    return _loop_sequential_progress(
        venv_configs,
        compile_venv_requirements,
        lambda v: f"Compiling {v.name}",
        lambda v: f"Compiled {v.name}",
    )


@cli.command()
@cliconf.configure(conf_settings, cliconf_settings)
def update(
    venv_names: Optional[List[str]] = VENV_NAMES_ARG,
    venvs: Optional[Venvs] = None,
    venv_folder: Path = VENV_FOLDER_OPTION,
    versions: Optional[List[str]] = PYTHON_VERSIONS_OPTION,
    platforms: Optional[List[str]] = PLATFORMS_OPTION,
):
    venv_configs = _create_internal_venv_configs(
        venvs, venv_names, venv_folder, versions=versions, platforms=platforms
    )

    def compile_and_sync(venv_config: VenvConfig):
        compile_venv_requirements(venv_config)
        sync_venv(venv_config)

    return _loop_sequential_progress(
        venv_configs,
        compile_and_sync,
        lambda v: f"Updating {v.name}",
        lambda v: f"Updated {v.name}",
    )


@cli.command()
@cliconf.configure(conf_settings, cliconf_settings)
def run(
    venv_name: str = typer.Argument(
        ..., help="Name of the virtual environment to run command in"
    ),
    command: List[str] = COMMAND_ARG,
    venvs: Optional[Venvs] = None,
    venv_folder: Path = VENV_FOLDER_OPTION,
):
    venv_configs = _create_internal_venv_configs(venvs, [venv_name], venv_folder)
    if len(venv_configs) == 0:
        raise NoSuchVenvException(f"Could not find {venv_name} in {venvs}")
    assert len(venv_configs) == 1
    venv_config = venv_configs[0]

    full_command = " ".join(command)
    run_in_venv(venv_config, full_command)


@cli.command()
@cliconf.configure(conf_settings, cliconf_settings)
def run_all(
    command: List[str] = COMMAND_ARG,
    venvs: Optional[Venvs] = None,
    venv_folder: Path = VENV_FOLDER_OPTION,
):
    if not venvs:
        raise ValueError(
            "Must have venvs defined in the config. Pass --config-gen to set up a new config"
        )
    venv_configs = _create_internal_venv_configs(venvs, None, venv_folder)
    full_command = " ".join(command)
    for venv_config in venv_configs:
        # TODO: add progress bar for run all. Need to create two separate sections in a live display
        print(f"Running command in {venv_config.name}")
        run_in_venv(venv_config, full_command)


def _create_internal_venv_configs(
    venvs: Optional[Venvs],
    venv_names: Optional[List[str]],
    venv_folder: Path,
    versions: Optional[List[str]] = None,
    platforms: Optional[List[str]] = None,
):
    if not venvs:
        raise MutlivenvConfigVenvsNotDefinedException(
            "Must have venvs defined in the config. Pass --config-gen to set up a new config"
        )
    venv_names = venv_names or [v for v in venvs]
    venv_configs = [
        VenvConfig.from_user_config(
            venv_config,
            name,
            venv_folder / name,
            global_versions=versions,
            global_platforms=platforms,
        )
        for name, venv_config in venvs.items()
        if name in venv_names
    ]
    return venv_configs


T = TypeVar("T")


def _loop_sequential_progress(
    iterable: Iterable[T],
    fn: Callable[[T], Any],
    before_message_fn: Callable[[T], str],
    after_message_fn: Callable[[T], str],
):
    with Progress(console=printer.console, transient=True) as progress:
        for item in iterable:
            task = progress.add_task(
                styled(before_message_fn(item), printer.styles["info"]),
                start=False,
                total=None,
            )
            fn(item)
            progress.remove_task(task)
            printer.success(after_message_fn(item))


if __name__ == "__main__":
    cli()
