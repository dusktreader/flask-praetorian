Blacklist Tutorial
------------------

This section of the tutorial covers concepts demonstrated by
`example/blacklist.py`_. These concepts include:

  * Working with long-lived JWT tokens
  * Blacklisting 'jti' claims

Long-lived JWT
..............

Often, RESTful APIs are consumed by other apps. These apps might make thousands
of requests per second and are pre-registered ahead of time as 'trusted' apps.
In these cases, you do not want to have to make the app have to constantly
refresh its token or to 'log in' repeatedly.

So, long-lived JWT are often provisioned for this. The problem is that a
long-lived token might fall into the wrong hands, and your app needs a
mechanism to revoke access from a stolen JWT.

This is what the blacklist is used for

The Blacklist
.............

A JWT token is uniquely identified by its `'jti' claim
<https://tools.ietf.org/html/rfc7519#section-4.1.7>`_. For flask-praetorian,
this is provisioned as `uuid4
<https://en.wikipedia.org/wiki/Universally_unique_identifier#Version_4_(random)>`_.
When a token is refreshed, the new token is given the same 'jti' claim. This
serves to identify the two tokens as being really the same.

A blacklist is a collection of 'jti' claims for tokens that have had access
revoked. The blacklist should be very performant and persistent. It is best to
use a container that minimizes lookup time.

One common pattern is to have a database table that persists the blacklist
data. However, this table should not be accessed to check the blacklist on
every request to a protected endpoint. Instead, when an app loads, the
blacklist should be loaded into some container that lives in local memory and
has very rapid lookup. You should use the 'refresh' operation as a mechanism
to flush the blacklist back out to the data-store for persistence so that if
your app dies, most of the blacklist is preserved.

For the purposes of our demo, the blacklist is simply a python ``set`` that is
stored in local memory:

.. literalinclude:: ../example/blacklist.py
   :language: python
   :lines: 43-47
   :caption: from `example/blacklist.py`_

The ``is_blacklisted`` function is then registered when initializing the
flask-praetorian instance with the app:

.. literalinclude:: ../example/blacklist.py
   :language: python
   :lines: 57-58
   :caption: from `example/blacklist.py`_

Now, any time a protected endpoint it accessed, the ``jti`` claim from the
JWT will first be checked against the blacklist.

To make demonstration of the blacklist more obvious,
the lifespans provisioned for this demo app are obscenely long

Blacklisting a Token
....................

The example app has an added 'blacklist_token' endpoint that will blacklist
the current token:

.. literalinclude:: ../example/blacklist.py
   :language: python
   :lines: 117-131
   :caption: from `example/blacklist.py`_

Let's try blacklisting a token for our admin user, 'Walter':

.. image:: _static/tutorial-blacklist-1.png

Now, the token for Walter is blacklisted. No access to any protected endpoint
will be granted because the 'jti' claim from that token will be found in the
blacklist:

.. image:: _static/tutorial-blacklist-2.png

In Conclusion
.............

* Apps often get long-lived JWTs
* Access for these long-lived tokens can be controlled with the blacklist
* The blacklist must have very fast lookup

.. _example/: https://github.com/dusktreader/flask-praetorian/tree/master/example
.. _example/basic.py: https://github.com/dusktreader/flask-praetorian/blob/master/example/basic.py
.. _example/refresh.py: https://github.com/dusktreader/flask-praetorian/blob/master/example/refresh.py
.. _example/blacklist.py: https://github.com/dusktreader/flask-praetorian/blob/master/example/blacklist.py
.. _example/custom_claims.py: https://github.com/dusktreader/flask-praetorian/blob/master/example/custom_claims.py
.. _example/api_tool.py: https://github.com/dusktreader/flask-praetorian/blob/master/example/api_tool.py
