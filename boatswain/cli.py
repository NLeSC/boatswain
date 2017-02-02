from __future__ import absolute_import

import argparse
import yaml
import os
import logging

from .boatswain import Boatswain

def argparser():
    desc = 'Builds docker images based on a docker-compose style yaml file'
    parser = argparse.ArgumentParser(description=desc)

    subparsers = parser.add_subparsers(help='sub-command help', dest='command')
    subparsers.required = True

    buildparser = subparsers.add_parser(
        'build', help='builds images'
    )

    buildparser.add_argument(
        '--boatswain_file', '-b', help='Override the default boatswain file',
        default='boatswain.yml'
    )

    return parser

def main():
    #logging.basicConfig(level=logging.DEBUG)
    arguments = argparser().parse_args()

    command = arguments.command
    with open(arguments.boatswain_file) as yamlfile:
        bsfile = yaml.load(yamlfile)

    print(bsfile)
    bs = Boatswain(bsfile)

    if command == 'build':
        bs.build()