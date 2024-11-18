class AuthenticationError(Exception):
    pass


class SanityException(Exception):
    pass


class PythonAnywhereApiException(Exception):
    pass


class NoTokenError(PythonAnywhereApiException):
    pass


class DomainAlreadyExistsException(PythonAnywhereApiException):
    pass