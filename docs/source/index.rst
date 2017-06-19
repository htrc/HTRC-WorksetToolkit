.. HTRC Python SDK documentation master file, created by
   sphinx-quickstart on Sun Jun 18 16:15:31 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to the HTRC Python SDK's documentation!
=================================================
The HTRC Python SDK provides a command line interface for interacting with 
and analyzing volumes in the HathiTrust Digital Library:

- Volume Download (``htrc download``)
- Metadata Download (``htrc metadata``)
- Pre-built Analysis Workflows (``htrc run``)

Each of these commands takes a *workset path* (described below).

In addition, it provides a software development kit (SDK) for working with the
HathiTrust Digital Library materials. It was designed for use in the HTRC Data
Capsule service, which is the target distribution. It has the following aspects:

- An access layer for the Bibliographic API (`htrc.metadata`_)
- An access layer for the Data API (`htrc.volumes`_)
- Pre-built analysis workflows (`htrc.tools`_)
- Provenance tracking for verification of non-consumptive exports (`htrc.prov`_)
- Mock testing interface for user-machine or maintenance-mode testing (`htrc.mock`_)
- Utilities for record and volume resolution (`htrc.util`_)

All source code for the HTRC Python SDK is available on `GitHub`_ under an
`Apache 2.0 License`_.

.. _GitHub: https://github.com/htrc/HTRC-PythonSDK/
.. _Apache 2.0 License: https://github.com/htrc/HTRC-PythonSDK/blob/master/LICENSE.md

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   index
   sdk
   tips

Workset paths
---------------
Each of these commands takes a *HathiTrust ID (HTID)* or *workset path*. Valid
identifier types and examples of each are:

==================================  ==============================================================================
Identifier Type                     Example
==================================  ==============================================================================
HathiTrust ID                       mdp.39015078560078
HathiTrust Catalog ID               001423370
HathiTrust URL                      https://babel.hathitrust.org/cgi/pt?id=mdp.39015078560078;view=1up;seq=13
Handle.org Volume URL               https://hdl.handle.net/2027/mdp.39015078560078
HathiTrust Catalog URL              https://catalog.hathitrust.org/Record/001423370
HathiTrust Collection Builder URL   https://babel.hathitrust.org/shcgi/mb?a=listis;c=696632727
Local volumes file                  ``/home/dcuser/Downloads/collections.txt``
==================================  ==============================================================================



Examples
''''''''''''
For example, to download the metadata associated with volume 1 of `The Works of
Jonathan Swift`_, the command would be: 

    ``htrc metadata mdp.39015078560078``

Note that this would only retrieve the first volume. If you want to download
metadata for all 8 volumes, the catalog identifier would be used:
    
    ``htrc metadata 001423370``

Each command can be used with the URL as well (*note the quote marks around each
URL*):

    ``htrc metadata "https://babel.hathitrust.org/cgi/pt?id=mdp.39015078560078;view=1up;seq=13"``

    ``htrc metadata "https://catalog.hathitrust.org/Record/001423370"``

This URL support makes it easy to browse `hathitrust.org`_ and copy links
for computational analysis using the SDK.

.. _The Works of Jonathan Swift: https://hdl.handle.net/2027/mdp.39015078560078
.. _hathitrust.org: https://www.hathitrust.org/


HTRC Data Capsule Service
------------------------------
The *HTRC Data Capsule Service* provisions virtual machines (VMs) to researchers
within the HTRC secure environment. The VM and software environment (including
the SDK) together form a Capsule. Each researcher has exclusive use of the
Capsule for a period of weeks or months during which they can configure their
own environment for performing research on HathiTrust Digital Library texts,
including both in-copyright and public domain volumes.

Each Capsule has both a maintenance mode and a secure mode. In secure
mode, network access is restricted to the HTRC Data API and some HTDL
resources, allowing text and image data to be downloaded to the Capsule.
Any changes made on the non-secure volumes are reverted when leaving secure
mode, so persistent code changes must occur in maintenance mode. The SDK
addresses these connectivity issues with the `htrc.mock`_ library.


Volume Download
--------------------
The Python SDK provides the ``htrc download`` function to download volumes
to the secure mode of the Capsule.

The function takes either a volume ID or one of several types of Workset files:

- volume HTID or HTIDs
- plain-text list of volume IDs (one per line)
- HTRC Portal Workset Builder
- HTRC JSON-LD Workset format
- HT Collection Builder


Bibliographic API Access
--------------------------


Analysis Workflows
--------------------
The Python SDK also provides the command line tool ``htrc run``. Like `volume
download`_, the

Topic Modeling
''''''''''''''''
There are two implementations of LDA topic modeling supported by the 



Mock Testing
--------------
`Mock testing`_ uses simulated objects or functions to mimic the behavior 
of real code in controlled ways. 

The HTRC Python SDK implements a mock of the Data API access layer in
`htrc.mock.volumes`_. The Data API server is only accessible via a Capsule 
in secure mode. By implementing a function with the same call signature 
that returns the same data types, workflows that rely on the Data API can be
tested either in Capsule maintenance mode or on a user's own computer.

An easy way to use this pattern is shown below.

Example
'''''''''

::

    if __debug__:
        # This code will execute when running `python script.py`
        import htrc.mock.volumes as volumes
    else:
        # This code will execute when running `python -O script.py`
        # The -O argument turns on optimizations, setting __debug__ = False.
        import htrc.volumes as volumes
    
    # The following is just to make a running script
    volume_ids = ['htrc.testid']    # any list will do
    output_dir = 'htrc_data'        # any path will do
    
    # download volumes
    volumes.download(volume_ids, output_dir)

This script leverages use of the ``python -O`` switch, which controls the
``__debug__`` global variable:

 -  When run in the development environment, which does not have secure 
    access to the Data API, the program is run with ``python script.py``, 
    setting ``__debug__ = True``. This means that ``volumes.download(volume_ids,
    output_dir)`` utilizes the function ``htrc.mock.volumes.download(volume_ids,
    output_dir)``.  
 -  When run in secure mode of the data capsule, the program is executed with 
    ``python -O script.py``, setting ``__debug__ = False``. The statement 
    ``volumes.download(volume_ids, output_dir)`` utilizes the function 
    ``htrc.mock.volumes.download(volume_ids, output_dir)``.


.. _Mock testing: https://en.wikipedia.org/wiki/Mock_object







Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
