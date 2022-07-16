from sys import path as sys_path
from os import path as os_path
from webbrowser import get
sys_path.insert(0, os_path.join(os_path.dirname(os_path.abspath(__file__)), ".."))

import pytest
import copy

from tortoise import Tortoise, run_async
from sanic.log import logger
from sanic_testing.reusable import ReusableClient
from sanic.exceptions import SanicException

from models import ValidatingUser, MixinUser, User
from server import create_app, _guard, _mail

import nest_asyncio
nest_asyncio.apply()


# Hack for using the same DB instance directly and within the app
async def init(db_path=None):
    await Tortoise.init(
        db_url=db_path,
        modules={'models': ["models"]},
    )
    await Tortoise.generate_schemas()


@pytest.fixture
def app(tmpdir_factory):

    db_path = tmpdir_factory.mktemp(
        "sanic-praetorian-test",
        numbered=True,
    ).join("sqlite.db")
    logger.info(f'Using DB_Path: {str(db_path)}')
    run_async(init(db_path=f'sqlite://{str(db_path)}'))

    sanic_app = create_app(db_path=f'sqlite://{str(db_path)}')
    # Hack to do some poor code work in the app for some workarounds for broken fucntions under pytest
    sanic_app.config['PYTESTING'] = True

    sanic_app.config.SUPPRESS_SEND = 1 # Don't actually send mails
    _mail.init_app(sanic_app)

    yield sanic_app
    sanic_app = None


@pytest.fixture(scope="session")
def user_class():
    """
    This fixture simply fetches the user_class to be used in testing
    """
    return User


@pytest.fixture(scope="session")
def mixin_user_class():
    """
    This fixture simply fetches the mixin user_class to be used in testing
    """
    return MixinUser


@pytest.fixture(scope="session")
def validating_user_class():
    """
    This fixture simply fetches the validating user_class to be used in testing
    """
    return ValidatingUser


@pytest.fixture(autouse=True)
#def db_setup(app, db_session):
def db_setup(app):
    """
    Prepares the testing database to hold testing data by creating the schema
    anew for each test function and then dropping all data after the test runs
    """
    """
    with app.app_context():
        db.create_all()
        db.session.commit()
        yield
        db.drop_all()
        db.session.commit()
    """
    pass


@pytest.fixture(scope="session")
def default_guard():
    """
    This fixtures fetches the sanic-praetorian instance to be used in testing
    """
    return _guard


@pytest.fixture(scope="session")
def mail():
    """
    This fixture simply fetches the db instance to be used in testing
    """
    return _mail


@pytest.fixture(autouse=True)
def clean_sanic_app_config(app):
    """
    This fixture ensures a clean `app.config` is available for each round
        of testing.
    """
    """
    with app.app_context():
        stock_config = app.config.copy()
        yield
        app.config = stock_config.copy()
    """
    stock_config = copy.copy(app.config)
    yield
    app.config = copy.copy(stock_config)
    pass


@pytest.fixture
def client(app):
    _client = ReusableClient(app, host='127.0.0.1', port='8000')
    with _client:
        yield _client


@pytest.fixture(autouse=True)
def use_cookie(app, default_guard):
    class withCookie:
        guard = default_guard
        #_client = ReusableClient(app, host='127.0.0.1', port='8000')
        _client = app.test_client
        server_name = "localhost.localdomain"

        def __init__(self, token):
            self.token = token

        def __enter__(self):
            self._client.set_cookie(
                self.server_name,
                self.guard.cookie_name,
                self.token,
                expires=None,
            )
            return self

        def __exit__(self, *_):
            self._client.delete_cookie(
                self.server_name, self.guard.cookie_name
            )

    return withCookie


@pytest.fixture()
def mock_users(user_class, default_guard):

    logger.critical('Mock_Users has been called!')
    async def _get_user(username: str = None, 
                        class_name: object = user_class,
                        guard_name: object = default_guard,
                        **kwargs):
        if not username:
            raise SanicException("You must supply a valid test user name!")

        # Set a default password of `something_secure`, unless one is provided
        password = guard_name.hash_password(kwargs.get('password', 'something_secure'))
        if kwargs.get('password'):
            # If one is provided, and already a hash, use it instead
            if guard_name.pwd_ctx.identify(str(kwargs['password'])):
                password = kwargs['password']

        email=kwargs.get('email', f"praetorian_{username}@mock.com")

        # TODO: This is ugly, gotta be a nicer way
        if kwargs.get('id'):
            return await class_name.create(
                username=username,
                email=email,
                password=password,
                roles=kwargs.get('roles', ""),
                is_active=kwargs.get('is_active', True),
                id=kwargs['id'],
            )
        else:
            return await class_name.create(
                username=username,
                email=email,
                password=password,
                roles=kwargs.get('roles', ""),
                is_active=kwargs.get('is_active', True),
            )

    
    return _get_user