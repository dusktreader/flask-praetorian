import flask
import pytest

from flask_praetorian.utilities import (
    add_jwt_data_to_app_context,
    app_context_has_jwt_data,
    remove_jwt_data_from_app_context,
    current_user,
    current_user_id,
    current_rolenames,
    current_custom_claims,
)
from flask_praetorian.exceptions import PraetorianError


class TestPraetorianUtilities:

    def test_app_context_has_jwt_data(self):
        """
        This test verifies that the app_context_has_jwt_data method can
        determine if jwt_data has been added to the app context yet
        """
        assert not app_context_has_jwt_data()
        add_jwt_data_to_app_context({'a': 1})
        assert app_context_has_jwt_data()
        remove_jwt_data_from_app_context()
        assert not app_context_has_jwt_data()

    def test_remove_jwt_data_from_app_context(self):
        """
        This test verifies that jwt data can be removed from an app context.
        It also verifies that attempting to remove the data if it does not
        exist there does not cause an exception
        """
        jwt_data = {'a': 1}
        add_jwt_data_to_app_context(jwt_data)
        assert flask._app_ctx_stack.top.jwt_data == jwt_data
        remove_jwt_data_from_app_context()
        assert not hasattr(flask._app_ctx_stack.top, 'jwt_data')
        remove_jwt_data_from_app_context()

    def test_current_user_id(self, user_class, db, default_guard):
        """
        This test verifies that the current user id can be successfully
        determined based on jwt token data that has been added to the current
        flask app's context.
        """
        jwt_data = {}
        add_jwt_data_to_app_context(jwt_data)
        with pytest.raises(PraetorianError) as err_info:
            current_user()
        assert 'Could not fetch an id' in str(err_info.value)

        jwt_data = {'id': 31}
        add_jwt_data_to_app_context(jwt_data)
        assert current_user_id() == 31

    def test_current_user(self, user_class, db, default_guard):
        """
        This test verifies that the current user can be successfully
        determined based on jwt token data that has been added to the current
        flask app's context.
        """
        jwt_data = {}
        add_jwt_data_to_app_context(jwt_data)
        with pytest.raises(PraetorianError) as err_info:
            current_user()
        assert 'Could not fetch an id' in str(err_info.value)

        jwt_data = {'id': 31}
        add_jwt_data_to_app_context(jwt_data)
        with pytest.raises(PraetorianError) as err_info:
            current_user()
        assert 'Could not identify the current user' in str(err_info.value)

        the_dude = user_class(
            id=13,
            username='TheDude',
        )
        db.session.add(the_dude)
        db.session.commit()
        jwt_data = {'id': 13}
        add_jwt_data_to_app_context(jwt_data)
        assert current_user() is the_dude

    def test_current_rolenames(self, user_class, db, default_guard):
        """
        This test verifies that the rolenames attached to the current user
        can be extracted from the jwt token data that has been added to the
        current flask app's context
        """
        jwt_data = {}
        add_jwt_data_to_app_context(jwt_data)
        assert current_rolenames() == set([
            'non-empty-but-definitely-not-matching-subset'
        ])

        jwt_data = {'rls': 'admin,operator'}
        add_jwt_data_to_app_context(jwt_data)
        assert current_rolenames() == set(['admin', 'operator'])

    def test_current_custom_claims(self, user_class, db, default_guard):
        """
        This test verifies that any custom claims attached to the current jwt
        can be extracted from the jwt token data that has been added to the
        current flask app's context
        """
        jwt_data = dict(
            id=13,
            jti='whatever',
            duder='brief',
            el_duderino='not brief',
        )
        add_jwt_data_to_app_context(jwt_data)
        assert current_custom_claims() == dict(
            duder='brief',
            el_duderino='not brief',
        )
