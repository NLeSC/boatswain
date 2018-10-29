.. image:: https://travis-ci.org/NLeSC/boatswain.svg?branch=master
    :target: https://travis-ci.org/NLeSC/boatswain
.. image:: https://ci.appveyor.com/api/projects/status/5n7uj8ownch05e34/branch/master?svg=true
    :target: https://ci.appveyor.com/project/NLeSC/boatswain/branch/master
.. image:: https://api.codacy.com/project/badge/Grade/67dac954463045d48541657bad72dcb2
    :target: https://www.codacy.com/app/b-weel/boatswain?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=nlesc-sherlock/boatswain&amp;utm_campaign=Badge_Grade
.. image:: https://api.codacy.com/project/badge/Coverage/67dac954463045d48541657bad72dcb2
    :target: https://www.codacy.com/app/b-weel/boatswain?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=nlesc-sherlock/boatswain&amp;utm_campaign=Badge_Coverage
.. image:: https://zenodo.org/badge/80722427.svg
   :target: https://zenodo.org/badge/latestdoi/80722427

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

Building
--------

You can build the images defined in the boatswain file using the following command. This invokes the docker build process for each image in the order so the dependencies are built before the dependent image.

::

    $ boatswain build

Cleaning
--------

You can clean the images that are defined in the boatswain file.

::

    $ boatswain clean
    
Pushing
-------

You can push the built images to dockerhub using the `push` command. It will be pushed to `organisation/imagetag` on dockerhub.

::

    $ boatswain push

Extra Options
=============
-h
    Display the options

-q, --quiet
    Don't display any output

-k, --keep_building
    Keep building images even if an error occurs

--dryrun
    Do not actually execute the command, just go through the motions

-b <boatswain_file>, --boatswain_file <boatswain_file>
    Override the default boatswain file (boatswain.yml)

-f, --force
    Force building the images, even if they already exist
    (only for build)

Debugging your build
====================
When your build does not go the way you expected boatswain
can display some more information by using:

-v
    Verbose mode, displays a build progress for each image

-vv
    Very verbose mode, displays the output of the docker build process

--debug
    Debug mode, displays debug information of boatswain
    as well as the output of the docker build process
