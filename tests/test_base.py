import freezegun
import jwt
import pendulum
import pytest

from flask_praetorian import Praetorian
from flask_praetorian.exceptions import (
    BlacklistedError,
    EarlyRefreshError,
    ExpiredAccessError,
    ExpiredRefreshError,
    MissingClaimError,
    PraetorianError,
)
from flask_praetorian.constants import (
    AccessType,
    DEFAULT_JWT_ACCESS_LIFESPAN,
    DEFAULT_JWT_REFRESH_LIFESPAN,
    DEFAULT_JWT_HEADER_NAME,
    DEFAULT_JWT_HEADER_TYPE,
)


class NoLookupUser:
    @classmethod
    def identify(cls, id):
        pass


class NoIdentifyUser:
    @classmethod
    def lookup(cls, username):
        pass


class TestPraetorian:

    def test_encrypt_password(self, app, user_class):
        """
        This test verifies that Praetorian encrypts passwords using the scheme
        specified by the HASH_SCHEME setting. If no scheme is supplied, the
        test verifies that the default scheme is used. Otherwise, the test
        verifies that the encrypted password matches the supplied scheme
        """
        default_guard = Praetorian(app, user_class)
        secret = default_guard.encrypt_password('some password')
        assert default_guard.pwd_ctx.identify(secret) == 'pbkdf2_sha512'

        app.config['PRAETORIAN_HASH_SCHEME'] = 'plaintext'
        dumb_guard = Praetorian(app, user_class)
        assert dumb_guard.encrypt_password('some password') == 'some password'

    def test_verify_passord(self, app, user_class, default_guard):
        """
        This test verifies that the verify_password function can be used to
        successfully compare a raw password against its hashed version
        """
        secret = default_guard.encrypt_password('some password')
        assert default_guard.verify_password('some password', secret)
        assert not default_guard.verify_password('not right', secret)

        app.config['PRAETORIAN_HASH_SCHEME'] = 'pbkdf2_sha512'
        specified_guard = Praetorian(app, user_class)
        secret = specified_guard.encrypt_password('some password')
        assert specified_guard.verify_password('some password', secret)
        assert not specified_guard.verify_password('not right', secret)

    def test_authenticate(self, app, user_class, db):
        """
        This test verifies that the authenticate function can be used to
        retrieve a User instance when the correct username and password are
        supplied. It also verifies that None is returned when a matching
        password and username are not supplied
        """
        default_guard = Praetorian(app, user_class)
        the_dude = user_class(
            username='TheDude',
            password=default_guard.encrypt_password('abides'),
        )
        db.session.add(the_dude)
        db.session.commit()
        assert default_guard.authenticate('TheDude', 'abides') == the_dude
        assert default_guard.authenticate('TheDude', 'is_undudelike') is None
        assert default_guard.authenticate('Walter', 'abides') is None
        db.session.delete(the_dude)
        db.session.commit()

    def test_validate_user_class(self, app, user_class):
        """
        This test verifies that the validate_user_class method properly
        checks the user_class that Praetorian will use for required attributes
        """
        with pytest.raises(PraetorianError) as err_info:
            Praetorian.validate_user_class(NoLookupUser)
        assert "must have a lookup class method" in err_info.value.message

        with pytest.raises(PraetorianError) as err_info:
            Praetorian.validate_user_class(NoIdentifyUser)
        assert "must have an identify class method" in err_info.value.message

        assert Praetorian.validate_user_class(user_class)

    def test_validate_jwt_data(self, app, user_class):
        """
        This test verifies that the validate_jwt_data method properly validates
        the data for a jwt token. It checks that the proper exceptions are
        raised when validation fails and that no exceptions are raised when
        validation passes
        """
        guard = Praetorian(
            app, user_class,
            is_blacklisted=(lambda jti: jti == 'blacklisted'),
        )
        data = dict()
        with pytest.raises(MissingClaimError) as err_info:
            guard.validate_jwt_data(data, AccessType.access)
        assert 'missing jti' in str(err_info.value)

        data = dict(jti='blacklisted')
        with pytest.raises(BlacklistedError) as err_info:
            guard.validate_jwt_data(data, AccessType.access)

        data = dict(jti='jti')
        with pytest.raises(MissingClaimError) as err_info:
            guard.validate_jwt_data(data, AccessType.access)
        assert 'missing id' in str(err_info.value)

        data = dict(jti='jti', id=1)
        with pytest.raises(MissingClaimError) as err_info:
            guard.validate_jwt_data(data, AccessType.access)
        assert 'missing exp' in str(err_info.value)

        data = dict(
            jti='jti',
            id=1,
            exp=pendulum.parse('2017-05-21 19:54:30').int_timestamp,
        )
        with pytest.raises(MissingClaimError) as err_info:
            guard.validate_jwt_data(data, AccessType.access)
        assert 'missing rf_exp' in str(err_info.value)

        data = dict(
            jti='jti',
            id=1,
            exp=pendulum.parse('2017-05-21 19:54:30').int_timestamp,
            rf_exp=pendulum.parse('2017-05-21 20:54:30').int_timestamp,
        )
        moment = pendulum.parse('2017-05-21 19:54:32')
        with freezegun.freeze_time(moment):
            with pytest.raises(ExpiredAccessError) as err_info:
                guard.validate_jwt_data(data, AccessType.access)

        data = dict(
            jti='jti',
            id=1,
            exp=pendulum.parse('2017-05-21 19:54:30').int_timestamp,
            rf_exp=pendulum.parse('2017-05-21 20:54:30').int_timestamp,
        )
        moment = pendulum.parse('2017-05-21 19:54:28')
        with freezegun.freeze_time(moment):
            with pytest.raises(EarlyRefreshError) as err_info:
                guard.validate_jwt_data(data, AccessType.refresh)

        data = dict(
            jti='jti',
            id=1,
            exp=pendulum.parse('2017-05-21 19:54:30').int_timestamp,
            rf_exp=pendulum.parse('2017-05-21 20:54:30').int_timestamp,
        )
        moment = pendulum.parse('2017-05-21 20:54:32')
        with freezegun.freeze_time(moment):
            with pytest.raises(ExpiredRefreshError) as err_info:
                guard.validate_jwt_data(data, AccessType.refresh)

        data = dict(
            jti='jti',
            id=1,
            exp=pendulum.parse('2017-05-21 19:54:30').int_timestamp,
            rf_exp=pendulum.parse('2017-05-21 20:54:30').int_timestamp,
        )
        moment = pendulum.parse('2017-05-21 19:54:28')
        with freezegun.freeze_time(moment):
            guard.validate_jwt_data(data, AccessType.access)

        data = dict(
            jti='jti',
            id=1,
            exp=pendulum.parse('2017-05-21 19:54:30').int_timestamp,
            rf_exp=pendulum.parse('2017-05-21 20:54:30').int_timestamp,
        )
        moment = pendulum.parse('2017-05-21 19:54:32')
        with freezegun.freeze_time(moment):
            guard.validate_jwt_data(data, AccessType.refresh)

    def test_encode_jwt_token(self, app, user_class):
        """
        This test verifies that the encode_jwt_token correctly encodes jwt
        data based on a user instance
        """
        guard = Praetorian(app, user_class)
        the_dude = user_class(
            username='TheDude',
            password=guard.encrypt_password('abides'),
            roles='admin,operator',
        )
        moment = pendulum.parse('2017-05-21 18:39:55')
        with freezegun.freeze_time(moment):
            token = guard.encode_jwt_token(the_dude)
            token_data = jwt.decode(
                token, guard.encode_key, algorithms=guard.allowed_algorithms,
            )
            assert token_data['iat'] == moment.int_timestamp
            assert token_data['exp'] == (
                moment + DEFAULT_JWT_ACCESS_LIFESPAN
            ).int_timestamp
            assert token_data['rf_exp'] == (
                moment + DEFAULT_JWT_REFRESH_LIFESPAN
            ).int_timestamp
            assert token_data['id'] == the_dude.id
            assert token_data['rls'] == 'admin,operator'

    def test_refresh_jwt_token(self, app, db, user_class):
        """
        This test  verifies that the refresh_jwt_token properly generates
        a refreshed jwt token. It ensures that a token who's access permission
        has not expired may not be refreshed. It also ensures that a token
        who's access permission has expired must not have an expired refresh
        permission for a new token to be issued
        """
        guard = Praetorian(app, user_class)
        the_dude = user_class(
            username='TheDude',
            password=guard.encrypt_password('abides'),
            roles='admin,operator',
        )
        db.session.add(the_dude)
        db.session.commit()
        moment = pendulum.parse('2017-05-21 18:39:55')
        with freezegun.freeze_time(moment):
            token = guard.encode_jwt_token(the_dude)

        new_moment = (
            pendulum.parse('2017-05-21 18:39:55')
            .add_timedelta(DEFAULT_JWT_ACCESS_LIFESPAN)
            .add(minutes=1)
        )
        with freezegun.freeze_time(new_moment):
            new_token = guard.refresh_jwt_token(token)
            new_token_data = jwt.decode(
                new_token, guard.encode_key,
                algorithms=guard.allowed_algorithms,
            )
            assert new_token_data['iat'] == new_moment.int_timestamp
            assert new_token_data['exp'] == (
                new_moment + DEFAULT_JWT_ACCESS_LIFESPAN
            ).int_timestamp
            assert new_token_data['rf_exp'] == (
                moment + DEFAULT_JWT_REFRESH_LIFESPAN
            ).int_timestamp
            assert new_token_data['id'] == the_dude.id
            assert new_token_data['rls'] == 'admin,operator'

    def test_read_token_from_header(self, app, db, user_class, client):
        """
        This test verifies that a token may be properly read from a flask
        request's header using the configuration settings for header name and
        type
        """
        guard = Praetorian(app, user_class)
        the_dude = user_class(
            username='TheDude',
            password=guard.encrypt_password('abides'),
            roles='admin,operator',
        )
        db.session.add(the_dude)
        db.session.commit()

        moment = pendulum.parse('2017-05-21 18:39:55')
        with freezegun.freeze_time(moment):
            token = guard.encode_jwt_token(the_dude)

        client.get(
            '/unprotected',
            headers={
                'Content-Type': 'application/json',
                DEFAULT_JWT_HEADER_NAME: DEFAULT_JWT_HEADER_TYPE + ' ' + token,
            },
        )

        assert guard.read_token_from_header() == token
