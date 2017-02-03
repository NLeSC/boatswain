"""
    Boatswain test files

    Currently tests only very basic things
"""
import StringIO
import logging

import pytest
import yaml

from boatswain import Boatswain

def boatswain_file():
    """
        The shared boatswain file
    """
    return """
        version: 1.0
        organisation: test1
        images:
            image1:
                context: image1
            image2:
                context: image2
                from: image1
            image3:
                context: image3
                from: image2
            image4:
                context: image4
                tag: image12
    """


@pytest.fixture
def bsfile():
    """
        Shared boatswain file loaded using yaml
    """
    boatswainfile = StringIO.StringIO(boatswain_file())
    return yaml.load(boatswainfile)


def test_file(bsfile):
    """
        Test creating the Boatswain object
    """
    # Should not throw an exception
    Boatswain(bsfile)


def test_up_to(bsfile):
    """
        Build only one image with its dependencies
    """
    logging.basicConfig(level=logging.DEBUG)
    bosun = Boatswain(bsfile)
    built = bosun.build_up_to("image3", dryrun=True)
    assert sorted(built, key=str.lower) == sorted(["image3", "image2", "image1"], key=str.lower)

#if __name__ == "__main__":
#    f = bsfile()
#    test_up_to(f)
