import functools

from flask_praetorian.exceptions import MissingRoleError

from flask_praetorian.utilities import (
    current_guard,
    add_jwt_data_to_app_context,
    app_context_has_jwt_data,
    remove_jwt_data_from_app_context,
    current_rolenames,
)


def _verify_and_add_jwt():
    """
    This helper method just checks and adds jwt data to the app context. Will
    not add jwt data if it is already present. Only use in this module
    """
    if not app_context_has_jwt_data():
        guard = current_guard()
        token = guard.read_token_from_header()
        jwt_data = guard.extract_jwt_token(token)
        add_jwt_data_to_app_context(jwt_data)


def auth_required(method):
    """
    This decorator is used to ensure that a user is authenticated before
    being able to access a flask route. It also adds the current user to the
    current flask context.
    """
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        _verify_and_add_jwt()
        try:
            return method(*args, **kwargs)
        finally:
            remove_jwt_data_from_app_context()
    return wrapper


def roles_required(*required_rolenames):
    """
    This decorator ensures that any uses accessing the decorated route have all
    the needed roles to access it. If an @auth_required decorator is not
    supplied already, this decorator will implicitly check @auth_required first
    """
    def decorator(method):
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            _verify_and_add_jwt()
            try:
                MissingRoleError.require_condition(
                    current_rolenames().issuperset(set(required_rolenames)),
                    "This endpoint requires all the following roles: {}",
                    [', '.join(required_rolenames)],
                )
                return method(*args, **kwargs)
            finally:
                remove_jwt_data_from_app_context()
        return wrapper
    return decorator


def roles_accepted(*accepted_rolenames):
    """
    This decorator ensures that any uses accessing the decorated route have one
    of the needed roles to access it. If an @auth_required decorator is not
    supplied already, this decorator will implicitly check @auth_required first
    """
    def decorator(method):
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            _verify_and_add_jwt()
            try:
                MissingRoleError.require_condition(
                    not current_rolenames().isdisjoint(
                        set(accepted_rolenames)
                    ),
                    "This endpoint requires one of the following roles: {}",
                    [', '.join(accepted_rolenames)],
                )
                return method(*args, **kwargs)
            finally:
                remove_jwt_data_from_app_context()
        return wrapper
    return decorator
