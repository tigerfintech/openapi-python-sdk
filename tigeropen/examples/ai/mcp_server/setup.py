#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
from tigermcp.version import __VERSION__

setup(
    name="tigermcp",
    version=__VERSION__,
    author='TigerBrokers',
    author_email='openapi@itiger.com',
    description="Tiger Broker API MCP Server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tigerfintech/openapi-python-sdk",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    license='Apache License v2',
    python_requires=">=3.9",
    install_requires=[
        "tigeropen>=3.4.6",
        "mcp[cli]>=1.13.0",
    ],
    entry_points={
        "console_scripts": [
            "tigermcp=tigermcp.server:main",
        ],
    },
)
