'''
   flask_praetorian init
'''

from flask_praetorian.base import Praetorian  # noqa
from flask_praetorian.exceptions import PraetorianError  # noqa
from flask_praetorian.decorators import (  # noqa
    auth_required,
    auth_accepted,
    roles_required,
    roles_accepted,
)
from flask_praetorian.utilities import (  # noqa
    current_user,
    current_user_id,
    current_rolenames,
    current_custom_claims,
)
