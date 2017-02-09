

class BuildError(Exception):
    """
        Error while building
    """
    pass


class ParseError(Exception):
    """
        Error parsing docker stream
    """
    pass
