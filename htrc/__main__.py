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
from htrc.util.resolve import *


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
    parser.add_argument("-m", "--mets", action='store_true',
                        help="add volume's METS file")
    parser.add_argument("-pg", "--pages",action='store_true',
        help="Download given page numbers of a volumes.")
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

        if args.pages:
            if args.mets and args.concat:
                print ("Cannot set both concat and mets with pages")
                sys.exit(1)

        try:
            resolve_and_download(args)
        except ValueError:
            print("Invalid identifier:", args.file)
            sys.exit(1)

def resolve_and_download(args):
    if args.file == sys.stdin:
        # For use with UNIX pipes
        download_with_tempfile(args, sys.stdin)
        return

    elif os.path.exists(args.file):
        # For use with downloaded workset files - either in JSON or 
        download(args)
        return

    elif (args.file.endswith('json')
        or args.file.endswith('jsonld')
        or args.file.startswith('http://')
        or args.file.startswith('https://')):
        # For use with HTRC Worksets and HT Collection Builder
        try:
            volumes = htrc.workset.load(args.file)
            download_with_tempfile(args, volumes)
            return
        except ValueError:
            # Invalid workset, continue to last block
            pass

    # Check for valid volume_id
    try:
        if parse_volume_id(args.file):
            volumes = [parse_volume_id(args.file)]
            download_with_tempfile(args, volumes)
            return
        else:
            raise ValueError("No Volume ID found")
    except ValueError:
        pass
    
    # Check for valid record id
    if parse_record_id(args.file):
        record_id = parse_record_id(args.file)
        volumes = record_id_to_volume_ids(record_id)
        download_with_tempfile(args, volumes)
        return
    else:
        # invalid
        raise ValueError("Not a valid ID file or workset identifier: {}".format(
                         args.file))


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

def download_with_tempfile(args, volumes):
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


if __name__ == '__main__':
    main()
