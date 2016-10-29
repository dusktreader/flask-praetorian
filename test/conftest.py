import pytest
import tempfile

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_praetorian import (
    Praetorian,
    PraetorianError,
    roles_required,
    roles_accepted,
)


@pytest.fixture(scope='session')
def app():
    app = Flask(__name__)
    app.debug = True
    app.config['SECRET_KEY'] = 'secret'
    app.config['TESTING'] = True
    # TODO: Add the rest of the configuration stuff here
    return app


@pytest.fixture(scope='session')
def security(app, tmpdir):
    (f, path) = tempfile.mkstemp(
        prefix='flask-praetorian-test-db',
        suffix='.db',
        dir=str(tmpdir),
    )

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + path
    db = SQLAlchemy(app)

    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.Text, unique=True)
        password = db.Column(db.Text)
        roles = db.Column(db.Text)

        @property
        def rolenames(self):
            return self.roles.split(',')

    with app.app_context():
        db.create_all()

    return Praetorian(app, User)
