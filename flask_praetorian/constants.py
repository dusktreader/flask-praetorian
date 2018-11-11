import pendulum
import enum
from os.path import dirname, abspath


DEFAULT_JWT_HEADER_NAME = 'Authorization'
DEFAULT_JWT_HEADER_TYPE = 'Bearer'
DEFAULT_JWT_ACCESS_LIFESPAN = dict(minutes=15)
DEFAULT_JWT_REFRESH_LIFESPAN = dict(days=30)
DEFAULT_JWT_ALGORITHM = 'HS256'
DEFAULT_JWT_ALLOWED_ALGORITHMS = ['HS256']
DEFAULT_USER_CLASS_VALIDATION_METHOD = 'is_valid'
DEFAULT_EMAIL_TEMPLATE = dirname(dirname(abspath(__file__))) + \
    "/flask_praetorian/templates/registration_email.html"

DEFAULT_CONFIRMATION_ENDPOINT = 'registration_confirmation'
DEFAULT_CONFIRMATION_SENDER = 'you@whatever.com'
DEFAULT_CONFIRMATION_SUBJECT = 'You still need to confirm your registration'
DEFAULT_HASH_AUTOUPDATE = False
DEFAULT_HASH_AUTOTEST = False
DEFAULT_HASH_SCHEME = 'pbkdf2_sha512'
DEFAULT_HASH_ALLOWED_SCHEMES = [
    'pbkdf2_sha512', 'sha256_crypt', 'sha512_crypt', 'bcrypt', 'argon2',
    'bcrypt_sha256',
]
DEFAULT_HASH_DEPRECATED_SCHEMES = []

RESERVED_CLAIMS = {'iat', 'exp', 'rf_exp', 'jti', 'id', 'rls'}

# 1M days seems reasonable. If this code is being used in 3000 years...welp
VITAM_AETERNUM = pendulum.Duration(days=1000000)


class AccessType(enum.Enum):

    access = 'ACCESS'
    refresh = 'REFRESH'
