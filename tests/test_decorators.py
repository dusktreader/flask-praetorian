import pendulum
import pytest
import freezegun

from flask_praetorian.exceptions import MissingRoleError


class TestPraetorianDecorators:

    @pytest.fixture(autouse=True)
    def setup(self, db, user_class, default_guard):
        """
        This fixture creates 4 users with different roles to test the
        decorators thoroughly
        """
        self.the_dude = user_class(
            username='TheDude',
            password=default_guard.encrypt_password('abides'),
        )
        self.walter = user_class(
            username='Walter',
            password=default_guard.encrypt_password('calmerthanyouare'),
            roles='admin'
        )
        self.donnie = user_class(
            username='Donnie',
            password=default_guard.encrypt_password('iamthewalrus'),
            roles='operator'
        )
        self.maude = user_class(
            username='Maude',
            password=default_guard.encrypt_password('andthorough'),
            roles='operator,admin'
        )
        self.jesus = user_class(
            username='Jesus',
            password=default_guard.encrypt_password('hecanroll'),
            roles='admin,god'
        )

        db.session.add(self.the_dude)
        db.session.add(self.walter)
        db.session.add(self.donnie)
        db.session.add(self.maude)
        db.session.add(self.jesus)
        db.session.commit()

    def test_auth_required(self, client, default_guard):
        """
        This test verifies that the @auth_required decorator can be used
        to ensure that any access to a protected endpoint must have a properly
        structured auth header including a valid jwt token.  Otherwise,
        a 401 error occurs with an informative error message.
        """

        # Token is not in header
        response = client.get(
            '/protected',
            headers={},
        )
        assert (
            "JWT token not found"
            in response.json['message']
        )
        assert response.status_code == 401

        # Token has invalid structure
        response = client.get(
            '/protected',
            headers={'Authorization': 'bad_structure iamatoken'},
        )
        assert (
            "JWT header structure is invalid"
            in response.json['message']
        )
        assert response.status_code == 401

        # Token is expired
        moment = pendulum.parse('2017-05-24 10:18:45')
        with freezegun.freeze_time(moment):
            headers = default_guard.pack_header_for_user(self.the_dude)
        moment = (
            moment +
            default_guard.access_lifespan +
            pendulum.Duration(seconds=1)
        )
        with freezegun.freeze_time(moment):
            response = client.get(
                '/protected',
                headers=headers,
            )
            assert response.status_code == 401
            assert (
                "access permission has expired"
                in response.json['message']
            )

        # Token is present and valid
        moment = pendulum.parse('2017-05-24 10:38:45')
        with freezegun.freeze_time(moment):
            response = client.get(
                '/protected',
                headers=default_guard.pack_header_for_user(self.the_dude),
            )
            assert response.status_code == 200

    def test_roles_required(self, client, default_guard):
        """
        This test verifies that the @roles_required decorator can be used
        to ensure that any users attempting to access a given endpoint must
        have all of the roles listed. If the correct roles are not supplied,
        a 401 error occurs with an informative error message.  This
        test also verifies that the @roles_required can be used with or without
        an explicit @auth_required decorator
        """

        # Lacks one of one required roles
        response = client.get(
            '/protected_admin_required',
            headers=default_guard.pack_header_for_user(self.the_dude),
        )
        assert response.status_code == 403
        assert (
            "This endpoint requires all the following roles"
            in response.json['message']
        )

        # Has one of one required roles
        response = client.get(
            '/protected_admin_required',
            headers=default_guard.pack_header_for_user(self.walter),
        )
        assert response.status_code == 200

        # Lacks one of two required roles
        response = client.get(
            '/protected_admin_and_operator_required',
            headers=default_guard.pack_header_for_user(self.walter),
        )
        assert response.status_code == 403
        assert MissingRoleError.__name__ in response.json['error']
        assert (
            "This endpoint requires all the following roles"
            in response.json['message']
        )

        # Has two of two required roles
        response = client.get(
            '/protected_admin_and_operator_required',
            headers=default_guard.pack_header_for_user(self.maude),
        )
        assert response.status_code == 200

        response = client.get(
            '/undecorated_admin_required',
            headers=default_guard.pack_header_for_user(self.maude),
        )
        assert response.status_code == 200

        response = client.get(
            '/undecorated_admin_accepted',
            headers=default_guard.pack_header_for_user(self.maude),
        )
        assert response.status_code == 200

        response = client.get(
            '/reversed_decorators',
            headers=default_guard.pack_header_for_user(self.maude),
        )
        assert response.status_code == 200

    def test_roles_accepted(self, client, default_guard):
        """
        This test verifies that the @roles_accepted decorator can be used
        to ensure that any users attempting to access a given endpoint must
        have one of the roles listed. If one of the correct roles are not
        supplied, a 401 error occurs with an informative error message.
        """
        response = client.get(
            '/protected',
            headers=default_guard.pack_header_for_user(self.the_dude),
        )
        assert response.status_code == 200

        response = client.get(
            '/protected_admin_and_operator_accepted',
            headers=default_guard.pack_header_for_user(self.the_dude),
        )
        assert response.status_code == 403
        assert MissingRoleError.__name__ in response.json['error']
        assert (
            "This endpoint requires one of the following roles"
            in response.json['message']
        )

        response = client.get(
            '/protected_admin_and_operator_accepted',
            headers=default_guard.pack_header_for_user(self.walter),
        )
        assert response.status_code == 200

        response = client.get(
            '/protected_admin_and_operator_accepted',
            headers=default_guard.pack_header_for_user(self.donnie),
        )
        assert response.status_code == 200

        response = client.get(
            '/protected_admin_and_operator_accepted',
            headers=default_guard.pack_header_for_user(self.maude),
        )
        assert response.status_code == 200

        response = client.get(
            '/protected_admin_and_operator_accepted',
            headers=default_guard.pack_header_for_user(self.jesus),
        )
        assert response.status_code == 200
