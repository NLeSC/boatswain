"""
    Utility functions for working with docker-py
    and dictionaries
"""

def extract_step(line):
    """
        Extracts the step from a docker-py result line

        These lines look like:
        Step 3/9: Sometext
    """
    # Get the first part: Step 3/9
    stepstr = line.split(':')[0]
    # Get the step numbers: 3/9
    stepstr = stepstr.split(' ')[1]
    # Split them
    steps = stepstr.split('/')
    # Convert them to numbers
    step = int(steps[0])
    total = int(steps[1])

    return (step, total)


def extract_id(line):
    """
        Extract the docker id from a success line

        These lines look like:
        'Successfully built ad8402983js938'
    """
    idstr = line.split(' ')[2]
    return idstr


def find_dependencies(name, images):
    """
    Finds the dependencies of name in the
    images dictionary and returns an array
    of all keys in images that should be built

    :param name: The name of the image to build
    :type name: string

    :param images: The dictionary of images
    :type images: dict(string: image_definition)
    """
    # Should this check whether keys exists
    # or just throw KeyError exceptions?
    names = []

    curname = name
    while 'from' in images[curname]:
        names.append(curname)
        curname = images[curname]['from']

    names.append(curname)

    return names
