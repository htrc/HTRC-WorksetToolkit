import re
from collections import defaultdict
from typing import List, TypeVar, Set, Iterator, Optional, Tuple, Dict

from htrc.models import Page, PageStructure
from htrc.hf_utils import clean_text, levenshtein, pairwise_combine_within_distance, flatten, group_consecutive_when

T = TypeVar('T', bound=Page)
U = TypeVar('U', bound=PageStructure)


class _Line:
    def __init__(self, text: str, line_number: int, page: Page) -> None:
        self.text = text
        self.line_number = line_number
        self.page = page
        self.cleaned_text = clean_text(text)

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, _Line):
            raise NotImplemented

        are_equal = self.page is o.page and self.line_number == o.line_number

        return are_equal

    def __ne__(self, o: object) -> bool:
        return not self == o

    def __hash__(self) -> int:
        line_hash = hash(self.line_number)
        page_hash = hash(self.page)
        hash_value = 31 * line_hash + page_hash

        return hash_value

    def __str__(self) -> str:
        return str((self.line_number, self.cleaned_text))

    def similarity_ratio(self, line: '_Line') -> float:
        ratio = 1 - float(levenshtein(self.cleaned_text, line.cleaned_text)) / max(len(self.cleaned_text),
                                                                                   len(line.cleaned_text))

        return ratio


def parse_page_structure(pages: List[T],
                         window_size: int = 6,
                         min_similarity_ratio: float = 0.7,
                         min_cluster_size: int = 3,
                         max_header_lines: int = 3,
                         max_footer_lines: int = 3) -> List[U]:
    def _get_page_lines(p: T) -> List[_Line]:
        return [_Line(text, line_num, p) for line_num, text in enumerate(p.text_lines)]

    def _cluster_lines(lines: List[Tuple[_Line, _Line]]) -> Set[tuple]:
        cluster_map = {}

        for l1, l2 in lines:
            c1 = cluster_map.get(l1)
            c2 = cluster_map.get(l2)

            if c1 is not None and c2 is not None and c1 is not c2:
                smaller, larger = (c1, c2) if len(c1) < len(c2) else (c2, c1)
                larger.extend(smaller)
                for x in smaller:
                    cluster_map[x] = larger
            elif c1 is not None and c2 is None:
                c1.append(l2)
                cluster_map[l2] = c1
            elif c1 is None and c2 is not None:
                c2.append(l1)
                cluster_map[l1] = c2
            elif c1 is None and c2 is None:
                c = [l1, l2]
                cluster_map[l1] = c
                cluster_map[l2] = c

        return set(map(tuple, cluster_map.values()))

    def _group_lines_by_page(lines: Iterator[_Line]) -> Dict[Page, List[_Line]]:
        lines_grouped_by_page = defaultdict(list)
        for line in lines:
            lines_grouped_by_page[line.page].append(line)

        return lines_grouped_by_page

    def _get_last_header_line(lines: List[_Line]) -> Optional[int]:
        if not lines:
            return None

        return max(l.line_number for l in lines)

    def _get_first_footer_line(lines: List[_Line]) -> Optional[int]:
        if not lines:
            return None

        return min(l.line_number for l in lines)

    def _extract_line_numbers(line: _Line) -> Tuple[_Line, List[int]]:
        numbers = [int(match.group(0)) for match in
                   re.finditer(r"(?:(?<=^)|(?<=\s))\d{1,4}(?=\s|$)", line.text, flags=re.UNICODE)]

        return line, numbers

    def _extract_potential_page_numbers(lines: List[_Line]) -> Tuple[_Line, List[int]]:
        assert len(lines) > 0
        line, numbers = _extract_line_numbers(lines[-1])
        if not numbers and not str.strip(line.text) and len(lines) > 1:
            line, numbers = _extract_line_numbers(lines[-2])

        return line, numbers

    candidate_header_lines = []
    candidate_footer_lines = []

    pages_lines = [_get_page_lines(p) for p in pages]

    for lines in pages_lines:
        # ignore lines that are <4 characters long and/or have no alphabetic characters
        candidate_header_lines.append([l for l in lines[:max_header_lines] if not len(l.cleaned_text) < 4])
        candidate_footer_lines.append([l for l in lines[-max_footer_lines:] if not len(l.cleaned_text) < 4])

    headers_for_comparison = pairwise_combine_within_distance(candidate_header_lines, window_size)
    footers_for_comparison = pairwise_combine_within_distance(candidate_footer_lines, window_size)

    header_line_similarities = []
    for (lines1, lines2) in headers_for_comparison:
        header_line_similarities.extend(
            (l1, l2) for l1 in lines1 for l2 in lines2 if l1.similarity_ratio(l2) >= min_similarity_ratio)

    footer_line_similarities = []
    for (lines1, lines2) in footers_for_comparison:
        footer_line_similarities.extend(
            (l1, l2) for l1 in lines1 for l2 in lines2 if l1.similarity_ratio(l2) >= min_similarity_ratio)

    header_clusters = [cluster for cluster in _cluster_lines(header_line_similarities) if
                       len(cluster) >= min_cluster_size]
    footer_clusters = [cluster for cluster in _cluster_lines(footer_line_similarities) if
                       len(cluster) >= min_cluster_size]

    if not footer_clusters:
        potential_page_numbers = [_extract_potential_page_numbers(lines) for lines in pages_lines if lines]
        potential_page_numbers = [(line, numbers[0]) for line, numbers in potential_page_numbers if len(numbers) == 1]
        potential_clusters = map(lambda group: tuple(map(lambda t: t[0], group)),
                                 group_consecutive_when(potential_page_numbers, lambda x, y: y[1] - x[1] == 1))
        footer_clusters = [cluster for cluster in potential_clusters if len(cluster) >= min_cluster_size]

    header_lines_grouped_by_page = _group_lines_by_page(flatten(header_clusters))
    footer_lines_grouped_by_page = _group_lines_by_page(flatten(footer_clusters))

    last_header_line_pages_map = {p: _get_last_header_line(lines) for p, lines in header_lines_grouped_by_page.items()}
    first_footer_line_pages_map = {p: _get_first_footer_line(lines) for p, lines in
                                   footer_lines_grouped_by_page.items()}

    for page in pages:
        last_header_line = last_header_line_pages_map.get(page)
        first_footer_line = first_footer_line_pages_map.get(page)
        page.__class__ = type('StructuredPage', (page.__class__, PageStructure), {})
        page.num_header_lines = last_header_line + 1 if last_header_line is not None else 0
        page.num_footer_lines = len(page.text_lines) - first_footer_line if first_footer_line is not None else 0

    return pages
