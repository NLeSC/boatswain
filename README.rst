.. image:: https://travis-ci.org/nlesc-sherlock/boatswain.svg?branch=master
    :target: https://travis-ci.org/nlesc-sherlock/boatswain


Boatswain
=========
Boatswain is a simple build system for docker images.

It is especially usefull when you have multiple docker images that
depend on each other.


Installation
============

Boatswain is a simple python script you can install with pip

::

    $ pip install boatswain


Usage
=====
Create a file called boatswain.yml for your project with the following
syntax, which is heavily based on docker-compose.

.. code-block:: yaml

    version: 1.0                    # The version of the boatswain yaml
    organisation: boatswain         # Your dockerhub organisation
    images:
        image1:pytest:              # the key will be used to tag the image
            context: docker/image1  # The path of the dockerfile
        image2:pytest:
            context: docker/image2
            from: image1:pytest     # This image depends on the other image
        image3:pytest:
            context: docker/image3
            from: image2:pytest
        image4:pytest:
            context: docker/image4
            tag: image12:pytest     # This image will be tagged with this
