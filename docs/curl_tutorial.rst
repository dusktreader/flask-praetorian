Tutorial (using curl command-line tool)
=======================================

This tutorial will use the example code provided in
`example/basic.py
<https://github.com/dusktreader/flask-praetorian/blob/master/example/basic.py>`_.

Download the source code and save it on your machine where you will be running
through the tutorial.

Requirements
------------

This tutorial requires (outside of the normal python dependencies):

* sqlite
* curl

Basic Tutorial
--------------

We will start this tutorial using the ``example/basic.py`` example file. This
provides a minimal application using flask-praetorian to authorize access to
specific endpoints.

Starting up the server
......................

The API server is started very easily by calling::

$ python basic.py

This will start our development flask server on localhost at port 5000

Accessing the api
.................

For this tutorial, we'll be using the curl command line program to send
requests to the server. You may also use a graphical api tool like Postman if
you prefer.

Let's try logging into an unprotected endpoint without any authorixation::

$ curl http://localhost:5000/ -X GET

The server should return an 'OK' response and print out the json payload of
the response::

    {
      "message": "root endpoint"
    }

Note that you can see more info about the response with curl by including the
``--verbose`` flag with your call to curl. This will show the status code for
the previous call to be ``HTTP/1.0 200 OK``

Logging in
..........

To access protected endpoints, the first thing that we will need to do is to
get a JWT token from our server. This token will be used to access any proteced
endpoints in our app.

In the example source code, you can see where the users are added
(look for 'Add users for the example'). Our most basic user is 'TheDude' with
the password 'abides'. Let's log in with this user::

$ curl http://localhost:5000/login -X POST -d '{"username":"TheDude","password":"abides"}'

You should get an 'OK' response back and curl will print out the json payload
that our server returned::

    {
      "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1MjQ1MTExMzQsImV4cCI6MTUyNDU5NzUzNCwicmZfZXhwIjoxNTI3MTAzMTM0LCJqdGkiOiI2MjllN2I0NS1lMjQ4LTQxMjEtYmJhNC00YTk4M2M3MDAyOTciLCJpZCI6MSwicmxzIjoiIn0.kGlDvt7XMwpyuzeZ9wlajMJW8bnw87FzY5VbZGc6nHk"
    }

Now that we have a token, we can use it to access endpoints where authorization
is required.

Note: in the basic example, the server is configured so that tokens access
lifespan is limited to 24 hours. So, if you don't finish the tutorial within
a day of starting it, you will have to get a new token and start over.

Accessing a protected endpoint
..............................

Endpoints that require authorization are decorated with the ``@auth_required``
decorator from flask-praetorian. In our example, the ``protected`` endpoint
is the first one that is protected. Let's try accessing it first without the
JWT token we provisioned above::

$ curl http://localhost:5000/protected -X GET

You should get an error response that looks like this::

    {
      "error": "MissingTokenHeader",
      "message": "JWT token not found in headers under 'Authorization'",
      "status_code": 401
    }

flask-praetorian uses flask's error handler to convert PraetorianErrors that
are raised during execution into responses that are nicely formatted and have
the correct error code.

Now, let's try hitting that same endpoint with the token we received earlier::

$ curl http://localhost:5000/protected -X GET -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1MjQ1MTExMzQsImV4cCI6MTUyNDU5NzUzNCwicmZfZXhwIjoxNTI3MTAzMTM0LCJqdGkiOiI2MjllN2I0NS1lMjQ4LTQxMjEtYmJhNC00YTk4M2M3MDAyOTciLCJpZCI6MSwicmxzIjoiIn0.kGlDvt7XMwpyuzeZ9wlajMJW8bnw87FzY5VbZGc6nHk"

Now, we should get an ``OK`` response and a nice message::

    {
      "message": "protected endpoint (allowed user TheDude)"
    }

Accessing endpoints with required roles
.......................................

flask-praetorian also supports limiting access to authorized users with certain
roles. In order to access the roles associated with a user, your User class
must have a method on a User instance called ``rolenames``.

In our example, we have set up the user 'Walter' with a password
'calmerthanyouare' and an 'admin' role.

First, let's try to access a protected endpoint that requires the admin role
with the token we were provisioned above::

$ curl http://localhost:5000/protected_admin_required -X GET -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1MjQ1MTExMzQsImV4cCI6MTUyNDU5NzUzNCwicmZfZXhwIjoxNTI3MTAzMTM0LCJqdGkiOiI2MjllN2I0NS1lMjQ4LTQxMjEtYmJhNC00YTk4M2M3MDAyOTciLCJpZCI6MSwicmxzIjoiIn0.kGlDvt7XMwpyuzeZ9wlajMJW8bnw87FzY5VbZGc6nHk"

Now, we get another error response but this time a 403::

    {
      "error": "MissingRoleError",
      "message": "This endpoint requires all the following roles: ['admin']",
      "status_code": 403
    }

It's nice that the problem is spelled out clearly, isn't it?

Now, let's log 'Walter' in and try that endpoint again::

    $ curl http://localhost:5000/login -X POST -d '{"username":"Walter","password":"calmerthanyouare"}'
    {
      "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1MjQ1MTE3ODEsImV4cCI6MTUyNDU5ODE4MSwicmZfZXhwIjoxNTI3MTAzNzgxLCJqdGkiOiI4ZmEwNDVmMS1hZWFlLTQ0NDEtOThkNi05Zjc0NjcyMDYxMzYiLCJpZCI6MiwicmxzIjoiYWRtaW4ifQ.p8IEgRZmEyJlFCBVpjg4UEUg4cV-UM-ElaIhMmcqaBg"
    }
    $ curl http://localhost:5000/protected_admin_required -X GET -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1MjQ1MTE3ODEsImV4cCI6MTUyNDU5ODE4MSwicmZfZXhwIjoxNTI3MTAzNzgxLCJqdGkiOiI4ZmEwNDVmMS1hZWFlLTQ0NDEtOThkNi05Zjc0NjcyMDYxMzYiLCJpZCI6MiwicmxzIjoiYWRtaW4ifQ.p8IEgRZmEyJlFCBVpjg4UEUg4cV-UM-ElaIhMmcqaBg"
    {
      "message": "protected_admin_required endpoint (allowed user Walter)"
    }

OK, we're in! One thing to note here is that in the second call, the request
does not have to include any human readable indication of who the user is.
Instead, everything your app needs to get the right user is embedded in the JWT
token.

Finally, it's worth noting that with the ``@roles_required`` decorator, *each
one of the required roles* must be possessed by the user or access will not be
granted. This means that even if a user has an 'admin' role, they could not
access an endpont that required 'admin' and 'flunky'. They would have to have
a 'flunky' role. There is no concept of role heirarchy in flask-praetorian.

Next, let's access an endpoint that uses the ``roles_accepted`` decorator

Accessing endpoints with accepted roles
.......................................

For this section, we will use the user 'Donnie' with password 'iamthewalrus'
and a role of 'operator'.

First, let's log 'Donnie' in and try to access the ``protected_admin_required``
endpoint above::

    $ curl http://localhost:5000/login -X POST -d '{"username":"Donnie","password":"iamthewalrus"}'
    {
      "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1MjQ1MTIyOTcsImV4cCI6MTUyNDU5ODY5NywicmZfZXhwIjoxNTI3MTA0Mjk3LCJqdGkiOiJhOTY2ZjcwYS1iYjRlLTQ2ZWItOWRhYi0wMTFhMjZlNTFkZjYiLCJpZCI6MywicmxzIjoib3BlcmF0b3IifQ.WgCcASGD0mUtGVnHGRN9ADBoR_VrjGy1VpUEJWAng5s"
    }
    $ curl http://localhost:5000/protected_admin_required -X GET -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1MjQ1MTIyOTcsImV4cCI6MTUyNDU5ODY5NywicmZfZXhwIjoxNTI3MTA0Mjk3LCJqdGkiOiJhOTY2ZjcwYS1iYjRlLTQ2ZWItOWRhYi0wMTFhMjZlNTFkZjYiLCJpZCI6MywicmxzIjoib3BlcmF0b3IifQ.WgCcASGD0mUtGVnHGRN9ADBoR_VrjGy1VpUEJWAng5s"
    {
      "error": "MissingRoleError",
      "message": "This endpoint requires all the following roles: ['admin']",
      "status_code": 403
    }

As expected, 'Donnie' can't reach that endpoint. However, he should be able to
access any endpoint that accepts the 'operator' role::

    $ curl http://localhost:5000/protected_operator_accepted -X GET -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1MjQ1MTIyOTcsImV4cCI6MTUyNDU5ODY5NywicmZfZXhwIjoxNTI3MTA0Mjk3LCJqdGkiOiJhOTY2ZjcwYS1iYjRlLTQ2ZWItOWRhYi0wMTFhMjZlNTFkZjYiLCJpZCI6MywicmxzIjoib3BlcmF0b3IifQ.WgCcASGD0mUtGVnHGRN9ADBoR_VrjGy1VpUEJWAng5s"
    {
      "message": "protected_operator_accepted endpoint (allowed user Donnie)"
    }

Refreshing Tokens
-----------------

The next section goes over how to manage refreshing tokens.

The basic concept of JWT is that essential user information is embedded in the
authorization token that can be very quickly accessed from any route that needs
to be protected. The advantage to this is that the application does not need
to access the data-store at all to check for authorization. In most
applications, accessing the data-store can be one of the most costly
operations. So, JWT offers a nice work around so that routes that do not need
to access the store can do so very quickly and simply.

Because we're using the token alone to authorize a user, and because
the token is issued once with all the information that's needed, logging out
a user is not so straight-forward. Thus, tokens need to have an expiration.

This is where the concept of refreshing a token comes in. We want to make sure
that we check the status of a user regularly (to make sure they haven't been
removed from the system), but we don't want to do this on every api request. We
also don't want to make the user have to regularly enter their credentials to
access the API. Ideally, entering credentials would be an infrequent operation.

So, flask-praetorian adds the ability to refresh a token. The general
guidelines are that a token should need to be refreshed relatively frequently
(the default is 15 minutes) and issuing new tokens should not have to happen
very frequently at all (the default is 30 days).

A token is granted an 'access lifespan'. This is the amount of time that a
token can be used to access authorized endpoints before needing to be
refreshed. The default is 15 minutes, but this can be overridden by setting
the configuration variable ``JWT_ACCESS_LIFESPAN``.  After that 15 minutes is
up, the token must be refrehed.

A token is also granted a 'refresh lifespan'. This is the amount of time that
a token can be refreshed. The default is 30 days, but this may be overridden by
setting the configuration variable ``JWT_REFRESH_LIFESPAN``. After that time is
up, the user must re-submit credentials and be issued a brand new token.

At refresh time, we also want to check on a user and make sure that they are
still active and enabled. We don't want to continue letting a user access the
system if they have been removed. Because refreshes happen more infrequently,
it's ok to access the data-store at this time to check up on things.

Ok, enough about the mechanisms, lets try it out

We will continue this tutorial on the topic of 'refreshing' using the
``example/refresh.py`` example file. This provides a shorter access lifespan
and refresh lifespan so it is easier to demonstrate the workings of
flask-praetorian. There's also an added utility endpoint to ``disable_user``.

Starting up the server
......................

Start up the api server by calling::

$ python refresh.py

Keep in mind as we go through this, taht the lifespans are much shorter::

* 30 second access lifespan
* 2 minute refresh lifespan

So, you may have to re-issue commands and be careful of timing. In order to
speed things up and avoid having to copy/paste the token many times, we'll use
the shell variable ``$TOKEN`` in our commands

Now, let's log in and immediately check that the token works::

    $ curl http://localhost:5000/login -X POST -d '{"username":"Walter","password":"calmerthanyouare"}'
    {
      "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1MjQ1MTUxMDAsImV4cCI6MTUyNDYwMTUwMCwicmZfZXhwIjoxNTI3MTA3MTAwLCJqdGkiOiI2MmI1NDdkOS1kNzA5LTRhZTMtYjgwNS04ZjFmNDI5ZDUzODMiLCJpZCI6MiwicmxzIjoiYWRtaW4ifQ.PacaZPOBNQ_6n8h7HiJtrfLC4YWqBIXZCtCMDa7X05Q"
    }
    $ TOKEN=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1MjQ1MTUxMDAsImV4cCI6MTUyNDYwMTUwMCwicmZfZXhwIjoxNTI3MTA3MTAwLCJqdGkiOiI2MmI1NDdkOS1kNzA5LTRhZTMtYjgwNS04ZjFmNDI5ZDUzODMiLCJpZCI6MiwicmxzIjoiYWRtaW4ifQ.PacaZPOBNQ_6n8h7HiJtrfLC4YWqBIXZCtCMDa7X05Q
    $ curl http://localhost:5000/protected -X GET -H "Authorization: Bearer $TOKEN"
    {
      "message": "protected endpoint (allowed user Walter)"
    }

Refreshing a token
..................

Now, let's wait 30 seconds for the token to expire and try again::

    $ curl http://localhost:5000/protected -X GET -H "Authorization: Bearer $TOKEN"
    {
      "error": "ExpiredAccessError",
      "message": "access permission has expired",
      "status_code": 401
    }

Ok, great! this is what we want to see. Now, quickly, let's hit the ``refresh``
endpoint (before the 2 minute refresh lifespan expires)::

    $ curl http://localhost:5000/refresh -X GET -H "Authorization: Bearer $TOKEN"
    {
      "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1MjQ1MTUzNTgsImV4cCI6MTUyNDUxNTM4OCwicmZfZXhwIjoxNTI0NTE1NDQ0LCJqdGkiOiIxOWI5NTM4OS1kNjk5LTQwZGQtOTZmYy02YWM3ZDUxODg5MzgiLCJpZCI6MiwicmxzIjoiYWRtaW4ifQ.6fCqybn-sAaXmwc4YpclBa8rCMv0sISfEtjTKmoqQ0g"
    }

So, refresh actually gives us a *new* JWT back. However, all of the information
in this new token is an exact duplicate of the token we had before. Only the
access lifespan has been extended.

Let's try to access the ``protected`` endpoint with the new token::

    $ TOKEN=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1MjQ1MTUzNTgsImV4cCI6MTUyNDUxNTM4OCwicmZfZXhwIjoxNTI0NTE1NDQ0LCJqdGkiOiIxOWI5NTM4OS1kNjk5LTQwZGQtOTZmYy02YWM3ZDUxODg5MzgiLCJpZCI6MiwicmxzIjoiYWRtaW4ifQ.6fCqybn-sAaXmwc4YpclBa8rCMv0sISfEtjTKmoqQ0g
    $ curl http://localhost:5000/protected -X GET -H "Authorization: Bearer $TOKEN"
    {
      "message": "protected endpoint (allowed user Walter)"
    }

Great! Now we can access the endpoints with the new token as before.

The refresh lifespan expires
............................

Next, let's wait over 1:30 for the expiration lifespan to run out as well.
After we are done waiting, we'll try to refresh the token again::

    $ curl http://localhost:5000/refresh -X GET -H "Authorization: Bearer $TOKEN"
    {
      "error": "ExpiredRefreshError",
      "message": "refresh permission for token has expired",
      "status_code": 401
    }

At this point, you would need to log in again with the user's credentials.

Checking a user at refresh time
...............................

Now, we'll demonstrate how the user is checked at refresh time to make sure
that they are still active in the system. First, we will log our user in and
verify that access has been granted::


    $ curl http://localhost:5000/login -X POST -d '{"username":"Walter","password":"calmerthanyouare"}'
    {
      "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1MjQ1MTU5MzksImV4cCI6MTUyNDUxNTk2OSwicmZfZXhwIjoxNTI0NTE2MDU5LCJqdGkiOiJkOTVkMDMxZS1mOWQ0LTQ3NjktOWJhNS0wZmNlMzk4M2I3NDgiLCJpZCI6MiwicmxzIjoiYWRtaW4ifQ.ol6qPrQUsGPjvtOfPkaWgbah3-m8zEg-89Kb0hnxrjk"
    }
    $ TOKEN=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1MjQ1MTU5MzksImV4cCI6MTUyNDUxNTk2OSwicmZfZXhwIjoxNTI0NTE2MDU5LCJqdGkiOiJkOTVkMDMxZS1mOWQ0LTQ3NjktOWJhNS0wZmNlMzk4M2I3NDgiLCJpZCI6MiwicmxzIjoiYWRtaW4ifQ.ol6qPrQUsGPjvtOfPkaWgbah3-m8zEg-89Kb0hnxrjk
    $ curl http://localhost:5000/protected -X GET -H "Authorization: Bearer $TOKEN"
    {
      "message": "protected endpoint (allowed user Walter)"
    }

Now, before the token's access expires, let's hit the ``disable_user``
endpoint::

    $ curl http://localhost:5000/disable_user -X POST -d '{"username":"Walter"}' -H "Authorization: Bearer $TOKEN"
    {
      "message": "disabled user Walter"
    }

Quickly, try the ``protected`` endpoint again::

    $ curl http://localhost:5000/protected -X GET -H "Authorization: Bearer $TOKEN"
    {
      "message": "protected endpoint (allowed user Walter)"
    }

Notice that we can still access the protected endpoint even though the user is
not enabled now? This is because the token's access lifespan hasn't expired
yet, so the application doesn't look up the user in the data-store; it merely
pulls authorization and user identification information from the token itself.
This is why access lifespans need to be short! Now, let's try that again after
the access lifespan expires and the token needs to be refreshed::

    $ curl http://localhost:5000/protected -X GET -H "Authorization: Bearer $TOKEN"
    {
      "error": "ExpiredAccessError",
      "message": "access permission has expired",
      "status_code": 401
    }

Great! Finally, let's attempt to refresh the token for the disabled user::

    $ curl http://localhost:5000/refresh -X GET -H "Authorization: Bearer $TOKEN"
    {
      "error": "InvalidUserError",
      "message": "The user is not valid or has had access revoked",
      "status_code": 403
    }

Now, we see that disabling the user is effective at refresh time.

Blacklisting Tokens
-------------------

Many times, JWT tokens are issued to other applications that consume your app's
API. In these cases, you may want to grant tokens that have very long
lifespans. There is even a special constant in flask-praetorian for a lifespan
that is one million seconds (3000 years) called ``VITAM_AETERNUM``. This should
never be used for an access lifespan unless your app uses a blacklist, because
that token will be able to access your app forever (or until you change your
secret key).

In such a case, you need a mechanism to disable a token (and any tokens that
have been generated by refreshing it). This is where the blacklist comes in.
Essentially, the blacklist should be a fast-access storage of the ``jti`` claim
from a JWT token (see https://tools.ietf.org/html/rfc7519#section-4.1.7). This
is a unique identifier for a token.

The blacklist lookup mechanism must be very fast, because the blacklist (if
enabled) will be looked up for each request to a protected endpoint. To enable
the blacklist, your application should provide a method that,
given a token's jti looks to see if it is blacklisted. This method is passed
into the initalization for the flask-praetorian instance when the app is being
set up

We will continue this tutorial on the topic of 'blacklisting' using the
``example/blacklist.py`` example file. This provides a very, very long access
lifespan and refresh lifespan.  There's also an added utility endpoint to
``blacklist_token``

Starting up the server
......................

Start up the api server by calling::

$ python blacklist.py

Now, let's log in and immediately check that the token works::

    $ curl http://localhost:5000/login -X POST -d '{"username":"Walter","password":"calmerthanyouare"}'
    {
      "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1MjQ1MTk4NDksImV4cCI6MTUyNDUxOTg3OSwicmZfZXhwIjoyMzg4NTE5ODQ5LCJqdGkiOiI4Y2UzOTMzNC04ODJiLTQ4NWMtYWIxNC1hNzJmZjU1ZTY0NTQiLCJpZCI6MiwicmxzIjoiYWRtaW4ifQ._GF8mhZSh5Kw-PzLxTEU8EQjLJ2PTwHIbYB6_rtsPpA"
    }
    $ TOKEN=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1MjQ1MTk4NDksImV4cCI6MTUyNDUxOTg3OSwicmZfZXhwIjoyMzg4NTE5ODQ5LCJqdGkiOiI4Y2UzOTMzNC04ODJiLTQ4NWMtYWIxNC1hNzJmZjU1ZTY0NTQiLCJpZCI6MiwicmxzIjoiYWRtaW4ifQ._GF8mhZSh5Kw-PzLxTEU8EQjLJ2PTwHIbYB6_rtsPpA
    $ curl http://localhost:5000/protected -X GET -H "Authorization: Bearer $TOKEN"
    {
      "message": "protected endpoint (allowed user Walter)"
    }

Next, we will blacklist the token::

    $ curl http://localhost:5000/blacklist_token -X POST -d "{\"token\":\"$TOKEN\"}" -H "Authorization: Bearer $TOKEN"
    {
      "message": "token blacklisted (eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1MjQ1MTk4NDksImV4cCI6MTUyNDUxOTg3OSwicmZfZXhwIjoyMzg4NTE5ODQ5LCJqdGkiOiI4Y2UzOTMzNC04ODJiLTQ4NWMtYWIxNC1hNzJmZjU1ZTY0NTQiLCJpZCI6MiwicmxzIjoiYWRtaW4ifQ._GF8mhZSh5Kw-PzLxTEU8EQjLJ2PTwHIbYB6_rtsPpA)"
    }

Finally, long before the token has expired, we will check to see if we can
access a protected route::

    $ curl http://localhost:5000/protected -X GET -H "Authorization: Bearer $TOKEN"
    {
      "error": "BlacklistedError",
      "message": "Token has a blacklisted jti",
      "status_code": 403
    }

As long as the blacklist is persisted, the token will be useless for accessing
protected routes.
