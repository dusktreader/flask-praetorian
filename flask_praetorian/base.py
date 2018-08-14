import flask
import jwt
import pendulum
import re
import textwrap
import uuid
import warnings

from passlib.context import CryptContext

from flask_praetorian.exceptions import (
    AuthenticationError,
    BlacklistedError,
    ClaimCollisionError,
    EarlyRefreshError,
    ExpiredAccessError,
    ExpiredRefreshError,
    InvalidTokenHeader,
    InvalidUserError,
    MissingClaimError,
    MissingTokenHeader,
    MissingUserError,
    PraetorianError,
)

from flask_praetorian.constants import (
    DEFAULT_JWT_ACCESS_LIFESPAN,
    DEFAULT_JWT_ALGORITHM,
    DEFAULT_JWT_ALLOWED_ALGORITHMS,
    DEFAULT_JWT_HEADER_NAME,
    DEFAULT_JWT_HEADER_TYPE,
    DEFAULT_JWT_REFRESH_LIFESPAN,
    DEFAULT_USER_CLASS_VALIDATION_METHOD,
    RESERVED_CLAIMS,
    VITAM_AETERNUM,
    AccessType,
)


class Praetorian:
    """
    Comprises the implementation for the flask-praetorian flask extension.
    Provides a tool that allows password authentication and token provision
    for applications and designated endpoints
    """

    def __init__(self, app=None, user_class=None, is_blacklisted=None):
        self.pwd_ctx = None
        self.hash_scheme = None
        self.salt = None

        if app is not None and user_class is not None:
            self.init_app(app, user_class, is_blacklisted)

    def init_app(self, app, user_class, is_blacklisted=None):
        """
        Initializes the Praetorian extension

        :param: app:            The flask app to bind this extension to
        :param: user_class:     The class used to interact with user data
        :param: is_blacklisted: A method that may optionally be used to
                                check the token against a blacklist when
                                access or refresh is requested
                                Should take the jti for the token to check
                                as a single argument. Returns True if
                                the jti is blacklisted, False otherwise.
                                By default, always returns False.
        """
        PraetorianError.require_condition(
            app.config.get('SECRET_KEY') is not None,
            "There must be a SECRET_KEY app config setting set",
        )

        possible_schemes = [
            'argon2',
            'bcrypt',
            'pbkdf2_sha512',
        ]
        self.pwd_ctx = CryptContext(
            default='pbkdf2_sha512',
            schemes=possible_schemes + ['plaintext'],
            deprecated=[],
        )

        self.hash_scheme = app.config.get('PRAETORIAN_HASH_SCHEME')
        valid_schemes = self.pwd_ctx.schemes()
        PraetorianError.require_condition(
            self.hash_scheme in valid_schemes or self.hash_scheme is None,
            "If {} is set, it must be one of the following schemes: {}",
            'PRAETORIAN_HASH_SCHEME',
            valid_schemes,
        )

        self.user_class = self._validate_user_class(user_class)
        self.is_blacklisted = is_blacklisted or (lambda t: False)

        self.encode_key = app.config['SECRET_KEY']
        self.allowed_algorithms = app.config.get(
            'JWT_ALLOWED_ALGORITHMS',
            DEFAULT_JWT_ALLOWED_ALGORITHMS,
        )
        self.encode_algorithm = app.config.get(
            'JWT_ALGORITHM',
            DEFAULT_JWT_ALGORITHM,
        )
        self.access_lifespan = pendulum.Duration(**app.config.get(
            'JWT_ACCESS_LIFESPAN',
            DEFAULT_JWT_ACCESS_LIFESPAN,
        ))
        self.refresh_lifespan = pendulum.Duration(**app.config.get(
            'JWT_REFRESH_LIFESPAN',
            DEFAULT_JWT_REFRESH_LIFESPAN,
        ))
        self.header_name = app.config.get(
            'JWT_HEADER_NAME',
            DEFAULT_JWT_HEADER_NAME,
        )
        self.header_type = app.config.get(
            'JWT_HEADER_TYPE',
            DEFAULT_JWT_HEADER_TYPE,
        )
        self.user_class_validation_method = app.config.get(
            'USER_CLASS_VALIDATION_METHOD',
            DEFAULT_USER_CLASS_VALIDATION_METHOD,
        )

        if not app.config.get('DISABLE_PRAETORIAN_ERROR_HANDLER'):
            app.register_error_handler(
                PraetorianError,
                PraetorianError.build_error_handler(),
            )

        self.is_testing = app.config.get('TESTING', False)

        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['praetorian'] = self

    @classmethod
    def _validate_user_class(cls, user_class):
        """
        Validates the supplied user_class to make sure that it has the
        class methods necessary to function correctly.

        Requirements:

        - ``lookup`` method. Accepts a string parameter, returns instance
        - ``identify`` method. Accepts an identity parameter, returns instance
        """
        PraetorianError.require_condition(
            getattr(user_class, 'lookup', None) is not None,
            textwrap.dedent("""
                The user_class must have a lookup class method:
                user_class.lookup(<str>) -> <user instance>
            """),
        )
        PraetorianError.require_condition(
            getattr(user_class, 'identify', None) is not None,
            textwrap.dedent("""
                The user_class must have an identify class method:
                user_class.identify(<identity>) -> <user instance>
            """),
        )
        # TODO: Figure out how to check for an identity property
        return user_class

    def authenticate(self, username, password):
        """
        Verifies that a password matches the stored password for that username.
        If verification passes, the matching user instance is returned
        """
        PraetorianError.require_condition(
            self.user_class is not None,
            "Praetorian must be initialized before this method is available",
        )
        user = self.user_class.lookup(username)
        MissingUserError.require_condition(
            user is not None,
            'Could not find the requested user',
        )
        AuthenticationError.require_condition(
            self._verify_password(password, user.password),
            'The password is incorrect',
        )
        return user

    def _verify_password(self, raw_password, hashed_password):
        """
        Verifies that a plaintext password matches the hashed version of that
        password using the stored passlib password context
        """
        PraetorianError.require_condition(
            self.pwd_ctx is not None,
            "Praetorian must be initialized before this method is available",
        )
        return self.pwd_ctx.verify(raw_password, hashed_password)

    def encrypt_password(self, raw_password):
        """
        Encrypts a plaintext password using the stored passlib password context
        """
        PraetorianError.require_condition(
            self.pwd_ctx is not None,
            "Praetorian must be initialized before this method is available",
        )
        return self.pwd_ctx.encrypt(raw_password, scheme=self.hash_scheme)

    def error_handler(self, error):
        """
        Provides a flask error handler that is used for PraetorianErrors
        (and derived exceptions).
        """
        warnings.warn(
            """
            error_handler is deprecated.
            Use FlaskBuzz.build_error_handler instead
            """,
            warnings.DeprecationWarning,
        )
        return error.jsonify(), error.status_code, error.headers

    def _check_user(self, user):
        """
        Checks to make sure that a user is valid. First, checks that the user
        is not None. If this check fails, a MissingUserError is raised. Next,
        checks if the user has a validation method. If the method does not
        exist, the check passes. If the method exists, it is called. If the
        result of the call is not truthy, an InvalidUserError is raised
        """
        MissingUserError.require_condition(
            user is not None,
            'Could not find the requested user',
        )
        user_validate_method = getattr(
            user, self.user_class_validation_method, None
        )
        if user_validate_method is None:
            return
        InvalidUserError.require_condition(
            user_validate_method(),
            "The user is not valid or has had access revoked",
        )

    def encode_jwt_token(
            self, user,
            override_access_lifespan=None, override_refresh_lifespan=None,
            **custom_claims
    ):
        """
        Encodes user data into a jwt token that can be used for authorization
        at protected endpoints

        :param: override_access_lifespan:  Override's the instance's access
                                           lifespan to set a custom duration
                                           after which the new token's
                                           accessability will expire. May not
                                           exceed the refresh_lifespan
        :param: override_refresh_lifespan: Override's the instance's refresh
                                           lifespan to set a custom duration
                                           after which the new token's
                                           refreshability will expire.
        :param: custom_claims:             Additional claims that should
                                           be packed in the payload. Note that
                                           any claims supplied here must be
                                           JSON compatible types
        """
        ClaimCollisionError.require_condition(
            set(custom_claims.keys()).isdisjoint(RESERVED_CLAIMS),
            "The custom claims collide with required claims",
        )
        self._check_user(user)

        moment = pendulum.now('UTC')

        if override_refresh_lifespan is None:
            refresh_lifespan = self.refresh_lifespan
        else:
            refresh_lifespan = override_refresh_lifespan
        refresh_expiration = (moment + refresh_lifespan).int_timestamp

        if override_access_lifespan is None:
            access_lifespan = self.access_lifespan
        else:
            access_lifespan = override_access_lifespan
        access_expiration = min(
            (moment + access_lifespan).int_timestamp,
            refresh_expiration,
        )

        payload_parts = dict(
            iat=moment.int_timestamp,
            exp=access_expiration,
            rf_exp=refresh_expiration,
            jti=str(uuid.uuid4()),
            id=user.identity,
            rls=','.join(user.rolenames),
            **custom_claims
        )
        return jwt.encode(
            payload_parts, self.encode_key, self.encode_algorithm,
        ).decode('utf-8')

    def encode_eternal_jwt_token(self, user, **custom_claims):
        """
        This utility function encodes a jwt token that never expires

        .. note:: This should be used sparingly since the token could become
                  a security concern if it is ever lost. If you use this
                  method, you should be sure that your application also
                  implements a blacklist so that a given token can be blocked
                  should it be lost or become a security concern
        """
        return self.encode_jwt_token(
            user,
            override_access_lifespan=VITAM_AETERNUM,
            override_refresh_lifespan=VITAM_AETERNUM,
            **custom_claims
        )

    def refresh_jwt_token(self, token, override_access_lifespan=None):
        """
        Creates a new token for a user if and only if the old token's access
        permission is expired but its refresh permission is not yet expired.
        The new token's refresh expiration moment is the same as the old
        token's, but the new token's access expiration is refreshed

        :param: token:                     The existing jwt token that needs to
                                           be replaced with a new, refreshed
                                           token
        :param: override_access_lifespan:  Override's the instance's access
                                           lifespan to set a custom duration
                                           after which the new token's
                                           accessability will expire. May not
                                           exceed the refresh lifespan
        """
        moment = pendulum.now('UTC')
        # Note: we disable exp verification because we do custom checks here
        with InvalidTokenHeader.handle_errors('failed to decode JWT token'):
            data = jwt.decode(
                token,
                self.encode_key,
                algorithms=self.allowed_algorithms,
                options={'verify_exp': False},
            )

        self._validate_jwt_data(data, access_type=AccessType.refresh)

        user = self.user_class.identify(data['id'])
        self._check_user(user)

        if override_access_lifespan is None:
            access_lifespan = self.access_lifespan
        else:
            access_lifespan = override_access_lifespan
        refresh_expiration = data['rf_exp']
        access_expiration = min(
            (moment + access_lifespan).int_timestamp,
            refresh_expiration,
        )

        custom_claims = {
            k: v for (k, v) in data.items() if k not in RESERVED_CLAIMS
        }
        payload_parts = dict(
            iat=moment.int_timestamp,
            exp=access_expiration,
            rf_exp=refresh_expiration,
            jti=data['jti'],
            id=data['id'],
            rls=','.join(user.rolenames),
            **custom_claims
        )
        return jwt.encode(
            payload_parts, self.encode_key, self.encode_algorithm,
        ).decode('utf-8')

    def extract_jwt_token(self, token):
        """
        Extracts a data dictionary from a jwt token
        """
        # Note: we disable exp verification because we will do it ourselves
        with InvalidTokenHeader.handle_errors('failed to decode JWT token'):
            data = jwt.decode(
                token,
                self.encode_key,
                algorithms=self.allowed_algorithms,
                options={'verify_exp': False},
            )
        self._validate_jwt_data(data, access_type=AccessType.access)
        return data

    def _validate_jwt_data(self, data, access_type):
        """
        Validates that the data for a jwt token is valid
        """
        MissingClaimError.require_condition(
            'jti' in data,
            'Token is missing jti claim',
        )
        BlacklistedError.require_condition(
            not self.is_blacklisted(data['jti']),
            'Token has a blacklisted jti',
        )
        MissingClaimError.require_condition(
            'id' in data,
            'Token is missing id field',
        )
        MissingClaimError.require_condition(
            'exp' in data,
            'Token is missing exp claim',
        )
        MissingClaimError.require_condition(
            'rf_exp' in data,
            'Token is missing rf_exp claim',
        )
        moment = pendulum.now('UTC').int_timestamp
        if access_type == AccessType.access:
            ExpiredAccessError.require_condition(
                moment <= data['exp'],
                'access permission has expired',
            )
        elif access_type == AccessType.refresh:
            EarlyRefreshError.require_condition(
                moment > data['exp'],
                'access permission for token has not expired. may not refresh',
            )
            ExpiredRefreshError.require_condition(
                moment <= data['rf_exp'],
                'refresh permission for token has expired',
            )

    def _unpack_header(self, headers):
        """
        Unpacks a jwt token from a request header
        """
        jwt_header = headers.get(self.header_name)
        MissingTokenHeader.require_condition(
            jwt_header is not None,
            "JWT token not found in headers under '{}'",
            self.header_name,
        )

        match = re.match(self.header_type + r'\s*([\w\.-]+)', jwt_header)
        InvalidTokenHeader.require_condition(
            match is not None,
            "JWT header structure is invalid",
        )
        token = match.group(1)
        return token

    def read_token_from_header(self):
        """
        Unpacks a jwt token from the current flask request
        """
        return self._unpack_header(flask.request.headers)

    def pack_header_for_user(
            self, user,
            override_access_lifespan=None, override_refresh_lifespan=None,
            **custom_claims
    ):
        """
        Encodes a jwt token and packages it into a header dict for a given user

        :param: user:                      The user to package the header for
        :param: override_access_lifespan:  Override's the instance's access
                                           lifespan to set a custom duration
                                           after which the new token's
                                           accessability will expire. May not
                                           exceed the refresh_lifespan
        :param: override_refresh_lifespan: Override's the instance's refresh
                                           lifespan to set a custom duration
                                           after which the new token's
                                           refreshability will expire.
        :param: custom_claims:             Additional claims that should
                                           be packed in the payload. Note that
                                           any claims supplied here must be
                                           JSON compatible types
        """
        token = self.encode_jwt_token(
            user,
            override_access_lifespan=override_access_lifespan,
            override_refresh_lifespan=override_refresh_lifespan,
            **custom_claims
        )
        return {self.header_name: self.header_type + ' ' + token}
