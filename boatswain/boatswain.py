from __future__ import absolute_import, print_function

import docker
import copy
import logging
import os
import json
import progressbar
from .bcolors import bcolors

from six import iteritems

class Boatswain(object):
    """
        Builds all images defined in the boatswain file

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

    def __init__(self, bsfile):
        self.client = docker.from_env()
        self.bsfile = bsfile
        self.cache = {}
        if 'organisation' in self.bsfile:
            self.organisation = self.bsfile['organisation']
        else:
            raise Exception('No organisation specified in the boatswain file!')
    
    def build(self, force=False, verbose=False):
        """
            Builds all images defined in the boatswain file

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
        print(bcolors.header("Boatswain be buildin' yer dockers!"))
        if 'images' in self.bsfile:
            logging.debug(self.bsfile['images'])
            return self.build_dict(self.bsfile['images'], force=force, verbose=verbose)
        else:
            logging.warn('No images defined in boatswain file')

    def remove_known_keys(self, dictionary):
        known_keys = ['context', 'tag']
        newdict = copy.deepcopy(dictionary)

        for key in known_keys:
            if key in newdict:
                del newdict[key]
        
        return newdict

    def remove_key_from_dict(self, key, dictionary):
        newdict = copy.deepcopy(dictionary)
        del newdict[key]
        return newdict


    def get_step(self, line):
        stepstr = line.split(':')[0]
        stepstr = stepstr.split(' ')[1]
        steps = stepstr.split('/')
        step = int(steps[0])
        total = int(steps[1])

        return (step, total)


    def extract_id(self, line):
        idstr = line.split(' ')[2]
        return idstr


    def build_dict(self, images, force=False, verbose=False):
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
        logging.debug(images)
        if not images:
            return False
        else:
            names = list(images)
            while len(names):
                name = names.pop(0) # get the first image name
                definition = images[name]

                # Make sure all the dependencies have been built
                if 'from' in definition and definition['from'] not in self.cache:
                    if definition['from'] not in names:
                        raise Exception("Could not find a recipe to build", definition['from'], "which is needed for", name)
                    else:
                        # Move this one to the back, because it from on another image
                        names.append(name)
                else:
                    self.build_one(name, definition, force=force, verbose=verbose)


    def build_one(self, name, definition, force=False, verbose=False):
        """
            Builds a single docker image.
            The image this docker image depends on should already be built!
        """

        if 'tag' in definition:
            tag = definition['tag']
        else:
            tag = name

        tag = os.path.join(self.organisation, tag)

        dobuild = False
        if force:
            dobuild = True
        else:
            try:
                image = self.client.images.get(tag)
                id = image.short_id
                if id.startswith('sha256:'):
                    id = id[7:]
                self.cache[name] = id
                print(bcolors.green("Found image for tag ") + bcolors.blue(name) +
                      bcolors.green(" that is already built with id: ") + bcolors.blue(id))
            except docker.errors.ImageNotFound as e:
                dobuild = True
            
        if dobuild:
            if 'context' in definition:
                directory = definition['context']
            else:
                raise Exception("No context defined in file, aborting")

            print(bcolors.green("Now building ") + bcolors.blue(name) + bcolors.green(" in directory ") +
                bcolors.blue(directory) + bcolors.green(" and tagging as ") + bcolors.blue(tag))

            gen = self.client.api.build(path=directory, tag=tag, rm=True, nocache=force)
            bar = None
            # The build function returns a generator with what would normally
            # be the console output. Here we parse it to find which step we 
            # are on (e.g. the layer)
            # and whether it was successfully built, although if it does not
            # build successfully we will get an Exception
            if verbose:
                print(bcolors.warning(name+": "), end="")
            for d in gen:
                line = json.loads(d.decode("utf-8"))['stream']
                if verbose:
                    if line.endswith("\n"):
                        print(bcolors.blue(line), end="")
                        print(bcolors.warning(name+": "), end="")
                    else:
                        print(bcolors.blue(line), end="")
                if line.startswith('Step'):
                    step, total = self.get_step(line)
                    if bar is None:
                        bar = progressbar.ProgressBar(max_value=total, redirect_stdout=True)
                        bar.update(step)
                    else:
                        bar.update(step)
                elif line.startswith('Successfully built'):
                    id = self.extract_id(line)
                    self.cache[name] = id

            if bar is not None:
                bar.finish()
            
            print(bcolors.green(" Successfully built image with tag:") + bcolors.blue(tag) +
                bcolors.green("  docker id is: ") + bcolors.blue(id))

            return True
