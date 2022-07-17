from pathlib import Path
from typing import List, Optional

import cliconf
import typer

from multivenv.compile import compile_venv_requirements
from multivenv.config import VenvConfig, VenvUserConfig
from multivenv.run import run_in_venv
from multivenv.sync import sync_venv

cli = cliconf.CLIConf(name="mvenv")
conf_settings = cliconf.CLIAppConfig(
    app_name="mvenv", config_name="mvenv", multi_format=True
)
cliconf_settings = cliconf.CLIConfSettings(recursive_loading=True)

COMMAND_ARG = typer.Argument(..., help="Command to run")
VENV_NAMES_ARG = typer.Argument(
    ...,
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


@cli.command()
@cliconf.configure(conf_settings, cliconf_settings)
def sync(
    venv_names: List[str] = VENV_NAMES_ARG,
    venvs: Optional[List[VenvUserConfig]] = None,
    venv_folder: Path = VENV_FOLDER_OPTION,
):
    if not venvs:
        raise ValueError(
            "Must have venvs defined in the config. Pass --config-gen to set up a new config"
        )
    venv_names = venv_names or [v.name for v in venvs]
    venv_configs = [
        VenvConfig.from_user_config(venv_config, venv_folder / venv_config.name)
        for venv_config in venvs
        if venv_config.name in venv_names
    ]
    for venv_config in venv_configs:
        sync_venv(venv_config)


@cli.command()
@cliconf.configure(conf_settings, cliconf_settings)
def compile(
    venv_names: List[str] = VENV_NAMES_ARG,
    venvs: Optional[List[VenvUserConfig]] = None,
    venv_folder: Path = VENV_FOLDER_OPTION,
):
    if not venvs:
        raise ValueError(
            "Must have venvs defined in the config. Pass --config-gen to set up a new config"
        )
    venv_names = venv_names or [v.name for v in venvs]
    venv_configs = [
        VenvConfig.from_user_config(venv_config, venv_folder / venv_config.name)
        for venv_config in venvs
        if venv_config.name in venv_names
    ]
    for venv_config in venv_configs:
        compile_venv_requirements(venv_config)


def update():
    # TODO: fill out update after finalizing sync and compile api
    pass


@cli.command()
@cliconf.configure(conf_settings, cliconf_settings)
def run(
    venv_name: str = typer.Argument(
        ..., help="Name of the virtual environment to run command in"
    ),
    command: str = COMMAND_ARG,
    venvs: Optional[List[VenvUserConfig]] = None,
    venv_folder: Path = VENV_FOLDER_OPTION,
):
    if not venvs:
        raise ValueError(
            "Must have venvs defined in the config. Pass --config-gen to set up a new config"
        )
    # TODO: check for correct venv name
    venv_user_config = next(v for v in venvs if v.name == venv_name)
    venv_config = VenvConfig.from_user_config(
        venv_user_config, venv_folder / venv_user_config.name
    )
    run_in_venv(venv_config, command)


@cli.command()
@cliconf.configure(conf_settings, cliconf_settings)
def run_all(
    command: str = COMMAND_ARG,
    venvs: Optional[List[VenvUserConfig]] = None,
    venv_folder: Path = VENV_FOLDER_OPTION,
):
    if not venvs:
        raise ValueError(
            "Must have venvs defined in the config. Pass --config-gen to set up a new config"
        )
    venv_configs = [
        VenvConfig.from_user_config(venv_config, venv_folder / venv_config.name)
        for venv_config in venvs
    ]
    for venv_config in venv_configs:
        run_in_venv(venv_config, command)


if __name__ == "__main__":
    cli()
