import sanic_praetorian
import sanic_praetorian.exceptions
import pytest


class TestUserMixin:
    async def test_basic(self, app, mixin_user_class, user_class, default_guard):
        mixin_guard = sanic_praetorian.Praetorian(app, mixin_user_class)
        the_dude = await mixin_user_class.create(
            username="TheDude",
            password=mixin_guard.hash_password("abides"),
            email="thedude@praetorian"
        )
        assert await mixin_guard.authenticate("TheDude", "abides") == the_dude
        with pytest.raises(sanic_praetorian.exceptions.AuthenticationError):
            await mixin_guard.authenticate("TheBro", "abides")
        with pytest.raises(sanic_praetorian.exceptions.AuthenticationError):
            await mixin_guard.authenticate("TheDude", "is_undudelike")
        await the_dude.delete()

        default_guard.init_app(app, user_class)
