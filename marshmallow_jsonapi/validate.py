from marshmallow.validate import Validator, ValidationError

class ForeignKey(Validator):
    """Validator which succeeds if the value it is passed is positive integer.
    """

    message_all = 'Must be and integer and greater than 0.'

    def __init__(self, error=None):
        self.min = 0
        self.error = error

    def _format_error(self, value, message):
        return (self.error or message).format(input=value)

    def __call__(self, value):
        if value < 1:
            message = self.message_all
            raise ValidationError(self._format_error(value, message))

        if not isinstance(value, int):
            message = self.message_all
            raise ValidationError(self._format_error(value, message))

        return value
