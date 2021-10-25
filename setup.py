# -*- coding: utf-8 -*-
"""
Created on 2018/9/16

@author: gaoan
"""
from os import path
from setuptools import find_packages, setup
from tigeropen import __VERSION__


with open(path.join(path.abspath(path.dirname(__file__)), 'requirements.txt')) as f:
    install_requires = f.read()

setup(
    name='tigeropen',
    version=__VERSION__,
    description='TigerBrokers Open API',
    packages=find_packages(exclude=[]),
    author='TigerBrokers',
    author_email='openapi@tigerbrokers.com',
    license='Apache License v2',
    package_data={'': ['*.*']},
    url='https://github.com/tigerbrokers/openapi-python-sdk',
    platforms='any',
    install_requires=install_requires,
    classifiers=[
        'Programming Language :: Python',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
