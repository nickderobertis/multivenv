from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, TypeVar

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
):
    venv_configs = _create_internal_venv_configs(venvs, venv_names, venv_folder)
    return _loop_sequential_progress(
        venv_configs,
        compile_venv_requirements,
        lambda v: f"Compiling {v.name}",
        lambda v: f"Compiled {v.name}",
    )


def update():
    # TODO: fill out update after finalizing sync and compile api
    pass


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
    # TODO: better CLI output
    print(run_in_venv(venv_config, full_command))


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
        print(f"Running in {venv_config.name}")
        print(run_in_venv(venv_config, full_command))


def _create_internal_venv_configs(
    venvs: Optional[Venvs], venv_names: Optional[List[str]], venv_folder: Path
):
    if not venvs:
        raise MutlivenvConfigVenvsNotDefinedException(
            "Must have venvs defined in the config. Pass --config-gen to set up a new config"
        )
    venv_names = venv_names or [v for v in venvs]
    venv_configs = [
        VenvConfig.from_user_config(venv_config, name, venv_folder / name)
        for name, venv_config in venvs.items()
        if name in venv_names
    ]
    return venv_configs


T = TypeVar("T")


def _loop_sequential_progress(
    iterable: Iterable[T],
    fn: Callable[[T], None],
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
