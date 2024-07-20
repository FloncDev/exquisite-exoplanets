class UnknownError(Exception):
    """A unknown error have occurred."""


class NetworkError(ConnectionError):
    """A network error have occurred."""


class UnknownNetworkError(UnknownError, NetworkError):
    """An unknown network error have occurred."""


class AlreadyExistError(NetworkError, FileExistsError):
    """The error which represent the material the client attempted to create already exist on the server."""


class DoNotExistError(NetworkError, FileNotFoundError):
    """The error which represent the requested material do not exist on the server."""


class UserError(Exception):
    """An error cause by the user causing the request failed to proceed."""
