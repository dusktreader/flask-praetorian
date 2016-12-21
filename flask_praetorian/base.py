from passlib.context import CryptContext
from textwrap import dedent

from flask_jwt import JWT

from flask_praetorian.exceptions import PraetorianError


class Praetorian:

    def __init__(self, app=None, user_class=None, jwt=None):

        self.pwd_ctx = None
        self.hash_scheme = None
        self.salt = None

        if app is not None and user_class is not None:
            self.init_app(app, user_class, jwt)

    def init_app(self, app, user_class, jwt=None):
        """
        Initializes the Praetorian extension

        :param: app:        The flask app to which this extension is bound
        :param: user_class: The class used to interact with user information
        :param: jwt:        An instance of a jwt extension that should be used
                            if None, a new jwt instance will be used instead
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
            default='bcrypt',
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

        self.user_class = self.validate_user_class(user_class)

        if jwt is None:
            jwt = JWT(
                app,
                authentication_handler=self.authenticate,
                identity_handler=self._identity,
            )
        else:
            jwt.authentication_callback = self.authenticate
            jwt.identity_callback = self._identity
        self.jwt = jwt

        app.errorhandler(PraetorianError)(self.error_handler)

        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['praetorian'] = self

    @classmethod
    def validate_user_class(cls, user_class):
        """
        Validates the supplied user_class to make sure that it has the
        class methods necessary to function correctly.

        Requirements:
        - ``lookup`` method. Accepts username parameter, returns instance
        - ``identify`` method. Accepts user id parameter, returns instance
        """
        PraetorianError.require_condition(
            getattr(user_class, 'lookup', None) is not None,
            dedent("""
                The user_class must have a lookup class method:
                user_class.lookup(<str:username>) -> <user instance>
            """),
        )
        PraetorianError.require_condition(
            getattr(user_class, 'identify', None) is not None,
            dedent("""
                The user_class must have an identify class method:
                user_class.identify(<int:id>) -> <user instance>
            """),
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
        if user is None or not self.verify_password(password, user.password):
            return None
        return user

    def _identity(self, payload):
        """
        A helper method for JWT identity handlers. Extracts a user identity
        from a json payload and returns the associated user instance
        """
        PraetorianError.require_condition(
            self.user_class is not None,
            "Praetorian must be initialized before this method is available",
        )
        user_id = payload['identity']
        return self.user_class.identify(user_id)

    def verify_password(self, raw_password, hashed_password):
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
        Provides a flask error handler
        """
        return error.jsonify(), error.status_code, error.headers
