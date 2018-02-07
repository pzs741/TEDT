#!/bin/python2.7
# -*- coding: utf-8 -*-
"""
Ex_treme 2018 -- https://github.com/pzs741
"""

import sys
import os
import codecs


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


packages = [
    'TEDT',
]


if sys.argv[-1] == 'publish':
    os.system('python3 setup.py sdist upload -r pypi')
    sys.exit()


# This *must* run early. Please see this API limitation on our users:
# https://github.com/codelucas/newspaper/issues/155
if sys.version_info[0] == 2 and sys.argv[-1] not in ['publish', 'upload']:
    sys.exit('WARNING! You are attempting to install newspaper3k\'s '
             'python3 repository on python2. PLEASE RUN '
             '`$ pip3 install TEDT` for python3 or '
             '`$ pip install TEDT` for python2')


with open('requires.txt') as f:
    required = f.read().splitlines()


with codecs.open('README.rst', 'r', 'utf-8') as f:
    readme = f.read()


setup(
    name='TEDT',
    version='0.3',
    description='News Title Extraction Algorithm Based on Density and Text Features',
    long_description=readme,
    author='ZhenSheng Peng',
    author_email='pzsyjsgldd@163.com',
    url='https://github.com/pzs741/TEDT',
    packages=packages,
    include_package_data=True,
    install_requires=required,
    license='MIT',
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Natural Language :: English',
        'Intended Audience :: Developers',
    ],
    package_data={'': ['requires.txt']},
)
