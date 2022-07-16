import textwrap
import pendulum
import plummet

from httpx import Cookies

from sanic_testing.reusable import ReusableClient

from sanic.log import logger

from sanic_praetorian.exceptions import MissingRoleError


class TestPraetorianDecorators:
    async def test_auth_accepted(self, app, default_guard, the_dude):
        """
        This test verifies that the @auth_accepted decorator can be used
        to optionally use a properly structured auth header including
        a valid jwt token, setting the `current_user()`.
        """

        # Token is not in header or cookie
        client = ReusableClient(app, host='127.0.0.1', port='8000')
        with client:
            _, response = client.get(
                "/kinda_protected",
                headers={},
            )
            logger.critical(f'Response: {vars(response)}')
            assert response.status == 200
            assert "success" in response.json["message"]
            assert response.json["user"] is None

            # Token is present and valid
            with plummet.frozen_time('2017-05-24 10:38:45'):
                _, response = client.get(
                    "/kinda_protected",
                    headers=await default_guard.pack_header_for_user(the_dude),
                )
                assert response.status == 200
                assert "success" in response.json["message"]
                assert response.json["user"] == the_dude.username
        await the_dude.delete()

    async def test_auth_required(self, app, default_guard, the_dude):
        """
        This test verifies that the @auth_required decorator can be used
        to ensure that any access to a protected endpoint must have a properly
        structured auth header or cookie including a valid jwt token.
        Otherwise, a 401 error occurs with an informative error message.
        """

        # Token is not in header or cookie

        client = ReusableClient(app, host='127.0.0.1', port='8000')
        with client:
            _, response = client.get(
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
            assert response.status == 401

            # Token has invalid structure
            _, response = client.get(
                "/protected",
                headers={"Authorization": "bad_structure iamatoken"},
            )
            assert "JWT header structure is invalid" in response.json["message"]
            assert response.status == 401
    
            # Token is expired
            moment = pendulum.parse('2017-05-24 10:18:45')
            with plummet.frozen_time(moment):
                headers = await default_guard.pack_header_for_user(the_dude)
            moment = (
                moment
                + default_guard.access_lifespan
                + pendulum.Duration(seconds=1)
            )
            with plummet.frozen_time(moment):
                _, response = client.get(
                    "/protected",
                    headers=headers,
                )
                assert response.status == 401
                assert "access permission has expired" in response.json["message"]
    
            # Token is present and valid in header or cookie
            with plummet.frozen_time('2017-05-24 10:38:45'):
                _, response = client.get(
                    "/protected",
                    headers=await default_guard.pack_header_for_user(the_dude),
                )
    
                assert response.status == 200

                cookies = Cookies()
                token = await default_guard.encode_jwt_token(the_dude)
                cookies[default_guard.cookie_name] = token
                _, response = client.get("/protected", cookies = cookies)
                assert response.status == 200
    
    async def test_roles_required(self, app, default_guard, walter, the_dude, maude):
        """
        This test verifies that the @roles_required decorator can be used
        to ensure that any users attempting to access a given endpoint must
        have all of the roles listed. If the correct roles are not supplied,
        a 401 error occurs with an informative error message.  This
        test also verifies that the @roles_required can be used with or without
        an explicit @auth_required decorator
        """

        # Lacks one of one required roles
        client = ReusableClient(app, host='127.0.0.1', port='8000')
        with client:
            _, response = client.get(
                "/protected_admin_required",
                headers=await default_guard.pack_header_for_user(the_dude),
            )
            assert response.status == 403
            assert (
                "This endpoint requires all the following roles"
                in response.json["message"]
            )
    
            # Has one of one required roles
            _, response = client.get(
                "/protected_admin_required",
                headers=await default_guard.pack_header_for_user(walter),
            )
            assert response.status == 200
    
            # Lacks one of two required roles
            _, response = client.get(
                "/protected_admin_and_operator_required",
                headers=await default_guard.pack_header_for_user(walter),
            )
            assert response.status == 403
            logger.critical(f"Got Response: {response}")
            logger.critical(f"Got Response Vars: {vars(response)}")
            assert MissingRoleError.__name__ in response.json["message"]
            assert (
                "This endpoint requires all the following roles"
                in response.json["message"]
            )
    
            # Has two of two required roles
            _, response = client.get(
                "/protected_admin_and_operator_required",
                headers=await default_guard.pack_header_for_user(maude),
            )
            assert response.status == 200
    
            _, response = client.get(
                "/undecorated_admin_required",
                headers=await default_guard.pack_header_for_user(maude),
            )
            assert response.status == 200
    
            _, response = client.get(
                "/undecorated_admin_accepted",
                headers=await default_guard.pack_header_for_user(maude),
            )
            assert response.status == 200
    
            _, response = client.get(
                "/reversed_decorators",
                headers=await default_guard.pack_header_for_user(maude),
            )
            assert response.status == 200
    
    async def test_roles_accepted(self, app, default_guard, the_dude, walter, donnie, maude, jesus):
        """
        This test verifies that the @roles_accepted decorator can be used
        to ensure that any users attempting to access a given endpoint must
        have one of the roles listed. If one of the correct roles are not
        supplied, a 401 error occurs with an informative error message.
        """
        client = ReusableClient(app, host='127.0.0.1', port='8000')
        with client:
            _, response = client.get(
                "/protected",
                headers=await default_guard.pack_header_for_user(the_dude),
            )
            assert response.status == 200
    
            _, response = client.get(
                "/protected_admin_and_operator_accepted",
                headers=await default_guard.pack_header_for_user(the_dude),
            )
            assert response.status == 403
            assert MissingRoleError.__name__ in response.json["message"]
            assert (
                "This endpoint requires one of the following roles"
                in response.json["message"]
            )
    
            _, response = client.get(
                "/protected_admin_and_operator_accepted",
                headers=await default_guard.pack_header_for_user(walter),
            )
            assert response.status == 200
    
            _, response = client.get(
                "/protected_admin_and_operator_accepted",
                headers=await default_guard.pack_header_for_user(donnie),
            )
            assert response.status == 200
    
            _, response = client.get(
                "/protected_admin_and_operator_accepted",
                headers=await default_guard.pack_header_for_user(maude),
            )
            assert response.status == 200
    
            _, response = client.get(
                "/protected_admin_and_operator_accepted",
                headers=await default_guard.pack_header_for_user(jesus),
            )
            assert response.status == 200
