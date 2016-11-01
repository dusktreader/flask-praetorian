import flask

from textwrap import dedent


class PraetorianError(Exception):
    """
    Provides a custom exception class for flask-praetorian. This class is fancy
    because it has the ability to automatically format its message string with
    additional args and kwargs
    """

    @classmethod
    def require_condition(cls, expr, failure_message, *format_args,
                          status_code=401, **format_kwds):
        """
        This utility method checks a boolean expression for truth. If that
        check fails, it raises an exception with a cutomizable message

        :param expr:         The expression to test for truthiness
        :param fail_message: The message to attach to the exception on failure
        """
        if not expr:
            raise cls(failure_message, *format_args,
                      status_code=status_code, **format_kwds)

    def __init__(self, message, *format_args, status_code=401, **format_kwds):
        """
        Initializes the exception

        :param message:     The message to return. May have formatting marks
        :param format_args: Format arguments. Follows str.format convention
        :param format_kwds: Format keyword args. Follows str.format convetion
        """
        self.message = dedent(message).format(*format_args, **format_kwds)
        self.status_code = status_code
        self.headers = None

    def __repr__(self):
        return self.__class__.__name__

    def __str__(self):
        return self.message

    def jsonify(self):
        """
        Returns a representation of the error in a jsonic form that is
        compatible with flask's error handling
        """
        return flask.jsonify({
            'status_code': self.status_code,
            'error': repr(self),
            'description': self.message,
        })
