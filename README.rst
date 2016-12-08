******************
 flask-praetorian
******************

.. contents:: Table of Contents
   :depth: 1

Overview
========

API security should be strong, simple, and precise like a Roman Legionary.
This package aims to provide that. Using `JWT <https://jwt.io/>`_ as
implemented by `Flask-JWT <https://pythonhosted.org/Flask-JWT/>`_,
flask_praetorian uses a very simple interface to make sure that the users
accessing your API's endpoints are provisioned with the correct roles for
access.

This project was heavily influenced by
`Flask-Security <https://pythonhosted.org/Flask-Security/>`_, but intends
to supply only essential functionality. Instead of trying to anticipate the
needs of all users, flask-praetorian will provide a simple and secure mechanism
to provide security for APIs specifically.

The flask-praetorian package can be used to:

* Encrypt (hash) passwords for storing in your database
* Verify plaintext passwords against the encrypted, stored versions
* Generate authorization tokens using a ``/auth`` api endpoint
* Check requests to secured endpoints for authorized tokens
* Ensure that the users associated with tokens have necessary roles for access

All of this is provided in a very simple to confiure and initialize flask
extension. Though simple, the security provided by flask-praetorian is strong
due to the usage of the proven security technology of JWT
and python's `PassLib <http://pythonhosted.org/passlib/>`_ package.

Installation
============

This package is not yet available on PyPi, so you will need to clone it from
github prior to installation:

Install with **pip**::

$ git clone https://github.com/dusktreader/flask-praetorian.git
$ pip install flask-praetorian

.. note::

    flask-praetorian does not support distutils or setuptools because the
    author has very strong feelings about python packaging and the role pip
    plays in taking us into a bright new future of standardized and usable
    python packaging

Quickstart
==========

This is a minimal example of how to use the flask-praetorian decorators:

.. code-block:: python

    import flask
    import tempfile
    import flask_sqlalchemy
    import flask_praetorian

    db = flask_sqlalchemy.SQLAlchemy()
    guard = flask_praetorian.Praetorian()


    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.Text, unique=True)
        password = db.Column(db.Text)
        roles = db.Column(db.Text)

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


    app = flask.Flask(__name__)
    app.debug = True
    app.config['SECRET_KEY'] = 'top secret'

    guard.init_app(app, User)

    local_database = tempfile.NamedTemporaryFile(prefix='local', suffix='.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(local_database)
    db.init_app(app)
    with app.app_context():
        db.create_all()
        db.session.add(User(
            username='TheDude',
            password=guard.encrypt_password('abides'),
        ))
        db.session.add(User(
            username='Walter',
            password=guard.encrypt_password('calmerthanyouare'),
            roles='admin'
        ))
        db.session.add(User(
            username='Donnie',
            password=guard.encrypt_password('iamthewalrus'),
            roles='operator'
        ))
        db.session.add(User(
            username='Maude',
            password=guard.encrypt_password('andthorough'),
            roles='operator,admin'
        ))
        db.session.commit()


    @app.route('/')
    def root():
        return 'root endpoint'


    @app.route('/protected')
    @flask_praetorian.auth_required()
    def protected():
        return 'protected endpoint'


    @app.route('/protected_admin_required')
    @flask_praetorian.auth_required()
    @flask_praetorian.roles_required('admin')
    def protected_admin_required():
        return 'protected_admin_required endpoint'


    @app.route('/protected_admin_accepted')
    @flask_praetorian.auth_required()
    @flask_praetorian.roles_accepted('admin', 'operator')
    def protected_admin_and_operator_accepted():
        return 'protected_admin_accepted endpoint'


    if __name__ == '__main__':
        app.run()

The above code can be found ``example/basic.py``.  The server can be started by
calling::

$ python example/basic.py

Once the server is up and running, you can login and get an auth token
by POSTing to the '/auth' endpoint with a body containing your username and
password::

    POST /auth HTTP/1.1
    Host: localhost:5000
    Content-Type: application/json
    {
        "username": "TheDude",
        "password": "abides"
    }

The response will have a json body containing the token::

    HTTP/1.1 200 OK
    Content-Type: application/json
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZGVudGl0eSI6MSwiaWF0IjoxNDQ0OTE3NjQwLCJuYmYiOjE0NDQ5MTc2NDAsImV4cCI6MTQ0NDkxNzk0MH0.KPmI6WSjRjlpzecPvs3q_T3cJQvAgJvaQAPtk1abC_E"
    }

This token can then be used to make requests against protected endpoints::
Once you have provisioned a token, you can try out the various endpoints that
were created above by include the token in the request header like soo::

    GET /protected HTTP/1.1
    Authorization: JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZGVudGl0eSI6MSwiaWF0IjoxNDQ0OTE3NjQwLCJuYmYiOjE0NDQ5MTc2NDAsImV4cCI6MTQ0NDkxNzk0MH0.KPmI6WSjRjlpzecPvs3q_T3cJQvAgJvaQAPtk1abC_E

You can try out the different endpoints with different users provisioned above
to see how the role constraining decorators from flask-praetorian work.

flask-praetorian Developer Guide
================================

This developer guide will help you get started on working on flask-praetorian
in a development environment so that you can add features and run tests

Dependencies
------------

* python3
* virtualenv

Setup
-----

Create a virtualenv
...................

You should set up your virtualenv using python3::

$ virtualenv --python=python3 env
$ source env/bin/activate

Install the package for development
...................................

In order to install the package for development and to include all its
dependencies (via pip), execute this command::

$ pip install -e .[dev]

The full list of dependencies can be found in ``setup.py``

Functional Requirements
-----------------------

The user_class
..............

The ``user_class`` argument supplied during initialization represents the
class that should be used to check for authorization for decorated routes. The
class itself may be implemented in any way that you see fit. It must, howerver,
satisfy the following requirements:

* Provide a ``lookup`` class method that:

  * should take a single argument of the name of the user

  * should return an instance of the ``user_class`` or ``None``

* Provide an ``identify`` class method

  * should take a single argument of the unique id of the user

  * should return an instance of the ``user_class`` or ``None``

* Provide a ``rolenames`` instance attribute

  * should return a list of string roles assigned to the user

* Provide a ``password`` instance attribute

  * should return the hashed password assigned to the user

Although the example given in this readme uses a SQLAlchemy model for the
userclass, this is not a requirement.

Running tests
=============

Invokation
----------

This project uses `pytest <http://doc.pytest.org/en/latest/>`_ for its unit
testing.

Tests are executed by invoking pytest directly from the root of the project::

$ py.test -ra test

The ``-ra`` option is recommended as it will report skipped tests

Generating the documentation
----------------------------

Simply execute the following script within an active virtual environment::

  $ bin/generate-docs

This will generate html documentation in docs/build

In the future, we will probably add extra arguments that will allow generation
of pdf or latex output for the docs as well.

Adding further documentation
----------------------------

The majority of the automatically generated developer's guide is produced
from `python docstrings <https://www.python.org/dev/peps/pep-0257/>`_

This project uses the sphinx extension
`sphinx-apidoc <http://www.sphinx-doc.org/en/stable/man/sphinx-apidoc.html>`_
to generate help pages from the docstrings at the module, class, and function
level.

There are several `special keywords
<http://www.sphinx-doc.org/en/stable/domains.html#info-field-lists>`_
that can be added to docstrings that have
special significance for sphinx. The most useful of these are the ``:param:``
and ``:return:`` keywords.

Items can be added to the project-wide todo list and notes that is shown in the
/help endpoint

Here is an example method with marked up docstring:

.. code-block:: python

  def some_method(param1, param2):
      """
      This is a method that does stuff

      :param: param1: This is the first param
      :param: param2: This is the second param
      :return: A string that says 'yo'
      .. todo:: Make this method more awesomer
      .. note:: This is just a lame example
      """
      return 'yo'

Code Style
==========

This project uses the style constraints `described in pep8
<https://www.python.org/dev/peps/pep-0008/>`_

Please follow the style guide as stated. Also, please enforce the style guide
during code reviews.

Useful tools
------------

reStructuredText viewer
.......................

reStructuredText documents can be previewed as they are edited on your
workstation using a tool called `restview <https://mg.pov.lt/restview/>`_. It
is indispensible when updating this README.rst document or one of the templates
for the autognerated sphinx documentation.


flake8
......

The `flake8 tool <https://pypi.python.org/pypi/flake8>`_ is very useful for
checking for compliant code style. It can be easily installed through pip::

  $ pip install flake8

The flake8 tool is invoked by targeting a specific source directory::

  $ flake8 flask_praetorian

Particular directories and source files may also be targeted directly

vim Editor plugin
`````````````````

The `vim-flake8 <https://github.com/nvie/vim-flake8>`_ plugin for vim is very
useful for identifying style issues inside the vim editor. the ``vim-flake8``
plugin is most easily added by using
`pathogen <https://github.com/tpope/vim-pathogen>`_.

The following vim binding is useful to execute the flake8 check on write for
all python source files::

  # autocmd BufWritePost *.py call Flake8()

It is most useful to include that in your ``.vimrc`` file

