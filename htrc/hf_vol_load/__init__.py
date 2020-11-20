import unittest
from typing import List

from htrc.models import HtrcPage
from htrc.runningheaders import parse_page_structure, clean_text, levenshtein


class TestRunningHeaders(unittest.TestCase):
    def test_finding_running_headers(self):
        pages = load_vol("data/vol1", num_pages=10)
        structured_pages = parse_page_structure(pages)
        headers = ["|".join(page.header_lines) for page in structured_pages]
        expected = [
            "",
            "",
            "CHAPTER 1|INTRODUCTION TO RUNNING HEADERS|Lorem Ipsum style",
            "1 INTRODUCTION TO RUNNING HEADERS|Lorem Ipsum style",
            "INTRODUCTION TO RUNNING HEADERS 1|Lorem Ipsum style",
            "1 INTRODUCTION TO RUNNING HEADERS|Lorem Ipsum style",
            "CHAPTER 2|EVERYTHING IS RELATIVE",
            "2 EVERYTHING IS RELATIVE",
            "EVERYTHING IS RELATIVE 2",
            "2 EVERYTHING IS RELATIVE"
        ]
        self.assertListEqual(expected, headers)

    def test_finding_running_footers(self):
        pages = load_vol("data/vol1", num_pages=10)
        structured_pages = parse_page_structure(pages)
        footers = ["|".join(page.footer_lines) for page in structured_pages]
        expected = [
            "",
            "",
            "Page 2",
            "Page 3",
            "Page 4",
            "Page 5",
            "Page 6",
            "Page 7",
            "Page 8",
            "Page 9"
        ]
        self.assertListEqual(expected, footers)

    def test_identify_correct_page_body(self):
        pages = load_vol("data/vol1", num_pages=10)
        structured_pages = parse_page_structure(pages)
        len_body_per_page = [len(page.body_lines) for page in structured_pages]
        expected = [0, 7, 43, 28, 26, 30, 31, 27, 28, 15]
        self.assertListEqual(expected, len_body_per_page)

    def test_find_footer_with_page_numbers(self):
        pages = load_vol("data/vol2", num_pages=10)
        structured_pages = parse_page_structure(pages)
        footers = ["|".join(page.footer_lines) for page in structured_pages]
        expected = [
            "",
            "",
            "2",
            "                                                                                    3",
            "4",
            "                                                                                    5",
            "6",
            "                                                                                    7",
            "8",
            "                                                                                    9"
        ]
        self.assertListEqual(expected, footers)


class TestUtils(unittest.TestCase):
    def test_clean_text(self):
        s1 = u"\t На   берегу \tпустынных волн  \t\n"
        s1_expected = u"на берегу пустынных волн"
        s2 = u" Pot să mănânc  sticlă și ea nu mă rănește. "
        s2_expected = u"pot să mănânc sticlă și ea nu mă rănește"
        s1_clean = clean_text(s1)
        s2_clean = clean_text(s2)

        self.assertEqual(s1_expected, s1_clean)
        self.assertEqual(s2_expected, s2_clean)

    def test_levenshtein(self):
        s1 = "rosettacode"
        s2 = "raisethysword"
        lev = levenshtein(s1, s2)
        self.assertEqual(8, lev)

        s1 = "kitten"
        s2 = "sitting"
        lev = levenshtein(s1, s2, replace_cost=2)
        self.assertEqual(5, lev)

        s1 = "abracadabra"
        s2 = "abracadabra"
        lev = levenshtein(s1, s2)
        self.assertEqual(0, lev)

        s1 = ""
        s2 = "abc"
        lev = levenshtein(s1, s2)
        self.assertEqual(3, lev)


def load_vol(path: str, num_pages: int) -> List[HtrcPage]:
    pages = []
    for n in range(num_pages):
        page_num = str(n+1).zfill(8)
        with open('{}/{}.txt'.format(path, page_num), encoding='utf-8') as f:
            lines = [line.rstrip() for line in f.readlines()]
            pages.append(HtrcPage(lines))

    return pages


if __name__ == '__main__':
    unittest.main()
