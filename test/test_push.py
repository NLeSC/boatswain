"""
    Boatswain test files
"""
import pytest
from boatswain import Boatswain


@pytest.mark.skip(reason="Automatic testing of pushing is difficult")
@pytest.mark.usefixtures("ensure_built")
def test_push(bsfile):
    """
        Test creating the Boatswain object
    """
    # Should not throw an exception
    with Boatswain(bsfile) as bosun:  # NOQA
        pushed = bosun.push()

        assert sorted(pushed, key=str.lower) \
            == sorted(["image4:pytest", "image3:pytest", "image2:pytest",
                       "image1:pytest"], key=str.lower)


@pytest.mark.skip(reason="Automatic testing of pushing is difficult")
@pytest.mark.usefixtures("ensure_built")
def test_push_dict(bsfile):
    """
        Push only one image with its dependencies
    """
    with Boatswain(bsfile) as bosun:
        pushed = bosun.push_dict(bsfile['images'])
        assert sorted(pushed, key=str.lower) \
            == sorted(["image4:pytest", "image3:pytest", "image2:pytest",
                       "image1:pytest"], key=str.lower)


@pytest.mark.skip(reason="Automatic testing of pushing is difficult")
@pytest.mark.usefixtures("ensure_built")
def test_push_up_to(bsfile):
    """
        Push only one image with its dependencies
    """
    with Boatswain(bsfile) as bosun:
        pushed = bosun.push_up_to("image3:pytest", dryrun=True)
        assert sorted(pushed, key=str.lower) \
            == sorted(["image3:pytest", "image2:pytest",
                       "image1:pytest"], key=str.lower)
