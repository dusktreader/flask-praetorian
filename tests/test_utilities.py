import flask
import pendulum
import pytest

from flask_praetorian.utilities import (
    add_jwt_data_to_app_context,
    app_context_has_jwt_data,
    remove_jwt_data_from_app_context,
    current_user,
    current_user_id,
    current_rolenames,
    current_custom_claims,
    duration_from_string,
)
from flask_praetorian.exceptions import (
    PraetorianError,
    ConfigurationError,
)


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

    def test_duration_from_string_success(self):
        """
        This test verifies that the duration_from_string method can be used to
        parse a duration from a string with expected formats
        """
        expected_duration = pendulum.duration(days=12, hours=1, seconds=1)
        computed_duration = duration_from_string('12d1h1s')
        assert computed_duration == expected_duration

        expected_duration = pendulum.duration(months=1, hours=2, minutes=3)
        computed_duration = duration_from_string('1 Month 2 Hours 3 minutes')
        assert computed_duration == expected_duration

        expected_duration = pendulum.duration(days=1, minutes=2, seconds=3)
        computed_duration = duration_from_string('1day,2min,3sec')
        assert computed_duration == expected_duration

        expected_duration = pendulum.duration(months=1, minutes=2)
        computed_duration = duration_from_string('1mo,2m')
        assert computed_duration == expected_duration

    def test_duration_from_string_fails(self):
        """
        This test verifies that the duration_from_string method raises a
        ConfiguationError exception if there was a problem parsing the string
        """
        with pytest.raises(ConfigurationError):
            duration_from_string('12x1y1z')
        with pytest.raises(ConfigurationError):
            duration_from_string('')
