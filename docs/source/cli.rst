HTRC Workset Toolkit
======================
The HTRC Workset Toolkit povides a command line interface for interacting with 
and analyzing volumes in the HathiTrust Digital Library:

- Volume Download (``htrc download``)
- Metadata Download (``htrc metadata``)
- Pre-built Analysis Workflows (``htrc run``)
- Export of volume lists (``htrc export``)

Workset Path
--------------

Each of these commands takes a *workset path*. Valid types of workset paths 
and examples of each are:

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



Volume Download
--------------------
The ``htrc download`` command retrieves volumes from the `HTRC Data API`_
to the secure mode of the :ref:`HTRC Data Capsule Service`.

.. note::

   This command will return an error when run on a non-HTRC computer or on a
   Capsule running in maintenance mode.

.. _HTRC Data API: https://wiki.htrc.illinois.edu/display/COM/HTRC+Data+API+Users+Guide


Examples
''''''''''


Arguments
'''''''''''
.. argparse::
   :module: htrc.__main__
   :func: download_parser
   :prog: htrc download 


Bibliographic API Access
--------------------------
``htrc metadata`` retrieves metadata from the `HathiTrust Bibliographic API`_.
This command has no limitations on which computer or network executes it.

.. _HathiTrust Bibliographic API: https://www.hathitrust.org/bib_api



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



Arguments
'''''''''''
.. argparse::
   :module: htrc.__main__
   :func: add_workset_path
   :prog: htrc metadata


Analysis Workflows
--------------------
The HTRC Workset Toolkit also provides the command line tool ``htrc run``. Like `volume
download`_, the

Topic Modeling
''''''''''''''''
There are two implementations of LDA topic modeling supported by the 


Arguments
'''''''''''
.. argparse::
   :module: htrc.tools.mallet
   :func: populate_parser
   :prog: htrc run mallet

.. argparse::
   :module: htrc.tools.topicexplorer
   :func: populate_parser
   :prog: htrc run topicexplorer

