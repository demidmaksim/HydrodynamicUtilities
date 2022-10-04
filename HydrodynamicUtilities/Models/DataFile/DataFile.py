from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from HydrodynamicUtilities.Models.DataFile import KeyWord
    from typing import Tuple

from .Sections.RUNSPEC import RUNSPEC
from .Sections.GRID import GRID
from .Sections.EDIT import EDIT
from .Sections.PROPS import PROPS
from .Sections.REGIONS import REGIONS
from .Sections.SOLUTION import SOLUTION
from .Sections.SUMMARY import SUMMARY
from .Sections.SCHEDULE import SCHEDULE
from .Sections.NoneSection import NoneSection
from .Base import Section


class DataFile:
    __Section = (
        "RUNSPEC",
        "GRID",
        "EDIT",
        "PROPS",
        "REGIONS",
        "SOLUTION",
        "SUMMARY",
        "SCHEDULE",
    )

    def __init__(self):
        self.NoneSection = NoneSection(self)
        self.RUNSPEC = RUNSPEC(self)
        self.GRID = GRID(self)
        self.EDIT = EDIT(self)
        self.PROPS = PROPS(self)
        self.REGIONS = REGIONS(self)
        self.SOLUTION = SOLUTION(self)
        self.SUMMARY = SUMMARY(self)
        self.SCHEDULE = SCHEDULE(self)

    @classmethod
    def get_section_name(cls) -> Tuple[str, ...]:
        return cls.__Section

    def add_keyword(self, keyword: KeyWord, section: Section) -> None:
        pass
