"""
flask-praetorian is a security extension for flask. It is modelled heavily on
flask-security (https://github.com/mattupstate/flask-security), but is targeted
at providing authentication for api-only applications that use token based
authentication. It builds on flask-jwt and provides some additional
functionality such as password encryption upon storage and decorators that
check the current users roles
"""

from flask_praetorian.base import Praetorian  # noqa
from flask_praetorian.exceptions import PraetorianError  # noqa
from flask_praetorian.decorators import (  # noqa
    auth_required,
    roles_required,
    roles_accepted,
)
