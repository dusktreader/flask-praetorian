flask-praetorian comparison to other libraries
==============================================

The flask-praetorian extension doesn't really offer functionality that isn't
covered by other packages or a combination of others. However, it serves a very
targeted purpose and is intended to be a batteries-included solution for API
security that's ready to go out-of-the-box.

This section will discuss how flask-praetorian differs from the others and what
sort of advantages it provides

Other similar security packages include::

* flask-jwt
* flask-jwt-extended
* flask-jwt-simple
* flask-security


flask-jwt
---------

The `flask-jwt <https://github.com/mattupstate/flask-jwt>`_ extension was one of
the original jwt based flask security extensions. It was a mostly fully featured
securtiy package, and it was highly opinionated. This was the package that the
precursor to flask-praetorian sought to use. However functionality was limited,
and while a solution to one particular issue was being pursued, it became
apparent that flask-jwt had been abandoned.

The last commit on this package was 4 years ago (as of this writing), and the
repository has 36 outstanding issues and 30 outstanding pull-requests. The
flask-jwt extension should probably not be chosen for this reason alone as it
will not be updated going forward.

Password authentication is supported as a stubbed out method to allow client
app to easily connect it, but the verification is not implemented at all.

There is a route protection decorator in ``@jwt_required``, but no further
refinement of access control is offered.

The flask-praetorian extension offers all of these features and more.


flask-jwt-extended
------------------

After the maintainer of flask-jwt stopped updating his package,
`flask-jwt-extended <https://github.com/vimalloc/flask-jwt-extended>`_ was
started as a new project. The author originally wanted to extend flask-jwt but
instead had to create a new project. Like flask-jwt, flask-jwt-extended is
opinionated, but takes things to the next level. The flask-jwt-exetended
extension is very full featured and eminently configurable. It is an excellent
package with a lot of activity and support.

The flask-jwt-extended package supports the following features that are not
found in flask-praetorian::

* Using cookies for JWT storage
* Partial route protection
* Requiring fresh tokens
* Custom placement of JWT in HTTP requests (headers, body, etc)
* CSRF protection

However, flask-jwt-extended does not include some nice features of
flask-praetorian such as password hashing, password verification, role based
access, email registration and verification. Additionally, the API for
flask-praetorian is simpler and there is less configuration.

The flask-praetorian package aims to be a complete security extension while
flask-jwt-extended focuses on JWT-based auth and supporting many patterns of
access.

Additionally, flask-praetorian aims to be simpler to configure and support
specific and common access patters for APIs using JWT.


flask-jwt-simple
----------------

The `flask-jwt-simple <https://github.com/vimalloc/flask-jwt-simple>`_ extension
is meant to be a bare-bones extension that adds JWT auth to flask. I has few
features outside of a decorator that requires JWT auth and methods to produce
JWTs.

It is useful for rapid prototyping or building out your own JWT based security
for your app.

However, it's feature set is extremely limited compared to flask-praetorian.


flask-security
--------------

This package was the original inspiration for flask-praetorian. It is a fully-
featured security extension for flask and offers some of the same features as
flask-praetorian like password verification, role based access, and others.
However, this extension is meant to be used for flask websites and includes
wtform components and other things that are not neeeded for flask-based APIs.
Including all the extra stuff is both cumbersome and unnecessary in an API.
The flask-praetorian extension intends to be a similar batteries-included
package while offering a simple API with a full set of security tools.
