#!/usr/bin/env python

from setuptools import setup

setup(
    name='cpblob',
    version='0.1.0',
    description='Copy blobs to and from Azure',
    maintainer='Eivind Fonn',
    maintainer_email='eivind.fonn@sintef.no',
    packages=['cpblob'],
    install_requires=[
        'azure-storage-blob',
        'click',
        'tqdm',
    ],
    entry_points={
        'console_scripts': [
            'cpblob=cpblob.__main__:main'
        ],
    },
)
