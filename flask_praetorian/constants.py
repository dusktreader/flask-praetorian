import pendulum
import enum
from os.path import dirname, abspath


DEFAULT_JWT_PLACES = ["header", "cookie"]
DEFAULT_JWT_COOKIE_NAME = "access_token"
DEFAULT_JWT_HEADER_NAME = "Authorization"
DEFAULT_JWT_HEADER_TYPE = "Bearer"
DEFAULT_JWT_ACCESS_LIFESPAN = pendulum.duration(minutes=15)
DEFAULT_JWT_REFRESH_LIFESPAN = pendulum.duration(days=30)
DEFAULT_JWT_ALGORITHM = "HS256"
DEFAULT_JWT_ALLOWED_ALGORITHMS = ["HS256"]

DEFAULT_ROLES_DISABLED = False

DEFAULT_USER_CLASS_VALIDATION_METHOD = "is_valid"

DEFAULT_CONFIRMATION_TEMPLATE = (
    "{}/flask_praetorian/templates/registration_email.html".format(
        dirname(dirname(abspath(__file__))),
    )
)

DEFAULT_CONFIRMATION_SENDER = "you@whatever.com"
DEFAULT_CONFIRMATION_SUBJECT = "Please confirm your registration"

DEFAULT_RESET_TEMPLATE = "{}/flask_praetorian/templates/{}".format(
    dirname(dirname(abspath(__file__))),
    "reset_email.html",
)

DEFAULT_RESET_SENDER = "you@whatever.com"
DEFAULT_RESET_SUBJECT = "Password Reset Requested"

DEFAULT_HASH_AUTOUPDATE = False
DEFAULT_HASH_AUTOTEST = False
DEFAULT_HASH_SCHEME = "pbkdf2_sha512"
DEFAULT_HASH_ALLOWED_SCHEMES = [
    "pbkdf2_sha512",
    "sha256_crypt",
    "sha512_crypt",
    "bcrypt",
    "argon2",
    "bcrypt_sha256",
]
DEFAULT_HASH_DEPRECATED_SCHEMES = []

REFRESH_EXPIRATION_CLAIM = "rf_exp"
IS_REGISTRATION_TOKEN_CLAIM = "is_ert"
IS_RESET_TOKEN_CLAIM = "is_prt"
RESERVED_CLAIMS = {
    "iat",
    "exp",
    "jti",
    "id",
    "rls",
    REFRESH_EXPIRATION_CLAIM,
    IS_REGISTRATION_TOKEN_CLAIM,
    IS_RESET_TOKEN_CLAIM,
}

# 1M days seems reasonable. If this code is being used in 3000 years...welp
VITAM_AETERNUM = pendulum.Duration(days=1000000)


class AccessType(enum.Enum):
    access = "ACCESS"
    refresh = "REFRESH"
    register = "REGISTER"
    reset = "RESET"
