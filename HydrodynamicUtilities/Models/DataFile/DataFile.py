from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from HydrodynamicUtilities.Models.DataFile.Base import Keyword
    from typing import Tuple

from .Sections.RUNSPEC import RUNSPEC, UnInitializedRUNSPEC
from .Sections.GRID import GRID,UnInitializedGRID
from .Sections.EDIT import EDIT, UnInitializedEDIT
from .Sections.PROPS import PROPS, UnInitializedPROPS
from .Sections.REGIONS import REGIONS, UnInitializedREGIONS
from .Sections.SOLUTION import SOLUTION, UnInitializedSOLUTION
from .Sections.SUMMARY import SUMMARY, UnInitializedSUMMARY
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

    def set_keyword(self, keyword: Keyword, section: Section) -> None:
        pass


class UnInitializedDataFile(DataFile):
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
        super().__init__()
        self.NoneSection = NoneSection(self)
        self.RUNSPEC = UnInitializedRUNSPEC(self)
        self.GRID = UnInitializedGRID(self)
        self.EDIT = UnInitializedEDIT(self)
        self.PROPS = UnInitializedPROPS(self)
        self.REGIONS = UnInitializedREGIONS(self)
        self.SOLUTION = UnInitializedSOLUTION(self)
        self.SUMMARY = UnInitializedSUMMARY(self)
        self.SCHEDULE = SCHEDULE(self)

    @classmethod
    def get_section_name(cls) -> Tuple[str, ...]:
        return cls.__Section

    def add_keyword(self, keyword: Keyword, section: Section) -> None:
        pass
