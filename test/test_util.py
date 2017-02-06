"""
    Tests for the boatswain util package
"""
from boatswain.util import extract_step, extract_id, find_dependencies


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


def test_find_dependencies(bsfile):
    """
        Find all dependencies of an image
    """
    dependencies = find_dependencies("image3", bsfile['images'])
    assert sorted(dependencies, key=str.lower) == sorted(
        ["image3", "image2", "image1"], key=str.lower)
