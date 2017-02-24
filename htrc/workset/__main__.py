from htrc.workset import *

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('filename')

    args = parser.parse_args()

    volumes = load(args.filename)

    for vol in volumes:
        print(vol)
