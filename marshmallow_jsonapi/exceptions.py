"""Exception classes."""


class JSONAPIError(Exception):
    """Base class for all exceptions in this package."""

    pass


class IncorrectTypeError(JSONAPIError, ValueError):
    """Raised when client provides an invalid `type` in a request."""

    pointer = "/data/type"
    default_message = 'Invalid type. Expected "{expected}".'

    def __init__(self, message=None, actual=None, expected=None):
        message = message or self.default_message
        format_kwargs = {}
        if actual:
            format_kwargs["actual"] = actual
        if expected:
            format_kwargs["expected"] = expected
        self.detail = message.format(**format_kwargs)
        super().__init__(self.detail)

    @property
    def messages(self):
        """JSON API-formatted error representation."""
        return {
            "errors": [{"detail": self.detail, "source": {"pointer": self.pointer}}]
        }
