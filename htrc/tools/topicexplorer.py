import subprocess

def main(path, topics, iterations):
    if path.endswith('/'):
        path = path[:-1]

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
        '-k'] + map(str,topics) + [
        '--iter', iterations,
        '--context-type', 'book',
        '-q'
    ])
    subprocess.check_call([
        'topicexplorer', 'launch', path 
    ])

def populate_parser(parser):
    parser.add_argument('-k', type=int, nargs='+', required=True,
        help="number of topics")
    parser.add_argument('--iter', help="number of iterations", default=200)
    parser.add_argument('path', default='/media/secure_volume/workset/',
        nargs='?')
    return parser

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(description="MALLET tools for the HTRC")
    populate_parser(parser)
    args = parser.parse_args()

    main(args.path, args.k, args.iter)
