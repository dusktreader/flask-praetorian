import functools

from flask_praetorian.exceptions import MissingRoleError

from flask_praetorian.utilities import (
    current_guard,
    add_jwt_data_to_app_context,
    remove_jwt_data_from_app_context,
    current_rolenames,
)


def auth_required(method):
    """
    This decorator is used to ensure that a user is authenticated before
    being able to access a flask route. It also adds the current user to the
    current flask context. This decorator should come first when using with
    other flask_praetorian decorators.
    """
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        guard = current_guard()
        token = guard.read_token_from_header()
        jwt_data = guard.extract_jwt_token(token)
        add_jwt_data_to_app_context(jwt_data)
        retval = method(*args, **kwargs)
        remove_jwt_data_from_app_context()
        return retval
    return wrapper


def roles_required(*required_rolenames):
    """
    This decorator ensures that any uses accessing the decorated route have all
    the needed roles to access it. This decorator must follow the
    @auth_required decorator.
    """
    def decorator(method):
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            MissingRoleError.require_condition(
                current_rolenames().issuperset(set(required_rolenames)),
                "This endpoint requires all the following roles: {}",
                [', '.join(required_rolenames)],
            )
            return method(*args, **kwargs)
        return wrapper
    return decorator


def roles_accepted(*accepted_rolenames):
    """
    This decorator ensures that any uses accessing the decorated route have one
    of the needed roles to access it. This decorator must follow the
    @auth_required decorator.
    """
    def decorator(method):
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            MissingRoleError.require_condition(
                not current_rolenames().isdisjoint(set(accepted_rolenames)),
                "This endpoint requires one of the following roles: {}",
                [', '.join(accepted_rolenames)],
            )
            return method(*args, **kwargs)
        return wrapper
    return decorator
