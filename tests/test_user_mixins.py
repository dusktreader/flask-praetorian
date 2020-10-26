import flask_praetorian
import flask_praetorian.exceptions
import pytest


class TestSQLAlchemyUserMixin:
    def test_basic(self, app, db, mixin_user_class):
        mixin_guard = flask_praetorian.Praetorian(app, mixin_user_class)
        the_dude = mixin_user_class(
            username="TheDude",
            password=mixin_guard.hash_password("abides"),
        )
        db.session.add(the_dude)
        db.session.commit()
        assert mixin_guard.authenticate("TheDude", "abides") == the_dude
        with pytest.raises(flask_praetorian.exceptions.MissingUserError):
            mixin_guard.authenticate("TheBro", "abides")
        with pytest.raises(flask_praetorian.exceptions.AuthenticationError):
            mixin_guard.authenticate("TheDude", "is_undudelike")
        db.session.delete(the_dude)
        db.session.commit()
        mixin_guard
