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

import json
import logging
import os
import posixpath
import shlex
import subprocess
import sys
import traceback

import docker

from .bcolors import bcolors
from .errors import BuildError, ParseError
from .util import extract_id, extract_step, find_dependencies
from .timed_progress_bar import TimedProgressBar


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

    def __init__(self, description, continue_building=False, verbose=1):
        self.logger = logging.getLogger('boatswain')

        # Docker interaction
        self.client = docker.from_env(version="auto")
        self.description = description

        # Cache of images built by boatswain
        self.cache = {}

        # Progress
        self.progress_bar = None
        self.continue_building = continue_building
        self.verbose = verbose

        if 'organisation' in self.description:
            self.organisation = self.description['organisation']
        else:
            raise Exception('No organisation specified in the boatswain file!')

        if 'images' in self.description:
            self.images = self.description['images']
        else:
            # Should not having images be an exception?
            self.images = {}
            self.logger.warning("No images defined in the boatswain description")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.progress_bar is not None:
            self.progress_bar.stop()
            self.progress_bar = None

        return False

    def build(self, dryrun=False, force=False):
        """
            Builds all images defined in the dictionary
        """
        return self._do_action('build', dryrun=dryrun, force=force)

    def clean(self, dryrun=False):
        """
            Removes all images defined in the dictionary
        """
        return self._do_action('clean', dryrun=dryrun)

    def push(self, dryrun=False):
        """
            Push the images defined in the dictionary to the repository
        """
        return self._do_action('push', dryrun=dryrun)

    def _do_action(self, action, **kwargs):
        if not self.images:
            self.logger.warning('No images defined in boatswain file')
            return {'success': True, 'images': [], 'failed': []}
        else:
            return self._do_action_dict(action, self.images, **kwargs)

    def build_dict(self, images, dryrun=False, force=False):
        """
            Build all images in the dictionary
        """
        return self._do_action_dict('build', images, dryrun=dryrun,
                                    force=force)

    def clean_dict(self, images, dryrun=False):
        """
            Remove all images in the dictionary
        """
        return self._do_action_dict('clean', images, dryrun=dryrun)

    def push_dict(self, images, dryrun=False):
        """
            Remove all images in the dictionary
        """
        return self._do_action_dict('push', images, dryrun=dryrun)

    def _do_action_dict(self, action, images, **kwargs):
        """
            Removes all images defined in the dictionary
        """
        if not images:
            return {'success': True, 'images': [], 'failed': []}
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

    def build_up_to(self, name, dryrun=False, force=False):
        """
            Builds the image with the given name and all of
            the images it depends on recursively
        """
        return self.build_up_to_dict(name, self.images, dryrun=dryrun,
                                     force=force)

    def push_up_to(self, name, dryrun=False):
        """
            Pushes the image with the given name and all of
            the images it depends on recursively
        """
        return self.push_up_to_dict(name, self.images, dryrun=dryrun)

    def clean_up_to_dict(self, name, images, dryrun=False):
        """
            Cleans the image with the given name and all of
            the images it depends on recursively
        """
        return self._process_up_to_dict('clean', name, images,
                                        dryrun=dryrun)

    def build_up_to_dict(self, name, images, dryrun=False, force=False):
        """
            Builds the image with the given name and all
            of the images it depends on recursively
        """
        return self._process_up_to_dict('build', name, images, dryrun=dryrun,
                                        force=force)

    def push_up_to_dict(self, name, images, dryrun=False):
        """
            Pushes the image with the given name and all of
            the images it depends on recursively
        """
        return self._process_up_to_dict('push', name, images,
                                        dryrun=dryrun)

    def _process_up_to_dict(self, action, name, images, dryrun=False,
                            force=False):
        """
           Build image name and all its dependencies from a dictionary
        """
        self.logger.debug("build_up_to_dict: %s", images)
        if not images:
            self.logger.warning('No images defined')
            return {'success': True, 'images': [], 'failed': []}
        elif name not in images:
            print(bcolors.fail("Cannot build undefined image " + name))
        else:
            names = find_dependencies(name, images)
            self.logger.debug(names)
            if action == 'build':
                return self.build_list(names, images, dryrun=dryrun,
                                       force=force)
            elif action == 'clean':
                return self.clean_list(names, images, dryrun=dryrun)
            elif action == 'push':
                return self.push_list(names, images, dryrun=dryrun)

    def build_list(self, names, images, dryrun=False, force=False):
        """
            Builds the all images given in names and all the dependencies
            of these images
        """
        built = []
        failed = []
        success = True
        self.logger.debug("build_list: %s", names)

        if self.verbose == 1:
            self.progress_bar = TimedProgressBar(0, len(names), "Total")
            self.progress_bar.start()
        while len(names):
            name = names.pop(0)  # get the first image name
            definition = images[name]

            # Make sure all the dependencies have been built
            if 'from' in definition and definition['from'] not in self.cache:
                if definition['from'] not in names:
                    print(bcolors.fail("Error: could not find a recipe to build"),
                          bcolors.blue(definition['from']),
                          bcolors.fail("which is needed for"),
                          bcolors.blue(name) + "\n", file=sys.stderr)
                    # do not append this image
                else:
                    # Move this one to the back, because it from on another
                    # image
                    names.append(name)
            else:
                if self.build_one(name, definition, dryrun=dryrun, force=force):
                    built.append(name)
                elif not self.continue_building:
                    return {'success': False, 'images': built, 'failed': [name]}
                else:
                    failed.append(name)
                    success = False

                if self.verbose == 1:
                    self.progress_bar.step += 1
                    self.progress_bar.imagename = name
                    self.progress_bar.update()

        if self.verbose == 1:
            self.progress_bar.stop()
            self.progress_bar = None

        return {'success': success, 'images': built, 'failed': failed}

    def clean_list(self, names, images, dryrun=False):
        """
            Removes all images defined in the list
        """
        cleaned = []
        failed = []
        success = True
        if self.verbose == 1:
            self.progress_bar = TimedProgressBar(0, len(names), "Total")
            self.progress_bar.start()
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
                elif not self.continue_building:
                    return {'success': False, 'images': cleaned, 'failed': [name]}
                else:
                    failed.append(name)
                    success = False

                if self.verbose == 1:
                    self.progress_bar.step += 1
                    self.progress_bar.imagename = name
                    self.progress_bar.update()

        if self.verbose == 1:
            self.progress_bar.stop()
            self.progress_bar = None
        return {'success': success, 'images': cleaned, 'failed': failed}

    def push_list(self, names, images, dryrun=False):
        """
            Removes all images defined in the list
        """
        pushed = []
        failed = []
        success = True
        if self.verbose == 1:
            self.progress_bar = TimedProgressBar(0, len(names), "Total")
            self.progress_bar.start()
        while len(names):
            name = names.pop(0)  # get the first image name
            definition = images[name]

            # Make sure all the dependencies have been built
            if 'from' in definition and definition['from'] in names:
                # Move this one to the back, because we first need to
                # remove another image that this one depends on
                names.append(name)
            else:
                if self.push_one(name, definition, dryrun=dryrun):
                    pushed.append(name)
                elif not self.continue_building:
                    return {'success': False, 'images': pushed, 'failed': [name]}
                else:
                    failed.append(name)
                    success = False

                if self.verbose == 1:
                    self.progress_bar.step += 1
                    self.progress_bar.imagename = name
                    self.progress_bar.update()
        if self.verbose == 1:
            self.progress_bar.stop()
            self.progress_bar = None
        return {'success': success, 'images': pushed, 'failed': failed}

    def before_command(self, name, definition, verbose=1, dryrun=False):
        if verbose > 1:
            print(bcolors.blue("Pre-build staging"))
        commands = definition['before']['command']
        for command in commands:
            output = None

            args = shlex.split(command)
            if verbose > 2:
                output = sys.stdout
            if not dryrun:
                if verbose > 1:
                    print("Running: ", args, " from directory ", os.getcwd())
                try:
                    subprocess.check_call(args, stdout=output, stderr=subprocess.PIPE)
                except subprocess.CalledProcessError:
                    failure_string = "\n{} from directory {}\n".format(args, os.getcwd())
                    print(bcolors.fail("An exception occured during before command for ") +
                          bcolors.blue(name) +
                          bcolors.fail(":" + failure_string))
                    print(bcolors.fail(traceback.format_exc()))
                    return False
            else:
                print(os.getcwd(), "> ", args)
        return True

    def build_one(self, name, definition, dryrun=False, force=False):
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

        if self.verbose > 1 or dryrun:
            print("Now building " + bcolors.blue(name) +
                  " in directory " + bcolors.blue(directory) +
                  " and tagging as " + bcolors.blue(tag))

        if 'before' in definition and 'command' in definition['before']:
            if not self.before_command(name, definition, dryrun=dryrun):
                return False

        if not os.path.exists(directory):
            print(bcolors.fail("Context directory: {} does not exist!".format(directory)))
            return False

        if not dryrun:
            try:
                generator = self.client.api.build(path=directory, tag=tag,
                                                  rm=True, nocache=force)
                ident = self._docker_progress(name, generator)
            except (ParseError, BuildError) as error:
                if self.verbose > 1:
                    self.progress_bar.stop()
                    self.progress_bar = None
                print(bcolors.fail("An error occurred while building ") +
                      bcolors.green(bcolors.blue(name)) +
                      bcolors.fail(": " + str(error)) + "\n", file=sys.stderr)
                return False
            except (KeyboardInterrupt, SystemExit):
                self.progress_bar.stop()
                self.progress_bar = None
                raise
        else:
            ident = 'testidentifier'
            self.cache[name] = ident

        if self.verbose > 1 or dryrun:
            print("Successfully built image with tag:" + bcolors.blue(tag) +
                  " docker id is: " + bcolors.blue(ident))

        return True

    def clean_one(self, name, definition, dryrun=False):
        """
            Removes the specified image if it exists
        """
        tag = self._get_full_tag(name, definition)
        exists = self._check_if_exists(tag)
        if exists:
            if self.verbose > 1:
                print("removing image with tag: " + bcolors.blue(tag))
            if not dryrun:
                self.client.images.remove(tag)
            return True
        return False

    def push_one(self, name, definition, dryrun=False):
        """
            Push the specified image if it exists
        """
        tag = self._get_full_tag(name, definition)
        exists = self._check_if_exists(tag)
        if exists:
            if self.verbose > 1:
                print("Pushing image with tag: " + bcolors.blue(tag))
            if not dryrun:
                try:
                    generator = self.client.images.push(tag, stream=True)
                    return self._docker_progress(name, generator,
                                                 has_step=False)
                except (ParseError, BuildError) as error:
                    if self.verbose > 1:
                        self.progress_bar.stop()
                        self.progress_bar = None
                    print(bcolors.fail("An error occurred during build: " +
                                       str(error)) + "\n", file=sys.stderr)
                    return False
                except (KeyboardInterrupt, SystemExit):
                    if self.verbose > 1:
                        self.progress_bar.stop()
                        self.progress_bar = None
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

    def _docker_progress(self, name, generator, has_step=True):
        # The build function returns a generator with what would normally
        # be the console output. Here we parse it to find which step we
        # are on (e.g. the layer)
        # and whether it was successfully built, although if it does not
        # build successfully we will get an Exception
        if self.verbose > 2:
            print(bcolors.warning(name + ": "))

        try:
            if self.verbose > 1:
                step = 0
                total = 0

            for response in generator:
                lines = response.rstrip().decode('utf-8')
                lines = lines.replace('\r', '')

                lines = lines.split('\n')

                for response_line in lines:
                    json_response = json.loads(response_line)
                    self.logger.debug(json_response)
                    if 'error' in json_response:
                        raise BuildError(json_response['error'])
                    if not ('stream' in json_response or     # Sent when building
                            'status' in json_response or     # Sent when building
                            'aux' in json_response):         # Sent when pushing
                        raise ParseError(
                            "Unsupported docker response: " + str(json_response))

                    if 'status' in json_response:
                        line = json_response['status'].rstrip()
                        # if line.endswith("\n"):
                        #     print(bcolors.bold(line), end="")
                        # else:
                        #     print(bcolors.bold(line))
                    elif 'stream' in json_response:
                        line = json_response['stream'].rstrip()
                    elif 'aux' in json_response:
                        # Docker 1.13 push gives aux when push is done
                        aux = json_response['aux']
                        from_index = len('sha256:')
                        if 'Digest' in aux:
                            id_line = aux['Digest'].rstrip()
                            ident = id_line[from_index:]
                        elif 'ID' in aux:
                            # sometimes you get an ID key instead of a Digest key
                            # (we're not sure why at the moment)
                            id_line = aux['ID'].rstrip()
                            ident = id_line[from_index:]
                        else:
                            raise Exception("No 'Digest' or 'ID' key in JSON response. Aborting.")

                    if self.verbose > 2 and 'status' not in json_response:
                        print(bcolors.warning(name + ": "), end="")
                        print(bcolors.blue(line))

                    if self.verbose > 1:
                        if has_step and line.startswith('Step'):
                            step, total = extract_step(line)
                        elif not has_step:
                            step += 1

                        if self.progress_bar is None:
                            self.progress_bar = TimedProgressBar(step, total, name)
                            self.progress_bar.start()
                        else:
                            self.progress_bar.step = step
                            self.progress_bar.update()

                    if line.startswith('Successfully built'):
                        ident = extract_id(line)
                        self.cache[name] = ident

            if self.verbose > 1:
                self.progress_bar.stop()
                self.progress_bar = None

            if ident:
                return ident
            else:
                return False
        except docker.errors.APIError as error:
            if self.verbose > 1:
                self.progress_bar.stop()
                self.progress_bar = None
            raise BuildError(str(error))
