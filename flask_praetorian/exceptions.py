class PraetorianError(Exception):
    """
    Provides a custom exception class for flask-praetorian. This class is fancy
    because it has the ability to automatically format its message string with
    additional args and kwargs
    """

    @classmethod
    def require_condition(cls, expr, fail_message='condition failed',
                          *format_args, **format_kwds):
        """
        This utility method checks a boolean expression for truth. If that
        check fails, it raises an exception with a cutomizable message

        :param expr:         The expression to test for truthiness
        :param fail_message: The message to attach to the exception on failure
        """
        if not expr:
            raise cls(fail_message, *format_args, **format_kwds)

    def __init__(self, message, *format_args, **format_kwds):
        """
        Initializes the exception

        :param message:     The message to return. May have formatting marks
        :param format_args: Format arguments. Follows str.format convention
        :param format_kwds: Format keyword args. Follows str.format convetion
        """
        self.message = message.format(*format_args, **format_kwds)

    def __str__(self):
        return self.message
