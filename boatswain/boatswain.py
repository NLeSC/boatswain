from __future__ import absolute_import

import docker
import copy
import logging
import os
import json
import progressbar

class Boatswain(object):
    def __init__(self, bsfile):
        self.client = docker.from_env()
        self.bsfile = bsfile
        self.cache = {}
        if 'organisation' in self.bsfile:
            self.organisation = self.bsfile['organisation']
        else:
            raise Exception('No organisation specified in the boatswain file!')
    
    def build(self):
        if 'images' in self.bsfile:
            logging.debug(self.bsfile['images'])
            return self._rec_build(self.bsfile['images'])
        else:
            logging.warn('No images defined in boatswain file')

    def remove_known_keys(self, dictionary):
        known_keys = ['context', 'tag']
        newdict = copy.deepcopy(dictionary)

        for key in known_keys:
            if key in newdict:
                del newdict[key]
        
        return newdict
    
    def get_step(self, line):
        stepstr = line.split(':')[0]
        stepstr = stepstr.split(' ')[1]
        steps = stepstr.split('/')
        step = int(steps[0])
        total = int(steps[1])

        return (step, total)

    def _rec_build(self, images):
        logging.debug(images)
        if not images:
            return True
        else:
            for name, definition in images.items():
                if 'context' in definition:
                    directory = definition['context']
                
                if 'tag' in definition:
                    tag = definition['tag']
                else:
                    tag = name

                tag = os.path.join(self.organisation, tag)
                print("Now building", name, "in directory", directory, "and tagging as", tag)
                gen = self.client.api.build(path=directory, tag=tag)
                bar = None
                for d in gen:
                    line = json.loads(d.decode("utf-8"))['stream']
                    if line.startswith('Step'):
                        step, total = self.get_step(line)
                        if bar is None:
                            bar = progressbar.ProgressBar(max_value=total)
                            bar.update(step)
                        else:
                            bar.update(step)

                if bar is not None:
                    bar.finish()
                self._rec_build(self.remove_known_keys(definition))