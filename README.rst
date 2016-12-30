.. image::  https://badge.fury.io/py/flask-praetorian.svg
   :target: https://badge.fury.io/py/flask-praetorian
   :alt:    Latest Published Version

.. image::  https://travis-ci.org/dusktreader/flask-praetorian.svg?branch=master
   :target: https://travis-ci.org/dusktreader/flask-praetorian
   :alt:    Build Status

.. image::  https://readthedocs.org/projects/flask-praetorian/badge/?version=latest
   :target: http://flask-praetorian.readthedocs.io/en/latest/?badge=latest
   :alt:    Documentation Build Status

******************
 flask-praetorian
******************

---------------------------------------------------
Strong, Simple, and Precise security for Flask APIs
---------------------------------------------------

API security should be strong, simple, and precise like a Roman Legionary.
This package aims to provide that. Using `JWT <https://jwt.io/>`_ as
implemented by `Flask-JWT <https://pythonhosted.org/Flask-JWT/>`_,
*flask_praetorian* uses a very simple interface to make sure that the users
accessing your API's endpoints are provisioned with the correct roles for
access.

This project was heavily influenced by
`Flask-Security <https://pythonhosted.org/Flask-Security/>`_, but intends
to supply only essential functionality. Instead of trying to anticipate the
needs of all users, *flask-praetorian* will provide a simple and secure mechanism
to provide security for APIs specifically.

The *flask-praetorian* package can be used to:

* Encrypt (hash) passwords for storing in your database
* Verify plaintext passwords against the encrypted, stored versions
* Generate authorization tokens using a ``/auth`` api endpoint
* Check requests to secured endpoints for authorized tokens
* Ensure that the users associated with tokens have necessary roles for access

All of this is provided in a very simple to confiure and initialize flask
extension. Though simple, the security provided by *flask-praetorian* is strong
due to the usage of the proven security technology of JWT
and python's `PassLib <http://pythonhosted.org/passlib/>`_ package.

Super-quick Start
-----------------
 - requirements: `python3.5`
 - install through pip: `$ pip install flask-praetorian`
 - minimal usage example: `example/basic.py <https://github.com/dusktreader/flask-praetorian/tree/master/example/basic.py>`_

Documentation
-------------

The complete documentation can be found at the
`flask-praetorian home page <http://flask-praetorian.readthedocs.io>`_
