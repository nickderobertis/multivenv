from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, TypeVar

import cliconf
import typer
from rich.progress import Progress

from multivenv._compile import compile_venv_requirements
from multivenv._config import TargetsUserConfig, VenvConfig, VenvUserConfig
from multivenv._delete import delete_venv
from multivenv._info import AllInfo, InfoFormat, create_venv_info
from multivenv._run import ErrorHandling, run_in_venv
from multivenv._state import venv_needs_sync
from multivenv._styles import printer, styled
from multivenv._sync import sync_venv
from multivenv.exc import MutlivenvConfigVenvsNotDefinedException, NoSuchVenvException

cli = cliconf.CLIConf(name="mvenv")
conf_settings = cliconf.CLIAppConfig(
    app_name="mvenv", config_name="mvenv", multi_format=True
)
cliconf_settings = cliconf.CLIConfSettings(recursive_loading=True)

COMMAND_ARG = typer.Argument(..., help="Command to run")

ERROR_HANDLING_OPTION = typer.Option(
    ErrorHandling.PROPAGATE,
    "-e",
    "--errors",
    help="How to handle errors while running commands. Default is to propagate: the CLI "
    "will exit with the code that the underlying command exited with. ",
)
NO_AUTO_SYNC_OPTION = typer.Option(
    False,
    "-n",
    "--no-auto-sync",
    help="Don't sync the venv before running the command",
)
NO_UPGRADE_OPTION = typer.Option(
    False,
    "-u",
    "--no-upgrade",
    help="Don't upgrade the dependencies when compiling. If they are already specified in "
    "the output requirements, the same version will be used.",
)
PERSISTENT_OPTION = typer.Option(
    None,
    "--persistent",
    is_flag=True,
    help="Keep the venv after the command has finished",
)
POST_CREATE_OPTION = typer.Option(
    None,
    "-p",
    "--post-create",
    help="Run this command after the venv has been created",
)
POST_SYNC_OPTION = typer.Option(
    None,
    "-s",
    "--post-sync",
    help="Run this command after the venv has been synced",
)
QUIET_OPTION = typer.Option(
    False,
    "-q",
    "--quiet",
    help="Don't print anything to the console",
    show_default=False,
)
TARGETS_OPTION = typer.Option(
    None,
    "-t",
    "--target",
    help="Targets to compile for. Defaults to the current platform and python version.",
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


# TODO: Detect and reject when user has configured multiple venvs to have the same output requirements file


@cli.command()
@cliconf.configure(conf_settings, cliconf_settings)
def sync(
    venv_names: Optional[List[str]] = VENV_NAMES_ARG,
    venvs: Optional[Venvs] = None,
    venv_folder: Path = VENV_FOLDER_OPTION,
    quiet: bool = QUIET_OPTION,
    post_create: Optional[List[str]] = POST_CREATE_OPTION,
    post_sync: Optional[List[str]] = POST_SYNC_OPTION,
    errors: ErrorHandling = ERROR_HANDLING_OPTION,
):
    if quiet:
        printer.make_quiet()

    venv_configs = _create_internal_venv_configs(
        venvs, venv_names, venv_folder, post_create=post_create, post_sync=post_sync
    )
    should_sync_venv_configs = [
        venv_config for venv_config in venv_configs if venv_config.persistent
    ]
    if not should_sync_venv_configs:
        printer.alert("No persistent venvs found")
        return

    return _loop_sequential_progress(
        should_sync_venv_configs,
        lambda v: sync_venv(v, errors=errors),
        lambda v: f"Syncing {v.name}",
        lambda v: f"Synced {v.name}",
    )


@cli.command()
@cliconf.configure(conf_settings, cliconf_settings)
def compile(
    venv_names: Optional[List[str]] = VENV_NAMES_ARG,
    venvs: Optional[Venvs] = None,
    venv_folder: Path = VENV_FOLDER_OPTION,
    targets: Optional[TargetsUserConfig] = TARGETS_OPTION,
    no_upgrade: bool = NO_UPGRADE_OPTION,
    quiet: bool = QUIET_OPTION,
):
    if quiet:
        printer.make_quiet()

    venv_configs = _create_internal_venv_configs(
        venvs,
        venv_names,
        venv_folder,
        targets=targets,
        no_auto_upgrade=no_upgrade,
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
    targets: Optional[TargetsUserConfig] = TARGETS_OPTION,
    no_upgrade: bool = NO_UPGRADE_OPTION,
    quiet: bool = QUIET_OPTION,
    post_create: Optional[List[str]] = POST_CREATE_OPTION,
    post_sync: Optional[List[str]] = POST_SYNC_OPTION,
    errors: ErrorHandling = ERROR_HANDLING_OPTION,
):
    if quiet:
        printer.make_quiet()

    venv_configs = _create_internal_venv_configs(
        venvs,
        venv_names,
        venv_folder,
        targets=targets,
        post_create=post_create,
        post_sync=post_sync,
        no_auto_upgrade=no_upgrade,
    )

    def compile_and_sync(venv_config: VenvConfig):
        compile_venv_requirements(venv_config)
        if venv_config.persistent:
            sync_venv(venv_config, errors=errors)

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
    errors: ErrorHandling = ERROR_HANDLING_OPTION,
    quiet: bool = QUIET_OPTION,
    no_auto_sync: bool = NO_AUTO_SYNC_OPTION,
    persistent: bool = PERSISTENT_OPTION,
    post_create: Optional[List[str]] = POST_CREATE_OPTION,
    post_sync: Optional[List[str]] = POST_SYNC_OPTION,
):
    if quiet:
        printer.make_quiet()

    venv_configs = _create_internal_venv_configs(
        venvs,
        [venv_name],
        venv_folder,
        persistent=persistent,
        post_create=post_create,
        post_sync=post_sync,
    )
    auto_sync = not no_auto_sync
    if len(venv_configs) == 0:
        raise NoSuchVenvException(f"Could not find {venv_name} in {venvs}")
    assert len(venv_configs) == 1
    venv_config = venv_configs[0]

    if not venv_config.persistent or (auto_sync and venv_needs_sync(venv_config)):
        _loop_sequential_progress(
            [venv_config],
            lambda v: sync_venv(v, errors=errors),
            lambda v: f"Syncing {v.name}",
            lambda v: f"Synced {v.name}",
        )

    full_command = " ".join(command)
    result = run_in_venv(venv_config, full_command, errors=errors)
    if not venv_config.persistent:
        delete_venv(venv_config, ignore_errors=True)
    if errors == ErrorHandling.PROPAGATE:
        exit(result.exit_code)


@cli.command()
@cliconf.configure(conf_settings, cliconf_settings)
def run_all(
    command: List[str] = COMMAND_ARG,
    venvs: Optional[Venvs] = None,
    venv_folder: Path = VENV_FOLDER_OPTION,
    errors: ErrorHandling = ERROR_HANDLING_OPTION,
    quiet: bool = QUIET_OPTION,
    no_auto_sync: bool = NO_AUTO_SYNC_OPTION,
    persistent: bool = PERSISTENT_OPTION,
    post_create: Optional[List[str]] = POST_CREATE_OPTION,
    post_sync: Optional[List[str]] = POST_SYNC_OPTION,
):
    if quiet:
        printer.make_quiet()

    venv_configs = _create_internal_venv_configs(
        venvs,
        None,
        venv_folder,
        persistent=persistent,
        post_create=post_create,
        post_sync=post_sync,
    )
    auto_sync = not no_auto_sync
    full_command = " ".join(command)
    for venv_config in venv_configs:
        if not venv_config.persistent or (auto_sync and venv_needs_sync(venv_config)):
            _loop_sequential_progress(
                [venv_config],
                lambda v: sync_venv(v, errors=errors),
                lambda v: f"Syncing {v.name}",
                lambda v: f"Synced {v.name}",
            )
        print(f"Running command in {venv_config.name}")
        # TODO: add progress bar for run all. Need to create two separate sections in a live display
        result = run_in_venv(venv_config, full_command, errors=errors)
        if not venv_config.persistent:
            delete_venv(venv_config, ignore_errors=True)
        if errors == ErrorHandling.PROPAGATE and result.exit_code != 0:
            exit(result.exit_code)


@cli.command()
@cliconf.configure(conf_settings, cliconf_settings)
def info(
    venv_names: Optional[List[str]] = VENV_NAMES_ARG,
    info_format: InfoFormat = typer.Option(
        InfoFormat.TEXT,
        "--info-format",
        "-i",
        help="Output format for venv info. Defaults to text.",
        show_default=False,
    ),
    venvs: Optional[Venvs] = None,
    venv_folder: Path = VENV_FOLDER_OPTION,
    targets: Optional[TargetsUserConfig] = TARGETS_OPTION,
    quiet: bool = QUIET_OPTION,
) -> AllInfo:
    if quiet:
        printer.make_quiet()

    venv_configs = _create_internal_venv_configs(
        venvs,
        venv_names,
        venv_folder,
        targets=targets,
    )
    all_info = AllInfo(
        venv_info=[create_venv_info(venv_config) for venv_config in venv_configs]
    )
    if info_format == InfoFormat.TEXT:
        printer.print(all_info)
    elif info_format == InfoFormat.JSON:
        printer.print(all_info.json(indent=2))
    else:
        raise NotImplementedError(f"Info format {info_format} not implemented")

    return all_info


@cli.command()
@cliconf.configure(conf_settings, cliconf_settings)
def delete(
    venv_names: Optional[List[str]] = VENV_NAMES_ARG,
    venvs: Optional[Venvs] = None,
    venv_folder: Path = VENV_FOLDER_OPTION,
    quiet: bool = QUIET_OPTION,
):
    if quiet:
        printer.make_quiet()

    venv_configs = _create_internal_venv_configs(venvs, venv_names, venv_folder)
    should_delete_venv_configs = [
        venv_config
        for venv_config in venv_configs
        if venv_config.persistent and venv_config.path.exists()
    ]
    if not should_delete_venv_configs:
        printer.alert("No existing venvs found matching the given criteria")
        return
    return _loop_sequential_progress(
        venv_configs,
        delete_venv,
        lambda v: f"Deleting {v.name}",
        lambda v: f"Deleted {v.name}",
    )


def _create_internal_venv_configs(
    venvs: Optional[Venvs],
    venv_names: Optional[List[str]],
    venv_folder: Path,
    targets: Optional[TargetsUserConfig] = None,
    persistent: Optional[bool] = None,
    no_auto_upgrade: bool = False,
    post_create: Optional[List[str]] = None,
    post_sync: Optional[List[str]] = None,
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
            global_targets=targets,
            global_persistent=persistent,
            global_post_create=post_create,
            global_post_sync=post_sync,
            global_auto_upgrade=not no_auto_upgrade,
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
