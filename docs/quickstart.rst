Quickstart
==========

Requirements
------------

* Python 3.8+

Note on Requirements
....................

This project is only mantained for python versions that have not reached their
end-of-life. It may work with older versions, but functionality is not checked.

Installation
------------

.. note::

    flask-praetorian does not support distutils or setuptools because the
    author has very strong feelings about python packaging and the role pip
    plays in taking us into a bright new future of standardized and usable
    python packaging

Install from pypi
.................
This will install the latest release of flask-praetorian from pypi via pip::

$ pip install flask-praetorian

Install latest version from github
..................................
If you would like a version other than the latest published on pypi, you may
do so by cloning the git repository::

$ git clone https://github.com/dusktreader/flask-praetorian.git

Next, checkout the branch or tag that you wish to use::

$ cd flask-praetorian
$ git checkout integration

Finally, use poetry to install from the local directory::

$ poetry install

Example
-------

A minimal example of how to use the flask-praetorian decorators is included:

.. literalinclude:: ../example/basic.py
   :language: python

The above code can be found in `example/basic.py
<https://github.com/dusktreader/flask-praetorian/blob/master/example/basic.py>`_.
