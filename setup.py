#!/usr/bin/env python
from __future__ import print_function

from setuptools import setup, find_packages
from setuptools.command.install import install
import os
import platform
import sys
import atexit
import tarfile
import wget

__version__ = '0.1.45b6'

install_requires = ['PyLD', 'future', 'prov', 'unicodecsv', 'progressbar2',
                    'requests', 'wget', 'argparse==1.1', 'topicexplorer>=1.0b194']
# TODO: migrate to docs confix:, 'sphinx-argparse', 'sphinxcontrib-fulltoc']
if sys.version_info.major == 2:
    install_requires.append('configparser')
    install_requires.append('mock')


def _download_config():
    print("Downloading .htrc file...")

    _config_file_url = 'https://analytics.hathitrust.org/files/.htrc'
    _path = os.path.expanduser('~/.htrc')
    if sys.version_info[0] < 3:
        import urllib2

        headers = {'User-agent': 'Mozilla/5.0'}
        req = urllib2.Request(_config_file_url, None, headers)
        filedata = urllib2.urlopen(req)
        datatowrite = filedata.read()

        with open(_path, 'w') as f:
            f.write(datatowrite)
    else:
        import urllib.request
        urllib.request.urlretrieve(_config_file_url, _path)

    print("\n")


def _install_mallet():
    if not os.path.exists("/home/dcuser/mallet"):
        print('Installing Mallet ...')
        os.makedirs('/home/dcuser/mallet')
        mallet_zip = wget.download('http://mallet.cs.umass.edu/dist/mallet-2.0.8RC3.tar.gz')
        mallet_dir = tarfile.open(mallet_zip, "r:gz")
        mallet_dir.extractall(path="/home/dcuser/mallet")
        mallet_dir.close()
        print('\n')


class PostInstallCommand(install, object):
    def __init__(self, *args, **kwargs):
        super(PostInstallCommand, self).__init__(*args, **kwargs)
        atexit.register(_download_config)
        atexit.register(_install_mallet)


setup(
    name='htrc',
    version=__version__,
    description='HathiTrust Research Center API Access',
    author="HathiTrust Research Center",
    author_email="htrc@indiana.edu",
    url='http://analytics.hathitrust.org',
    download_url='http://github.com/htrc/HTRC-PythonSDK',
    keywords=[],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
    ],
    packages=find_packages(),
    install_requires=install_requires,
    include_package_data=True,
    data_files=[('htrc/mock/volumes/', ['htrc/mock/volumes/example.zip']),
                ('htrc/', ['htrc/.htrc.default'])],
    zip_safe=False,
    entry_points={
        'console_scripts': ['htrc = htrc.__main__:main']
    },
    test_suite="unittest2.collector",
    tests_require=['unittest2'],
    cmdclass={'install': PostInstallCommand}
)
