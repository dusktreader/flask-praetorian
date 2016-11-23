from passlib.context import CryptContext

from flask_jwt import JWT

from flask_praetorian.exceptions import PraetorianError


class Praetorian:

    def __init__(self, app=None, user_class=None):

        self.pwd_ctx = None
        self.hash_scheme = None
        self.salt = None

        if app is not None and user_class is not None:
            self.init_app(app, user_class)

    def init_app(self, app, user_class):
        PraetorianError.require_condition(
            app.config.get('SECRET_KEY') is not None,
            "There must be a SECRET_KEY app config setting set",
        )

        possible_schemes = [
            # 'argon2',
            'bcrypt',
            'pbkdf2_sha512',
        ]
        self.pwd_ctx = CryptContext(
            default='bcrypt',
            schemes=possible_schemes + ['plaintext'],
            deprecated=[],
        )

        self.hash_scheme = app.config.get('PRAETORIAN_HASH_SCHEME')

        self.user_class = user_class
        self.jwt = JWT(
            app,
            authentication_handler=self._authenticate,
            identity_handler=self._identity,
        )

        app.errorhandler(PraetorianError)(self.error_handler)

        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['jwt_roles'] = self

    def _authenticate(self, username, password):
        user = self.user_class.query.filter_by(username=username).one_or_none()
        if user is None or not self.verify_password(password, user.password):
            return None
        return user

    def _identity(self, payload):
        user_id = payload['identity']
        return self.user_class.query.get(user_id)

    def verify_password(self, raw_password, hashed_password):
        return self.pwd_ctx.verify(raw_password, hashed_password)

    def encrypt_password(self, raw_password):
        return self.pwd_ctx.encrypt(raw_password, scheme=self.hash_scheme)

    def error_handler(self, error):
        return error.jsonify(), error.status_code, error.headers
