from boatswain import argparser


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
