Notes
=====

Error Handling
--------------

By default, flask-praetorian will add an error handler to Flask for
PraetorianErrors. This error handler produces nicely formatted json responses
with status codes that reflect the failures. The flask-praetorian package's
custom exception type ``PraetorianError`` derives from the ``FlaskBuzz`` base
exception type from the
`flask-buzz exceptions package <https://github.com/dusktreader/flask-buzz>`_.
The flask-buzz package provides convenience methods for error handlers.

The error handling may be disabled by adding a configuration setting for
``DISABLE_PRAETORIAN_ERROR_HANDLER``. You may wish to do this if you want to
customize your error handling even further.

For example, you may wish to have the error handler log messages about failures
prior to returning an error response. In this case, you can still take
advantage of flask-buzz's features to do so:

.. code-block:: python

   app.register_error_handler(
       PraetorianError,
       PraetorianError.build_error_handler(lambda e: logger.error(e.message)),
   )

Flask-Restplus compatibility
----------------------------

Flask-Restplus's error handler is not compatible with the normal Flask error
handler. What's more, prior to Flask-Restplus 0.11.0, Flask-Restplus's error
handler did not automatically handle derived exception classes, so you would
need to handle each and every PraetorianError type in your handler.

The
`flask-buzz exceptions package <https://github.com/dusktreader/flask-buzz>`_
provides a helper method for registering error handlers with flask-restplus:

.. code-block:: python

   PraetorianError.register_error_handler_with_flask_restplus(api)

Like the normal Flask error handler, additional tasks may be passed to this
method to be executed on the error prior to returning the response

Configuration Settings
----------------------

.. list-table:: Configuration Settings
   :header-rows: 1

   * - Flag
     - Description
     - Default Value
   * - ``SECRET_KEY``
     - A secret string value used to salt encryptions and hashes for the app.

       ABSOLUTELY MUST BE SET TO SOMETHING OTHER THAN DEFAULT IN PRODUCTION.
     - DO NOT USE THE DEFAULT IN PRODUCTION
   * - ``PRAETORIAN_HASH_SCHEME``
     - The hash scheme used to hash passwords in the database. If unset,
       passlib will use the default scheme which is ``pbkdf2_sha512``
     - ``'pbkdf2_sha512'``
   * - ``JWT_ALLOWED_ALGORITHMS``
     - A list of allowed algorithms that may be used to hash the JWT. See `the
       PyJWT docs <https://pyjwt.readthedocs.io/en/latest/algorithms.html>`_
       for more details.
     - ``['HS256']``
   * - ``JWT_ALGORITHM``
     - The jwt hashing algorithm to be used to encode tokens
     - ``'HS256'``
   * - ``JWT_ACCESS_LIFESPAN``
     - The default length of time that a JWT may be used to access a protected
       endpoint. See `the PyJWT docs
       <https://pyjwt.readthedocs.io/en/latest/usage.html#expiration-time-claim-exp>`_
       for more details.
     - ``{'minutes': 15}``
   * - ``JWT_REFRESH_LIFESPAN``
     - The default length of time that a JWT may be refreshed. JWT may also not
       be refreshed if its access lifespan is not expired.
     - ``{'days': 30}``
   * - ``JWT_PLACES``
     - A list of places where JWT will be checked
     - ``['header', 'cookie']``
   * - ``JWT_COOKIE_NAME``
     - The name of the cookie in HTTP requests where the JWT will be found
     - ``'access_token'``
   * - ``JWT_HEADER_NAME``
     - The name of the header in HTTP requests where the JWT will be found
     - ``'Authorization'``
   * - ``JWT_HEADER_TYPE``
     - A string describing the type of the header. Usually 'Bearer' but may be
       customized by the user
     - ``'Bearer'``
   * - ``USER_CLASS_VALIDATION_METHOD``
     - The name of the method on a user instance that should be used to
       validate that the user is active in the system.
     - ``'is_valid'``
   * - ``DISABLE_PRAETORIAN_ERROR_HANDLER``
     - Do not register the flask error handler automatically. The user may wish
       to configure the error handler themselves
     - ``None``


.. _user-class-requirements:

Requirements for the user_class
-------------------------------

The ``user_class`` argument supplied during initialization represents the
class that should be used to check for authorization for decorated routes. The
class itself may be implemented in any way that you see fit. It must, however,
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

* Provide an ``identity`` instance attribute

  * should return the unique id of the user

Although the example given in the documentation uses a SQLAlchemy model for the
userclass, this is not a requirement.
