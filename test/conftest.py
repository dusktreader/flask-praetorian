import pytest

import flask_praetorian

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_praetorian import Praetorian


_db = SQLAlchemy()


class User(_db.Model):
    id = _db.Column(_db.Integer, primary_key=True)
    username = _db.Column(_db.Text, unique=True)
    password = _db.Column(_db.Text)
    roles = _db.Column(_db.Text)

    @property
    def rolenames(self):
        try:
            return self.roles.split(',')
        except:
            return []

    @classmethod
    def lookup(cls, username):
        return cls.query.filter_by(username=username).one_or_none()

    @classmethod
    def identify(cls, id):
        return cls.query.get(id)


@pytest.fixture(scope='session')
def app(tmpdir_factory):
    app = Flask(__name__)
    app.debug = True
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'top secret'
    # TODO: Add the rest of the configuration stuff here

    db_path = tmpdir_factory.mktemp(
        'flask-praetorian-test',
        numbered=True
    ).join('sqlite.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + str(db_path)
    _db.init_app(app)
    with app.app_context():
        _db.create_all()

    @app.route('/unprotected')
    @flask_praetorian.roles_required('admin')
    def unprotected():
        return 'success'

    @app.route('/protected')
    @flask_praetorian.auth_required()
    def protected():
        return 'success'

    @app.route('/protected_admin_required')
    @flask_praetorian.auth_required()
    @flask_praetorian.roles_required('admin')
    def protected_admin_required():
        return 'success'

    @app.route('/protected_admin_and_operator_required')
    @flask_praetorian.auth_required()
    @flask_praetorian.roles_required('admin', 'operator')
    def protected_admin_and_operator_required():
        return 'success'

    @app.route('/protected_admin_and_operator_accepted')
    @flask_praetorian.auth_required()
    @flask_praetorian.roles_accepted('admin', 'operator')
    def protected_admin_and_operator_accepted():
        return 'success'

    return app


@pytest.fixture(scope='session')
def user_class():
    return User


@pytest.fixture(scope='session')
def db():
    return _db


@pytest.yield_fixture(autouse=True)
def db_setup(app, db):
    with app.app_context():
        db.create_all()
        db.session.commit()
        yield
        db.drop_all()
        db.session.commit()


@pytest.fixture(scope='session')
def default_guard(app, user_class):
    return Praetorian(app, user_class)
