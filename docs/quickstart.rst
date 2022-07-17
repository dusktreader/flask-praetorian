Quickstart
==========

Requirements
------------

* Python 3.7+

Note on Requirements
....................

I do not currently plan to support older versions of python. Python 2 support
is very unlikely to arrive as the original author is a die-hard believer in
python 3. As for older versions of python 3, my test harnesses depend on some
features only available in python 3.7 and up.

Installation
------------

.. note::

    sanic-praetorian does not support distutils or setuptools because the
    author has very strong feelings about python packaging and the role pip
    plays in taking us into a bright new future of standardized and usable
    python packaging

Install from pypi (**not yet available**)
.................
This will install the latest release of sanic-praetorian from pypi via pip::

$ pip install sanic-praetorian

Install latest version from github
..................................
If you would like a version other than the latest published on pypi, you may
do so by cloning the git repository::

$ git clone https://github.com/pahrohfit/sanic-praetorian.git

Next, checkout the branch or tag that you wish to use::

$ cd sanic-praetorian
$ git checkout sanic

Finally, use poetry to install from the local directory::

$ poetry install

Example
-------

A minimal example of how to use the flask-praetorian decorators is included:

.. literalinclude:: ../example/basic.py
   :language: python

The above code can be found in `example/basic.py
<https://github.com/pahrohfit/sanic-praetorian/blob/master/example/basic.py>`_.
