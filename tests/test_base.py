import freezegun
import jwt
import pendulum
import pytest
from os.path import dirname, abspath

from jinja2 import Template

from flask_praetorian import Praetorian
from flask_praetorian.exceptions import (
    AuthenticationError,
    BlacklistedError,
    ClaimCollisionError,
    EarlyRefreshError,
    ExpiredAccessError,
    ExpiredRefreshError,
    InvalidUserError,
    MissingClaimError,
    MissingUserError,
    PraetorianError,
    LegacyScheme,
)
from flask_praetorian.constants import (
    AccessType,
    DEFAULT_JWT_ACCESS_LIFESPAN,
    DEFAULT_JWT_REFRESH_LIFESPAN,
    DEFAULT_JWT_HEADER_NAME,
    DEFAULT_JWT_HEADER_TYPE,
    VITAM_AETERNUM,
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

    def test_hash_password(self, app, user_class):
        """
        This test verifies that Praetorian encrypts passwords using the scheme
        specified by the HASH_SCHEME setting. If no scheme is supplied, the
        test verifies that the default scheme is used. Otherwise, the test
        verifies that the encrypted password matches the supplied scheme.
        """

        default_guard = Praetorian(app, user_class)
        secret = default_guard.hash_password('some password')
        assert default_guard.pwd_ctx.identify(secret) == 'pbkdf2_sha512'

    def test__verify_password(self, app, user_class, default_guard):
        """
        This test verifies that the _verify_password function can be used to
        successfully compare a raw password against its hashed version
        """

        secret = default_guard.hash_password('some password')
        assert default_guard._verify_password('some password', secret)
        assert not default_guard._verify_password('not right', secret)

        app.config['PRAETORIAN_HASH_SCHEME'] = 'pbkdf2_sha512'
        specified_guard = Praetorian(app, user_class)
        secret = specified_guard.hash_password('some password')
        assert specified_guard._verify_password('some password', secret)
        assert not specified_guard._verify_password('not right', secret)

    def test_authenticate(self, app, user_class, db):
        """
        This test verifies that the authenticate function can be used to
        retrieve a User instance when the correct username and password are
        supplied. It also verifies that exceptions are raised when a user
        cannot be found or the passwords do not match
        """
        default_guard = Praetorian(app, user_class)
        the_dude = user_class(
            username='TheDude',
            password=default_guard.hash_password('abides'),
        )
        db.session.add(the_dude)
        db.session.commit()
        assert default_guard.authenticate('TheDude', 'abides') == the_dude
        with pytest.raises(MissingUserError):
            default_guard.authenticate('TheBro', 'abides')
        with pytest.raises(AuthenticationError):
            default_guard.authenticate('TheDude', 'is_undudelike')
        db.session.delete(the_dude)
        db.session.commit()

    def test__validate_user_class(self, app, user_class):
        """
        This test verifies that the _validate_user_class method properly
        checks the user_class that Praetorian will use for required attributes
        """
        with pytest.raises(PraetorianError) as err_info:
            Praetorian._validate_user_class(NoLookupUser)
        assert "must have a lookup class method" in err_info.value.message

        with pytest.raises(PraetorianError) as err_info:
            Praetorian._validate_user_class(NoIdentifyUser)
        assert "must have an identify class method" in err_info.value.message

        assert Praetorian._validate_user_class(user_class)

    def test__validate_jwt_data(self, app, user_class):
        """
        This test verifies that the _validate_jwt_data method properly
        validates the data for a jwt token. It checks that the proper
        exceptions are raised when validation fails and that no exceptions are
        raised when validation passes
        """
        guard = Praetorian(
            app, user_class,
            is_blacklisted=(lambda jti: jti == 'blacklisted'),
        )
        data = dict()
        with pytest.raises(MissingClaimError) as err_info:
            guard._validate_jwt_data(data, AccessType.access)
        assert 'missing jti' in str(err_info.value)

        data = dict(jti='blacklisted')
        with pytest.raises(BlacklistedError) as err_info:
            guard._validate_jwt_data(data, AccessType.access)

        data = dict(jti='jti')
        with pytest.raises(MissingClaimError) as err_info:
            guard._validate_jwt_data(data, AccessType.access)
        assert 'missing id' in str(err_info.value)

        data = dict(jti='jti', id=1)
        with pytest.raises(MissingClaimError) as err_info:
            guard._validate_jwt_data(data, AccessType.access)
        assert 'missing exp' in str(err_info.value)

        data = dict(
            jti='jti',
            id=1,
            exp=pendulum.parse('2017-05-21 19:54:30').int_timestamp,
        )
        with pytest.raises(MissingClaimError) as err_info:
            guard._validate_jwt_data(data, AccessType.access)
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
                guard._validate_jwt_data(data, AccessType.access)

        data = dict(
            jti='jti',
            id=1,
            exp=pendulum.parse('2017-05-21 19:54:30').int_timestamp,
            rf_exp=pendulum.parse('2017-05-21 20:54:30').int_timestamp,
        )
        moment = pendulum.parse('2017-05-21 19:54:28')
        with freezegun.freeze_time(moment):
            with pytest.raises(EarlyRefreshError) as err_info:
                guard._validate_jwt_data(data, AccessType.refresh)

        data = dict(
            jti='jti',
            id=1,
            exp=pendulum.parse('2017-05-21 19:54:30').int_timestamp,
            rf_exp=pendulum.parse('2017-05-21 20:54:30').int_timestamp,
        )
        moment = pendulum.parse('2017-05-21 20:54:32')
        with freezegun.freeze_time(moment):
            with pytest.raises(ExpiredRefreshError) as err_info:
                guard._validate_jwt_data(data, AccessType.refresh)

        data = dict(
            jti='jti',
            id=1,
            exp=pendulum.parse('2017-05-21 19:54:30').int_timestamp,
            rf_exp=pendulum.parse('2017-05-21 20:54:30').int_timestamp,
        )
        moment = pendulum.parse('2017-05-21 19:54:28')
        with freezegun.freeze_time(moment):
            guard._validate_jwt_data(data, AccessType.access)

        data = dict(
            jti='jti',
            id=1,
            exp=pendulum.parse('2017-05-21 19:54:30').int_timestamp,
            rf_exp=pendulum.parse('2017-05-21 20:54:30').int_timestamp,
        )
        moment = pendulum.parse('2017-05-21 19:54:32')
        with freezegun.freeze_time(moment):
            guard._validate_jwt_data(data, AccessType.refresh)

    def test_encode_jwt_token(self, app, user_class, validating_user_class):
        """
        This test::
            * verifies that the encode_jwt_token correctly encodes jwt
              data based on a user instance.
            * verifies that if a user specifies an override for the access
              lifespan it is used in lieu of the instance's access_lifespan.
            * verifies that the access_lifespan cannot exceed the refresh
              lifespan.
            * ensures that if the user_class has the instance method
              validate(), it is called an any exceptions it raises are wrapped
              in an InvalidUserError
            * verifies that custom claims may be encoded in the token and
              validates that the custom claims do not collide with reserved
              claims
        """
        guard = Praetorian(app, user_class)
        the_dude = user_class(
            username='TheDude',
            password=guard.hash_password('abides'),
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
                moment + pendulum.Duration(**DEFAULT_JWT_ACCESS_LIFESPAN)
            ).int_timestamp
            assert token_data['rf_exp'] == (
                moment + pendulum.Duration(**DEFAULT_JWT_REFRESH_LIFESPAN)
            ).int_timestamp
            assert token_data['id'] == the_dude.id
            assert token_data['rls'] == 'admin,operator'

        moment = pendulum.parse('2017-05-21 18:39:55')
        override_access_lifespan = pendulum.Duration(minutes=1)
        override_refresh_lifespan = pendulum.Duration(hours=1)
        with freezegun.freeze_time(moment):
            token = guard.encode_jwt_token(
                the_dude,
                override_access_lifespan=override_access_lifespan,
                override_refresh_lifespan=override_refresh_lifespan,
            )
            token_data = jwt.decode(
                token, guard.encode_key, algorithms=guard.allowed_algorithms,
            )
            assert token_data['iat'] == moment.int_timestamp
            assert token_data['exp'] == (
                moment + override_access_lifespan
            ).int_timestamp
            assert token_data['rf_exp'] == (
                moment + override_refresh_lifespan
            ).int_timestamp
            assert token_data['id'] == the_dude.id
            assert token_data['rls'] == 'admin,operator'

        moment = pendulum.parse('2017-05-21 18:39:55')
        override_access_lifespan = pendulum.Duration(hours=1)
        override_refresh_lifespan = pendulum.Duration(minutes=1)
        with freezegun.freeze_time(moment):
            token = guard.encode_jwt_token(
                the_dude,
                override_access_lifespan=override_access_lifespan,
                override_refresh_lifespan=override_refresh_lifespan,
            )
            token_data = jwt.decode(
                token, guard.encode_key, algorithms=guard.allowed_algorithms,
            )
            assert token_data['iat'] == moment.int_timestamp
            assert token_data['exp'] == token_data['rf_exp']
            assert token_data['rf_exp'] == (
                moment + override_refresh_lifespan
            ).int_timestamp
            assert token_data['id'] == the_dude.id
            assert token_data['rls'] == 'admin,operator'

        validating_guard = Praetorian(app, validating_user_class)
        brandt = validating_user_class(
            username='brandt',
            password=guard.hash_password("can't watch"),
            is_active=True,
        )
        validating_guard.encode_jwt_token(brandt)
        brandt.is_active = False
        with pytest.raises(InvalidUserError) as err_info:
            validating_guard.encode_jwt_token(brandt)
        expected_message = 'The user is not valid or has had access revoked'
        assert expected_message in str(err_info.value)

        moment = pendulum.parse('2018-08-18 08:55:12')
        with freezegun.freeze_time(moment):
            token = guard.encode_jwt_token(
                the_dude,
                duder='brief',
                el_duderino='not brief',
            )
            token_data = jwt.decode(
                token, guard.encode_key, algorithms=guard.allowed_algorithms,
            )
            assert token_data['iat'] == moment.int_timestamp
            assert token_data['exp'] == (
                moment + pendulum.Duration(**DEFAULT_JWT_ACCESS_LIFESPAN)
            ).int_timestamp
            assert token_data['rf_exp'] == (
                moment + pendulum.Duration(**DEFAULT_JWT_REFRESH_LIFESPAN)
            ).int_timestamp
            assert token_data['id'] == the_dude.id
            assert token_data['rls'] == 'admin,operator'
            assert token_data['duder'] == 'brief'
            assert token_data['el_duderino'] == 'not brief'

        with pytest.raises(ClaimCollisionError) as err_info:
            guard.encode_jwt_token(the_dude, exp='nice marmot')
        expected_message = 'custom claims collide'
        assert expected_message in str(err_info.value)

    def test_encode_eternal_jwt_token(self, app, user_class):
        """
        This test verifies that the encode_eternal_jwt_token correctly encodes
        jwt data based on a user instance. Also verifies that the lifespan is
        set to the constant VITAM_AETERNUM
        """
        guard = Praetorian(app, user_class)
        the_dude = user_class(
            username='TheDude',
            password=guard.hash_password('abides'),
            roles='admin,operator',
        )
        moment = pendulum.parse('2017-05-21 18:39:55')
        with freezegun.freeze_time(moment):
            token = guard.encode_eternal_jwt_token(the_dude)
            token_data = jwt.decode(
                token, guard.encode_key, algorithms=guard.allowed_algorithms,
            )
            assert token_data['iat'] == moment.int_timestamp
            assert token_data['exp'] == (
                moment + VITAM_AETERNUM
            ).int_timestamp
            assert token_data['rf_exp'] == (
                moment + VITAM_AETERNUM
            ).int_timestamp
            assert token_data['id'] == the_dude.id

    def test_refresh_jwt_token(
            self, app, db,
            user_class, validating_user_class,
    ):
        """
        This test::
            * verifies that the refresh_jwt_token properly generates
              a refreshed jwt token.
            * ensures that a token who's access permission has not expired may
              not be refreshed.
            * ensures that a token who's access permission has expired must not
              have an expired refresh permission for a new token to be issued.
            * ensures that if an override_access_lifespan argument is supplied
              that it is used instead of the instance's access_lifespan.
            * ensures that the access_lifespan may not exceed the refresh
              lifespan.
            * ensures that if the user_class has the instance method
              validate(), it is called an any exceptions it raises are wrapped
              in an InvalidUserError.
            * verifies that if a user is no longer identifiable that a
              MissingUserError is raised
            * verifies that any custom claims in the original token's
              payload are also packaged in the new token's payload
        """
        guard = Praetorian(app, user_class)
        the_dude = user_class(
            username='TheDude',
            password=guard.hash_password('abides'),
            roles='admin,operator',
        )
        db.session.add(the_dude)
        db.session.commit()

        moment = pendulum.parse('2017-05-21 18:39:55')
        with freezegun.freeze_time(moment):
            token = guard.encode_jwt_token(the_dude)
        new_moment = (
            pendulum.parse('2017-05-21 18:39:55') +
            pendulum.Duration(**DEFAULT_JWT_ACCESS_LIFESPAN) +
            pendulum.Duration(minutes=1)
        )
        with freezegun.freeze_time(new_moment):
            new_token = guard.refresh_jwt_token(token)
            new_token_data = jwt.decode(
                new_token, guard.encode_key,
                algorithms=guard.allowed_algorithms,
            )
            assert new_token_data['iat'] == new_moment.int_timestamp
            assert new_token_data['exp'] == (
                new_moment + pendulum.Duration(**DEFAULT_JWT_ACCESS_LIFESPAN)
            ).int_timestamp
            assert new_token_data['rf_exp'] == (
                moment + pendulum.Duration(**DEFAULT_JWT_REFRESH_LIFESPAN)
            ).int_timestamp
            assert new_token_data['id'] == the_dude.id
            assert new_token_data['rls'] == 'admin,operator'

        moment = pendulum.parse('2017-05-21 18:39:55')
        with freezegun.freeze_time(moment):
            token = guard.encode_jwt_token(the_dude)
        new_moment = (
            pendulum.parse('2017-05-21 18:39:55') +
            pendulum.Duration(**DEFAULT_JWT_ACCESS_LIFESPAN) +
            pendulum.Duration(minutes=1)
        )
        with freezegun.freeze_time(new_moment):
            new_token = guard.refresh_jwt_token(
                token,
                override_access_lifespan=pendulum.Duration(hours=2),
            )
            new_token_data = jwt.decode(
                new_token, guard.encode_key,
                algorithms=guard.allowed_algorithms,
            )
            assert new_token_data['exp'] == (
                new_moment + pendulum.Duration(hours=2)
            ).int_timestamp

        moment = pendulum.parse('2017-05-21 18:39:55')
        with freezegun.freeze_time(moment):
            token = guard.encode_jwt_token(
                the_dude,
                override_refresh_lifespan=pendulum.Duration(hours=2),
                override_access_lifespan=pendulum.Duration(minutes=30),
            )
        new_moment = moment + pendulum.Duration(minutes=31)
        with freezegun.freeze_time(new_moment):
            new_token = guard.refresh_jwt_token(
                token,
                override_access_lifespan=pendulum.Duration(hours=2),
            )
            new_token_data = jwt.decode(
                new_token, guard.encode_key,
                algorithms=guard.allowed_algorithms,
            )
            assert new_token_data['exp'] == new_token_data['rf_exp']

        expiring_interval = (
            pendulum.Duration(**DEFAULT_JWT_ACCESS_LIFESPAN) +
            pendulum.Duration(minutes=1)
        )
        validating_guard = Praetorian(app, validating_user_class)
        brandt = validating_user_class(
            username='brandt',
            password=guard.hash_password("can't watch"),
            is_active=True,
        )
        db.session.add(brandt)
        db.session.commit()
        moment = pendulum.parse('2017-05-21 18:39:55')
        with freezegun.freeze_time(moment):
            token = guard.encode_jwt_token(brandt)
        new_moment = moment + expiring_interval
        with freezegun.freeze_time(new_moment):
            validating_guard.refresh_jwt_token(token)
        brandt.is_active = False
        db.session.merge(brandt)
        db.session.commit()
        new_moment = new_moment + expiring_interval
        with freezegun.freeze_time(new_moment):
            with pytest.raises(InvalidUserError) as err_info:
                validating_guard.refresh_jwt_token(token)
        expected_message = 'The user is not valid or has had access revoked'
        assert expected_message in str(err_info.value)

        expiring_interval = (
            pendulum.Duration(**DEFAULT_JWT_ACCESS_LIFESPAN) +
            pendulum.Duration(minutes=1)
        )
        guard = Praetorian(app, user_class)
        bunny = user_class(
            username='bunny',
            password=guard.hash_password("can't blow that far"),
        )
        db.session.add(bunny)
        db.session.commit()
        moment = pendulum.parse('2017-05-21 18:39:55')
        with freezegun.freeze_time(moment):
            token = guard.encode_jwt_token(bunny)
        db.session.delete(bunny)
        db.session.commit()
        new_moment = moment + expiring_interval
        with freezegun.freeze_time(new_moment):
            with pytest.raises(MissingUserError) as err_info:
                validating_guard.refresh_jwt_token(token)
        expected_message = 'Could not find the requested user'
        assert expected_message in str(err_info.value)

        moment = pendulum.parse('2018-08-14 09:05:24')
        with freezegun.freeze_time(moment):
            token = guard.encode_jwt_token(
                the_dude,
                duder='brief',
                el_duderino='not brief',
            )
        new_moment = (
            pendulum.parse('2018-08-14 09:05:24') +
            pendulum.Duration(**DEFAULT_JWT_ACCESS_LIFESPAN) +
            pendulum.Duration(minutes=1)
        )
        with freezegun.freeze_time(new_moment):
            new_token = guard.refresh_jwt_token(token)
            new_token_data = jwt.decode(
                new_token, guard.encode_key,
                algorithms=guard.allowed_algorithms,
            )
            assert new_token_data['iat'] == new_moment.int_timestamp
            assert new_token_data['exp'] == (
                new_moment + pendulum.Duration(**DEFAULT_JWT_ACCESS_LIFESPAN)
            ).int_timestamp
            assert new_token_data['rf_exp'] == (
                moment + pendulum.Duration(**DEFAULT_JWT_REFRESH_LIFESPAN)
            ).int_timestamp
            assert new_token_data['id'] == the_dude.id
            assert new_token_data['rls'] == 'admin,operator'
            assert new_token_data['duder'] == 'brief'
            assert new_token_data['el_duderino'] == 'not brief'

    def test_read_token_from_header(self, app, db, user_class, client):
        """
        This test verifies that a token may be properly read from a flask
        request's header using the configuration settings for header name and
        type
        """
        guard = Praetorian(app, user_class)
        the_dude = user_class(
            username='TheDude',
            password=guard.hash_password('abides'),
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

    def test_pack_header_for_user(self, app, user_class):
        """
        This test::
          * verifies that the pack_header_for_user method can be used to
            package a token into a header dict for a specified user
          * verifies that custom claims may be packaged as well
        """
        guard = Praetorian(app, user_class)
        the_dude = user_class(
            username='TheDude',
            password=guard.hash_password('abides'),
            roles='admin,operator',
        )

        moment = pendulum.parse('2017-05-21 18:39:55')
        with freezegun.freeze_time(moment):
            header_dict = guard.pack_header_for_user(the_dude)
            token_header = header_dict.get(DEFAULT_JWT_HEADER_NAME)
            assert token_header is not None
            token = token_header.replace(DEFAULT_JWT_HEADER_TYPE, '')
            token = token.strip()
            token_data = jwt.decode(
                token, guard.encode_key, algorithms=guard.allowed_algorithms,
            )
            assert token_data['iat'] == moment.int_timestamp
            assert token_data['exp'] == (
                moment + pendulum.Duration(**DEFAULT_JWT_ACCESS_LIFESPAN)
            ).int_timestamp
            assert token_data['rf_exp'] == (
                moment + pendulum.Duration(**DEFAULT_JWT_REFRESH_LIFESPAN)
            ).int_timestamp
            assert token_data['id'] == the_dude.id
            assert token_data['rls'] == 'admin,operator'

        moment = pendulum.parse('2017-05-21 18:39:55')
        override_access_lifespan = pendulum.Duration(minutes=1)
        override_refresh_lifespan = pendulum.Duration(hours=1)
        with freezegun.freeze_time(moment):
            header_dict = guard.pack_header_for_user(
                the_dude,
                override_access_lifespan=override_access_lifespan,
                override_refresh_lifespan=override_refresh_lifespan,
            )
            token_header = header_dict.get(DEFAULT_JWT_HEADER_NAME)
            assert token_header is not None
            token = token_header.replace(DEFAULT_JWT_HEADER_TYPE, '')
            token = token.strip()
            token_data = jwt.decode(
                token, guard.encode_key, algorithms=guard.allowed_algorithms,
            )
            assert token_data['exp'] == (
                moment + override_access_lifespan
            ).int_timestamp
            assert token_data['rf_exp'] == (
                moment + override_refresh_lifespan
            ).int_timestamp
            assert token_data['id'] == the_dude.id

        moment = pendulum.parse('2018-08-14 09:08:39')
        with freezegun.freeze_time(moment):
            header_dict = guard.pack_header_for_user(
                the_dude,
                duder='brief',
                el_duderino='not brief',
            )
            token_header = header_dict.get(DEFAULT_JWT_HEADER_NAME)
            assert token_header is not None
            token = token_header.replace(DEFAULT_JWT_HEADER_TYPE, '')
            token = token.strip()
            token_data = jwt.decode(
                token, guard.encode_key, algorithms=guard.allowed_algorithms,
            )
            assert token_data['iat'] == moment.int_timestamp
            assert token_data['exp'] == (
                moment + pendulum.Duration(**DEFAULT_JWT_ACCESS_LIFESPAN)
            ).int_timestamp
            assert token_data['rf_exp'] == (
                moment + pendulum.Duration(**DEFAULT_JWT_REFRESH_LIFESPAN)
            ).int_timestamp
            assert token_data['id'] == the_dude.id
            assert token_data['rls'] == 'admin,operator'
            assert token_data['duder'] == 'brief'
            assert token_data['el_duderino'] == 'not brief'

    def test_registration_email(
        self, app, user_class, db, clean_flask_app_config
    ):
        """
        This test verifies email based registration functions as expected.
        This includes sending messages with valid time expiring JWT tokens
           and ensuring the body matches the expected body, as well
           as token validation.
        """

        _pwd = dirname(dirname(abspath(__file__)))
        here = _pwd + '/flask_praetorian/templates'
        tmpl_file = here + '/registration_email.html'
        with open(tmpl_file) as _template:
            tmpl = Template(_template.read())

        # generate (w/o sending) a notification email and match it to our own
        app.config['TESTING'] = True
        app.config['PRAETORIAN_EMAIL_TEMPLATE'] = tmpl_file
        app.config['PRAETORIAN_CONFIRMATION_ENDPOINT'] = 'unprotected'

        default_guard = Praetorian(app, user_class)

        # create our default test user
        the_dude = user_class(
            username='TheDude',
            email='the@dude.com',
            password=default_guard.hash_password('abides'),
        )
        db.session.add(the_dude)
        db.session.commit()

        with app.mail.record_messages() as outbox:
            notify = default_guard.send_registration_email(user=the_dude)
            the_dude.token = notify['token']

            # test our own interpretation and what we got back from flask_mail
            assert tmpl.render(the_dude.__dict__).strip() in notify['message']
            assert notify['message'] == outbox[0].html

            # test we got an expected confirmation URI
            assert notify['confirmation_uri'].endswith(
                'unprotected/{}'.format(notify['token'])
            )

            # test for no errors
            assert not notify['result']

        # test our token is good
        assert default_guard.validate_confirmation(notify['token'])

        # test a bad token is treated as bad
        with pytest.raises(PraetorianError):
            default_guard.validate_confirmation('not a token')

        # put away your toys
        db.session.delete(the_dude)
        db.session.commit()

    def test_registration_confirmation(
        self,
        app,
        user_class,
        db,
        clean_flask_app_config
    ):
        """
        This test verifies email based registration confirmations.
        Tests against invalid tokens, expired tokens, and
           valid tokens are tested.
        """

        app.config['TESTING'] = True
        app.config['PRAETORIAN_CONFIRMATION_ENDPOINT'] = 'reg_confirm'

        default_guard = Praetorian(app, user_class)

        # create our default test user
        the_dude = user_class(
            username='TheDude',
            email='the@dude.com',
            password=default_guard.hash_password('abides'),
        )
        db.session.add(the_dude)
        db.session.commit()

        """
           test to ensure a regular registration token is good
        """
        reg_token = default_guard.encode_jwt_token(
            the_dude,
            bypass_user_check=True
        )

        # ensure we got a token
        assert reg_token
        # ensure the user ID in the token is 1 (we only have one user)
        assert default_guard.validate_confirmation(reg_token)['id'] == 1

        """
           test to ensure a bad (nonsense) token fails validation
        """
        with pytest.raises(PraetorianError):
            default_guard.validate_confirmation('not a token')

        """
           test to ensure a registration token that is expired
               sets off an 'ExpiredAccessError' exception
        """
        expired_reg_token = default_guard.encode_jwt_token(
            the_dude,
            bypass_user_check=True,
            override_access_lifespan=pendulum.Duration(seconds=1),
        )

        assert expired_reg_token
        import time
        time.sleep(2)
        with pytest.raises(ExpiredAccessError):
            assert default_guard.validate_confirmation(expired_reg_token)

        # put away your toys
        db.session.delete(the_dude)
        db.session.commit()

    def test_validate_and_update(self, app, user_class, db):
        """
        This test verifies that Praetorian encrypts passwords using the scheme
        specified by the HASH_SCHEME setting. If no scheme is supplied, the
        test verifies that the default scheme is used. Otherwise, the test
        verifies that the encrypted password matches the supplied scheme.
        """

        default_guard = Praetorian(app, user_class)
        pbkdf2_sha512_password = default_guard.hash_password('pbkdf2_sha512')

        # create our default test user
        the_dude = user_class(
            username='TheDude',
            email='the@dude.com',
            password=pbkdf2_sha512_password,
        )
        db.session.add(the_dude)
        db.session.commit()

        """
        Test the current password is hashed with PRAETORIAN_HASH_SCHEME
        """
        assert default_guard.verify_and_update(user=the_dude)

        """
        Test a password hashed with something other than
            PRAETORIAN_HASH_ALLOWED_SCHEME triggers an Exception.
        """
        app.config['PRAETORIAN_HASH_SCHEME'] = 'bcrypt'
        default_guard = Praetorian(app, user_class)
        bcrypt_password = default_guard.hash_password('bcrypt_password')
        the_dude.password = bcrypt_password

        del app.config['PRAETORIAN_HASH_SCHEME']
        app.config['PRAETORIAN_HASH_DEPRECATED_SCHEMES'] = ['bcrypt']
        default_guard = Praetorian(app, user_class)
        with pytest.raises(LegacyScheme):
            default_guard.verify_and_update(the_dude)

        """
        Test a password hashed with something other than
            PRAETORIAN_HASH_SCHEME, and supplied good password
            gets the user entry's password updated and saved.
        """
        the_dude_old_password = the_dude.password
        updated_dude = default_guard.verify_and_update(
            the_dude,
            'bcrypt_password'
        )
        assert updated_dude.password != the_dude_old_password

        """
        Test a password hashed with something other than
            PRAETORIAN_HASH_SCHEME, and supplied bad password
            gets an Exception raised.
        """
        the_dude.password = bcrypt_password
        with pytest.raises(AuthenticationError):
            default_guard.verify_and_update(user=the_dude, password='failme')

        # put away your toys
        db.session.delete(the_dude)
        db.session.commit()

    def test_authenticate_validate_and_update(self, app, user_class, db):
        """
        This test verifies the authenticate() function, when altered by
        either 'PRAETORIAN_HASH_AUTOUPDATE' or 'PRAETORIAN_HASH_AUTOTEST'
        performs the authentication and the required subaction.
        """

        default_guard = Praetorian(app, user_class)
        pbkdf2_sha512_password = default_guard.hash_password('start_password')

        # create our default test user
        the_dude = user_class(
            username='TheDude',
            email='the@dude.com',
            password=pbkdf2_sha512_password,
        )
        db.session.add(the_dude)
        db.session.commit()

        """
        Test the existing model as a baseline
        """
        assert default_guard.authenticate(the_dude.username, 'start_password')

        """
        Test the existing model with a bad password as a baseline
        """
        with pytest.raises(AuthenticationError):
            default_guard.authenticate(the_dude.username, 'failme')

        """
        Test the updated model with a bad hash scheme and AUTOTEST enabled.
        Should raise and exception
        """
        app.config['PRAETORIAN_HASH_SCHEME'] = 'bcrypt'
        default_guard = Praetorian(app, user_class)
        bcrypt_password = default_guard.hash_password('bcrypt_password')
        the_dude.password = bcrypt_password

        del app.config['PRAETORIAN_HASH_SCHEME']
        app.config['PRAETORIAN_HASH_DEPRECATED_SCHEMES'] = ['bcrypt']
        app.config['PRAETORIAN_HASH_AUTOTEST'] = True
        default_guard = Praetorian(app, user_class)
        with pytest.raises(LegacyScheme):
            default_guard.authenticate(the_dude.username, 'bcrypt_password')

        """
        Test the updated model with a bad hash scheme and AUTOUPDATE enabled.
        Should return an updated user object we need to save ourselves.
        """
        the_dude_old_password = the_dude.password
        app.config['PRAETORIAN_HASH_AUTOUPDATE'] = True
        default_guard = Praetorian(app, user_class)
        updated_dude = default_guard.authenticate(
            the_dude.username,
            'bcrypt_password'
        )
        assert updated_dude.password != the_dude_old_password

        # put away your toys
        db.session.delete(the_dude)
        db.session.commit()
