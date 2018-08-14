import pendulum
import enum


DEFAULT_JWT_HEADER_NAME = 'Authorization'
DEFAULT_JWT_HEADER_TYPE = 'Bearer'
DEFAULT_JWT_ACCESS_LIFESPAN = dict(minutes=15)
DEFAULT_JWT_REFRESH_LIFESPAN = dict(days=30)
DEFAULT_JWT_ALGORITHM = 'HS256'
DEFAULT_JWT_ALLOWED_ALGORITHMS = ['HS256']
DEFAULT_USER_CLASS_VALIDATION_METHOD = 'is_valid'

RESERVED_CLAIMS = {'iat', 'exp', 'rf_exp', 'jti', 'id', 'rls'}

# 1M days seems reasonable. If this code is being used in 3000 years...welp
VITAM_AETERNUM = pendulum.Duration(days=1000000)


class AccessType(enum.Enum):

    access = 'ACCESS'
    refresh = 'REFRESH'
