#!/usr/bin/env python

from setuptools import setup

setup(
    name='giraffe',
    version='3.0',
    description='Blast and feature detection',
    author='Benjie Chen',
    author_email='benjie@alum.mit.edu',
    long_description=open('README.md', 'r').read(),
    packages=["giraffe", "hippo", "hippo.migrations", "hippo.management", "hippo.management.commands"],
    package_dir={"": "src"},
    package_data = { "hippo": ["fixtures/*"] },
    zip_safe=False,
    requires=[],
    install_requires=[ 'biopython' ],
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)
