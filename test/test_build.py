"""
    Boatswain test files

    Currently tests only very basic things
"""
import pytest
import docker
import platform
from boatswain import Boatswain


def test_file(bsfile):
    """
        Test creating the Boatswain object
    """
    # Should not throw an exception
    with Boatswain(bsfile):  # NOQA
        pass


@pytest.mark.usefixtures("ensure_clean")
def test_build(bsfile):
    """
        Test exception when there are no images in the file
    """
    with Boatswain(bsfile) as bosun:
        built = bosun.build()
        assert sorted(built['images'], key=str.lower) \
            == sorted(["image4:pytest", "image3:pytest", "image2:pytest",
                       "image1:pytest"], key=str.lower)


@pytest.mark.usefixtures("ensure_clean")
def test_build_verbose(bsfile):
    """
        Test exception when there are no images in the file
    """
    with Boatswain(bsfile, verbose=2) as bosun:
        built = bosun.build()
        assert sorted(built['images'], key=str.lower) \
            == sorted(["image4:pytest", "image3:pytest", "image2:pytest",
                       "image1:pytest"], key=str.lower)


@pytest.mark.usefixtures("ensure_clean")
def test_build_failing(bsfile_single_fail):
    """
        Test exception when building image fails
    """
    with Boatswain(bsfile_single_fail) as bosun:
        built = bosun.build()
        assert not built['images']


@pytest.mark.usefixtures("ensure_clean")
def test_build_failing_continue(bsfile_fail):
    """
        Test exception when building image fails, but keep building the next
    """
    with Boatswain(bsfile_fail, continue_building=True) as bosun:
        built = bosun.build()
        assert sorted(built['images'], key=str.lower) \
            == sorted(["image1:pytest"], key=str.lower)


@pytest.mark.usefixtures("ensure_clean")
def test_build_up_to(bsfile):
    """
        Build only one image with its dependencies
    """
    with Boatswain(bsfile) as bosun:
        built = bosun.build_up_to("image3:pytest", dryrun=True)
        assert sorted(built['images'], key=str.lower) \
            == sorted(["image3:pytest", "image2:pytest",
                       "image1:pytest"], key=str.lower)


@pytest.mark.usefixtures("ensure_clean")
def test_build_dict(bsfile):
    """
        Build only one image with its dependencies
    """
    with Boatswain(bsfile) as bosun:
        built = bosun.build_dict(bsfile['images'])
        assert sorted(built['images'], key=str.lower) \
            == sorted(["image4:pytest", "image3:pytest", "image2:pytest",
                       "image1:pytest"], key=str.lower)


def test_build_no_images(bsfile):
    """
        Test exception when there are no images in the file
    """
    del bsfile['images']
    with Boatswain(bsfile) as bosun:
        built = bosun.build()
        assert built['images'] == []


def test_build_missing_dependency(bsfile):
    """
        Test exception when there is a missing dependency
    """
    del bsfile['images']['image1:pytest']
    with Boatswain(bsfile) as bosun:
        built = bosun.build()
        assert built['images'] == ["image4:pytest"]


def test_build_missing_context(bsfile):
    """
        Test exception when there is context missing
    """
    del bsfile['images']['image1:pytest']['context']
    with Boatswain(bsfile) as bosun:
        with pytest.raises(Exception):
            bosun.build()


def test_build_up_to_no_images(bsfile):
    """
        Test exception when there are no images in the file
    """
    del bsfile['images']
    with Boatswain(bsfile) as bosun:
        built = bosun.build_up_to("image3:pytest")
        assert built['images'] == []


def test_build_dict_no_images(bsfile):
    """
        Test exception when there are no images in the file
    """
    del bsfile['images']
    with Boatswain(bsfile) as bosun:
        built = bosun.build_dict({})
        print(built)
        assert built['images'] == []


def test_build_up_to_dict_no_images(bsfile):
    """
        Test exception when there are no images in the file
    """
    del bsfile['images']
    with Boatswain(bsfile) as bosun:
        built = bosun.build_up_to_dict("image3:pytest", {})
        assert built['images'] == []


def test_build_no_organisation(bsfile):
    """
        Test exception when there is no organisation in the file
    """
    del bsfile['organisation']
    with pytest.raises(Exception):
        with Boatswain(bsfile):  # NOQA
            pass


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
    path = "test/docker/linux/image1"
    if platform.system() == 'Windows':
        path = "test\\docker\\windows\\image1"
    client.images.build(path=path)
    with Boatswain(bsfile) as bosun:
        cleaned = bosun.clean()
        assert cleaned['images']


def test_clean_no_images(bsfile):
    """
        Test the clean function

        test it first, because we need it later
    """
    del bsfile['images']
    with Boatswain(bsfile) as bosun:
        cleaned = bosun.clean()
        assert not cleaned['images']


@pytest.mark.usefixtures("ensure_built")
def test_clean_up_to(bsfile):
    """
        Test cleaning images
    """
    with Boatswain(bsfile) as bosun:
        cleaned = bosun.clean_up_to("image3:pytest")
        assert sorted(cleaned['images'], key=str.lower) \
            == sorted(["image3:pytest", "image2:pytest", "image1:pytest"],
                      key=str.lower)


@pytest.mark.usefixtures("ensure_built")
def test_clean_up_to_no_images(bsfile):
    """
        Test cleaning images
    """
    del bsfile['images']
    with Boatswain(bsfile) as bosun:
        cleaned = bosun.clean_up_to("image3:pytest")
        assert not cleaned['images']


@pytest.mark.usefixtures("ensure_built")
def test_clean_dict(bsfile):
    """
        Test cleaning images
    """
    del bsfile['images']
    with Boatswain(bsfile) as bosun:
        cleaned = bosun.clean_dict({})
        assert not cleaned['images']


@pytest.mark.usefixtures("ensure_built")
def test_clean_up_to_dict(bsfile):
    """
        Test cleaning images
    """
    del bsfile['images']
    with Boatswain(bsfile) as bosun:
        cleaned = bosun.clean_up_to_dict("image3:pytest", {})
        assert not cleaned['images']
