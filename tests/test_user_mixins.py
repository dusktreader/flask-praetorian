import sanic_praetorian
import sanic_praetorian.exceptions
import pytest


class TestSQLAlchemyUserMixin:
    def test_basic(self, app, db_session, mixin_user_class, user_class, default_guard):
        mixin_guard = sanic_praetorian.Praetorian(app, mixin_user_class)
        the_dude = mixin_user_class(
            username="TheDude",
            password=mixin_guard.hash_password("abides"),
        )
        db_session.add(the_dude)
        db_session.commit()
        assert mixin_guard.authenticate("TheDude", "abides") == the_dude
        with pytest.raises(sanic_praetorian.exceptions.AuthenticationError):
            mixin_guard.authenticate("TheBro", "abides")
        with pytest.raises(sanic_praetorian.exceptions.AuthenticationError):
            mixin_guard.authenticate("TheDude", "is_undudelike")
        db_session.delete(the_dude)
        db_session.commit()
        default_guard.init_app(app, user_class)
