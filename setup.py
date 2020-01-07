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
    version='1.0.4',
    url='https://github.com/nlesc-sherlock/boatswain',
    license='Apache Software License',
    author='Berend Weel',
    install_requires=[
        'setuptools >= 30', 'docker>=3.0.0, <5.0.0', 'PyYAML>=4.2b1', 'progressbar2>=3.16.0, <4.0.0',
        'six>=1.10.0, <2.0.0'
    ],
    extras_require={
        'registry': ['docker-registry-client>=0.5.1'],
        'test': ['pytest', 'pytest-flake8', 'pytest-cov'],
        'windows': ['pywin32==224']
    },
    author_email='b.weel@esiencecenter.nl',
    description=('Yaml based way to build Docker images.'),
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/x-rst',
    packages=find_packages(),
    include_package_data=True,
    platforms='any',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Development Status :: 5 - Production/Stable',
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
