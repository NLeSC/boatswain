"""
    Boatswain test files

    Currently tests only very basic things
"""
import pytest
import docker
from boatswain import Boatswain


def test_file(bsfile):
    """
        Test creating the Boatswain object
    """
    # Should not throw an exception
    Boatswain(bsfile)


@pytest.mark.usefixtures("ensure_clean")
def test_build(bsfile):
    """
        Test exception when there are no images in the file
    """
    bosun = Boatswain(bsfile)
    built = bosun.build()
    assert sorted(built, key=str.lower) \
        == sorted(["image4:pytest", "image3:pytest", "image2:pytest",
                   "image1:pytest"], key=str.lower)


@pytest.mark.usefixtures("ensure_clean")
def test_build_verbose(bsfile):
    """
        Test exception when there are no images in the file
    """
    bosun = Boatswain(bsfile)
    built = bosun.build(verbose=True)
    assert sorted(built, key=str.lower) \
        == sorted(["image4:pytest", "image3:pytest", "image2:pytest",
                   "image1:pytest"], key=str.lower)


@pytest.mark.usefixtures("ensure_clean")
def test_build_failing(bsfile_fail):
    """
        Test exception when building image fails
    """
    bosun = Boatswain(bsfile_fail)
    built = bosun.build()
    assert not built


@pytest.mark.usefixtures("ensure_clean")
def test_build_up_to(bsfile):
    """
        Build only one image with its dependencies
    """
    bosun = Boatswain(bsfile)
    built = bosun.build_up_to("image3:pytest", dryrun=True)
    assert sorted(built, key=str.lower) \
        == sorted(["image3:pytest", "image2:pytest",
                   "image1:pytest"], key=str.lower)


@pytest.mark.usefixtures("ensure_clean")
def test_build_dict(bsfile):
    """
        Build only one image with its dependencies
    """
    bosun = Boatswain(bsfile)
    built = bosun.build_dict(bsfile['images'])
    assert sorted(built, key=str.lower) \
        == sorted(["image4:pytest", "image3:pytest", "image2:pytest",
                   "image1:pytest"], key=str.lower)


def test_build_no_images(bsfile):
    """
        Test exception when there are no images in the file
    """
    del bsfile['images']
    bosun = Boatswain(bsfile)
    built = bosun.build()
    assert built == []


def test_build_missing_dependency(bsfile):
    """
        Test exception when there is a missing dependency
    """
    del bsfile['images']['image1:pytest']
    bosun = Boatswain(bsfile)
    built = bosun.build()
    assert built == ["image4:pytest"]


def test_build_missing_context(bsfile):
    """
        Test exception when there is context missing
    """
    del bsfile['images']['image1:pytest']['context']
    bosun = Boatswain(bsfile)
    with pytest.raises(Exception):
        bosun.build()


def test_build_up_to_no_images(bsfile):
    """
        Test exception when there are no images in the file
    """
    del bsfile['images']
    bosun = Boatswain(bsfile)
    built = bosun.build_up_to("image3:pytest")
    assert built == []


def test_build_dict_no_images(bsfile):
    """
        Test exception when there are no images in the file
    """
    del bsfile['images']
    bosun = Boatswain(bsfile)
    built = bosun.build_dict({})
    assert built == []


def test_build_up_to_dict_no_images(bsfile):
    """
        Test exception when there are no images in the file
    """
    del bsfile['images']
    bosun = Boatswain(bsfile)
    built = bosun.build_up_to_dict("image3:pytest", {})
    assert built == []


def test_build_no_organisation(bsfile):
    """
        Test exception when there is no organisation in the file
    """
    del bsfile['organisation']
    with pytest.raises(Exception):
        Boatswain(bsfile)


#
# Continue testing cleaning
# Building should succeed by now
#
@pytest.mark.usefixtures("ensure_built")
def test_clean(bsfile):
    """
        Test the clean function

        test it first, because we need it later
    """
    # Build an image by hand to remove
    client = docker.from_env()
    client.images.build(path="test/docker/image1")
    bosun = Boatswain(bsfile)
    cleaned = bosun.clean()
    assert cleaned


def test_clean_no_images(bsfile):
    """
        Test the clean function

        test it first, because we need it later
    """
    del bsfile['images']
    bosun = Boatswain(bsfile)
    cleaned = bosun.clean()
    assert not cleaned


@pytest.mark.usefixtures("ensure_built")
def test_clean_up_to(bsfile):
    """
        Test cleaning images
    """
    bosun = Boatswain(bsfile)
    cleaned = bosun.clean_up_to("image3:pytest")
    assert sorted(cleaned, key=str.lower) \
        == sorted(["image3:pytest", "image2:pytest", "image1:pytest"],
                  key=str.lower)


@pytest.mark.usefixtures("ensure_built")
def test_clean_up_to_no_images(bsfile):
    """
        Test cleaning images
    """
    del bsfile['images']
    bosun = Boatswain(bsfile)
    cleaned = bosun.clean_up_to("image3:pytest")
    assert not cleaned


@pytest.mark.usefixtures("ensure_built")
def test_clean_dict(bsfile):
    """
        Test cleaning images
    """
    del bsfile['images']
    bosun = Boatswain(bsfile)
    cleaned = bosun.clean_dict({})
    assert not cleaned


@pytest.mark.usefixtures("ensure_built")
def test_clean_up_to_dict(bsfile):
    """
        Test cleaning images
    """
    del bsfile['images']
    bosun = Boatswain(bsfile)
    cleaned = bosun.clean_up_to_dict("image3:pytest", {})
    assert not cleaned
