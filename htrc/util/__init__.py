from __future__ import absolute_import

import math

from .resolve import ORG_CODES

def split_items(seq, split_size):
    """
    Returns a generator that returns portions of `seq` up to `split_size`.
    Useful when chunking requests to bulk endpoints.

    :param seq: A sequence to split.
    :param split_size: The maximum size of each split.
    """
    full_segments = math.floor(len(seq) / split_size)
    for i in range(1,full_segments+1):
        yield seq[(i-1)*split_size:i*split_size]
    if (full_segments * split_size) < len(seq):
        yield seq[full_segments*split_size:]
