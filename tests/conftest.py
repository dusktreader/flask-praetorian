import pytest

import flask_praetorian

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_praetorian import Praetorian
from flask_mail import Mail


_db = SQLAlchemy()
_guard = Praetorian()
_mail = Mail()


class User(_db.Model):
    """
    Provides a basic user model for use in the tests
    """
    id = _db.Column(_db.Integer, primary_key=True)
    username = _db.Column(_db.Text, unique=True)
    password = _db.Column(_db.Text)
    email = _db.Column(_db.Text)
    roles = _db.Column(_db.Text)

    @property
    def rolenames(self):
        try:
            return self.roles.split(',')
        except Exception:
            return []

    @classmethod
    def lookup(cls, username):
        return cls.query.filter_by(username=username).one_or_none()

    @classmethod
    def identify(cls, id):
        return cls.query.get(id)

    @property
    def identity(self):
        return self.id


class ValidatingUser(User):
    __tablename__ = 'validating_users'
    id = _db.Column(_db.Integer, primary_key=True)
    username = _db.Column(_db.Text, unique=True)
    password = _db.Column(_db.Text)
    roles = _db.Column(_db.Text)
    is_active = _db.Column(_db.Boolean, default=True, server_default='true')

    def is_valid(self):
        return self.is_active

    __mapper_args__ = {'concrete': True}


@pytest.fixture(scope='session')
def app(tmpdir_factory):
    """
    Initializes the flask app for the test suite. Also prepares a set of routes
    to use in testing with varying levels of protections
    """
    app = Flask(__name__)
    # In order to process more requests after initializing the app,
    # we have to set degug to false so that it will not check to see if there
    # has already been a request before a setup function
    app.debug = False
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'top secret'

    _guard.init_app(app, User)

    _mail.init_app(app)
    app.mail = _mail

    db_path = tmpdir_factory.mktemp(
        'flask-praetorian-test',
        numbered=True
    ).join('sqlite.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + str(db_path)
    """
    Set to False as we don't use it, and to suppress warnings,
        as documented by SQLALCHEMY.
    """
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    _db.init_app(app)
    with app.app_context():
        _db.create_all()

    @app.route('/unprotected')
    def unprotected():
        return jsonify(message='success')

    @app.route('/protected')
    @flask_praetorian.auth_required
    def protected():
        return jsonify(message='success')

    @app.route('/protected_admin_required')
    @flask_praetorian.auth_required
    @flask_praetorian.roles_required('admin')
    def protected_admin_required():
        return jsonify(message='success')

    @app.route('/protected_admin_and_operator_required')
    @flask_praetorian.auth_required
    @flask_praetorian.roles_required('admin', 'operator')
    def protected_admin_and_operator_required():
        return jsonify(message='success')

    @app.route('/protected_admin_and_operator_accepted')
    @flask_praetorian.auth_required
    @flask_praetorian.roles_accepted('admin', 'operator')
    def protected_admin_and_operator_accepted():
        return jsonify(message='success')

    @app.route('/undecorated_admin_required')
    @flask_praetorian.roles_required('admin')
    def undecorated_admin_required():
        return jsonify(message='success')

    @app.route('/undecorated_admin_accepted')
    @flask_praetorian.roles_accepted('admin')
    def undecorated_admin_accepted():
        return jsonify(message='success')

    @app.route('/reversed_decorators')
    @flask_praetorian.roles_required('admin', 'operator')
    @flask_praetorian.auth_required
    def reversed_decorators():
        return jsonify(message='success')

    @app.route('/registration_confirmation')
    def reg_confirm():
        return jsonify(message='fuck')

    return app


@pytest.fixture(scope='session')
def user_class():
    """
    This fixture simply fetches the user_class to be used in testing
    """
    return User


@pytest.fixture(scope='session')
def validating_user_class():
    """
    This fixture simply fetches the validating user_class to be used in testing
    """
    return ValidatingUser


@pytest.fixture(scope='session')
def db():
    """
    This fixture simply fetches the db instance to be used in testing
    """
    return _db


@pytest.fixture(autouse=True)
def db_setup(app, db):
    """
    Prepares the testing database to hold testing data by creating the schema
    anew for each test function and then dropping all data after the test runs
    """
    with app.app_context():
        db.create_all()
        db.session.commit()
        yield
        db.drop_all()
        db.session.commit()


@pytest.fixture(scope='session')
def default_guard():
    """
    This fixtures fetches the flask-praetorian instance to be used in testing
    """
    return _guard


@pytest.fixture(scope='session')
def mail():
    """
    This fixture simply fetches the db instance to be used in testing
    """
    return _mail


@pytest.fixture(autouse=True)
def clean_flask_app_config(app):
    """
    This fixture ensures a clean `app.config` is available for each round
        of testing.
    """
    with app.app_context():
        stock_config = app.config.copy()
        yield
        app.config = stock_config.copy()
