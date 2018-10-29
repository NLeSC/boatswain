"""
    Boatswain command line interface
"""
from __future__ import absolute_import

import argparse
import sys
import logging
import yaml
from .boatswain import Boatswain
from .bcolors import bcolors
from .display import Tree


def argparser():
    """
        Define the argument parsers for Boatswain

        We use subparsers, currently the implemented subparsers are:
        - build: building docker images
    """
    desc = 'Builds docker images based on a docker-compose style yaml file'
    parser = argparse.ArgumentParser(description=desc)

    subparsers = parser.add_subparsers(help='sub-command help', dest='command')
    subparsers.required = True

    #
    # Common options
    #
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        '-v', '--verbose', help="Verbose output",
        action='store_true'
    )
    common.add_argument(
        '-vv', '--verboseverbose', help="Very Verbose output",
        action='store_true'
    )
    common.add_argument(
        '-q', '--quiet', help="Quiet output",
        action='store_true'
    )
    common.add_argument(
        '-k', '--keep_building', help="Keep building even if errors occur",
        action='store_true'
    )
    common.add_argument(
        '--dryrun', help="Do a dry run don't actually build",
        action='store_true'
    )
    common.add_argument(
        '--debug', help="Debug boatswain itself",
        action='store_true'
    )
    common.add_argument(
        '-b', '--boatswain_file', help='Override the default boatswain file',
        default='boatswain.yml'
    )

    #
    # Build parser
    #
    buildparser = subparsers.add_parser(
        'build', help='builds the images specified in the boatswain.yml file',
        parents=[common]
    )
    buildparser.add_argument(
        '-f', '--force',
        help="Force building images even if they already exists",
        action='store_true'
    )
    buildparser.add_argument(
        'imagename', help="Name of the image to build",
        nargs='?'
    )

    #
    # Clean parser
    #
    cleanparser = subparsers.add_parser(
        'clean', help='Clean the images specified in the boatswain.yml file',
        parents=[common]
    )
    cleanparser.add_argument(
        'imagename', help="Name of the image to clean",
        nargs='?'
    )

    #
    # Push parser
    #
    pushparser = subparsers.add_parser(
        'push', help='Push the images specified in the boatswain.yml file to dockerhub',
        parents=[common]
    )
    pushparser.add_argument(
        'imagename', help="Name of the image to push",
        nargs='?'
    )

    #
    # Tree parser
    #
    subparsers.add_parser(
        'tree', help='Print the tree of the boatswain.yml file',
        parents=[common]
    )

    return parser


def print_summary(result, command):

    print(bcolors.header("\nBuild summary"))
    if command == 'build':
        verbed = 'built'
    else:
        verbed = command + 'ed'

    print(bcolors.blue(verbed + ':'))
    for image in result['images']:
        print('    ' + image)

    if not result['success']:
        print(bcolors.fail('Failed to ' + command + ':'))
        for image in result['failed']:
            print('    ' + image)

    if result['success']:
        final = bcolors.green('success')
    else:
        final = bcolors.fail('failure')
    print("Final result was deemed a: " + final)


def main():
    """
        Run the boatswain command using the given arguments
    """
    parser = argparser()
    if len(sys.argv) < 1:
        parser.print_help()
        sys.exit(1)

    arguments = parser.parse_args()

    if not arguments.quiet:
        print(bcolors.header("Welcome to Boatswain"))

    if arguments.debug:
        logging.basicConfig(level=logging.DEBUG)

    command = arguments.command
    try:
        with open(arguments.boatswain_file) as yamlfile:
            bsfile = yaml.load(yamlfile)
    except IOError as error:
        print(bcolors.fail(error.filename + ": " + error.strerror))
        sys.exit(-error.errno)

    verbosity_level = 1     # standard verbosity
    if arguments.quiet:
        verbosity_level = 0
    elif arguments.verbose:
        verbosity_level = 2
    elif arguments.verboseverbose:
        verbosity_level = 3

    with Boatswain(bsfile,
                   verbose=verbosity_level,
                   continue_building=arguments.keep_building) as bosun:
        if command == 'tree':
            tree = Tree()
            tree.print_boatswain_tree(bsfile)
            sys.exit(0)
        elif command == 'build':
            if arguments.imagename:
                result = bosun.build_up_to(arguments.imagename, dryrun=arguments.dryrun, force=arguments.force)
            else:
                result = bosun.build(dryrun=arguments.dryrun, force=arguments.force)

        elif command == 'clean':
            if arguments.imagename:
                result = bosun.clean_up_to(arguments.imagename, dryrun=arguments.dryrun)
            else:
                result = bosun.clean(dryrun=arguments.dryrun)

        elif command == 'push':
            if arguments.imagename:
                result = bosun.push_up_to(arguments.imagename, dryrun=arguments.dryrun)
            else:
                result = bosun.push(dryrun=arguments.dryrun)

    if verbosity_level >= 1:
        print_summary(result, command)
    if result['success']:
        sys.exit(0)
    else:
        sys.exit(1)
