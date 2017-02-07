"""
    Shared fixtures for testing
"""
from io import StringIO
import pytest
import yaml
import docker

from boatswain import Boatswain


def boatswain_file():
    """
        The shared boatswain file
    """
    return u"""
        version: 1.0
        organisation: boatswain
        images:
            image1:
                context: test/docker/image1
            image2:
                context: test/docker/image2
                from: image1
            image3:
                context: test/docker/image3
                from: image2
            image4:
                context: test/docker/image4
                tag: image12
    """


def boatswain_failing_file():
    """
        A failing boatswain file
    """
    return u"""
        version: 1.0
        organisation: boatswain
        images:
            image1fail:
                context: test/docker/image1_fail
    """


@pytest.fixture
def bsfile():
    """
        Shared boatswain file loaded using yaml
    """
    boatswainfile = StringIO(boatswain_file())
    return yaml.load(boatswainfile)


@pytest.fixture
def bsfile_fail():
    """
        Failing boatswain file loaded using yaml
    """
    boatswainfile = StringIO(boatswain_failing_file())
    return yaml.load(boatswainfile)


@pytest.fixture
def ensure_not_built(bsfile):
    """
        Make sure the images in the boatswain file
        do not exist
    """
    bosun = Boatswain(bsfile)
    bosun.clean()


@pytest.fixture
def ensure_built(bsfile):
    """
        Make sure the images in the boatswain file
        do exists
    """
    bosun = Boatswain(bsfile)
    bosun.build()


@pytest.fixture
def ensure_not_built_failing(bsfile_fail):
    """
        Make sure the failing image is not built
    """
    bosun = Boatswain(bsfile_fail)
    bosun.clean()

    client = docker.from_env()
    client.images.remove("alpine:latest")
