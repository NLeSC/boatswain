"""
    Shared fixtures for testing
"""
from io import StringIO
import posixpath
import pytest
import yaml
import docker
import platform

from boatswain import Boatswain


def boatswain_file():
    if platform.system() == 'Windows':
        return boatswain_windows_file()
    else:
        return boatswain_linux_file()


def boatswain_linux_file():
    """
        The shared boatswain file
    """
    return u"""
        version: 1.0
        organisation: boatswain
        images:
            image1:pytest:
                context: test/docker/linux/image1
            image2:pytest:
                context: test/docker/linux/image2
                from: image1:pytest
            image3:pytest:
                context: test/docker/linux/image3
                from: image2:pytest
            image4:pytest:
                context: test/docker/linux/image4
                tag: image12:pytest
    """


def boatswain_windows_file():
    """
        The shared boatswain file
    """
    return u"""
        version: 1.0
        organisation: boatswain
        images:
            image1:pytest:
                context: test\docker\windows\image1
            image2:pytest:
                context: test\docker\windows\image2
                from: image1:pytest
            image3:pytest:
                context: test\docker\windows\image3
                from: image2:pytest
            image4:pytest:
                context: test\docker\windows\image4
                tag: image12:pytest
    """


def boatswain_failing_file():
    if platform.system() == 'Windows':
        return boatswain_windows_failing_file()
    else:
        return boatswain_linux_failing_file()


def boatswain_linux_failing_file():
    """
        A failing boatswain file
    """
    return u"""
        version: 1.0
        organisation: boatswain
        images:
            image1fail:pytest:
                context: test/docker/linux/image1_fail
            image1:pytest:
                context: test/docker/linux/image1
    """


def boatswain_windows_failing_file():
    """
        A failing boatswain file
    """
    return u"""
        version: 1.0
        organisation: boatswain
        images:
            image1fail:pytest:
                context: test\docker\windows\image1_fail
            image1:pytest:
                context: test\docker\windows\image1
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


def image_names(file):
    """
        All image names fully qualified with their organisation
        in both test boatswain files
    """
    images = list(file['images'])

    for key in file['images']:
        image = file['images'][key]
        if 'tag' in image:
            images.append(image['tag'])

    return images


def full_image_names(names, org):
    return [full_name(name, org) for name in names]


def full_name(name, org):
    return posixpath.join(org, name)


def sort_by_dependency(names, images):
    """
        Make sure images that have dependencies are last
    """
    dependencies = []
    while len(names):
        name = names.pop(0)  # get the first image name
        if name in images:
            definition = images[name]
            # check if it has a dependency
            if 'from' in definition and definition['from'] in names:
                # Move this one to the back, because we first need to
                # remove another image that this one depends on
                names.append(name)
            else:
                dependencies.append(name)
    return dependencies


def check_if_exists(client, tag):
    """
        Check whether this image exists.
    """
    try:
        client.images.get(tag)
        return True
    except docker.errors.ImageNotFound:
        return False


@pytest.fixture
def ensure_clean(bsfile, bsfile_fail):
    """
        Make sure the images in the boatswain file
        do not exist without using any boatswain
        functionality

        Also do not remove any exisisting containers
        or images on the system
    """
    bs_org = bsfile['organisation']
    bs_image_names = image_names(bsfile)

    fail_org = bsfile_fail['organisation']
    fail_image_names = image_names(bsfile_fail)

    full_names = full_image_names(bs_image_names, bs_org)
    full_names += full_image_names(fail_image_names, fail_org)

    client = docker.from_env()
    containers = client.containers.list(all=True)
    for container in containers:
        image_id = container.attrs['Image']
        image = client.images.get(image_id)
        if any(name in image.tags for name in full_names):
            # This container is based on one of the test images
            # so we remove it
            container.stop()
            container.remove()

    docker_images = sort_by_dependency(bs_image_names, bsfile['images'])
    for image in docker_images:
        if check_if_exists(client, image):
            client.images.remove(full_name(image, bs_org))

    docker_images = sort_by_dependency(fail_image_names, bsfile_fail['images'])
    for image in docker_images:
        if check_if_exists(client, image):
            client.images.remove(full_name(image, fail_org))

    try:
        client.images.remove("alpine:latest")
    except docker.errors.APIError:
        # Removing alpine:latest may not succeed
        # if there are other dependencies.
        # but we don't care
        print("Alpine latest not removed because of dependencies")


@pytest.fixture
def ensure_built(bsfile):
    """
        Make sure the images in the boatswain file
        do exists
    """
    bosun = Boatswain(bsfile)
    bosun.build()
