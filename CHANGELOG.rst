************
 Change Log
************

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

v0.4.4rc - 2018-05-09
---------------------
- Got docs working again...by pinning the flask version to 1.0
- Upgraded to Pendulum 2.0
- May cause issues downstream. Leaving this an RC release for now

v0.4.3 - 2018-05-03
-------------------
- Docs are finally working right. Ready to announce the 0.4 release!

v0.4.2 - 2018-05-02
-------------------
- Fixed failing docs build issue? again?

v0.4.1 - 2018-05-02
-------------------
- Fixed failing docs build issue

v0.4.0 - 2018-05-02
-------------------
- Lots of updates to make the package compliant with:
  - awesome-flask
  - approved flask extensions
- Verified python 3.4 support
- Added tutorials to the docs
- Added a custom logo to the docs!

v0.3.22 - 2018-04-23
--------------------
- Added github links to the docs

v0.3.21 - 2018-04-23
--------------------
- Wrote a tutorial and expanded examples

v0.3.20 - 2018-04-23
--------------------
- Added a logo!

v0.3.19 - 2018-04-20
--------------------
- Added homepage to setup.py

v0.3.18 - 2018-04-20
--------------------
- Fixed issues with travis build

v0.3.17 - 2018-04-20
--------------------
- Fixed flake8 error
- Fixed long_description to pull from README for pypi

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
