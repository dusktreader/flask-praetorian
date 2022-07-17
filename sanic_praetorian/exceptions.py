from buzz import Buzz

from sanic.exceptions import SanicException
from sanic import json

"""
class PraetorianErrorHandler(ErrorHandler):
    def default(self, request, exception):
        exception = PraetorianError(exception)
        return super().default(request, exception)
"""


class PraetorianError(SanicException, Buzz):
    """
    Provides a custom exception class for sanic-praetorian based on py-buzz.
    `py-buzz on gitub <https://github.com/dusktreader/py-buzz>`_
    """
    status: int = 401
    json_response: dict = dict({})

    def __init__(self, message, *args, **kwargs):
        self.status = self.status
        self.message = f'{self.__class__.__name__}: {message}'
        self.extra_args = args
        self.extra_kwargs = kwargs
        self.json_response = json({"error": message, "data": self.__class__.__name__, "status": self.status}, status=self.status)
        super().__init__(self.message, self.status)

    def __str__(self):
        return f"{super().__str__()} ({self.status})"


class MissingClaimError(PraetorianError):
    """
    The jwt token is missing a required claim
    """
    pass


class BlacklistedError(PraetorianError):
    """
    The jwt token has been blacklisted and may not be used any more
    """
    status = 403


class ExpiredAccessError(PraetorianError):
    """
    The jwt token has expired for access and must be refreshed
    """
    pass


class EarlyRefreshError(PraetorianError):
    """
    The jwt token has not yet expired for access and may not be refreshed
    """
    status = 425  # HTTP Status Code : 425 Too Early


class ExpiredRefreshError(PraetorianError):
    """
    The jwt token has expired for refresh. An entirely new token must be issued
    """
    pass


class MissingToken(PraetorianError):
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
    status = 403


class MissingRoleError(PraetorianError):
    """
    The token is missing a required role
    """
    status = 403


class MissingUserError(PraetorianError):
    """
    The user could not be identified
    """
    pass


class AuthenticationError(PraetorianError):
    """
    The entered user's password did not match the stored password
    """
    pass


class ClaimCollisionError(PraetorianError):
    """"
    Custom claims to pack into the JWT payload collide with reserved claims
    """
    pass


class LegacyScheme(PraetorianError):
    """
    The processed hash is using an outdated scheme
    """
    pass


class InvalidResetToken(PraetorianError):
    """
    The supplied registration token is invalid
    """
    pass


class InvalidRegistrationToken(PraetorianError):
    """
    The supplied registration token is invalid
    """
    pass


class MisusedRegistrationToken(PraetorianError):
    """
    Attempted to use a registration token for normal access
    """
    pass


class MisusedResetToken(PraetorianError):
    """
    Attempted to use a password reset token for normal access
    """
    pass


class ConfigurationError(PraetorianError):
    """
    There was a problem with the configuration
    """
    pass


class TOTPRequired(AuthenticationError):
    """
    The user requires TOTP authentication, which was not
        performed yet
    """
    pass
