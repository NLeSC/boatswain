"""
    Shared fixtures for testing
"""
from io import StringIO
import posixpath
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
            image1:pytest:
                context: test/docker/image1
            image2:pytest:
                context: test/docker/image2
                from: image1:pytest
            image3:pytest:
                context: test/docker/image3
                from: image2:pytest
            image4:pytest:
                context: test/docker/image4
                tag: image12:pytest
    """


def boatswain_failing_file():
    """
        A failing boatswain file
    """
    return u"""
        version: 1.0
        organisation: boatswain
        images:
            image1fail:pytest:
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
def image_names(bsfile, bsfile_fail):
    """
        All image names fully qualified with their organisation
        in both test boatswain files
    """
    org = bsfile['organisation']
    images = [posixpath.join(org, name) for name
              in bsfile['images'].keys()]

    for key in bsfile['images']:
        image = bsfile['images'][key]
        if 'tag' in image:
            images.append(posixpath.join(org, image['tag']))

    org = bsfile_fail['organisation']
    images += [posixpath.join(org, name) for name
               in bsfile_fail['images'].keys()]
    for key in bsfile_fail['images']:
        image = bsfile_fail['images'][key]
        if 'tag' in image:
            images.append(posixpath.join(org, image['tag']))

    return images


@pytest.fixture
def ensure_clean(image_names):
    """
        Make sure the images in the boatswain file
        do not exist without using any boatswain
        functionality

        Also do not remove any exisisting containers
        or images on the system
    """
    client = docker.from_env()
    containers = client.containers.list(all=True)
    for container in containers:
        image_id = container.attrs['Image']
        image = client.images.get(image_id)
        if any(name in image.tags for name in image_names):
            # This container is based on one of the test images
            # so we remove it
            container.stop()
            container.remove()

    docker_images = client.images.list(all=True)
    for image in docker_images:
        if any(name in image.tags for name in image_names):
            client.images.remove(image.id)

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
