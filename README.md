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

Run the unit tests with the command: `python setup.py test`


## Documentation
For usage instructions and documentation see [https://htrc.github.io/HTRC-WorksetToolkit/]
