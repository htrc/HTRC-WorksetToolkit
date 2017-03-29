from __future__ import print_function

import itertools
import os, os.path

import loremipsum

VOL_NAME = 'htrc.test{}'
PAGE_FILENAME = '{0:08d}.txt'

def generate_file(filename, N=4, separator='\n\n'):
    with open(filename, 'w') as outfile:
        for _,_,text in loremipsum.generate_paragraphs(N):
            outfile.write(text + separator)

def generate_volumes(num_volumes, num_pages=5):
    if isinstance(num_pages, int):
        num_pages = itertools.repeat(num_pages, num_volumes)
    elif len(num_pages) != num_volumes:
        raise ValueError("len(num_pages) != num_volumes")
    
    for i, pages in enumerate(num_pages):
        vol_name = VOL_NAME.format(i)
        if not os.path.exists(vol_name):
            os.makedirs(vol_name)

        for page in range(pages):
            page = page+1
            filename = os.path.join(vol_name, PAGE_FILENAME.format(page))
            generate_file(filename)

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('vols', type=int)
    parser.add_argument('pages', type=int)
    args = parser.parse_args()

    generate_volumes(args.vols, args.pages)
        
