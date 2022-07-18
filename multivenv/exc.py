class MultivenvException(Exception):
    pass


class MultivenvConfigException(MultivenvException):
    pass


class MutlivenvConfigVenvsNotDefinedException(MultivenvConfigException):
    pass


class NoSuchVenvException(MultivenvConfigException):
    pass
