# HTRC Workset Toolkit
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/htrc.svg)](https://pypi.python.org/pypi/htrc)
[![PyPI Version](https://img.shields.io/pypi/v/htrc.svg)](https://pypi.python.org/pypi/htrc)
[![Build Status](https://travis-ci.org/htrc/HTRC-WorksetToolkit.svg?branch=master)](https://travis-ci.org/htrc/HTRC-WorksetToolkit)
[![Coverage Status](https://coveralls.io/repos/github/htrc/HTRC-WorksetToolkit/badge.svg?branch=master)](https://coveralls.io/github/htrc/HTRC-WorksetToolkit?branch=master)

HTRC Workset Toolkit provides tools for interacting with and analyzing volumes in the HathiTrust Digital Library:

- Volume Download (`htrc download`)
- Metadata Download (`htrc metadata`)
- Pre-built Analysis Workflows (`htrc run`)
- Export of volume lists (`htrc export`)

Each tool operates on a *workset*, which is a collection of volumes, pages, or catalog records. 

The tools also assist with the HTRC Data Capsule, enabling you to download volumes to the secure mode of the capsule for analysis.

For usage instructions and documentation see [https://htrc.github.io/HTRC-WorksetToolkit/cli.html].

For developers, the Workset Toolkit provides ways to test algorithms that will be run in the secure mode of the Data Capsule. It also provides methods for accessing the bibliographic records for HathiTrust volumes and ways to resolve catalog records for multivolume collections. It has the following components:

- An access layer for the Bibliographic API (`htrc.metadata`)
- An access layer for the Data API (`htrc.volumes`)
- Pre-built analysis workflows (`htrc.tools`)
- Provenance tracking for verification of non-consumptive exports (`htrc.prov`)
- Mock testing interface for user-machine or maintenance-mode testing of
  secure-mode commands (`htrc.mock`)
- Utilities for record and volume resolution (`htrc.util`)

For documentation of the development libraries see [https://htrc.github.io/HTRC-WorksetToolkit/sdk.html].

## Data Capsule usage
The HTRC Data Capsule allows for analysis of HathiTrust volumes. It is the only way to perform analysis on the raw OCR text of in-copyright works.

New users can register and configure a data capsule by following the [HTRC Data Capsule Tutorial](https://wiki.htrc.illinois.edu/display/COM/HTRC+Data+Capsule+Tutorial).

The HTRC Workset Toolkit will be pre-installed on Data Capsule images in the near future. Current data capsules will need to follow the [installation instructions](#installation-instructions).


## Installation instructions

1. Download and install [Anaconda Python](https://www.continuum.io/downloads). The HTRC Workset Toolkit is compatible with both Python 2.7 and 3.6, but we recommend using the 3.6 version for future compatibility.

2. After installing Anaconda, open a new terminal and type `pip install htrc` to install the SDK.

## Testing

1. `git clone https://github.com/htrc/HTRC-WorksetToolkit.git`
2. `cd HTRC-WorksetToolkit`
3. `python setup.py develop`
4. The `htrc` command will now refer to the code in this local repository.
5. Run the unit tests with the command: `python setup.py test`
6. To revert to the PyPI version:
   ```
   pip uninstall htrc
   pip install htrc
   ```

## Updating PyPI
In order to update PyPI, you will need owner permissions, which are currently held by Samitha Liyanage and Jaimie Murdock.

1. Create a `.pypirc` containing your username and password:
   ```
   [distutils]
   index-servers =
      pypi

   [pypi]
   repository=https://upload.pypi.org/legacy/
   username:USERNAME
   password:PASSWORD
   ```
2. Run `python setup.py sdist upload` to upload the tarball.
3. Run `python setup.py bdist_egg upload` to upload the egg file.

## Documentation
For usage instructions and documentation please see: [https://htrc.github.io/HTRC-WorksetToolkit/]

For a more detailed guide please see: [https://wiki.htrc.illinois.edu/x/NQBTAw.]
