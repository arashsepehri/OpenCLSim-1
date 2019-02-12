#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Setup file for hydraulic_infrastructure_realisation.
    Use setup.cfg to configure your project.

    This file was generated with PyScaffold 3.1.
    PyScaffold helps you to put up the scaffold of your new Python project.
    Learn more under: https://pyscaffold.org/
"""
import sys

from pkg_resources import require, VersionConflict
from setuptools import setup

try:
    require('setuptools>=38.3')
except VersionConflict:
    print("Error: version of setuptools is too old (<38.3)!")
    sys.exit(1)

requires = [
    "pandas",
    "numpy",
]

tests_require = [
    "pytest",
    "pytest-cov",
]


setup(
    name="digital_twin",
    version="0.2.0",
    description="The Digital Twin package aims to facilitate basic nautical traffic simulations.",
    long_description="",  # README + '\n\n' + CHANGES,
        classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    author="Mark van Koningsveld",
    author_email="m.vankoningsveld@tudelft.nl",
    url="https://github.com/TUDelft-CITG/digital_twin",
    keywords="digital_twin",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    tests_require=tests_require,
    install_requires=requires,
    entry_points={
        'console_scripts': [
            'digital_twin=digital_twin.cli:main',
        ],
    },
)