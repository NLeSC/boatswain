"""
    Boatswain is a simple build system for docker images.

    The build is done from a yaml file that is inspired by
    a docker-compose file.

    The Boatswain class accepts any dictionary with the
    structure in the example below

    Example boatswain file:
        version: 1.0
        organisation: myorg
        tag1:
            context: example/docker1
            from: tag3
        tag2:
            context: example/docker2
            from: tag3
        tag3:
            context: example/docker3
"""
from __future__ import absolute_import, print_function

import logging
import posixpath
import json

import docker
import progressbar

from .bcolors import bcolors
from .util import find_dependencies, extract_step, extract_id

class Boatswain(object):
    """
        Boatswain is a simple build system for docker images.

        Requires a boatswain dictionary as shown below:
        version: 1.0
        organisation: myorg
        tag1:
            context: example/docker1
            from: tag3
        tag2:
            context: example/docker2
            from: tag3
        tag3:
            context: example/docker3
    """

    def __init__(self, description):
        self.client = docker.from_env()
        self.description = description
        self.cache = {}
        self.logger = logging.getLogger('boatswain')
        if 'organisation' in self.description:
            self.organisation = self.description['organisation']
        else:
            raise Exception('No organisation specified in the boatswain file!')

        if 'images' in self.description:
            self.images = self.description['images']
        else:
            self.logger.warn("No images defined in the boatswain description")


    def build(self, dryrun=False, force=False, verbose=False):
        """
            Builds all images defined in the dictionary
        """
        if self.images:
            self.logger.debug(self.images)
            return self.build_dict(self.images, dryrun=dryrun, force=force, verbose=verbose)
        else:
            self.logger.warn('No images defined in boatswain file')


    def build_up_to(self, name, dryrun=False, force=False, verbose=False):
        """
            Builds the image with the given name and all of
            the images it depends on recursively
        """
        if self.images:
            self.logger.debug(self.images)
            return self.build_up_to_dict(name, self.images, dryrun=dryrun,
                                         force=force, verbose=verbose)
        else:
            self.logger.warn('No images defined in boatswain file')



    def build_dict(self, images, dryrun=False, force=False, verbose=False):
        """
            Build all the images and their dependencies as they are defined
            in the images dictionary

            Example dictionary:
            tag1:
                context: example/docker1
                from: tag3
            tag2:
                context: example/docker2
                from: tag3
            tag3:
                context: example/docker3
        """
        self.logger.debug(images)
        if not images:
            return False
        else:
            names = list(images)
            return self.build_list(names, images, dryrun=dryrun, force=force, verbose=verbose)


    def build_up_to_dict(self, name, images, dryrun=False, force=False, verbose=False):
        """
           Build image name and all its dependencies from a dictionary
        """
        self.logger.debug("build_up_to_dict: %s", images)
        if not images:
            return False
        else:
            names = find_dependencies(name, images)
            self.logger.debug(names)
            return self.build_list(names, images, dryrun=dryrun, force=force, verbose=verbose)


    def build_list(self, names, images, dryrun=False, force=False, verbose=False):
        """
            Builds the all images given in names and all the dependencies
            of these images
        """
        built = []
        self.logger.debug("build_list: %s", names)
        while len(names):
            name = names.pop(0) # get the first image name
            definition = images[name]

            # Make sure all the dependencies have been built
            if 'from' in definition and definition['from'] not in self.cache:
                if definition['from'] not in names:
                    raise Exception("Could not find a recipe to build",
                                    definition['from'], "which is needed for", name)
                else:
                    # Move this one to the back, because it from on another image
                    names.append(name)
            else:
                if self.build_one(name, definition, dryrun=dryrun, force=force, verbose=verbose):
                    built.append(name)

        return built


    def build_one(self, name, definition, dryrun=False, force=False, verbose=False):
        """
            Builds a single docker image.
            The image this docker image depends on should already be built!
        """

        self.logger.debug("build_one: Building %s", name)
        self.logger.debug("build_one: definition: %s", definition)

        tag = self.get_full_tag(name, definition)
        dobuild = self.check_for_build(name, tag, verbose=verbose, force=force)

        if dobuild:
            if 'context' in definition:
                directory = definition['context']
            else:
                raise Exception("No context defined in file, aborting")

            print("Now building " + bcolors.blue(name) +
                  " in directory " + bcolors.blue(directory) +
                  " and tagging as " + bcolors.blue(tag))

            if not dryrun:
                ident = self._build_one(name, tag, directory, force=force, verbose=verbose)
            else:
                ident = 'testidentifier'
                self.cache[name] = ident

            print("Successfully built image with tag:" + bcolors.blue(tag) +
                  " docker id is: " + bcolors.blue(ident))

            return True


    def check_for_build(self, name, tag, verbose=False, force=False):
        """
           Check whether we should build this image.
        """
        if force:
            return True
        else:
            try:
                image = self.client.images.get(tag)
                ident = image.short_id
                if ident.startswith('sha256:'):
                    ident = ident[7:]
                self.cache[name] = ident
                if verbose:
                    print("Found image for tag " + bcolors.blue(name) +
                          " that is already built with id: " + bcolors.blue(ident))
                return False
            except docker.errors.ImageNotFound:
                return True


    def check_if_exists(self, tag, verbose=False):
        """
           Check whether this image exists.
        """
        try:
            image = self.client.images.get(tag)
            return True
        except docker.errors.ImageNotFound:
            return False


    def clean(self, dryrun=False, force=False, verbose=False):
        """
            Builds all images defined in the dictionary
        """
        if self.images:
            self.logger.debug(self.images)
            return self.clean_dict(self.images, dryrun=dryrun, force=force, verbose=verbose)
        else:
            self.logger.warn('No images defined in boatswain file')


    def clean_dict(self, images, dryrun=False, force=False, verbose=False):
        if not images:
            return False
        else:
            names = list(images)
            return self.clean_list(names, images, dryrun=dryrun, force=force, verbose=verbose)


    def clean_list(self, names, images, dryrun=False, force=False, verbose=False):
        while len(names):
            name = names.pop(0) # get the first image name
            definition = images[name]

            # Make sure all the dependencies have been built
            if 'from' in definition and definition['from'] in names:
                # Move this one to the back, because we first need to
                # remove another image that this one depends on
                names.append(name)
            else:
                self.clean_one(name, definition, dryrun=dryrun, force=force, verbose=verbose)


    def clean_one(self, name, definition, dryrun=False, force=False, verbose=False):
        tag = self.get_full_tag(name, definition)
        exists = self.check_if_exists(tag)
        if exists:
            print("removing image with tag: "+bcolors.blue(tag))
            self.client.images.remove(tag)

    def get_full_tag(self, name, definition):
        """
            Get the full tag for image
        """
        if 'tag' in definition:
            tag = definition['tag']
        else:
            tag = name

        tag = posixpath.join(self.organisation, tag)

        return tag

    def _build_one(self, name, tag, directory, force=False, verbose=False):
        gen = self.client.api.build(path=directory, tag=tag, rm=True, nocache=force)
        probress_bar = None
        # The build function returns a generator with what would normally
        # be the console output. Here we parse it to find which step we
        # are on (e.g. the layer)
        # and whether it was successfully built, although if it does not
        # build successfully we will get an Exception
        if verbose:
            print(bcolors.warning(name+": "), end="")
        for response in gen:
            line = json.loads(response.decode("utf-8"))['stream']
            if verbose:
                if line.endswith("\n"):
                    print(bcolors.blue(line), end="")
                    print(bcolors.warning(name+": "), end="")
                else:
                    print(bcolors.blue(line), end="")
            if line.startswith('Step'):
                step, total = extract_step(line)
                if probress_bar is None:
                    probress_bar = progressbar.ProgressBar(max_value=total,
                                                           redirect_stdout=True)
                    probress_bar.update(step)
                else:
                    probress_bar.update(step)
            elif line.startswith('Successfully built'):
                ident = extract_id(line)
                self.cache[name] = ident

        if probress_bar is not None:
            probress_bar.finish()

        if ident:
            return ident
        else:
            return False
