import re
from typing import TypeVar, List, Iterator, Tuple, Callable

T = TypeVar('T')


def clean_text(s: str) -> str:
    # replace all characters which aren't letters with whitespaces ([\W\d_] is equivalent of \P{L} which is unsupported)
    s = re.sub(r'[\W\d_]+', " ", s, flags=re.UNICODE)
    # replace multiple sequential whitespaces with single whitespace
    s = re.sub(r'\s{2,}', " ", s, flags=re.UNICODE)
    # trim whitespaces at the beginning and end
    s = s.strip()
    # lowercase
    s = s.lower()

    return s


def levenshtein(s: str, t: str, insert_cost: int = 1, delete_cost: int = 1, replace_cost: int = 1) -> int:
    """ From Wikipedia article; Iterative with two matrix rows. """
    # degenerate cases
    if s == t:
        return 0

    len0 = len(s)
    len1 = len(t)

    if not len0:
        return len1

    if not len1:
        return len0

    # the array of distances
    v0 = [0] * (len0 + 1)
    v1 = [0] * (len0 + 1)

    # initial cost of skipping prefix in s
    for i in range(len(v0)):
        v0[i] = i

    # dynamically compute the array of distances

    # transformation cost for each letter in t
    for j in range(len1):
        # initial cost of skipping prefix in t
        v1[0] = j + 1

        # transformation cost for each letter in s
        for i in range(len0):
            # matching current letters in both strings
            match = 0 if s[i] == t[j] else 1

            # computing cost for each transformation
            cost_insert = v0[i + 1] + insert_cost
            cost_delete = v1[i] + delete_cost
            cost_replace = v0[i] + match * replace_cost

            # keep minimum cost
            v1[i + 1] = min(cost_insert, cost_delete, cost_replace)

        # swap cost arrays
        v0, v1 = v1, v0

    # the distance is the cost for transforming all letters in both strings
    return v0[len0]


def pairwise_combine_within_distance(xs: List[T], n: int) -> List[Tuple[T, T]]:
    if not xs:
        return []

    result = []
    x, xs = xs[0], xs[1:]

    while xs:
        result = result + [(x, v) for v in xs[:n - 1]]
        x, xs = xs[0], xs[1:]

    return result


def group_consecutive_when(xs: List[T], pred: Callable[[T, T], bool]) -> Iterator[List[T]]:
    result = []
    _prev, _next = None, None

    while len(xs) > 1:
        _prev, _next = xs[0], xs[1]
        result.append(_prev)
        if not pred(_prev, _next):
            yield result
            result = []
        xs = xs[1:]

    if len(xs) == 1:
        _prev, _next = _next, xs[0]

    if _prev is not None and _next is not None and pred(_prev, _next):
        result.extend([_prev, _next])
    elif _next is not None:
        result.append(_next)

    yield result


def flatten(xss: List[tuple]) -> Iterator[T]:
    for xs in xss:
        for x in xs:
            yield x
