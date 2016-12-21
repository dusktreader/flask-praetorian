import flask_jwt
import json

from flask_praetorian import Praetorian

from tests.test_decorators import get_token, make_request


class TestIntegrationPraetorian:

    def test_integration_basic(self, app, db, user_class, client):
        """
        Tests the basic funciton of Praetorian with a vanilla setup
        """
        guard = Praetorian(app, user_class)
        db.session.add(user_class(
            username='TheDude',
            password=guard.encrypt_password('abides'),
            roles='operator,admin'
        ))
        db.session.commit()
        response = make_request(
            client,
            '/protected_admin_required',
            get_token(client, 'TheDude', 'abides'),
        )
        assert response.status_code == 200

    def test_integration_late_binding(self, app, db, user_class, client):
        """
        Tests to make sure that late bindings may be used to set up the
        Praetorian extension. In particular verifies that a foreign jwt
        instance may be passed in at init time.

        .. note::

           Using an extant jwt instance will result in the authentication
           and identity handlers for that instance to be overridden.
        """
        the_dude = user_class(
            username='TheDude',
            password='abides',
            roles='operator,admin'
        )
        db.session.add(the_dude)
        db.session.commit()

        jwt = flask_jwt.JWT(
            app,
            authentication_handler=lambda u, p: None,
            identity_handler=lambda p: None,
        )
        response = client.post(
            '/auth',
            headers={'Content-Type': 'application/json'},
            data=json.dumps({'username': 'TheDude', 'password': 'abides'}),
        )
        assert response.status_code != 200

        guard = Praetorian(app=app, user_class=user_class, jwt=jwt)
        the_dude.password = guard.encrypt_password('abides')
        db.session.commit()
        response = client.post(
            '/auth',
            headers={'Content-Type': 'application/json'},
            data=json.dumps({'username': 'TheDude', 'password': 'abides'}),
        )
        assert response.status_code == 200
        token = response.json['access_token']
        response = make_request(
            client,
            '/protected_admin_required',
            token,
        )
        assert response.status_code == 200
