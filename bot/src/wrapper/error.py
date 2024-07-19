class UnknownError(Exception): ...


class NetworkError(ConnectionError): ...


class UnknownNetworkError(UnknownError, NetworkError): ...


class AlreadyExistError(NetworkError, FileExistsError): ...


class DoNotExistError(NetworkError, FileNotFoundError): ...


class UserError(Exception): ...