#!/usr/bin/env python
from __future__ import absolute_import
from ConfigParser import RawConfigParser as ConfigParser
import httplib
import ssl
import json
import os.path
from StringIO import StringIO  # used to stream http response into zipfile.
import sys
from time import sleep
from urllib2 import urlopen, HTTPError
from urllib import quote_plus, urlencode
import xml.etree.ElementTree as ET
from zipfile import ZipFile  # used to decompress requested zip archives.
import requests
import re

from htrc.metadata import *
from htrc.volumes import *

from topicexplorer.lib.util import *

def main():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parsers = parser.add_subparsers(help="select a command")

    # Metadata Helpers
    parser_getmd = parsers.add_parser('get-md',
                                      help="Get metadata for a folder of HathiTrust volumes")
    parser_getmd.add_argument("folder", nargs="?",
                              type=lambda x: is_valid_filepath(parser_getmd, x),
                              help="Path to Config [optional]")
    parser_getmd.set_defaults(func='getmd')

    # Download Helper
    parser_download = parsers.add_parser('download',
                                         help="Download HathiTrust volumes to disk [requires auth]")
    parser_download.add_argument("-u", "--username", help="HTRC username")
    parser_download.add_argument("-p", "--password", help="HTRC password")
    parser_download.add_argument("file", help="input file of ids",
                                 type=lambda x: is_valid_filepath(parser_download, x))
    parser_download.add_argument("-o", "--output", help="output directory", default='ht_data')
    parser_download.set_defaults(func='download')

    args = parser.parse_args()

    if args.func == 'getmd':
        get_metadata(args.folder)
    if args.func == 'download':
        download(args)

if __name__ == '__main__':
    main()
