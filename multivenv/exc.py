class MultivenvException(Exception):
    pass


class MultivenvConfigException(MultivenvException):
    pass


class MutlivenvConfigVenvsNotDefinedException(MultivenvConfigException):
    pass


class NoSuchVenvException(MultivenvConfigException):
    pass


class NoSuchPlatformStringException(MultivenvConfigException):
    pass


class RequirementsFileException(MultivenvException):
    pass


class VenvNotSyncedException(MultivenvException):
    pass


class CompiledRequirementsNotFoundException(RequirementsFileException):
    pass


class MultivenvCommandException(MultivenvException):
    pass


class CommandExitException(MultivenvCommandException):
    def __init__(self, exit_code: int, command: str, output: str):
        self.exit_code = exit_code
        self.command = command
        self.output = output
        super().__init__(f"Command '{command}' exited with code {exit_code}")

    def __str__(self) -> str:
        return f"Command '{self.command}' exited with code {self.exit_code}. Output:\n{self.output}"
