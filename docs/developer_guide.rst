sanic-praetorian Developer Guide
================================

This developer guide will help you get started on working on sanic-praetorian
in a development environment so that you can add features and run tests

Dependencies
------------

* python3
* poetry

Setup
-----

This package relies on `Poetry <https://poetry.eustace.io/>`_ for dependency
management and packaging.

Install the package for development
...................................

In order to install the package for development and to include all its
dependencies, navigate to the root project folder and execute this command::

$ poetry install

The full list of dependencies can be found in ``pyproject.toml``

Running tests
-------------

This project uses `pytest <http://doc.pytest.org/en/latest/>`_ for its unit
testing.

Tests are executed by invoking pytest through poetry from the root of the
project::

$ poetry run pytest -ra tests

The ``-ra`` option is recommended as it will report skipped tests

Documentation
-------------

readthedocs.org
...............

Documentation for the sanic-praetorian package is available on
`readthedocs.org <http://sanic-praetorian.readthedocs.io/en/latest/>`_. It is
configured so that new documentation is generated from the sanic-praetorian
docs directory automatically whenever a new commit is pushed to the master
branch. So, developers need not do anything to build documentation.

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

sphinx-view
...........

reStructuredText documents and sphinx documentation can be previewed as they
are edited on your workstation using a tool called
`sphinx-view <https://github.com/dusktreader/sphinx-view>`_. It is
indispensable when updating this README.rst document or one of the templates
for the autognerated sphinx documentation.


flake8
......

The `flake8 tool <https://pypi.python.org/pypi/flake8>`_ is very useful for
checking for compliant code style. Flake8 is included when *sanic-praetorian* is
installed with poetry.

The flake8 tool is invoked by targeting a specific source directory::

  $ poetry run flake8 sanic_praetorian

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

Other notes
-----------

* sanic-praetorian uses the ``pendulum`` to timestamp its JWT tokens with
  UTC timestamps
