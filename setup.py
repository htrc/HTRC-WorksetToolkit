#!/usr/bin/env python
from setuptools import setup, find_packages
import os
import platform
__version__ = '0.1.0'

install_requires = [ 'PyLD' ]

setup(
    name='htrc',
    version=__version__,
    description='HathiTrust Research Center API Access',
    author = "HathiTrust Research Center",
    author_email = "htrc@indiana.edu",
    url='http://analytics.hathitrust.org',
    download_url='http://github.com/htrc/HTRC-PythonSDK',
    keywords = [],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Topic :: Text Processing :: Linguistic",
        ],
    packages=find_packages(),
    install_requires=install_requires,
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts' : ['htrc = htrc.__main__:main']
    }
)

