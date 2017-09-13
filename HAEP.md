# HEAP-1: HTRC User Toolkit

HTRC Analytics Enhancement Proposal 1: HTRC Workset Toolkit

## Introduction
The HTRC Workset Toolkit provides a command line interface for interacting with
and analyzing volumes in the HathiTrust Digital Library. It operates on the
concept of a "workset". A workset is a research collection intended for
consumption by an automated process for non-consumptive analysis.

The tools also assist with the HTRC Data Capsule, enabling you to download volumes 
to the secure mode of the capsule for analysis.

## Motivation
Currently, we do not have an end-user tool built around the workset paradigm.
This tool allows for a workset to be downloaded and analyzed using the Data
Capsule, and enables testing outside of the data Capsule.

## Related Work

## Proposed Change
The proposed changes are stored in the GitHub repository
[htrc/HTRC-WorksetToolkit](http://github.com/htrc/HTRC-PythonToolkit), with
[documentation at GitHub.io](http://htrc.github.io/HTRC-WorksetToolkit)

## User Interface
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


## Migration and Maintenance Plan
The project has complete Travis-CI unit test integratioin at [http://travis-ci.org/htrc/HTRC-PythonSDK].

