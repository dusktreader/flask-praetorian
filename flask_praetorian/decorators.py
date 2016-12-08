import functools
import flask_jwt

from flask_praetorian.exceptions import PraetorianError


def _current_rolenames():
    user = flask_jwt.current_identity
    PraetorianError.require_condition(
        user._get_current_object() is not None,
        """
        Cannot check roles without identity set. Add jwt token a la flask_jwt
        and make sure the ``@flask_jwt.jwt_required`` or
        ``@flask_praetorian.auth_required`` decorator is applied to functions
        using flask_praetorian role checks and is declared *before*
        flask_praetorian decorators
        """,
    )
    rolenames = user.rolenames
    if len(rolenames) == 0:
        return set(['non-empty-but-definitely-not-matching-subset'])
    else:
        return set(rolenames)


def auth_required(*args, **kwargs):
    return flask_jwt.jwt_required(*args, **kwargs)


def roles_required(*required_rolenames):
    def decorator(method):
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            PraetorianError.require_condition(
                _current_rolenames().issuperset(set(required_rolenames)),
                "This endpoint requires all the following roles: {}",
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
                _current_rolenames().issubset(set(accepted_rolenames)),
                "This endpoint requires one of the following roles: {}",
                [', '.join(accepted_rolenames)],
            )
            return method(*args, **kwargs)
        return wrapper
    return decorator
