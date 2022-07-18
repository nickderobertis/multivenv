class MultivenvException(Exception):
    pass


class MultivenvConfigException(MultivenvException):
    pass


class MutlivenvConfigVenvsNotDefinedException(MultivenvConfigException):
    pass


class NoSuchVenvException(MultivenvConfigException):
    pass


class RequirementsFileException(MultivenvException):
    pass


class CompiledRequirementsNotFoundException(RequirementsFileException):
    pass
