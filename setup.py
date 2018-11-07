# -*- coding: utf-8 -*-
"""
Created on 2018/9/16

@author: gaoan
"""

import platform

try:
    from pip._internal.req import parse_requirements
except ImportError:
    from pip.req import parse_requirements

from setuptools import find_packages, setup

requirements = parse_requirements("requirements.txt", session=False)

python_version = platform.python_version()

req_strs = [str(ir.req) for ir in requirements]

setup(
    name='tigeropen',
    version='1.0.0',
    description='TigerBrokers Open API',
    packages=find_packages(exclude=[]),
    author='tigerbrokers',
    author_email='openapi@tigerbrokers.com',
    license='Apache License v2',
    package_data={'': ['*.*']},
    url='https://github.com/tigerbrokers/openapi-python-sdk',
    platforms='any',
    install_requires=req_strs,
    classifiers=[
        'Programming Language :: Python',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
