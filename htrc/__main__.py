#!/usr/bin/env python
from __future__ import absolute_import, division, print_function
from future import standard_library
standard_library.install_aliases()

from htrc.metadata import *
from htrc.volumes import *
import htrc.workset

from tempfile import NamedTemporaryFile

def main():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parsers = parser.add_subparsers(help="select a command")

    # Metadata Helpers
    parser_getmd = parsers.add_parser('get-md',
                                      help="Get metadata for a folder of HathiTrust volumes")
    parser_getmd.add_argument("folder", nargs="?",
                              help="Path to Config [optional]")
    parser_getmd.set_defaults(func='getmd')

    # Download Helper
    parser_download = parsers.add_parser('download',
                                         help="Download HathiTrust volumes to disk [requires auth]")
    parser_download.add_argument("-u", "--username", help="HTRC username")
    parser_download.add_argument("-p", "--password", help="HTRC password")
    parser_download.add_argument("file", help="input file of ids")
    parser_download.add_argument("-o", "--output", help="output directory", default='ht_data')
    parser_download.set_defaults(func='download')

    args = parser.parse_args()

    if args.func == 'getmd':
        get_metadata(args.folder)
    if args.func == 'download':
        if (args.file.endswith('json')
            or args.file.endswith('jsonld')
            or args.file.startswith('http://')
            or args.file.startswith('https://')):
            volumes = htrc.workset.load(args.file)
            f = NamedTemporaryFile()
            for volume in volumes:
                f.write(volume + '\n')
            args.file = f.name

            try:
                download(args)
            except RuntimeError as e:
                print("Could not download volumes. " + e.message)
            finally:
                print("Closing temporary file: " + f.name)
                f.close()
        else:
            download(args)

if __name__ == '__main__':
    main()
