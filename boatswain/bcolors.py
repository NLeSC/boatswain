class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def blue(string):
        return bcolors._wrap(bcolors.OKBLUE, string)

    @staticmethod
    def green(string):
        return bcolors._wrap(bcolors.OKGREEN, string)

    @staticmethod
    def warning(string):
        return bcolors._wrap(bcolors.WARNING, string)

    @staticmethod
    def fail(string):
        return bcolors._wrap(bcolors.FAIL, string)

    @staticmethod
    def header(string):
        return bcolors._wrap(bcolors.HEADER, string)

    @staticmethod
    def bold(string):
        return bcolors._wrap(bcolors.BOLD, string)

    @staticmethod
    def underline(string):
        return bcolors._wrap(bcolors.UNDERLINE, string)

    @staticmethod
    def _wrap(color, string):
        the_str = string
        if type(the_str) == 'bytes':
            the_str = string.decode()
        return color + the_str + bcolors.ENDC
