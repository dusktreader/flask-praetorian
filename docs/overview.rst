Overview
========

API security should be strong, simple, and precise like a Roman Legionary.
This package aims to provide that. Using `JWT <https://jwt.io/>`_ tokens as
implemented by `PyJWT <https://pyjwt.readthedocs.io/en/latest/>`_,
`flask-praetorian <https://github.com/dusktreader/flask-praetorian>`_
uses a very simple interface to make sure that the users
accessing your API's endpoints are provisioned with the correct roles for
access.

This project was heavily influenced by
`Flask-Security <https://pythonhosted.org/Flask-Security/>`_, but intends
to supply only essential functionality. Instead of trying to anticipate the
needs of all users,
`flask-praetorian <https://github.com/dusktreader/flask-praetorian>`_ will
provide a simple and secure mechanism to provide security for APIs
specifically.

The `flask-praetorian <https://github.com/dusktreader/flask-praetorian>`_
package can be used to:

* Encrypt (hash) passwords for storing in your database
* Verify plaintext passwords against the encrypted, stored versions
* Generate authorization tokens upon verification of passwords
* Check requests to secured endpoints for authorized tokens
* Ensure that the users associated with tokens have necessary roles for access
* Parse user information from request headers for use in client route handlers

All of this is provided in a very simple to configure and initialize flask
extension. Though simple, the security provided by
`flask-praetorian <https://github.com/dusktreader/flask-praetorian>`_ is strong
due to the usage of the proven security technology of JWT
and python's `PassLib <http://pythonhosted.org/passlib/>`_ package.

The `flask-praetorian <https://github.com/dusktreader/flask-praetorian>`_
source code is hosted on
`github <https://github.com/dusktreader/flask-praetorian>`_. If you find issues
that you wish to report or want to add features via a pull-request, please do
so there. Pull-requests welcome!
