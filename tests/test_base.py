import pytest

from flask_praetorian import Praetorian
from flask_praetorian.exceptions import PraetorianError


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
        assert default_guard.pwd_ctx.identify(secret) == 'bcrypt'

        app.config['PRAETORIAN_HASH_SCHEME'] = 'pbkdf2_sha512'
        specified_guard = Praetorian(app, user_class)
        secret = specified_guard.encrypt_password('some password')
        assert specified_guard.pwd_ctx.identify(secret) == 'pbkdf2_sha512'

        app.config['PRAETORIAN_HASH_SCHEME'] = 'plaintext'
        dumb_guard = Praetorian(app, user_class)
        assert dumb_guard.encrypt_password('some password') == 'some password'

    def test_verify_passord(self, app, user_class):
        """
        This test verifies that the verify_password function can be used to
        successfully compare a raw password against its hashed version
        """
        # TODO: Add verify_and_update_support and testing
        default_guard = Praetorian(app, user_class)
        secret = default_guard.encrypt_password('some password')
        assert default_guard.verify_password('some password', secret)
        assert not default_guard.verify_password('not right', secret)

    def test__authenticate(self, app, user_class, db):
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

    def test__identity(self, app, user_class, db):
        """
        This test verifies that the _identity method can retrieve a User
        instance based on the user id supplied in the payload
        """
        default_guard = Praetorian(app, user_class)
        the_dude = user_class(
            id=9999,
            username='TheDude',
            password=default_guard.encrypt_password('abides'),
        )
        db.session.add(the_dude)
        db.session.commit()
        assert default_guard._identity({'identity': 9999}) == the_dude
        assert default_guard._identity({'identity': 7777}) is None
        db.session.delete(the_dude)
        db.session.commit()

    def test__validate_user_class(self, app, user_class):
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
