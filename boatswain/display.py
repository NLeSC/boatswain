# -*- coding: utf8 -*-
from __future__ import print_function

import sys

from .bcolors import bcolors


class Node(object):
    def __init__(self, label):
        self.label = label
        self.children = []

    def find_child(self, label):
        if self.label == label:
            return self
        else:
            return self.find_in_children(self.children, label)

    def find_in_children(self, children, label):
        for child in children:
            if child.label == label:
                return child
            else:
                child = self.find_in_children(child.children, label)
                if child:
                    return child
        return False


class Tree(object):
    _child = u'\u251c'         # ├
    _bar_space = u'\u2502   '  # │ + 3 spaces
    _last_child = u'\u2514'    # └
    _dash = u'\u2500\u2500'    # ──
    _space = u'    '           # 4 spaces

    def __init__(self):
        self.cache = []
        self.root = Node('root')

    def print_boatswain_tree(self, boatswain):
        self.cache = []
        self.extract_tree(boatswain)
        self.print_tree()

    def extract_tree(self, yamlfile):
        images = yamlfile['images']
        names = sorted(list(images))
        while len(names) > 0:
            name = names.pop(0)  # get the first image name
            definition = images[name]

            if 'from' in definition:
                if definition['from'] not in self.cache:
                    # We depend on another image that has
                    # not been processed yet
                    if definition['from'] not in names:
                        # Zomg it doesn't exists :O
                        print(
                            bcolors.fail(
                                "Error: could not find a recipe for "
                            ) +
                            bcolors.blue(definition['from']) +
                            bcolors.fail(" which is needed for ") +
                            bcolors.blue(name) + "\n", file=sys.stderr
                        )
                    else:
                        # The parent image still needs to be processed
                        names.append(name)
                else:
                    # The parent image has been processed, let's find it.
                    child = self.root.find_child(definition['from'])
                    child.children.append(Node(name))
                    self.cache.append(name)
            else:
                # This is a root image
                self.root.children.append(Node(name))
                self.cache.append(name)
        return self.root

    def print_tree(self):
        self.print_recursive(self.root, [])

    def print_recursive(self, node, last):
        if not node:
            return
        else:
            if node.label is not 'root':
                for l in last[:-1]:
                    if l:
                        print(self._space, end="")
                    else:
                        print(self._bar_space, end="")

                if last[-1]:
                    print(self._last_child, end="")
                else:
                    print(self._child, end="")

                print(self._dash + " " + node.label)

            if len(node.children) > 0:
                for index, child in enumerate(node.children):
                    last.append(index == (len(node.children) - 1))
                    self.print_recursive(child, last)
                    last.pop()
