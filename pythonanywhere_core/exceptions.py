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


class SlowStartupException(PythonAnywhereApiException):
    def __init__(self) -> None:
        super().__init__(
            "Website startup could not be confirmed after the reload attempt. "
            "Check your website's server and error logs."
        )


class MissingCNAMEException(PythonAnywhereApiException):
    def __init__(self):
        super().__init__(
            "Could not find a CNAME for your website. If you're using an A record, "
            "CloudFlare, or some other way of pointing your domain at PythonAnywhere "
            "then that should not be a problem. If you're not, you should double-check "
            "your DNS setup."
        )
