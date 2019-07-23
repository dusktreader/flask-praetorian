Contributing Guidelines
=======================

Security Concerns
-----------------

Before any further discussion, a point about security needs to be addressed.
*If you find a serious security vulnerability that could affect current users,
please report it to maintainers via email or some form of private
communication*. For other issue reports, see below.

Thanks!
-------

First, thank you for your interest in contributing to flask-praetorian! Even
though this is a small flask-extension project, it takes a bit of work to keep
it maintained. All contributions help and improve the extension.

Contact Us
----------

The maintainers of flask-praetorian can be reached most easily via email::

  * Tucker Beck <tucker.beck@gmail.com>

Conduct
-------
Everyone's conduct should be respectful and friendly. For most folks, these
things don't need to be spelled out. However, to establish a baseline of
acceptable conduct, the flask-praetorian project expects contributors to adhere
to a `customized version <coc.html>`_ of the
`Python Software Foundation's Code of Conduct <https://www.python.org/psf/codeofconduct>`_.
Please see the "Conduct" section to reference the code of conduct.
Any issues working with other contributors should be reported to the maintainers

Contribution Recommendations
----------------------------

Github Issues
.............

The first and primary source of contributions is opening issues on github.
Please feel free to open issues when you find problems or wish to request a
feature. All issues will be treated seriously and taken under consideration.
However, the maintainers may disregard/close issues at their discretion.

Issues are most helpful when they contain specifics about the problem they
address. Specific error messages, references to specific lines of code,
environment contexts, and such are extremely helpful.

Code Contributions
..................

Code contributions should be submitted via pull-requests on github. Project
maintainers will review pull-requests and may test new features out. All
merge requests should come with commit messages that describe the changes as
well as a reference to the issue that the code addresses.

*All commits should include the issue #*

Commit messages should follow this format::

  Issue #56: Fixed gizmo component that was parfolecting

  The parfolection happening in the gizmo component was causing a vulterability
  in the anti-parfolection checks during the enmurculation process.

  This was addressed by caching the restults of parfolection prior to
  enmurculation.

  Also:
  * Added and updated unit tests
  * Added documentation
  * Cleaned up some code

Code contributions should follow best-practices where possible. Use the
`Zen of Python <https://www.python.org/dev/peps/pep-0020/>`_ as a guideline.
All code must stick to pep8 style guidelines.

Adding addtional dependencies should be limited except where needed
functionality can be easily added through pip packages. Please include
dependencies that are only applicable to development and testing in the
dev dependency list. Packages should only be added to the dependency lists if::

* They are actively maintained
* They are widely used
* They are hosted on pypi.org
* They have source code hosted on a public repository (github, gitlab, bitbucket, etc)
* They include tests in their repositories
* They include a software license

Documentation
.............

Help with documentation is *always* welcome.

The flask-praetorian project uses
`sphinx <http://www.sphinx-doc.org/en/master/>`_ for document generation.

Documentation lives in the ``docs`` subdirectory. Added pages should be
referenced from the table of contents.

Documentation should be clear, include examples where possible, and reference
source material as much as possible.

Documentation through code comments should be kept to a minimum. Code should
be as self-documenting as possible. If a section of code needs some explanation,
the bulk of it should be be presented as sphix-compatible
`docstrings <https://www.python.org/dev/peps/pep-0257/>`_ for methods, modules,
and classes.

Non-preferred Contributions
---------------------------

There are some types of contribution that aren't as helpful and are not as
welcome::

  * Complaints without suggestion
  * Criticism about the overall approach of the extension
  * Copied code without attribution
  * Promotion of personal packages/projects without due need
  * Sarcasm/ridicule of contributions or design choices
