import datetime
import flask
import jinja2
import jwt
import pendulum
import re
import textwrap
import uuid
import warnings

from flask_mailman import EmailMessage

from passlib.context import CryptContext

from flask_praetorian.utilities import deprecated, duration_from_string

from flask_praetorian.exceptions import (
    AuthenticationError,
    BlacklistedError,
    ClaimCollisionError,
    EarlyRefreshError,
    ExpiredAccessError,
    ExpiredRefreshError,
    InvalidRegistrationToken,
    InvalidResetToken,
    InvalidTokenHeader,
    InvalidUserError,
    LegacyScheme,
    MissingClaimError,
    MissingToken,
    MissingUserError,
    MisusedRegistrationToken,
    MisusedResetToken,
    ConfigurationError,
    PraetorianError,
)

from flask_praetorian.constants import (
    DEFAULT_JWT_ACCESS_LIFESPAN,
    DEFAULT_JWT_ALGORITHM,
    DEFAULT_JWT_ALLOWED_ALGORITHMS,
    DEFAULT_JWT_PLACES,
    DEFAULT_JWT_COOKIE_NAME,
    DEFAULT_JWT_HEADER_NAME,
    DEFAULT_JWT_HEADER_TYPE,
    DEFAULT_JWT_REFRESH_LIFESPAN,
    DEFAULT_USER_CLASS_VALIDATION_METHOD,
    DEFAULT_CONFIRMATION_TEMPLATE,
    DEFAULT_CONFIRMATION_SUBJECT,
    DEFAULT_RESET_TEMPLATE,
    DEFAULT_RESET_SUBJECT,
    DEFAULT_HASH_SCHEME,
    DEFAULT_HASH_ALLOWED_SCHEMES,
    DEFAULT_HASH_AUTOUPDATE,
    DEFAULT_HASH_AUTOTEST,
    DEFAULT_HASH_DEPRECATED_SCHEMES,
    DEFAULT_ROLES_DISABLED,
    IS_REGISTRATION_TOKEN_CLAIM,
    IS_RESET_TOKEN_CLAIM,
    REFRESH_EXPIRATION_CLAIM,
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

    def __init__(
        self,
        app=None,
        user_class=None,
        is_blacklisted=None,
        encode_jwt_token_hook=None,
        refresh_jwt_token_hook=None,
    ):
        self.pwd_ctx = None
        self.hash_scheme = None
        self.salt = None

        if app is not None and user_class is not None:
            self.init_app(
                app,
                user_class,
                is_blacklisted,
                encode_jwt_token_hook,
                refresh_jwt_token_hook,
            )

    def init_app(
        self,
        app=None,
        user_class=None,
        is_blacklisted=None,
        encode_jwt_token_hook=None,
        refresh_jwt_token_hook=None,
    ):
        """
        Initializes the Praetorian extension

        :param: app:                    The flask app to bind this
                                        extension to
        :param: user_class:             The class used to interact with
                                        user data
        :param: is_blacklisted:         A method that may optionally be
                                        used to check the token against
                                        a blacklist when access or refresh
                                        is requested should take the jti
                                        for the token to check as a single
                                        argument. Returns True if the jti is
                                        blacklisted, False otherwise. By
                                        default, always returns False.
        :param encode_jwt_token_hook:   A method that may optionally be
                                        called right before an encoded jwt
                                        is generated. Should take
                                        payload_parts which contains the
                                        ingredients for the jwt.
        :param refresh_jwt_token_hook:  A method that may optionally be called
                                        right before an encoded jwt is
                                        refreshed. Should take payload_parts
                                        which contains the ingredients for
                                        the jwt.
        """
        PraetorianError.require_condition(
            app.config.get("SECRET_KEY") is not None,
            "There must be a SECRET_KEY app config setting set",
        )

        self.roles_disabled = app.config.get(
            "PRAETORIAN_ROLES_DISABLED",
            DEFAULT_ROLES_DISABLED,
        )

        self.hash_autoupdate = app.config.get(
            "PRAETORIAN_HASH_AUTOUPDATE",
            DEFAULT_HASH_AUTOUPDATE,
        )

        self.hash_autotest = app.config.get(
            "PRAETORIAN_HASH_AUTOTEST",
            DEFAULT_HASH_AUTOTEST,
        )

        self.pwd_ctx = CryptContext(
            schemes=app.config.get(
                "PRAETORIAN_HASH_ALLOWED_SCHEMES",
                DEFAULT_HASH_ALLOWED_SCHEMES,
            ),
            default=app.config.get(
                "PRAETORIAN_HASH_SCHEME",
                DEFAULT_HASH_SCHEME,
            ),
            deprecated=app.config.get(
                "PRAETORIAN_HASH_DEPRECATED_SCHEMES",
                DEFAULT_HASH_DEPRECATED_SCHEMES,
            ),
        )

        valid_schemes = self.pwd_ctx.schemes()
        PraetorianError.require_condition(
            self.hash_scheme in valid_schemes or self.hash_scheme is None,
            "If {} is set, it must be one of the following schemes: {}".format(
                "PRAETORIAN_HASH_SCHEME",
                valid_schemes,
            ),
        )

        self.user_class = self._validate_user_class(app, user_class)
        self.is_blacklisted = is_blacklisted or (lambda t: False)
        self.encode_jwt_token_hook = encode_jwt_token_hook
        self.refresh_jwt_token_hook = refresh_jwt_token_hook

        self.encode_key = app.config["SECRET_KEY"]
        self.allowed_algorithms = app.config.get(
            "JWT_ALLOWED_ALGORITHMS",
            DEFAULT_JWT_ALLOWED_ALGORITHMS,
        )
        self.encode_algorithm = app.config.get(
            "JWT_ALGORITHM",
            DEFAULT_JWT_ALGORITHM,
        )
        self.access_lifespan = app.config.get(
            "JWT_ACCESS_LIFESPAN",
            DEFAULT_JWT_ACCESS_LIFESPAN,
        )
        self.refresh_lifespan = app.config.get(
            "JWT_REFRESH_LIFESPAN",
            DEFAULT_JWT_REFRESH_LIFESPAN,
        )
        self.jwt_places = app.config.get(
            "JWT_PLACES",
            DEFAULT_JWT_PLACES,
        )
        self.cookie_name = app.config.get(
            "JWT_COOKIE_NAME",
            DEFAULT_JWT_COOKIE_NAME,
        )
        self.header_name = app.config.get(
            "JWT_HEADER_NAME",
            DEFAULT_JWT_HEADER_NAME,
        )
        self.header_type = app.config.get(
            "JWT_HEADER_TYPE",
            DEFAULT_JWT_HEADER_TYPE,
        )
        self.user_class_validation_method = app.config.get(
            "USER_CLASS_VALIDATION_METHOD",
            DEFAULT_USER_CLASS_VALIDATION_METHOD,
        )

        self.confirmation_template = app.config.get(
            "PRAETORIAN_CONFIRMATION_TEMPLATE",
            DEFAULT_CONFIRMATION_TEMPLATE,
        )
        self.confirmation_uri = app.config.get(
            "PRAETORIAN_CONFIRMATION_URI",
        )
        self.confirmation_sender = app.config.get(
            "PRAETORIAN_CONFIRMATION_SENDER",
        )
        self.confirmation_subject = app.config.get(
            "PRAETORIAN_CONFIRMATION_SUBJECT",
            DEFAULT_CONFIRMATION_SUBJECT,
        )
        self.confirmation_lifespan = app.config.get(
            'PRAETORIAN_CONFIRMATION_LIFESPAN',
            DEFAULT_JWT_ACCESS_LIFESPAN,
        )

        self.reset_template = app.config.get(
            "PRAETORIAN_RESET_TEMPLATE",
            DEFAULT_RESET_TEMPLATE,
        )
        self.reset_uri = app.config.get(
            "PRAETORIAN_RESET_URI",
        )
        self.reset_sender = app.config.get(
            "PRAETORIAN_RESET_SENDER",
        )
        self.reset_subject = app.config.get(
            "PRAETORIAN_RESET_SUBJECT",
            DEFAULT_RESET_SUBJECT,
        )
        self.reset_lifespan = app.config.get(
            'PRAETORIAN_RESET_LIFESPAN',
            DEFAULT_JWT_ACCESS_LIFESPAN,
        )

        if isinstance(self.access_lifespan, dict):
            self.access_lifespan = pendulum.duration(**self.access_lifespan)
        elif isinstance(self.access_lifespan, str):
            self.access_lifespan = duration_from_string(self.access_lifespan)
        ConfigurationError.require_condition(
            isinstance(self.access_lifespan, datetime.timedelta),
            "access lifespan was not configured",
        )

        if isinstance(self.refresh_lifespan, dict):
            self.refresh_lifespan = pendulum.duration(**self.refresh_lifespan)
        if isinstance(self.refresh_lifespan, str):
            self.refresh_lifespan = duration_from_string(self.refresh_lifespan)
        ConfigurationError.require_condition(
            isinstance(self.refresh_lifespan, datetime.timedelta),
            "refresh lifespan was not configured",
        )

        if not app.config.get("DISABLE_PRAETORIAN_ERROR_HANDLER"):
            app.register_error_handler(
                PraetorianError,
                PraetorianError.build_error_handler(),
            )

        self.is_testing = app.config.get("TESTING", False)

        if not hasattr(app, "extensions"):
            app.extensions = {}
        app.extensions["praetorian"] = self

        return app

    def _validate_user_class(self, app, user_class):
        """
        Validates the supplied user_class to make sure that it has the
        class methods and attributes necessary to function correctly.
        After validating class methods, will attempt to instantiate a dummy
        instance of the user class to test for the requisite attributes

        Requirements:

        - ``lookup`` method. Accepts a string parameter, returns instance
        - ``identify`` method. Accepts an identity parameter, returns instance
        - ``identity`` attribute. Provides unique id for the instance
        - ``rolenames`` attribute. Provides list of roles attached to instance
        - ``password`` attribute. Provides hashed password for instance
        """
        PraetorianError.require_condition(
            getattr(user_class, "lookup", None) is not None,
            textwrap.dedent(
                """
                The user_class must have a lookup class method:
                user_class.lookup(<str>) -> <user instance>
                """
            ),
        )
        PraetorianError.require_condition(
            getattr(user_class, "identify", None) is not None,
            textwrap.dedent(
                """
                The user_class must have an identify class method:
                user_class.identify(<identity>) -> <user instance>
                """
            ),
        )

        dummy_user = None
        try:
            dummy_user = user_class()
        except Exception:
            app.logger.debug(
                "Skipping instance validation because "
                "user cannot be instantiated without arguments"
            )
        if dummy_user:
            PraetorianError.require_condition(
                hasattr(dummy_user, "identity"),
                textwrap.dedent(
                    """
                    Instances of user_class must have an identity attribute:
                    user_instance.identity -> <unique id for instance>
                    """
                ),
            )
            PraetorianError.require_condition(
                self.roles_disabled or hasattr(dummy_user, "rolenames"),
                textwrap.dedent(
                    """
                    Instances of user_class must have a rolenames attribute:
                    user_instance.rolenames -> [<role1>, <role2>, ...]
                    """
                ),
            )
            PraetorianError.require_condition(
                hasattr(dummy_user, "password"),
                textwrap.dedent(
                    """
                    Instances of user_class must have a password attribute:
                    user_instance.password -> <hashed password>
                    """
                ),
            )

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
        AuthenticationError.require_condition(
            user is not None
            and self._verify_password(
                password,
                user.password,
            ),
            "The username and/or password are incorrect",
        )

        """
        If we are set to PRAETORIAN_HASH_AUTOUPDATE then check our hash
            and if needed, update the user.  The developer is responsible
            for using the returned user object and updating the data
            storage endpoint.

        Else, if we are set to PRAETORIAN_HASH_AUTOTEST then check out hash
            and return exception if our hash is using the wrong scheme,
            but don't modify the user.
        """
        if self.hash_autoupdate:
            self.verify_and_update(user=user, password=password)
        elif self.hash_autotest:
            self.verify_and_update(user=user)

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

    @deprecated("Use `hash_password` instead.")
    def encrypt_password(self, raw_password):
        """
        *NOTE* This should be deprecated as its an incorrect definition for
            what is actually being done -- we are hashing, not encrypting
        """
        return self.hash_password(raw_password)

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
            "Could not find the requested user",
        )
        user_validate_method = getattr(user, self.user_class_validation_method, None)
        if user_validate_method is None:
            return
        InvalidUserError.require_condition(
            user_validate_method(),
            "The user is not valid or has had access revoked",
        )

    def encode_jwt_token(
        self,
        user,
        override_access_lifespan=None,
        override_refresh_lifespan=None,
        bypass_user_check=False,
        is_registration_token=False,
        is_reset_token=False,
        **custom_claims,
    ):
        """
        Encodes user data into a jwt token that can be used for authorization
        at protected endpoints

        :param: override_access_lifespan:  Override's the instance's access
                                           lifespan to set a custom duration
                                           after which the new token's
                                           accessibility will expire. May not
                                           exceed the refresh_lifespan
        :param: override_refresh_lifespan: Override's the instance's refresh
                                           lifespan to set a custom duration
                                           after which the new token's
                                           refreshability will expire.
        :param: bypass_user_check:         Override checking the user for
                                           being real/active.  Used for
                                           registration token generation.
        :param: is_registration_token:     Indicates that the token will be
                                           used only for email-based
                                           registration
        :param: custom_claims:             Additional claims that should
                                           be packed in the payload. Note that
                                           any claims supplied here must be
                                           JSON compatible types
        """
        ClaimCollisionError.require_condition(
            set(custom_claims.keys()).isdisjoint(RESERVED_CLAIMS),
            "The custom claims collide with required claims",
        )
        if not bypass_user_check:
            self._check_user(user)

        moment = pendulum.now("UTC")

        if override_refresh_lifespan is None:
            refresh_lifespan = self.refresh_lifespan
        elif isinstance(override_refresh_lifespan, dict):
            refresh_lifespan = pendulum.duration(**override_refresh_lifespan)
        else:
            refresh_lifespan = override_refresh_lifespan
        refresh_expiration = (moment + refresh_lifespan).int_timestamp

        if override_access_lifespan is None:
            access_lifespan = self.access_lifespan
        elif isinstance(override_access_lifespan, dict):
            access_lifespan = pendulum.duration(**override_access_lifespan)
        else:
            access_lifespan = override_access_lifespan
        access_expiration = min(
            (moment + access_lifespan).int_timestamp,
            refresh_expiration,
        )

        payload_parts = {
            "iat": moment.int_timestamp,
            "exp": access_expiration,
            "jti": str(uuid.uuid4()),
            "id": user.identity,
            "rls": ",".join(user.rolenames),
            REFRESH_EXPIRATION_CLAIM: refresh_expiration,
        }
        if is_registration_token:
            payload_parts[IS_REGISTRATION_TOKEN_CLAIM] = True
        if is_reset_token:
            payload_parts[IS_RESET_TOKEN_CLAIM] = True
        flask.current_app.logger.debug(
            "Attaching custom claims: {}".format(custom_claims),
        )
        payload_parts.update(custom_claims)

        if self.encode_jwt_token_hook:
            self.encode_jwt_token_hook(**payload_parts)
        return jwt.encode(
            payload_parts,
            self.encode_key,
            self.encode_algorithm,
        )

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
            **custom_claims,
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
                                           accessibility will expire. May not
                                           exceed the refresh lifespan
        """
        moment = pendulum.now("UTC")
        data = self.extract_jwt_token(token, access_type=AccessType.refresh)

        user = self.user_class.identify(data["id"])
        self._check_user(user)

        if override_access_lifespan is None:
            access_lifespan = self.access_lifespan
        elif isinstance(override_access_lifespan, dict):
            access_lifespan = pendulum.duration(**override_access_lifespan)
        else:
            access_lifespan = override_access_lifespan
        refresh_expiration = data[REFRESH_EXPIRATION_CLAIM]
        access_expiration = min(
            (moment + access_lifespan).int_timestamp,
            refresh_expiration,
        )

        custom_claims = {k: v for (k, v) in data.items() if k not in RESERVED_CLAIMS}
        payload_parts = {
            "iat": moment.int_timestamp,
            "exp": access_expiration,
            "jti": data["jti"],
            "id": data["id"],
            "rls": ",".join(user.rolenames),
            REFRESH_EXPIRATION_CLAIM: refresh_expiration,
        }
        payload_parts.update(custom_claims)

        if self.refresh_jwt_token_hook:
            self.refresh_jwt_token_hook(**payload_parts)
        return jwt.encode(
            payload_parts,
            self.encode_key,
            self.encode_algorithm,
        )

    def extract_jwt_token(self, token, access_type=AccessType.access):
        """
        Extracts a data dictionary from a jwt token
        """
        # Note: we disable exp verification because we will do it ourselves
        with InvalidTokenHeader.handle_errors("failed to decode JWT token"):
            data = jwt.decode(
                token,
                self.encode_key,
                algorithms=self.allowed_algorithms,
                options={"verify_exp": False},
            )
        self._validate_jwt_data(data, access_type=access_type)
        return data

    def _validate_jwt_data(self, data, access_type):
        """
        Validates that the data for a jwt token is valid
        """
        MissingClaimError.require_condition(
            "jti" in data,
            "Token is missing jti claim",
        )
        BlacklistedError.require_condition(
            not self.is_blacklisted(data["jti"]),
            "Token has a blacklisted jti",
        )
        MissingClaimError.require_condition(
            "id" in data,
            "Token is missing id field",
        )
        MissingClaimError.require_condition(
            "exp" in data,
            "Token is missing exp claim",
        )
        MissingClaimError.require_condition(
            REFRESH_EXPIRATION_CLAIM in data,
            "Token is missing {} claim".format(REFRESH_EXPIRATION_CLAIM),
        )
        moment = pendulum.now("UTC").int_timestamp
        if access_type == AccessType.access:
            MisusedRegistrationToken.require_condition(
                IS_REGISTRATION_TOKEN_CLAIM not in data,
                "registration token used for access",
            )
            MisusedResetToken.require_condition(
                IS_RESET_TOKEN_CLAIM not in data,
                "password reset token used for access",
            )
            ExpiredAccessError.require_condition(
                moment <= data["exp"],
                "access permission has expired",
            )
        elif access_type == AccessType.refresh:
            MisusedRegistrationToken.require_condition(
                IS_REGISTRATION_TOKEN_CLAIM not in data,
                "registration token used for refresh",
            )
            MisusedResetToken.require_condition(
                IS_RESET_TOKEN_CLAIM not in data,
                "password reset token used for refresh",
            )
            EarlyRefreshError.require_condition(
                moment > data["exp"],
                "access permission for token has not expired. may not refresh",
            )
            ExpiredRefreshError.require_condition(
                moment <= data[REFRESH_EXPIRATION_CLAIM],
                "refresh permission for token has expired",
            )
        elif access_type == AccessType.register:
            ExpiredAccessError.require_condition(
                moment <= data["exp"],
                "register permission has expired",
            )
            InvalidRegistrationToken.require_condition(
                IS_REGISTRATION_TOKEN_CLAIM in data,
                "invalid registration token used for verification",
            )
            MisusedResetToken.require_condition(
                IS_RESET_TOKEN_CLAIM not in data,
                "password reset token used for registration",
            )
        elif access_type == AccessType.reset:
            MisusedRegistrationToken.require_condition(
                IS_REGISTRATION_TOKEN_CLAIM not in data,
                "registration token used for reset",
            )
            ExpiredAccessError.require_condition(
                moment <= data["exp"],
                "reset permission has expired",
            )
            InvalidResetToken.require_condition(
                IS_RESET_TOKEN_CLAIM in data,
                "invalid reset token used for verification",
            )

    def _unpack_header(self, headers):
        """
        Unpacks a jwt token from a request header
        """
        jwt_header = headers.get(self.header_name)
        MissingToken.require_condition(
            jwt_header is not None,
            "JWT token not found in headers under '{}'".format(
                self.header_name,
            ),
        )

        match = re.match(self.header_type + r"\s*([\w\.-]+)", jwt_header)
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

    def _unpack_cookie(self, cookies):
        """
        Unpacks a jwt token from a request cookies
        """
        jwt_cookie = cookies.get(self.cookie_name)
        MissingToken.require_condition(
            jwt_cookie is not None,
            "JWT token not found in cookie under '{}'".format(self.cookie_name),
        )
        return jwt_cookie

    def read_token_from_cookie(self):
        """
        Unpacks a jwt token from the current flask request
        """
        return self._unpack_cookie(flask.request.cookies)

    def read_token(self):
        """
        Tries to unpack the token from the current flask request
        in the locations configured by JWT_PLACES.
        Check-Order is defined by the value order in JWT_PLACES.
        """

        for place in self.jwt_places:
            try:
                return getattr(
                    self,
                    "read_token_from_{place}".format(
                        place=place.lower(),
                    ),
                )()
            except MissingToken:
                pass
            except AttributeError:
                flask.current_app.logger.warning(
                    textwrap.dedent(
                        f"""
                        Flask_Praetorian hasn't implemented reading JWT tokens
                        from location {place.lower()}.
                        Please reconfigure JWT_PLACES.
                        Values accepted in JWT_PLACES are:
                        {DEFAULT_JWT_PLACES}
                        """
                    )
                )

        raise MissingToken(
            textwrap.dedent(
                f"""
                Could not find token in any
                 of the given locations: {self.jwt_places}
                """
            ).replace("\n", "")
        )

    def pack_header_for_user(
        self,
        user,
        override_access_lifespan=None,
        override_refresh_lifespan=None,
        **custom_claims,
    ):
        """
        Encodes a jwt token and packages it into a header dict for a given user

        :param: user:                      The user to package the header for
        :param: override_access_lifespan:  Override's the instance's access
                                           lifespan to set a custom duration
                                           after which the new token's
                                           accessibility will expire. May not
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
            **custom_claims,
        )
        return {self.header_name: self.header_type + " " + token}

    def send_registration_email(self, email, user):
        """
        Sends a registration email to a new user, containing a time expiring token for
        validation.  This requires your application is initialized with a `mail`
        extension, which supports Flask-Mail's `Message()` object and a `send()` method.

        Returns a dict containing the information sent

        :param: email: The email address to attempt to send to
        :param: user:  The user object for which the reset email should be sent
        """
        custom_token = self.encode_jwt_token(
            user,
            override_access_lifespan=self.confirmation_lifespan,
            bypass_user_check=True,
            is_registration_token=True,
        )

        with open(self.confirmation_template) as fh:
            template = fh.read()

        return self.send_token_email(
            email,
            template=template,
            action_sender=self.confirmation_sender,
            action_uri=self.confirmation_uri,
            subject=self.confirmation_subject,
            custom_token=custom_token,
        )

    def send_reset_email(self, email, user):
        """
        Sends a password reset email to a user, containing a time expiring token for
        validation.  This requires your application is initialized with a `mail`
        extension, which supports Flask-Mail's `Message()` object and a `send()` method.

        Returns a dict containing the information sent

        :param: email: The email address to attempt to send to
        :param: user:  The user object for which the reset email should be sent
        """
        custom_token = self.encode_jwt_token(
            user,
            override_access_lifespan=self.reset_lifespan,
            is_reset_token=True,
        )

        with open(self.reset_template) as fh:
            template = fh.read()

        return self.send_token_email(
            email=email,
            template=template,
            action_sender=self.reset_sender,
            action_uri=self.reset_uri,
            subject=self.reset_subject,
            custom_token=custom_token,
        )

    def send_token_email(
        self,
        email,
        template,
        action_sender,
        action_uri,
        subject,
        custom_token,
    ):
        """
        Sends an email containing a time expiring token and a clickable url to
        complete an action with said token. Your flask application must be initialized
        with a `mail` extension, which supports Flask-Mail's `Message()` object and a
        `send()` method.

        Returns a dict containing the information sent

        :param: email:         The email address to which the message should be sent
        :param: template:      HTML Template for confirmation email.
                               If not provided, a stock entry is
                               used
        :param: action_sender: The sender that should be attached
                               to the confirmation email.
        :param: action_uri:    The uri that should be visited to
                               complete the token action.
        :param: subject:       The email subject.
        :param: custom_token:  The token to be carried as the
                               email's payload
        """
        PraetorianError.require_condition(
            custom_token,
            "A custom_token is required to send notification email",
        )
        notification = {
            'result': None,
            'message': None,
            'email': email,
            'token': custom_token,
            'subject': subject,
            'confirmation_uri': action_uri,  # backwards compatibility
            'action_uri': action_uri,
        }

        PraetorianError.require_condition(
            "mailman" in flask.current_app.extensions,
            "Your app must have a mail extension enabled to register by email",
        )

        PraetorianError.require_condition(
            action_sender,
            "A sender is required to send a token bearing email",
        )

        PraetorianError.require_condition(
            template,
            "A template is required to send a token bearing email",
        )

        with PraetorianError.handle_errors('Failed to send token-bearking email'):
            jinja_tmpl = jinja2.Template(template)
            notification["message"] = jinja_tmpl.render(notification).strip()

            msg = EmailMessage(
                notification["subject"],
                notification["message"],
                action_sender,
                [notification["email"]],
            )

            flask.current_app.logger.debug("Sending email to {}".format(email))
            msg.content_subtype = "html"
            msg.send(msg)

        return notification

    def get_user_from_registration_token(self, token):
        """
        Gets a user based on the registration token that is supplied. Verifies
        that the token is a regisration token and that the user can be properly
        retrieved
        """
        data = self.extract_jwt_token(token, access_type=AccessType.register)
        user_id = data.get("id")
        PraetorianError.require_condition(
            user_id is not None,
            "Could not fetch an id from the registration token",
        )
        user = self.user_class.identify(user_id)
        PraetorianError.require_condition(
            user is not None,
            "Could not identify the user from the registration token",
        )
        return user

    def validate_reset_token(self, token):
        """
        Validates a password reset request based on the reset token
        that is supplied. Verifies that the token is a reset token
        and that the user can be properly retrieved
        """
        data = self.extract_jwt_token(token, access_type=AccessType.reset)
        user_id = data.get("id")
        PraetorianError.require_condition(
            user_id is not None,
            "Could not fetch an id from the reset token",
        )
        user = self.user_class.identify(user_id)
        PraetorianError.require_condition(
            user is not None,
            "Could not identify the user from the reset token",
        )
        return user

    def hash_password(self, raw_password):
        """
        Hashes a plaintext password using the stored passlib password context
        """
        PraetorianError.require_condition(
            self.pwd_ctx is not None,
            "Praetorian must be initialized before this method is available",
        )
        """
        `scheme` is now set with self.pwd_ctx.update(default=scheme) due
            to the depreciation in upcoming passlib 2.0.
         zillions of warnings suck.
        """
        return self.pwd_ctx.hash(raw_password)

    def verify_and_update(self, user=None, password=None):
        """
        Validate a password hash contained in the user object is
             hashed with the defined hash scheme (PRAETORIAN_HASH_SCHEME).
        If not, raise an Exception of `LegacySchema`, unless the
             `password` argument is provided, in which case an attempt
             to call `user.save()` will be made, updating the hashed
             password to the currently desired hash scheme
             (PRAETORIAN_HASH_SCHEME).

        :param: user:     The user object to tie claim to
                              (username, id, email, etc). *MUST*
                              include the hashed password field,
                              defined as `user.password`
        :param: password: The user's provide password from login.
                          If present, this is used to validate
                              and then attempt to update with the
                              new PRAETORIAN_HASH_SCHEME scheme.
        """
        if self.pwd_ctx.needs_update(user.password):
            if password:
                (rv, updated) = self.pwd_ctx.verify_and_update(
                    password,
                    user.password,
                )
                AuthenticationError.require_condition(
                    rv,
                    "Could not verify password",
                )
                user.password = updated
            else:
                used_hash = self.pwd_ctx.identify(user.password)
                desired_hash = self.hash_scheme
                raise LegacyScheme(
                    "Hash using non-current scheme '{}'." "Use '{}' instead.".format(
                        used_hash, desired_hash
                    )
                )

        return user
