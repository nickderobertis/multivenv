from typing import Final

from rich.console import Console

from multivenv._types import HasStr

console: Final[Console] = Console()
legacy_windows = console.legacy_windows

# Legacy windows does not seem to support unicode, so strip out the emojis on that platform
INFO_STYLE: Final[str] = ""
SUCCESS_STYLE: Final[str] = (
    "[green]:heavy_check_mark:" if not legacy_windows else "[green]"
)
ALERT_STYLE: Final[str] = "[red]:x:" if not legacy_windows else "[red]"
ACTION_REQUIRED_STYLE: Final[str] = (
    "[yellow]:pencil:" if not legacy_windows else "[yellow]"
)


def styled(message: str, style: str) -> str:
    return f"{style} {message}"


class ConsolePrinter:
    styles = {
        "info": INFO_STYLE,
        "success": SUCCESS_STYLE,
        "alert": ALERT_STYLE,
        "action_required": ACTION_REQUIRED_STYLE,
    }

    def __init__(self, console: Console):
        self.console = console

    def print(self, message: HasStr, end: str = "\n"):
        self.console.print(message, end=end)

    def info(self, message: str):
        self.console.print(styled(message, self.styles["info"]))

    def success(self, message: str):
        self.console.print(styled(message, self.styles["success"]))

    def alert(self, message: str):
        self.console.print(styled(message, self.styles["alert"]))

    def action_required(self, message: str):
        self.console.print(styled(message, self.styles["action_required"]))

    def make_quiet(self):
        self.console.quiet = True


printer = ConsolePrinter(console)
