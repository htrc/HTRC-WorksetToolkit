# HTRC-PythonSDK

HTRC-PythonSDK is a translation layer between Python code and the HTRC Data API and the HTRC Solr API, providing easy access to metadata and volumes. It is interoperable with both Python 2.7+ and 3.2+.

## Installation instructions
The only supported HTRC Python SDK testing environment is on the Data Capsule. 

1. Register and configure a data capsule by following the [HTRC Data Capsule Tutorial](https://wiki.htrc.illinois.edu/display/COM/HTRC+Data+Capsule+Tutorial)
2. Open a terminal and type `pip install --pre htrc` to install the SDK.

## Usage instructions
Download volumes by creating a file with 1 HathiTrust ID per line. For example:
```
uc2.ark+=13960=t5fb53094
uc2.ark+=13960=t4bn9xv1t
mdp.39015018624224
njp.32101073333633
uc2.ark+=13960=t6k075534
```

Save the file as `htids.txt`.

The volumes can then be downloaded with `htrc download htids.txt`.

## Organization

### htrc.metadata
Contains functions for retrieving volume metadata

### htrc.util.resolve
Contains functions for resolving volume and records.

### htrc.volumes
Contains functions for retrieving volume data

### htrc.workset
Contains functions for the workset mapping.

## Roadmap
1. Test framework with mock Solr and Data API server for remote scripting

