#!/usr/bin/env python
from __future__ import absolute_import, division, print_function
from future import standard_library
standard_library.install_aliases()

import os, os.path
import shutil
from tempfile import NamedTemporaryFile

from htrc.metadata import *
import htrc.volumes
import htrc.workset
import htrc.tools.mallet
import htrc.tools.topicexplorer
from htrc.lib.cli import bool_prompt


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parsers = parser.add_subparsers(help="select a command")

    # Metadata Helpers
    parser_getmd = parsers.add_parser('metadata',
                                      help="Get metadata for a folder of HathiTrust volumes")
    parser_getmd.add_argument("folder", help="Path to HathiTrust Volumes")
    parser_getmd.set_defaults(func='metadata')

    # Download Helper
    parser_download = parsers.add_parser('download',
        help="Download HathiTrust volumes to disk [requires auth]")
    parser_download.add_argument("-u", "--username", help="HTRC username")
    parser_download.add_argument("-p", "--password", help="HTRC password")
    parser_download.add_argument("file", help="input file of ids")
    parser_download.add_argument("-o", "--output", help="output directory",
        default='/media/secure_volume/workset/')
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

    if args.func == 'metadata':
        get_metadata(args.folder)
    if args.func == 'run':
        if args.run == 'mallet':
            htrc.tools.mallet.main(args.path, args.k, args.iter)
        if args.run == 'topicexplorer':
            htrc.tools.topicexplorer.main(args.path, args.k, args.iter)
    if args.func == 'download':
        if os.path.exists(args.output):
            if bool_prompt('Folder {} exists. Delete?'.format(args.output), default=False):
                shutil.rmtree(args.output)
                os.makedirs(args.output)
            else:
                print("Please choose another output folder and try again.")
                sys.exit(1)

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
        else:
            print("Could not download volumes. {} {}".format(e.strerror, e.filename))
    except RuntimeError as e:
        print("Could not download volumes. {}".format(e.message))

if __name__ == '__main__':
    main()
