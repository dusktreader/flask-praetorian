import base64
import hashlib
import hmac
import passlib.context

from flask_jwt import JWT

from flask_praetorian.exceptions import PraetorianError

# TODO: Figure out how to register the /auth endpoint with swagger


class Praetorian:

    def __init__(self, app=None, user_class=None):

        self.pwd_ctx = None
        self.hash_scheme = None
        self.salt = None

        if app is not None and user_class is not None:
            self.init_app(app, user_class)

    def init_app(self, app, user_class):
        # TODO: add error handler stuff

        # TODO: make sure to add test for a few non plaintext hash methods
        self.pwd_ctx = passlib.context.CryptContext(
            default=app.config.get('SECURITY_PASSWORD_HASH', 'plaintext'),
            schemes=[
                'bcrypt',
                'des_crypt',
                'pbkdf2_sha256',
                'pbkdf2_sha512',
                'sha256_crypt',
                'sha512_crypt',
                # plaintext needs to be last
                # TODO: Figure out a more elegant way to do this
                'plaintext'
            ],
            deprecated=['auto'],
        )

        self.hash_scheme = app.config.get('SECURITY_PASSWORD_HASH')
        if self.hash_scheme == 'plaintext':
            self.hash_scheme = None

        self.salt = app.config.get('SECURITY_PASSWORD_SALT')
        PraetorianError.require_condition(
            self.salt is not None,
            'SECURITY_PASSWORD_SALT must be set in the app configuration',
        )

        self.user_class = user_class
        self.jwt = JWT(app, self._authenticate, self._identity)

        # TODO: figure out extension nameing convention
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['jwt_roles'] = self

    def _authenticate(self, username, password):
        user = self.user_class.query.filter_by(username=username).one()
        if not self.verify_password(password, user.password):
            return None
        return user

    def _identity(self, payload):
        user_id = payload['identity']
        return self.user_class.get(user_id)

    def get_hmac(self, password):
        """
        Returns a Base64 encoded HMAC+SHA512 of the password signed with the
        salt specified by ``SECURITY_PASSWORD_SALT``.
        """
        if self.hash_scheme is None:
            return password

        h = hmac.new(
            self.salt.encode('utf-8'),
            password.encode('utf-8'),
            hashlib.sha512,
        )
        return base64.b64encode(h.digest())

    def verify_password(self, raw_password, hashed_password):
        return self.pwd_ctx.verify(
            self.get_hmac(raw_password),
            hashed_password,
        )

    def encrypt_password(self, raw_password):
        if self.hash_scheme is None:
            return raw_password

        # TODO: do we really need to decode to f'in ascii here?
        return self.pwd_ctx.encrypt(
            self.get_hmac(raw_password).decode('ascii')
        )
