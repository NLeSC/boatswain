==========
Change Log
==========

This document records all notable changes to Boatswain.
This project adheres to `Semantic Versioning <http://semver.org/>`_.


`0.5.0`_ (2017-02-10):
----------------------

    * Build will now greedily try to build images instead of throwing an exception at the first error.
    * Added error messages to failing builds
    * Standardized return values (e.g. always a list)
    * Refactored to reduce code duplication in boatswain class

`0.4.0`_ (2017-02-09):
----------------------

    * Progress timer now increases every second
    * Improved error reporting (No longer uses an exception)

`0.3.0`_ (2017-02-08):
----------------------

   * Added a whole bunch of tests
   * Added the clean command
   * Changed file layout from recursive to using from

`0.2.0`_ (2017-02-06):
----------------------

    * Added dry-run option
    * Added ability to build only one image

`0.1.0`_ (2017-02-02):
----------------------

    * Initial release