#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name='manpac',
    version="1.0.0",
    packages=find_packages(),
    author="Theomat, Galeniium, Dathy",
    author_email="theomatricon@gmail.com",

    description="Manpac game.",
    long_description=open('README.md').read(),

    install_requires=[
        "pygame",
        "tqdm",
        "numpy"
    ],

    include_package_data=True,
    url='https://github.com/Theomat/manpac',
    license="Creative Commons 3",
)
