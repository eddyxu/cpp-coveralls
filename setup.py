#!/usr/bin/env python
#
# Author: Lei Xu <eddyxu@gmail.com>


from __future__ import print_function
from setuptools import setup, find_packages
import sys
import os

wd = os.path.dirname(os.path.abspath(__file__))
os.chdir(wd)
sys.path.insert(1, wd)

name = 'cpp-coveralls'
pkg = __import__('cpp_coveralls')

author, email = pkg.__author__.rsplit(' ', 1)
email = email.strip('<>')

version = pkg.__version__
classifiers = pkg.__classifiers__

description = 'Upload gcov to coveralls.io'
long_description = description

with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as f:
    reqs = f.read()

setup(
    name=name,
    version=version,
    author=author,
    author_email=email,
    url='https://github.com/eddyxu/cpp-coveralls',
    maintainer=author,
    maintainer_email=email,
    description=description,
    long_description=long_description,
    classifiers=classifiers,
    install_requires=reqs,
    packages=find_packages(),
    license='Apache License 2.0',
    keywords='coveralls.io',
    entry_points={
        'console_scripts': [
            'coveralls = cpp_coveralls:run',
            'cpp-coveralls = cpp_coveralls:run',
        ],
    },
)
