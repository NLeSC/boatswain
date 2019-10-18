from progressbar import Variable
from .bcolors import bcolors


class DynamicStringMessage(Variable):
    '''Displays a custom variable.'''

    def __init__(self, name, **kwargs):
        '''Creates a DynamicStringMessage associated with the given name.'''
        if not isinstance(name, str):
            raise TypeError('DynamicStringMessage(): argument must be a string')
        if len(name.split()) > 1:
            raise ValueError('DynamicStringMessage(): argument must be single word')

        super().__init__(name, min_width=3, **kwargs)

    def __call__(self, progress, data):
        val = data['dynamic_messages'][self.name]
        if val:
            return bcolors.blue('{:20.20}'.format(val))
        else:
            return bcolors.blue('{:20.20}'.format(10 * '-'))
