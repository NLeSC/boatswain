from progressbar import DynamicMessage
from .bcolors import bcolors


class DynamicStringMessage(DynamicMessage):
    '''Displays a custom variable.'''

    def __init__(self, name):
        '''Creates a DynamicMessage associated with the given name.'''
        if not isinstance(name, str):
            raise TypeError('DynamicMessage(): argument must be a string')
        if len(name.split()) > 1:
            raise ValueError(
                'DynamicMessage(): argument must be single word')

        self.name = name

    def __call__(self, progress, data):
        val = data['dynamic_messages'][self.name]
        if val:
            return bcolors.blue('{:20.20}'.format(val))
        else:
            return bcolors.blue('{:20.20}'.format(10 * '-'))
