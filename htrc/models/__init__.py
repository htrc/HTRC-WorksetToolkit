import os
from abc import ABC, abstractmethod
from typing import List


class Page(ABC):
    @property
    @abstractmethod
    def text_lines(self) -> List[str]:
        """
        The lines of text on the page
        """
        pass

    @property
    def text(self) -> str:
        return os.linesep.join(self.text_lines)


class PageStructure(Page, ABC):
    def __init__(self) -> None:
        self.num_header_lines = 0
        self.num_footer_lines = 0

    @property
    def has_header(self) -> bool:
        return self.num_header_lines > 0

    @property
    def has_body(self) -> bool:
        return len(self.text_lines) - self.num_header_lines - self.num_footer_lines > 0

    @property
    def has_footer(self) -> bool:
        return self.num_footer_lines > 0

    @property
    def header_lines(self) -> List[str]:
        return self.text_lines[:self.num_header_lines]

    @property
    def body_lines(self) -> List[str]:
        return self.text_lines[self.num_header_lines:len(self.text_lines) - self.num_footer_lines]

    @property
    def footer_lines(self) -> List[str]:
        return self.text_lines[-self.num_footer_lines:] if self.has_footer else []

    @property
    def header(self) -> str:
        return os.linesep.join(self.header_lines)

    @property
    def body(self) -> str:
        return os.linesep.join(self.body_lines)

    @property
    def footer(self) -> str:
        return os.linesep.join(self.footer_lines)


class HtrcPage(Page):
    def __init__(self, lines: List[str]) -> None:
        self._lines = lines

    @property
    def text_lines(self) -> List[str]:
        return self._lines
