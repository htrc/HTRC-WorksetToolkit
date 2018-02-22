HTRC Workset Toolkit Development Library
==========================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

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
addresses these connectivity issues with the ``htrc.mock`` library.



Mock Testing
''''''''''''''
`Mock testing`_ uses simulated objects or functions to mimic the behavior 
of real code in controlled ways. 

The HTRC Workset Toolkit implements a mock of the Data API access layer in
``htrc.mock.volumes``. The Data API server is only accessible via a Capsule 
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


Modules
---------

`htrc.metadata`
-----------------
.. automodule:: htrc.metadata
   :members:

`htrc.mock`
-----------------
.. automodule:: htrc.mock
   :members:

`htrc.mock.volumes`
'''''''''''''''''''''
.. automodule:: htrc.mock.volumes
   :members:

`htrc.volumes`
----------------
.. automodule:: htrc.volumes
   :members:

`htrc.util`
----------------
.. automodule:: htrc.util
   :members:
