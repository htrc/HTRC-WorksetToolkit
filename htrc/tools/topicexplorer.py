from builtins import map
import os.path
import subprocess
from tempfile import NamedTemporaryFile

from htrc.workset import path_to_volumes

def main(path, topics, iterations):
    # strip trailing slash for topic support.
    if path.endswith('/'):
        path = path[:-1]

    # If a workset url was given to the script, we'll need to create a temporary
    # file with the volumes for processing by topic explorer.
    if not os.path.exists(path):
        try:
            volumes = path_to_volumes(path)

            volfile = NamedTemporaryFile(prefix='htrc-workset', delete=False)
            volfile.write(bytes('\n'.join(volumes), "ascii"))

            path = volfile.name

            volfile.close()

        except ValueError as e:
            print("Could not process workset. {}".format(str(e)))
            sys.exit(1)

    subprocess.check_call([
        'topicexplorer', 'init', path,
        '--name', '"HathiTrust Workset"',
        '--rebuild', '--htrc', '-q'
    ])
    subprocess.check_call([
        'topicexplorer', 'prep', path,
        '-q', '--min-word-len', '3', '--lang', 'en'
    ])
    subprocess.check_call([
        'topicexplorer', 'train', path,
        '-k'] + list(map(str,topics)) + [
        '--iter', str(iterations),
        '--context-type', 'book',
        '-q'
    ])
    subprocess.check_call([
        'topicexplorer', 'launch', path
    ])

def populate_parser(parser=None):
    if parser is None:
        from argparse import ArgumentParser
        parser = ArgumentParser()

    parser.add_argument('-k', type=int, nargs='+', required=True,
        help="number of topics")
    parser.add_argument('--iter', help="number of iterations", default=200)
    parser.add_argument('path', default='/media/secure_volume/workset/',
        nargs='?')
    return parser

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(description="Topic Explorer tools for the HTRC")
    populate_parser(parser)
    args = parser.parse_args()

    main(args.path, args.k, args.iter)
