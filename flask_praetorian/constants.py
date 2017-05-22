import datetime
import enum


DEFAULT_JWT_HEADER_NAME = 'Authorization'
DEFAULT_JWT_HEADER_TYPE = 'Bearer'
DEFAULT_JWT_ACCESS_LIFESPAN = datetime.timedelta(minutes=15)
DEFAULT_JWT_REFRESH_LIFESPAN = datetime.timedelta(days=30)
DEFAULT_JWT_ALGORITHM = 'HS256'
DEFAULT_JWT_ALLOWED_ALGORITHMS = ['HS256']


class AccessType(enum.Enum):

    access = 'ACCESS'
    refresh = 'REFRESH'
