import functools

from flask_jwt import current_identity
from flask_praetorian import PraetorianError


def _current_rolenames():
    user = current_identity
    rolenames = user.rolenames
    return set(rolenames)


def roles_required(*required_rolenames):
    def decorator(method):
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            PraetorianError.require_condition(
                _current_rolenames().issubset(set(required_rolenames)),
                "This method requires all the following role names: {}",
                [', '.join(required_rolenames)],
            )
            return method(*args, **kwargs)
        return wrapper
    return decorator


def roles_accepted(*accepted_rolenames):
    def decorator(method):
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            PraetorianError.require_condition(
                _current_rolenames().intersection(set(accepted_rolenames)),
                "This method requires one of the following role names: {}",
                [', '.join(accepted_rolenames)],
            )
            return method(*args, **kwargs)
        return wrapper
    return decorator
