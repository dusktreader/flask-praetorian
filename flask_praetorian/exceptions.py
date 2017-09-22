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
    """
    The jwt token is missing a required claim
    """
    pass


class BlacklistedError(PraetorianError):
    """
    The jwt token has been blacklisted and may not be used any more
    """
    pass


class ExpiredAccessError(PraetorianError):
    """
    The jwt token has expired for access and must be refreshed
    """
    pass


class EarlyRefreshError(PraetorianError):
    """
    The jwt token has not yet expired for access and may not be refreshed
    """
    pass


class ExpiredRefreshError(PraetorianError):
    """
    The jwt token has expired for refresh. An entirely new token must be issued
    """
    pass


class MissingTokenHeader(PraetorianError):
    """
    The header is missing the required jwt token
    """
    pass


class InvalidTokenHeader(PraetorianError):
    """
    The token contained in the header is invalid
    """
    pass


class InvalidUserError(PraetorianError):
    """
    The user is no longer valid and is now not authorized
    """
    pass
