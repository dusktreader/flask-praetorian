************
 Change Log
************

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

v0.3.15 - 2017-10-04
--------------------
- Changed InvalidUserError to have status code 403

v0.3.14 - 2017-10-04
--------------------
- Revised exceptions to derive from FlaskBuzz

v0.3.13 - 2017-10-01
--------------------
- Errors decoding JWT tokens now raise InvalidTokenHeader

v0.3.12 - 2017-09-28
--------------------
- Made user validation more configurable, and condensed validation code

v0.3.11 - 2017-09-27
--------------------
- Added capability for user to override fields for PraetorianError's in jsonify

v0.3.10 - 2017-09-27
--------------------
- Fixed issues with overrides for lifespan settings

v0.3.9 - 2017-09-27
-------------------
- Added overrides for pack_header_for_user

v0.3.8 - 2017-09-27
-------------------
- Allowed pack_user_for_header to be used outside of tests

v0.3.7 - 2017-09-22
-------------------
- Added special exception for missing user

v0.3.6 - 2017-09-22
-------------------
- Changed role decorators to raise MissingRoleError on failure

v0.3.5 - 2017-09-22
-------------------
- Added support for user models containing a validate method
- Added abilitiy to provision tokens that don't expire
- Added ability to override expiration times

v0.3.4 - 2017-09-13
-------------------
- Added utility function to fetch just user_id

v0.3.3 - 2017-09-11
-------------------
- Updated quickstart documentation

v0.3.2 - 2017-09-11
-------------------
- Converted all timestamping to pendulum (for freezing time in tests)

v0.3.1 - 2017-06-22
-------------------
- Added in missing MANIFEST.in

v0.3.0 - 2017-06-20
-------------------
- Removed dependence on flask-jwt. Provides jwt support via PyJWT
- Converted PraetorianError to be based on Buzz exceptions
- Updated documentation to reflect pypi availability of flask-praetorian
- Added support for using extant instance of jwt in new Praetorian instances
- Added a few integration tests
- Fixed up the documentation and README a little bit

v0.2.0 - 2016-12-15
-------------------
- First release of flask-praetorian and contained functionality
- Added this CHANGELOG
- Added a README providing a brief overview of the project
- Added documentation on a readthedocs site include full module docs
