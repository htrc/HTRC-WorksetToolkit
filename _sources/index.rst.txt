.. HTRC Workset Toolkit documentation master file, created by
   sphinx-quickstart on Sun Jun 18 16:15:31 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to the HTRC Workset Toolkit's documentation!
=======================================================
The HTRC Workset Toolkit provides a command line interface for interacting with 
and analyzing volumes in the HathiTrust Digital Library:

- Volume Download (``htrc download``)
- Metadata Download (``htrc metadata``)
- Pre-built Analysis Workflows (``htrc run``)
- Export of volume lists (``htrc export``)

Each tool operates on a *workset*, which is a collection of volumes, pages,
or catalog records. 

A workset is referenced by a :ref:`workset path`, which is one of 7 types of
identifiers. Almost any web page on http://hathitrust.org is a valid identifier,
including the PageTurner view, Catalog record view, and Collection Builder
collections.

The tools also assist with the HTRC Data Capsule, enabling you to download volumes 
to the secure mode of the capsule for analysis.

More details on each command can be found on the :ref:`HTRC Workset Toolkit` page.

For developers, the Workset Toolkit provides ways to test algorithms that will
be run in the secure mode of the Data Capsule. It also provides methods for
accessing the bibliographic records for HathiTrust volumes and ways to resolve
catalog records for multivolume collections. It has the following components:

- An access layer for the Bibliographic API (``htrc.metadata``)
- An access layer for the Data API (``htrc.volumes``)
- Pre-built analysis workflows (``htrc.tools``)
- Provenance tracking for verification of non-consumptive exports (``htrc.prov``)
- Mock testing interface for user-machine or maintenance-mode testing of
  secure-mode commands (``htrc.mock``)
- Utilities for record and volume resolution (``htrc.util``)

More details on each module can be found on the :ref:`HTRC Workset Toolkit
Development Library` page.

All source code for the HTRC Workset Toolkit is available on `GitHub`_ under an
`Apache 2.0 License`_.

.. _GitHub: https://github.com/htrc/HTRC-PythonSDK/
.. _Apache 2.0 License: https://github.com/htrc/HTRC-PythonSDK/blob/master/LICENSE.md


Data Capsule usage
----------------------------
The HTRC Data Capsule allows for analysis of HathiTrust volumes. It is the only
way to perform analysis on the raw OCR text of in-copyright works.

New users can register and configure a data capsule by following the `HTRC Data
Capsule Tutorial`_.

The HTRC Workset Toolkit will be pre-installed on Data Capsule images in the
near future. Current data capsules will need to follow the ref:`installation
instructions`.

.. _HTRC Data Capsule Tutorial: https://wiki.htrc.illinois.edu/display/COM/HTRC+Data+Capsule+Tutorial


Installation instructions
---------------------------

1. Download and install `Anaconda Python`_. The HTRC Workset Toolkit is
   compatible with both Python 2.7 and 3.6, but we recommend using the 3.6 version
   for future compatibility.

2. After installing Anaconda, open a new terminal and type ``pip install htrc``
   to install the SDK.

.. _Anaconda Python: https://www.continuum.io/downloads


Table of Contents
================================
.. toctree::
   :maxdepth: 2

   cli
   sdk
   tips


Indices and tables
====================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
