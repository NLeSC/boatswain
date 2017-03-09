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
import sys
import posixpath
import json
import threading

import docker
import progressbar
from progressbar import Percentage, Bar, Timer, SimpleProgress, Counter

from .bcolors import bcolors
from .util import find_dependencies, extract_step, extract_id
from .errors import BuildError, ParseError


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
        self.logger = logging.getLogger('boatswain')

        # Docker interaction
        self.client = docker.from_env(version="auto")
        self.description = description

        # Cache of images built by boatswain
        self.cache = {}

        # Progress
        self.progress_bar = None
        self.timer = None
        self.done = False
        self.total = None
        self.step = None

        if 'organisation' in self.description:
            self.organisation = self.description['organisation']
        else:
            raise Exception('No organisation specified in the boatswain file!')

        if 'images' in self.description:
            self.images = self.description['images']
        else:
            # Should not having images be an exception?
            self.images = {}
            self.logger.warn("No images defined in the boatswain description")

    def build(self, dryrun=False, force=False, verbose=1):
        """
            Builds all images defined in the dictionary
        """
        return self._do_action('build', dryrun=dryrun, force=force,
                               verbose=verbose)

    def clean(self, dryrun=False):
        """
            Removes all images defined in the dictionary
        """
        return self._do_action('clean', dryrun=dryrun)

    def push(self, dryrun=False, verbose=1):
        """
            Push the images defined in the dictionary to the repository
        """
        return self._do_action('push', dryrun=dryrun, verbose=verbose)

    def _do_action(self, action, **kwargs):
        if not self.images:
            self.logger.warn('No images defined in boatswain file')
            return []
        else:
            return self._do_action_dict(action, self.images, **kwargs)

    def build_dict(self, images, dryrun=False, force=False, verbose=1):
        """
            Build all images in the dictionary
        """
        return self._do_action_dict('build', images, dryrun=dryrun,
                                    force=force, verbose=verbose)

    def clean_dict(self, images, dryrun=False):
        """
            Remove all images in the dictionary
        """
        return self._do_action_dict('clean', images, dryrun=dryrun)

    def push_dict(self, images, dryrun=False, verbose=1):
        """
            Remove all images in the dictionary
        """
        return self._do_action_dict('push', images, dryrun=dryrun,
                                    verbose=verbose)

    def _do_action_dict(self, action, images, **kwargs):
        """
            Removes all images defined in the dictionary
        """
        if not images:
            return []
        else:
            names = list(images)
            if action == 'build':
                return self.build_list(names, images, **kwargs)
            elif action == 'clean':
                return self.clean_list(names, images, **kwargs)
            elif action == 'push':
                return self.push_list(names, images, **kwargs)

    def clean_up_to(self, name, dryrun=False):
        """
            Cleans the image with the given name and all of
            the images it depends on recursively
        """
        return self.clean_up_to_dict(name, self.images, dryrun=dryrun)

    def build_up_to(self, name, dryrun=False, force=False, verbose=1):
        """
            Builds the image with the given name and all of
            the images it depends on recursively
        """
        return self.build_up_to_dict(name, self.images, dryrun=dryrun,
                                     force=force, verbose=verbose)

    def push_up_to(self, name, dryrun=False, verbose=1):
        """
            Pushes the image with the given name and all of
            the images it depends on recursively
        """
        return self.push_up_to_dict(name, self.images, dryrun=dryrun,
                                    verbose=verbose)

    def clean_up_to_dict(self, name, images, dryrun=False):
        """
            Cleans the image with the given name and all of
            the images it depends on recursively
        """
        return self._process_up_to_dict('clean', name, images,
                                        dryrun=dryrun)

    def build_up_to_dict(self, name, images, dryrun=False, force=False,
                         verbose=1):
        """
            Builds the image with the given name and all
            of the images it depends on recursively
        """
        return self._process_up_to_dict('build', name, images, dryrun=dryrun,
                                        force=force, verbose=verbose)

    def push_up_to_dict(self, name, images, dryrun=False, verbose=1):
        """
            Pushes the image with the given name and all of
            the images it depends on recursively
        """
        return self._process_up_to_dict('push', name, images,
                                        dryrun=dryrun, verbose=verbose)

    def _process_up_to_dict(self, action, name, images, dryrun=False,
                            force=False, verbose=1):
        """
           Build image name and all its dependencies from a dictionary
        """
        self.logger.debug("build_up_to_dict: %s", images)
        if not images:
            self.logger.warn('No images defined')
            return []
        elif name not in images:
            print(bcolors.fail("Cannot build undefined image " + name))
        else:
            names = find_dependencies(name, images)
            self.logger.debug(names)
            if action == 'build':
                return self.build_list(names, images, dryrun=dryrun,
                                       force=force, verbose=verbose)
            elif action == 'clean':
                return self.clean_list(names, images, dryrun=dryrun)
            elif action == 'push':
                return self.push_list(names, images, dryrun=dryrun,
                                      verbose=verbose)

    def build_list(self, names, images, dryrun=False, force=False,
                   verbose=1):
        """
            Builds the all images given in names and all the dependencies
            of these images
        """
        built = []
        self.logger.debug("build_list: %s", names)
        while len(names):
            name = names.pop(0)  # get the first image name
            definition = images[name]

            # Make sure all the dependencies have been built
            if 'from' in definition and definition['from'] not in self.cache:
                if definition['from'] not in names:
                    print(bcolors.fail
                          (
                              "Error: could not find a recipe to build "
                          ) +
                          bcolors.blue(definition['from']) +
                          bcolors.fail(" which is needed for ") +
                          bcolors.blue(name) + "\n", file=sys.stderr)
                    # do not append this image
                else:
                    # Move this one to the back, because it from on another
                    # image
                    names.append(name)
            else:
                if self.build_one(name, definition, dryrun=dryrun, force=force,
                                  verbose=verbose):
                    built.append(name)

        return built

    def clean_list(self, names, images, dryrun=False):
        """
            Removes all images defined in the list
        """
        cleaned = []
        while len(names):
            name = names.pop(0)  # get the first image name
            definition = images[name]

            # Make sure all the dependencies have been built
            if 'from' in definition and definition['from'] in names:
                # Move this one to the back, because we first need to
                # remove another image that this one depends on
                names.append(name)
            else:
                if self.clean_one(name, definition, dryrun=dryrun):
                    cleaned.append(name)
        return cleaned

    def push_list(self, names, images, dryrun=False, verbose=1):
        """
            Removes all images defined in the list
        """
        pushed = []
        while len(names):
            name = names.pop(0)  # get the first image name
            definition = images[name]

            # Make sure all the dependencies have been built
            if 'from' in definition and definition['from'] in names:
                # Move this one to the back, because we first need to
                # remove another image that this one depends on
                names.append(name)
            else:
                if self.push_one(name, definition, dryrun=dryrun,
                                 verbose=verbose):
                    pushed.append(name)
        return pushed

    def build_one(self, name, definition, dryrun=False, force=False,
                  verbose=1):
        """
            Builds a single docker image.
            The image this docker image depends on should already be built!
        """

        self.logger.debug("build_one: Building %s", name)
        self.logger.debug("build_one: definition: %s", definition)

        tag = self._get_full_tag(name, definition)

        if 'context' in definition:
            directory = definition['context']
        else:
            raise Exception("No context defined in file, aborting")

        if verbose > 1:
            print("Now building " + bcolors.blue(name) +
                  " in directory " + bcolors.blue(directory) +
                  " and tagging as " + bcolors.blue(tag))

        if not dryrun:
            try:
                generator = self.client.api.build(path=directory, tag=tag,
                                                  rm=True, nocache=force)
                ident = self._docker_progress(name, generator, verbose=verbose)
            except (ParseError, BuildError) as error:
                self._stop_build()
                print(bcolors.fail("An error occurred during build: " +
                                   str(error)) + "\n", file=sys.stderr)
                return False
            except (KeyboardInterrupt, SystemExit):
                self._stop_build()
                raise
        else:
            ident = 'testidentifier'
            self.cache[name] = ident

        if verbose > 1:
            print("Successfully built image with tag:" + bcolors.blue(tag) +
                  " docker id is: " + bcolors.blue(ident))

        return True

    def clean_one(self, name, definition, verbose=1, dryrun=False):
        """
            Removes the specified image if it exists
        """
        tag = self._get_full_tag(name, definition)
        exists = self._check_if_exists(tag)
        if exists:
            if verbose > 1:
                print("removing image with tag: " + bcolors.blue(tag))
            if not dryrun:
                self.client.images.remove(tag)
            return True
        return False

    def push_one(self, name, definition, dryrun=False, verbose=1):
        """
            Push the specified image if it exists
        """
        tag = self._get_full_tag(name, definition)
        exists = self._check_if_exists(tag)
        if exists:
            if verbose > 1:
                print("Pushing image with tag: " + bcolors.blue(tag))
            if not dryrun:
                try:
                    generator = self.client.images.push(tag, stream=True)
                    return self._docker_progress(name, generator,
                                                 has_step=False,
                                                 verbose=verbose)
                except (ParseError, BuildError) as error:
                    self._stop_build()
                    print(bcolors.fail("An error occurred during build: " +
                                       str(error)) + "\n", file=sys.stderr)
                    return False
                except (KeyboardInterrupt, SystemExit):
                    self._stop_build()
                    raise
            return True
        return False

    def _check_if_exists(self, tag):
        """
           Check whether this image exists.
        """
        try:
            self.client.images.get(tag)
            return True
        except docker.errors.ImageNotFound:
            return False

    def _get_full_tag(self, name, definition):
        """
            Get the full tag for image
        """
        if 'tag' in definition:
            tag = definition['tag']
        else:
            tag = name

        tag = posixpath.join(self.organisation, tag)

        return tag

    def _update_progress(self):
        """
            Scheduled task to update progress bar every second
        """
        if not self.done:
            if self.progress_bar:
                self.progress_bar.update(self.step)

                self.timer = threading.Timer(1, self._update_progress)
                self.timer.start()

    def _stop_build(self):
        """
            Stop all the build related activities
        """
        if self.progress_bar is not None:
            self.progress_bar.finish()
            self.progress_bar = None

        if self.timer:
            self.timer.cancel()

    def _docker_progress(self, name, generator, has_step=True, verbose=1):
        self.progress_bar = None
        self.done = False
        self.timer = None
        self.step = 0
        self.total = None

        # The build function returns a generator with what would normally
        # be the console output. Here we parse it to find which step we
        # are on (e.g. the layer)
        # and whether it was successfully built, although if it does not
        # build successfully we will get an Exception
        if verbose > 0:
            print(bcolors.blue(name))
        if verbose > 2:
            print(bcolors.warning(name + ": "), end="")

        try:
            for response in generator:
                json_response = json.loads(response.decode("utf-8"))
                self.logger.debug(json_response)
                if 'error' in json_response:
                    raise BuildError(json_response['error'])
                if not ('stream' in json_response or     # Sent when building
                        'status' in json_response or     # Sent when building
                        'aux' in json_response):         # Sent when pushing
                    raise ParseError(
                        "Unsupported docker response: " + str(json_response))

                if 'status' in json_response:
                    line = json_response['status']
                    # if line.endswith("\n"):
                    #     print(bcolors.bold(line), end="")
                    # else:
                    #     print(bcolors.bold(line))
                elif 'stream' in json_response:
                    line = json_response['stream']
                elif 'aux' in json_response:
                    # Docker 1.13 push gives aux when push is done
                    ident = json_response['aux']['Digest'][7:]

                if verbose > 2 and 'status' not in json_response:
                    if line.endswith("\n"):
                        print(bcolors.blue(line), end="")
                        print(bcolors.warning(name + ": "), end="")
                    else:
                        print(bcolors.blue(line), end="")

                if has_step and line.startswith('Step'):
                    self.step, self.total = extract_step(line)
                elif not has_step:
                    self.step += 1

                self.create_progress_bar(name)
                self.progress_bar.update(self.step)

                if line.startswith('Successfully built'):
                    ident = extract_id(line)
                    self.cache[name] = ident
                    self.done = True

            self._stop_build()

            if ident:
                return ident
            else:
                return False
        except docker.errors.APIError as error:
            raise BuildError(str(error))

    def create_progress_bar(self, name):
        """
            Initialize the progress bar
        """
        if self.progress_bar is None:
            if self.total is None:
                self.total = progressbar.UnknownLength
                widgets = [Counter(), ' ', Bar(), ' ', Timer()]
            else:
                widgets = [Percentage(), ' (', SimpleProgress(), ')',
                           ' ', Bar(), ' ', Timer()]

            self.progress_bar = progressbar.ProgressBar(
                max_value=self.total, redirect_stdout=True,
                widgets=widgets).start()

            self.timer = threading.Timer(1, self._update_progress)
            self.timer.start()
