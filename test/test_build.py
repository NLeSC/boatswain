"""
    Boatswain test files

    Currently tests only very basic things
"""
import pytest
from boatswain import Boatswain


@pytest.mark.usefixtures("ensure_not_built")
def test_build_dict(bsfile):
    """
        Build only one image with its dependencies
    """
    bosun = Boatswain(bsfile)
    built = bosun.build_dict(bsfile['images'])
    assert sorted(built, key=str.lower) \
        == sorted(["image4", "image3", "image2", "image1"],
                  key=str.lower)


def test_file(bsfile):
    """
        Test creating the Boatswain object
    """
    # Should not throw an exception
    Boatswain(bsfile)


@pytest.mark.usefixtures("ensure_not_built")
def test_build_up_to(bsfile):
    """
        Build only one image with its dependencies
    """
    bosun = Boatswain(bsfile)
    built = bosun.build_up_to("image3", dryrun=True)
    assert sorted(built, key=str.lower) \
        == sorted(["image3", "image2", "image1"], key=str.lower)
