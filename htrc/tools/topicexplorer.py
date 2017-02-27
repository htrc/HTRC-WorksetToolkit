import subprocess

def main(path, topics, iterations):
    subprocess.check_call([
        'topicexplorer', 'init', path,
        '--name', '"HathiTrust Workset"',
        '--rebuild', '--htrc'
    ])
    subprocess.check_call([
        'topicexplorer', 'prep', path, 
        '-q', '--lang'
    ])
    subprocess.check_call([
        'topicexplorer', 'train', path,
        '-k', topics,
        '--iter', iterations,
        '--context-type', 'book'
    ])

def populate_parser(parser):
    parser.add_argument('-k', help="number of topics", required=True)
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
