Quickstart
==========

Requirements
------------

* Python 3.5

Note on Requirements
....................

I do not currently plan to support older versions of python. Python 2 support
is very unlikely to arrive as the original author is a die-hard believer in
python 3. As for older versions of python 3, my test harnesses depend on some
features only available in python 3.5.

Installation
------------

Install from pypi
.................
This will install the latest release of flask-praetorian from pypi via pip::

$ pip install flask-praetorian

Install latest version from github
..................................
If you would like a version other than the latest published on pypi, you may
do so by cloning the git repostiory::

$ git clone https://github.com/dusktreader/flask-praetorian.git

Next, checkout the branch or tag that you wish to use::

$ cd flask-praetorian
$ git checkout integration

Finally, use pip to install from the local directory::

$ pip install .

.. note::

    flask-praetorian does not support distutils or setuptools because the
    author has very strong feelings about python packaging and the role pip
    plays in taking us into a bright new future of standardized and usable
    python packaging


Example
-------

This is a minimal example of how to use the flask-praetorian decorators:

.. literalinclude:: ../example/basic.py
   :language: python

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
