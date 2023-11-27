import flask_buzz


class PraetorianError(flask_buzz.FlaskBuzz):
    """
    Provides a custom exception class for flask-praetorian based on flask-buzz.
    `flask-buzz on gitub <https://github.com/dusktreader/flask-buzz>`_
    """

    status_code = 401


class MissingClaimError(PraetorianError):
    """
    The jwt token is missing a required claim
    """

    pass


class BlacklistedError(PraetorianError):
    """
    The jwt token has been blacklisted and may not be used any more
    """

    status_code = 403


class ExpiredAccessError(PraetorianError):
    """
    The jwt token has expired for access and must be refreshed
    """

    pass


class EarlyRefreshError(PraetorianError):
    """
    The jwt token has not yet expired for access and may not be refreshed
    """

    status_code = 425  # HTTP Status Code : 425 Too Early


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

    status_code = 403


class MissingRoleError(PraetorianError):
    """
    The token is missing a required role
    """

    status_code = 403


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
    """ "
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
