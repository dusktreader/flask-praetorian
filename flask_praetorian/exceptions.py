import flask
import buzz


class PraetorianError(buzz.Buzz):
    """
    Provides a custom exception class for flask-praetorian based on Buzz.
    `py-buzz on gitub <https://github.com/dusktreader/py-buzz>`_
    """

    def __init__(self, *format_args, status_code=401, **format_kwds):
        super().__init__(*format_args, **format_kwds)
        self.status_code = status_code
        self.headers = None

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


class MissingClaimError(PraetorianError):
    pass


class BlacklistedError(PraetorianError):
    pass


class ExpiredAccessError(PraetorianError):
    pass


class EarlyRefreshError(PraetorianError):
    pass


class ExpiredRefreshError(PraetorianError):
    pass


class MissingTokenHeader(PraetorianError):
    pass


class InvalidTokenHeader(PraetorianError):
    pass
