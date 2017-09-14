==========
Change Log
==========

This document records all notable changes to Boatswain.

This project adheres to `Semantic Versioning <http://semver.org/>`_.

`1.0.0`_
-------

* Fixed help text of push command
* Fixed extraction of image id from docker response in some cases
* Windows compatibility
* Appveyor windows tests are passing


`0.7.0`_ (2017-04-03)
----------

* Added a 'before' and 'command' key to the build definition. This is a list of commands that need to be staged into the context directory.
* Default verbosity only shows 1 progress bar for all images
* Changed progress indication to full white block

`0.6.0`_ (2017-03-09)
--------------------

* Added the tree command which will print the tree of the boatswain file
* Added quiet and extra verbose modes

`0.5.1`_ (2017-02-10)

* Fixed issue with printing unicode text from the docker stream

`0.5.0`_ (2017-02-10)
---------------------

* Implemented push command
* Build will now greedily try to build images instead of throwing an exception at the first error.
* Added error messages to failing builds
* Standardized return values (e.g. always a list)
* Refactored to reduce code duplication in boatswain class

`0.4.0`_ (2017-02-09)
---------------------

* Progress timer now increases every second
* Improved error reporting (No longer uses an exception)

`0.3.0`_ (2017-02-08)
---------------------

* Added a whole bunch of tests
* Added the clean command
* Changed file layout from recursive to using from

`0.2.0`_ (2017-02-06)
---------------------

* Added dry-run option
* Added ability to build only one image

`0.1.0`_ (2017-02-02)
---------------------

* Initial release


.. _0.1.0: https://github.com/nlesc-sherlock/boatswain/commit/f8b85edd3ed9f21c04fa846eae1af7abed8d0d77
.. _0.2.0: https://github.com/nlesc-sherlock/boatswain/compare/f8b85ed...0.2.0
.. _0.3.0: https://github.com/nlesc-sherlock/boatswain/compare/0.2.0...0.3.0
.. _0.4.0: https://github.com/nlesc-sherlock/boatswain/compare/0.3.0...0.2.0
.. _0.5.0: https://github.com/nlesc-sherlock/boatswain/compare/0.4.0...0.5.0
.. _0.5.1: https://github.com/nlesc-sherlock/boatswain/compare/0.5.0...0.5.1
.. _0.6.0: https://github.com/nlesc-sherlock/boatswain/compare/0.5.1...0.6.0
.. _0.7.0: https://github.com/nlesc-sherlock/boatswain/compare/0.6.0...0.7.0
