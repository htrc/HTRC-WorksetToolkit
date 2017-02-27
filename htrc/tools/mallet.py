import os, os.path
import subprocess
import tarfile
import wget

# Mallet is downloaded and intalled in users current directory
if not os.path.exists("/home/dcuser/mallet"):
    os.makedirs('/home/dcuser/mallet')
    mallet_zip = wget.download('http://mallet.cs.umass.edu/dist/mallet-2.0.8RC3.tar.gz')
    mallet_dir = tarfile.open(mallet_zip, "r:gz")
    mallet_dir.extractall(path="/home/dcuser/mallet")
    mallet_dir.close()

def main(path, topics, iterations):
    # import the workset to MALLET format.
    subprocess.check_call([
        '/home/dcuser/mallet/mallet-2.0.8RC3/bin/mallet',
        'import-dir',
        '--input', path,
        '--output', path + '../corpus.mallet',
        '--keep-sequence',
        '--remove-stopwords'
        ], stdout=subprocess.STDOUT, stderr=subprocess.STDOUT)

    subprocess.check_call([
        '/home/dcuser/mallet/mallet-2.0.8RC3/bin/mallet',
        'train-topics',
        '--input', path + '../corpus.mallet',
        '--num-topics', topics,
        '--output-state', path + '../mallet_state.gz',
        '--output-topic-keys', path + '../mallet_topic-keys.txt',
        '--output-doc-topics', path + '../mallet_doc-topics.txt',
        '--num-iterations', iterations
        ], stdout=stdprocess.STDOUT, stderr=subprocess.STDOUT)

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
