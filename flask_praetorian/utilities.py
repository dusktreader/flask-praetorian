import flask

from flask_praetorian.constants import RESERVED_CLAIMS
from flask_praetorian.exceptions import PraetorianError


def current_guard():
    """
    Fetches the current instance of flask-praetorian that is attached to the
    current flask app
    """
    guard = flask.current_app.extensions.get('praetorian', None)
    PraetorianError.require_condition(
        guard is not None,
        "No current guard found; Praetorian must be initialized first",
    )
    return guard


def app_context_has_jwt_data():
    """
    Checks if there is already jwt_data added to the app context
    """
    return hasattr(flask._app_ctx_stack.top, 'jwt_data')


def add_jwt_data_to_app_context(jwt_data):
    """
    Adds a dictionary of jwt data (presumably unpacked from a token) to the
    top of the flask app's context
    """
    ctx = flask._app_ctx_stack.top
    ctx.jwt_data = jwt_data


def get_jwt_data_from_app_context():
    """
    Fetches a dict of jwt token data from the top of the flask app's context
    """
    ctx = flask._app_ctx_stack.top
    jwt_data = getattr(ctx, 'jwt_data', None)
    PraetorianError.require_condition(
        jwt_data is not None,
        """
        No jwt_data found in app context.
        Make sure @auth_required decorator is specified *first* for route
        """,
    )
    return jwt_data


def remove_jwt_data_from_app_context():
    """
    Removes the dict of jwt token data from the top of the flask app's context
    """
    ctx = flask._app_ctx_stack.top
    if app_context_has_jwt_data():
        del ctx.jwt_data


def current_user_id():
    """
    This method returns the user id retrieved from jwt token data attached to
    the current flask app's context
    """
    jwt_data = get_jwt_data_from_app_context()
    user_id = jwt_data.get('id')
    PraetorianError.require_condition(
        user_id is not None,
        "Could not fetch an id for the current user",
    )
    return user_id


def current_user():
    """
    This method returns a user instance for jwt token data attached to the
    current flask app's context
    """
    user_id = current_user_id()
    guard = current_guard()
    user = guard.user_class.identify(user_id)
    PraetorianError.require_condition(
        user is not None,
        "Could not identify the current user from the current id",
    )
    return user


def current_rolenames():
    """
    This method returns the names of all roles associated with the current user
    """
    jwt_data = get_jwt_data_from_app_context()
    if 'rls' not in jwt_data:
        # This is necessary so our set arithmetic works correctly
        return set(['non-empty-but-definitely-not-matching-subset'])
    else:
        return set(r.strip() for r in jwt_data['rls'].split(','))


def current_custom_claims():
    """
    This method returns any custom claims in the current jwt
    """
    jwt_data = get_jwt_data_from_app_context()
    return {k: v for (k, v) in jwt_data.items() if k not in RESERVED_CLAIMS}
