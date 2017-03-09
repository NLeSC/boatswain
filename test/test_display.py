"""
    Boatswain test files

    Currently tests only very basic things
"""
from boatswain import Tree


def test_extract(bsfile):
    tree = Tree()
    root = tree.extract_tree(bsfile)
    assert len(root.children) > 0


def test_find_child(bsfile):
    tree = Tree()
    root = tree.extract_tree(bsfile)
    assert root.find_child('image3:pytest')


def test_print(bsfile):
    tree = Tree()
    tree.print_boatswain_tree(bsfile)
