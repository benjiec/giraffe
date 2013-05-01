#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

setup(
    name='giraffe',
    version='2.0',
    description='Sequence BLAST, feature detection, and visualization',
    author='Benjie Chen',
    author_email='benjie@alum.mit.edu',
    long_description=open('README.md', 'r').read(),
    packages=["giraffe", "hippo", "hippo.migrations", "hippo.management", "hippo.management.commands"],
    package_dir={"": "src"},
    package_data = {"giraffe": ["static/giraffe/css/*.css",
                                "static/giraffe/css/jquery-ui/redmond/*.css",
                                "static/giraffe/js/*.js",
                                "static/giraffe/js/jquery/*.js",
                                "static/giraffe/js/jquery/jquery-ui-1.9.2.custom/js/*.js",
                                "static/giraffe/js/jquery/jquery-ui-1.9.2.custom/css/*/*.css",
                                "static/giraffe/js/jquery/jquery-ui-1.9.2.custom/css/*/*/*.png",
                                "templates/giraffe/*"],
                    "hippo": ["fixtures/*"],
                   },
    zip_safe=False,
    requires=[],
    install_requires=[
      'numpy',
      'biopython',
    ],
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)

