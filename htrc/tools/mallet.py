from builtins import str
import os, os.path
import subprocess
import tarfile
import wget

# Mallet is downloaded and intalled in users current directory
def install_mallet():
    if not os.path.exists("/home/dcuser/mallet"):
        os.makedirs('/home/dcuser/mallet')
        mallet_zip = wget.download('http://mallet.cs.umass.edu/dist/mallet-2.0.8RC3.tar.gz')
        mallet_dir = tarfile.open(mallet_zip, "r:gz")
        mallet_dir.extractall(path="/home/dcuser/mallet")
        mallet_dir.close()

def main(path, topics, iterations):
    install_mallet()

    # import the workset to MALLET format.
    subprocess.check_call([
        '/home/dcuser/mallet/mallet-2.0.8RC3/bin/mallet',
        'import-dir',
        '--input', path,
        '--output', os.path.join(path, '../corpus.mallet'),
        '--keep-sequence',
        '--remove-stopwords'
        ])

    subprocess.check_call([
        '/home/dcuser/mallet/mallet-2.0.8RC3/bin/mallet',
        'train-topics',
        '--input', os.path.join(path, '../corpus.mallet'),
        '--num-topics', str(topics),
        '--output-state', os.path.join(path, '../mallet_state.gz'),
        '--output-topic-keys', os.path.join(path, '../mallet_topic-keys.txt'),
        '--output-doc-topics', os.path.join(path, '../mallet_doc-topics.txt'),
        '--num-iterations', str(iterations)
        ])

def populate_parser(parser=None):
    if parser is None:
        from argparse import ArgumentParser
        parser = ArgumentParser()
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
