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
