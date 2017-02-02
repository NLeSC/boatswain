from __future__ import absolute_import, print_function

import io
import os

from setuptools import find_packages, setup


def read(*names, **kwargs):
    with io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8'),
    ) as fp:
        return fp.read()


readme = open('README.rst').read()
history = open('CHANGES.rst').read().replace('.. :changelog:', '')


setup(
    name='boatswain',
    version='0.1.0-dev',
    url='https://github.com/nlesc-sherlock/boatswain',
    license='Apache Software License',
    author='Berend Weel',
    tests_require=['nose'],
    install_requires=[
        'docker>=2.0.2, <3.0.0'
    ],
    extras_require={
        'registry': ['docker-registry-client>=0.5.1'],
    },
    author_email='b.weel@esiencecenter.nl',
    description=(
        'Yaml based way to build Docker images.'
    ),
    long_description=readme + '\n\n' + history,
    packages=find_packages(),
    include_package_data=True,
    platforms='any',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    entry_points={
        'console_scripts': [
            'boatswain = boatswain.cli:main',
        ],
    },
)
