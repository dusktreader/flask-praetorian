import pendulum
import enum


DEFAULT_JWT_HEADER_NAME = 'Authorization'
DEFAULT_JWT_HEADER_TYPE = 'Bearer'
DEFAULT_JWT_ACCESS_LIFESPAN = pendulum.Interval(minutes=15)
DEFAULT_JWT_REFRESH_LIFESPAN = pendulum.Interval(days=30)
DEFAULT_JWT_ALGORITHM = 'HS256'
DEFAULT_JWT_ALLOWED_ALGORITHMS = ['HS256']

VITAM_AETERNUM = pendulum.Interval.max


class AccessType(enum.Enum):

    access = 'ACCESS'
    refresh = 'REFRESH'
