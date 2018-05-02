#!/usr/bin/env python
"""
Master script for HTRC Workset Toolkit.
"""
from __future__ import absolute_import, division, print_function
from future import standard_library
standard_library.install_aliases()

import json
import os, os.path
import shutil
import sys
from tempfile import NamedTemporaryFile

from htrc.metadata import get_metadata, get_volume_metadata
import htrc.volumes
import htrc.workset
import htrc.tools.mallet
from argparse import ArgumentParser
import htrc.tools.topicexplorer
from htrc.lib.cli import bool_prompt


def download_parser(parser=None):
    if parser is None:
        parser = ArgumentParser()
    parser.add_argument("-u", "--username", help="HTRC username")
    parser.add_argument("-p", "--password", help="HTRC password")
    parser.add_argument("file", nargs='?', default=sys.stdin,
        help="workset path[s]")
    parser.add_argument("-f", "--force", action='store_true', 
        help="remove folder if exists")
    parser.add_argument("-o", "--output", help="output directory",
        default='/media/secure_volume/workset/')
    parser.add_argument("-c", "--concat", action='store_true',
        help="concatenate a volume's pages in to a single file")
    parser.add_argument("-t", "--token", help="JWT for volumes download.")
    parser.add_argument("-dh", "--datahost", help="Data API host.")
    parser.add_argument("-dp", "--dataport", help="Data API port.")
    parser.add_argument("-de", "--dataepr", help="Data API EPR.")
    parser.add_argument("-dc", "--datacert", help="Client certificate file for mutual TLS with Data API.")
    parser.add_argument("-dk", "--datakey", help="Client key file for mutual TLS with Data API.")
    return parser

def add_workset_path(parser=None):
    if parser is None:
        parser = ArgumentParser()
    parser.add_argument("path", nargs='+', help="workset path[s]")
    return parser

    

def main():
    parser = ArgumentParser()
    parser.add_argument('-d', '--debug', help="print long debug messages",
                        action='store_true')
    parsers = parser.add_subparsers(help="select a command")

    # Metadata Helpers
    parser_getmd = parsers.add_parser('metadata',
                                      help="Get metadata for a folder of HathiTrust volumes")
    add_workset_path(parser_getmd)
    parser_getmd.set_defaults(func='metadata')

    # Export Helpers
    parser_export = parsers.add_parser('export',
                                      help="Export the list of HathiTrust volumes")
    add_workset_path(parser_export)
    parser_export.set_defaults(func='export')

    # Download Helper
    parser_download = parsers.add_parser('download',
        help="Download HathiTrust volumes to disk [requires auth]")
    download_parser(parser_download)
    parser_download.set_defaults(func='download')

    # Run helper
    parser_run = parsers.add_parser('run', help="Run a built-in algorithm.")
    run_parsers = parser_run.add_subparsers(help="select a command")

    parser_mallet = run_parsers.add_parser('mallet')
    htrc.tools.mallet.populate_parser(parser_mallet)
    parser_mallet.set_defaults(run='mallet')
    
    parser_topicexplorer = run_parsers.add_parser('topicexplorer')
    htrc.tools.topicexplorer.populate_parser(parser_topicexplorer)
    parser_topicexplorer.set_defaults(run='topicexplorer')
    
    parser_run.set_defaults(func='run')

    args = parser.parse_args()

    if args.func in ['metadata', 'export']:
        volumes = []
        if not args.path:
            for line in sys.stdin:
                volumes.append(line)
        else:
            for path in args.path:
                try:
                    volumes.extend(htrc.workset.path_to_volumes(path))
                except ValueError:
                    volumes.append(path)
        if args.func == 'export':
            for volume in volumes:
                print(volume)
        if args.func == 'metadata':
            metadata = get_metadata(volumes)
            print(json.dumps(metadata))
    elif args.func == 'run':
        if args.run == 'mallet':
            htrc.tools.mallet.main(args.path, args.k, args.iter)
        if args.run == 'topicexplorer':
            htrc.tools.topicexplorer.main(args.path, args.k, args.iter)
    elif args.func == 'download':
        if os.path.exists(args.output):
            if args.force or bool_prompt('Folder {} exists. Delete?'.format(args.output), default=False):
                shutil.rmtree(args.output)
                os.makedirs(args.output)
            else:
                print("Please choose another output folder and try again.")
                sys.exit(1)


        if args.file == sys.stdin:
            f = NamedTemporaryFile()
            for volume in sys.stdin:
                f.write((volume + '\n').encode('utf-8'))
            f.flush()
            args.file = f.name

            try:
                download(args)
            finally:
                print("Closing temporary file: " + f.name)
                f.close()
        

        elif (args.file.endswith('json')
            or args.file.endswith('jsonld')
            or args.file.startswith('http://')
            or args.file.startswith('https://')):
            volumes = htrc.workset.load(args.file)

            f = NamedTemporaryFile()
            for volume in volumes:
                f.write((volume + '\n').encode('utf-8'))
            f.flush()
            args.file = f.name

            try:
                download(args)
            finally:
                print("Closing temporary file: " + f.name)
                f.close()

        elif os.path.exists(args.file):
            download(args)
        else:
            print("Not a valid ID file or workset identifier: {}".format(
                args.file))
            sys.exit(1)


def download(args):
    try:
        htrc.volumes.download(args)
    except OSError as e:
        if not os.path.exists('/media/secure_volume/'):
            print('Secure volume not mounted. Could not download volumes')
            sys.exit(1)
        else:
            print("Could not download volumes. {} {}".format(e.strerror, e.filename))
            sys.exit(1)
    except RuntimeError as e:
        if not args.debug:
            print("Could not download volumes. {}".format(str(e)))
            sys.exit(1)
        else:
            raise e

if __name__ == '__main__':
    main()
