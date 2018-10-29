import pytest
from boatswain import argparser
from boatswain.cli import main


def test_image():
    parser = argparser()
    args = parser.parse_args('build image2'.split())

    assert args.imagename == 'image2'


def test_no_image():
    parser = argparser()
    args = parser.parse_args('build'.split())

    assert not args.imagename


def test_verbose():
    parser = argparser()
    args = parser.parse_args('build -v'.split())

    assert args.verbose


def test_empty_args():
    with pytest.raises(SystemExit):
        main()
