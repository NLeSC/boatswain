"""
    Tests for the boatswain util package
"""
from boatswain.util import extract_step, extract_id, find_dependencies, \
    extract_container_id_removal, extract_container_id


def test_extract_step():
    """
        Test step extraction
    """
    step, total = extract_step("Step 3/9: Sometext")
    assert step == 3
    assert total == 9


def test_extract_id():
    """
        Test id extraction
    """
    ident = extract_id('Successfully built ad8402983js938')
    assert ident == 'ad8402983js938'


def test_extract_container_id_removal():
    """
        Test id extraction
    """
    ident = extract_container_id_removal(
        "Removing intermediate container 816abeca3961")
    assert ident == "816abeca3961"


def test_extract_container_id():
    """
        Test id extraction
    """
    ident = extract_container_id("---> Running in 816abeca3961")
    assert ident == '816abeca3961'


def test_find_dependencies(bsfile):
    """
        Find all dependencies of an image
    """
    dependencies = find_dependencies("image3:pytest", bsfile['images'])
    assert sorted(dependencies, key=str.lower) == sorted(
        ["image3:pytest", "image2:pytest", "image1:pytest"], key=str.lower)
