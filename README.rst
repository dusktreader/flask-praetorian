******************
 flask-praetorian
******************

.. contents:: Table of Contents
   :depth: 1

Overview
========

API security should be simple, precise, and powerful like a Roman Legionary.
This package aims to provide that. Using `JWT <https://jwt.io/>`_ as
implemented by the `Flask-JWT <https://pythonhosted.org/Flask-JWT/>`_,
flask_praetorian uses a very simple interface to make sure that the users
accessing your APIs endpoints are provisioned with the correct roles for
access.

This project was heavily influenced by
`Flask-Security <https://pythonhosted.org/Flask-Security/>`_, but intents
do supply only essential functionality. Instead of trying to anticipate the
needs of all users, flask-praetorian will provide a simple and secure mechanism
to provide security to your API.

Installation
============

This package is not yet available on PyPi, so you will need to clone it from
github prior to installation:

Install with *pip*::

    git clone https://github.com/dusktreader/flask-praetorian.git
    pip install flask-praetorian

Quickstart
==========

This is a minimal example of how to use the flask-praetorian decorators::

    import flask_jwt
    import flask_praetorian

    @app.route('/example_admin_required')
    @flask_jwt.jwt_required()
    @flask_praetorian.roles_required('admin')
    def route1():
        return 'success'

    @app.route('/example_admin_accepted')
    @flask_jwt.jwt_required()
    @flask_praetorian.roles_accepted('admin')
    def route1():
        return 'success'

Since flask-praetorian is a flask extension, it is initialized in the usual
manner. You must also supply the user class that will be used to for
authorization::

    import flask_praetorian
    flask_praetorian.Praetorian(app, user_class)

If you are using an `app factory pattern
<http://flask.pocoo.org/docs/0.11/patterns/appfactories/>`_, it can be
initialized like::

    import flask_praetorian
    guard = flask_praetorian.Praetorian()
    ...
    guard.init_app(app, user_class)

flask-praetorian Developer Guide
================================

This developer guide will help you get started on working on flask-praetorian
in a development environment so that you can add features and run tests

TODO list
---------

* Add a thin wrapper for @jwt.jwt_required so that you can use flask-praetorian
  by itself if you want
* Describe requirements for user_class in the documentation
* get doc generation up and going
* expand the Quickstart documentation a bit
* find some lineart for the documentation
* get it up on pypi!

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

$ pip install --process-dependency-links -e .[dev]

The full list of dependencies can be found in ``setup.py``

Running tests
=============

Invokation
----------

This project uses `pytest <http://doc.pytest.org/en/latest/>`_

Tests are executed by invoke pytest directly from the root of the project::

$ py.test -ra test

The -ra option is recommended as it will report skipped tests

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

