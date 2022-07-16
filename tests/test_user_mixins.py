import sanic_praetorian
import sanic_praetorian.exceptions
import pytest


class TestUserMixin:
    async def test_basic(self, app, mixin_user_class, user_class, default_guard, mock_users):
        mixin_guard = sanic_praetorian.Praetorian(app, mixin_user_class)

        the_dude = await mock_users(username="the_dude", password="abides", guard_name=mixin_guard, class_name=mixin_user_class)

        assert await mixin_guard.authenticate("the_dude", "abides") == the_dude
        with pytest.raises(sanic_praetorian.exceptions.AuthenticationError):
            await mixin_guard.authenticate("the_bro", "abides")
        with pytest.raises(sanic_praetorian.exceptions.AuthenticationError):
            await mixin_guard.authenticate("the_dude", "is_undudelike")
        await the_dude.delete()

        default_guard.init_app(app, user_class)
