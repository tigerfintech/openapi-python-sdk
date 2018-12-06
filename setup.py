# -*- coding: utf-8 -*-
"""
Created on 2018/9/16

@author: gaoan
"""
from setuptools import find_packages, setup

install_requires = ['six', 'simplejson', 'python-dateutil', 'pytz', 'pyasn1==0.4.4', 'rsa==4.0', 'stomp.py']

setup(
    name='tigeropen',
    version='1.0.4',
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
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
