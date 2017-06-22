HTRC Python SDK Tips
======================

This document contains a number of tips for using the CLI and SDK in conjunction
with other tools.

Pretty-print of JSON data using ``jq``
--------------------------------------
The command line tool ``jq`` is very powerful when combined with the ``htrc
metadata`` command, as it can be used to quickly query documents::

    htrc metadata mdp.39015078560078 | jq

