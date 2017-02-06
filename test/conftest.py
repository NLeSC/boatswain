"""
    Shared fixtures for testing
"""
from io import StringIO
import pytest
import yaml

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


@pytest.fixture
def bsfile():
    """
        Shared boatswain file loaded using yaml
    """
    boatswainfile = StringIO(boatswain_file())
    return yaml.load(boatswainfile)


@pytest.fixture
def ensure_not_built(bsfile):
    """
        Make sure the images in the boatswain file
        do not exist
    """
    bosun = Boatswain(bsfile)
    bosun.clean()
