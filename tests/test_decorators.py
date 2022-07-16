import textwrap
import pendulum
import plummet
import pytest

from sanic_praetorian.exceptions import MissingRoleError


class TestPraetorianDecorators:
    @pytest.fixture(autouse=True)
    def setup(self, db_session, user_class, default_guard):
        """
        This fixture creates 4 users with different roles to test the
        decorators thoroughly
        """
        self.the_dude = user_class(
            username="TheDude",
            password=default_guard.hash_password("abides"),
        )
        self.walter = user_class(
            username="Walter",
            password=default_guard.hash_password("calmerthanyouare"),
            roles="admin",
        )
        self.donnie = user_class(
            username="Donnie",
            password=default_guard.hash_password("iamthewalrus"),
            roles="operator",
        )
        self.maude = user_class(
            username="Maude",
            password=default_guard.hash_password("andthorough"),
            roles="operator,admin",
        )
        self.jesus = user_class(
            username="Jesus",
            password=default_guard.hash_password("hecanroll"),
            roles="admin,god",
        )

        db_session.add(self.the_dude)
        db_session.add(self.walter)
        db_session.add(self.donnie)
        db_session.add(self.maude)
        db_session.add(self.jesus)
        db_session.commit()

    def test_auth_accepted(self, app, default_guard):
        """
        This test verifies that the @auth_accepted decorator can be used
        to optionally use a properly structured auth header including
        a valid jwt token, setting the `current_user()`.
        """

        # Token is not in header or cookie
        response = app.test_client.get(
            "/kinda_protected",
            headers={},
        )
        assert response.status_code == 200
        assert "success" in response.json["message"]
        assert response.json["user"] is None

        # Token is present and valid
        with plummet.frozen_time('2017-05-24 10:38:45'):
            response = app.test_client.get(
                "/kinda_protected",
                headers=default_guard.pack_header_for_user(self.the_dude),
            )
            assert response.status_code == 200
            assert "success" in response.json["message"]
            assert response.json["user"] == self.the_dude.username

    def test_auth_required(self, app, default_guard, use_cookie):
        """
        This test verifies that the @auth_required decorator can be used
        to ensure that any access to a protected endpoint must have a properly
        structured auth header or cookie including a valid jwt token.
        Otherwise, a 401 error occurs with an informative error message.
        """

        # Token is not in header or cookie
        response = app.test_client.get(
            "/protected",
            headers={},
        )

        exc_msg = textwrap.dedent(
                f"""
                Could not find token in any
                 of the given locations: {default_guard.jwt_places}
                """
        ).replace("\n", "")

        assert exc_msg in response.json["message"]
        assert response.status_code == 401

        # Token has invalid structure
        response = app.test_client.get(
            "/protected",
            headers={"Authorization": "bad_structure iamatoken"},
        )
        assert "JWT header structure is invalid" in response.json["message"]
        assert response.status_code == 401

        # Token is expired
        moment = pendulum.parse('2017-05-24 10:18:45')
        with plummet.frozen_time(moment):
            headers = default_guard.pack_header_for_user(self.the_dude)
        moment = (
            moment
            + default_guard.access_lifespan
            + pendulum.Duration(seconds=1)
        )
        with plummet.frozen_time(moment):
            response = app.test_client.get(
                "/protected",
                headers=headers,
            )
            assert response.status_code == 401
            assert "access permission has expired" in response.json["message"]

        # Token is present and valid in header or cookie
        with plummet.frozen_time('2017-05-24 10:38:45'):
            response = app.test_client.get(
                "/protected",
                headers=default_guard.pack_header_for_user(self.the_dude),
            )

            assert response.status_code == 200
            token = default_guard.encode_jwt_token(self.the_dude)
            with use_cookie(token):
                response = app.test_client.get("/protected")
                assert response.status_code == 200

    def test_roles_required(self, app, default_guard):
        """
        This test verifies that the @roles_required decorator can be used
        to ensure that any users attempting to access a given endpoint must
        have all of the roles listed. If the correct roles are not supplied,
        a 401 error occurs with an informative error message.  This
        test also verifies that the @roles_required can be used with or without
        an explicit @auth_required decorator
        """

        # Lacks one of one required roles
        response = app.test_client.get(
            "/protected_admin_required",
            headers=default_guard.pack_header_for_user(self.the_dude),
        )
        assert response.status_code == 403
        assert (
            "This endpoint requires all the following roles"
            in response.json["message"]
        )

        # Has one of one required roles
        response = app.test_client.get(
            "/protected_admin_required",
            headers=default_guard.pack_header_for_user(self.walter),
        )
        assert response.status_code == 200

        # Lacks one of two required roles
        response = app.test_client.get(
            "/protected_admin_and_operator_required",
            headers=default_guard.pack_header_for_user(self.walter),
        )
        assert response.status_code == 403
        assert MissingRoleError.__name__ in response.json["error"]
        assert (
            "This endpoint requires all the following roles"
            in response.json["message"]
        )

        # Has two of two required roles
        response = app.test_client.get(
            "/protected_admin_and_operator_required",
            headers=default_guard.pack_header_for_user(self.maude),
        )
        assert response.status_code == 200

        response = app.test_client.get(
            "/undecorated_admin_required",
            headers=default_guard.pack_header_for_user(self.maude),
        )
        assert response.status_code == 200

        response = app.test_client.get(
            "/undecorated_admin_accepted",
            headers=default_guard.pack_header_for_user(self.maude),
        )
        assert response.status_code == 200

        response = app.test_client.get(
            "/reversed_decorators",
            headers=default_guard.pack_header_for_user(self.maude),
        )
        assert response.status_code == 200

    def test_roles_accepted(self, app, default_guard):
        """
        This test verifies that the @roles_accepted decorator can be used
        to ensure that any users attempting to access a given endpoint must
        have one of the roles listed. If one of the correct roles are not
        supplied, a 401 error occurs with an informative error message.
        """
        response = app.test_client.get(
            "/protected",
            headers=default_guard.pack_header_for_user(self.the_dude),
        )
        assert response.status_code == 200

        response = app.test_client.get(
            "/protected_admin_and_operator_accepted",
            headers=default_guard.pack_header_for_user(self.the_dude),
        )
        assert response.status_code == 403
        assert MissingRoleError.__name__ in response.json["error"]
        assert (
            "This endpoint requires one of the following roles"
            in response.json["message"]
        )

        response = app.test_client.get(
            "/protected_admin_and_operator_accepted",
            headers=default_guard.pack_header_for_user(self.walter),
        )
        assert response.status_code == 200

        response = app.test_client.get(
            "/protected_admin_and_operator_accepted",
            headers=default_guard.pack_header_for_user(self.donnie),
        )
        assert response.status_code == 200

        response = app.test_client.get(
            "/protected_admin_and_operator_accepted",
            headers=default_guard.pack_header_for_user(self.maude),
        )
        assert response.status_code == 200

        response = app.test_client.get(
            "/protected_admin_and_operator_accepted",
            headers=default_guard.pack_header_for_user(self.jesus),
        )
        assert response.status_code == 200
