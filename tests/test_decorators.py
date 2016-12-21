import pytest
import json

from flask_praetorian.exceptions import PraetorianError


def get_token(client, username, password):
    """
    This is a helper function that retrieves a jwt token based on a username
    and password. It is used just for testing
    """
    response = client.post(
        '/auth',
        headers={'Content-Type': 'application/json'},
        data=json.dumps({'username': username, 'password': password}),
    )
    PraetorianError.require_condition(
        response.status_code == 200,
        "Couldn't fetch a token {}",
        str(response.status),
    )
    return response.json['access_token']


def make_request(client, url, token):
    """
    This helper function calls a GET on the designated url and adds an
    authorization header with the supplied token. It is used just for testing
    """
    return client.get(url, headers={'Authorization': 'JWT ' + token})


class TestPraetorian:

    @pytest.fixture(autouse=True)
    def setup(self, app, db, user_class, default_guard):
        """
        This fixture creates 4 users with different roles to test the
        decorators thoroughly
        """
        db.session.add(user_class(
            username='TheDude',
            password=default_guard.encrypt_password('abides'),
        ))
        db.session.add(user_class(
            username='Walter',
            password=default_guard.encrypt_password('calmerthanyouare'),
            roles='admin'
        ))
        db.session.add(user_class(
            username='Donnie',
            password=default_guard.encrypt_password('iamthewalrus'),
            roles='operator'
        ))
        db.session.add(user_class(
            username='Maude',
            password=default_guard.encrypt_password('andthorough'),
            roles='operator,admin'
        ))
        db.session.commit()

    def test_roles_required(self, client):
        """
        This test verifies that the @roles_required decorator can be used
        to ensure that any users attempting to access a given endpoint must
        have all of the roles listed. If the correct roles are not supplied,
        a 401 error occurs with an informative error message. This test
        also verifies that the @roles_required decorator has to be used with
        the @jwt_required decorator
        """
        response = client.get('/unprotected')
        assert response.status_code == 401
        assert (
            "Cannot check roles without identity"
            in response.json['description']
        )

        response = make_request(
            client,
            '/protected',
            get_token(client, 'TheDude', 'abides'),
        )
        assert response.status_code == 200

        response = make_request(
            client,
            '/protected_admin_required',
            get_token(client, 'TheDude', 'abides'),
        )
        assert response.status_code == 401
        assert (
            "This endpoint requires all the following roles"
            in response.json['description']
        )

        response = make_request(
            client,
            '/protected_admin_required',
            get_token(client, 'Walter', 'calmerthanyouare'),
        )
        assert response.status_code == 200

        response = make_request(
            client,
            '/protected_admin_and_operator_required',
            get_token(client, 'Walter', 'calmerthanyouare'),
        )
        assert response.status_code == 401
        assert (
            "This endpoint requires all the following roles"
            in response.json['description']
        )

        response = make_request(
            client,
            '/protected_admin_and_operator_required',
            get_token(client, 'Maude', 'andthorough'),
        )
        assert response.status_code == 200

        response = make_request(
            client,
            '/undecorated_admin_required',
            get_token(client, 'Walter', 'calmerthanyouare'),
        )
        assert response.status_code == 401
        assert (
            "Cannot check roles without identity set"
            in response.json['description']
        )

        response = make_request(
            client,
            '/undecorated_admin_accepted',
            get_token(client, 'Walter', 'calmerthanyouare'),
        )
        assert response.status_code == 401
        assert (
            "Cannot check roles without identity set"
            in response.json['description']
        )

        response = make_request(
            client,
            '/reversed_decorators',
            get_token(client, 'Walter', 'calmerthanyouare'),
        )
        assert response.status_code == 401
        assert (
            "Cannot check roles without identity set"
            in response.json['description']
        )

    def test_roles_accepted(self, client):
        """
        This test verifies that the @roles_accepted decorator can be used
        to ensure that any users attempting to access a given endpoint must
        have one of the roles listed. If one of the correct roles are not
        supplied, a 401 error occurs with an informative error message. This
        test also verifies that the @roles_required decorator has to be used
        with the @jwt_required decorator
        """
        response = client.get('/unprotected')
        assert response.status_code == 401
        assert (
            "Cannot check roles without identity"
            in response.json['description']
        )

        response = make_request(
            client,
            '/protected',
            get_token(client, 'TheDude', 'abides'),
        )
        assert response.status_code == 200

        response = make_request(
            client,
            '/protected_admin_and_operator_accepted',
            get_token(client, 'TheDude', 'abides'),
        )
        assert response.status_code == 401
        assert (
            "This endpoint requires one of the following roles"
            in response.json['description']
        )

        response = make_request(
            client,
            '/protected_admin_and_operator_accepted',
            get_token(client, 'Walter', 'calmerthanyouare'),
        )
        assert response.status_code == 200

        response = make_request(
            client,
            '/protected_admin_and_operator_accepted',
            get_token(client, 'Maude', 'andthorough'),
        )
        assert response.status_code == 200
