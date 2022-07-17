import sanic_praetorian
from sanic_praetorian.base import Praetorian
import sanic_praetorian.exceptions
import pytest


class TestUserMixin:
    async def test_basic(self, app, mixin_user_class, mock_users):
        mixin_guard = sanic_praetorian.Praetorian(app, mixin_user_class)

        the_dude = await mock_users(username="the_dude", password="abides", guard_name=mixin_guard, class_name=mixin_user_class)

        assert await mixin_guard.authenticate("the_dude", "abides") == the_dude
        with pytest.raises(sanic_praetorian.exceptions.AuthenticationError):
            await mixin_guard.authenticate("the_bro", "abides")
        with pytest.raises(sanic_praetorian.exceptions.AuthenticationError):
            await mixin_guard.authenticate("the_dude", "is_undudelike")
        await the_dude.delete()

    async def test_totp(self, app, totp_user_class, mock_users):
        totp_guard = sanic_praetorian.Praetorian(app, totp_user_class)

        the_dude = await mock_users(username="the_dude",
                                    password="abides",
                                    guard_name=totp_guard,
                                    class_name=totp_user_class,
                                    totp='mock')
        assert the_dude.totp == 'mock'
        assert app.config.get('PRAETORIAN_TOTP_ENFORCE', True) is True

        # good creds, missing TOTP
        with pytest.raises(sanic_praetorian.exceptions.AuthenticationError) as e:
            await totp_guard.authenticate("the_dude", "abides")
        assert e.type is sanic_praetorian.exceptions.TOTPRequired

        # bad creds
        with pytest.raises(sanic_praetorian.exceptions.AuthenticationError) as e:
            await totp_guard.authenticate("the_dude", "is_undudelike")
        assert e.type is not sanic_praetorian.exceptions.TOTPRequired

        # bad token
        with pytest.raises(sanic_praetorian.exceptions.AuthenticationError):
            await totp_guard.authenticate_totp("the_dude", 80085)

        # good creds, bad token
        with pytest.raises(sanic_praetorian.exceptions.AuthenticationError) as e:
            await totp_guard.authenticate("the_dude", "abides", 80085)
        assert e.type is not sanic_praetorian.exceptions.TOTPRequired

        # bad creds, bad token
        with pytest.raises(sanic_praetorian.exceptions.AuthenticationError) as e:
            await totp_guard.authenticate("the_dude", "is_undudelike", 80085)
        assert e.type is not sanic_praetorian.exceptions.TOTPRequired

        """
        Verify its ok to call `authenticate` w/o a `token`, for a required user,
            while `PRAETORIAN_TOTP_ENFORCE` is set to `False`
        """
        app.config.PRAETORIAN_TOTP_ENFORCE = False
        _totp_optional_guard = Praetorian(app, totp_user_class)
        # good creds, missing TOTP
        _optional_the_dude = await _totp_optional_guard.authenticate("the_dude", "abides")
        assert _optional_the_dude == the_dude

        await the_dude.delete()
