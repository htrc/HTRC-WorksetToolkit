from builtins import str
import os, os.path
import subprocess
import sys
import tarfile
import wget

from htrc.volumes import download_volumes
from htrc.workset import path_to_volumes

# Mallet is downloaded and intalled in users current directory
def install_mallet():
    if not os.path.exists("/home/dcuser/mallet"):
        os.makedirs('/home/dcuser/mallet')
        mallet_zip = wget.download('http://mallet.cs.umass.edu/dist/mallet-2.0.8RC3.tar.gz')
        mallet_dir = tarfile.open(mallet_zip, "r:gz")
        mallet_dir.extractall(path="/home/dcuser/mallet")
        mallet_dir.close()

def main(path, topics, iterations, output_dir='/media/secure_volume/workset/'):
    if not os.path.exists("/home/dcuser/mallet"):
        if not os.path.exists('/media/secure_volume/'):
            print('Installing Mallet ...')
            install_mallet()
            print('\n')
        else:
            print('Mallet not installed, but capsule is in secure mode.')
            print('Switch to maintenance mode and run this command again')
            print('to install Mallet. Then, switch to secure mode to train')
            print('topic models.')
            sys.exit(1)

    if not os.path.isdir(path):
        try:
            volumes = path_to_volumes(path)
        except ValueError as e:
            print("Could not process workset. {}".format(str(e)))
            sys.exit(1)

        try:
            download_volumes(volumes, output_dir)
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
        path = output_dir


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
    parser.add_argument('--workset-path', help="Location to store workset download.",
                        default='/media/secure_volume/workset/')
    parser.add_argument('path', default='/media/secure_volume/workset/',
        nargs='?')
    return parser


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(description="MALLET tools for the HTRC")
    populate_parser(parser)
    args = parser.parse_args()

    main(args.path, args.k, args.iter, args.workset_path)
