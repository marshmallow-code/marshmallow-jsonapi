# -*- coding: utf-8 -*-

class JSONAPIError(Exception):
    """Base class for all exceptions in this package."""
    pass

class IncorrectTypeError(JSONAPIError, ValueError):
    """Raised when client provides an invalid `type` in a request."""
    default_message = 'Invalid type. Expected "{expected}".'

    def __init__(self, message=None, actual=None, expected=None):
        message = message or self.default_message
        format_kwargs = {}
        if actual:
            format_kwargs['actual'] = actual
        if expected:
            format_kwargs['expected'] = expected
        super(IncorrectTypeError, self).__init__(message.format(**format_kwargs))
