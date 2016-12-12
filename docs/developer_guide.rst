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

If you would like to be able to run tests also, include the test 'extras'::

$ pip install -e .[dev,test]

Additional options for 'extras' include 'lint' for style checking and 'doc'
for document generation

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
-------------

This project uses `pytest <http://doc.pytest.org/en/latest/>`_ for its unit
testing.

Tests are executed by invoking pytest directly from the root of the project::

$ py.test -ra tests

The ``-ra`` option is recommended as it will report skipped tests

Documentation
-------------

Generating the documentation
............................

Simply execute the following script within an active virtual environment::

  $ bin/generate-docs

This will generate html documentation in docs/build

In the future, we will probably add extra arguments that will allow generation
of pdf or latex output for the docs as well.

Adding further documentation
............................

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
----------

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

