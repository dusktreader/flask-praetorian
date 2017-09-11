************
 Change Log
************

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

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
